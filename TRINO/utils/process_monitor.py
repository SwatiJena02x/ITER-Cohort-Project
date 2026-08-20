from __future__ import annotations

import os
import platform
import re
import subprocess
from typing import List, Sequence

VM_MARKERS = (
    "virtualbox",
    "vmware",
    "qemu",
    "hyper-v",
    "kvm",
    "docker",
    "wsl",
    "vbox",
    "vm",
)

UNAUTHORIZED_APPS = {
    "zoom",
    "teams",
    "telegram",
    "whatsapp",
    "skype",
    "teamviewer",
    "anydesk",
    "ultravnc",
    "screenconnect",
    "chrome_remote_desktop",
    "remote_desktop",
}


def normalize_process_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def detect_unauthorized_processes(process_names: Sequence[str], watchlist: Sequence[str] | None = None) -> List[dict]:
    watch = {normalize_process_name(item) for item in (watchlist or list(UNAUTHORIZED_APPS))}
    flagged: List[dict] = []
    for app_name in process_names:
        normalized = normalize_process_name(app_name)
        if normalized in watch:
            flagged.append({
                "app_name": app_name,
                "severity": "high",
                "reason": "matched unauthorized process watchlist",
            })
    return flagged


def get_running_processes() -> List[str]:
    system = platform.system().lower()
    try:
        if system == "windows":
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "Get-Process | Select-Object -ExpandProperty ProcessName"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            return [line.strip() for line in output.splitlines() if line.strip()]
        output = subprocess.check_output(["ps", "-eo", "comm="], text=True, stderr=subprocess.DEVNULL)
        return [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        return []


def detect_vm() -> bool:
    combined = " ".join(
        [
            os.environ.get("WSL_DISTRO_NAME", ""),
            platform.platform(),
            platform.release(),
            platform.version(),
        ]
    ).lower()
    for marker in VM_MARKERS[:-1]:
        if marker in combined:
            return True
    return False
