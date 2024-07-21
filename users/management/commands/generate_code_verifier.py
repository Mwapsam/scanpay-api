import random
import string
import base64
import hashlib
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates a code verifier and code challenge for OAuth2 PKCE"

    def handle(self, *args, **options):
        code_verifier = "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(random.randint(43, 128))
        )
        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = (
            base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")
        )

        self.stdout.write(f"Code Verifier: {code_verifier}")
        self.stdout.write(f"Code Challenge: {code_challenge}")
