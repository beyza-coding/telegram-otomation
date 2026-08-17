#!/usr/bin/env python3
"""
BayMavi Telegram Otomatik Gönderici
------------------------------------
Kendi bilgisayarında çalışır. schedule.json'daki postları,
vakti geldikçe Telegram Bot API üzerinden kanala otomatik gönderir.

Token bu dosyada DEĞİL — .env dosyasından okunur (sen doldurursun).

Kullanım:
  python telegram_poster.py            # Vakti gelen postları bir kez gönderir (Task Scheduler için)
  python telegram_poster.py --daemon   # Sürekli çalışır, her 60 sn'de kontrol eder

Gereksinim:
  pip install requests
"""

import os
import sys
import json
import time
import mimetypes
from datetime import datetime
from pathlib import Path

import requests

# --- Yollar -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CONTENT_ROOT = BASE_DIR          # Telegram-Otomasyon klasoru (gorseller burada)
ENV_FILE = BASE_DIR / ".env"
SCHEDULE_FILE = BASE_DIR / "schedule.json"
SENT_LOG = BASE_DIR / "sent.log"
RUN_LOG = BASE_DIR / "poster.log"

# Bu kadar dakikadan fazla gecikmiş postu GÖNDERME (backlog'un topluca dökülmesini önler).
# Örn. bilgisayar kapalı kaldıysa, açılınca eski postlar atlanır; sadece güncel olanlar gider.
MAX_OVERDUE_MIN = 120

# İki gönderim arası EN AZ bu kadar dakika olsun (arka arkaya dökülmesin).
MIN_GAP_MIN = 170
LAST_SEND = BASE_DIR / "last_send.txt"


def load_last_send():
    if LAST_SEND.exists():
        try:
            return datetime.fromisoformat(LAST_SEND.read_text(encoding="utf-8").strip())
        except Exception:
            return None
    return None


def save_last_send(dt):
    try:
        LAST_SEND.write_text(dt.isoformat(), encoding="utf-8")
    except Exception:
        pass


# --- Basit .env okuyucu (python-dotenv gerekmez) ----------------------------
def load_env():
    # .env yoksa sorun değil: bulutta (GitHub Actions) token ortam değişkeninden gelir.
    if not ENV_FILE.exists():
        return {}
    env = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def log(msg):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line)
    try:
        with open(RUN_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# --- Gönderilmiş kaydı -------------------------------------------------------
def load_sent():
    if SENT_LOG.exists():
        return set(SENT_LOG.read_text(encoding="utf-8").split())
    return set()


def mark_sent(post_id):
    with open(SENT_LOG, "a", encoding="utf-8") as f:
        f.write(post_id + "\n")


# --- Medya tipi --------------------------------------------------------------
def detect_media_type(path):
    ext = Path(path).suffix.lower()
    if ext in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
        return "video"
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        return "photo"
    return "document"


def resolve_media_path(rel_path):
    p = Path(rel_path)
    if p.is_absolute() and p.exists():
        return p
    candidate = (CONTENT_ROOT / rel_path)
    if candidate.exists():
        return candidate
    candidate2 = (BASE_DIR / rel_path)
    if candidate2.exists():
        return candidate2
    return None


# --- Telegram gönderimi ------------------------------------------------------
def _build_extras(post, entities_field):
    """Inline link butonları ve custom/animated emoji entity'lerini API verisine ekler."""
    extras = {}
    buttons = post.get("buttons")
    if not buttons and post.get("button"):
        buttons = [post["button"]]
    if buttons:
        # Her satır bir liste: [{"text": "...", "url": "..."}]. Tek buton = tek satır.
        keyboard = [[{"text": b["text"], "url": b["url"]}] for b in buttons]
        extras["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    if post.get("entities"):
        # Telegram custom (animated) emoji vb. için MessageEntity listesi
        # Örn: [{"type":"custom_emoji","offset":0,"length":2,"custom_emoji_id":"5368324170671202286"}]
        extras[entities_field] = json.dumps(post["entities"])
    return extras


def send_post(token, chat_id, post):
    media_rel = post.get("media_path")
    caption = post.get("caption", "")
    media_type = post.get("media_type") or (detect_media_type(media_rel) if media_rel else "text")

    api = f"https://api.telegram.org/bot{token}"

    # Medyasız (düz metin) post
    if not media_rel:
        data = {"chat_id": chat_id, "text": caption}
        data.update(_build_extras(post, "entities"))
        return requests.post(f"{api}/sendMessage", data=data, timeout=60)

    media_path = resolve_media_path(media_rel)
    if not media_path:
        log(f"  ! Medya bulunamadı: {media_rel} — atlanıyor")
        return None

    method = {"video": "sendVideo", "photo": "sendPhoto", "document": "sendDocument"}[media_type]
    field = {"video": "video", "photo": "photo", "document": "document"}[media_type]

    with open(media_path, "rb") as fh:
        files = {field: (media_path.name, fh, mimetypes.guess_type(str(media_path))[0])}
        data = {"chat_id": chat_id, "caption": caption}
        data.update(_build_extras(post, "caption_entities"))
        r = requests.post(f"{api}/{method}", data=data, files=files, timeout=180)
    return r


# --- Ana döngü ---------------------------------------------------------------
def run_once(token, chat_id):
    if not SCHEDULE_FILE.exists():
        log(f"schedule.json yok ({SCHEDULE_FILE}) — gönderilecek post yok.")
        return
    posts = json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
    sent = load_sent()
    now = datetime.now()
    due = []
    for p in posts:
        pid = str(p.get("id"))
        if pid in sent:
            continue
        try:
            when = datetime.fromisoformat(p["datetime"])
        except Exception:
            log(f"  ! Geçersiz tarih ({p.get('id')}): {p.get('datetime')} — atlanıyor")
            continue
        if when <= now:
            overdue_min = (now - when).total_seconds() / 60
            if overdue_min > MAX_OVERDUE_MIN:
                log(f"  ⏭ Atlandı (çok geç: {int(overdue_min)} dk gecikmiş): {pid}")
                mark_sent(pid)  # bir daha denenmesin
                continue
            due.append(p)

    if not due:
        return
    due.sort(key=lambda x: x["datetime"])

    # Postlar arası minimum boşluk: arka arkaya (3 dk gibi) gönderme.
    last = load_last_send()
    if last is not None and (now - last).total_seconds() < MIN_GAP_MIN * 60:
        return  # henüz gönderim zamanı değil, bir sonraki döngüde tekrar bak

    p = due[0]  # her çalıştırmada YALNIZCA 1 post → doğal aralık sağlanır
    pid = str(p.get("id"))
    log(f"Gönderiliyor: {pid} — {p.get('datetime')} — {p.get('media_path','(metin)')}")
    try:
        r = send_post(token, chat_id, p)
        if r is None:
            return
        ok = r.json().get("ok", False)
        if ok:
            mark_sent(pid)
            save_last_send(now)
            log(f"  ✓ Gönderildi: {pid}")
        else:
            log(f"  ✗ Telegram hatası ({pid}): {r.text[:300]}")
    except Exception as e:
        log(f"  ✗ İstisna ({pid}): {e}")


def main():
    env = load_env()
    token = env.get("BOT_TOKEN") or os.environ.get("BOT_TOKEN")
    chat_id = env.get("CHANNEL_ID") or os.environ.get("CHANNEL_ID")
    if not token or not chat_id:
        log("HATA: .env içinde BOT_TOKEN ve CHANNEL_ID tanımlı olmalı.")
        sys.exit(1)

    if "--test" in sys.argv:
        log("Bağlantı testi...")
        try:
            me = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=30).json()
            if not me.get("ok"):
                log(f"  ✗ Token geçersiz: {me}")
                sys.exit(1)
            log(f"  ✓ Bot bağlı: @{me['result'].get('username')} ({me['result'].get('first_name')})")
            r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                              data={"chat_id": chat_id,
                                    "text": "✅ BayMavi otomasyon testi — bağlantı çalışıyor."},
                              timeout=30).json()
            if r.get("ok"):
                log(f"  ✓ Kanala test mesajı gönderildi ({chat_id}). Kurulum tamam!")
            else:
                log(f"  ✗ Kanala gönderilemedi: {r}")
                log("    → Bot kanalda admin mi ve 'mesaj gönderme' yetkisi var mı? CHANNEL_ID doğru mu?")
        except Exception as e:
            log(f"  ✗ Test hatası: {e}")
        return

    daemon = "--daemon" in sys.argv
    if daemon:
        log("Daemon modu başladı — her 60 sn'de kontrol edilecek. (Durdurmak için Ctrl+C)")
        while True:
            try:
                run_once(token, chat_id)
            except Exception as e:
                log(f"Döngü hatası: {e}")
            time.sleep(60)
    else:
        run_once(token, chat_id)


if __name__ == "__main__":
    main()
