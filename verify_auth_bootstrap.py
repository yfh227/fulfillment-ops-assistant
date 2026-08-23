"""Check that auth_config.yaml bootstraps correctly from a clean state.

Exercises the real code path app.py takes on a cold start, in a temp directory
so the working config is never touched. Verifies the bcrypt hashes actually
open with the supplied passwords rather than just checking the file exists.

    python verify_auth_bootstrap.py
"""

import sys
import tempfile
from pathlib import Path

import bcrypt
import yaml

import make_auth_config as mac

failures = []


def check(label, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    if not cond:
        failures.append(label)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "auth_config.yaml"
        pw = {u: f"pw-{u}-12345" for u in mac.USERS}

        print("\n--- cold start with supplied passwords ---")
        src = mac.ensure_config(path, pw, cookie_key="fixed-cookie-key")
        check("returns 'created'", src == "created", src)
        check("file created", path.exists())

        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        check("has cookie + credentials", {"cookie", "credentials"} <= set(cfg))
        check("cookie key honoured", cfg["cookie"]["key"] == "fixed-cookie-key")
        check("cookie name preserved",
              cfg["cookie"]["name"] == "fulfillment_ops_auth")

        users = cfg["credentials"]["usernames"]
        check(f"all {len(mac.USERS)} users present", set(users) == set(mac.USERS),
              str(sorted(users)))

        # The point of the whole exercise: can these credentials actually log in?
        for u in mac.USERS:
            h = users[u]["password"].encode()
            check(f"  {u}: bcrypt hash opens with its password",
                  bcrypt.checkpw(pw[u].encode(), h))
            check(f"  {u}: plaintext not stored", users[u]["password"] != pw[u])

        for u, fields in mac.USERS.items():
            check(f"  {u}: roles preserved",
                  users[u]["roles"] == fields["roles"], str(users[u]["roles"]))

        print("\n--- second call is a no-op ---")
        before = path.read_bytes()
        src2 = mac.ensure_config(path, pw, cookie_key="different-key")
        check("returns 'existing'", src2 == "existing", src2)
        check("file untouched", path.read_bytes() == before)

        print("\n--- cold start with no passwords supplied ---")
        p2 = Path(tmp) / "none.yaml"
        src3 = mac.ensure_config(p2, None)
        check("returns 'missing'", src3 == "missing", src3)
        # The whole point: writing an unusable config would let the NEXT rerun
        # report "existing" and silently show a login nobody can open.
        check("writes nothing", not p2.exists())
        check("stays 'missing' on repeat call",
              mac.ensure_config(p2, None) == "missing")

        print("\n--- partial secrets are treated as missing ---")
        p3 = Path(tmp) / "partial.yaml"
        partial = {u: (f"pw-{u}" if u == "admin" else None) for u in mac.USERS}
        src4 = mac.ensure_config(p3, partial)
        check("returns 'missing' on partial input", src4 == "missing", src4)
        check("writes nothing on partial input", not p3.exists())

        print("\n--- build_config rejects incomplete input ---")
        try:
            mac.build_config({"admin": "x"})
            check("raises on missing passwords", False, "no exception")
        except ValueError as e:
            check("raises on missing passwords", True, str(e)[:60])

    print()
    print("RESULT:", "ALL PASSED" if not failures else f"FAILURES: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
