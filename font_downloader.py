#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import zipfile
from pathlib import Path

def download_google_fonts():
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    fonts_to_download = {
        "Inter": "https://fonts.google.com/download?family=Inter",
        "Roboto": "https://fonts.google.com/download?family=Roboto", 
        "JetBrains Mono": "https://fonts.google.com/download?family=JetBrains%20Mono",
        "Poppins": "https://fonts.google.com/download?family=Poppins",
        "Open Sans": "https://fonts.google.com/download?family=Open%20Sans"
    }
    
    print("🔄 Скачивание шрифтов Google Fonts...")
    
    for font_name, url in fonts_to_download.items():
        try:
            print(f"📥 Скачивание {font_name}...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            zip_path = fonts_dir / f"{font_name.replace(' ', '_')}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            font_folder = fonts_dir / font_name.replace(' ', '_')
            font_folder.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('.ttf'):
                        zip_ref.extract(file_info, font_folder)
            
            zip_path.unlink()
            
            print(f"✅ {font_name} скачан успешно")
            
        except Exception as e:
            print(f"❌ Ошибка при скачивании {font_name}: {e}")
    
    print("🎉 Скачивание шрифтов завершено!")

def install_system_fonts():
    import platform
    
    if platform.system() != "Windows":
        print("⚠️ Автоматическая установка шрифтов поддерживается только в Windows")
        return
    
    try:
        import winreg
        import shutil
        
        fonts_dir = Path("fonts")
        if not fonts_dir.exists():
            print("❌ Папка fonts не найдена")
            return
        
        fonts_folder = Path(os.environ['WINDIR']) / 'Fonts'
        
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
                                0, winreg.KEY_SET_VALUE)
        
        print("📦 Установка шрифтов в систему...")
        
        for ttf_file in fonts_dir.rglob("*.ttf"):
            try:
                dest_path = fonts_folder / ttf_file.name
                shutil.copy2(ttf_file, dest_path)
                
                font_name = ttf_file.stem + " (TrueType)"
                winreg.SetValueEx(reg_key, font_name, 0, winreg.REG_SZ, ttf_file.name)
                
                print(f"✅ Установлен: {ttf_file.name}")
                
            except Exception as e:
                print(f"❌ Ошибка установки {ttf_file.name}: {e}")
        
        winreg.CloseKey(reg_key)
        print("🎉 Установка шрифтов завершена! Перезапустите приложение.")
        
    except Exception as e:
        print(f"❌ Ошибка установки шрифтов: {e}")

if __name__ == "__main__":
    print("🎨 Google Fonts Downloader")
    print("=" * 40)
    
    choice = input("Выберите действие:\n1. Скачать шрифты\n2. Установить в систему\n3. Скачать и установить\nВвод: ")
    
    if choice in ["1", "3"]:
        download_google_fonts()
    
    if choice in ["2", "3"]:
        install_system_fonts()
    
    input("\nНажмите Enter для выхода...") 