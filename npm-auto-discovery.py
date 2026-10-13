#!/usr/bin/env python3
"""
Nginx Proxy Manager auto-discovery.

Discovers running Docker containers carrying npm.expose=true labels and creates
NPM proxy hosts. Docker API access is expected through docker-socket-proxy,
not through a direct Docker socket mount.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

import docker
import requests
from flask import Flask

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


NPM_API_URL = os.getenv("NPM_API_URL", "http://nginx-proxy-manager:81/api").rstrip("/")
NPM_API_EMAIL = required_env("NPM_API_EMAIL")
NPM_API_PASSWORD = required_env("NPM_API_PASSWORD")
DOMAIN_SUFFIX = required_env("DOMAIN_NAME").strip(".")
DISCOVERY_INTERVAL = int(os.getenv("DISCOVERY_INTERVAL", "300"))

DOCKER_CLIENT = docker.from_env()
app = Flask(__name__)


class NPMClient:
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token: Optional[str] = None
        self.token_expiry = 0.0
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "NPM-AutoDiscovery/2.0"}
        )

    def authenticate(self) -> bool:
        try:
            response = self.session.post(
                f"{self.base_url}/tokens",
                json={"identity": self.email, "secret": self.password},
                timeout=10,
            )
            response.raise_for_status()
            token = response.json().get("token")
            if not token:
                raise RuntimeError("NPM authentication response did not contain a token")
            self.token = token
            self.token_expiry = time.time() + 3300
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            logger.info("NPM authentication succeeded")
            return True
        except (requests.RequestException, RuntimeError) as exc:
            logger.error("NPM authentication failed: %s", exc)
            return False

    def ensure_authenticated(self) -> bool:
        return bool(self.token and time.time() < self.token_expiry) or self.authenticate()

    def get_proxy_hosts(self) -> List[Dict]:
        if not self.ensure_authenticated():
            return []
        try:
            response = self.session.get(f"{self.base_url}/nginx/proxy-hosts", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except requests.RequestException as exc:
            logger.warning("Unable to read NPM proxy hosts: %s", exc)
            return []

    def create_proxy_host(
        self,
        domain: str,
        forward_host: str,
        forward_port: int,
        websockets: bool = False,
    ) -> bool:
        if not self.ensure_authenticated():
            return False
        payload = {
            "domain_names": [domain],
            "forward_scheme": "http",
            "forward_host": forward_host,
            "forward_port": forward_port,
            "caching_enabled": False,
            "certificate_id": 0,
            "ssl_forced": False,
            "http2_support": True,
            "websockets_support": websockets,
            "access_list_id": 0,
            "advanced_config": "",
            "meta": {},
            "allow_websocket_upgrade": websockets,
        }
        try:
            response = self.session.post(
                f"{self.base_url}/nginx/proxy-hosts", json=payload, timeout=10
            )
            response.raise_for_status()
            logger.info("Proxy created: %s -> %s:%s", domain, forward_host, forward_port)
            return True
        except requests.RequestException as exc:
            logger.error("Unable to create proxy %s: %s", domain, exc)
            return False


class DockerDiscovery:
    def __init__(self, client: docker.DockerClient):
        self.client = client

    def get_containers_to_expose(self) -> List[Dict]:
        result: List[Dict] = []
        try:
            for container in self.client.containers.list():
                labels = container.labels or {}
                if labels.get("npm.expose", "false").lower() != "true":
                    continue
                parsed = self._parse_container(container, labels)
                if parsed:
                    result.append(parsed)
        except docker.errors.DockerException as exc:
            logger.error("Docker discovery failed: %s", exc)
        return result

    def _parse_container(self, container, labels: Dict) -> Optional[Dict]:
        try:
            container_name = container.name
            hostname = labels.get("npm.hostname", container_name).strip()
            if not hostname:
                return None
            port = int(labels.get("npm.port", "80"))
            if not 1 <= port <= 65535:
                raise ValueError("invalid port")
            forward_host = labels.get("npm.forward_host", container_name).strip()
            return {
                "domain": f"{hostname}.{DOMAIN_SUFFIX}",
                "forward_host": forward_host,
                "forward_port": port,
                "websockets": labels.get("npm.websockets", "false").lower() == "true",
            }
        except (ValueError, AttributeError) as exc:
            logger.warning("Skipping container %s: %s", getattr(container, "name", "?"), exc)
            return None


class DiscoverySynchronizer:
    def __init__(self, npm: NPMClient, docker_discovery: DockerDiscovery):
        self.npm = npm
        self.docker = docker_discovery

    def sync(self) -> None:
        logger.info("Discovery sync started at %s", datetime.now().isoformat(timespec="seconds"))
        containers = self.docker.get_containers_to_expose()
        existing = self.npm.get_proxy_hosts()
        existing_domains = {
            domain
            for proxy in existing
            for domain in (proxy.get("domain_names") or [])
            if isinstance(domain, str)
        }

        for item in containers:
            if item["domain"] in existing_domains:
                continue
            self.npm.create_proxy_host(
                domain=item["domain"],
                forward_host=item["forward_host"],
                forward_port=item["forward_port"],
                websockets=item["websockets"],
            )

    def run(self) -> None:
        while True:
            try:
                self.sync()
            except Exception:
                logger.exception("Unexpected discovery error")
            time.sleep(DISCOVERY_INTERVAL)


@app.get("/health")
def health():
    return {"status": "ok"}, 200


def main() -> int:
    try:
        DOCKER_CLIENT.ping()
    except docker.errors.DockerException as exc:
        logger.error("Docker API is unavailable: %s", exc)
        return 1

    npm = NPMClient(NPM_API_URL, NPM_API_EMAIL, NPM_API_PASSWORD)
    if not npm.authenticate():
        return 1

    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=8888, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()

    DiscoverySynchronizer(npm, DockerDiscovery(DOCKER_CLIENT)).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
