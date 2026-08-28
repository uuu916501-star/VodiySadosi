# VodiySadosi - Mediabay Playlist Generator

Mediabay API dan `.m3u8` playlist fayl generatsiya qilish uchun Python skripti.

## Tavsif

Bu skript:
- Mediabay API dan kanallarni oladi
- Har safar yangi kanallarni `playlist.m3u8` ga qo'shadi (append mode)
- Extended M3U format-da faylni yaratadi

## O'rnatish

```bash
# Repository klonlash
git clone https://github.com/uuu916501-star/VodiySadosi.git
cd VodiySadosi

# Requirements o'rnatish
pip install -r requirements.txt
```

## Foydalanish

```bash
# Skriptni ishga tushirish
python generate_playlist.py
```

## API Endpoint

- **URL**: `https://api.v1.mediabay.tv/v2/channels/thread/339`
- **Javob**: JSON format-da kanallar ro'yxati

## Output

`playlist.m3u8` fayli quyidagi formatda yaratiladi:

```m3u8
#EXTM3U
#EXTINF:-1, Kanal 969
https://st2.mediabay.tv/Radio_Echo/playlist.m3u8?token=...
```

## Avtomatsiyalash (Cron)

Har soat ishga tushirish uchun:

```bash
0 * * * * cd /path/to/VodiySadosi && python generate_playlist.py
```

## Muallif

**Vodiy_Sadosi**

## Litsenziya

MIT License
