#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AsilTV Playlist Generator — TOKEN bilan ishlaydigan yangilangan versiya
API: https://api.v1.mediabay.tv/v2/channels/thread/339
"""
import requests
import json
import os
import sys
import argparse
from datetime import datetime

API_URL = "https://api.v1.mediabay.tv/v2/channels/thread/339"
DEFAULT_PLAYLIST = "AsilTV.m3u8"


def get_auth_header(token):
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def fetch_api(url, token=None, timeout=15):
    headers = get_auth_header(token)
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 APIga soʻrov yuborilmoqda: {url}")
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        print("✗ Ulanish xatosi: Timeout")
    except requests.exceptions.ConnectionError:
        print("✗ Ulanish xatosi: Tarmoq muammosi")
    except requests.exceptions.HTTPError as e:
        code = getattr(e.response, "status_code", "??")
        print(f"✗ HTTP xatosi: {code} - {e}")
        # Agar server JSON xato bilan qaytarsa uni ko‘rsatish foydali bo‘ladi
        try:
            print("✱ Server javobi:")
            print(e.response.text[:1000])
        except Exception:
            pass
    except json.JSONDecodeError:
        print("✗ JSON tahlil xatosi")
    except Exception as e:
        print(f"✗ Noma'lum xato: {e}")
    return None


def extract_m3u8_urls_from_channel(channel):
    """Kanal obyekti ichidan .m3u8 URL(lar)ni topish uchun moslashuvchan qidiruv."""
    urls = set()

    def check_and_add(val):
        if isinstance(val, str) and ".m3u8" in val:
            urls.add(val)

    if not channel:
        return list(urls)

    # Oddiy maydonlar
    for k in ("threadAddress", "url", "streamUrl", "playUrl"):
        if isinstance(channel, dict) and channel.get(k):
            check_and_add(channel.get(k))

    # stream ichida bo‘lishi mumkin
    stream = None
    if isinstance(channel, dict):
        stream = channel.get("stream") or channel.get("streams")
    if stream:
        # agar stream dict bo‘lsa
        if isinstance(stream, dict):
            # mumkin bo‘lgan maydonlar
            for v in stream.values():
                if isinstance(v, str):
                    check_and_add(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            check_and_add(item)
                        elif isinstance(item, dict):
                            for vv in item.values():
                                if isinstance(vv, str):
                                    check_and_add(vv)
        elif isinstance(stream, list):
            for item in stream:
                if isinstance(item, str):
                    check_and_add(item)
                elif isinstance(item, dict):
                    for vv in item.values():
                        if isinstance(vv, str):
                            check_and_add(vv)

    # playlists ko'rinishi
    playlists = None
    if isinstance(channel, dict):
        playlists = channel.get("playlists") or channel.get("variants")
    if isinstance(playlists, list):
        for p in playlists:
            if isinstance(p, str):
                check_and_add(p)
            elif isinstance(p, dict):
                for v in p.values():
                    if isinstance(v, str):
                        check_and_add(v)

    # fallback: rekursiv izlash kanal obyekti bo‘ylab
    def recurse(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                recurse(v)
        elif isinstance(obj, list):
            for i in obj:
                recurse(i)
        elif isinstance(obj, str):
            check_and_add(obj)
    recurse(channel)

    return list(urls)


def build_playlist(channels, out_file, api_url):
    if not channels:
        print("⚠ Hech qanday kanal yo'q, playlist yaratilmaydi.")
        return False
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U url-tvg=\"\" tvg-shift=0\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Source API: {api_url}\n")
            f.write(f"# Total channels: {len(channels)}\n\n")
            added = 0
            for idx, ch in enumerate(channels, start=1):
                name = ch.get("name") or ch.get("title") or f"Kanal {idx}"
                duration = ch.get("duration", "-1")
                logo = ch.get("logo", "")
                group = ch.get("group") or ch.get("category") or "AsilTV"
                tvg_id = ch.get("tvg_id") or ch.get("id") or idx

                urls = extract_m3u8_urls_from_channel(ch)
                if not urls:
                    # agar channel o'zi string bo'lsa
                    if isinstance(ch, str) and ".m3u8" in ch:
                        urls = [ch]

                if not urls:
                    print(f"⚠ [{idx}] {name}: .m3u8 topilmadi, o'tkazildi.")
                    continue

                # Bir yoki bir nechta URL bo'lishi mumkin — birinchisini yozamiz
                for url in urls:
                    extinf = f"#EXTINF:{duration} tvg-id=\"{tvg_id}\""
                    if logo:
                        extinf += f' tvg-logo="{logo}"'
                    extinf += f' group-title="{group}", {name}\n'
                    f.write(extinf)
                    f.write(f"{url}\n")
                    added += 1
                    # agar faqat bir URL yozmoqchi bo'lsangiz, break qiling
                    break

            print(f"✓ Playlist yozildi: {out_file} ({added} item)")
        return True
    except IOError as e:
        print(f"✗ Fayl yozishda xato: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="AsilTV playlist generator (Mediabay API)")
    parser.add_argument("--token", "-t", help="API Bearer token (agar muhitda yo'q bo'lsa)")
    parser.add_argument("--output", "-o", default=DEFAULT_PLAYLIST, help="Chiqish playlist nomi (default: AsilTV.m3u8)")
    parser.add_argument("--save-json", action="store_true", help="API javobini JSON faylga saqlash")
    parser.add_argument("--api-url", default=API_URL, help="API URL (default mediabay thread/339)")
    args = parser.parse_args()

    token = args.token or os.getenv("TOKEN")
    data = fetch_api(args.api_url, token=token)
    if data is None:
        print("✗ APIdan ma'lumot olinmadi.")
        sys.exit(1)

    # Agar javob strukturasi {'status':'ok','data':[...]} 
    channels = []
    if isinstance(data, dict):
        if data.get("status") and data.get("data") is not None:
            channels = data.get("data", [])
        else:
            # Ba'zan API to'g'ridan-to'g'ri list qaytaradi ichida kanal obyektlari bo'ladi
            # yoki boshqa nom bilan o'rnatilgan bo'lishi mumkin
            # Shu sababli tarkibdan mos obyektlarni topamiz:
            if "data" in data and isinstance(data["data"], list):
                channels = data["data"]
            else:
                # imkon qadar topish: agar dict ichida obyektlar ro'yxati bo'lsa
                # masalan: {"channels":[...]} 
                for k in ("channels", "items", "results"):
                    if k in data and isinstance(data[k], list):
                        channels = data[k]
                        break
                # agar hali bo'sh bo'lsa va dict ichida to'g'ri obyektlar ko'rinsa, sinov uchun uni listga qo'shamiz
                if not channels:
                    # ba'zan API bitta obyekti qaytaradi
                    if any(isinstance(v, (dict, list)) for v in data.values()):
                        channels = [data]
    elif isinstance(data, list):
        channels = data
    else:
        print("⚠ API javobi kutilmagan formatda.")
        sys.exit(1)

    # ixtiyoriy: API JSONni saqlash
    if args.save_json:
        fn = f"channel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(fn, "w", encoding="utf-8") as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)
            print(f"✓ API javobi saqlandi: {fn}")
        except Exception as e:
            print(f"✗ JSON yozishda xato: {e}")

    # Endi playlist yaratamiz
    success = build_playlist(channels, args.output, args.api_url)
    if not success:
        sys.exit(2)

if __name__ == "__main__":
    main()
