#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediabay API dan playlist.m3u8 generatsiya qilish
Thread 339 dan kanallarni oladi
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

def create_playlist(channels):
    """
    Playlist fayli yaratish
    """
    if not channels:
        print("⚠ Qo'shish uchun kanal yo'q")
        return False

    try:
        with open(PLAYLIST_FILE, 'w') as f:
            f.write("#EXTM3U\n")
            
            for channel in channels:
                channel_id = channel.get('id', 'Unknown')
                url = channel.get('threadAddress', '')

                if url:
                    f.write(f"#EXTINF:-1, Kanal {channel_id}\n")
                    f.write(f"{url}\n")
                    print(f"✓ Kanal {channel_id} qo'shildi")

        print(f"\n✓ {PLAYLIST_FILE} yaratildi ({len(channels)} kanal)")
        return True
    except IOError as e:
        print(f"✗ Fayl yozish xatosi: {e}")
        return False

def main():
    """
    Asosiy funksiya
    """
    print("="*50)
    print("Mediabay Playlist Generator")
    print(f"Vaqti: {datetime.now()}")
    print("="*50)

    # Kanallarni olish
    channels = get_channels()

    # Playlist yaratish
    if channels:
        create_playlist(channels)
        print("\n✓ Bajarildi!")
    else:
        print("\n✗ Hech qanday kanal topilmadi")

    print("="*50)

if __name__ == "__main__":
    main()
