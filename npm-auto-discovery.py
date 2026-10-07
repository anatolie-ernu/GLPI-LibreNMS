#!/usr/bin/env python3

"""
Nginx Proxy Manager - Auto-Discovery Service

Scanează containerele Docker cu labels npm.expose=true
și crează proxy hosts automat în Nginx Proxy Manager.

Labels Docker acceptate:
  npm.expose: "true"              # Activează auto-discovery
  npm.hostname: "app"             # Domain: app.local (default: container name)
  npm.port: "8080"                # Port forward (default: 80)
  npm.ssl: "true"                 # Force SSL redirect (default: false)
  npm.websockets: "true"          # WebSocket support (default: false)
"""

import os
import sys
import json
import time
import logging
import requests
import docker
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask
import threading

# ============================================================================
# CONFIGURARE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURARE VARIABILE
# ============================================================================

NPM_API_URL = os.getenv('NPM_API_URL', 'http://nginx-proxy-manager:81/api')
NPM_ADMIN_EMAIL = os.getenv('NPM_ADMIN_EMAIL', 'admin@ernu.md')
NPM_ADMIN_PASSWORD = os.getenv('NPM_ADMIN_PASSWORD', 'Npm@ernu2025!')
DISCOVERY_INTERVAL = int(os.getenv('DISCOVERY_INTERVAL', '300'))  # 5 min default
DOMAIN_SUFFIX = os.getenv('DOMAIN_NAME', 'local')  # Matches .env configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info').upper()

# Docker client
DOCKER_CLIENT = docker.from_env()

# Flask app pentru health check
app = Flask(__name__)

# ============================================================================
# NPM API CLIENT
# ============================================================================

class NPMClient:
    """Client pentru Nginx Proxy Manager API"""
    
    def __init__(self, base_url: str, email: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.token = None
        self.token_expiry = 0
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'NPM-AutoDiscovery/1.0'
        })
    
    def authenticate(self) -> bool:
        """Obține token de autentificare"""
        try:
            logger.info("Autentificare la NPM...")
            response = self.session.post(
                f"{self.base_url}/tokens",
                json={
                    'identity': self.email,
                    'secret': self.password
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')
            self.token_expiry = time.time() + 3600  # 1 hour validity
            
            logger.info(f"✓ Autentificare reușită (Token: {self.token[:20]}...)")
            self._update_headers()
            return True
            
        except requests.RequestException as e:
            logger.error(f"✗ Autentificare eșuată: {e}")
            return False
    
    def _update_headers(self):
        """Update Authorization header"""
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
    
    def ensure_authenticated(self) -> bool:
        """Verifica și reînnodește autentificarea dacă expirat"""
        if not self.token or time.time() >= self.token_expiry:
            return self.authenticate()
        return True
    
    def get_proxy_hosts(self) -> List[Dict]:
        """Obține lista proxy hosts existente"""
        if not self.ensure_authenticated():
            return []
        
        try:
            response = self.session.get(
                f"{self.base_url}/nginx/proxy-hosts",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"⚠ Eroare la obținerea proxy hosts: {e}")
            return []
    
    def create_proxy_host(self, 
                         domain: str,
                         forward_host: str,
                         forward_port: int,
                         websockets: bool = False,
                         ssl_forced: bool = False) -> bool:
        """Crează un proxy host nou"""
        if not self.ensure_authenticated():
            return False
        
        try:
            payload = {
                'domain_names': [domain],
                'forward_scheme': 'http',
                'forward_host': forward_host,
                'forward_port': forward_port,
                'caching_enabled': False,
                'certificate_id': None,
                'ssl_forced': ssl_forced,
                'http2_support': True,
                'websockets_support': websockets,
                'access_list_id': 0,
                'advanced_config': '',
                'meta': {},
                'allow_websocket_upgrade': websockets
            }
            
            response = self.session.post(
                f"{self.base_url}/nginx/proxy-hosts",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"✓ Proxy creat: {domain} → {forward_host}:{forward_port}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"✗ Eroare creare proxy {domain}: {e}")
            return False
    
    def delete_proxy_host(self, proxy_id: int) -> bool:
        """Șterge un proxy host"""
        if not self.ensure_authenticated():
            return False
        
        try:
            response = self.session.delete(
                f"{self.base_url}/nginx/proxy-hosts/{proxy_id}",
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"✓ Proxy șters: ID {proxy_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"✗ Eroare ștergere proxy: {e}")
            return False

# ============================================================================
# DOCKER DISCOVERY
# ============================================================================

class DockerDiscovery:
    """Descoperă containerele Docker cu label npm.expose=true"""
    
    def __init__(self, client: docker.DockerClient):
        self.client = client
    
    def get_containers_to_expose(self) -> List[Dict]:
        """Obține containerele care trebuie expuse"""
        containers = []
        
        try:
            for container in self.client.containers.list():
                labels = container.labels or {}
                
                # Verifică label npm.expose
                if labels.get('npm.expose', 'false').lower() != 'true':
                    continue
                
                container_info = self._parse_container(container, labels)
                if container_info:
                    containers.append(container_info)
                    logger.debug(f"  └─ {container_info['domain']}")
        
        except docker.errors.DockerException as e:
            logger.error(f"✗ Eroare Docker: {e}")
        
        return containers
    
    def _parse_container(self, container, labels: Dict) -> Optional[Dict]:
        """Parsează informații din container și labels"""
        try:
            container_name = container.name
            container_ip = container.attrs['NetworkSettings']['Networks']
            
            # Găsește rețeaua (assume prima rețea disponibilă)
            network_name = next(iter(container_ip.keys())) if container_ip else None
            if not network_name:
                logger.warning(f"⚠ Container {container_name} nu e conectat la rețea")
                return None
            
            forward_host = container_ip[network_name]['IPAddress']
            if not forward_host:
                logger.warning(f"⚠ Container {container_name} nu are IP")
                return None
            
            # Parseaza labels
            hostname = labels.get('npm.hostname', container_name)
            port = int(labels.get('npm.port', '80'))
            websockets = labels.get('npm.websockets', 'false').lower() == 'true'
            ssl_forced = labels.get('npm.ssl', 'false').lower() == 'true'
            
            return {
                'container_name': container_name,
                'container_id': container.id[:12],
                'domain': f"{hostname}.{DOMAIN_SUFFIX}",
                'forward_host': forward_host,
                'forward_port': port,
                'websockets': websockets,
                'ssl_forced': ssl_forced
            }
        
        except (KeyError, ValueError) as e:
            logger.warning(f"⚠ Eroare parsing container: {e}")
            return None

# ============================================================================
# SYNCHRONIZER
# ============================================================================

class DiscoverySynchronizer:
    """Sincronizează containerele Docker cu proxy hosts în NPM"""
    
    def __init__(self, npm_client: NPMClient, docker_discovery: DockerDiscovery):
        self.npm = npm_client
        self.docker = docker_discovery
        self.last_sync = {}
    
    def sync(self) -> bool:
        """Sincronizează dockerele cu NPM"""
        logger.info("=" * 70)
        logger.info(f"SYNC START - {datetime.now().strftime('%H:%M:%S')}")
        
        # Obține containerele de expus
        containers = self.docker.get_containers_to_expose()
        logger.info(f"Containerele găsite: {len(containers)}")
        
        if containers:
            for info in containers:
                logger.info(f"  • {info['domain']} → {info['forward_host']}:{info['forward_port']}")
        
        # Obține proxy hosts existente din NPM
        existing_proxies = self.npm.get_proxy_hosts()
        existing_domains = {p.get('domain_names', [''])[0]: p for p in existing_proxies}
        
        # Crează proxies noi
        created = 0
        for container in containers:
            domain = container['domain']
            if domain not in existing_domains:
                if self.npm.create_proxy_host(
                    domain=domain,
                    forward_host=container['forward_host'],
                    forward_port=container['forward_port'],
                    websockets=container['websockets'],
                    ssl_forced=container['ssl_forced']
                ):
                    created += 1
        
        if created > 0:
            logger.info(f"✓ Proxies create: {created}")
        
        # TODO: Detectează și șterge proxies orfane
        
        logger.info("=" * 70)
        return True
    
    def start_discovery_loop(self):
        """Loop de sincronizare continuă"""
        logger.info(f"Auto-discovery pornit (interval: {DISCOVERY_INTERVAL}s)")
        
        while True:
            try:
                self.sync()
            except Exception as e:
                logger.error(f"✗ Eroare în discovery loop: {e}", exc_info=True)
            
            time.sleep(DISCOVERY_INTERVAL)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/health')
def health():
    """Endpoint pentru health checks"""
    return {'status': 'ok'}, 200

# ============================================================================
# MAIN
# ============================================================================

def main():
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.info("╔════════════════════════════════════════════════════════════════╗")
    logger.info("║   Nginx Proxy Manager - Auto-Discovery Service v1.0           ║")
    logger.info("╚════════════════════════════════════════════════════════════════╝")
    
    logger.info(f"NPM API URL: {NPM_API_URL}")
    logger.info(f"NPM Admin Email: {NPM_ADMIN_EMAIL}")
    logger.info(f"Domain Suffix: {DOMAIN_SUFFIX}")
    logger.info(f"Discovery Interval: {DISCOVERY_INTERVAL}s")
    
    # Initialize clients
    npm_client = NPMClient(NPM_API_URL, NPM_ADMIN_EMAIL, NPM_ADMIN_PASSWORD)
    docker_discovery = DockerDiscovery(DOCKER_CLIENT)
    synchronizer = DiscoverySynchronizer(npm_client, docker_discovery)
    
    # Inițial authenticate
    if not npm_client.authenticate():
        logger.error("✗ Nu pot autentifica cu NPM. Ieșire.")
        sys.exit(1)
    
    # Start Flask health check în background
    def run_flask():
        app.run(host='0.0.0.0', port=8888, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✓ Health check endpoint: http://0.0.0.0:8888/health")
    
    # Start discovery loop
    try:
        synchronizer.start_discovery_loop()
    except KeyboardInterrupt:
        logger.info("\n✓ Auto-discovery stopat")
        sys.exit(0)

if __name__ == '__main__':
    main()
