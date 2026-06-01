import os
import subprocess

# Güncel kanal listesi ve canlı yayın URL'leri
kanallar = [
    ("trthaber", "TRT Haber", "https://www.youtube.com/@trthaber/live"),
    ("cnnturk", "CNN Türk", "https://www.youtube.com/@cnnturk/live"),
    ("ntv", "NTV", "https://www.youtube.com/@ntv/live"),
    ("ahaber", "A Haber", "https://www.youtube.com/@Ahaber/live"),
    ("haberturk", "Haber Türk", "https://www.youtube.com/@haberturktv/live"),
    ("halktv", "Halk TV", "https://www.youtube.com/@halktv/live"),
    ("sozcutelevizyonu", "Sözcü TV", "https://www.youtube.com/@sozcutelevizyonu/live"),
    ("tgrthaber", "TGRT Haber", "https://www.youtube.com/@tgrthaber/live"),
    ("flashhaber", "Flash Haber", "https://www.youtube.com/@flashhabertvcom/live"),
    ("haberglobal", "Haber Global", "https://www.youtube.com/@HaberGlobalTV/live"),
    ("tele1", "Tele 1", "https://www.youtube.com/@tele1tv/live"),
    ("tv100", "TV 100", "https://www.youtube.com/@tv100/live"),
    ("bloomberght", "Bloomberg HT", "https://www.youtube.com/@bloomberght/live"),
    ("benguturk", "Bengü Türk", "https://www.youtube.com/@benguturk/live"),
    ("krttv", "KRT TV", "https://www.youtube.com/@krttv/live"),
    ("ulusalkanal", "Ulusal Kanal", "https://www.youtube.com/@ulusalkanal/live"),
    ("ulketv", "Ülke TV", "https://www.youtube.com/@ulketv/live"),
    ("ekoturk", "Eko Türk", "https://www.youtube.com/@ekoturktv/live"),
    ("ekoltv", "Ekol TV", "https://www.youtube.com/@ekoltv/live"),
    ("tv24", "24 TV", "https://www.youtube.com/@tv24comtr/live"),
    ("aspor", "A Spor", "https://www.youtube.com/@aspor/live"),
    ("htspor", "HT Spor", "https://www.youtube.com/@htspor/live"),
    ("beinsportshaber", "Bein Spor Haber", "https://www.youtube.com/@beinsportshaber/live"),
    ("cnbce", "CNBC-e", "https://www.youtube.com/@cnbce/live")
]

# Ayrı m3u8 dosyalarının toplanacağı klasör
streams_dir = "streams"
os.makedirs(streams_dir, exist_ok=True)

ana_m3u = "#EXTM3U\n"
print("📡 Kanal linkleri yerel temiz IP kullanılarak toplanıyor...\n")

for slug, isim, url in kanallar:
    try:
        # Sunucunun kendi IP'si ile yt-dlp çalışıyor
        result = subprocess.run(
            ["yt-dlp", "-f", "best", "-g", url],
            capture_output=True, text=True, timeout=20
        )
        link = result.stdout.strip()
        
        if link and link.startswith("http"):
            # 1. Her kanal için bağımsız m3u8 dosyası oluşturuyoruz
            kanal_m3u_icerik = f"#EXTM3U\n#EXTINF:-1,{isim}\n{link}\n"
            with open(f"{streams_dir}/{slug}.m3u8", "w", encoding="utf-8") as f:
                f.write(kanal_m3u_icerik)
                
            # 2. Hepsini içeren tek bir ana listeye ekleme yapıyoruz
            ana_m3u += f'#EXTINF:-1,{isim}\n{link}\n'
            print(f"✅ {isim} linki alındı ve dosyası üretildi.")
        else:
            print(f"❌ {isim} - Yayın linki çözülemedi.")
    except Exception as e:
        print(f"❌ {isim} - Hata oluştu: {e}")

# Ana toplu listeyi kaydet
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(ana_m3u)

print("\n💾 Dosyalar yerelde hazırlandı. GitHub'a pushlanıyor...")

# Git otomatik commit ve push adımları
try:
    subprocess.run(["git", "config", "user.name", "Lokal Sunucu Proxy"], check=True)
    subprocess.run(["git", "config", "user.email", "sunucu@proxy.local"], check=True)
    
    # Tüm değişiklikleri (silinen eski dosyaları ve yeni eklenen m3u8'leri) git'e ekle
    subprocess.run(["git", "add", "-A"], check=True)
    
    # Değişiklik varsa commit et, yoksa hata verme
    subprocess.run("git diff-index --quiet HEAD || git commit -m 'Lokal Otomatik Güncelleme'", shell=True, check=True)
    
    # GitHub'a gönder (Eski reponun ana dalı 'master' ise aşağıyı 'master' yapabilirsin, genelde 'main'dir)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("\n🚀 Muazzam! GitHub yüklemesi başarıyla tamamlandı!")
except Exception as e:
    print(f"\n❌ GitHub'a yüklenirken bir sorun çıktı: {e}")
