#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediabay API dan IPTV va Televizo ilovasiga mos playlist generatsiya qilish
Thread 339 dan kanallarni oladi va extended M3U8 format ishlatadi
"""

import requests
import json
from datetime import datetime
import os

# Konfiguratsiya
API_URL = "https://api.v1.mediabay.tv/v2/channels/thread/339"
PLAYLIST_FILE = "playlist.m3u8"

def get_channels():
    """
    Mediabay API dan kanallarni olish
    """
    try:
        print(f"[{datetime.now()}] API dan ma'lumot olinmoqda...")
        print(f"URL: {API_URL}")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('status') == 'ok':
            channels = data.get('data', [])
            print(f"✓ {len(channels)} kanal topildi")
            return channels
        else:
            print(f"✗ API xatosi: {data.get('message')}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"✗ Ulanish xatosi: {e}")
        return []
    except json.JSONDecodeError:
        print(f"✗ JSON tahlil xatosi")
        return []

def create_iptv_playlist(channels):
    """
    IPTV va Televizo ilovasiga mos Extended M3U8 playlist yaratish
    """
    if not channels:
        print("⚠ Qo'shish uchun kanal yo'q")
        return False

    try:
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            # Extended M3U8 header
            f.write("#EXTM3U url-tvg=\"\" tvg-shift=0\n")
            
            for idx, channel in enumerate(channels, 1):
                channel_id = channel.get('id', 'Unknown')
                channel_name = channel.get('name', f'Kanal {channel_id}')
                url = channel.get('threadAddress', '')
                
                # Ixtiyoriy maydonlar
                logo = channel.get('logo', '')
                group = channel.get('group', 'Boshqa')

                if url:
                    # EXTINF line IPTV/Televizo ilovasiga mos
                    extinf = f"#EXTINF:-1"
                    
                    # TVG ID qo'shish
                    if channel_id:
                        extinf += f' tvg-id="{channel_id}"'
                    
                    # Logo qo'shish
                    if logo:
                        extinf += f' tvg-logo="{logo}"'
                    else:
                        extinf += f' tvg-logo=""'
                    
                    # Guruh qo'shish
                    if group:
                        extinf += f' group-title="{group}"'
                    
                    # Kanal nomi
                    extinf += f', {channel_name}\n'
                    
                    f.write(extinf)
                    f.write(f"{url}\n")
                    print(f"✓ [{idx}] {channel_name} qo'shildi")

        print(f"\n✓ {PLAYLIST_FILE} yaratildi ({len(channels)} kanal)")
        print(f"📱 IPTV ilovasiga (Televizo, IPTV Extreme, GSE IPTV va h.k.) import qiling")
        return True
    except IOError as e:
        print(f"✗ Fayl yozish xatosi: {e}")
        return False

def main():
    """
    Asosiy funksiya
    """
    print("="*60)
    print("IPTV/Televizo Playlist Generator")
    print(f"Vaqti: {datetime.now()}")
    print("="*60)

    # Kanallarni olish
    channels = get_channels()

    # IPTV playlist yaratish
    if channels:
        create_iptv_playlist(channels)
        print("\n✅ Bajarildi! Playlist ishga tayyoroti")
        print(f"\n📋 Playlist manzili: {os.path.abspath(PLAYLIST_FILE)}")
        print("💡 Maslahat: Playlist-ni IPTV ilovasiga qo'shish uchun:")
        print("   1. IPTV ilovasini oching")
        print("   2. 'Playlist qo'shish' yoki 'Import' tanglang")
        print("   3. Fayl manzilini kiriting yoki fayl tanlang")
    else:
        print("\n✗ Hech qanday kanal topilmadi")

    print("="*60)

if __name__ == "__main__":
    main()
