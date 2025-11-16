#!/usr/bin/env python3
"""
MNIST Training Script for Query.ai Test Suite
Configurable training script that logs to WandB
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import wandb
import argparse
import json
import os
from datetime import datetime


class MNISTNet(nn.Module):
    """Configurable MNIST Neural Network"""

    def __init__(self, config):
        super(MNISTNet, self).__init__()
        self.config = config

        # Build architecture based on config
        layers = []
        input_size = 784  # 28x28 flattened

        for i, hidden_size in enumerate(config['hidden_layers']):
            layers.append(nn.Linear(input_size, hidden_size))

            if config.get('batch_norm', False):
                layers.append(nn.BatchNorm1d(hidden_size))

            layers.append(nn.ReLU())

            if config.get('dropout', 0) > 0:
                layers.append(nn.Dropout(config['dropout']))

            input_size = hidden_size

        # Output layer
        layers.append(nn.Linear(input_size, 10))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        return self.network(x)


def get_data_loaders(config):
    """Create train and test data loaders with optional augmentation"""

    # Base transforms
    transform_list = [transforms.ToTensor()]

    # Optional data augmentation
    if config.get('data_augmentation', False):
        transform_list = [
            transforms.RandomRotation(10),
            transforms.RandomAffine(0, translate=(0.1, 0.1)),
            transforms.ToTensor()
        ]

    # Add normalization
    transform_list.append(transforms.Normalize((0.1307,), (0.3081,)))

    transform = transforms.Compose(transform_list)

    train_dataset = datasets.MNIST(
        './data',
        train=True,
        download=True,
        transform=transform
    )

    test_dataset = datasets.MNIST(
        './data',
        train=False,
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=2
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=2
    )

    return train_loader, test_loader


def get_optimizer(model, config):
    """Create optimizer based on config"""

    optimizer_name = config.get('optimizer', 'adam').lower()
    lr = config['learning_rate']
    weight_decay = config.get('weight_decay', 0.0)

    if optimizer_name == 'adam':
        return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name == 'sgd':
        momentum = config.get('momentum', 0.9)
        return optim.SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
    elif optimizer_name == 'rmsprop':
        return optim.RMSprop(model.parameters(), lr=lr, weight_decay=weight_decay)
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")


def get_scheduler(optimizer, config):
    """Create learning rate scheduler if configured"""

    if not config.get('lr_scheduler', False):
        return None

    scheduler_type = config.get('scheduler_type', 'step')

    if scheduler_type == 'step':
        return optim.lr_scheduler.StepLR(
            optimizer,
            step_size=config.get('scheduler_step', 10),
            gamma=config.get('scheduler_gamma', 0.1)
        )
    elif scheduler_type == 'cosine':
        return optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config['epochs']
        )
    elif scheduler_type == 'reduce_on_plateau':
        return optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            patience=5,
            factor=0.5
        )

    return None


def train_epoch(model, device, train_loader, optimizer, criterion, epoch):
    """Train for one epoch"""
    model.train()
    train_loss = 0
    correct = 0
    total = 0

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)

    avg_loss = train_loss / len(train_loader)
    accuracy = 100. * correct / total

    return avg_loss, accuracy


def test(model, device, test_loader, criterion):
    """Evaluate on test set"""
    model.eval()
    test_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

    avg_loss = test_loss / len(test_loader)
    accuracy = 100. * correct / total

    return avg_loss, accuracy


def train(config, wandb_project=None, wandb_run_name=None):
    """Main training function"""

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Initialize WandB if project specified
    if wandb_project:
        wandb.init(
            project=wandb_project,
            name=wandb_run_name,
            config=config
        )

    # Data loaders
    train_loader, test_loader = get_data_loaders(config)

    # Model
    model = MNISTNet(config).to(device)
    print(f"Model architecture:\n{model}")

    # Loss function
    criterion = nn.CrossEntropyLoss()

    # Optimizer
    optimizer = get_optimizer(model, config)

    # Scheduler
    scheduler = get_scheduler(optimizer, config)

    # Training loop
    best_val_acc = 0
    patience_counter = 0
    early_stopping_patience = config.get('early_stopping_patience', None)

    for epoch in range(1, config['epochs'] + 1):
        # Train
        train_loss, train_acc = train_epoch(
            model, device, train_loader, optimizer, criterion, epoch
        )

        # Test
        val_loss, val_acc = test(model, device, test_loader, criterion)

        # Learning rate
        current_lr = optimizer.param_groups[0]['lr']

        # Print progress
        print(f'Epoch {epoch}/{config["epochs"]}:')
        print(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
        print(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        print(f'  LR: {current_lr:.6f}')

        # Log to WandB
        if wandb_project:
            wandb.log({
                'epoch': epoch,
                'train_loss': train_loss,
                'train_accuracy': train_acc,
                'val_loss': val_loss,
                'val_accuracy': val_acc,
                'learning_rate': current_lr
            })

        # Update scheduler
        if scheduler is not None:
            if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(val_loss)
            else:
                scheduler.step()

        # Early stopping
        if early_stopping_patience:
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping at epoch {epoch}")
                    break

    # Final metrics
    final_train_loss, final_train_acc = train_epoch(
        model, device, train_loader, optimizer, criterion, epoch
    )
    final_val_loss, final_val_acc = test(model, device, test_loader, criterion)

    print(f'\nFinal Results:')
    print(f'  Train Acc: {final_train_acc:.2f}%, Val Acc: {final_val_acc:.2f}%')

    if wandb_project:
        wandb.log({
            'final_train_accuracy': final_train_acc,
            'final_val_accuracy': final_val_acc,
            'final_train_loss': final_train_loss,
            'final_val_loss': final_val_loss
        })
        wandb.finish()

    return final_val_acc


def main():
    parser = argparse.ArgumentParser(description='MNIST Training')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to experiment config JSON file')
    parser.add_argument('--wandb-project', type=str, default=None,
                        help='WandB project name')
    parser.add_argument('--wandb-run-name', type=str, default=None,
                        help='WandB run name')

    args = parser.parse_args()

    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)

    print(f"Configuration: {json.dumps(config, indent=2)}")

    # Train
    train(config, args.wandb_project, args.wandb_run_name)


if __name__ == '__main__':
    main()
