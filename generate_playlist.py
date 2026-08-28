#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediabay API dan playlist.m3u8 generatsiya qilish
Har safar farqli thread ID dan kanallar qo'shiladi
"""

import requests
import json
from datetime import datetime
import os

# Konfiguratsiya
API_BASE_URL = "https://api.v1.mediabay.tv/v2/channels/thread"
PLAYLIST_FILE = "playlist.m3u8"
STATE_FILE = ".thread_state"

# Thread ID ro'yxati (alternativ qilish uchun)
THREAD_IDS = [339, 340, 341, 342, 343]

def get_current_thread_id():
    """
    Joriy thread ID ni olish va keyingi thread-ga o'tkazish
    """
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                current_index = int(f.read().strip())
        else:
            current_index = 0
        
        # Keyingi index-ga o'tkazish
        next_index = (current_index + 1) % len(THREAD_IDS)
        
        # State fayl-ni yangilash
        with open(STATE_FILE, 'w') as f:
            f.write(str(next_index))
        
        return THREAD_IDS[current_index]
    except Exception as e:
        print(f"⚠ State xatosi: {e}, default 339 ishlatilmoqda")
        return THREAD_IDS[0]

def get_channels(thread_id):
    """
    Mediabay API dan kanallarni olish
    """
    api_url = f"{API_BASE_URL}/{thread_id}"
    
    try:
        print(f"[{datetime.now()}] API dan ma'lumot olinmoqda (Thread {thread_id})...")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('status') == 'ok':
            channels = data.get('data', [])
            print(f"✓ {len(channels)} kanal topildi (Thread {thread_id})")
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

def add_to_playlist(channels, thread_id):
    """
    Kanallarni playlist-ga qo'shish (append mode)
    """
    if not channels:
        print("⚠ Qo'shish uchun kanal yo'q")
        return

    try:
        with open(PLAYLIST_FILE, 'a') as f:
            # Thread ID uchun separator qo'shish
            f.write(f"\n# Thread {thread_id} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            
            for channel in channels:
                channel_id = channel.get('id', 'Unknown')
                url = channel.get('threadAddress', '')

                if url:
                    # Extended M3U format
                    f.write(f"#EXTINF:-1, [Thread {thread_id}] Kanal {channel_id}\n")
                    f.write(f"{url}\n")
                    print(f"✓ Kanal {channel_id} qo'shildi")

        print(f"✓ {PLAYLIST_FILE} yangilandi ({len(channels)} kanal qo'shildi)")
    except IOError as e:
        print(f"✗ Fayl yozish xatosi: {e}")

def main():
    """
    Asosiy funksiya
    """
    print("="*50)
    print("Mediabay Playlist Generator (Alternativ Mode)")
    print(f"Vaqti: {datetime.now()}")
    print(f"Thread ID ro'yxati: {THREAD_IDS}")
    print("="*50)

    # Playlist-ni tayyorlash
    initialize_playlist()

    # Joriy thread ID olish
    current_thread = get_current_thread_id()
    print(f"📌 Joriy Thread: {current_thread}\n")

    # Kanallarni olish
    channels = get_channels(current_thread)

    # Playlist-ga qo'shish
    if channels:
        add_to_playlist(channels, current_thread)
        print("\n✓ Bajarildi!")
    else:
        print("\n✗ Hech qanday kanal qo'shilmadi")

    print("="*50)

if __name__ == "__main__":
    main()
