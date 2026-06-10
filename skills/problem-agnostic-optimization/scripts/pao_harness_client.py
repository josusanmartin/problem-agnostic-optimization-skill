#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_SERVER_JSON = Path("work/optimization_harness/server.json")


def load_base_url(args: argparse.Namespace) -> str:
    if args.base_url:
        return args.base_url.rstrip("/")

    server_json = Path(args.server_json)
    if not server_json.exists():
        raise SystemExit(f"server discovery file not found: {server_json}")
    with server_json.open(encoding="utf-8") as f:
        data = json.load(f)
    base_url = data.get("base_url")
    if not isinstance(base_url, str) or not base_url.strip():
        raise SystemExit(f"{server_json} missing base_url")
    return base_url.rstrip("/")


def request_json(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(f"{base_url}{path}", data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return response.status, data
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"ok": False, "message": raw}
        return exc.code, data
    except URLError as exc:
        raise SystemExit(f"request failed: {exc}") from exc


def print_response(status: int, data: dict[str, Any]) -> int:
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0 if 200 <= status < 300 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Call a local PAO harness API server.")
    parser.add_argument("--base-url", help="Override server discovery and use this base URL.")
    parser.add_argument("--server-json", type=Path, default=DEFAULT_SERVER_JSON, help="Server discovery JSON written by pao_harness_server.py.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Check server liveness.")
    subparsers.add_parser("contract", help="Print the evaluation contract.")
    subparsers.add_parser("best", help="Print the best candidate tracked by the server.")

    evaluate = subparsers.add_parser("evaluate", help="Evaluate one candidate artifact.")
    evaluate.add_argument("--candidate", required=True, help="Candidate id, for example cand_0042.")
    evaluate.add_argument("--artifact", required=True, help="Candidate artifact path inside project_root.")
    evaluate.add_argument("--parent", help="Parent candidate id.")
    evaluate.add_argument("--label", default="", help="Compact hypothesis/result label for the progress row.")
    evaluate.add_argument("--mechanism", default="", help="Mechanism class, for candidate result artifacts.")
    evaluate.add_argument("--force-candidate-result", action="store_true", help="Ask the server to write a candidate result JSON.")

    refresh = subparsers.add_parser("refresh", help="Refresh sidecar artifacts on demand.")
    refresh.add_argument("--artifact", dest="artifacts", action="append", choices=("dashboard", "chart", "review"), help="Artifact to refresh; may be repeated.")

    args = parser.parse_args(argv)
    base_url = load_base_url(args)

    if args.command == "health":
        status, data = request_json(base_url, "GET", "/health")
    elif args.command == "contract":
        status, data = request_json(base_url, "GET", "/contract")
    elif args.command == "best":
        status, data = request_json(base_url, "GET", "/best")
    elif args.command == "evaluate":
        payload = {
            "candidate_id": args.candidate,
            "artifact_path": args.artifact,
            "parent": args.parent,
            "label": args.label,
            "mechanism": args.mechanism,
        }
        if args.force_candidate_result:
            payload["force_candidate_result"] = True
        status, data = request_json(base_url, "POST", "/evaluate", payload)
    elif args.command == "refresh":
        status, data = request_json(base_url, "POST", "/refresh", {"artifacts": args.artifacts or ["dashboard", "chart"]})
    else:  # pragma: no cover - argparse prevents this.
        raise SystemExit(f"unknown command: {args.command}")

    return print_response(status, data)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
