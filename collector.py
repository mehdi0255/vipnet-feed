#!/usr/bin/env python3
"""Collect public proxy configuration links from approved public Telegram pages."""
from __future__ import annotations
import base64, hashlib, html, json, re
from pathlib import Path
from urllib.request import Request, urlopen

CHANNELS = ("persianvpnhub", "vpnproxylinks", "v2ray_dalghak")
OUT = Path("docs/configs.json")
MAX_ITEMS = 1200
UA = "Mozilla/5.0 (compatible; VIPNetFeed/1.0; public-channel-reader)"
PATTERN = re.compile(r"(?:(?:vless|trojan|ss)://[^\s<>\"']+|vmess://[A-Za-z0-9_+/=-]+)", re.I)


def fetch(channel: str) -> str:
    request = Request(f"https://t.me/s/{channel}", headers={"User-Agent": UA})
    with urlopen(request, timeout=35) as reply:
        return reply.read().decode("utf-8", "replace")


def trim(value: str) -> str:
    value = html.unescape(value).strip().rstrip(".,;:!؟،)]}>\"")
    # URI fragments usually contain the source-provided label, not connection data.
    if not value.lower().startswith("vmess://"):
        value = value.split("#", 1)[0]
    return value


def vip_id(seed: str) -> str:
    return "VIP-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:9].upper()


def rename_vmess(value: str, label: str) -> str:
    """Replace the conventional vmess JSON 'ps' display label, retaining connection fields."""
    try:
        encoded = value.split("://", 1)[1]
        encoded += "=" * (-len(encoded) % 4)
        payload = json.loads(base64.b64decode(encoded).decode("utf-8"))
        if isinstance(payload, dict):
            payload["ps"] = label
            raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            return "vmess://" + base64.b64encode(raw).decode("ascii")
    except Exception:
        pass
    return value


def normalize(raw: str) -> tuple[str, str, str] | None:
    value = trim(raw)
    protocol = value.split("://", 1)[0].upper() if "://" in value else ""
    if protocol not in {"VLESS", "VMESS", "TROJAN", "SS"}:
        return None
    label = vip_id(value)
    if protocol == "VMESS":
        value = rename_vmess(value, label)
    return value, label, protocol


def old_entries() -> list[dict]:
    try:
        data = json.loads(OUT.read_text("utf-8"))
        return data.get("configs", []) if isinstance(data, dict) else []
    except (OSError, json.JSONDecodeError):
        return []


def main() -> None:
    collected: list[dict] = []
    failures: list[str] = []
    for channel in CHANNELS:
        try:
            for hit in PATTERN.findall(fetch(channel)):
                item = normalize(hit)
                if item:
                    config, name, protocol = item
                    collected.append({"id": name, "name": name, "protocol": protocol, "config": config})
        except Exception as exc:
            failures.append(f"{channel}: {type(exc).__name__}")

    # Retain previously published items so a config doesn't disappear merely because it
    # has moved off the first public page. New results take priority.
    seen: set[str] = set()
    result: list[dict] = []
    for item in collected + old_entries():
        config = item.get("config") if isinstance(item, dict) else None
        if isinstance(config, str) and config not in seen:
            seen.add(config)
            result.append(item)
        if len(result) >= MAX_ITEMS:
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "version": 1,
        "updatedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "sources": list(CHANNELS),
        "configs": result,
        "warnings": failures,
    }, ensure_ascii=False, separators=(",", ":")), "utf-8")
    print(f"published {len(result)} configs; fetch warnings: {', '.join(failures) or 'none'}")

if __name__ == "__main__":
    main()
