# Office Presence Setup

## Background

The `$office` command shows who is physically in the CClub office by querying active DHCP leases on the morgana network (192.168.1.0/24).

## Architecture

- **Condor**: Runs Kea DHCP server, maintains `/var/lib/kea/dhcp4.leases`
- **Push Script**: Condor runs `/usr/local/bin/push-dhcp-loop.sh` which periodically pushes the DHCP lease file to yakko
- **Yakko**: Mounts `/tmp/morgana-dhcp.leases` into the office-presence container
- **office-presence**: Docker container on yakko that:
  - Parses the DHCP lease file
  - Reads registered MAC→nick mappings from data/registrations.config
  - Provides REST API endpoints for the bot ($office command)

## Known Issues & Fixes

### Issue: Push script had broken shebang
**File**: `/usr/local/bin/push-dhcp.sh` on condor
**Problem**: Shebang was `#\!/bin/sh` (with extra backslash) instead of `#!/bin/sh`, causing the script to not execute
**Fix**: Corrected the shebang to `#!/bin/sh`
**Also fixed**: Script permissions changed from 755 to 700 for security

### Testing the Fix
```bash
# On yakko:
$ $office  # Should show registered users present on morgana network
```

## Security Notes

- SSH key for push: `/root/.ssh/office_presence_key` on condor (restricted to only write to /tmp/morgana-dhcp.leases)
- DHCP leases contain device MAC addresses; access should be limited
- Push scripts run as root with 700 permissions (owner-only)
