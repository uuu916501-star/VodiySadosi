#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediabay API dan IPTV va Televizo ilovasiga mos playlist generatsiya qilish
Har safar farqli thread ID dan kanallar qo'shiladi (avtomatik almashuv)
API BASE URL: https://api.v1.mediabay.tv/v2/channels/thread/339
"""

import requests
import json
from datetime import datetime
import os

# Konfiguratsiya
API_URL = "https://api.v1.mediabay.tv/v2/channels/thread/339"
PLAYLIST_FILE = "playlist.m3u8"
STATE_FILE = ".thread_state"

# Thread ID ro'yxati (avtomatik almashuv uchun)
THREAD_IDS = [339, 340, 341, 342, 343]

def get_current_thread_id():
    """
    Joriy thread ID ni olish va keyingi thread-ga o'tkazish (avtomatik almashuv)
    Har safar ichi avtomatik ravishda keyingi thread ID ga o'tadi
    """
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                current_index = int(f.read().strip())
        else:
            current_index = 0
        
        # Keyingi index-ga o'tkazish (siklik)
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
    API URL: https://api.v1.mediabay.tv/v2/channels/thread/{thread_id}
    """
    api_url = f"https://api.v1.mediabay.tv/v2/channels/thread/{thread_id}"
    
    try:
        print(f"[{datetime.now()}] API dan ma'lumot olinmoqda (Thread {thread_id})...")
        print(f"🔗 API URL: {api_url}")
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

def create_iptv_playlist(channels, thread_id):
    """
    IPTV va Televizo ilovasiga mos Extended M3U8 playlist yaratish
    Barcha IPTV ilovasiga (Televizo, IPTV Extreme, GSE IPTV va h.k.) moslanadi
    """
    if not channels:
        print("⚠ Qo'shish uchun kanal yo'q")
        return False

    try:
        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            # Extended M3U8 header
            f.write("#EXTM3U url-tvg=\"\" tvg-shift=0\n")
            
            # Thread ID uchun separator qo'shish
            f.write(f"\n# Thread {thread_id} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write(f"# API: https://api.v1.mediabay.tv/v2/channels/thread/{thread_id}\n\n")
            
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
                    
                    # Kanal nomi (Thread ID bilan)
                    extinf += f', [{thread_id}] {channel_name}\n'
                    
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
    Asosiy funksiya
    Har safar ichi avtomatik ravishda farqli thread ID dan kanallarni oladi
    va playlist yaratadi
    
    Almashuv tartibi:
    1-safari: Thread 339
    2-safari: Thread 340
    3-safari: Thread 341
    4-safari: Thread 342
    5-safari: Thread 343
    6-safari: Thread 339 (qayta boshlanadi)
    """
    print("="*70)
    print("🎬 IPTV/Televizo Playlist Generator (Avtomatik Almashuv Rejimida)")
    print(f"⏰ Vaqti: {datetime.now()}")
    print(f"📡 API: https://api.v1.mediabay.tv/v2/channels/thread/")
    print(f"🔄 Thread ID ro'yxati: {THREAD_IDS}")
    print("="*70)

    # Joriy thread ID olish (avtomatik almashuv bilan)
    current_thread = get_current_thread_id()
    print(f"\n📌 Joriy Thread: {current_thread}\n")

    # Kanallarni olish API dan
    channels = get_channels(current_thread)

    # IPTV playlist yaratish
    if channels:
        create_iptv_playlist(channels, current_thread)
        
        next_thread = THREAD_IDS[(THREAD_IDS.index(current_thread) + 1) % len(THREAD_IDS)]
        
        print("\n✅ Bajarildi! Playlist ishga tayyoroti")
        print(f"\n📋 Playlist fayli: {os.path.abspath(PLAYLIST_FILE)}")
        print(f"🔄 Keyingi safari: Thread {next_thread} dan kanallar olinadi")
        print("\n💡 IPTV ilovasiga qo'shish:")
        print("   1. IPTV ilovasini oching (Televizo, IPTV Extreme, GSE IPTV va h.k.)")
        print("   2. 'Playlist qo'shish' yoki 'Import' tanglang")
        print("   3. Fayl manzilini kiriting yoki fayl tanlang")
        print(f"\n📱 Raw URL: https://raw.githubusercontent.com/uuu916501-star/VodiySadosi/main/{PLAYLIST_FILE}")
    else:
        print("\n✗ Hech qanday kanal topilmadi")
        print(f"⚠️  API URL ni tekshiring: https://api.v1.mediabay.tv/v2/channels/thread/{current_thread}")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
