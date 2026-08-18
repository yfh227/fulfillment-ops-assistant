"""Generate auth_config.yaml, the credential store for the Streamlit login.

Creates one test user per content role plus an all-access admin used for
regression runs. Passwords are random and bcrypt-hashed by
streamlit-authenticator; the plaintext is printed once here and stored
nowhere, so a lost password means re-running with --force rather than
recovering it.

The generated file is gitignored. This script is the tracked artefact, so the
config can always be rebuilt from a clean checkout.

    python make_auth_config.py [--force]
"""

import argparse
import secrets
import string
import sys
from pathlib import Path

import streamlit_authenticator as stauth
import yaml

import core

CONFIG_PATH = Path(__file__).parent / "auth_config.yaml"

# One user per role. Admin carries every content role as well as ROLE_ADMIN so
# that "log in as admin" is genuinely all-access rather than a fourth, empty
# role - eval.py's original 8 cases are re-run as this user.
USERS = {
    "billing": {
        "first_name": "Billing",
        "last_name": "Analyst",
        "email": "billing@example.invalid",
        "roles": [core.ROLE_BILLING],
    },
    "warehouse": {
        "first_name": "Warehouse",
        "last_name": "Lead",
        "email": "warehouse@example.invalid",
        "roles": [core.ROLE_WAREHOUSE],
    },
    "account": {
        "first_name": "Account",
        "last_name": "Manager",
        "email": "account@example.invalid",
        "roles": [core.ROLE_ACCOUNT],
    },
    "admin": {
        "first_name": "All",
        "last_name": "Access",
        "email": "admin@example.invalid",
        "roles": [core.ROLE_ADMIN, *core.CONTENT_ROLES],
    },
}

ALPHABET = string.ascii_letters + string.digits


def random_password(length: int = 16) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing auth_config.yaml (invalidates current passwords)",
    )
    args = parser.parse_args()

    if CONFIG_PATH.exists() and not args.force:
        print(f"{CONFIG_PATH.name} already exists. Re-run with --force to replace it.")
        return 1

    plaintext = {username: random_password() for username in USERS}

    credentials = {
        "usernames": {
            username: {**fields, "password": plaintext[username]}
            for username, fields in USERS.items()
        }
    }
    # hash_passwords replaces each plaintext password with its bcrypt hash.
    credentials = stauth.Hasher.hash_passwords(credentials)

    config = {
        "cookie": {
            "name": "fulfillment_ops_auth",
            "key": secrets.token_urlsafe(32),
            "expiry_days": 1,
        },
        "credentials": credentials,
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)

    print(f"Wrote {CONFIG_PATH.name} with {len(USERS)} users.\n")
    print("Test credentials - shown once, not stored in plaintext anywhere:\n")
    width = max(len(u) for u in USERS)
    for username, fields in USERS.items():
        print(f"  {username:<{width}}  {plaintext[username]}  ({', '.join(fields['roles'])})")
    print("\nauth_config.yaml is gitignored. Do not commit it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
