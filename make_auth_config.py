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


def build_config(passwords: dict, cookie_key: str = None) -> dict:
    """Assemble the config dict from a username -> plaintext mapping.

    Split out of main() so the app can build the same structure at startup
    without shelling out to this script - Streamlit Community Cloud has no
    shell, so the manual step this file documents is impossible there.
    """
    missing = sorted(set(USERS) - {u for u, p in passwords.items() if p})
    if missing:
        raise ValueError(f"no password supplied for: {', '.join(missing)}")

    credentials = {
        "usernames": {
            username: {**fields, "password": passwords[username]}
            for username, fields in USERS.items()
        }
    }
    # hash_passwords replaces each plaintext password with its bcrypt hash.
    credentials = stauth.Hasher.hash_passwords(credentials)

    return {
        "cookie": {
            "name": "fulfillment_ops_auth",
            # A fresh key per container is fine - it only invalidates cookies
            # issued by a previous container, which are gone anyway. Supplying
            # one keeps sessions alive across restarts.
            "key": cookie_key or secrets.token_urlsafe(32),
            "expiry_days": 1,
        },
        "credentials": credentials,
    }


def write_config(config: dict, path: Path = CONFIG_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)


def ensure_config(path: Path = CONFIG_PATH, passwords: dict = None,
                  cookie_key: str = None) -> str:
    """Create the config if it is absent, but only from usable credentials.

    "existing" - file was already there, nothing written
    "created"  - written from the caller's passwords
    "missing"  - no complete set of passwords supplied; nothing written

    Deliberately does NOT invent random passwords as a fallback. Writing a
    config whose passwords are printed nowhere produces a login form that
    cannot be opened, and - because Streamlit reruns the whole script on every
    interaction - the very next rerun would see the file, report "existing",
    and hide the problem. Returning "missing" without writing keeps the failure
    visible on every rerun instead of only the first.
    """
    if path.exists():
        return "existing"
    if not (passwords and all(passwords.get(u) for u in USERS)):
        return "missing"
    write_config(build_config(passwords, cookie_key), path)
    return "created"


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
    write_config(build_config(plaintext), CONFIG_PATH)

    print(f"Wrote {CONFIG_PATH.name} with {len(USERS)} users.\n")
    print("Test credentials - shown once, not stored in plaintext anywhere:\n")
    width = max(len(u) for u in USERS)
    for username, fields in USERS.items():
        print(f"  {username:<{width}}  {plaintext[username]}  ({', '.join(fields['roles'])})")
    print("\nauth_config.yaml is gitignored. Do not commit it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
