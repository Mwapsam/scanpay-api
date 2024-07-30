import secrets
from django.core.management.base import BaseCommand
import environ
import os


class Command(BaseCommand):
    help = "Generate a client identifier and store it in the .env file"

    def handle(self, *args, **kwargs):
        identifier_length = 32  # Length of the client identifier
        client_identifier = secrets.token_hex(identifier_length)

        # Read the current .env file content
        env_file_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            ".env",
        )

        if os.path.exists(env_file_path):
            env = environ.Env()
            env.read_env(env_file_path)

            with open(env_file_path, "r") as file:
                lines = file.readlines()

            # Check if CLIENT_IDENTIFIER already exists
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("CLIENT_IDENTIFIER="):
                    lines[i] = f"CLIENT_IDENTIFIER={client_identifier}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"CLIENT_IDENTIFIER={client_identifier}\n")

            # Write the updated content back to the .env file
            with open(env_file_path, "w") as file:
                file.writelines(lines)
        else:
            # If .env file does not exist, create it and add the CLIENT_IDENTIFIER
            with open(env_file_path, "w") as file:
                file.write(f"CLIENT_IDENTIFIER={client_identifier}\n")

        self.stdout.write(
            self.style.SUCCESS(f"Generated client identifier: {client_identifier}")
        )
