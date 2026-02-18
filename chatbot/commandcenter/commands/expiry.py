from ..command import Command
from ..command import CommandCodeResponse
from ..eventpackage import EventPackage

import ldap3
import time
from datetime import date
from os import environ
from ldap3.utils.conv import escape_filter_chars

class ExpiryCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = "$expiry"
        self.help = (
            "$expiry | Manage member expiry dates. | "
            "Usage: $expiry [user] | $expiry -a | "
            "$expiry -s <user> <YYYY-MM-DD> | "
            "$expiry -w [list | add <user> | rm <user>]"
        )
        self.author = "nothingbutflowers, sphinx, krackentosh"
        self.last_updated = "Feb. 18, 2026"
        self.whitelist = ["crosstangent", "kahrl", "sphinx", "rezenee", "estlin", "krackentosh"]

        self.LDAP_URL = environ.get("LDAP_URL", "ldap://openldap:389")
        self.FALLBACK_URL = "ldap://containers-openldap-1:389"
        self.MEMBER_BASE = "cn=members,dc=yakko,dc=cs,dc=wmich,dc=edu"
        self.POSIX_DAY = 86400
        self.DESIRED_FIELDS = ["shadowExpire"]
        self.ADMIN_FIELDS = ["uid", "cn", "shadowExpire"]

    def _is_admin(self, nick: str) -> bool:
        if nick == "airbreak" or nick in self.whitelist:
            return True
        return any(nick == m.decode() for m in self.db_set_get("admin_whitelist"))

    def _connect(self, url: str, write=False) -> ldap3.Connection:
        server = ldap3.Server(url, get_info=ldap3.NONE)
        if write:
            dn = environ.get("LDAP_ADMIN_DN", "cn=admin,dc=yakko,dc=cs,dc=wmich,dc=edu")
            pw = environ.get("LDAP_ADMIN_PASSWORD", "")
        else:
            dn = "cn=readonly,dc=yakko,dc=cs,dc=wmich,dc=edu"
            pw = environ.get("LDAP_PASSWORD", "")
        return ldap3.Connection(
            server,
            user=dn,
            password=pw,
            auto_bind=True,
            raise_exceptions=True,
            receive_timeout=5,
        )

    def _bind(self, write=False) -> ldap3.Connection:
        try:
            return self._connect(self.LDAP_URL, write=write)
        except Exception:
            if self.FALLBACK_URL and self.FALLBACK_URL != self.LDAP_URL:
                return self._connect(self.FALLBACK_URL, write=write)
            raise

    def _fmt_date(self, days_since_epoch: int) -> str:
        return date.fromtimestamp(int(days_since_epoch) * self.POSIX_DAY).strftime("%Y-%m-%d")

    def _find_member(self, conn: ldap3.Connection, name: str, attrs):
        safe = escape_filter_chars(name)
        filt = f"(|(uid={safe})(cn={safe}))"
        conn.search(
            search_base=self.MEMBER_BASE,
            search_filter=filt,
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
            if val in (None, ""):
                return None
            return int(val)
        except Exception:
            return None

    def _expired_members_paged(self, conn: ldap3.Connection):
        today_days = int(time.time()) // self.POSIX_DAY
        filt = f"(shadowExpire<={today_days})"
        results = []
        for entry in conn.extend.standard.paged_search(
            search_base=self.MEMBER_BASE,
            search_filter=filt,
            search_scope=ldap3.SUBTREE,
            attributes=self.ADMIN_FIELDS,
            paged_size=200,
            generator=True,
        ):
            if entry.get("type") != "searchResEntry":
                continue
            attrs = entry.get("attributes", {}) or {}
            uid = attrs.get("uid")
            cn = attrs.get("cn")
            label = uid or cn or entry.get("dn") or ""
            exp = attrs.get("shadowExpire")
            if isinstance(exp, list):
                exp = exp[0] if exp else None
            if exp not in (None, ""):
                results.append((str(label), self._fmt_date(int(exp))))
        return results

    def _cmd_set_expiry(self, conn, args):
        if len(args) < 3:
            return "Usage: $expiry -s <user> <YYYY-MM-DD>"
        target, date_str = args[1], args[2]
        try:
            d = date.fromisoformat(date_str)
        except ValueError:
            return f"Invalid date: {date_str} (use YYYY-MM-DD)"
        new_days = (d - date(1970, 1, 1)).days
        entry = self._find_member(conn, target, ["uid", "shadowExpire"])
        if not entry:
            return f"I don't know who {target} is!"
        wconn = self._bind(write=True)
        try:
            wconn.modify(entry.entry_dn, {"shadowExpire": [(ldap3.MODIFY_REPLACE, [new_days])]})
            if wconn.result["result"] != 0:
                return f"LDAP modify failed: {wconn.result['description']}"
        finally:
            try:
                if wconn.bound:
                    wconn.unbind()
            except Exception:
                pass
        return f"Set {target} expiry to {date_str}."

    def _cmd_whitelist(self, args):
        sub = args[1] if len(args) > 1 else "list"
        if sub == "list":
            base = sorted(set(self.whitelist) | {"airbreak"})
            extra = sorted(m.decode() for m in self.db_set_get("admin_whitelist"))
            lines = [f"{u} (base)" for u in base] + [f"{u} (added)" for u in extra]
            return CommandCodeResponse("\n".join(lines) if lines else "whitelist is empty")
        if sub in ("add", "rm") and len(args) > 2:
            user = args[2]
            if user in self.whitelist or user == "airbreak":
                return f"{user} is already in the base whitelist."
            if sub == "add":
                self.db_set_add("admin_whitelist", user)
                return f"Added {user} to admin whitelist."
            else:
                self.db_set_remove("admin_whitelist", user)
                return f"Removed {user} from admin whitelist."
        return "Usage: $expiry -w [list | add <user> | rm <user>]"

    def run(self, event_pack: EventPackage):
        args = event_pack.body[1:]
        nick = event_pack.sender.split(":")[0][1:]

        # whitelist-only commands that don't need LDAP
        if args and args[0] == "-w":
            if not self._is_admin(nick):
                return "You don't have permission to use this command."
            return self._cmd_whitelist(args)

        try:
            conn = self._bind()
        except Exception as e:
            print("LDAP bind error:", e)
            return "Failed to bind to LDAP (unreachable or bad creds)."

        try:
            if not args:
                entry = self._find_member(conn, nick, self.DESIRED_FIELDS)
                if not entry:
                    return f"I don't know who {nick} is!"
                exp = self._get_shadow_expire(entry)
                if exp is None:
                    return f"{nick} doesn't expire!"
                return f"{nick}: {self._fmt_date(exp)}"

            if args[0] == "-a":
                if not self._is_admin(nick):
                    return "You don't have permission to use this command."
                rows = self._expired_members_paged(conn)
                if not rows:
                    return "No expired members found."
                rows.sort(key=lambda x: x[0])
                return CommandCodeResponse("\n".join(f"{u}: {d}" for u, d in rows))

            if args[0] == "-s":
                if not self._is_admin(nick):
                    return "You don't have permission to use this command."
                return self._cmd_set_expiry(conn, args)

            target = args[0]
            entry = self._find_member(conn, target, self.DESIRED_FIELDS)
            if not entry:
                return f"I don't know who {target} is!"
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
