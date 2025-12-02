"""
📱 MOBILE SECURITY EDUCATION TOOL
🛡️ Termux-Compatible Network Simulator
⚡ Safe & Legal Simulation Only
"""

import sys
import os
import time
import random
import socket
import threading
from datetime import datetime

# Telefon kontrolü
IS_TERMUX = 'com.termux' in sys.executable.lower() if sys.executable else False

class MobileSecurityTool:
    def __init__(self):
        self.version = "2.0"
        self.author = "Security Education"
        self.is_mobile = IS_TERMUX
        self.config = self.load_config()
        
    def load_config(self):
        """Telefon için güvenli config"""
        return {
            "max_threads": 3 if self.is_mobile else 10,
            "timeout": 5,
            "packet_size": 128,
            "simulation_mode": True,
            "max_targets": 1,
            "cooldown": 2
        }
    
    def clear_screen(self):
        """Platforma göre ekran temizle"""
        os.system('clear' if self.is_mobile or os.name != 'nt' else 'cls')
    
    def display_banner(self):
        """Ana banner"""
        banner = f"""
╔══════════════════════════════════════════════╗
║      📱 MOBILE SECURITY SIMULATOR v{self.version}     ║
║          Educational Purposes Only           ║
║      Running on: {'Termux' if self.is_mobile else 'PC'}             ║
╚══════════════════════════════════════════════╝
        """
        print(banner)
    
    def display_menu(self):
        """Ana menü"""
        menu = """
[1] 🎮 Game Server Test
[2] 🌐 Website Ping Test  
[3] 🔧 Connection Test
[4] 📊 System Info
[5] ⚠️  Legal Warning
[6] 🚪 Exit

Select option: """
        print(menu)
    
    def game_server_test(self):
        """Oyun server test simülasyonu"""
        self.clear_screen()
        print("🎮 GAME SERVER TEST SIMULATION")
        print("="*40)
        
        games = {
            "1": ("Roblox", "192.168.1.100"),
            "2": ("Minecraft", "mc.hypixel.net"),
            "3": ("Discord Voice", "162.159.135.234")
        }
        
        print("\nSelect game:")
        for key, (name, _) in games.items():
            print(f"[{key}] {name}")
        
        choice = input("\nChoice: ")
        if choice not in games:
            print("Invalid choice!")
            return
        
        game_name, default_ip = games[choice]
        
        print(f"\nGame: {game_name}")
        ip = input(f"Server IP/Address [{default_ip}]: ") or default_ip
        
        print(f"\n🔍 Testing {game_name} server at {ip}...")
        
        # Simüle edilmiş test
        for i in range(5):
            time.sleep(0.5)
            latency = random.randint(20, 100)
            print(f"  Ping {i+1}: {latency}ms")
        
        print(f"\n✅ {game_name} server is reachable")
        print("📊 Average latency: 45ms")
        print("⚠️  This is a SIMULATION only")
    
    def website_ping_test(self):
        """Website ping testi"""
        self.clear_screen()
        print("🌐 WEBSITE PING TEST")
        print("="*40)
        
        url = input("\nEnter website URL (e.g., google.com): ")
        if not url:
            url = "google.com"
        
        print(f"\n🔍 Pinging {url}...")
        
        # Simüle edilmiş ping testi
        results = []
        for i in range(4):
            time.sleep(0.7)
            ping = random.randint(10, 150)
            results.append(ping)
            print(f"  Reply from {url}: time={ping}ms")
        
        avg = sum(results) // len(results)
        print(f"\n📊 Ping statistics for {url}:")
        print(f"  Minimum: {min(results)}ms")
        print(f"  Maximum: {max(results)}ms")
        print(f"  Average: {avg}ms")
        print(f"  Packets: 4 sent, 4 received")
    
    def connection_test(self):
        """Bağlantı testi"""
        self.clear_screen()
        print("🔧 CONNECTION TEST")
        print("="*40)
        
        print("\n🔍 Testing network configuration...")
        time.sleep(1)
        
        tests = [
            ("Localhost", "127.0.0.1", True),
            ("Google DNS", "8.8.8.8", random.choice([True, False])),
            ("Cloudflare", "1.1.1.1", random.choice([True, False]))
        ]
        
        for name, ip, status in tests:
            print(f"\n  Testing {name} ({ip})...")
            time.sleep(0.5)
            if status:
                print(f"    ✅ Reachable (simulated)")
            else:
                print(f"    ❌ Unreachable (simulated)")
        
        print("\n📊 Network Status Summary:")
        print("  Internet: Connected (simulated)")
        print("  Latency: Good (simulated)")
        print("  Stability: Excellent (simulated)")
    
    def system_info(self):
        """Sistem bilgisi"""
        self.clear_screen()
        print("📊 SYSTEM INFORMATION")
        print("="*40)
        
        info = {
            "Platform": sys.platform,
            "Python Version": sys.version.split()[0],
            "Running on": "Termux (Mobile)" if self.is_mobile else "Desktop",
            "Processor": "ARM (Mobile)" if self.is_mobile else "x86/x64",
            "Max Threads": self.config["max_threads"],
            "Simulation Mode": "ACTIVE",
            "Legal Compliance": "EDUCATIONAL USE ONLY"
        }
        
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    def legal_warning(self):
        """Yasal uyarı"""
        self.clear_screen()
        print("⚠️  LEGAL WARNING & DISCLAIMER")
        print("="*50)
        
        warnings = [
            "THIS TOOL IS FOR EDUCATIONAL PURPOSES ONLY",
            "Unauthorized network attacks are ILLEGAL",
            "You are responsible for your own actions",
            "Respect all laws and regulations",
            "Use this knowledge to PROTECT systems, not attack",
            "Report vulnerabilities responsibly",
            "Stay ethical and legal"
        ]
        
        for warning in warnings:
            print(f"\n🔸 {warning}")
        
        print("\n" + "="*50)
        print("By using this tool, you agree to:")
        print("1. Use only on systems you own")
        print("2. Never attack without permission")
        print("3. Follow all applicable laws")
        print("="*50)
        
        input("\nPress Enter to acknowledge and continue...")
    
    def run(self):
        """Ana çalıştırıcı"""
        self.legal_warning()
        
        while True:
            self.clear_screen()
            self.display_banner()
            self.display_menu()
            
            choice = input().strip()
            
            if choice == "1":
                self.game_server_test()
            elif choice == "2":
                self.website_ping_test()
            elif choice == "3":
                self.connection_test()
            elif choice == "4":
                self.system_info()
            elif choice == "5":
                self.legal_warning()
                continue
            elif choice == "6":
                print("\n👋 Thank you for using Security Education Tool!")
                print("🔒 Stay safe and ethical!")
                time.sleep(2)
                break
            else:
                print("\n❌ Invalid choice! Please select 1-6")
                time.sleep(1)
                continue
            
            input("\nPress Enter to continue...")

def main():
    """Giriş noktası"""
    print("Initializing Mobile Security Tool...")
    time.sleep(1)
    
    tool = MobileSecurityTool()
    tool.run()

if __name__ == "__main__":
    main()