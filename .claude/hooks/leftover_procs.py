"""Stop and SubagentStop hook: block the end of a turn while servers or browsers from this repo still run."""

import json
import os
import subprocess
import sys

SERVER_MARKERS = ("uvicorn", "vite", "serve.py", "http.server", "Google Chrome")
OWN_MARKERS = ("cdp-verify",)
IGNORED_EXECUTABLES = ("zsh", "bash", "sh", "claude")


def server_processes() -> dict[int, str]:
    ps = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True, check=True)
    servers = {}
    for line in ps.stdout.splitlines():
        pid, _, command = line.strip().partition(" ")
        if os.path.basename(command.split(" ", 1)[0]) in IGNORED_EXECUTABLES or "Helper" in command:
            continue
        if any(marker in command for marker in SERVER_MARKERS):
            servers[int(pid)] = command
    return servers


def working_dirs(pids: list[int]) -> dict[int, str]:
    lsof = subprocess.run(
        ["lsof", "-a", "-d", "cwd", "-Fpn", "-p", ",".join(map(str, pids))], capture_output=True, text=True
    )
    dirs, pid = {}, 0
    for field in lsof.stdout.splitlines():
        if field.startswith("p"):
            pid = int(field[1:])
        elif field.startswith("n"):
            dirs[pid] = field[1:]
    return dirs


def leftover_processes(repo: str) -> list[str]:
    servers = server_processes()
    if not servers:
        return []
    dirs = working_dirs(list(servers))
    return [
        f"  {pid} {command[:140]}"
        for pid, command in servers.items()
        if repo in command
        or (dirs.get(pid, "") + "/").startswith(repo)
        or any(marker in command for marker in OWN_MARKERS)
    ]


def main() -> int:
    event = json.load(sys.stdin)
    if event.get("stop_hook_active"):
        return 0
    repo = (os.environ.get("CLAUDE_PROJECT_DIR") or event["cwd"]).rstrip("/") + "/"
    found = leftover_processes(repo)
    if not found:
        return 0
    print(
        "Still running from this repo:\n" + "\n".join(found) + "\n"
        "Stop them before you finish, or tell the user why they must stay open.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
