# A collection of reusable helper/utility functions
import secrets

def generate_session_id() -> str:
  """
  Generates a cryptographically secure, URL-safe session ID.
  """
  return secrets.token_urlsafe(32)
