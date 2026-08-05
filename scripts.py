#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
from datetime import datetime

# -------------------- KANAL LİSTESİ --------------------
kanallar = [
    ("trthaber", "TRT Haber", "https://www.youtube.com/@trthaber/live"),
    ("cnnturk", "CNN Turk", "https://www.youtube.com/@cnnturk/live"),
    ("ntv", "NTV", "https://www.youtube.com/@ntv/live"),
    ("ahaber", "A Haber", "https://www.youtube.com/@Ahaber/live"),
    ("haberturk", "Haber Turk", "https://www.youtube.com/@haberturktv/live"),
    ("halktv", "Halk TV", "https://www.youtube.com/@Halktvkanali/live"),
    ("sozcutelevizyonu", "Sozcu TV", "https://www.youtube.com/@sozcutelevizyonu/live"),
    ("tgrthaber", "TGRT Haber", "https://www.youtube.com/@tgrthaber/live"),
    ("flashhaber", "Flash Haber", "https://www.youtube.com/@flashhabertv/live"),
    ("haberglobal", "Haber Global", "https://www.youtube.com/@haberglobal/live"),
    ("tv100", "TV 100", "https://www.youtube.com/@tv100/live"),
    ("bloomberght", "Bloomberg HT", "https://www.youtube.com/@bloomberght/live"),
    ("benguturk", "Bengu Turk", "https://www.youtube.com/@tvbenguturk/live"),
    ("krttv", "KRT TV", "https://www.youtube.com/@krtcanli/live"),
    ("ulusalkanal", "Ulusal Kanal", "https://www.youtube.com/@ulusalkanaltv/live"),
    ("ulketv", "Ulke TV", "https://www.youtube.com/@ulketv/live"),
    ("ekoturk", "Eko Turk", "https://www.youtube.com/@ekoturktv/live"),
    ("tv24", "24 TV", "https://www.youtube.com/@YirmidortTV/live"),
    ("aspor", "A Spor", "https://www.youtube.com/@aspor/live"),
    ("htspor", "HT Spor", "https://www.youtube.com/@htspor/live"),
    ("tvnet", "TV Net", "https://www.youtube.com/@tvnet/live"),
    ("beinsportshaber", "Bein Spor Haber", "https://www.youtube.com/@beINSPORTSTurkiye/live"),
    ("cnbce", "CNBC-e", "https://www.youtube.com/@cnbce/live")
]

# -------------------- AYARLAR --------------------
CHANNELS_DIR = "channels"            # PHP dosyalarının bulunduğu klasör
PLAYLIST_FILE = "playlist.m3u"
USER_AGENT = "VLC/3.0.20"
YT_DLP_TIMEOUT = 60
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/tecotv2025/youtube-canli/main"  # Repo adresiniz

# yt-dlp yolunu bul
YT_DLP = shutil.which("yt-dlp")
if not YT_DLP:
    print("❌ yt-dlp bulunamadı! Lütfen yt-dlp'yi kurun: pip install yt-dlp")
    sys.exit(1)

# -------------------- FONKSİYONLAR --------------------
def get_live_url(youtube_url):
    """YouTube canlı yayın URL'sini alır."""
    try:
        result = subprocess.run(
            [YT_DLP, "--geo-bypass", "-f", "best", "-g", youtube_url],
            capture_output=True,
            text=True,
            timeout=YT_DLP_TIMEOUT
        )
        if result.returncode != 0:
            return None, f"yt-dlp çıkış kodu {result.returncode}: {result.stderr.strip()}"
        link = result.stdout.strip()
        if not link or not link.startswith("http"):
            return None, f"Geçersiz link: {link}"
        return link, None
    except subprocess.TimeoutExpired:
        return None, "Zaman aşımı"
    except Exception as e:
        return None, str(e)

def write_php_file(slug, url):
    """Kanal için PHP yönlendirme dosyası oluşturur/günceller."""
    php_content = f"""<?php
header("Location: {url}");
exit;
?>
"""
    filepath = os.path.join(CHANNELS_DIR, f"{slug}.php")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(php_content)
    return filepath

def git_push():
    """Değişiklikleri commit'leyip push'lar."""
    try:
        subprocess.run(["git", "config", "user.name", "Lokal Sunucu Proxy"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "sunucu@proxy.local"], check=True, capture_output=True)

        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("📭 Hiç değişiklik yok, commit atlanıyor.")
            return

        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

        commit_msg = f"Otomatik güncelleme - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        commit = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )
        if commit.returncode != 0:
            if "nothing to commit" in commit.stderr:
                print("📭 Değişiklik yok, commit atlanıyor.")
                return
            else:
                raise subprocess.CalledProcessError(commit.returncode, "git commit", commit.stderr)

        branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        aktif_dal = branch.stdout.strip() or "main"

        subprocess.run(["git", "push", "origin", aktif_dal], check=True, capture_output=True)
        print(f"\n🚀 GitHub yüklemesi '{aktif_dal}' dalına başarıyla tamamlandı!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git işlemi başarısız: {e}")
        if e.stderr:
            print("Hata detayı:", e.stderr)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")

# -------------------- ANA PROGRAM --------------------
def main():
    os.makedirs(CHANNELS_DIR, exist_ok=True)
    print("📡 Kanal linkleri toplanıyor ve PHP dosyaları oluşturuluyor...\n")

    for slug, isim, url in kanallar:
        print(f"➡️  {isim} ... ", end="", flush=True)
        link, hata = get_live_url(url)
        if link is None:
            print(f"❌ {hata}")
            continue

        # PHP dosyasını oluştur/güncelle
        write_php_file(slug, link)
        print("✅ OK")

    # -------- SABİT PLAYLİST OLUŞTUR (SADECE PHP DOSYALARINA İŞARET EDER) --------
    # Bu dosya her seferinde aynı şekilde oluşturulur, değişmez.
    # İçinde kanal adları ve PHP dosyalarının raw URL'leri yer alır.
    ana_m3u = "#EXTM3U\n"
    for slug, isim, _ in kanallar:
        php_url = f"{GITHUB_RAW_BASE}/{CHANNELS_DIR}/{slug}.php"
        ana_m3u += f'#EXTINF:-1 tvg-name="{isim}" group-title="Canlı" http-user-agent="{USER_AGENT}",{isim}\n{php_url}\n'

    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        f.write(ana_m3u)

    print(f"\n📁 PHP dosyaları '{CHANNELS_DIR}/' klasörüne kaydedildi.")
    print(f"📁 Ana playlist '{PLAYLIST_FILE}' dosyasına kaydedildi (sabit içerik).")

    # Git push
    git_push()

if __name__ == "__main__":
    main()
