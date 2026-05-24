import os
from typing import Tuple
from supabase import create_client, Client
import jwt
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")

        self.supabase: Client = create_client(url, key)

    def sign_in_user(self, email: str, password: str) -> Tuple[str, dict]:
        """Signs in a user with email and password.
        Args:
            email (str): The user's email.
            password (str): The user's password.
        Returns:
            tuple: A tuple containing the auth ID and a dictionary with session details or error message.
        """
        try:
            

            response = self.supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )

            auth_id = response.user.id if response.user else None

            

            if response.user:
                session_token = response.session.access_token
                refresh_token = response.session.refresh_token

                return auth_id, {"status": "success", "session_token": session_token, "refresh_token": refresh_token, "auth_id": auth_id}
            else:
                return None, {"status": "error", "message": "Invalid credentials"}
        except Exception as e:
            return None, {"status": "error", "message": str(e)}
        


    def sign_out_user(self, access_token: str, refresh_token: str) -> dict:
        """Sign out user by invalidating the session tokens.
        Args:
            access_token (str): The current access token.
            refresh_token (str): The refresh token.
        Returns:
            dict: A dictionary with the status of the sign-out operation."""
        supabase = self.supabase
        if not supabase:
            return {"status": "error", "message": "User not signed in"}

        try:
            self.supabase.auth.set_session(access_token, refresh_token)
            self.supabase.auth.sign_out()
            return {"status": "success", "message": "User signed out successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        

    def refresh_session(self, access_token: str, refresh_token: str) -> Tuple[str, dict]:
        """Refreshes the user session using the refresh token.
        Args:
            access_token (str): The current access token.
            refresh_token (str): The refresh token.
        Returns:
            tuple: A tuple containing the auth ID and a dictionary with new session details or error message.
        """
        try:
            jwt_decoded = jwt.decode(access_token, options={"verify_signature": False})
            auth_id = jwt_decoded.get("sub")

            if not auth_id:
                return {"status": "error", "message": "Invalid access token"}
            
            response = self.supabase.auth.refresh_session(refresh_token)

            auth_id = response.user.id if response.user else None

            if response.user:
                new_access_token = response.session.access_token
                new_refresh_token = response.session.refresh_token

                return auth_id, {"status": "success", "access_token": new_access_token, "refresh_token": new_refresh_token, "auth_id": auth_id}
            else:
                return None, {"status": "error", "message": "Failed to refresh session"}
            
        except Exception as e:
            return None, {"status": "error", "message": str(e)}   
        

    def sign_up_user(self, email: str, password: str) -> Tuple[str, dict]:
        """Signs up a new user with email and password.
        Args:
            email (str): The user's email.
            password (str): The user's password.
        Returns:
            tuple: A tuple containing the auth ID and a dictionary with session details or error message.
        """
        try:

            supabase: Client = self.supabase    

            response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "email_redirect_to": os.environ.get("SUPABASE_REDIRECT_URL")
                    }
                }
            )

            auth_id = response.user.id if response.user else None

            if response.user:
                return auth_id, {"status": "success", "auth_id": auth_id}
            else:
                return None, {"status": "error", "message": "Sign up failed"}
        except Exception as e:
            return None, {"status": "error", "message": str(e)}