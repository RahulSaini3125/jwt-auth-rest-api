# tokens.py

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
import base64
import json
from dateutil.parser import isoparse

class ExpiringTokenGenerator(default_token_generator.__class__):
    def make_token(self, user):
        token = super().make_token(user)
        expiration_time = timezone.now() + timedelta(hours=1)  # Token expires in 1 hour
        payload = {
            'token': token,
            'expires_at': expiration_time.isoformat()
        }
        return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    def check_token(self, user, token):
        try:
            payload = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
            token_value = payload['token']
            iso_date_string = payload['expires_at']
            expires_at = isoparse(iso_date_string)
            if timezone.now() > expires_at:
                return False
            return True
        except Exception:
            return False

# Instantiate the custom token generator
expiring_token_generator = ExpiringTokenGenerator()
