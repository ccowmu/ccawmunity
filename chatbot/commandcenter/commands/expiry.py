from ..command import Command
from ..command import CommandCodeResponse
from ..eventpackage import EventPackage

import ldap3
import requests
import time
from datetime import date
from os import environ
from ldap3.utils.conv import escape_filter_chars

MATRIX_DOMAIN = "cclub.cs.wmich.edu"

class ExpiryCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$expiry"
        self.help = "$expiry | Manage member expiry dates and lifetime membership. | Run $expiry help for usage."
        self.author = "nothingbutflowers, sphinx, krackentosh, airbreak"
        self.last_updated = "Feb. 19, 2026"


        self.LDAP_URL      = environ.get("LDAP_URL", "ldap://openldap:389")
        self.FALLBACK_URL  = "ldap://containers-openldap-1:389"
        self.SYNAPSE_URL   = environ.get("SYNAPSE_URL", "http://synapse:8008")
        self.SYNAPSE_TOKEN = environ.get("SYNAPSE_ADMIN_TOKEN", "")
        self.MEMBER_BASE   = "cn=members,dc=yakko,dc=cs,dc=wmich,dc=edu"
        self.POSIX_DAY     = 86400
        self.DESIRED_FIELDS = ["shadowExpire"]
        self.ADMIN_FIELDS   = ["uid", "cn", "shadowExpire"]

    # ------------------------------------------------------------------ auth

    def _is_officer(self, nick: str) -> bool:
        """
        Check if user is an officer (has access to officer commands).
        """
        conn = None
        try:
            conn = self._bind()
            
            # Check if user is in officers group
            conn.search(
                "cn=officers,dc=yakko,dc=cs,dc=wmich,dc=edu",
                "(objectClass=posixGroup)",
                attributes=["memberUid"]
            )
            if conn.entries:
                officers_group = conn.entries[0]
                if hasattr(officers_group, "memberUid"):
                    members = officers_group.memberUid.values
                    if nick in members:
                        return True
            
            return False
        except Exception as e:
            print(f"LDAP error in _is_officer: {e}")
            return False
        finally:
            if conn and conn.bound:
                try:
                    conn.unbind()
                except Exception:
                    pass

    # ------------------------------------------------------------------ ldap

    def _connect(self, url: str, write=False) -> ldap3.Connection:
        server = ldap3.Server(url, get_info=ldap3.NONE)
        if write:
            dn = environ.get("LDAP_ADMIN_DN", "cn=admin,dc=yakko,dc=cs,dc=wmich,dc=edu")
            pw = environ.get("LDAP_ADMIN_PASSWORD", "")
        else:
            dn = "cn=readonly,dc=yakko,dc=cs,dc=wmich,dc=edu"
            pw = environ.get("LDAP_PASSWORD", "")
        return ldap3.Connection(
            server, user=dn, password=pw,
            auto_bind=True, raise_exceptions=True, receive_timeout=5,
        )

    def _bind(self, write=False) -> ldap3.Connection:
        try:
            return self._connect(self.LDAP_URL, write=write)
        except Exception:
            if self.FALLBACK_URL and self.FALLBACK_URL != self.LDAP_URL:
                return self._connect(self.FALLBACK_URL, write=write)
            raise

    def _ldap_modify(self, dn: str, changes: dict):
        """Open a write connection, apply changes, unbind. Returns None on success, error string on failure."""
        wconn = self._bind(write=True)
        try:
            wconn.modify(dn, changes)
            if wconn.result["result"] != 0:
                return f"Failed to update LDAP: {wconn.result['description']}"
        finally:
            try:
                if wconn.bound:
                    wconn.unbind()
            except Exception:
                pass
        return None

    def _fmt_date(self, days_since_epoch: int) -> str:
        return date.fromtimestamp(int(days_since_epoch) * self.POSIX_DAY).strftime("%Y-%m-%d")

    def _find_member(self, conn: ldap3.Connection, name: str, attrs):
        safe = escape_filter_chars(name)
        conn.search(
            search_base=self.MEMBER_BASE,
            search_filter=f"(|(uid={safe})(cn={safe}))",
            search_scope=ldap3.SUBTREE,
            attributes=attrs,
            size_limit=1,
        )
        return conn.entries[0] if conn.entries else None

    def _get_shadow_expire(self, entry):
        if not entry:
            return None
        try:
            val = entry["shadowExpire"].value
            return int(val) if val not in (None, "") else None
        except Exception:
            return None

    def _get_lifetime_members(self, conn: ldap3.Connection):
        """Get list of lifetime members (no shadowExpire attribute)."""
        results = []
        for entry in conn.extend.standard.paged_search(
            search_base=self.MEMBER_BASE,
            search_filter="(&(objectClass=shadowAccount)(!(shadowExpire=*)))",
            search_scope=ldap3.SUBTREE,
            attributes=["uid", "cn"],
            paged_size=200, generator=True,
        ):
            if entry.get("type") != "searchResEntry":
                continue
            attrs = entry.get("attributes", {}) or {}
            uid = attrs.get("uid") or attrs.get("cn") or ""
            # Handle LDAP attribute that might be a list or bytes
            if isinstance(uid, list):
                uid = uid[0] if uid else ""
            if isinstance(uid, bytes):
                uid = uid.decode()
            if uid:
                results.append(str(uid))
        return sorted(results)
    
    def _ping_free(self, username: str) -> str:
        """Replace a character with lookalike to prevent Matrix mentions."""
        if not username:
            return username
        # Replace common letters with Unicode lookalikes
        replacements = {'a': 'а', 'e': 'е', 'o': 'о', 'c': 'с', 'p': 'р'}  # Cyrillic lookalikes
        for ascii_char, cyrillic_char in replacements.items():
            if ascii_char in username.lower():
                # Replace first occurrence (case-insensitive)
                idx = username.lower().index(ascii_char)
                return username[:idx] + cyrillic_char + username[idx+1:]
        return username

    def _expired_members_paged(self, conn: ldap3.Connection):
        today_days = int(time.time()) // self.POSIX_DAY
        results = []
        for entry in conn.extend.standard.paged_search(
            search_base=self.MEMBER_BASE,
            search_filter=f"(shadowExpire<={today_days})",
            search_scope=ldap3.SUBTREE,
            attributes=self.ADMIN_FIELDS,
            paged_size=200, generator=True,
        ):
            if entry.get("type") != "searchResEntry":
                continue
            attrs = entry.get("attributes", {}) or {}
            uid = attrs.get("uid") or attrs.get("cn") or entry.get("dn") or ""
            exp = attrs.get("shadowExpire")
            if isinstance(exp, list):
                exp = exp[0] if exp else None
            if exp not in (None, ""):
                results.append((str(uid), self._fmt_date(int(exp))))
        return results

    # ------------------------------------------------------------------ synapse

    def _synapse_headers(self):
        return {"Authorization": f"Bearer {self.SYNAPSE_TOKEN}"}

    def _synapse_suspend(self, uid: str) -> str:
        if not self.SYNAPSE_TOKEN:
            return "SYNAPSE_ADMIN_TOKEN not set."
        user_id = requests.utils.quote(f"@{uid}:{MATRIX_DOMAIN}")
        url = f"{self.SYNAPSE_URL}/_synapse/admin/v1/suspend/{user_id}"
        try:
            r = requests.put(url, json={"suspend": True},
                             headers=self._synapse_headers(), timeout=10)
            return None if r.status_code == 200 else f"Synapse error {r.status_code}: {r.text}"
        except requests.RequestException as e:
            return f"Synapse unreachable: {e}"

    def _synapse_unsuspend(self, uid: str) -> str:
        if not self.SYNAPSE_TOKEN:
            return "SYNAPSE_ADMIN_TOKEN not set."
        user_id = requests.utils.quote(f"@{uid}:{MATRIX_DOMAIN}")
        url = f"{self.SYNAPSE_URL}/_synapse/admin/v1/suspend/{user_id}"
        try:
            r = requests.put(url, json={"suspend": False},
                             headers=self._synapse_headers(), timeout=10)
            return None if r.status_code == 200 else f"Synapse error {r.status_code}: {r.text}"
        except requests.RequestException as e:
            return f"Synapse unreachable: {e}"

    # ------------------------------------------------------------------ commands

    def _cmd_all_expired(self, conn, args):
        rows = self._expired_members_paged(conn)
        if not rows:
            return "No expired members found."
        rows.sort(key=lambda x: x[0])
        return CommandCodeResponse("\n".join(f"{u}: {d}" for u, d in rows))

    def _cmd_set_expiry(self, conn, args):
        if len(args) < 3:
            return "Usage: $expiry -s <user> <YYYY-MM-DD>"
        target, date_str = args[1], args[2]
        try:
            d = date.fromisoformat(date_str)
        except ValueError:
            return f"Invalid date: {date_str} (use YYYY-MM-DD)"
        entry = self._find_member(conn, target, ["uid", "shadowExpire"])
        if not entry:
            return f"No member found for '{target}'."
        new_days = (d - date(1970, 1, 1)).days
        err = self._ldap_modify(entry.entry_dn, {"shadowExpire": [(ldap3.MODIFY_REPLACE, [new_days])]})
        if err:
            return err
        return f"Set {target} expiry to {date_str}."

    def _cmd_unsuspend(self, conn, args):
        if len(args) < 2:
            return "Usage: $expiry -r <user>"
        target = args[1]
        entry = self._find_member(conn, target, ["uid"])
        if not entry:
            return f"No member found for '{target}'."
        uid = str(entry["uid"].value)
        err = self._synapse_unsuspend(uid)
        if err:
            return err
        return f"Unsuspended @{uid} — they can now send messages and use chat."

    def _cmd_suspend(self, conn, args):
        if len(args) < 2:
            return "Usage: $expiry -d <user>"
        target = args[1]
        entry = self._find_member(conn, target, ["uid"])
        if not entry:
            return f"No member found for '{target}'."
        uid = str(entry["uid"].value)
        err = self._synapse_suspend(uid)
        if err:
            return err
        return f"Suspended @{uid} — chat access blocked (stays in rooms, settings preserved)."

    def _cmd_lifetime(self, conn, args):
        """Manage lifetime membership (no expiry, no dues)."""
        sub = args[1] if len(args) > 1 else "list"

        if sub == "list":
            # Get lifetime members using the helper function
            results = self._get_lifetime_members(conn)
            if not results:
                return "No lifetime members."
            # Make usernames ping-free to avoid notifications
            ping_free_names = [self._ping_free(uid) for uid in results]
            return CommandCodeResponse("\n".join(ping_free_names))

        if sub == "add":
            if len(args) < 3:
                return "Usage: $expiry -lifetime add <user>"
            target = args[2]
            entry = self._find_member(conn, target, ["uid", "shadowExpire"])
            if not entry:
                return f"No member found for '{target}'."
            err = self._ldap_modify(entry.entry_dn, {"shadowExpire": [(ldap3.MODIFY_DELETE, [])]})
            if err:
                return err
            return f"✅ Granted lifetime membership to {target} — no expiry, no dues."

        if sub == "rm":
            if len(args) < 3:
                return "Usage: $expiry -lifetime rm <user>"
            target = args[2]
            return f"Use $expiry -set {target} <YYYY-MM-DD> to set their expiry date."

        return "Usage: $expiry -lifetime [list | add <user> | rm <user>]"

    # ------------------------------------------------------------------ run

    def run(self, event_pack: EventPackage):
        args = event_pack.body[1:]
        sender = event_pack.sender
        nick = sender.split(":")[0][1:]
        
        # Bot Protection: Block bot accounts from using this command (defense in depth).
        # Framework (chat.py) already blocks these via botconfig.ignored, but we add
        # an explicit check here for security-sensitive operations.
        BOT_ACCOUNTS = ["rustix", "ccawmu", "fish", "scoob"]
        if nick.lower() in [b.lower() for b in BOT_ACCOUNTS]:
            return  # Silent ignore, consistent with framework behavior

        if args and args[0] == "help":
            is_officer = self._is_officer(nick)
            lines = [
                "$expiry            — View your expiry date",
                "$expiry <user>     — View someone's expiry date",
            ]
            if is_officer:
                lines += [
                    "",
                    "━━ Officer Commands ━━",
                    "$expiry -set <user> <YYYY-MM-DD>   — Set expiry date",
                    "$expiry -suspend <user>            — Suspend chat access",
                    "$expiry -unsuspend <user>          — Restore chat access",
                    "$expiry -expired                   — List expired members",
                    "",
                    "━━ Lifetime Membership ━━",
                    "$expiry -lifetime list             — List lifetime members",
                    "$expiry -lifetime add <user>       — Grant lifetime membership",
                    "$expiry -lifetime rm <user>        — Remove lifetime membership",
                ]
            return CommandCodeResponse("\n".join(lines))

        try:
            conn = self._bind()
        except Exception as e:
            print("LDAP bind error:", e)
            return "Failed to bind to LDAP (unreachable or bad creds)."

        try:
            OFFICER_CMDS = {
                "-set": self._cmd_set_expiry,
                "-suspend": self._cmd_suspend,
                "-unsuspend": self._cmd_unsuspend,
                "-expired": self._cmd_all_expired,
                "-lifetime": self._cmd_lifetime,
            }

            if args and args[0] in OFFICER_CMDS:
                if not self._is_officer(nick):
                    return "⛔ Officer access required."
                return OFFICER_CMDS[args[0]](conn, args)


            # show expiry for caller (no args) or named user
            target = args[0] if args else nick
            entry = self._find_member(conn, target, self.DESIRED_FIELDS)
            if not entry:
                return f"No member found for '{target}'."
            exp = self._get_shadow_expire(entry)
            if exp is None:
                return f"{target} doesn't expire!"
            return f"{target}: {self._fmt_date(exp)}"

        except ldap3.core.exceptions.LDAPException as e:
            print("LDAP error:", e)
            return "Failed to query LDAP server."
        except Exception as e:
            print("Unexpected error:", e)
            return "An error occurred while processing your request."
        finally:
            try:
                if conn.bound:
                    conn.unbind()
            except Exception:
                pass
