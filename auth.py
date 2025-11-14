"""Simple authentication for the Streamlit app."""

import streamlit as st
import hashlib
import os
from typing import Optional, Dict
from logger_config import get_logger

logger = get_logger(__name__)


class SimpleAuthenticator:
    """Simple username/password authentication."""

    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        """
        Initialize authenticator.

        Args:
            credentials: Dictionary of {username: hashed_password}
        """
        self.credentials = credentials or self._load_default_credentials()

    def _load_default_credentials(self) -> Dict[str, str]:
        """Load credentials from environment variables."""
        credentials = {}

        # Load from env vars (format: USERNAME=user1,user2 PASSWORD=hash1,hash2)
        usernames = os.getenv("AUTH_USERNAMES", "admin").split(",")
        passwords = os.getenv("AUTH_PASSWORDS", "").split(",")

        if not passwords or passwords == ['']:
            # No passwords configured, use demo password hashed
            demo_password = self._hash_password("demo123")
            passwords = [demo_password] * len(usernames)

        for username, password_hash in zip(usernames, passwords):
            credentials[username.strip()] = password_hash.strip()

        logger.info(f"Loaded {len(credentials)} user credentials")
        return credentials

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Password (plain text)

        Returns:
            True if authentication successful
        """
        if username not in self.credentials:
            logger.warning(f"Login attempt with unknown username: {username}")
            return False

        password_hash = self._hash_password(password)
        authenticated = self.credentials[username] == password_hash

        if authenticated:
            logger.info(f"Successful login for user: {username}")
        else:
            logger.warning(f"Failed login attempt for user: {username}")

        return authenticated

    def login_form(self) -> bool:
        """
        Display login form in Streamlit and handle authentication.

        Returns:
            True if user is authenticated
        """
        # Check if already authenticated
        if st.session_state.get("authenticated", False):
            return True

        # Display login form
        st.markdown("## Login")
        st.markdown("Please enter your credentials to access Query.ai")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if self.authenticate(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        # Show demo credentials hint if using defaults
        if os.getenv("AUTH_PASSWORDS", "") == "":
            st.info("Demo credentials: username=`admin`, password=`demo123`")

        return False

    def logout(self):
        """Logout current user."""
        username = st.session_state.get("username", "unknown")
        logger.info(f"User logged out: {username}")
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.rerun()

    def require_auth(self):
        """Decorator/helper to require authentication for a page."""
        if not st.session_state.get("authenticated", False):
            return False
        return True


def get_authenticator() -> SimpleAuthenticator:
    """Get authenticator instance (singleton)."""
    if "authenticator" not in st.session_state:
        st.session_state["authenticator"] = SimpleAuthenticator()
    return st.session_state["authenticator"]
