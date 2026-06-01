import subprocess

# YouTube canlı yayın hesap adları ve URL'leri tamamen stabilize edildi
kanallar = [
    ("TRT Haber", "https://www.youtube.com/@trthaber"),
    ("CNN Türk", "https://www.youtube.com/@cnnturk"),
    ("NTV", "https://www.youtube.com/@ntv"),
    ("A Haber", "https://www.youtube.com/@Ahaber"),
    ("Haber Türk", "https://www.youtube.com/@haberturktv"), # @haberturk -> @haberturktv olarak düzeltildi
    ("Halk TV", "https://www.youtube.com/@halktv"),
    ("Sözcü TV", "https://www.youtube.com/@sozcutelevizyonu"), # @sozcu -> @sozcutelevizyonu olarak düzeltildi
    ("TGRT Haber", "https://www.youtube.com/@tgrthaber"),
    ("Flash Haber", "https://www.youtube.com/@flashhabertvcom"),
    ("Haber Global", "https://www.youtube.com/@HaberGlobalTV"),
    ("Tele 1", "https://www.youtube.com/@tele1tv"),
    ("TV 100", "https://www.youtube.com/@tv100"),
    ("Bloomberg HT", "https://www.youtube.com/@bloomberght"),
    ("Bengü Türk", "https://www.youtube.com/@benguturk"),
    ("KRT TV", "https://www.youtube.com/@krttv"),
    ("Ulusal Kanal", "https://www.youtube.com/@ulusalkanal"),
    ("Ülke TV", "https://www.youtube.com/@ulketv"),
    ("Eko Türk", "https://www.youtube.com/@ekoturktv"),
    ("Ekol TV", "https://www.youtube.com/@ekoltv"),
    ("24 TV", "https://www.youtube.com/@tv24comtr"),
    ("A Spor", "https://www.youtube.com/@aspor"),
    ("HT Spor", "https://www.youtube.com/@htspor"),
    ("Bein Spor Haber", "https://www.youtube.com/@beinsportshaber"),
    ("CNBC-e", "https://www.youtube.com/@cnbce")
]

m3u = "#EXTM3U\n"
print(f"📡 {len(kanallar)} kanal için linkler GitHub Actions üzerinde simüle edilerek toplanıyor...\n")

for isim, url in kanallar:
    try:
        # GitHub veri merkezi IP engellerini aşmak için User-Agent ve Referer simülasyonu yapıyoruz
        live_url = f"{url.rstrip('/')}/live"
        
        result = subprocess.run(
            [
                "yt-dlp", 
                "-f", "best", 
                "-g", 
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--referer", "https://www.youtube.com/",
                "--no-warnings",
                live_url
            ],
            capture_output=True, text=True, timeout=30
        )
        
        link = result.stdout.strip()
        
        if link and link.startswith("http"):
            m3u += f'#EXTINF:-1,{isim}\n{link}\n'
            print(f"✅ {isim}")
        else:
            # Fallback: Eğer /live yemezse doğrudan kanal URL'sinden canlı yayını ayıklamayı dene
            fallback_result = subprocess.run(
                [
                    "yt-dlp", "-f", "best", "-g",
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "--playlist-items", "1",
                    "--match-filter", "live_status = live",
                    url
                ],
                capture_output=True, text=True, timeout=20
            )
            fallback_link = fallback_result.stdout.strip()
            
            if fallback_link and fallback_link.startswith("http"):
                m3u += f'#EXTINF:-1,{isim}\n{fallback_link}\n'
                print(f"✅ {isim} (Kanal Doğrulama Yöntemiyle)")
            else:
                print(f"❌ {isim} - Yayın bulunamadı")
                
    except Exception as e:
        print(f"❌ {isim} - Hata: {e}")

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(m3u)
print("\n🚀 playlist.m3u güncellendi!")
