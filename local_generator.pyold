# -*- coding: utf-8 -*-
import os
import subprocess

# Guncel ve dogrulanmis YouTube IPTV kanal listesi
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

# Cikti klasorunu ayarla
streams_dir = "streams"
os.makedirs(streams_dir, exist_ok=True)

ana_m3u = "#EXTM3U\n"
print("Kanal linkleri toplaniyor...\n")

for slug, isim, url in kanallar:
    try:
        # Full path kullaniyoruz
        result = subprocess.run(
            ["/usr/local/bin/yt-dlp", "-f", "best", "-g", url],
            capture_output=True, text=True, timeout=20
        )
        link = result.stdout.strip()
        
        if link and link.startswith("http"):
            # TiviMate ve VLC icin User-Agent parametreleri
            tivimate_params = '#EXTVLCOPT:http-user-agent=VLC\n#EXTATTRIBUTES:User-Agent=VLC'
            
            # 1. Tekil m3u8 dosyasi uretimi
            kanal_m3u_icerik = f"#EXTM3U\n{tivimate_params}\n#EXTINF:-1,{isim}\n{link}\n"
            with open(f"{streams_dir}/{slug}.m3u8", "w", encoding="utf-8") as f:
                f.write(kanal_m3u_icerik)
                
            # 2. Ana playlist.m3u dosyasina ekleme
            ana_m3u += f'#EXTINF:-1 tvg-name="{isim}" group-title="Canli" http-user-agent="VLC",{isim}\n{link}\n'
            print(f"OK: {isim} linki alindi.")
        else:
            print(f"HATA: {isim} - Yayin linki cozulemedi.")
    except Exception as e:
        print(f"HATA: {isim} - Sorun olustu: {e}")

# Toplu m3u listesini kaydet
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(ana_m3u)

print("\nDosyalar hazirlandi. GitHub'a pushlaniyor...")

# Git Otomasyonu
try:
    subprocess.run(["git", "config", "user.name", "Lokal Sunucu Proxy"], check=True)
    subprocess.run(["git", "config", "user.email", "sunucu@proxy.local"], check=True)
    
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run("git diff-index --quiet HEAD || git commit -m 'Lokal Otomatik Guncelleme'", shell=True, check=True)
    
    branch_check = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    aktif_dal = branch_check.stdout.strip() or "main"
    
    subprocess.run(["git", "push", "origin", aktif_dal], check=True)
    print(f"\n🚀 GitHub yuklemesi '{aktif_dal}' dalina basariyla tamamlandi!")
except Exception as e:
    print(f"\n❌ GitHub'a yuklenirken sorun cikti: {e}")
