#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediabay API dan real-time ma'lumotlarni olub IPTV playlist generatsiya qilish
API: https://api.v1.mediabay.tv/v2/channels/thread/339
AsilTV uchun optimallashtirilgan playlist
"""

import requests
import json
from datetime import datetime
import os

# Konfiguratsiya
API_URL = "https://api.v1.mediabay.tv/v2/channels/thread/339"
PLAYLIST_FILE = "AsilTV.m3u8"

def get_channels_from_api():
    """
    Mediabay API dan real-time kanallarni olish
    API: https://api.v1.mediabay.tv/v2/channels/thread/339
    """
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 API dan ma'lumot olinmoqda...")
        print(f"🔗 API URL: {API_URL}")
        
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        # API status tekshirish
        if data.get('status') == 'ok':
            channels = data.get('data', [])
            print(f"✓ {len(channels)} kanal topildi")
            return channels
        else:
            error_msg = data.get('message', 'Noma\'lum xato')
            print(f"✗ API xatosi: {error_msg}")
            return []
    
    except requests.exceptions.Timeout:
        print(f"✗ Ulanish xatosi: Timeout")
        return []
    except requests.exceptions.ConnectionError:
        print(f"✗ Ulanish xatosi: Tarmoq xatosi")
        return []
    except requests.exceptions.RequestException as e:
        print(f"✗ Ulanish xatosi: {e}")
        return []
    except json.JSONDecodeError:
        print(f"✗ JSON tahlil xatosi")
        return []

def create_iptv_playlist(channels):
    """
    AsilTV uchun IPTV playlist yaratish
    Extended M3U8 formatida
    """
    if not channels:
        print("⚠ Qo'shish uchun kanal yo'q")
        return False

    try:
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            # Extended M3U8 header
            f.write("#EXTM3U url-tvg=\"\" tvg-shift=0\n")
            f.write(f"# AsilTV Playlist\n")
            f.write(f"# Yangilandi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# API: {API_URL}\n")
            f.write(f"# Jami kanallar: {len(channels)}\n\n")
            
            for idx, channel in enumerate(channels, 1):
                # API dan olingan ma'lumotlarni ishlatish
                channel_id = channel.get('id', str(idx))
                channel_name = channel.get('name', f'Kanal {idx}')
                url = channel.get('threadAddress', '')
                
                # Ixtiyoriy maydonlar
                logo = channel.get('logo', '')
                group = channel.get('group', 'AsilTV')
                duration = channel.get('duration', '-1')
                tvg_id = channel.get('tvg_id', str(channel_id))

                if url:
                    # EXTINF line
                    extinf = f"#EXTINF:{duration}"
                    
                    # TVG ID
                    extinf += f' tvg-id="{tvg_id}"'
                    
                    # Logo (agar mavjud bo'lsa)
                    if logo:
                        extinf += f' tvg-logo="{logo}"'
                    
                    # Guruh
                    extinf += f' group-title="{group}"'
                    
                    # Kanal nomi
                    extinf += f', {channel_name}\n'
                    
                    f.write(extinf)
                    f.write(f"{url}\n")
                    print(f"✓ [{idx}] {channel_name} qo'shildi")

        print(f"\n✓ {PLAYLIST_FILE} yaratildi ({len(channels)} kanal)")
        return True
    
    except IOError as e:
        print(f"✗ Fayl yozish xatosi: {e}")
        return False

def main():
    """
    Asosiy funksiya - AsilTV playlist generator
    """
    print("="*70)
    print("🎬 AsilTV Playlist Generator (Real-Time API)")
    print(f"⏰ Vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 API: {API_URL}")
    print("="*70)
    print()

    # API dan kanallarni olish
    channels = get_channels_from_api()

    # IPTV playlist yaratish
    if channels:
        create_iptv_playlist(channels)
        
        print("\n✅ AsilTV Playlist tayyor!")
        print(f"\n📋 Fayl: {os.path.abspath(PLAYLIST_FILE)}")
        print(f"🔄 Yangilash vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 IPTV ilovasiga qo'shish:")
        print("   1. IPTV ilovasini oching")
        print("   2. 'Playlist qo'shish' yoki 'Import' tanglang")
        print("   3. Fayl manzilini kiriting")
        print(f"\n📱 Raw URL: https://raw.githubusercontent.com/uuu916501-star/VodiySadosi/main/{PLAYLIST_FILE}")
        print(f"\n🔗 GitHub: https://github.com/uuu916501-star/VodiySadosi/blob/main/{PLAYLIST_FILE}")
    else:
        print("\n✗ Hech qanday kanal topilmadi")
        print(f"⚠️  API URL ni tekshiring: {API_URL}")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
