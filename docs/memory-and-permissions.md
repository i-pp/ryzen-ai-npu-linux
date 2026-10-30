# Device access and locked-memory limits

Historical U evidence shows a render-owned accelerator node and an already-render-member user, followed by a 64 MiB mapping error (-11) under an approximately 8 MiB shell limit. Root plus unlimited memlock worked; ordinary-user validation later worked with 1 GiB. The limit is a strong Corroborated explanation, but the first comparison also changed uid. It does not establish the exact minimum required for every workload.

Present files E012/E014 specify 1048576 KiB in PAM and `LimitMEMLOCK=1G` in the correct system service drop-in. The collector's actual soft/hard limits are 1073741824 bytes. Historical U also verified manager and child-service limits. Current effective host service/ACL access cannot be rechecked from this namespace.

## Diagnostic: distinguish four different states

```bash
id
ls -l /dev/accel/accel0
getfacl -p /dev/accel/accel0
ulimit -Sl
ulimit -Hl
prlimit --pid "$$" --memlock
systemctl show "user@$(id -u).service" -p MainPID -p LimitMEMLOCK -p LimitMEMLOCKSoft -p DropInPaths
systemctl --user show -p DefaultLimitMEMLOCK
```

Inspect `/proc/<manager-pid>/limits` and the limits in the actual worker/service too. A file says what was configured; `systemctl show` can show parsed settings; `/proc` shows the running process; a child can inherit or override limits. None alone proves all other contexts.

## Conditional: reviewed configuration on a separate clean host

These commands are **proposed privileged operations, not operations run by this project**. Compare existing files first; never overwrite an administrator's unrelated policy. The snapshot value is 1 GiB, not a workload-independent minimum.

PAM file `/etc/security/limits.d/99-xrt-memlock.conf` should contain the chosen account name, then:

```text
<account> soft memlock 1048576
<account> hard memlock 1048576
```

The real login path must use pam_limits.so; selected PAM files were captured in phase 1. For the system manager's user service, the correct file is `/etc/systemd/system/user@.service.d/99-memlock.conf`:

```ini
[Service]
LimitMEMLOCK=1G
```

After an authorized administrator creates/reviews this drop-in, `sudo systemctl daemon-reload` reloads configuration. It does not retroactively change all running processes. A new login/user-manager lifecycle may be required; capture actual new process limits before claiming success. Restarting the user manager can terminate work, so do this only on the isolated test host. No restart was attempted here.

Group changes are **Conditional** only when actual host membership/access is insufficient. Use the administrator-approved render/ACL policy and a new session if necessary. The user was already in render historically; adding video/render again is not an established required remedy. Do not use world-writable device permissions as a workaround.

## FailedHistorical

The early file under `/etc/systemd/user@.service.d/` was misplaced; copying that path would reproduce the error. It is absent now, but the deletion time/command is Unknown. An unprivileged process cannot simply raise its own hard limit above the inherited hard ceiling; the historical 128 MiB attempt failed with EPERM. Routine root/unlimited validation is not the optimized procedure.

References for the distinction: [getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html), [limits.conf(5)](https://man7.org/linux/man-pages/man5/limits.conf.5.html), [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#LimitCPU=).
