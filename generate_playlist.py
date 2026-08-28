#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediabay API dan barcha kanal ID-larini olish va ularning playlist-larini qo'shish
Har soatda yangi playlist-lar olinadi
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
    Mediabay API dan barcha kanallarni olish
    """
    try:
        print(f"[{datetime.now()}] API dan ma'lumot olinmoqda...")
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

def get_channel_playlist(channel_id):
    """
    Har bir kanal ID uchun playlist URL-ni olish
    """
    try:
        # Kanal ID-dan playlist URL yaratish
        playlist_url = f"https://api.v1.mediabay.tv/v2/channel/{channel_id}/playlist.m3u8"
        
        # Yoki API-dan bevosita olish
        channel_url = f"https://api.v1.mediabay.tv/v2/channels/{channel_id}"
        
        response = requests.get(channel_url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data.get('status') == 'ok':
            channel_data = data.get('data', {})
            playlist = channel_data.get('threadAddress') or playlist_url
            return playlist
        else:
            return playlist_url
    except Exception as e:
        # Agar xato bo'lsa, default URL qaytarish
        return f"https://api.v1.mediabay.tv/v2/channel/{channel_id}/playlist.m3u8"

def initialize_playlist():
    """
    Playlist fayli bormi, yo'q qilsa yaratish
    """
    try:
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, 'r') as f:
                content = f.read()
                if '#EXTM3U' not in content:
                    print(f"⚠ {PLAYLIST_FILE} qayta yaratilmoqda...")
                    with open(PLAYLIST_FILE, 'w') as fw:
                        fw.write("#EXTM3U\n")
        else:
            print(f"📝 {PLAYLIST_FILE} fayli yaratilmoqda...")
            with open(PLAYLIST_FILE, 'w') as f:
                f.write("#EXTM3U\n")
    except IOError as e:
        print(f"✗ Fayl xatosi: {e}")

def add_to_playlist(channels):
    """
    Barcha kanallarni playlist-ga qo'shish (append mode)
    Har kanal uchun uning o'z playlist URL-ni qo'shish
    """
    if not channels:
        print("⚠ Qo'shish uchun kanal yo'q")
        return

    try:
        with open(PLAYLIST_FILE, 'a') as f:
            # Vaqt bilan separator qo'shish
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n# Yangilash: {current_time}\n")
            
            for idx, channel in enumerate(channels, 1):
                channel_id = channel.get('id', 'Unknown')
                channel_name = channel.get('name', f'Kanal {channel_id}')
                url = channel.get('threadAddress', '')

                if url:
                    # Extended M3U format
                    f.write(f"#EXTINF:-1, {channel_name} (ID: {channel_id})\n")
                    f.write(f"{url}\n")
                    print(f"✓ [{idx}] Kanal {channel_id}: {channel_name}")
                else:
                    print(f"⚠ [{idx}] Kanal {channel_id}: URL topilmadi")

        print(f"\n✓ {PLAYLIST_FILE} yangilandi ({len(channels)} kanal qo'shildi)")
    except IOError as e:
        print(f"✗ Fayl yozish xatosi: {e}")

def main():
    """
    Asosiy funksiya
    """
    print("="*60)
    print("Mediabay Playlist Generator (Barcha Kanallar)")
    print(f"Vaqti: {datetime.now()}")
    print(f"API: {API_URL}")
    print("="*60)

    # Playlist-ni tayyorlash
    initialize_playlist()

    # Kanallarni olish
    channels = get_channels()

    # Playlist-ga qo'shish
    if channels:
        add_to_playlist(channels)
        print("\n✓ Bajarildi!")
    else:
        print("\n✗ Hech qanday kanal qo'shilmadi")

    print("="*60)

if __name__ == "__main__":
    main()
