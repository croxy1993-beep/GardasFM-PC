"""
Gardaş FM 8.2 - mp3 gerekmez, şarkılar internetten (YouTube) çalınır; istersen indirip internetsiz dinlersin.

8.2: Yeni arayüz: tam ekran sözler (L), indir / bu listeyi indir / yeni liste / listeye ekle, sade kenar menü (Keşfet katlanır)
8.1: Logo gömüldü, EXE kurulum paketi uyumu (taşınabilir VLC, başlatıcı kısayolu), yeni arayüz simgesi
8.0: Yeni (web tabanlı) arayüz ANA ARAYÜZ oldu: arama, favori, sıra, ana sayfa, sözler; klasik pencere tepsiye küçülür
7.1: Yeni arayüz hata ayıklama (hata yazısı ekranda görünür), söz zamanları düzeltildi, logo yoksa otomatik neon simge (kısayol Python simgesi göstermez)
7.0: Yeni arayüz (beta): gerçek müzik verisiyle çalışan bulanık cam ve akıcı animasyonlu ikinci pencere (F2)
6.2: Discord sunucu rolü kapısı (sunucuda olma + rol kontrolü, kurucular muaf); GUILD_ID boşsa kapalı
6.1: Zorunlu Discord girişi (giriş yapılmadan uygulama açılmaz), kurucu kimliği eklendi
6.0: Profil + Discord ile giriş, kurucu rozeti, dinleme istatistikleri ve aylık özet resmi, liste paylaşma/dışa aktarma,
     tekrarları temizleme, söz kaydırma, şarkı başına ses, Discord "Dinle" butonu
5.5: Radyo modu, şarkılar arası yumuşak geçiş, sürükle-bırak sıralama, son temizlik
5.3: Şarkı bul (sözden / dinleyerek), neon kenarlar kapak renginde, Senin için yeni, F1 kısayol yardımı
5.2: Güncelleme duvarı + otomatik yeniden başlatma, yeni ayarlar ekranı (sekmeli), arama önerileri, yeni kataloglar,
     daralan/gizlenen sol menü, kusursuz köşe ve simetri düzeltmeleri, tüm pencerelerde logo
5.1: Neon cam arayüz (pembeden maviye parlayan kenarlıklı paneller, ikonlu menü, mavi çubuklar, neon kapak ve söz kartı)
5.0: Yeni arayüz (neon cam paneller, yeni temalar), daha fazla animasyon (Tam/Hafif/Kapalı), şarkı değişince bildirim,
     ruh haline göre mix, şarkı etiketleri, güvenli güncelleme (açılmazsa eski sürüme otomatik dönüş)
4.7: Ayarlar'dan masaüstüne kısayol oluşturma (konsol penceresi açmadan, logolu simgeyle)
4.6: Logolu güncelleme kartı (ortada açılır, tek tuşla güncelle + yeniden başlat), pencere simgesi, Discord logosu
4.5: Yedekle/geri yükle, "Neler yeni" penceresi, Discord'da dinlediğin şarkı
4.4: GitHub'dan otomatik güncelleme (favoriler, mixler, listeler, ayarlar korunur)

4.0 yenilikleri:
    - Çevrimdışı: şarkıları indir (sağ tık > İndir), İndirilenler sayfası, klasörden müzik ekleme,
      internet yoksa otomatik olarak indirilenler çalınır, sözler de saklanır
    - Sıradakiler kuyruğu, sağ tık menüsü, birden çok çalma listesi, YouTube playlist içe aktarma
    - Akıllı sürüm seçimi (cover/canlı/remix yerine doğru kaydı bulur), video kimliği önbelleği
    - Tekrar: kapalı / liste / tek şarkı, geri tuşu için şarkı geçmişi, karışık modda da hazırlık
    - Ekolayzır ön ayarları ve çalma hızı, medya tuşları (klavyedeki oynat/duraklat/sonraki), sistem tepsisi
    - Animasyonlar: kapak etrafında dalga, hareketli ses çubukları, kayan menü seçimi, ana sayfa girişi,
      kapaktan renk alma, tam ekran animasyonlu şarkı sözü modu, mini oynatıcı
    - Ana sayfada Bugünün karışığı, kaldığın yerden devam, haftalık özet; 5 renk teması
    - Türkçe harfe duyarlı arama (İ/ı/ş/ğ...), ayarlar çökme durumunda da kaybolmaz, günlük dosyası

Kurulum:   py -m pip install customtkinter python-vlc yt-dlp requests Pillow pystray
           (VLC programı da kurulu olmalı: videolan.org, 64-bit; pystray sadece tepsi için, isteğe bağlı)
Çalıştır:  py gardas_fm.py
"""
# ---- Güvenli güncelleme koruması (5.0): yeni sürüm ilk açılışta çökerse eski sürüme otomatik dönülür ----
import sys as _sys, os as _os, json as _json, re as _re, traceback as _tb, subprocess as _sp
from pathlib import Path as _P

_ME = _P(__file__).resolve()
_MARK = _ME.with_name("guncelleme_durumu.json")      # güncellemeden sonraki ilk açılış bitene kadar durur
_NOTICE = _ME.with_name("geri_alindi.json")          # geri dönüş olduysa açılışta kullanıcıya haber verir


def _boot_rollback(exc_text):
    """Yeni sürüm daha ilk açılışta hata verirse gardas_fm.py.eski'yi geri koyup uygulamayı yeniden başlatır."""
    try:
        info = _json.loads(_MARK.read_text(encoding="utf-8"))
        old = _ME.with_name(_ME.name + ".eski")
        m = _re.search(r'^APP_VERSION\s*=\s*"([0-9.]+)"', _ME.read_text(encoding="utf-8"), _re.M)
        if info.get("tamam") or not old.exists() or not m or m.group(1) != str(info.get("yeni")):
            return False
        _ME.with_name(_ME.name + ".bozuk").write_bytes(_ME.read_bytes())
        _os.replace(old, _ME)
        _NOTICE.write_text(_json.dumps({"bozuk": info.get("yeni"), "hata": exc_text[-400:]}, ensure_ascii=False),
                           encoding="utf-8")
        _MARK.unlink()
        exe, flags = _sys.executable, 0
        if _os.name == "nt":
            pw = _P(exe).with_name("pythonw.exe")
            if pw.exists():
                exe = str(pw)
            flags = 0x00000008 | 0x00000200
        _sp.Popen([exe, str(_ME)], cwd=str(_ME.parent), creationflags=flags, close_fds=True)
        return True
    except Exception:
        return False


def _boot_excepthook(et, ev, tb):
    if _boot_rollback("".join(_tb.format_exception(et, ev, tb))):
        _os._exit(0)
    _sys.__excepthook__(et, ev, tb)


_sys.excepthook = _boot_excepthook

import ast
import base64
import io
import json
import math
import os
import socket
import colorsys
import unicodedata
import webbrowser
from urllib.parse import quote_plus
import random
import time
import re
import shutil
import zipfile
import threading
import queue
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk
import requests
try:
    from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageTk
except Exception:
    raise SystemExit("Pillow bulunamadı. Şunu çalıştır:  py -m pip install Pillow")
# ---- EXE kurulum paketi uyumu: uygulama klasöründe "vlc" klasörü varsa taşınabilir VLC kullanılır ----
_vd = _P(__file__).resolve().parent / "vlc"
if (_vd / "libvlc.dll").exists():
    _os.environ.setdefault("PYTHON_VLC_LIB_PATH", str(_vd / "libvlc.dll"))
    _os.environ.setdefault("PYTHON_VLC_MODULE_PATH", str(_vd / "plugins"))
    try:
        _os.add_dll_directory(str(_vd))
    except Exception:
        pass
try:
    import vlc
except Exception:   # VLC programı kurulu değilse python-vlc anlaşılmaz hata verir
    raise SystemExit("VLC player bulunamadı. https://www.videolan.org adresinden kur "
                     "(Python'la aynı 64-bit sürüm), sonra tekrar çalıştır.")
import yt_dlp

CATALOG = {
    "Türkçe Rap": [
        "Ezhel - Geceler", "Ezhel - Felaket", "Ezhel - Olay", "Ezhel - Müptezel",
        "Ezhel - Şehrimin Tadı", "Ezhel - Aya", "Ezhel - Bulut", "Ezhel - İmkansızım",
        "Uzi - Arasan Da", "Uzi - Papa", "Uzi - Unuttum", "Uzi - Kızılcık Şerbeti",
        "Uzi - Senin Uğruna", "Uzi - Neon",
        "Çakal - İmdat", "Çakal - Lütfen", "Çakal - Mingofresh", "Çakal - Deden",
        "Ceza - Holocaust", "Ceza - Suspus", "Ceza - Neyim Var Ki", "Ceza - Yerli Plaka",
        "Ceza - Fark Var", "Ceza - Rapstar", "Ceza - Med Cezir",
        "Gazapizm - Heyecanı Yok", "Sagopa Kajmer - Bir Pesimistin Gözyaşları",
        "Norm Ender - Mekanın Sahibi", "Mero - Olabilir", "Eypio - Gömün Beni Çukura",
        "Reynmen - Ela", "Reynmen - Derdim Olsun", "Reynmen - Leila", "Reynmen - Renklensin",
        "Reynmen - Cennet",
        "Blok3 - Hovarda", "Blok3 - Sevmeyi Denemedin", "Blok3 - Güzel ve İddialı", "Blok3 - Habibi",
        "Lvbel C5 - Say", "Lvbel C5 - Bi' Tek Ben Anlarım", "Lvbel C5 - Sorun Bende",
        "Lvbel C5 - Sezen Aksu", "Lvbel C5 - Havhavhav", "Lvbel C5 - Doğuştan Beri Haklıyım",
        "Era7capone - Duruldum", "Sefo - Kapalı Kapılar", "Ati242 - Panorama", "Ati242 - Rüya",
    ],
    "Yabancı Rap": [
        "Eminem - Lose Yourself", "Eminem - Mockingbird", "Eminem - Without Me", "Eminem - Stan",
        "Eminem - The Real Slim Shady", "Eminem - Rap God", "Eminem - Love The Way You Lie",
        "Eminem - Not Afraid", "Eminem - Till I Collapse", "Eminem - Sing for the Moment",
        "Kendrick Lamar - HUMBLE.", "Kendrick Lamar - DNA.", "Kendrick Lamar - Alright",
        "Kendrick Lamar - Not Like Us", "Kendrick Lamar - Swimming Pools", "Kendrick Lamar - Money Trees",
        "2Pac - California Love", "2Pac - Changes", "2Pac - Dear Mama", "2Pac - Hit 'Em Up",
        "2Pac - All Eyez on Me", "2Pac - Keep Ya Head Up", "2Pac - Ambitionz Az a Ridah",
        "The Notorious B.I.G. - Juicy", "The Notorious B.I.G. - Hypnotize",
        "The Notorious B.I.G. - Big Poppa", "The Notorious B.I.G. - Mo Money Mo Problems",
        "Jay-Z - 99 Problems", "Jay-Z - Empire State of Mind", "Jay-Z - Dirt Off Your Shoulder",
        "Drake - God's Plan", "Drake - Hotline Bling", "Drake - One Dance", "Drake - In My Feelings",
        "Travis Scott - SICKO MODE", "Travis Scott - goosebumps", "Travis Scott - Highest in the Room",
        "Kanye West - Stronger", "Kanye West - Gold Digger", "Kanye West - All of the Lights",
        "50 Cent - In Da Club", "50 Cent - Candy Shop", "50 Cent - P.I.M.P.",
        "Dr. Dre - Still D.R.E.", "Dr. Dre - The Next Episode", "Dr. Dre - Forgot About Dre",
        "Snoop Dogg - Drop It Like It's Hot", "Snoop Dogg - Gin and Juice",
        "Nas - N.Y. State of Mind", "Nas - If I Ruled the World",
        "Wiz Khalifa - See You Again", "Cardi B - Bodak Yellow", "Lil Nas X - Old Town Road",
        "Lil Wayne - Lollipop", "OutKast - Hey Ya!", "OutKast - Ms. Jackson",
        "Post Malone - Rockstar", "Post Malone - Congratulations", "Juice WRLD - Lucid Dreams",
        "XXXTENTACION - SAD!", "Lil Uzi Vert - XO Tour Llif3", "Future - Mask Off",
        "Migos - Bad and Boujee", "Mac Miller - Self Care", "J. Cole - No Role Modelz",
        "Tyler, The Creator - EARFQUAKE", "Ice Cube - It Was a Good Day", "Coolio - Gangsta's Paradise",
        "Wu-Tang Clan - C.R.E.A.M.", "DMX - X Gon' Give It to Ya", "Pop Smoke - Dior",
        "Cypress Hill - Insane in the Brain", "Missy Elliott - Work It",
    ],
    "Popüler Pop": [
        "The Weeknd - Blinding Lights", "The Weeknd - Save Your Tears", "Dua Lipa - Levitating",
        "Dua Lipa - Don't Start Now", "Ed Sheeran - Shape of You", "Ed Sheeran - Perfect",
        "Billie Eilish - bad guy", "Harry Styles - As It Was", "Harry Styles - Watermelon Sugar",
        "Taylor Swift - Blank Space", "Taylor Swift - Shake It Off", "Adele - Rolling in the Deep",
        "Adele - Someone Like You", "Bruno Mars - Uptown Funk", "Bruno Mars - Locked Out of Heaven",
        "Rihanna - Diamonds", "Rihanna - Umbrella", "Ariana Grande - 7 rings",
        "Ariana Grande - thank u, next", "Olivia Rodrigo - drivers license", "Sia - Chandelier",
        "Lady Gaga - Bad Romance", "Justin Bieber - Peaches", "Camila Cabello - Havana",
        "Shawn Mendes - Stitches", "Charlie Puth - Attention", "Maroon 5 - Sugar",
        "Coldplay - Viva La Vida", "Coldplay - Yellow", "Miley Cyrus - Flowers", "SZA - Kill Bill",
        "Doja Cat - Say So", "Lewis Capaldi - Someone You Loved", "Shakira - Hips Don't Lie",
        "Shakira - Waka Waka", "Luis Fonsi - Despacito", "Pharrell Williams - Happy",
        "Michael Jackson - Billie Jean", "Michael Jackson - Beat It", "Madonna - Like a Prayer",
        "Britney Spears - Toxic", "Katy Perry - Roar", "David Guetta - Titanium", "Avicii - Wake Me Up",
        "Tarkan - Kuzu Kuzu", "Tarkan - Şımarık", "Tarkan - Dudu", "Tarkan - Hepsi Senin mi",
        "Tarkan - Ölürüm Sana", "Sezen Aksu - Hadi Bakalım", "Sezen Aksu - Gülümse Kaderine",
        "Sezen Aksu - Firuze", "Sezen Aksu - Kaybolan Yıllar", "Hadise - Düm Tek Tek",
        "Mustafa Sandal - Araba", "Kenan Doğulu - Yaparım Bilirsin", "Ajda Pekkan - Bambaşka Biri",
        "Murat Boz - Janti", "Gülşen - Be Adam", "Hande Yener - Acele Etme",
        "Simge - Aşkın Olayım", "Aleyna Tilki - Cevapsız Çınlama", "Edis - Martılar",
        "Mabel Matiz - Antidepresan", "Semicenk - Gözlerinden Gözlerine", "Zeynep Bastık - Lan",
    ],
    "Rock Alternatif": [
        "Linkin Park - In the End", "Linkin Park - Numb", "Nirvana - Smells Like Teen Spirit",
        "Nirvana - Come as You Are", "Queen - Bohemian Rhapsody", "Queen - We Will Rock You",
        "Queen - Don't Stop Me Now", "Metallica - Nothing Else Matters", "Metallica - Enter Sandman",
        "Guns N' Roses - Sweet Child O' Mine", "Guns N' Roses - November Rain", "AC/DC - Back In Black",
        "AC/DC - Thunderstruck", "Led Zeppelin - Stairway to Heaven", "Pink Floyd - Wish You Were Here",
        "Pink Floyd - Another Brick in the Wall", "Pink Floyd - Comfortably Numb",
        "Green Day - Boulevard of Broken Dreams", "Green Day - Basket Case",
        "Red Hot Chili Peppers - Californication", "Red Hot Chili Peppers - Under the Bridge",
        "Foo Fighters - Everlong", "Foo Fighters - The Pretender", "System of a Down - Chop Suey!",
        "System of a Down - Toxicity", "Imagine Dragons - Believer", "Imagine Dragons - Radioactive",
        "Arctic Monkeys - Do I Wanna Know?", "Arctic Monkeys - R U Mine?", "Radiohead - Creep",
        "Eagles - Hotel California", "Oasis - Wonderwall", "The Killers - Mr. Brightside",
        "Muse - Uprising", "Muse - Supermassive Black Hole", "Evanescence - Bring Me to Life",
        "Evanescence - My Immortal", "Nickelback - How You Remind Me", "The Cranberries - Zombie",
        "Pearl Jam - Black", "Alice in Chains - Man in the Box", "Rage Against the Machine - Killing in the Name",
        "Slipknot - Duality", "Disturbed - Down with the Sickness", "Deep Purple - Smoke on the Water",
        "Black Sabbath - Paranoid", "Scorpions - Wind of Change", "Bon Jovi - It's My Life",
        "The Rolling Stones - Paint It Black", "The Beatles - Hey Jude", "U2 - With or Without You",
        "Twenty One Pilots - Stressed Out", "Paramore - Misery Business",
        "My Chemical Romance - Welcome to the Black Parade", "Fall Out Boy - Sugar, We're Goin Down",
        "Måneskin - Beggin'", "Kings of Leon - Sex on Fire",
        "Duman - Her Şeyi Yak", "Duman - Köprüaltı", "Duman - Bu Akşam", "Duman - Kendine İyi Bak",
        "Mor ve Ötesi - Bir Derdim Var", "Mor ve Ötesi - Deli", "Mor ve Ötesi - Cambaz",
        "Teoman - Papatya", "Teoman - İstanbul'da Sonbahar", "Teoman - Paramparça",
        "maNga - Fly to Stay Alive", "maNga - Bir Kadın Çizeceksin",
        "Yüksek Sadakat - Belki Üstümüzden Bir Kuş Geçer", "Şebnem Ferah - Sil Baştan",
        "Şebnem Ferah - Çakıl Taşları", "Barış Manço - Gülpembe", "Barış Manço - Dönence",
        "Cem Karaca - Resimdeki Gözyaşları", "Cem Karaca - Tamirci Çırağı",
    ],
    "Arabesk Damar": [
        "Müslüm Gürses - Nilüfer", "Müslüm Gürses - Sevdim Sevilmedim", "Müslüm Gürses - Affet",
        "Müslüm Gürses - Mutlu Ol Yeter", "Müslüm Gürses - Tutsak", "Müslüm Gürses - Olmadı Yar",
        "Müslüm Gürses - Esrarlı Gözler", "Müslüm Gürses - Tanrı İstemezse", "Müslüm Gürses - Seni Yazdım",
        "Ferdi Tayfur - Huzurum Kalmadı", "Ferdi Tayfur - Emmoğlu", "Ferdi Tayfur - Merak Etme Sen",
        "İbrahim Tatlıses - Haydi Söyle", "İbrahim Tatlıses - Mavi Mavi", "İbrahim Tatlıses - Leylim Ley",
        "İbrahim Tatlıses - Acı Gerçekler",
        "Orhan Gencebay - Batsın Bu Dünya", "Orhan Gencebay - Hatasız Kul Olmaz",
        "Orhan Gencebay - Bir Teselli Ver", "Orhan Gencebay - Dilenci",
        "Ahmet Kaya - Acılara Tutunmak", "Ahmet Kaya - Kum Gibi", "Ahmet Kaya - Şafak Türküsü",
        "Ahmet Kaya - Başım Belada",
        "Bergen - Elimde Fotoğrafın", "Adnan Şenses - Neden Saçların Beyazlamış",
        "Esengül - Taht Kurmuşsun Kalbime", "Kibariye - Tanrım", "Ali Tekintüre - İçiyorsam Sebebi Var",
        "Güllü - Sabah Olmadan", "Kamuran Akkor - Bir Ateşe Attın", "Ferdi Özbeğen - Gündüzüm Seninle",
        "Erol Budan - Harabe Gönlüm", "Hakan Gürses - Sensiz Hayat", "Bülent Ersoy - Unutamazsın",
        "Gökhan Güney - Bir Seni Düşündüm Bir de Kendimi", "Orhan Akdeniz - Bu Şehirde Yaşanmaz",
        "Selami Şahin - Ben Sana Mecburum", "Sibel Can - Padişah", "Yıldız Tilbe - Delikanlım",
    ],
}

# ============================== GENEL AYARLAR ==============================
APP_DIR = Path(__file__).resolve().parent


def _pick_data_dir():
    """Veriler script'in yanına yazılır; klasör yazılabilir değilse %APPDATA%\\GardasFM kullanılır."""
    try:
        t = APP_DIR / ".yazma_testi"
        t.write_text("x")
        t.unlink()
        return APP_DIR
    except Exception:
        d = Path(os.environ.get("APPDATA") or Path.home()) / "GardasFM"
        d.mkdir(parents=True, exist_ok=True)
        return d


DATA_DIR = _pick_data_dir()
MIX_FILE = DATA_DIR / "mix_listem.json"
MIX2_FILE = DATA_DIR / "mix_listesi.json"          # eski sürümden taşıma için okunur
PLAYLISTS_FILE = DATA_DIR / "calma_listeleri.json"
SETTINGS_FILE = DATA_DIR / "ayarlar.json"
CATALOG_FILE = DATA_DIR / "katalog.json"
CACHE_FILE = DATA_DIR / "onbellek.json"
LYRICS_FILE = DATA_DIR / "sozler.json"
DL_INDEX_FILE = DATA_DIR / "indirilenler.json"
LOG_FILE = DATA_DIR / "gardas_fm.log"
BG_DIR = DATA_DIR / "arkaplan"
DL_DIR = DATA_DIR / "indirilenler"
COVER_DIR = DL_DIR / "kapaklar"
# ---- Sürüm ve GitHub otomatik güncelleme ayarı: sadece GITHUB_REPO satırını kendi deponla değiştir ----
APP_VERSION = "8.2"
GITHUB_REPO = "croxy1993-beep/GardasFM-PC"   # GitHub deposu: kullanici/depo
GITHUB_BRANCH = "main"
GITHUB_FILE = "gardas_fm.py"                 # depoda uygulama dosyasının yolu (kökteyse böyle kalsın)
BACKUP_DIR = DATA_DIR / "yedek"
USER_DATA_FILES = ["mix_listem.json", "calma_listeleri.json", "ayarlar.json", "indirilenler.json", "sozler.json"]
RESTORE_FILES = ["mix_listem.json", "calma_listeleri.json", "ayarlar.json", "sozler.json"]   # "Yedekle" dosyasına girenler
PENDING_RESTORE = DATA_DIR / "geri_yukle.zip"          # geri yüklenecek yedek: bir sonraki açılışta uygulanır
LOGO_B64 = "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"   # gömülü logo (PNG, base64)
DISCORD_CLIENT_ID = "1561842805662552196"                  # Discord uygulama kimliği (herkese açık bilgi): giriş ve durum için

FORCE_UPDATE_BELOW = ""          # yeni sürümde doldurulursa (örn. "5.3") bundan eski sürümlerde güncelleme duvarında "Sonra" düğmesi gizlenir
OAUTH_PORT = 53682
# ---- Discord sunucu rolü kapısı (6.2): GUILD_ID boş bırakılırsa kapı KAPALIDIR, uygulama 6.1 gibi çalışır ----
GUILD_ID = "1551586915352969317"   # Discord sunucu kimliği (boş bırakılırsa rol kapısı KAPALI olur)
ALLOWED_ROLE_IDS = [             # izinli roller: bunlardan birine sahip olan girer ("Üyeler" rolü BİLEREK yok: herkesin rolü olabilir)
    "1563537068012085300",       # Doğrulanmış
    "1551587968823595148",       # Yönetici
    "1551587960116486266",       # Mekanın Sahibi
    "1551643958885490748",       # Kralinho
]
INVITE_URL = "https://discord.gg/WQdPWxEEC"   # kalıcı davet bağlantısı (giriş kartında "Sunucuya katıl" düğmesi)
TIKTOK_NAME = ""                 # örn. "@hesapadi" (kartta yönerge olarak yazar)
VERIFY_CHANNEL = "doğrulama"     # doğrulama kanalının adı (kartta yönerge olarak yazar)
STATS_FILE = DATA_DIR / "istatistik.json"
AVATAR_FILE = DATA_DIR / "profil_avatar.png"
FOUNDERS = [("Umut", "Dean", "1020761559141711882"), ("Kayra", "Kayra", "996042982291673130")]   # (profil adı, Discord adı, Discord kimliği): kimlik boşsa rozet verilmez
LIVE_FILE = DATA_DIR / "canli_katalog.json"
LIVE_CATS = {   # ad: (alt yazı, YouTube arama sorgusu, uzun videolara izin ver): kenar menüde "✦" ile görünür, YouTube'dan canlı yüklenir
    "Senin için yeni": ("Sevdiğin sanatçılardan yeni şarkılar", "", False),
    "Lo-fi Çalışma": ("Odaklan, rahatla", "lofi hip hop study beats mix", True),
    "Yeni Çıkanlar": ("Bu hafta çıkanlar", "yeni çıkan türkçe şarkılar", False),
    "Trend Türkçe": ("Herkes bunu dinliyor", "türkçe pop hit şarkılar 2026", False),
    "Dizi Film Müziği": ("Jenerikler ve unutulmaz sahneler", "dizi film müzikleri soundtrack", False),
    "Gece Yarısı": ("Slow, karanlık, uzun yol", "gece yarısı slow türkçe şarkılar", False),
    "Oyun Müziği": ("Oyun için enerji", "gaming music mix no copyright", True),
}
EXTRA_CATALOG = {   # katalog.json'a bir kere eklenir (sonradan silersen geri gelmez, kendi şarkılarını da ekleyebilirsin)
    "Türkçe Pop": [
        "Tarkan - Kuzu Kuzu", "Tarkan - Şımarık", "Tarkan - Hepsi Senin mi?", "Tarkan - Dudu", "Tarkan - Yolla",
        "Tarkan - Bir Oyundur", "Tarkan - Kış Güneşi", "Sezen Aksu - Firuze", "Sezen Aksu - Hadi Bakalım",
        "Sezen Aksu - Gülümse", "Sezen Aksu - Şarkı Söylemek Lazım", "Sertab Erener - Aşk", "Sertab Erener - Sakin Ol",
        "Sertab Erener - Everyway That I Can", "Hadise - Düm Tek Tek", "Hadise - Aşkkolik", "Gülşen - Bangır Bangır",
        "Gülşen - Be Adam", "Kenan Doğulu - Yaparım Bilirsin", "Kenan Doğulu - Tutamıyorum Zamanı",
        "Mustafa Sandal - Araba", "Mustafa Sandal - Aya Benzer", "Yıldız Tilbe - Delikanlım", "Hande Yener - Kırmızı",
        "Hande Yener - Acele Etme", "Ajda Pekkan - Bambaşka Biri", "Ajda Pekkan - Yakar Geçerim Dünyayı",
        "Simge - Aşkın Olayım", "Aleyna Tilki - Cevapsız Çınlama", "Murat Boz - Aşkı Bulamam Ben"],
    "Türkçe Rock": [
        "Duman - Her Şeyi Yak", "Duman - Köprüaltı", "Duman - Bu Akşam", "Duman - Senden Daha Güzel",
        "Mor ve Ötesi - Bir Derdim Var", "Mor ve Ötesi - Cambaz", "Mor ve Ötesi - Deli", "Teoman - İstanbul'da Sonbahar",
        "Teoman - Paramparça", "Teoman - Gönül", "manga - Beni Benimle Bırak", "manga - Bir Kadın Çizeceksin",
        "manga - Fly to Stay Alive", "Yüksek Sadakat - Belki Üstümüzden Bir Kuş Geçer", "Yüksek Sadakat - Sensiz",
        "Pinhani - Beni Sorarlarsa", "Pinhani - Dön Bebeğim", "Pinhani - Ben Kendim", "Gripin - Aşk Kadar",
        "Şebnem Ferah - Sil Baştan", "Şebnem Ferah - Hep Sonradan", "Şebnem Ferah - Sigara", "Haluk Levent - Elfida"],
    "Nostalji": [
        "Barış Manço - Gül Pembe", "Barış Manço - Dönence", "Barış Manço - Kol Düğmeleri",
        "Barış Manço - Can Bedenden Çıkmayınca", "Barış Manço - Gibi Gibi", "Barış Manço - Alla Beni Pulla Beni",
        "Barış Manço - Sözüm Meclisten Dışarı", "Cem Karaca - Resimdeki Gözyaşları", "Cem Karaca - Tamirci Çırağı",
        "Cem Karaca - Mutlu Ol Yeter", "Cem Karaca - Namus Belası", "Erkin Koray - Fesuphanallah", "Erkin Koray - Cemalim",
        "Selda Bağcan - Yaz Gazeteci Yaz", "MFÖ - Ele Güne Karşı", "MFÖ - Mavi Mavi", "MFÖ - Ali Desidero",
        "MFÖ - Peki Peki Anladık", "Kayahan - Prenses", "Sezen Aksu - Sen Ağlama"],
    "Elektronik Dance": [
        "Daft Punk - Get Lucky", "Daft Punk - One More Time", "Daft Punk - Harder Better Faster Stronger",
        "Avicii - Levels", "Avicii - Wake Me Up", "Avicii - Hey Brother", "Calvin Harris - Summer",
        "Calvin Harris - This Is What You Came For", "Swedish House Mafia - Don't You Worry Child",
        "Martin Garrix - Animals", "Alan Walker - Faded", "Kygo - Firestone", "The Chainsmokers - Closer",
        "Marshmello - Alone", "Zedd - Clarity", "David Guetta - Titanium", "David Guetta - Without You",
        "Tiësto - The Business", "Illenium - Good Things Fall Apart", "Major Lazer - Lean On", "Disclosure - Latch",
        "Robin Schulz - Sugar", "Lost Frequencies - Are You with Me", "Kungs - This Girl"],
    "Akustik Chill": [
        "Ed Sheeran - Perfect", "Ed Sheeran - Photograph", "Passenger - Let Her Go", "Lewis Capaldi - Someone You Loved",
        "James Arthur - Say You Won't Let Go", "Jeremy Zucker - comethru", "Billie Eilish - when the party's over",
        "Billie Eilish - ocean eyes", "Adele - Someone Like You", "Coldplay - Fix You", "Coldplay - Yellow",
        "Coldplay - The Scientist", "Sam Smith - Stay With Me", "John Legend - All of Me", "Lana Del Rey - Video Games",
        "Lana Del Rey - Summertime Sadness", "Hozier - Take Me to Church", "Hozier - Work Song", "Bon Iver - Skinny Love",
        "The Neighbourhood - Sweater Weather", "Cigarettes After Sex - Apocalypse", "Cigarettes After Sex - K.",
        "Arctic Monkeys - Do I Wanna Know?", "Arctic Monkeys - 505", "Radiohead - Creep"],
    "Enerji": [
        "Imagine Dragons - Believer", "Imagine Dragons - Thunder", "Imagine Dragons - Warriors",
        "Imagine Dragons - Whatever It Takes", "Imagine Dragons - Radioactive", "Linkin Park - Numb",
        "Linkin Park - In the End", "Linkin Park - Faint", "Linkin Park - Papercut", "Eminem - Lose Yourself",
        "Eminem - Till I Collapse", "Eminem - Not Afraid", "Skillet - Monster", "Skillet - Hero",
        "Fall Out Boy - Centuries", "Alan Walker - Alone", "Alan Walker - On My Way", "Survivor - Eye of the Tiger",
        "Kavinsky - Nightcall", "Gorillaz - Feel Good Inc.", "Thirty Seconds to Mars - Kings and Queens",
        "Bring Me The Horizon - Throne", "Papa Roach - Last Resort", "Three Days Grace - I Hate Everything About You",
        "Disturbed - Down with the Sickness"],
    "Latin": [
        "Luis Fonsi - Despacito", "Shakira - Hips Don't Lie", "Shakira - Waka Waka", "Shakira - Whenever, Wherever",
        "Daddy Yankee - Gasolina", "Bad Bunny - Tití Me Preguntó", "J Balvin - Mi Gente", "Enrique Iglesias - Bailando",
        "Ricky Martin - Livin' la Vida Loca", "Maluma - Felices los 4", "Camila Cabello - Havana", "Ozuna - Taki Taki",
        "Pitbull - Give Me Everything", "Jennifer Lopez - On the Floor", "Bad Bunny - Dákiti", "Rosalía - Malamente",
        "Karol G - Tusa", "Rauw Alejandro - Todo de Ti", "Sebastián Yatra - Traicionera", "Becky G - Mayores"],
}

MOODS = [   # (ad, alt yazı, katalog kategorileri, etiket): ana sayfadaki ruh hali karışıkları
    ("Sakin", "Yavaş, duygusal, çay yanında", ["Arabesk Damar", "Akustik Chill", "Popüler Pop"], "sakin"),
    ("Hareketli", "Tempo yüksek, enerji tam", ["Popüler Pop", "Elektronik Dance", "Latin", "Türkçe Pop"], "hareketli"),
    ("Gece sürüşü", "Cam açık, yol boş", ["Türkçe Rap", "Yabancı Rap", "Elektronik Dance", "Gece Yarısı"], "gece"),
    ("Çalışma", "Dikkat dağıtmayan akış", ["Akustik Chill", "Lo-fi Çalışma", "Rock Alternatif"], "çalışma"),
]

WHATS_NEW = [   # en yeni sürüm en üstte
    ("8.2", ["Yeni arayüzde tam ekran sözler: ⛶ düğmesi ya da L tuşu (kapatmak için Esc).", "Şarkı satırlarında İndir ve Listeye ekle düğmeleri, listelerde “Bu listeyi indir”, kenar menüde “Yeni liste”.", "Kenar menü sadeleşti: Kütüphane, Listelerim ve katlanabilir Keşfet bölümü."]),
    ("8.1", ["Gardaş FM logosu uygulamaya gömüldü: pencere, kısayol, menü ve yeni arayüz simgesi.", "EXE kurulum paketi desteği: tek dosyayla Python, VLC ve her şey otomatik kurulur."]),
    ("8.0", ["Yeni arayüz artık ana arayüz: açılışta kendiliğinden açılır. Ana sayfa, arama, favori ve sıra düğmeleri, canlı sözler, bulanık cam arka plan ve akıcı animasyonlar.", "Sözler düzeltildi: şarkı açıldıktan sonra gelen sözler de artık görünür.", "Klasik arayüz: yeni arayüzde sol alttaki “Klasik arayüz” düğmesi ya da tepsi simgesi. Ayarlar > Görünüm'den yeni arayüzü varsayılan olmaktan çıkarabilirsin."]),
    ("7.1", ["Yeni arayüz: hata olursa ekranda sebebi yazar, söz zamanlaması düzeltildi.", "Masaüstü kısayolu ve pencere simgesi artık Python simgesi yerine Gardaş FM simgesini gösterir (kısayolu Ayarlar > Sistem'den yeniden oluştur)."]),
    ("7.0", ["Yeni arayüz (beta): kenar menüde “Yeni arayüz” ya da F2 tuşuyla aç. Kapaktan renk alan bulanık arka plan, akıcı geçişler, canlı sözler ve ışıklı müzik halkası. Müziğin ve listelerin aynı, sadece görünüm yeni."]),
    ("6.6", ["Giriş kartına Discord sunucusuna katılma düğmesi eklendi."]),
    ("6.5", ["Discord rol kapısı AÇILDI: Gardaş FM'i kullanmak için sunucumuzda Doğrulanmış (ya da yetkili) role sahip olmak gerekir."]),
    ("6.4", ["Discord rol kapısı için izinli roller eklendi."]),
    ("6.3", ["Kayra kurucu olarak eklendi (doğrulanmış kurucu rozeti)."]),
    ("6.2", ["Discord sunucu doğrulaması: uygulamayı kullanmak için sunucumuzda doğrulanmış role sahip olmak gerekir. Rol verilince kendiliğinden açılır.",
             "Açılışta rol sessizce yeniden kontrol edilir; rol alınırsa erişim kapanır."]),
    ("6.1", ["Giriş zorunlu: Discord ile giriş yapmadan uygulama kullanılamaz. Bir kere giriş yeterli, sonraki açılışlarda sorulmaz.",
             "Kurucu doğrulaması düzeltildi: Umut (Dean) artık doğrulanmış kurucu olarak görünür."]),
    ("6.0", ["Profil: Discord ile giriş yap, adın ve resmin gelsin. Kurucular (Umut ve Kayra) doğrulanmış rozetle görünür, diğer herkes doğrulanmamış.",
             "Dinleme istatistikleri ve paylaşmalık aylık özet resmi (Ayarlar > Profil).",
             "Discord durumunda \"YouTube'da dinle\" butonu ve profil adın.",
             "Listeleri .gfm dosyasıyla arkadaşınla paylaş, .txt / .m3u olarak dışa aktar, tekrar eden şarkıları tek tuşla temizle (Diğer menüsü).",
             "Sözler geç ya da erken geliyorsa ] ve [ tuşlarıyla kaydır. Şarkı başına ses ayarı hatırlama (Ayarlar > Sistem)."]),
    ("5.5", ["Radyo modu: şarkıya sağ tık > Radyo başlat, ana sayfadaki Radyo kartı ya da R tuşu. YouTube'un benzer şarkı listesiyle sonsuz akar.",
             "Yumuşak geçiş: Ayarlar > Sistem > Ses ve geçiş. Şarkı bitmeden ses azalır, yeni şarkı yavaşça açılır.",
             "Sürükle-bırak sıralama: favorilerde, kendi listelerinde ve sırada şarkıyı fareyle tutup yukarı-aşağı taşı.",
             "Son temizlik ve kararlılık düzeltmeleri. Bu son sürümdür."]),
    ("5.3", ["Şarkı bul: kenar menüde yeni bölüm. Aklındaki sözü yazıp olası şarkıları listele ya da çalan şarkıyı dinleterek tanıt (AudD anahtarı gerekir).",
             "Neon kenarlar çalan şarkının kapak renginde parlar (Ayarlar > Görünüm'den kapatılabilir).",
             "Senin için yeni: favori sanatçılarının yeni çıkan şarkıları kenar menüde ve ana sayfada.",
             "F1: kısayol yardım penceresi."]),
    ("5.2", ["Güncelleme duvarı: yeni sürüm gelince pencere kilitlenir ve ortada kart çıkar; güncelleyince uygulama kendini otomatik yeniden başlatır.",
             "Yeni ayarlar ekranı: solda sekmeler, kartlar halinde düzenli ayarlar, Hakkında sekmesi ve teşhis paketi.",
             "Sol menü daraldı ve « düğmesiyle gizlenip açılır. 7 yeni katalog (Türkçe Pop, Türkçe Rock, Nostalji, Elektronik Dance, Akustik Chill, Enerji, Latin) ve YouTube'dan canlı yüklenen 6 katalog (✦ işaretli).",
             "Arama önerileri: yazdıkça listendeki eşleşmeler ve YouTube önerileri açılır.",
             "Kusursuz köşe ve simetri: taşan köşeler, kapak etrafındaki çift çerçeve, alt çubuğun ortalanması, uzun şarkı adının sanatçıyla çakışması düzeltildi.",
             "Tüm pencerelerde Gardaş FM logosu simgesi."]),
    ("5.1", ["Neon cam arayüz: paneller pembeden maviye geçişli, parlayan kenarlıklı cam gibi. Menüde ikonlar, seçili satırda pembe çizgi, mavi ilerleme ve ses çubukları, neon kapak çerçevesi ve mavi söz satırı."]),
    ("5.0", ["Yeni arayüz: neon kenarlıklı cam paneller, yeni başlık yazı tipi, tema renginden boyanan arka plan ışıkları ve 4 yeni tema (Neon Siber, Kırmızı Kadife, Gece Mavisi, Altın Saat).",
            "Daha fazla animasyon: sayfa başlıkları süzülerek gelir, kapak yeni şarkıda yumuşakça değişir, menüde seçim çubuğu kayar. Ayarlar'dan Tam / Hafif / Kapalı seçebilirsin.",
            "Şarkı değişince bildirim: uygulama arkadayken köşede kapaklı küçük bir kart çıkar, tıklayınca uygulama açılır.",
            "Ruh haline göre mix: ana sayfada Sakin, Hareketli, Gece sürüşü ve Çalışma karışıkları.",
            "Etiketler: şarkıya sağ tık > Etiketler. Etiketler kenar menüde listelenir, tıklayınca o etiketli şarkılar açılır.",
            "Güvenli güncelleme: yeni sürüm açılışta hata verirse otomatik olarak eski sürüme geri dönülür."]),
    ("4.7", ["Masaüstü kısayolu: Ayarlar'daki tek tuşla masaüstüne Gardaş FM kısayolu eklenir. Siyah konsol penceresi açılmaz, logon simge olur."]),
    ("4.6", ["Güncelleme kartı: yeni sürüm çıkınca ekranın ortasında logolu bir kart açılır, yenilikleri gösterir; tek tuşla güncelleyip kendini yeniden başlatır.",
             "Logo: pencere simgesi, güncelleme kartı ve yenilikler penceresinde Gardaş FM logosu (uygulama klasörüne logo.png koyman yeterli).",
             "Discord durumunda Gardaş FM logosu."]),
    ("4.5", ["Yedekle / geri yükle: Ayarlar'dan favorilerini, listelerini ve ayarlarını tek dosyaya yedekle, istediğin zaman geri yükle.",
             "Neler yeni penceresi: güncelleme sonrası ilk açılışta yenilikleri burada görürsün.",
             "Discord durumu: dinlediğin şarkı Discord profilinde görünür (Ayarlar > Discord)."]),
    ("4.4", ["GitHub'dan otomatik güncelleme: Gardaş FM günde bir kez yeni sürümü denetler ve kendini günceller.",
             "Güncellemeden önce favoriler ve listeler 'yedek' klasörüne kopyalanır."]),
]


def _backup_user_data():
    """Favoriler, mixler, çalma listeleri ve ayarlar 'yedek' klasörüne kopyalanır (son 5 yedek kalır)."""
    try:
        d = BACKUP_DIR / time.strftime("%Y%m%d_%H%M%S")
        d.mkdir(parents=True, exist_ok=True)
        for n in USER_DATA_FILES:
            f = DATA_DIR / n
            if f.exists():
                shutil.copy2(f, d / n)
        olds = sorted(p for p in BACKUP_DIR.iterdir() if p.is_dir())
        for p in olds[:-5]:
            shutil.rmtree(p, ignore_errors=True)
        return True
    except Exception as ex:
        print("Yedek alınamadı:", ex)
        return False


def _read_backup_zip(path):
    """Yedek zip'ini doğrular; {dosya_adı: bayt} döndürür, geçersizse None. Sadece bilinen dosya adları okunur."""
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if "yedek_bilgi.json" not in names:
            return None
        info = json.loads(zf.read("yedek_bilgi.json").decode("utf-8-sig"))
        if info.get("uygulama") != "GardasFM":
            return None
        out = {}
        for n in RESTORE_FILES:
            if n in names:
                if zf.getinfo(n).file_size > 100 * 1024 * 1024:
                    return None
                data = zf.read(n)
                json.loads(data.decode("utf-8-sig"))      # bozuk dosya geri yüklenmesin
                out[n] = data
        return out or None


def _apply_pending_restore():
    """Açılışta, hiçbir veri okunmadan önce: bekleyen yedeği uygular (şu anki veriler önce yedeklenir)."""
    if not PENDING_RESTORE.exists():
        return
    try:
        files = _read_backup_zip(PENDING_RESTORE)
        if files:
            _backup_user_data()
            for n, data in files.items():
                tmp = DATA_DIR / (n + ".tmp")
                tmp.write_bytes(data)
                os.replace(tmp, DATA_DIR / n)
    except Exception as ex:
        print("Yedek geri yüklenemedi:", ex)
    finally:
        try:
            PENDING_RESTORE.unlink()
        except Exception:
            pass


_apply_pending_restore()
AUDIO_EXT = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".opus", ".webm", ".aac", ".wma"}


class _Tee:
    """Konsol yazılarını (hata dökümleri dahil) gardas_fm.log dosyasına da yazar."""

    def __init__(self, orig, fh):
        self.orig, self.fh = orig, fh

    def write(self, s):
        try:
            self.fh.write(s)
            self.fh.flush()
        except Exception:
            pass
        if self.orig is not None:
            try:
                self.orig.write(s)
            except Exception:
                pass
        return len(s)

    def flush(self):
        try:
            if self.orig is not None:
                self.orig.flush()
        except Exception:
            pass


def _setup_log():
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > 512 * 1024:
            LOG_FILE.write_text("", encoding="utf-8")
        fh = open(LOG_FILE, "a", encoding="utf-8")
        fh.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} Gardaş FM başladı ---\n")
        sys.stdout, sys.stderr = _Tee(sys.stdout, fh), _Tee(sys.stderr, fh)
    except Exception:
        pass


_setup_log()


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, data):
    """Önce geçici dosyaya yazıp sonra yerine koyar: yarım kalan yazma dosyayı bozmaz."""
    try:
        p = Path(path)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, p)
    except Exception as ex:
        print("Kaydedilemedi:", path, ex)


def _merge_extra_catalog(cat):
    """5.2 kataloglarını katalog.json'a bir kere ekler; sonradan silersen geri gelmez."""
    try:
        marker = DATA_DIR / "katalog_eklenenler.json"
        done = set(load_json(marker, []))
        add = {k: v for k, v in EXTRA_CATALOG.items() if k not in cat and k not in done}
        if add:
            cat = {**cat, **add}
            save_json(CATALOG_FILE, cat)
        save_json(marker, sorted(done | set(EXTRA_CATALOG)))
    except Exception as ex:
        print("Yeni kataloglar eklenemedi:", ex)
    return cat


def _load_catalog():
    """Katalog katalog.json dosyasından okunur (yoksa yerleşik katalogdan oluşturulur): şarkıyı kodu açmadan ekleyebilirsin."""
    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data and all(isinstance(v, list) for v in data.values()):
            return _merge_extra_catalog({str(k): [str(s) for s in v if isinstance(s, str)] for k, v in data.items()})
    except FileNotFoundError:
        save_json(CATALOG_FILE, CATALOG)
    except Exception as ex:
        print("katalog.json okunamadı, yerleşik katalog kullanılıyor:", ex)
    return _merge_extra_catalog(dict(CATALOG))


CATALOG = _load_catalog()

HOME = "Ana sayfa"
SEARCH = "Arama"
MIX = "Favorilerim"
MIX2 = "Benim mix listem"
RECENT = "Son çalınanlar"
DOWNLOADS = "İndirilenler"
QUEUE = "Sıradakiler"
PL_PREFIX = "♪ "
NAV = list(CATALOG)
TAGLINES = {
    "Türkçe Rap": "Sokaktan, mikrofona",
    "Yabancı Rap": "Okyanus ötesinden bas ve ritim",
    "Popüler Pop": "Herkesin ağzında dolaşanlar",
    "Rock Alternatif": "Gitarlar, davullar, gürültü",
    "Arabesk Damar": "Gece geç saat, çay soğumuş",
    MIX: "Senin seçtiklerin",
    RECENT: "En son dinlediklerin",
    SEARCH: "Katalog + YouTube",
    "Türkçe Pop": "Herkesin bildiği melodiler",
    "Türkçe Rock": "Gitar ve Türkçe söz",
    "Nostalji": "Zamanın ötesinden",
    "Elektronik Dance": "Bas, ışık, hareket",
    "Akustik Chill": "Sakin akşamlar için",
    "Enerji": "Sahneye çık",
    "Latin": "Ritim ve sıcaklık",
}
for _n, (_a, _q, _l) in LIVE_CATS.items():
    TAGLINES[_n] = _a
TAGLINES[MIX2] = "Kendi karışık listen"
TAGLINES[DOWNLOADS] = "İnternetsiz de çalar"
TAGLINES[QUEUE] = "Sıradaki şarkılar"

# Gece İstanbul paleti
BG = "#0b0918"
PANEL = "#14102e"
PANEL_RGB = (20, 16, 46)
GLASS = (14, 11, 34)
ACCENT = "#ff4f8b"
ACCENT_RGB = (255, 79, 139)
GOLD = "#ffc857"
TEXT = "#ece9ff"
SOFT = "#cfc9f5"
MUTED = "#9a94c4"
BTN = "#241e4d"
ROW_ALT = "#1a1540"
HEAD_FONT = "Georgia"
BODY_FONT = "Segoe UI"

DEFAULT_CFG = {"volume": 70, "shuffle": False, "repeat": 0, "view": HOME, "bg": "", "dim": 0.45,
               "blur": 6, "intro": True, "searches": [], "recent": [], "theme": "Gece İstanbul",
               "eq": "Düz", "rate": 1.0, "offline": False, "tray": False, "plays": [], "ytdlp_day": 0.0, "auto_update": True, "update_day": 0.0,
               "discord": False, "discord_id": "", "last_seen": "",
               "anim": "Tam", "notify": True, "tags": {}, "bad_version": "", "side_open": True, "cover_color": True, "audd_token": "", "fade": 0, "webui_default": True, "song_vol_on": False, "song_vol": {}, "lyr_off": {}}

THEMES = {
    "Gece İstanbul": ("#ff4f8b", (255, 79, 139), "#ffc857"),
    "Okyanus": ("#2ec4ff", (46, 196, 255), "#ffe066"),
    "Orman": ("#3ddc97", (61, 220, 151), "#ffd166"),
    "Gün batımı": ("#ff7a45", (255, 122, 69), "#ffd23f"),
    "Mor sis": ("#a78bfa", (167, 139, 250), "#f9a8d4"),
    "Neon Siber": ("#00e5ff", (0, 229, 255), "#ff4fd8"),
    "Kırmızı Kadife": ("#ff3d57", (255, 61, 87), "#ffb86b"),
    "Gece Mavisi": ("#5b8cff", (91, 140, 255), "#7ee0ff"),
    "Altın Saat": ("#ffb020", (255, 176, 32), "#ff7a7a"),
}
_th = THEMES.get(str(load_json(SETTINGS_FILE, {}).get("theme", "")))
if _th:                                  # tema, arayüz kurulmadan önce uygulanır (değişince yeniden aç)
    ACCENT, ACCENT_RGB, GOLD = _th
ACCENT_HOVER = "#%02x%02x%02x" % tuple(int(c * 0.88) for c in ACCENT_RGB)
GOLD_RGB = tuple(int(GOLD[i:i + 2], 16) for i in (1, 3, 5))
EDGE = tuple(ACCENT_RGB) + (78,)          # panellerin neon kenar çizgisi (tema rengi)
_hh = colorsys.rgb_to_hsv(*[c / 255 for c in ACCENT_RGB])[0] * 360
NEON2 = "#4db8ff" if (_hh < 150 or _hh > 290) else "#ff5fa2"          # kenar çizgisinin ikinci rengi (pembe temada mavi)
NEON2_RGB = tuple(int(NEON2[i:i + 2], 16) for i in (1, 3, 5))
_NEON_DYN = None                        # (renk1, renk2): çalan şarkının kapak rengi; None ise tema renkleri
NEON2_DIM = "#%02x%02x%02x" % tuple(int(c * 0.55 + p * 0.45) for c, p in zip(NEON2_RGB, (20, 16, 46)))

ctk.set_appearance_mode("dark")

# ============================== SİNEMATİK AÇILIŞ (Jarvis'ten uyarlandı) ==============================
# Jarvis'teki "Uzay -> Türkiye -> Şehriniz" sahnesinin Python karşılığı:
#   yıldızlı siyah ekran, gerçek OpenStreetMap haritası (Jarvis'teki renk filtresiyle),
#   Leaflet'in flyTo algoritmasıyla uçuş, HUD yazıları, hedef artısı, radar, ilerleme çubuğu ve bip sesleri.
try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageTk
    INTRO_OK = True
except Exception:      # Pillow yoksa uygulama açılış olmadan çalışır
    INTRO_OK = False

try:
    import winsound
except Exception:
    winsound = None

import io
import struct
import wave
import tkinter.font as tkfont

HUD_RENK = "#22d3ee"        # Jarvis'teki --accent2 (istersen ACCENT veya GOLD yap)
DIM_RENK = "#8b949e"        # Jarvis'teki --text-dim
KONUM_ZORLA = None          # IP yerine sabit konum için örn: ("Antalya", 36.8969, 30.7133)
SON_YAZI = "GARDAŞ FM ONLINE"
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE_DIR = Path(__file__).resolve().parent / "harita_onbellek"
TILE_UA = {"User-Agent": "GardasFM/1.0 (kisisel muzik calar acilis animasyonu)"}


# ---------------------------------------------------------------- yardımcılar
def _clamp(t, lo=0.0, hi=1.0):
    return max(lo, min(hi, t))


def _ease(t):
    t = _clamp(t)
    return t * t * (3 - 2 * t)


def _mix(c1, c2, t):
    t = _clamp(t)
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def _tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def _lon_to_x(lon, z):
    return (lon + 180.0) / 360.0 * 256 * 2 ** z


def _lat_to_y(lat, z):
    lat = max(min(lat, 85.0511), -85.0511)
    r = math.radians(lat)
    return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 256 * 2 ** z


def _x_to_lon(x, z):
    return x / (256 * 2 ** z) * 360.0 - 180.0


def _y_to_lat(y, z):
    n = math.pi - 2 * math.pi * y / (256 * 2 ** z)
    return math.degrees(math.atan(math.sinh(n)))


class FlyPath:
    """Leaflet map.flyTo() algoritmasının (van Wijk) Python karşılığı."""
    RHO = 1.42

    def __init__(self, start, end, z0, z1, size, duration):
        self.end, self.z0, self.z1, self.duration = end, z0, z1, duration
        self.p0 = (_lon_to_x(start[1], z0), _lat_to_y(start[0], z0))
        self.p1 = (_lon_to_x(end[1], z0), _lat_to_y(end[0], z0))
        self.w0 = float(max(size))
        w1 = self.w0 * 2 ** (z0 - z1)        # Leaflet: getZoomScale(startZoom, targetZoom)
        self.u1 = math.hypot(self.p1[0] - self.p0[0], self.p1[1] - self.p0[1]) or 1.0
        self.rho2 = self.RHO ** 2

        def r(i):
            s1 = -1 if i else 1
            s2 = w1 if i else self.w0
            t1 = w1 * w1 - self.w0 * self.w0 + s1 * self.rho2 * self.rho2 * self.u1 * self.u1
            b = t1 / (2 * s2 * self.rho2 * self.u1)
            sq = math.sqrt(b * b + 1) - b
            return -18.0 if sq < 1e-9 else math.log(sq)

        self.r0 = r(0)
        self.S = (r(1) - self.r0) / self.RHO

    def _w(self, s):
        return self.w0 * (math.cosh(self.r0) / math.cosh(self.r0 + self.RHO * s))

    def _u(self, s):
        return self.w0 * (math.cosh(self.r0) * math.tanh(self.r0 + self.RHO * s) - math.sinh(self.r0)) / self.rho2

    def at(self, t):
        """t: 0..1 -> (enlem, boylam, zoom)"""
        if t >= 1:
            return self.end[0], self.end[1], float(self.z1)
        t = max(t, 0.0)
        s = (1 - (1 - t) ** 1.5) * self.S
        f = self._u(s) / self.u1
        px = self.p0[0] + (self.p1[0] - self.p0[0]) * f
        py = self.p0[1] + (self.p1[1] - self.p0[1]) * f
        return _y_to_lat(py, self.z0), _x_to_lon(px, self.z0), self.z0 + math.log2(self.w0 / self._w(s))


def tiles_for(lat, lon, zoom, W, H):
    """Bu görünüm için gereken harita karoları ve yerleşim bilgisi."""
    zt = max(0, min(18, int(math.floor(zoom + 1e-6))))   # hep büyütme: küçültmeden çok daha hızlı
    scale = 2.0 ** (zoom - zt)
    cx, cy = _lon_to_x(lon, zt), _lat_to_y(lat, zt)
    hw, hh = W / (2 * scale), H / (2 * scale)
    x0, x1 = int(math.floor((cx - hw) / 256)), int(math.floor((cx + hw) / 256))
    y0, y1 = int(math.floor((cy - hh) / 256)), int(math.floor((cy + hh) / 256))
    return zt, (cx - hw, cy - hh, hw, hh), (x0, x1, y0, y1)


def plan_path(fly, W, H, steps=60):
    """Uçuş boyunca gerekecek karoları, ihtiyaç sırasına göre listeler."""
    keys, seen = [], set()
    for i in range(steps + 1):
        lat, lon, z = fly.at(i / steps)
        zt, _, (x0, x1, y0, y1) = tiles_for(lat, lon, z, W, H)
        n = 1 << zt
        for ty in range(y0, y1 + 1):
            if 0 <= ty < n:
                for tx in range(x0, x1 + 1):
                    k = (zt, tx % n, ty)
                    if k not in seen:
                        seen.add(k)
                        keys.append(k)
    return keys


def plan_static(lat, lon, zoom, W, H):
    zt, _, (x0, x1, y0, y1) = tiles_for(lat, lon, zoom, W, H)
    n = 1 << zt
    return [(zt, tx % n, ty) for ty in range(y0, y1 + 1) if 0 <= ty < n for tx in range(x0, x1 + 1)]


# ---------------------------------------------------------------- harita karoları + Jarvis'in CSS filtresi
def _m(rows, off=(0, 0, 0)):
    return (rows[0][0], rows[0][1], rows[0][2], off[0],
            rows[1][0], rows[1][1], rows[1][2], off[1],
            rows[2][0], rows[2][1], rows[2][2], off[2])


def css_filter(img):
    """filter: saturate(.55) brightness(.7) hue-rotate(190deg) contrast(1.15)  (Jarvis #sinematik-harita)"""
    s = 0.55
    img = img.convert("RGB", _m(((0.213 + 0.787 * s, 0.715 - 0.715 * s, 0.072 - 0.072 * s),
                                 (0.213 - 0.213 * s, 0.715 + 0.285 * s, 0.072 - 0.072 * s),
                                 (0.213 - 0.213 * s, 0.715 - 0.715 * s, 0.072 + 0.928 * s))))
    b = 0.7
    img = img.convert("RGB", _m(((b, 0, 0), (0, b, 0), (0, 0, b))))
    a = math.radians(190)
    c, sn = math.cos(a), math.sin(a)
    img = img.convert("RGB", _m(((0.213 + c * 0.787 - sn * 0.213, 0.715 - c * 0.715 - sn * 0.715, 0.072 - c * 0.072 + sn * 0.928),
                                 (0.213 - c * 0.213 + sn * 0.143, 0.715 + c * 0.285 + sn * 0.140, 0.072 - c * 0.072 - sn * 0.283),
                                 (0.213 - c * 0.213 - sn * 0.787, 0.715 - c * 0.715 + sn * 0.715, 0.072 + c * 0.928 + sn * 0.072))))
    k = 1.15
    off = (0.5 - 0.5 * k) * 255
    return img.convert("RGB", _m(((k, 0, 0), (0, k, 0), (0, 0, k)), (off, off, off)))


class TileStore:
    """OSM karolarını arka planda indirir, diske kaydeder (bir kez inen karo bir daha inmez)."""

    def __init__(self, workers=4):
        self.tiles = {}
        self.queued = set()
        self.alive = True
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.session = requests.Session()
        self.session.headers.update(TILE_UA)

    def request(self, keys):
        for k in keys:
            if k not in self.queued:
                self.queued.add(k)
                self.pool.submit(self._load, k)

    def _load(self, key):
        if not self.alive:
            return
        z, x, y = key
        path = TILE_DIR / str(z) / str(x) / f"{y}.png"
        data = None
        try:
            if path.exists():
                data = path.read_bytes()
            else:
                r = self.session.get(TILE_URL.format(z=z, x=x, y=y), timeout=8)
                if r.status_code == 200:
                    data = r.content
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
            if data and self.alive:
                self.tiles[key] = css_filter(Image.open(io.BytesIO(data)).convert("RGB"))
        except Exception as ex:
            print("Karo alınamadı", key, ex)

    def get(self, z, x, y):
        t = self.tiles.get((z, x, y))
        if t is not None:
            return t
        for d in (1, 2, 3, 4):          # karo henüz inmediyse bir üst seviyeden büyütülmüş hali
            if z - d < 0:
                break
            p = self.tiles.get((z - d, x >> d, y >> d))
            if p is not None:
                size = 256 >> d
                ox, oy = (x & ((1 << d) - 1)) * size, (y & ((1 << d) - 1)) * size
                return p.crop((ox, oy, ox + size, oy + size)).resize((256, 256), Image.BILINEAR)
        return None

    def close(self):
        self.alive = False
        try:
            self.pool.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass


def render_map(store, lat, lon, zoom, W, H, fast=False):
    zt, (left, top, hw, hh), (x0, x1, y0, y1) = tiles_for(lat, lon, zoom, W, H)
    scale = 2.0 ** (zoom - zt)
    n = 1 << zt
    mosaic = Image.new("RGB", ((x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256), (0, 0, 0))
    for ty in range(y0, y1 + 1):
        if 0 <= ty < n:
            for tx in range(x0, x1 + 1):
                tile = store.get(zt, tx % n, ty)
                if tile is not None:
                    mosaic.paste(tile, ((tx - x0) * 256, (ty - y0) * 256))
    bx, by = left - x0 * 256, top - y0 * 256
    mw, mh = mosaic.size
    if abs(scale - 1.0) < 1e-6:                      # tam zoom seviyesi: büyütme yok, sadece kırp (çok hızlı)
        ix = max(0, min(int(round(bx)), mw - W))
        iy = max(0, min(int(round(by)), mh - H))
        return mosaic.crop((ix, iy, ix + W, iy + H))
    box = (max(0.0, bx), max(0.0, by), min(float(mw), bx + 2 * hw), min(float(mh), by + 2 * hh))
    return mosaic.resize((W, H), Image.NEAREST if fast else Image.BILINEAR, box=box)


# ---------------------------------------------------------------- bip sesi (Jarvis'teki sinematikBipCal)
_beep_cache = {}


def make_beep(freq, dur, gain=0.06):
    key = (freq, dur)
    if key not in _beep_cache:
        rate = 22050
        n = int(rate * dur)
        frames = bytearray()
        for i in range(n):
            g = gain * (0.0001 / gain) ** (i / n)       # üstel azalan ses zarfı
            frames += struct.pack("<h", int(32767 * g * math.sin(2 * math.pi * freq * i / rate)))
        buf = io.BytesIO()
        w = wave.open(buf, "wb")
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
        w.close()
        _beep_cache[key] = buf.getvalue()
    return _beep_cache[key]


class CinematicIntro:
    """Uzay -> Türkiye -> Şehriniz. Bitince (ya da tıklanınca) kendini kaldırır ve on_done() çağırır."""

    HUD_ADIM = 5            # harf aralığı (px)
    COORD_ADIM = 2

    def __init__(self, root, on_done=None):
        self.root = root
        self.on_done = on_done
        self.alive = True
        self.W = self.H = 0
        self.cv = tk.Canvas(root, bg="black", highlightthickness=0, cursor="hand2")
        self.cv.place(x=0, y=0, relwidth=1, relheight=1)
        self.cv.bind("<Button-1>", lambda e: self.finish())
        root.bind("<Escape>", lambda e: self.finish(), add="+")

        self.hud_font = tkfont.Font(family="Consolas", size=-13)
        self.crd_font = tkfont.Font(family="Consolas", size=-11)
        self.skip_font = tkfont.Font(family="Segoe UI", size=-11)
        self.store = TileStore()
        self.t0 = None
        self.view = (15.0, 20.0, 2.0)          # Jarvis: setView([15, 20], 2)
        self.map_since = None
        self.fly = None
        self.fly_t0 = 0.0
        self.geo = None
        self.geo_planned = False
        self.hud_text, self.hud_new, self.hud_t, self.hud_swap = "", "", -9.0, -9.0
        self.prog_from = self.prog_to = 0.0
        self.prog_t = -9.0
        self.radar_t0 = None
        self.cross_t0 = None
        self.coord_text, self.coord_t0 = "", None
        self.script = self._script()
        self.wait_until = 0.0
        self.photo = None
        self.img_item = None
        self.ema = 0.03          # ortalama kare süresi (sn)
        self.last_frame = None
        threading.Thread(target=self._geo_job, daemon=True).start()
        self.root.after(20, self._frame)

    # ------------------------------------------------ konum (Jarvis: ipapi.co/json)
    def _geo_job(self):
        res = {"lat": 39.0, "lon": 35.0, "sehir": "Bilinmiyor", "ulke": "Türkiye"}
        try:
            if KONUM_ZORLA:
                res.update(sehir=KONUM_ZORLA[0], lat=KONUM_ZORLA[1], lon=KONUM_ZORLA[2])
            else:
                k = requests.get("https://ipapi.co/json/", timeout=5, headers=TILE_UA).json()
                if k and k.get("latitude") is not None:
                    res.update(lat=float(k["latitude"]), lon=float(k["longitude"]),
                               sehir=k.get("city") or res["sehir"], ulke=k.get("country_name") or res["ulke"])
        except Exception as ex:
            print("Konum alınamadı, varsayılan kullanılıyor:", ex)
        if res["ulke"] == "Turkey":
            res["ulke"] = "Türkiye"
        self.geo = res

    # ------------------------------------------------ hazırlık (boyut değişince yeniden)
    def _prepare(self, W, H):
        self.W, self.H = W, H
        # yıldızlar: 300x300 döşeme, Jarvis'teki radial-gradient noktalarıyla aynı konumlar
        st = Image.new("RGB", (W + 300, H + 300), (0, 0, 0))
        d = ImageDraw.Draw(st)
        pts = [(.20, .30, 1), (.70, .60, 1), (.40, .80, 1), (.90, .20, 2), (.10, .90, 1), (.85, .85, 1),
               (.55, .15, 1), (.25, .55, 1)]
        for ox in range(0, W + 300, 300):
            for oy in range(0, H + 300, 300):
                for fx, fy, r in pts:
                    x, y = ox + fx * 300, oy + fy * 300
                    d.ellipse((x - r - 1, y - r - 1, x + r + 1, y + r + 1), fill=(45, 45, 45))
                    d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 150, 150))
        self.stars = st
        # vinyet: inset 0 0 160px 60px #000  +  tarama çizgileri (3px'te bir, %6)
        hole = Image.new("L", (W, H), 255)
        ImageDraw.Draw(hole).rectangle((60, 60, W - 61, H - 61), fill=0)
        shadow = hole.filter(ImageFilter.GaussianBlur(80))
        clear = ImageChops.invert(shadow)
        scan_mul = Image.new("L", (W, H), 255)
        dm = ImageDraw.Draw(scan_mul)
        for y in range(H - 1, -1, -3):
            dm.line((0, y, W, y), fill=245)        # çok hafif tarama çizgisi (3 pikselde bir)
        mul = ImageChops.multiply(clear, scan_mul)
        self.mul = Image.merge("RGB", (mul, mul, mul))
        self.photo = ImageTk.PhotoImage(Image.new("RGB", (W, H)))
        self.cv.delete("all")
        self.img_item = self.cv.create_image(0, 0, anchor="nw", image=self.photo)
        # başlangıç ve Türkiye uçuşu için karoları indirmeye başla
        self.fly1 = FlyPath((15.0, 20.0), (39.0, 35.0), 2, 6, (W, H), 2.1)
        self.store.request(plan_static(15.0, 20.0, 2.0, W, H) + plan_path(self.fly1, W, H))

    # ------------------------------------------------ senaryo (Jarvis'teki await zinciri)
    def _now(self):
        return time.perf_counter()

    def _hud(self, text):
        now = self._now()
        self.hud_new, self.hud_t, self.hud_swap = text, now, now + 0.22

    def _progress(self, pct):
        self.prog_from = self._display_progress()
        self.prog_to = pct
        self.prog_t = self._now()

    def _display_progress(self):
        return self.prog_from + (self.prog_to - self.prog_from) * _clamp((self._now() - self.prog_t) / 0.3)

    def _beep(self, freq, dur):
        if winsound is None:
            return
        try:
            self._beep_data = make_beep(freq, dur)
            winsound.PlaySound(self._beep_data, winsound.SND_MEMORY | winsound.SND_ASYNC)
        except Exception:
            pass

    def _fly(self, path):
        self.fly, self.fly_t0 = path, self._now()

    def _script(self):
        self._beep(440, 0.15)
        self._hud("SYSTEM INITIALIZING")
        self._progress(8)
        yield 1100
        self._hud("GEOLOCATION SCANNING")
        self._progress(22)
        waited = 0
        while self.geo is None and waited < 6000:      # konum cevabını bekle
            yield 50
            waited += 50
        if self.geo is None:
            self.geo = {"lat": 39.0, "lon": 35.0, "sehir": "Bilinmiyor", "ulke": "Türkiye"}
        g = self.geo
        self.fly2 = FlyPath((39.0, 35.0), (g["lat"], g["lon"]), 6, 12, (self.W, self.H), 2.1)
        self.store.request(plan_path(self.fly2, self.W, self.H) + plan_static(g["lat"], g["lon"], 12.0, self.W, self.H))
        self.map_since = self._now()                    # harita belirir (1.3 sn solarak)
        yield 700
        self._hud("LOCATION IDENTIFIED")
        self._progress(38)
        yield 900
        self._hud(_tr_upper(g["ulke"]))
        self._progress(55)
        self._fly(self.fly1)
        yield 2300
        self._hud(_tr_upper(g["sehir"]))
        self._progress(75)
        self._fly(self.fly2)
        yield 2000
        now = self._now()
        self.radar_t0 = self.cross_t0 = self.coord_t0 = now
        self.coord_text = (f"{abs(g['lat']):.4f}°{'K' if g['lat'] >= 0 else 'G'}  "
                           f"{abs(g['lon']):.4f}°{'D' if g['lon'] >= 0 else 'B'}")
        self._hud("LOCATION CONFIRMED")
        self._progress(90)
        self._beep(660, 0.12)
        yield 1300
        self._hud(SON_YAZI)
        self._progress(100)
        self._beep(880, 0.2)
        yield 1000

    # ------------------------------------------------ kare çizimi
    def _frame(self):
        if not self.alive:
            return
        W, H = self.cv.winfo_width(), self.cv.winfo_height()
        if W < 300 or H < 200:                           # pencere henüz hazır değil
            self.root.after(30, self._frame)
            return
        if (W, H) != (self.W, self.H):
            self._prepare(W, H)
        now = self._now()
        if self.t0 is None:
            self.t0 = now
        if now >= self.wait_until:
            try:
                self.wait_until = now + next(self.script) / 1000.0
            except StopIteration:
                self.finish()
                return

        t = now - self.t0
        cx0, cy0 = int((13.333 * t) % 300), int((-6.667 * t) % 300)
        frame = self.stars.crop((cx0, cy0, cx0 + W, cy0 + H))
        if self.map_since is not None:
            if self.fly is not None:
                self.view = self.fly.at((now - self.fly_t0) / self.fly.duration)
            mp = render_map(self.store, *self.view, W, H, fast=self.ema > 0.07)
            op = _ease((now - self.map_since) / 1.3)
            frame = mp if op >= 1 else Image.blend(frame, mp, op)
        frame = ImageChops.multiply(frame, self.mul)
        if self.radar_t0 is not None:
            self._paste_radar(frame, now)
        self.photo.paste(frame)
        self._draw_ui(now)
        done = self._now()
        self.ema = 0.9 * self.ema + 0.1 * (done - now)
        self.root.after(1, self._frame)

    def _paste_radar(self, frame, now):
        ph = ((now - self.radar_t0) % 1.5) / 1.5
        spread = 46 * (1 - (1 - ph) ** 2)
        alpha = 0.65 * (1 - (1 - (1 - ph) ** 2))
        S = 2
        size = 130
        ov = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        c = size * S / 2
        r = (6 + spread) * S
        d.ellipse((c - r, c - r, c + r, c + r), fill=(34, 211, 238, int(255 * alpha)))
        d.ellipse((c - 6 * S, c - 6 * S, c + 6 * S, c + 6 * S), fill=(34, 211, 238, 255))
        ov = ov.resize((size, size), Image.LANCZOS)
        frame.paste(ov, (self.W // 2 - size // 2, self.H // 2 - size // 2), ov)

    def _spaced(self, text, font, step, x_center, y, color, glow=None):
        cv = self.cv
        adv = font.measure("M") + step
        total = adv * len(text) - step
        x = x_center - total / 2 + adv / 2 - step / 2
        for ch in text:
            if ch != " ":
                if glow:
                    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        cv.create_text(x + dx, y + dy, text=ch, font=font, fill=glow, tags="ui")
                cv.create_text(x, y, text=ch, font=font, fill=color, tags="ui")
            x += adv

    def _draw_ui(self, now):
        cv, W, H = self.cv, self.W, self.H
        cv.delete("ui")
        # ekran köşelerindeki HUD çerçeveleri (opacity .5)
        kc = _mix("#000000", HUD_RENK, 0.5)
        for sx, sy, ax, ay in ((22, 22, 1, 1), (W - 22, 22, -1, 1), (22, H - 22, 1, -1), (W - 22, H - 22, -1, -1)):
            cv.create_line(sx, sy + ay * 34, sx, sy, sx + ax * 34, sy, fill=kc, width=2, tags="ui")
        # hedef artısı
        if self.cross_t0 is not None:
            a = _ease((now - self.cross_t0) / 0.5)
            sc = 1.4 - 0.4 * a
            half = 45 * sc
            cx, cy = W / 2, H / 2
            line, glow = _mix("#000000", HUD_RENK, a), _mix("#000000", HUD_RENK, 0.35 * a)
            for wd, col in ((3, glow), (1, line)):
                cv.create_line(cx - half + 8 * sc, cy, cx + half - 8 * sc, cy, fill=col, width=wd, tags="ui")
                cv.create_line(cx, cy - half + 8 * sc, cx, cy + half - 8 * sc, fill=col, width=wd, tags="ui")
            bc, k = _mix("#000000", HUD_RENK, 0.85 * a), 16 * sc
            for sx, sy, ax, ay in ((cx - half, cy - half, 1, 1), (cx + half, cy - half, -1, 1),
                                   (cx - half, cy + half, 1, -1), (cx + half, cy + half, -1, -1)):
                cv.create_line(sx, sy + ay * k, sx, sy, sx + ax * k, sy, fill=bc, width=2, tags="ui")
        # HUD yazısı (değişirken solar, harfler aralıklı, hafif parıltı)
        if now >= self.hud_swap and self.hud_new != self.hud_text:
            self.hud_text = self.hud_new
        if self.hud_text:
            a = _clamp((now - self.hud_swap) / 0.4) if now >= self.hud_swap else _clamp(1 - (now - self.hud_t) / 0.4)
            if a > 0.02:
                self._spaced(self.hud_text, self.hud_font, self.HUD_ADIM, W / 2, H - 78 - 8,
                             _mix("#000000", HUD_RENK, a), _mix("#000000", HUD_RENK, 0.22 * a))
        # koordinat
        if self.coord_text:
            a = _ease((now - self.coord_t0) / 0.4) * 0.85
            self._spaced(self.coord_text, self.crd_font, self.COORD_ADIM, W / 2, H - 56 - 7,
                         _mix("#000000", DIM_RENK, a))
        # ilerleme çubuğu
        x0, y0 = W / 2 - 110, H - 34
        cv.create_rectangle(x0, y0 - 2, x0 + 220, y0, fill="#1f1f1f", outline="", tags="ui")
        w = 220 * self._display_progress() / 100
        if w > 0:
            cv.create_rectangle(x0, y0 - 2, x0 + w, y0, fill=HUD_RENK, outline="", tags="ui")
        cv.create_text(W - 28, H - 24, text="Atlamak için tıklayın →", font=self.skip_font, fill=DIM_RENK,
                       anchor="se", tags="ui")

    # ------------------------------------------------ bitiş
    def finish(self):
        if not self.alive:
            return
        self.alive = False
        if winsound is not None:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        self.store.close()
        try:
            self.root.unbind("<Escape>")
        except Exception:
            pass
        self.cv.destroy()
        self.store.tiles.clear()
        if self.on_done:
            self.on_done()
# =================================================================================================



# yt-dlp ayarları: hızlı mod (gereksiz istekleri atlar), olmazsa normal mod
YDL_FAST = {"quiet": True, "no_warnings": True, "format": "bestaudio/best", "noplaylist": True,
            "socket_timeout": 10, "extractor_args": {"youtube": {"skip": ["hls", "translated_subs"]}}}
YDL_PLAIN = {"quiet": True, "no_warnings": True, "format": "bestaudio/best", "noplaylist": True}


# ============================== YARDIMCI FONKSİYONLAR ==============================
def key_of(it):
    return it["url"] or f"{it['artist']} - {it['title']}"


def split_name(s: str):
    if " - " in s:
        a, t = s.split(" - ", 1)
        return a.strip(), t.strip()
    return "", s.strip()


def make_item(artist, title, url=None, dur=None):
    return {"artist": artist, "title": title, "url": url, "dur": dur}


_TR = str.maketrans({"İ": "i", "I": "i", "ı": "i", "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g",
                     "Ü": "u", "ü": "u", "Ö": "o", "ö": "o", "Ç": "c", "ç": "c"})


def fold(s):
    """Arama için normalleştirme: büyük/küçük harf, Türkçe harfler (İ ı ş ğ ü ö ç) ve aksanlar yok sayılır."""
    s = unicodedata.normalize("NFKD", (s or "").translate(_TR).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


def is_local(it):
    return (it.get("url") or "").startswith("local:")


def fmt_total(sec):
    sec = int(sec)
    h, m = divmod(sec // 60, 60)
    return f"{h} sa {m} dk" if h else f"{m} dk"


_BAD_WORDS = ("cover", "live", "canli", "remix", "karaoke", "instrumental", "8d", "slowed", "reverb",
              "sped up", "nightcore", "concert", "konser", "mashup", "reaction", "tutorial", "lesson")


def pick_best(entries, artist, title):
    """YouTube arama sonuçları arasından doğru kaydı seçer (cover/canlı/remix/karaoke ve yanlış süreyi eler,
    'Sanatçı - Topic' ve resmî kayıtları öne alır)."""
    want_t, want_a = fold(title), fold(artist)
    words = [w for w in re.findall(r"\w+", want_t) if len(w) > 2]
    best, best_score = None, -10 ** 9
    for i, e in enumerate(entries):
        et, ch = fold(e.get("title")), fold(e.get("channel") or e.get("uploader"))
        s = -2 * i
        for bad in _BAD_WORDS:
            if re.search(rf"\b{re.escape(bad)}\b", et) and not re.search(rf"\b{re.escape(bad)}\b", want_t):
                s -= 60
        d = e.get("duration")
        if d:
            if d < 60 or d > 720:
                s -= 80
            elif 90 <= d <= 480:
                s += 10
        if want_a and (want_a in et or want_a in ch):
            s += 30
        if ch.endswith("- topic"):
            s += 25
        if "official" in et or "resmi" in et or "audio" in et or "vevo" in ch:
            s += 10
        s += 8 * sum(1 for w in words if w in et)
        if s > best_score:
            best, best_score = e, s
    return best


def dominant_color(im):
    """Kapak resminden canlı, baskın bir renk seçer (arayüz animasyonları bu renge boyanır)."""
    small = im.convert("RGB").resize((32, 32))
    best, best_s = None, -1.0
    for cnt, (r, g, b) in small.getcolors(2048) or []:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if v < 0.25:
            continue
        score = cnt * (0.25 + s) * (0.5 + v)
        if score > best_s:
            best, best_s = (h, s, v), score
    if best is None:
        return ACCENT_RGB
    h, s, v = best
    r, g, b = colorsys.hsv_to_rgb(h, max(s, 0.45), max(v, 0.75))
    return (int(r * 255), int(g * 255), int(b * 255))


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def _mix_rgb(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(x + (y - x) * t for x, y in zip(a, b))


_LRC = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")


def parse_lrc(text: str):
    """lrclib'in senkronlu söz formatını [(saniye, satır), ...] listesine çevirir."""
    out = []
    for line in text.splitlines():
        stamps = _LRC.findall(line)
        if not stamps:
            continue
        lyric = _LRC.sub("", line).strip()
        for m, sec in stamps:
            out.append((int(m) * 60 + float(sec), lyric))
    out.sort(key=lambda x: x[0])
    return out


def rr_points(x1, y1, x2, y2, r):
    """Köşeleri yuvarlak dikdörtgen için smooth=True ile çizilecek nokta listesi."""
    r = max(1, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    return [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r,
            x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
            x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1]


def rr_poly(x1, y1, x2, y2, r, seg=10):
    """Köşeleri tam yay olan dikdörtgenin nokta listesi (smooth kullanmadan: kusursuz köşe)."""
    r = max(1, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    pts = []
    for cx_, cy_, a0 in ((x2 - r, y1 + r, -90), (x2 - r, y2 - r, 0), (x1 + r, y2 - r, 90), (x1 + r, y1 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts += [cx_ + r * math.cos(a), cy_ + r * math.sin(a)]
    return pts


def fit_lines(text, fam, px, width, max_lines=2, weight="bold"):
    """Metni verilen genişlikte en fazla max_lines satıra sığdırır; sığmazsa sona … koyar."""
    try:
        f = tkfont.Font(family=fam, size=-px, weight=weight)
    except Exception:
        return text[:60]
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if f.measure(t) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        last = lines[max_lines - 1]
        while last and f.measure(last + "…") > width:
            last = last[:-1]
        lines = lines[:max_lines - 1] + [last.rstrip() + "…"]
    return "\n".join(lines)


WEBUI_HTML = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gardaş FM</title>
<style>
@property --a{syntax:'<color>';inherits:true;initial-value:#ff4f8b}
@property --b{syntax:'<color>';inherits:true;initial-value:#4db8ff}
:root{--a:#ff4f8b;--b:#4db8ff;--bg:#0a0720;--text:#f3f0ff;--soft:#b9b3e0;--muted:#8a85b5;transition:--a 1s ease,--b 1s ease;color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%}
body{background:var(--bg);color:var(--text);font-family:"Segoe UI",system-ui,Roboto,Arial,sans-serif;overflow:hidden}
.amb{position:fixed;inset:-25%;z-index:0;background-size:cover;background-position:center;filter:blur(80px) saturate(1.5) brightness(.75);transform:scale(1.15);transition:opacity 1.5s ease;opacity:0}
.noise{position:fixed;inset:0;z-index:1;background:radial-gradient(circle at 50% 40%,transparent 30%,rgba(5,3,15,.7));pointer-events:none}
.app{position:relative;z-index:2;display:grid;grid-template-columns:240px 1fr 350px;grid-template-rows:1fr 92px;gap:14px;height:100%;padding:14px}
.glass{position:relative;border-radius:24px;background:rgba(20,14,48,.55);backdrop-filter:blur(22px) saturate(1.4);box-shadow:0 18px 50px rgba(0,0,0,.35)}
.glass::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:1.5px;background:linear-gradient(160deg,var(--a),var(--b));-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:.75;pointer-events:none}
.rail{padding:20px 12px 12px;display:flex;flex-direction:column;min-height:0;animation:pop .8s cubic-bezier(.2,.9,.2,1) both}
.brand{font-weight:900;letter-spacing:.08em;font-size:1.3rem;background:linear-gradient(90deg,var(--a),var(--b));-webkit-background-clip:text;background-clip:text;color:transparent;margin:0 8px 2px}
.hello{font-size:.8rem;color:var(--muted);margin:0 8px 14px}
.nav{flex:1;overflow:auto;scrollbar-width:thin;min-height:0}
.nav button,.foot button{position:relative;display:flex;justify-content:space-between;width:100%;height:40px;margin-bottom:3px;text-align:left;padding:0 14px;align-items:center;border:1.5px solid transparent;background:none;color:var(--soft);font-family:inherit;font-size:.93rem;font-weight:600;border-radius:13px;cursor:pointer;transition:color .3s,transform .3s,background .3s,border-color .3s}
.nav button small{color:var(--muted);font-weight:400}
.nav button:hover,.foot button:hover{color:#fff;transform:translateX(4px)}
.nav button.on{color:#fff;border-color:var(--a);background:color-mix(in srgb,var(--a) 18%,transparent);box-shadow:0 0 20px color-mix(in srgb,var(--a) 40%,transparent)}
.foot{border-top:1px solid rgba(255,255,255,.1);padding-top:8px;margin-top:6px}.foot button{height:34px;font-size:.85rem}
.main{padding:22px 24px;display:flex;flex-direction:column;min-width:0;animation:pop .8s .1s cubic-bezier(.2,.9,.2,1) both}
.head{display:flex;align-items:center;gap:18px;margin-bottom:16px}.head h1{font-size:2rem;font-weight:900;white-space:nowrap}
.head input{margin-left:auto;width:100%;max-width:360px;height:42px;border-radius:21px;border:1.5px solid rgba(255,255,255,.14);background:rgba(255,255,255,.06);color:#fff;padding:0 18px;font:inherit;outline:none;transition:.3s}
.head input:focus{border-color:var(--b);box-shadow:0 0 0 4px color-mix(in srgb,var(--b) 22%,transparent)}
.views{flex:1;overflow:auto;scrollbar-width:thin;scrollbar-color:var(--b) transparent}
.view-anim{animation:viewIn .6s cubic-bezier(.2,.9,.2,1) both}
@keyframes viewIn{from{opacity:0;transform:translateY(22px) scale(.985);filter:blur(5px)}to{opacity:1;transform:none;filter:none}}
.row{display:grid;grid-template-columns:30px 1fr 150px 50px 32px 32px 32px 32px;align-items:center;gap:8px;padding:9px 12px;border-radius:14px;cursor:pointer;color:var(--soft);transition:background .3s,transform .3s;animation:rowIn .55s calc(var(--i)*35ms) cubic-bezier(.2,.9,.2,1) both}
.row:hover{background:rgba(255,255,255,.07);transform:translateX(6px);color:#fff}
.row.cur{background:linear-gradient(90deg,color-mix(in srgb,var(--a) 32%,transparent),transparent);color:#fff;font-weight:600;box-shadow:inset 3px 0 var(--a)}
.row .n{color:var(--muted);font-size:.85rem}.row div:nth-child(2),.row div:nth-child(3){white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.row div:nth-child(3){font-size:.88rem}
.ib{border:0;background:none;color:var(--muted);font-size:1.05rem;cursor:pointer;border-radius:10px;height:30px;transition:transform .25s cubic-bezier(.34,1.56,.64,1),color .2s}
.ib:hover{transform:scale(1.25);color:#fff}.ib.fav{color:var(--a);text-shadow:0 0 12px var(--a)}
@keyframes rowIn{from{opacity:0;transform:translateX(-24px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:translateY(30px) scale(.97)}to{opacity:1;transform:none}}
.empty{color:var(--muted);padding:40px;text-align:center}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px}
.card{position:relative;height:120px;border-radius:20px;padding:16px;cursor:pointer;overflow:hidden;transition:transform .35s cubic-bezier(.34,1.56,.64,1),box-shadow .35s;animation:rowIn .6s calc(var(--i)*70ms) cubic-bezier(.2,.9,.2,1) both;color:#fff}
.card:hover{transform:translateY(-6px) scale(1.03);box-shadow:0 18px 40px rgba(0,0,0,.45)}.card b{display:block;font-size:1.08rem}.card span{font-size:.82rem;opacity:.9}
.sec{margin:20px 4px 10px;font-size:.75rem;letter-spacing:.14em;color:var(--muted)}
.np{padding:22px;display:flex;flex-direction:column;align-items:center;min-height:0;animation:pop .8s .2s cubic-bezier(.2,.9,.2,1) both}
.stagebox{position:relative;width:200px;height:200px;margin:8px 0 16px;flex:0 0 auto}
#viz{position:absolute;inset:-60px;width:320px;height:320px;pointer-events:none}
.cover{position:absolute;inset:0;border-radius:26px;display:grid;place-items:center;font-size:4rem;overflow:hidden;background:linear-gradient(135deg,var(--a),var(--b));transition:transform .15s ease-out;box-shadow:0 20px 60px color-mix(in srgb,var(--a) 50%,transparent)}
.cover img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .8s}.cover img.on{opacity:1}
.ntitle{display:flex;align-items:center;gap:8px;max-width:100%}.np h2{font-size:1.15rem;text-align:center;max-height:3.2em;overflow:hidden}.np .art{color:var(--b);font-size:.95rem;margin:2px 0 8px}
.lyr{flex:1;min-height:0;width:100%;overflow:hidden;position:relative;mask-image:linear-gradient(transparent,#000 22%,#000 78%,transparent);-webkit-mask-image:linear-gradient(transparent,#000 22%,#000 78%,transparent)}
.lyr-in{transition:transform .7s cubic-bezier(.2,.9,.2,1)}
.lyr-in div{padding:7px 4px;text-align:center;font-size:.98rem;color:var(--muted);filter:blur(1px);transition:all .5s cubic-bezier(.2,.9,.2,1)}
.lyr-in div.on{color:var(--b);font-weight:800;font-size:1.22rem;filter:none;text-shadow:0 0 18px color-mix(in srgb,var(--b) 60%,transparent)}
.lyr-in.plain div{filter:none;color:var(--soft)}
.player{grid-column:1/-1;display:flex;align-items:center;gap:22px;padding:0 28px;animation:pop .8s .3s cubic-bezier(.2,.9,.2,1) both}
.pinfo{width:230px;min-width:0}.pinfo b{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pinfo span{font-size:.82rem;color:var(--muted)}
.ctl{display:flex;align-items:center;gap:12px}
.ctl button{width:44px;height:44px;border-radius:14px;border:1.5px solid color-mix(in srgb,var(--b) 70%,transparent);background:rgba(255,255,255,.05);color:#fff;font-size:1rem;cursor:pointer;transition:transform .25s cubic-bezier(.34,1.56,.64,1),background .25s}
.ctl button:hover{transform:scale(1.12);background:rgba(255,255,255,.12)}.ctl button:active{transform:scale(.92)}
.ctl .pp{width:58px;height:58px;border-radius:50%;border:0;background:var(--a);font-size:1.25rem;box-shadow:0 0 26px color-mix(in srgb,var(--a) 70%,transparent)}
.prog{flex:1;display:flex;align-items:center;gap:12px;font-size:.82rem;color:var(--soft)}
.track{position:relative;flex:1;height:6px;border-radius:9px;background:rgba(255,255,255,.14);cursor:pointer}
.track i{position:absolute;left:0;top:0;bottom:0;border-radius:9px;background:linear-gradient(90deg,var(--a),var(--b))}
.track u{position:absolute;top:50%;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;background:#fff;box-shadow:0 0 14px var(--b);transition:transform .2s}.track:hover u{transform:scale(1.35)}
input[type=range]{accent-color:var(--b);width:100px}
.toast{position:fixed;left:50%;bottom:122px;z-index:60;padding:12px 22px;border-radius:999px;background:rgba(20,14,48,.92);border:1.5px solid var(--a);transform:translate(-50%,30px);opacity:0;transition:.45s cubic-bezier(.34,1.56,.64,1)}
.toast.show{opacity:1;transform:translate(-50%,0)}
.lost{position:fixed;inset:0;z-index:99;display:none;place-items:center;background:rgba(5,3,15,.88);text-align:center;color:var(--soft);line-height:1.8}
@media(max-width:1100px){.app{grid-template-columns:210px 1fr}.np{display:none}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
.tools{display:flex;gap:10px;margin:0 4px 12px;flex-wrap:wrap}
.tb{height:36px;padding:0 16px;border-radius:18px;border:1.5px solid color-mix(in srgb,var(--b) 60%,transparent);background:rgba(255,255,255,.05);color:#fff;font-family:inherit;font-size:.85rem;font-weight:600;cursor:pointer;transition:.25s}
.tb:hover{background:rgba(255,255,255,.14);transform:translateY(-2px)}
.nav .grp{font-size:.7rem;letter-spacing:.14em;color:var(--muted);margin:14px 10px 6px;cursor:pointer;user-select:none}
.nav .grp.col::after{content:" ▸"}.nav .grp.opn::after{content:" ▾"}
.pm{position:fixed;z-index:70;min-width:190px;max-height:320px;overflow:auto;border-radius:16px;background:rgba(18,12,44,.97);border:1px solid rgba(255,255,255,.14);padding:6px;display:none;box-shadow:0 16px 40px rgba(0,0,0,.5)}
.pm div{padding:9px 14px;border-radius:10px;font-size:.9rem;color:var(--soft);cursor:pointer}.pm div:hover{background:rgba(255,255,255,.1);color:#fff}
#fs{position:fixed;inset:0;z-index:80;display:none;background:rgba(6,4,18,.94);backdrop-filter:blur(30px);overflow:hidden}
#fs.on{display:block;animation:viewIn .5s both}
#fs .fl{position:absolute;inset:70px 8% 60px 8%;overflow:hidden;mask-image:linear-gradient(transparent,#000 25%,#000 75%,transparent);-webkit-mask-image:linear-gradient(transparent,#000 25%,#000 75%,transparent)}
#fs .lyr-in div{font-size:2rem;padding:14px 0;color:var(--muted);filter:blur(2px);text-align:center;transition:all .5s cubic-bezier(.2,.9,.2,1)}
#fs .lyr-in div.on{font-size:3.2rem;font-weight:900;color:var(--b);filter:none;text-shadow:0 0 30px color-mix(in srgb,var(--b) 60%,transparent)}
#fs .ft{position:absolute;top:22px;left:0;right:0;text-align:center;color:var(--soft)}#fs .x{position:absolute;top:14px;right:22px}
</style></head><body>
<div class="amb" id="amb1"></div><div class="amb" id="amb2"></div><div class="noise"></div>
<div class="app">
 <aside class="glass rail"><div class="brand">GARDAŞ FM</div><div class="hello" id="hello"></div><div class="nav" id="nav"></div>
  <div class="foot"><button id="bset">⚙&nbsp; Ayarlar</button><button id="bcls">▭&nbsp; Klasik arayüz</button><button id="bq">⏻&nbsp; Çıkış</button></div></aside>
 <main class="glass main"><div class="head"><h1 id="title">Ana sayfa</h1><input id="q" placeholder="Şarkı ya da sanatçı ara, Enter'a bas..." autocomplete="off"></div>
  <div class="views" id="views"></div></main>
 <aside class="glass np"><div class="stagebox"><canvas id="viz" width="640" height="640"></canvas><div class="cover" id="cover"><span id="ph">🎧</span><img id="cimg" alt=""></div></div>
  <div class="ntitle"><h2 id="ntitle">Bir şarkı seç</h2><button class="ib" id="nfav" title="Favorilere ekle / çıkar">♥</button><button class="ib" id="nfs" title="Tam ekran sözler (L)">⛶</button></div><div class="art" id="nart"></div><div class="lyr"><div class="lyr-in" id="lyr"></div></div></aside>
 <footer class="glass player"><div class="pinfo"><b id="ptitle">—</b><span id="part"></span></div>
  <div class="ctl"><button id="prev">⏮</button><button class="pp" id="pp">▶</button><button id="next">⏭</button></div>
  <div class="prog"><span id="tcur">0:00</span><div class="track" id="track"><i id="fill"></i><u id="knob"></u></div><span id="ttot">0:00</span></div>
  <input type="range" id="vol" min="0" max="100" value="70" title="Ses"></footer>
</div>
<div id="fs"><div class="ft" id="fst"></div><button class="ib x" id="fsx" style="font-size:1.6rem">✕</button><div class="fl"><div class="lyr-in" id="lyr2"></div></div></div>
<div class="pm" id="pm"></div>
<div class="toast" id="toast"></div>
<div class="lost" id="lost"><div><h2>Bağlantı koptu</h2>Gardaş FM çalışıyor mu? Uygulamada F2'ye basıp<br>yeni arayüzü yeniden aç.</div></div>
<script>
var T=new URLSearchParams(location.search).get("t"),st=null,t0=performance.now(),lastKey="",lastCid=-1,lastLs=-1,amb=1,fails=0,curList="__ana",volDrag=0,lyrOn=-2,searchGen=0;
function $(i){return document.getElementById(i)}
function api(p){return fetch(p+(p.indexOf("?")>-1?"&":"?")+"t="+T).then(function(r){return r.json().catch(function(){return {}}).then(function(j){if(!r.ok)throw j;return j})})}
function cmd(o){return fetch("/api/cmd?t="+T,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)})}
function fmt(s){s=Math.max(0,Math.floor(s||0));return Math.floor(s/60)+":"+("0"+s%60).slice(-2)}
function rgb(c){return "rgb("+c[0]+","+c[1]+","+c[2]+")"}
function esc(x){return String(x==null?"":x).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function toast(t){var e=$("toast");e.textContent=t;e.classList.add("show");clearTimeout(toast.h);toast.h=setTimeout(function(){e.classList.remove("show")},1800)}
var grads=["#ff4f8b,#7a3cff","#4db8ff,#2ec4b6","#ffb020,#ff4f8b","#7ee0ff,#5b8cff","#3ddc97,#4db8ff","#ff7a45,#ffd23f","#a78bfa,#f9a8d4","#00e5ff,#ff4fd8"];
function setNav(n){document.querySelectorAll("#nav button").forEach(function(b){b.classList.toggle("on",b.dataset.n===n)})}
function loadNav(){api("/api/lists").then(function(ls){
  $("nav").innerHTML='<button data-n="__ana">⌂&nbsp; Ana sayfa</button>'+ls.map(function(l){return '<button data-n="'+esc(l.n)+'" data-l="'+esc(l.label)+'">'+esc(l.label)+'<small>'+l.c+'</small></button>'}).join("");
  document.querySelectorAll("#nav button").forEach(function(b){b.onclick=function(){if(b.dataset.n==="__ana")showHome();else showList(b.dataset.n,b.dataset.l)}});setNav(curList)})}
function showHome(){curList="__ana";$("title").textContent="Ana sayfa";setNav("__ana");
  api("/api/home").then(function(cs){var h='<div class="sec">HIZLI BAŞLA</div><div class="cards view-anim">'+cs.map(function(c,i){return '<div class="card" style="--i:'+i+';background:linear-gradient(135deg,'+grads[i%grads.length]+')" data-id="'+esc(c.id)+'"><b>'+esc(c.t)+'</b><span>'+esc(c.s)+'</span></div>'}).join("")+'</div><div class="sec">LİSTELERİN</div><div class="cards view-anim" id="lcards"></div>';
    $("views").innerHTML=h;document.querySelectorAll("#views .card[data-id]").forEach(function(c){c.onclick=function(){cmd({cmd:"home",id:c.dataset.id});toast("Hazırlanıyor...")}});
    api("/api/lists").then(function(ls){$("lcards").innerHTML=ls.filter(function(l){return l.c>0}).slice(0,12).map(function(l,i){return '<div class="card" style="--i:'+i+';background:linear-gradient(135deg,'+grads[(i+3)%grads.length]+')" data-n="'+esc(l.n)+'" data-l="'+esc(l.label)+'"><b>'+esc(l.label)+'</b><span>'+l.c+' şarkı</span></div>'}).join("");
      document.querySelectorAll("#lcards .card").forEach(function(c){c.onclick=function(){showList(c.dataset.n,c.dataset.l)}})})})}
function rowsHtml(rows,n){return rows.length?rows.map(function(r,i){return '<div class="row" style="--i:'+Math.min(i,24)+'" data-i="'+i+'" data-s="'+esc((r.t+" "+r.a).toLowerCase())+'" data-t="'+esc(r.t)+'" data-a="'+esc(r.a)+'"><div class="n">'+(i+1)+'</div><div>'+esc(r.t)+'</div><div>'+esc(r.a)+'</div><div>'+(r.d?fmt(r.d):"")+'</div><button class="ib fav'+(r.f?"":"")+'" data-f="'+(r.f?1:0)+'" title="Favori">'+(r.f?"♥":"♡")+'</button><button class="ib" data-q="1" title="Sıraya ekle">＋</button></div>'}).join(""):'<div class="empty">Burada şarkı yok.</div>'}
function bindRows(n){document.querySelectorAll(".row").forEach(function(r){r.onclick=function(e){
    var b=e.target.closest("button");if(b&&b.dataset.q){cmd({cmd:"enqueue",n:n,i:+r.dataset.i});toast("Sıraya eklendi");return}
    if(b&&b.dataset.f!==undefined){cmd({cmd:"fav_row",n:n,i:+r.dataset.i});var on=b.dataset.f==="1";b.dataset.f=on?0:1;b.textContent=on?"♡":"♥";b.classList.toggle("fav",!on);toast(on?"Favorilerden çıkarıldı":"Favorilere eklendi");return}
    cmd({cmd:"play_list",n:n,i:+r.dataset.i})}});
  document.querySelectorAll(".row .ib[data-f]").forEach(function(b){b.classList.toggle("fav",b.dataset.f==="1")});markCur()}
function showList(n,label){curList=n;$("title").textContent=label;$("q").value="";setNav(n);
  api("/api/list?n="+encodeURIComponent(n)).then(function(rows){$("views").innerHTML='<div class="view-anim">'+rowsHtml(rows,n)+'</div>';bindRows(n)})}
function doSearch(q){q=q.trim();if(q.length<2)return;curList="__ara";$("title").textContent="Arama: "+q;setNav("");var g=++searchGen;$("views").innerHTML='<div class="empty">Aranıyor...</div>';
  api("/api/search?q="+encodeURIComponent(q)).then(function(rows){if(g!==searchGen)return;$("views").innerHTML='<div class="view-anim">'+rowsHtml(rows,"__ara")+'</div>';bindRows("__ara")}).catch(function(){$("views").innerHTML='<div class="empty">Arama yapılamadı.</div>'})}
function markCur(){if(!st)return;document.querySelectorAll(".row").forEach(function(r){r.classList.toggle("cur",r.dataset.t===st.title&&r.dataset.a===st.artist)})}
$("q").onkeydown=function(e){if(e.key==="Enter")doSearch(this.value)};
$("q").oninput=function(){if(curList==="__ana"||curList==="__ara")return;var v=this.value.toLowerCase();document.querySelectorAll(".row").forEach(function(r){r.style.display=r.dataset.s.indexOf(v)>-1?"":"none"})};
function renderLyrics(s){var el=$("lyr");el.innerHTML=(s.lyrics||[]).map(function(x,k){return '<div id="l'+k+'">'+esc(x)+'</div>'}).join("");el.classList.toggle("plain",!s.times);el.style.transform="";lyrOn=-2}
function songChanged(s){$("ntitle").textContent=s.title||"Bir şarkı seç";$("nart").textContent=s.artist;$("ptitle").textContent=s.title||"—";$("part").textContent=s.artist;
  if(s.title)toast("Çalıyor: "+s.title);markCur();$("hello").textContent="Merhaba, "+(s.user||"")}
function coverChanged(s){var img=$("cimg");
  if(s.cid){var u="/api/cover?t="+T+"&v="+s.cid;img.onload=function(){img.classList.add("on");$("ph").style.display="none"};img.src=u;
    var inn=amb?$("amb1"):$("amb2"),out=amb?$("amb2"):$("amb1");inn.style.backgroundImage="url("+u+")";inn.style.opacity=1;out.style.opacity=0;amb=amb?0:1}
  else{img.classList.remove("on");$("ph").style.display=""}}
function poll(){api("/api/state").then(function(s){fails=0;$("lost").style.display="none";st=s;t0=performance.now();
  if(s.key!==lastKey){lastKey=s.key;songChanged(s)}
  if(s.cid!==lastCid){lastCid=s.cid;coverChanged(s)}
  if(s.lsig!==lastLs){lastLs=s.lsig;renderLyrics(s)}
  document.documentElement.style.setProperty("--a",rgb(s.colors[0]));document.documentElement.style.setProperty("--b",rgb(s.colors[1]));
  $("pp").textContent=s.playing?"❚❚":"▶";$("ttot").textContent=fmt(s.dur);$("nfav").classList.toggle("fav",!!s.fav);$("nfav").textContent=s.fav?"♥":"♡";
  if(!volDrag&&+$("vol").value!==s.vol)$("vol").value=s.vol;markCur()
 }).catch(function(e){if(e&&e.err){$("lost").innerHTML="<div><h2>Hata</h2>"+esc(e.err)+"<br><small>Bu yazının ekran görüntüsünü gönder.</small></div>";$("lost").style.display="grid"}else if(++fails>=3)$("lost").style.display="grid"})}
$("pp").onclick=function(){cmd({cmd:"toggle"})};$("next").onclick=function(){cmd({cmd:"next"})};$("prev").onclick=function(){cmd({cmd:"prev"})};
$("nfav").onclick=function(){if(st&&st.title){cmd({cmd:"fav_now"});toast(st.fav?"Favorilerden çıkarıldı":"Favorilere eklendi")}};
$("bset").onclick=function(){cmd({cmd:"settings"})};$("bcls").onclick=function(){cmd({cmd:"classic"})};$("bq").onclick=function(){if(confirm("Gardaş FM kapatılsın mı?"))cmd({cmd:"quit"})};
$("track").onclick=function(e){var r=this.getBoundingClientRect();cmd({cmd:"seek",f:(e.clientX-r.left)/r.width})};
$("vol").oninput=function(){volDrag=1;clearTimeout($("vol").h);cmd({cmd:"vol",v:+this.value});$("vol").h=setTimeout(function(){volDrag=0},1500)};
document.addEventListener("keydown",function(e){if(e.code==="Space"&&document.activeElement.tagName!=="INPUT"){e.preventDefault();cmd({cmd:"toggle"})}});
document.querySelector(".np").addEventListener("mousemove",function(e){var r=$("cover").getBoundingClientRect(),x=(e.clientX-r.left-r.width/2)/r.width,y=(e.clientY-r.top-r.height/2)/r.height;
  $("cover").style.transform="perspective(700px) rotateY("+(x*22)+"deg) rotateX("+(-y*22)+"deg) scale(1.04)"});
document.querySelector(".np").addEventListener("mouseleave",function(){$("cover").style.transform=""});
var cv=$("viz"),cx=cv.getContext("2d"),bars=64,lv=[],last=performance.now(),smooth=0;for(var i=0;i<bars;i++)lv.push(0);
function frame(now){var dt=Math.min(.1,(now-last)/1000);last=now;
  if(st){var pos=st.pos+(st.playing?(now-t0)/1000:0);if(st.dur)pos=Math.min(pos,st.dur);var p=st.dur?pos/st.dur:0;
   $("fill").style.width=(p*100)+"%";$("knob").style.left=(p*100)+"%";$("tcur").textContent=fmt(pos);
   if(st.times&&st.times.length){var k=-1;for(var j=0;j<st.times.length;j++){if(st.times[j]<=pos+.15+(st.off||0))k=j;else break}
     if(k!==lyrOn){lyrOn=k;fsActive(k);document.querySelectorAll("#lyr div").forEach(function(d){d.classList.remove("on")});var el=$("l"+k);
       if(el){el.classList.add("on");var box=document.querySelector(".lyr");$("lyr").style.transform="translateY("+(box.clientHeight/2-el.offsetTop-el.clientHeight/2)+"px)"}}}}
  cx.clearRect(0,0,640,640);var R=224,t=now/1000,pl=st&&st.playing;smooth+=((pl?1:.1)-smooth)*Math.min(1,dt*4);
  var ca=getComputedStyle(document.documentElement);var A=ca.getPropertyValue("--a"),B=ca.getPropertyValue("--b");
  for(var i=0;i<bars;i++){var target=(Math.sin(t*3+i*.5)*.5+.5)*(Math.sin(t*1.3+i*.2)*.4+.6)*smooth;lv[i]+=(target-lv[i])*Math.min(1,dt*12);
    var a=i/bars*Math.PI*2-Math.PI/2,h=12+lv[i]*70,x1=320+Math.cos(a)*R*.7,y1=320+Math.sin(a)*R*.7,x2=320+Math.cos(a)*(R*.7+h),y2=320+Math.sin(a)*(R*.7+h);
    var g=cx.createLinearGradient(x1,y1,x2,y2);g.addColorStop(0,A);g.addColorStop(1,B);cx.strokeStyle=g;cx.lineWidth=6;cx.lineCap="round";cx.beginPath();cx.moveTo(x1,y1);cx.lineTo(x2,y2);cx.stroke()}
  requestAnimationFrame(frame)}
var navLists=[],collapsed={cat:1};
function loadNav(){api("/api/lists").then(function(ls){navLists=ls;var g={lib:[],pl:[],cat:[]};ls.forEach(function(l){(l.g==0?g.lib:l.g==1?g.pl:g.cat).push(l)});
  function btn(l){return '<button data-n="'+esc(l.n)+'" data-l="'+esc(l.label)+'">'+esc(l.label)+'<small>'+l.c+'</small></button>'}
  $("nav").innerHTML='<button data-n="__ana">⌂&nbsp; Ana sayfa</button><div class="grp" style="cursor:default">KÜTÜPHANE</div>'+g.lib.map(btn).join("")+'<div class="grp" style="cursor:default">LİSTELERİM</div>'+g.pl.map(btn).join("")+'<button data-new="1">＋&nbsp; Yeni liste</button><div class="grp '+(collapsed.cat?"col":"opn")+'" id="gcat">KEŞFET</div><div id="catbox" style="display:'+(collapsed.cat?"none":"block")+'">'+g.cat.map(btn).join("")+'</div>';
  $("gcat").onclick=function(){collapsed.cat=collapsed.cat?0:1;$("catbox").style.display=collapsed.cat?"none":"block";this.className="grp "+(collapsed.cat?"col":"opn")};
  document.querySelectorAll("#nav button").forEach(function(b){b.onclick=function(){if(b.dataset.new){newList(null);return}if(b.dataset.n==="__ana")showHome();else showList(b.dataset.n,b.dataset.l)}});setNav(curList)})}
function newList(add){var n=prompt("Yeni liste adı:");if(!n||!n.trim())return;cmd(Object.assign({cmd:"new_list",name:n.trim()},add||{})).then(function(){toast("Liste oluşturuldu");setTimeout(loadNav,700)})}
function rowsHtml(rows,n){return rows.length?rows.map(function(r,i){return '<div class="row" style="--i:'+Math.min(i,24)+'" data-i="'+i+'" data-s="'+esc((r.t+" "+r.a).toLowerCase())+'" data-t="'+esc(r.t)+'" data-a="'+esc(r.a)+'"><div class="n">'+(i+1)+'</div><div>'+esc(r.t)+'</div><div>'+esc(r.a)+'</div><div>'+(r.d?fmt(r.d):"")+'</div><button class="ib fav" data-f="'+(r.f?1:0)+'" title="Favori">'+(r.f?"♥":"♡")+'</button><button class="ib" data-q="1" title="Sıraya ekle">＋</button><button class="ib" data-d="1" title="İndir">⬇</button><button class="ib" data-m="1" title="Listeye ekle">⋯</button></div>'}).join(""):'<div class="empty">Burada şarkı yok.</div>'}
function openPm(e,n,i){var pm=$("pm");var items=[{t:"♥  Favorilerim",k:"Favorilerim"}].concat(navLists.filter(function(l){return l.g==1}).map(function(l){return {t:l.label,k:l.n}}));
  pm.innerHTML=items.map(function(x){return '<div data-k="'+esc(x.k)+'">'+esc(x.t)+'</div>'}).join("")+'<div data-new="1">＋&nbsp; Yeni liste...</div>';
  pm.style.display="block";pm.style.left=Math.min(e.clientX,innerWidth-220)+"px";pm.style.top=Math.min(e.clientY,innerHeight-340)+"px";
  pm.querySelectorAll("div").forEach(function(d){d.onclick=function(ev){ev.stopPropagation();pm.style.display="none";if(d.dataset.new){newList({add_n:n,add_i:i})}else{cmd({cmd:"add_to_list",n:n,i:i,t:d.dataset.k});toast("Listeye eklendi")}}})}
document.addEventListener("click",function(e){if(!e.target.closest(".pm")&&!e.target.closest("[data-m]"))$("pm").style.display="none"});
function bindRows(n){document.querySelectorAll(".row").forEach(function(r){r.onclick=function(e){var b=e.target.closest("button"),i=+r.dataset.i;
    if(b&&b.dataset.q){cmd({cmd:"enqueue",n:n,i:i});toast("Sıraya eklendi");return}
    if(b&&b.dataset.d){cmd({cmd:"dl_row",n:n,i:i});toast("İndirme başladı");return}
    if(b&&b.dataset.m){openPm(e,n,i);return}
    if(b&&b.dataset.f!==undefined){cmd({cmd:"fav_row",n:n,i:i});var on=b.dataset.f==="1";b.dataset.f=on?0:1;b.textContent=on?"♡":"♥";b.classList.toggle("fav",!on);toast(on?"Favorilerden çıkarıldı":"Favorilere eklendi");return}
    cmd({cmd:"play_list",n:n,i:i})}});
  document.querySelectorAll(".row .ib[data-f]").forEach(function(b){b.classList.toggle("fav",b.dataset.f==="1")});markCur()}
function showList(n,label){curList=n;$("title").textContent=label;$("q").value="";setNav(n);
  api("/api/list?n="+encodeURIComponent(n)).then(function(rows){$("views").innerHTML='<div class="tools"><button class="tb" id="tpl">▶ Hepsini çal</button><button class="tb" id="tdl">⬇ Bu listeyi indir</button></div><div class="view-anim">'+rowsHtml(rows,n)+'</div>';
    $("tpl").onclick=function(){cmd({cmd:"play_list",n:n,i:0})};$("tdl").onclick=function(){cmd({cmd:"dl_list",n:n});toast("Liste indiriliyor...")};bindRows(n)})}
function renderLyrics(s){var L=s.lyrics||[],el=$("lyr");el.innerHTML=L.map(function(x,k){return '<div id="l'+k+'">'+esc(x)+'</div>'}).join("");el.classList.toggle("plain",!s.times);el.style.transform="";
  $("lyr2").innerHTML=L.map(function(x,k){return '<div id="m'+k+'">'+esc(x)+'</div>'}).join("");$("lyr2").style.transform="";lyrOn=-2}
function fsActive(k){var e=$("m"+k);document.querySelectorAll("#lyr2 div").forEach(function(d){d.classList.remove("on")});if(!e)return;e.classList.add("on");var box=document.querySelector("#fs .fl");$("lyr2").style.transform="translateY("+(box.clientHeight/2-e.offsetTop-e.clientHeight/2)+"px)"}
function fsToggle(on){var f=$("fs");if(on===undefined)on=!f.classList.contains("on");f.classList.toggle("on",on);
  if(on){$("fst").textContent=st?(st.title+" · "+st.artist):"";if(f.requestFullscreen)f.requestFullscreen().catch(function(){});lyrOn=-2}else if(document.fullscreenElement)document.exitFullscreen().catch(function(){})}
$("nfs").onclick=function(){fsToggle()};$("fsx").onclick=function(){fsToggle(false)};
document.addEventListener("keydown",function(e){if((e.key==="l"||e.key==="L")&&document.activeElement.tagName!=="INPUT")fsToggle();if(e.key==="Escape")fsToggle(false)});
document.addEventListener("fullscreenchange",function(){if(!document.fullscreenElement)$("fs").classList.remove("on")});
(function(){var l=document.createElement("link");l.rel="icon";l.href="/api/logo?t="+T;document.head.appendChild(l)})();loadNav();showHome();poll();setInterval(poll,500);setInterval(loadNav,20000);requestAnimationFrame(frame);
</script></body></html>
"""


_APP = None


class GToplevel(ctk.CTkToplevel):
    """Yan pencerelere (Ayarlar, Ses, Etiketler...) logo simgesini koyar; CTk kendi simgesini ~200 ms sonra koyduğu için biraz bekler."""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.after(320, self._set_logo)

    def _set_logo(self):
        try:
            ph = getattr(_APP, "_icon_photo", None)
            if ph is not None and self.winfo_exists():
                self.iconphoto(False, ph)
        except Exception:
            pass


def _neon_edges(img, boxes):
    """Panel kenarlarına üstte tema rengi, altta ikinci renk (pembe -> mavi) geçişli, parlayan çizgi ekler."""
    W, H = img.size
    edge = Image.new("RGB", (W, H), (0, 0, 0))
    emask = Image.new("L", (W, H), 0)
    c1, c2 = _NEON_DYN or (tuple(ACCENT_RGB), NEON2_RGB)
    for (x1, y1, x2, y2), r in boxes:
        w, h = int(x2 - x1) + 1, int(y2 - y1) + 1
        if w < 12 or h < 12:
            continue
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, outline=255, width=2)
        col = Image.composite(Image.new("RGB", (w, h), c2), Image.new("RGB", (w, h), c1),
                              Image.linear_gradient("L").resize((w, h)))
        try:
            edge.paste(col, (int(x1), int(y1)), m)
            emask.paste(m, (int(x1), int(y1)), m)
        except Exception:
            pass
    gw, gh = max(2, W // 2), max(2, H // 2)
    glow = edge.resize((gw, gh), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    glow = glow.resize((W, H), Image.Resampling.BILINEAR).point(lambda v: min(255, int(v * 1.45)))
    out = ImageChops.add(img, glow)
    out.paste(edge, (0, 0), emask)
    return out


def glass(base, shapes):
    """Fotoğrafın üstüne yarı saydam 'cam' şekiller koyar.
    shapes = [(kutu, köşe_yarıçapı, rgb, saydamlık_0_255, kenar), ...]
    kenar: 0 (yok) | beyaz çizgi saydamlığı (sayı) | (r, g, b, a) | "neon" (parlayan pembe-mavi çizgi)"""
    over = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    neon = []
    for box, r, rgb, alpha, line in shapes:
        if isinstance(line, str):
            d.rounded_rectangle(box, radius=r, fill=tuple(rgb) + (alpha,))
            neon.append((box, r))
            continue
        outline = (line if isinstance(line, tuple) else (255, 255, 255, line)) if line else None
        d.rounded_rectangle(box, radius=r, fill=tuple(rgb) + (alpha,), outline=outline, width=1)
    out = Image.alpha_composite(base.convert("RGBA"), over).convert("RGB")
    return _neon_edges(out, neon) if neon else out


_default_cache = {}


def default_bg(W, H):
    """Fotoğraf seçilmediğinde kullanılan gece moru gradyan arka plan."""
    if (W, H) in _default_cache:
        return _default_cache[(W, H)]
    w, h = max(4, W // 4), max(4, H // 4)
    mask = Image.linear_gradient("L").resize((w, h))
    img = Image.composite(Image.new("RGB", (w, h), (8, 6, 20)), Image.new("RGB", (w, h), (24, 18, 62)), mask)
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(glow)
    tint = tuple(int(c * 0.47) for c in ACCENT_RGB)
    g1 = (120, 28, 86) if ACCENT == "#ff4f8b" else tint
    g2 = (30, 52, 130) if ACCENT == "#ff4f8b" else tuple(int(x) for x in _mix_rgb((30, 52, 130), tint, 0.5))
    d.ellipse((int(w * 0.55), int(-h * 0.25), int(w * 1.15), int(h * 0.5)), fill=g1)
    d.ellipse((int(-w * 0.15), int(h * 0.55), int(w * 0.45), int(h * 1.15)), fill=g2)
    glow = glow.filter(ImageFilter.GaussianBlur(max(2, w // 6)))
    img = ImageChops.add(img, glow).resize((W, H), Image.Resampling.BILINEAR)
    _default_cache.clear()
    _default_cache[(W, H)] = img
    return img


class PhotoCanvas(tk.Canvas):
    """Şeffaf görünümlü tuval. Tk'de gerçek şeffaflık olmadığı için: arkadaki fotoğrafın aynı bölgesini
    kendi görüntüsü yapar, üstüne cam şekiller, yazılar ve tıklanabilir alanlar çizer."""

    def __init__(self, master, app, draw_cb, **kw):
        super().__init__(master, highlightthickness=0, bd=0, bg=BG, **kw)
        self.app, self.draw_cb = app, draw_cb
        self.hits = []             # (x1, y1, x2, y2, işlev)
        self.rhits = []            # sağ tık alanları
        self.wheel_cb = None
        self._photo = None
        self._job = None
        self._hover = None
        self.bind("<Configure>", lambda e: self.schedule())
        self.bind("<Motion>", lambda e: self._set_hover(self._hit_at(e.x, e.y)))
        self.bind("<Leave>", lambda e: self._set_hover(None))
        self.bind("<Button-1>", self._on_click)
        self.bind("<Button-3>", self._on_rclick)
        self.bind("<MouseWheel>", self._on_wheel)
        app.photo_canvases.append(self)

    def schedule(self, delay=60):
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
        self._job = self.after(delay, self.redraw)

    def redraw(self):
        self._job = None
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20 or h < 20:
            return
        if not self.app.bg_ready():          # arka plan henüz hazır değil, biraz sonra tekrar dene
            self.schedule(100)
            return
        self.delete("all")
        self.hits, self.rhits = [], []
        self._hover = None
        base = self.app.bg_crop(self, w, h)
        try:
            self.draw_cb(self, w, h, base)
        except Exception:
            traceback.print_exc()

    def paint(self, base):
        self._photo = ImageTk.PhotoImage(base)
        self.create_image(0, 0, image=self._photo, anchor="nw")

    def add_hit(self, box, cb, rcb=None):
        self.hits.append((box[0], box[1], box[2], box[3], cb))
        if rcb is not None:
            self.rhits.append((box[0], box[1], box[2], box[3], rcb))

    def _hit_at(self, x, y):
        for hit in reversed(self.hits):
            if hit[0] <= x <= hit[2] and hit[1] <= y <= hit[3]:
                return hit
        return None

    def _set_hover(self, hit):
        if hit is self._hover:
            return
        self._hover = hit
        self.delete("hover")
        self.configure(cursor="hand2" if hit else "")
        if hit:
            x1, y1, x2, y2, _ = hit
            self.create_polygon(rr_points(x1, y1, x2, y2, self.app.S(16)), smooth=True, outline=ACCENT,
                                fill="", width=2, tags="hover")

    def _on_click(self, e):
        hit = self._hit_at(e.x, e.y)
        if hit:
            hit[4]()

    def _on_rclick(self, e):
        for x1, y1, x2, y2, cb in reversed(self.rhits):
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                cb(e.x_root, e.y_root)
                return

    def _on_wheel(self, e):
        if self.wheel_cb:
            self.wheel_cb(-1 if e.delta > 0 else 1)


# ============================== ANA UYGULAMA ==============================
EQ_PRESETS = {
    "Düz": [0] * 10,
    "Bas güçlendir": [6, 5, 4, 2, 0, 0, 0, 0, 0, 0],
    "Vokal": [-2, -1, 0, 2, 4, 4, 3, 1, 0, -1],
    "Rock": [5, 3, 1, -1, -2, -1, 1, 3, 4, 5],
    "Parlak": [-2, -1, 0, 0, 0, 1, 3, 5, 6, 6],
    "Gece (kısık)": [3, 2, 1, 0, 0, 0, -1, -2, -3, -3],
}


class GardasFM(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.pick_fonts()
        self.sc = max(1.0, self.winfo_fpixels("1i") / 96.0)      # Windows ekran ölçeği (125%, 150% ...)
        lw = int(min(1360, self.winfo_screenwidth() / self.sc * 0.94))
        lh = int(min(860, self.winfo_screenheight() / self.sc * 0.90))
        self.title("Gardaş FM")
        self.geometry(f"{lw}x{lh}")
        self.minsize(min(1100, lw), min(720, lh))
        self.configure(fg_color=BG)

        self.cfg = self.load_cfg()
        self.ui_q = queue.Queue()                 # thread'lerden arayüze güvenli mesaj kuyruğu
        self.photo_canvases = []
        self.bg_src = None
        self.bg_full = None
        self.bg_photo = None
        self._bg_job = None
        self._last_size = None
        self._set_win = None
        self.bg_label = tk.Label(self, bd=0, highlightthickness=0, bg=BG)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.load_bg_source()

        # --- oynatıcı
        self.vlc_instance = vlc.Instance("--no-video", "--network-caching=800", "--quiet")
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(int(self.cfg["volume"]))
        self.pool = ThreadPoolExecutor(max_workers=3)
        self.tls = threading.local()
        self.futures = {}

        # --- listeler
        self.lists = {c: [make_item(*split_name(s)) for s in songs] for c, songs in CATALOG.items()}
        self.live_cache = load_json(LIVE_FILE, {})
        self._live_busy = set()
        for _n in LIVE_CATS:
            self.lists[_n] = list(self.live_cache.get(_n, {}).get("items", []))
        self.lists[MIX] = self.load_mix()
        self.dl_index = load_json(DL_INDEX_FILE, {})        # indirilenler + klasörden eklenen yerel müzikler
        if not isinstance(self.dl_index, dict):
            self.dl_index = {}
        self.id_cache = load_json(CACHE_FILE, {})           # şarkı -> doğru YouTube video kimliği
        if not isinstance(self.id_cache, dict):
            self.id_cache = {}
        self.cache_lock = threading.Lock()
        self.pl_keys = []
        self.load_playlists()
        self.lists[RECENT] = [make_item(d.get("artist", ""), d.get("title", "?"), d.get("url"), d.get("dur"))
                              for d in self.cfg.get("recent", []) if isinstance(d, dict)]
        self.lists[SEARCH] = []
        self.queue = []
        self.lists[QUEUE] = self.queue
        self.lists[DOWNLOADS] = self.dl_items()
        self.search_local, self.search_online = [], []
        self.search_scope = "all"
        self.search_busy = False
        self.search_done = False
        self.search_gen = 0
        valid = {HOME, MIX, RECENT, DOWNLOADS, QUEUE, *NAV, *self.pl_keys}
        self.cur_view = self.cfg["view"] if self.cfg["view"] in valid else HOME
        self.view_items = []
        self.play_items = []
        self.play_idx = -1
        self.token = 0
        self.shuffle = bool(self.cfg["shuffle"])
        r = self.cfg.get("repeat", 0)
        self.repeat = 2 if r is True else (int(r) if r in (0, 1, 2) else 0)    # 0 kapalı, 1 liste, 2 tek şarkı
        self.failed_streak = 0
        self.sleep_at = None
        self._sleep_min = None
        self.sync, self.sync_idx = [], -1
        self.lyrics_cache = load_json(LYRICS_FILE, {})
        if not isinstance(self.lyrics_cache, dict):
            self.lyrics_cache = {}
        self.history, self.now_item, self._shuf_pick = [], None, None
        self.dl_progress, self.dl_active = {}, set()
        self.dl_pool = ThreadPoolExecutor(max_workers=2)
        self.net_bad = 0
        self.side_scroll = self.home_scroll = 0
        self.side_max = self.home_max = 0
        self.home_t0 = time.time()
        self.pill_y = self.pill_target = self.side_geo = self.np_geo = None
        self.dyn_rgb = self.dyn_target = tuple(ACCENT_RGB)
        self.bars = [0.05] * 28
        self._tray = self._mini = self._audio_win = self._lf = None
        self._playing_iid = None
        self._frame_i = 0
        self._hk_thread = None
        self.rate = float(self.cfg.get("rate", 1.0) or 1.0)
        self._eq = None
        self.cover = None
        self._ph_cache = {}
        self.queued_next = None
        self.prefetch_job = None
        self._toast_job = None
        self._seeking = False

        self.setup_tree_style()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.build_sidebar()
        self.build_hero()
        self.build_home()
        self.build_list()
        self.build_np()
        self.build_bar()

        self.bind("<Configure>", self._on_root_configure)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind_keys()
        self.show_view(self.cur_view)
        self.shuffle_btn.configure(text_color=GOLD if self.shuffle else MUTED)
        self.update_repeat_btn()
        self.apply_audio()
        self.after(50, self._drain_ui)
        self.after(200, self._lyric_tick)
        self.after(200, self.render_bg)
        self.after(500, self.update_progress)
        self.after(40, self._anim)
        self.after(1500, self.net_check)
        self.after(6000, self.maybe_update_ytdlp)
        self.after(9000, self.maybe_update_app)
        self._dc_rpc = None
        self._dc_key = None
        self._dc_last = 0.0
        self._dc_fail = 0.0
        self._dc_warned = False
        self._dc_lock = threading.Lock()
        self.after(3000, self.maybe_show_whats_new)
        self.after(500, self.apply_logo_icon)
        self.view_t0 = 0.0
        self._cover_fade = None
        self._toast_after = None
        self.radio_on, self._radio_busy, self._radio_seen, self._fade_last, self._drag = False, False, set(), None, None
        self._login_busy, self._st_t, self._st_saved, self._st_tok, self._st_cur, self._st_counted, self._vol_base = False, None, time.time(), None, 0.0, None, None
        self.stats = load_json(STATS_FILE, {"total": 0.0, "months": {}})
        self._wu_srv, self._wu_vol = None, 70
        self.after(6500, self.boot_ok)
        self._login_wall = None
        self.after(900, self.require_login)
        self.after(3000, self.recheck_access_silent)
        self.after(2600, self.start_web_mode)
        self.after(8000, self.discord_tick)
        self.start_media_keys()
        self.start_intro()

    # ------------------------------------------------------------ küçük yardımcılar
    def S(self, v):
        """Ekran ölçeğine göre piksel."""
        return int(round(v * self.sc))

    def F(self, family, px, weight="normal"):
        """Tuval yazıları için piksel tabanlı font (negatif boyut = piksel)."""
        return (family, -self.S(px), weight)

    @staticmethod
    def fmt(ms):
        s = max(0, int(ms // 1000))
        return f"{s // 60}:{s % 60:02d}"

    def dur_text(self, it):
        d = it.get("dur")
        return self.fmt(int(d * 1000)) if d else ""

    def ui(self, fn):
        """Arka plan thread'lerinden arayüzü güvenle güncellemek için (tkinter thread-safe değildir)."""
        self.ui_q.put(fn)

    def _drain_ui(self):
        try:
            while True:
                fn = self.ui_q.get_nowait()
                try:
                    fn()
                except Exception:
                    traceback.print_exc()
        except queue.Empty:
            pass
        self.after(50, self._drain_ui)

    def flash(self, text, ms=3500):
        self.toast.configure(text=text)
        if self._toast_job is not None:
            try:
                self.after_cancel(self._toast_job)
            except Exception:
                pass
        self._toast_job = self.after(ms, lambda: self.toast.configure(text=""))

    # ------------------------------------------------------------ ayarlar
    def load_cfg(self):
        cfg = dict(DEFAULT_CFG)
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
        return cfg

    def save_cfg(self):
        try:
            self.cfg.update(volume=int(self.vol.get()), shuffle=self.shuffle, repeat=self.repeat, rate=self.rate,
                            view=self.cur_view if self.cur_view != SEARCH else HOME,
                            recent=[make_item(i["artist"], i["title"], i["url"], i.get("dur"))
                                    for i in self.lists[RECENT][:40]])
            SETTINGS_FILE.write_text(json.dumps(self.cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as ex:
            print("Ayarlar kaydedilemedi:", ex)

    def on_close(self):
        if self.cfg.get("tray") and self.to_tray():
            return
        self.quit_app()

    def quit_app(self):
        self.save_cfg()
        try:
            if self._tray is not None:
                self._tray.stop()
            save_json(STATS_FILE, self.stats)
            if self._dc_rpc is not None:
                t = threading.Thread(target=self.discord_close, daemon=True)
                t.start()
                t.join(1.0)
            self.player.stop()
            self.pool.shutdown(wait=False, cancel_futures=True)   # bekleyen link çözme işleri çıkışı geciktirmesin
            self.dl_pool.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        busy = bool(self.dl_active)
        self.destroy()
        if busy:
            os._exit(0)          # süren indirme çıkışı bekletmesin

    def load_mix(self):
        items = []
        try:
            for d in json.loads(MIX_FILE.read_text(encoding="utf-8")):
                if isinstance(d, dict) and d.get("title"):
                    items.append(make_item(d.get("artist", ""), d["title"], d.get("url"), d.get("dur")))
        except Exception:
            pass
        return items

    def save_mix(self):
        try:
            MIX_FILE.write_text(json.dumps(self.lists[MIX], ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as ex:
            print("Favoriler kaydedilemedi:", ex)

    @staticmethod
    def items_from(seq):
        out = []
        for d in seq or []:
            if isinstance(d, dict) and d.get("title"):
                out.append(make_item(d.get("artist", ""), d["title"], d.get("url"), d.get("dur")))
        return out

    def load_playlists(self):
        data = load_json(PLAYLISTS_FILE, None)
        if not (isinstance(data, dict) and isinstance(data.get("lists"), dict)):
            old = load_json(MIX2_FILE, [])        # eski sürümdeki "Benim mix listem" buraya taşınır
            data = {"order": [MIX2], "lists": {MIX2: old if isinstance(old, list) else []}}
        order = [k for k in data.get("order", []) if k in data["lists"]]
        if MIX2 not in order:
            order.insert(0, MIX2)
        self.pl_keys = order
        for k in order:
            self.lists[k] = self.items_from(data["lists"].get(k, []))

    def save_playlists(self):
        save_json(PLAYLISTS_FILE, {"order": self.pl_keys, "lists": {k: self.lists[k] for k in self.pl_keys}})

    def ask_text(self, title, prompt):
        try:
            return (ctk.CTkInputDialog(text=prompt, title=title).get_input() or "").strip()
        except Exception:
            return ""

    def new_playlist(self, then_add=None):
        name = self.ask_text("Yeni liste", "Çalma listesinin adı:")[:30]
        if not name:
            return None
        key = PL_PREFIX + name
        if key in self.lists or name == MIX2:
            self.flash("Bu adda bir liste zaten var")
            return None
        self.lists[key] = []
        self.pl_keys.append(key)
        self.save_playlists()
        if then_add is not None:
            self.add_to_list(key, then_add)
        self.side_cv.schedule(1)
        self.flash(f"“{name}” listesi oluşturuldu")
        return key

    def rename_playlist(self, key):
        if key == MIX2 or key not in self.pl_keys:
            self.flash("Bu liste yeniden adlandırılamaz")
            return
        name = self.ask_text("Yeniden adlandır", "Yeni ad:")[:30]
        if not name:
            return
        new = PL_PREFIX + name
        if new in self.lists:
            self.flash("Bu adda bir liste zaten var")
            return
        self.lists[new] = self.lists.pop(key)
        self.pl_keys[self.pl_keys.index(key)] = new
        self.save_playlists()
        self.show_view(new if self.cur_view == key else self.cur_view)

    def delete_playlist(self, key):
        if key == MIX2:
            if self.lists[MIX2] and messagebox.askyesno("Gardaş FM", "Mix listesindeki tüm şarkılar silinsin mi?"):
                self.lists[MIX2].clear()
                self.save_playlists()
                self.show_view(self.cur_view)
            return
        if key not in self.pl_keys or not messagebox.askyesno("Gardaş FM", f"“{key[len(PL_PREFIX):]}” listesi silinsin mi?"):
            return
        self.pl_keys.remove(key)
        self.lists.pop(key, None)
        self.save_playlists()
        self.show_view(HOME if self.cur_view == key else self.cur_view)

    def import_playlist(self):
        url = self.ask_text("YouTube playlist", "Playlist linkini yapıştır:")
        if not url:
            return
        if "list=" not in url and "playlist" not in url:
            self.flash("Bu bir playlist linkine benzemiyor", 5000)
            return
        if self.is_offline():
            self.flash("İnternet yok, playlist alınamaz", 5000)
            return
        self.flash("Playlist okunuyor...", 60000)

        def worker():
            items, title = [], "YouTube listesi"
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True,
                                       "skip_download": True, "socket_timeout": 15}) as ydl:
                    info = ydl.extract_info(url, download=False)
                title = (info.get("title") or title)[:30]
                for e in info.get("entries") or []:
                    if e and e.get("id"):
                        items.append(make_item(e.get("channel") or e.get("uploader") or "", e.get("title", "?"),
                                               e.get("url") or f"https://www.youtube.com/watch?v={e['id']}",
                                               e.get("duration")))
            except Exception as ex:
                print("Playlist hatası:", ex)

            def done():
                if not items:
                    self.flash("Playlist okunamadı (özel liste olabilir)", 6000)
                    return
                key = PL_PREFIX + title
                if key in self.lists:
                    key = f"{key} ({len(self.pl_keys)})"
                self.lists[key] = items[:300]
                self.pl_keys.append(key)
                self.save_playlists()
                self.flash(f"{len(items[:300])} şarkı eklendi: {title}", 6000)
                self.show_view(key)
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------ arka plan (fotoğraf)
    def load_bg_source(self):
        self.bg_src = None
        p = self.cfg.get("bg")
        if p and Path(p).exists():
            try:
                im = Image.open(p)
                im.load()
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((2560, 2560))
                self.bg_src = im
            except Exception as ex:
                print("Arka plan fotoğrafı açılamadı:", ex)

    def bg_ready(self):
        return self.bg_full is not None and self.bg_full.size == (self.winfo_width(), self.winfo_height())

    def bg_crop(self, widget, w, h):
        x = widget.winfo_rootx() - self.winfo_rootx()
        y = widget.winfo_rooty() - self.winfo_rooty()
        return self.bg_full.crop((x, y, x + w, y + h))

    def _on_root_configure(self, e):
        size = (self.winfo_width(), self.winfo_height())
        if size == self._last_size:
            return
        self._last_size = size
        self.bg_changed()

    def bg_changed(self, delay=120):
        if self._bg_job is not None:
            try:
                self.after_cancel(self._bg_job)
            except Exception:
                pass
        self._bg_job = self.after(delay, self.render_bg)

    def render_bg(self):
        self._bg_job = None
        W, H = self.winfo_width(), self.winfo_height()
        if W < 300 or H < 300:
            self.bg_changed(200)
            return
        try:
            if self.bg_src is not None:
                img = ImageOps.fit(self.bg_src, (W, H), method=Image.Resampling.BILINEAR)
                blur = float(self.cfg["blur"])
                if blur > 0:   # yarı boyutta bulanıklaştır: çok daha hızlı, görüntü aynı
                    small = img.resize((max(1, W // 2), max(1, H // 2)), Image.Resampling.BILINEAR)
                    small = small.filter(ImageFilter.GaussianBlur(blur / 2))
                    img = small.resize((W, H), Image.Resampling.BILINEAR)
                img = ImageEnhance.Brightness(img).enhance(max(0.05, 1.0 - float(self.cfg["dim"])))
            else:
                img = default_bg(W, H)
        except Exception:
            traceback.print_exc()
            img = default_bg(W, H)
        self.bg_full = img
        self.bg_photo = ImageTk.PhotoImage(img)
        self.bg_label.configure(image=self.bg_photo)
        for cv in self.photo_canvases:
            cv.schedule(10)

    def pick_photo(self):
        parent = self._set_win if (self._set_win is not None and self._set_win.winfo_exists()) else self
        path = filedialog.askopenfilename(parent=parent, title="Arka plan fotoğrafı seç",
                                          filetypes=[("Resimler", "*.jpg *.jpeg *.png *.webp *.bmp"),
                                                     ("Tüm dosyalar", "*.*")])
        if not path:
            return
        try:
            BG_DIR.mkdir(exist_ok=True)
            dest = BG_DIR / Path(path).name        # kopyalıyoruz: orijinal silinse/taşınsa bozulmasın
            if Path(path).resolve() != dest.resolve():
                shutil.copy2(path, dest)
            self.cfg["bg"] = str(dest)
            self.load_bg_source()
            if self.bg_src is None:
                raise ValueError("resim açılamadı")
            self.save_cfg()
            self.bg_changed(10)
            self.flash("Arka plan güncellendi")
        except Exception as ex:
            self.flash(f"Fotoğraf eklenemedi: {ex}", 6000)

    def clear_photo(self):
        self.cfg["bg"] = ""
        self.bg_src = None
        self.save_cfg()
        self.bg_changed(10)

    def open_settings(self):
        if self._set_win is not None and self._set_win.winfo_exists():
            self._set_win.lift()
            return
        win = GToplevel(self)
        self._set_win = win
        win.title("Ayarlar ve görünüm")
        win.geometry("880x660")
        win.minsize(780, 540)
        win.configure(fg_color=PANEL)
        win.transient(self)
        win.after(150, win.lift)
        card_bg = _mix(PANEL, "#ffffff", 0.06)
        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(16, 0))
        tabs = ctk.CTkFrame(body, fg_color=card_bg, corner_radius=20, border_width=1, border_color=NEON2_DIM, width=200)
        tabs.pack(side="left", fill="y", padx=(0, 14))
        tabs.pack_propagate(False)
        ctk.CTkLabel(tabs, text="Ayarlar", font=ctk.CTkFont(HEAD_FONT, 24, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=20, pady=(20, 10))
        stage = ctk.CTkFrame(body, fg_color="transparent")
        stage.pack(side="left", fill="both", expand=True)
        sections, tab_btns, box = {}, {}, None

        def show_tab(name):
            for n_, sc in sections.items():
                sc.pack_forget()
                tab_btns[n_].configure(fg_color="transparent", border_width=0, text_color=SOFT)
            sections[name].pack(fill="both", expand=True)
            tab_btns[name].configure(fg_color=_mix(PANEL, ACCENT, 0.22), border_width=1, border_color=ACCENT,
                                     text_color=TEXT)

        def head(text, tab):
            nonlocal box
            if tab not in sections:
                sections[tab] = ctk.CTkScrollableFrame(stage, fg_color="transparent")
                tab_btns[tab] = ctk.CTkButton(tabs, text=tab, anchor="w", height=42, corner_radius=14,
                                              fg_color="transparent", hover_color="#2a2160", text_color=SOFT,
                                              font=ctk.CTkFont(BODY_FONT, 14, "bold"),
                                              command=lambda t=tab: show_tab(t))
                tab_btns[tab].pack(fill="x", padx=12, pady=3)
                if len(sections) == 1:
                    show_tab(tab)
            box = ctk.CTkFrame(sections[tab], fg_color=card_bg, corner_radius=20, border_width=1,
                               border_color=NEON2_DIM)
            box.pack(fill="x", padx=4, pady=8)
            ctk.CTkLabel(box, text=text, text_color=ACCENT, font=ctk.CTkFont(BODY_FONT, 12, "bold")).pack(
                anchor="w", padx=18, pady=(16, 4))

        def btn(parent, text, cmd, primary=False):
            ctk.CTkButton(parent, text=text, height=36, corner_radius=18, fg_color=ACCENT if primary else BTN,
                          hover_color=ACCENT_HOVER if primary else "#33296b",
                          font=ctk.CTkFont(BODY_FONT, 13, "bold" if primary else "normal"),
                          command=cmd).pack(side="left", padx=(0, 10), pady=2)

        def switch(text, key, extra=None):
            def on():
                self.cfg[key] = bool(sw.get())
                if extra:
                    extra()
            sw = ctk.CTkSwitch(box, text=text, progress_color=ACCENT, text_color=SOFT,
                               font=ctk.CTkFont(BODY_FONT, 12), command=on)
            if self.cfg.get(key):
                sw.select()
            sw.pack(anchor="w", padx=18, pady=6)

        head("PROFİL", "Profil")
        prow = ctk.CTkFrame(box, fg_color="transparent")
        prow.pack(fill="x", padx=18, pady=(2, 8))
        av_lbl = ctk.CTkLabel(prow, text="", width=76, height=76)
        av_lbl.pack(side="left")
        pinfo = ctk.CTkFrame(prow, fg_color="transparent")
        pinfo.pack(side="left", padx=14)
        pname = ctk.CTkLabel(pinfo, text="", font=ctk.CTkFont(HEAD_FONT, 20, "bold"), text_color=TEXT, anchor="w")
        pname.pack(anchor="w")
        pbadge = ctk.CTkLabel(pinfo, text="", font=ctk.CTkFont(BODY_FONT, 13, "bold"), anchor="w")
        pbadge.pack(anchor="w")
        pid = ctk.CTkLabel(pinfo, text="", text_color=MUTED, font=ctk.CTkFont(BODY_FONT, 11), anchor="w")
        pid.pack(anchor="w")
        prow2 = ctk.CTkFrame(box, fg_color="transparent")
        prow2.pack(fill="x", padx=18, pady=(0, 6))

        def refresh_profile():
            try:
                if not win.winfo_exists():
                    return
                im = self.avatar_ctk(72)
                if im is not None:
                    av_lbl.configure(image=im)
                    av_lbl._img = im
                pname.configure(text=self.profile_name())
                txt, col = self.profile_status()
                pbadge.configure(text=txt, text_color=col)
                pid.configure(text=("Discord kimliği: " + str(self.profile().get("id", ""))) if self.profile()
                              else "Discord ile giriş yaparak profilini oluştur")
                login_btn.configure(text="Hesabı yenile" if self.profile() else "Discord ile giriş")
            except Exception:
                traceback.print_exc()

        def copy_id():
            if self.profile():
                self.clipboard_clear()
                self.clipboard_append(str(self.profile().get("id", "")))
                self.flash("Discord kimliğin kopyalandı", 3500)
        login_btn = ctk.CTkButton(prow2, text="Discord ile giriş", height=34, corner_radius=17, fg_color=ACCENT,
                                  hover_color=ACCENT_HOVER, font=ctk.CTkFont(BODY_FONT, 12, "bold"),
                                  command=lambda: self.discord_login(refresh_profile))
        login_btn.pack(side="left", padx=(0, 8))
        btn(prow2, "Çıkış yap", lambda: (self.discord_logout(), win.destroy()))
        btn(prow2, "Kimliğimi kopyala", copy_id)
        ctk.CTkLabel(box, text="Giriş sadece adını ve profil resmini okur, şifre ya da başka bir izin istemez. "
                               "Bilgiler yalnızca bu bilgisayarda saklanır.", text_color=MUTED, wraplength=440,
                     justify="left", font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", padx=18, pady=(2, 14))
        refresh_profile()

        head("DİNLEME İSTATİSTİKLERİM", "Profil")
        sm = self.month_summary()
        st_lines = [f"Toplam dinleme: {self.fmt_hm(self.stats.get('total', 0))}", f"Bu ay: {self.fmt_hm(sm['sec'])}"]
        if sm["artists"]:
            st_lines.append("En çok dinlenen sanatçı: " + sm["artists"][0][0])
        for i_, s_ in enumerate(sm["songs"][:3], 1):
            st_lines.append(f"{i_}. {s_['t'][:42]}  ({s_['n']} kez)")
        for ln_ in st_lines:
            ctk.CTkLabel(box, text=ln_, text_color=TEXT, anchor="w", font=ctk.CTkFont(BODY_FONT, 13)).pack(
                anchor="w", padx=18, pady=1)
        rowst = ctk.CTkFrame(box, fg_color="transparent")
        rowst.pack(fill="x", padx=18, pady=(8, 14))
        btn(rowst, "Aylık özet resmini kaydet", self.make_month_card)

        head("KURUCULAR", "Profil")
        for f_ in FOUNDERS:
            ctk.CTkLabel(box, text="★  " + (f"{f_[0]} ({f_[1]})" if f_[0] != f_[1] else f_[0]), text_color=GOLD,
                         anchor="w", font=ctk.CTkFont(BODY_FONT, 15, "bold")).pack(anchor="w", padx=18, pady=2)
        ctk.CTkLabel(box, text="Kurucu rozeti, Discord kimliği kurucu listesindeki kişiye otomatik verilir. "
                               "Diğer herkes “doğrulanmamış” görünür.", text_color=MUTED, wraplength=440,
                     justify="left", font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", padx=18, pady=(4, 14))

        head("ARKA PLAN", "Görünüm")
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=18)
        btn(row, "Fotoğraf seç...", self.pick_photo, True)
        btn(row, "Fotoğrafı kaldır", self.clear_photo)

        def slider(title, key, lo, hi, steps):
            ctk.CTkLabel(box, text=title, text_color=SOFT, font=ctk.CTkFont(BODY_FONT, 13)).pack(
                anchor="w", padx=18, pady=(12, 2))

            def on_change(v):
                self.cfg[key] = float(v)
                self.bg_changed(150)
            s = ctk.CTkSlider(box, from_=lo, to=hi, number_of_steps=steps, button_color=GOLD,
                              button_hover_color="#ffd98a", progress_color=ACCENT, command=on_change)
            s.set(float(self.cfg[key]))
            s.pack(fill="x", padx=18)
        slider("Karartma (yazılar okunsun diye)", "dim", 0.0, 0.85, 34)
        slider("Bulanıklık", "blur", 0, 20, 20)

        head("RENK TEMASI", "Görünüm")

        def set_theme(v):
            self.cfg["theme"] = v
            self.save_cfg()
            self.flash("Tema bir sonraki açılışta uygulanır", 6000)
        om = ctk.CTkOptionMenu(box, values=list(THEMES), command=set_theme, fg_color=BTN, button_color=ACCENT,
                               button_hover_color=ACCENT_HOVER, font=ctk.CTkFont(BODY_FONT, 13))
        om.set(self.cfg.get("theme", "Gece İstanbul"))
        om.pack(anchor="w", padx=18)

        head("ÇEVRİMDIŞI", "Çevrimdışı")
        ctk.CTkLabel(box, text=f"İndirilenler: {len(self.lists[DOWNLOADS])} şarkı  ·  {self.dl_size_text()}",
                     text_color=SOFT, font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=18, pady=(0, 6))
        switch("Sadece indirilenleri çal (internet yokmuş gibi)", "offline", lambda: (self.side_cv.schedule(1),
                                                                                  self.flash("Çevrimdışı mod " + ("açık" if self.cfg["offline"] else "kapalı"))))
        row2 = ctk.CTkFrame(box, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=(6, 0))
        btn(row2, "Klasörden müzik ekle", self.add_local_folder)
        btn(row2, "İndirilenleri sil", self.clear_downloads)

        head("SİSTEM", "Sistem")
        switch("Açılış animasyonunu göster (bir sonraki açılışta)", "intro")
        switch("Pencereyi kapatınca sistem tepsisine küçül", "tray")
        switch("Açılışta yeni sürüm var mı diye bak (günde bir)", "auto_update")
        row3 = ctk.CTkFrame(box, fg_color="transparent")
        row3.pack(fill="x", padx=18, pady=(6, 0))
        btn(row3, "yt-dlp'yi şimdi güncelle", self.update_ytdlp)
        btn(row3, f"Gardaş FM güncellemesini denetle (v{APP_VERSION})", lambda: self.update_app(silent=False))
        row3b = ctk.CTkFrame(box, fg_color="transparent")
        row3b.pack(fill="x", padx=18, pady=(6, 0))
        btn(row3b, "Masaüstüne kısayol oluştur", self.make_desktop_shortcut)
        row3c = ctk.CTkFrame(box, fg_color="transparent")
        row3c.pack(fill="x", padx=18, pady=(6, 0))
        btn(row3c, "Güncelleme kartı önizlemesi", lambda: (self.save_cfg(), win.destroy(), self.after(250, lambda: self.show_update_card(
            {"version": "9.9", "preview": True,
             "notes": ["Bu bir önizlemedir, hiçbir şey kurulmaz.", "Gerçek güncellemede buraya yenilikler yazılır."]}))))

        head("ANİMASYON VE BİLDİRİM", "Görünüm")
        ctk.CTkLabel(box, text="Animasyon seviyesi (yavaş bilgisayarda Hafif ya da Kapalı seç)", text_color=SOFT,
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=18, pady=(2, 0))

        def set_anim(v):
            self.cfg["anim"] = v
            self.save_cfg()
            self.flash(f"Animasyon: {v}")
        seg = ctk.CTkSegmentedButton(box, values=["Tam", "Hafif", "Kapalı"], command=set_anim, fg_color=BTN,
                                     selected_color=ACCENT, selected_hover_color=ACCENT_HOVER, unselected_color=BTN,
                                     unselected_hover_color="#33296b")
        seg.set(self.cfg.get("anim", "Tam"))
        seg.pack(anchor="w", padx=18, pady=(4, 6))
        switch("Şarkı değişince bildirim göster (uygulama arkadayken)", "notify")
        switch("Yeni arayüz ana arayüz olsun (açılışta kendiliğinden açılır, klasik pencere tepsiye küçülür)", "webui_default")
        switch("Neon kenarlar çalan şarkının kapak renginde olsun", "cover_color",
               extra=lambda: self.apply_cover_neon(self.dyn_target))

        head("SES VE GEÇİŞ", "Sistem")
        ctk.CTkLabel(box, text="Yumuşak geçiş: şarkı bitmeden ses azalır, yeni şarkı yavaşça açılır.", text_color=SOFT,
                     wraplength=440, justify="left", font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=18, pady=(2, 4))
        fade_map = {"Kapalı": 0, "2 sn": 2, "4 sn": 4, "6 sn": 6}

        def set_fade(v):
            self.cfg["fade"] = fade_map[v]
            self.save_cfg()
            self.flash(f"Yumuşak geçiş: {v}")
        segf = ctk.CTkSegmentedButton(box, values=list(fade_map), command=set_fade, fg_color=BTN,
                                      selected_color=ACCENT, selected_hover_color=ACCENT_HOVER, unselected_color=BTN,
                                      unselected_hover_color="#33296b")
        segf.set(next((k for k, v in fade_map.items() if v == int(self.cfg.get("fade", 0) or 0)), "Kapalı"))
        segf.pack(anchor="w", padx=18, pady=(2, 8))
        switch("Şarkı başına ses ayarını hatırla (şarkıdayken sesi değiştirirsen o şarkı sonra o sesle açılır)", "song_vol_on")

        head("ŞARKI BULMA", "Sistem")
        ctk.CTkLabel(box, text="Dinleyerek şarkı bulma için AudD anahtarı (audd.io adresinden ücretsiz hesapla alınır). "
                               "Sözden bulma için anahtar gerekmez.", text_color=SOFT, wraplength=440, justify="left",
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=18, pady=(2, 4))
        rowk = ctk.CTkFrame(box, fg_color="transparent")
        rowk.pack(fill="x", padx=18, pady=(2, 12))
        ent_k = ctk.CTkEntry(rowk, width=250, height=34, show="•", placeholder_text="AudD anahtarı")
        ent_k.pack(side="left", padx=(0, 10))
        if self.cfg.get("audd_token"):
            ent_k.insert(0, self.cfg["audd_token"])

        def save_audd():
            self.cfg["audd_token"] = ent_k.get().strip()
            self.save_cfg()
            self.flash("AudD anahtarı kaydedildi" if self.cfg["audd_token"] else "AudD anahtarı silindi")
        btn(rowk, "Kaydet", save_audd)

        head("YEDEK", "Yedek")
        row4 = ctk.CTkFrame(box, fg_color="transparent")
        row4.pack(fill="x", padx=18, pady=(2, 0))
        btn(row4, "Yedekle...", self.backup_to_zip)
        btn(row4, "Yedekten geri yükle...", self.restore_from_zip)
        ctk.CTkLabel(box, text="Favoriler, çalma listeleri, ayarlar ve kayıtlı sözler tek bir .zip dosyasına yedeklenir.",
                     text_color=MUTED, wraplength=380, justify="left",
                     font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", padx=18, pady=(4, 0))

        head("DISCORD", "Discord")
        switch("Discord durumumda dinlediğim şarkıyı göster", "discord", extra=self.discord_toggled)
        row5 = ctk.CTkFrame(box, fg_color="transparent")
        row5.pack(fill="x", padx=18, pady=(2, 0))
        ent = ctk.CTkEntry(row5, width=230, height=34, placeholder_text="Discord uygulama kimliği")
        ent.pack(side="left", padx=(0, 10))
        if self.cfg.get("discord_id"):
            ent.insert(0, self.cfg["discord_id"])

        def save_dc_id():
            self.cfg["discord_id"] = re.sub(r"\D", "", ent.get())
            self.save_cfg()
            self._dc_key = None
            self._dc_fail = 0.0
            self._dc_warned = False
            self.flash("Discord kimliği kaydedildi" if self.cfg["discord_id"] else "Discord kimliği silindi")
        btn(row5, "Kaydet", save_dc_id)
        ctk.CTkLabel(box, text="Kimlik için: discord.com/developers/applications > New Application (adı: Gardaş FM) "
                               "> General Information > Application ID'yi kopyalayıp buraya yapıştır. Discord uygulaması açık olmalı.",
                     text_color=MUTED, wraplength=380, justify="left",
                     font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", padx=18, pady=(4, 0))
        head("GARDAŞ FM", "Hakkında")
        lg2 = self.logo_ctk(72)
        if lg2 is not None:
            ctk.CTkLabel(box, image=lg2, text="").pack(anchor="w", padx=18, pady=(2, 0))
        ctk.CTkLabel(box, text=f"Gardaş FM  v{APP_VERSION}", font=ctk.CTkFont(HEAD_FONT, 20, "bold"),
                     text_color=GOLD).pack(anchor="w", padx=18, pady=(6, 0))
        ctk.CTkLabel(box, text="YouTube'dan müzik, kendi listelerin, sözler, neon arayüz ve Discord durumu: hepsi tek yerde.",
                     text_color=SOFT, wraplength=440, justify="left",
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=18, pady=(4, 8))
        ctk.CTkLabel(box, text="Kurucular: " + "  ·  ".join(f"{f_[0]} ({f_[1]})" if f_[0] != f_[1] else f_[0] for f_ in FOUNDERS),
                     text_color=GOLD, font=ctk.CTkFont(BODY_FONT, 13, "bold")).pack(anchor="w", padx=18, pady=(0, 8))
        rowa = ctk.CTkFrame(box, fg_color="transparent")
        rowa.pack(fill="x", padx=18, pady=(0, 4))
        btn(rowa, "Neler yeni?", lambda: self.show_whats_new())
        btn(rowa, "Teşhis paketi oluştur", self.make_diag_zip)
        if os.name == "nt":
            btn(rowa, "Veri klasörünü aç", lambda: os.startfile(str(DATA_DIR)))
        ctk.CTkLabel(box, text=f"Veri klasörü: {DATA_DIR}", text_color=MUTED, wraplength=440, justify="left",
                     font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", padx=18, pady=(8, 16))
        ctk.CTkButton(win, text="Kapat", height=36, corner_radius=18, fg_color=BTN, hover_color="#33296b",
                      command=lambda: (self.save_cfg(), win.destroy())).pack(anchor="e", padx=24, pady=12)

    def open_audio(self):
        if self._audio_win is not None and self._audio_win.winfo_exists():
            self._audio_win.lift()
            return
        win = GToplevel(self)
        self._audio_win = win
        win.title("Ses ayarları")
        win.geometry("380x280")
        win.configure(fg_color=PANEL)
        win.transient(self)
        win.after(150, win.lift)
        ctk.CTkLabel(win, text="Ses ayarları", font=ctk.CTkFont(HEAD_FONT, 20, "bold"),
                     text_color=GOLD).pack(anchor="w", padx=24, pady=(22, 10))
        ctk.CTkLabel(win, text="Ekolayzır", text_color=SOFT, font=ctk.CTkFont(BODY_FONT, 13)).pack(anchor="w", padx=24)

        def set_eq(v):
            self.cfg["eq"] = v
            self.apply_audio()
            self.save_cfg()
        om = ctk.CTkOptionMenu(win, values=list(EQ_PRESETS), command=set_eq, fg_color=BTN, button_color=ACCENT,
                               button_hover_color=ACCENT_HOVER, font=ctk.CTkFont(BODY_FONT, 13))
        om.set(self.cfg.get("eq", "Düz"))
        om.pack(anchor="w", padx=24, pady=(4, 18))
        ctk.CTkLabel(win, text="Çalma hızı", text_color=SOFT, font=ctk.CTkFont(BODY_FONT, 13)).pack(anchor="w", padx=24)
        speeds = {"0.75x": 0.75, "1x": 1.0, "1.25x": 1.25, "1.5x": 1.5}

        def set_rate(v):
            self.rate = speeds[v]
            self.cfg["rate"] = self.rate
            self.player.set_rate(self.rate)
            self.save_cfg()
        sb = ctk.CTkSegmentedButton(win, values=list(speeds), command=set_rate, selected_color=ACCENT,
                                    selected_hover_color=ACCENT_HOVER, unselected_color=BTN,
                                    font=ctk.CTkFont(BODY_FONT, 13))
        sb.set(next((k for k, v in speeds.items() if abs(v - self.rate) < 0.01), "1x"))
        sb.pack(anchor="w", padx=24, pady=(4, 12))
        ctk.CTkButton(win, text="Kapat", height=34, corner_radius=17, fg_color=BTN, hover_color="#33296b",
                      command=win.destroy).pack(anchor="e", padx=24, pady=10)

    # ------------------------------------------------------------ arayüz iskeleti
    def setup_tree_style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                     rowheight=36, borderwidth=0, font=(BODY_FONT, 11))
        st.configure("Treeview.Heading", background=PANEL, foreground=MUTED, relief="flat",
                     borderwidth=0, font=(BODY_FONT, 10), padding=(8, 8))
        st.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        st.map("Treeview.Heading", background=[("active", PANEL)])

        def fixed(option):
            return [e for e in st.map("Treeview", query_opt=option) if e[:2] != ("!disabled", "!selected")]
        st.map("Treeview", background=[("selected", _mix(PANEL, ACCENT, 0.36))] + fixed("background"),
               foreground=[("selected", "white")] + fixed("foreground"))

    def build_sidebar(self):
        self.side_cv = PhotoCanvas(self, self, self.draw_sidebar, width=self.S(212), height=10)
        self.side_cv.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(14, 7), pady=(14, 7))
        self.side_cv.wheel_cb = self.side_wheel
        self.side_tab = ctk.CTkButton(self, text="»", width=26, height=68, corner_radius=13, fg_color=PANEL,
                                      hover_color=BTN, border_width=1, border_color=NEON2, text_color=TEXT,
                                      font=ctk.CTkFont(BODY_FONT, 18, "bold"), command=self.toggle_sidebar)
        if not self.cfg.get("side_open", True):
            self.side_cv.grid_remove()
            self.side_tab.place(x=2, y=self.S(120))

    def build_hero(self):
        self.hero_cv = PhotoCanvas(self, self, self.draw_hero, width=10, height=self.S(160))
        self.hero_cv.grid(row=0, column=1, sticky="ew", padx=7, pady=(14, 7))
        self.search_entry = ctk.CTkEntry(self.hero_cv, placeholder_text="Şarkı ya da sanatçı ara...",
                                         fg_color=PANEL, border_width=0, corner_radius=0, text_color=TEXT,
                                         placeholder_text_color=MUTED, bg_color=PANEL, height=40,
                                         font=ctk.CTkFont(BODY_FONT, 14))
        self._sug_frame, self._sug_inner, self._sug_rows, self._sug_idx, self._sug_job = None, None, [], -1, None
        self.search_entry.bind("<Return>", self.on_search_return)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)
        self.search_entry.bind("<Down>", lambda e: self.on_search_nav(1))
        self.search_entry.bind("<Up>", lambda e: self.on_search_nav(-1))
        self.search_entry.bind("<Escape>", lambda e: self.hide_suggestions())
        self.search_entry.bind("<FocusOut>", lambda e: self.after(220, self.hide_suggestions))

    def build_home(self):
        self.home_cv = PhotoCanvas(self, self, self.draw_home, width=10, height=10)
        self.home_cv.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=7, pady=(14, 7))
        self.home_cv.wheel_cb = self.home_wheel

    def build_list(self):
        self.list_cv = PhotoCanvas(self, self, self.draw_list, width=10, height=10)
        self.list_cv.grid(row=1, column=1, sticky="nsew", padx=7, pady=(0, 7))
        li = self.list_inner = ctk.CTkFrame(self.list_cv, fg_color=PANEL, corner_radius=0)
        li.grid_columnconfigure(0, weight=1)
        li.grid_rowconfigure(2, weight=1)
        tools = ctk.CTkFrame(li, fg_color="transparent")
        tools.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 6))

        def tool_btn(text, cmd, primary=False, parent=None):
            ctk.CTkButton(parent or tools, text=text, height=32, corner_radius=16, width=0,
                          fg_color=ACCENT if primary else BTN, hover_color=ACCENT_HOVER if primary else "#33296b",
                          border_width=0 if primary else 1, border_color=NEON2_DIM,
                          font=ctk.CTkFont(BODY_FONT, 12, "bold" if primary else "normal"),
                          command=cmd).pack(side="left", padx=(0, 8))
        tool_btn("▶  Çal", self.play_selected, True)
        tool_btn("Karışık çal", self.play_view_shuffled)
        tool_btn("♥  Favori", self.toggle_fav)
        tool_btn("⬇  İndir", self.download)
        tool_btn("+ Sıraya", self.enqueue)
        tools2 = ctk.CTkFrame(li, fg_color="transparent")
        tools2.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 6))
        tool_btn("Listeye ekle  ▾", self.add_menu, parent=tools2)
        tool_btn("Listeden çıkar", self.remove_selected, parent=tools2)
        tool_btn("Diğer  ▾", self.more_menu, parent=tools2)

        self.tree = ttk.Treeview(li, columns=("no", "title", "artist", "dur", "src"), show="headings",
                                 selectmode="browse")
        self.tree.bind("<ButtonPress-1>", self._drag_press, add="+")
        self.tree.bind("<B1-Motion>", self._drag_motion, add="+")
        self.tree.bind("<ButtonRelease-1>", self._drag_release, add="+")
        for col, text, w, anchor, stretch in (("no", "#", 46, "center", False), ("title", "Şarkı", 220, "w", True),
                                              ("artist", "Sanatçı", 150, "w", True),
                                              ("dur", "Süre", 56, "center", False), ("src", "Kaynak", 92, "w", False)):
            self.tree.heading(col, text=text, anchor="center" if col in ("no", "dur") else "w")
            self.tree.column(col, width=w, anchor=anchor, stretch=stretch, minwidth=40)
        self.tree.tag_configure("alt", background=ROW_ALT)
        self.tree.grid(row=2, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
        sb = ctk.CTkScrollbar(li, command=self.tree.yview, fg_color=PANEL, button_color=NEON2_DIM,
                              button_hover_color=NEON2)
        sb.grid(row=2, column=1, sticky="ns", padx=(4, 8), pady=(0, 10))
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda e: self.play_selected())
        self.tree.bind("<Return>", lambda e: self.play_selected())
        self.tree.bind("<Button-3>", self.on_tree_menu)

    def more_menu(self):
        e = [("⬇  Bu sayfadakilerin hepsini indir", self.download_many),
             ("Tüm sayfayı sıraya ekle", self.enqueue_all),
             None,
             ("+  Yeni çalma listesi", self.new_playlist),
             ("YouTube playlist'ten içe aktar", self.import_playlist),
             ("Klasörden müzik ekle", self.add_local_folder)]
        if self.cur_view in self.pl_keys:
            e += [None, ("Listeyi yeniden adlandır", lambda: self.rename_playlist(self.cur_view)),
                  ("Listeyi sil" if self.cur_view != MIX2 else "Listeyi temizle",
                   lambda: self.delete_playlist(self.cur_view))]
        e += [None, ("Listeyi paylaş (.gfm dosyası)", self.export_gfm),
              ("Listeyi .txt olarak kaydet", lambda: self.export_text("txt")),
              ("Listeyi .m3u olarak kaydet", lambda: self.export_text("m3u")),
              ("Dosyadan liste içe aktar (.gfm)", self.import_gfm)]
        if self.cur_view == MIX or self.cur_view in self.pl_keys:
            e += [("Tekrar edenleri temizle", self.dedupe_current)]
        if self.cur_view == QUEUE:
            e += [None, ("Sırayı temizle", self.clear_queue)]
        self.popup(e, self.winfo_pointerx(), self.winfo_pointery())

    def new_list_menu(self):
        self.popup([("+  Boş çalma listesi", self.new_playlist),
                    ("YouTube playlist'ten içe aktar", self.import_playlist),
                    ("Dosyadan içe aktar (.gfm)", self.import_gfm),
                    ("Klasörden müzik ekle", self.add_local_folder)], self.winfo_pointerx(), self.winfo_pointery())

    def playlist_menu(self, key, x, y):
        self.popup([("▶  Karışık çal", lambda: (self.show_view(key), self.play_view_shuffled())),
                    ("⬇  Hepsini indir", lambda: self.download_many(self.lists[key])),
                    None,
                    ("Yeniden adlandır", lambda: self.rename_playlist(key)),
                    ("Sil" if key != MIX2 else "Temizle", lambda: self.delete_playlist(key))], x, y)

    def build_np(self):
        self.np_cv = PhotoCanvas(self, self, self.draw_np, width=self.S(360), height=10)
        self.np_cv.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(7, 14), pady=(14, 7))
        self.lyrics_inner = ctk.CTkFrame(self.np_cv, fg_color=PANEL, corner_radius=0)
        # tam ekran söz modundaki gibi akan söz görünümü (çalan satır altın/turuncu, diğerleri soluk)
        self.lyr_cv = tk.Canvas(self.lyrics_inner, bg=PANEL, highlightthickness=0)
        self.lyr_cv.pack(fill="both", expand=True, padx=6, pady=6)
        self.lyr_lines, self.lyr_pos, self.lyr_manual, self.lyr_sig = [], 0.0, 0.0, None
        self.lyr_cum, self.lyr_cum_key = [], None
        self.lyr_cv.bind("<MouseWheel>", self._lyr_wheel)
        self.set_lyrics("Şarkı sözleri burada görünecek.")

    def build_bar(self):
        self.bar_cv = PhotoCanvas(self, self, self.draw_bar, width=10, height=self.S(104))
        self.bar_cv.grid(row=2, column=0, columnspan=3, sticky="ew", padx=14, pady=(7, 14))
        bi = self.bar_inner = ctk.CTkFrame(self.bar_cv, fg_color=PANEL, corner_radius=0)
        bi.grid_columnconfigure(1, weight=1)
        left = ctk.CTkFrame(bi, fg_color="transparent", width=360, height=84)
        left.grid(row=0, column=0, sticky="w", padx=(18, 0))
        left.pack_propagate(False)
        self.np_title = ctk.CTkLabel(left, text="Bir şarkı seç", anchor="w", text_color=TEXT, width=350,
                                     font=ctk.CTkFont(BODY_FONT, 15, "bold"))
        self.np_title.pack(anchor="w", pady=(12, 0))
        self.np_sub = ctk.CTkLabel(left, text="Gardaş FM hazır", anchor="w", text_color=GOLD, width=350,
                                   font=ctk.CTkFont(BODY_FONT, 12))
        self.np_sub.pack(anchor="w")
        self.toast = ctk.CTkLabel(left, text="", text_color=SOFT, width=350, anchor="w", justify="left",
                                  wraplength=350, font=ctk.CTkFont(BODY_FONT, 11))
        self.toast.pack(anchor="w")

        mid = ctk.CTkFrame(bi, fg_color="transparent")
        mid.grid(row=0, column=1, sticky="ew", padx=10)
        mid.grid_columnconfigure(0, weight=1)
        ctrl = ctk.CTkFrame(mid, fg_color="transparent")
        ctrl.grid(row=0, column=0, pady=(10, 0))

        def cbtn(text, cmd, size=40, fg=BTN, hover="#33296b", font=18, edge=False):
            b = ctk.CTkButton(ctrl, text=text, width=size + (16 if edge else 0), height=size,
                              corner_radius=14 if edge else size // 2, fg_color=fg,
                              hover_color=hover, text_color=TEXT, font=ctk.CTkFont(BODY_FONT, font), command=cmd,
                              border_width=1 if edge else 0, border_color=NEON2)
            b.pack(side="left", padx=5)
            return b
        self.shuffle_btn = cbtn("Karışık", self.toggle_shuffle, 40, "transparent", BTN, 12)
        self.shuffle_btn.configure(width=70, text_color=MUTED)
        cbtn("⏮", self.prev_song, 42, edge=True)
        self.play_btn = cbtn("▶", self.toggle_play, 48, ACCENT, ACCENT_HOVER, 20)
        cbtn("⏭", lambda: self.next_song(), 42, edge=True)
        self.repeat_btn = cbtn("Tekrar", self.toggle_repeat, 40, "transparent", BTN, 12)
        self.repeat_btn.configure(width=100, text_color=MUTED)

        prog = ctk.CTkFrame(mid, fg_color="transparent")
        prog.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        prog.grid_columnconfigure(1, weight=1)
        self.time_lbl = ctk.CTkLabel(prog, text="0:00", width=44, text_color=MUTED, font=ctk.CTkFont(BODY_FONT, 12))
        self.time_lbl.grid(row=0, column=0)
        self.slider = ctk.CTkSlider(prog, from_=0, to=1, height=14, button_color=NEON2, button_hover_color="#9fdcff",
                                    progress_color=NEON2, fg_color=BTN, command=self.on_seek_drag)
        self.slider.set(0)
        self.slider.grid(row=0, column=1, sticky="ew", padx=6)
        self.slider.bind("<ButtonPress-1>", lambda e: setattr(self, "_seeking", True))
        self.slider.bind("<ButtonRelease-1>", self.on_seek_release)
        self.total_lbl = ctk.CTkLabel(prog, text="0:00", width=44, text_color=MUTED, font=ctk.CTkFont(BODY_FONT, 12))
        self.total_lbl.grid(row=0, column=2)

        rwrap = ctk.CTkFrame(bi, fg_color="transparent", width=360, height=84)
        rwrap.grid(row=0, column=2, sticky="e", padx=(0, 18))
        rwrap.pack_propagate(False)
        right = ctk.CTkFrame(rwrap, fg_color="transparent")
        right.place(relx=1.0, rely=0.5, anchor="e")

        def rbtn(text, cmd, width):
            ctk.CTkButton(right, text=text, width=width, height=32, corner_radius=16, fg_color=BTN,
                          hover_color="#33296b", font=ctk.CTkFont(BODY_FONT, 12), command=cmd,
                          border_width=1, border_color=NEON2_DIM).pack(side="left", padx=(0, 8))
        rbtn("EQ / Hız", self.open_audio, 70)
        rbtn("Mini", self.open_mini, 52)
        self.sleep_btn = ctk.CTkButton(right, text="Uyku: kapalı", width=88, height=32, corner_radius=16,
                                       fg_color=BTN, hover_color="#33296b", font=ctk.CTkFont(BODY_FONT, 12),
                                       command=self.cycle_sleep, border_width=1, border_color=NEON2_DIM)
        self.sleep_btn.pack(side="left", padx=(0, 10))
        self.vol = ctk.CTkSlider(right, from_=0, to=100, width=90, height=14, button_color=NEON2,
                                 progress_color=NEON2, fg_color=BTN, command=self.on_volume)
        self.vol.set(int(self.cfg["volume"]))
        self.vol.pack(side="left", padx=4)

    # ------------------------------------------------------------ çizim (cam paneller)
    def nav_items(self):
        items = [("Ana sayfa", HOME), ("Arama", SEARCH), ("♫  Şarkı bul", "bul"), ("◈  Yeni arayüz (beta)", "yeniui"), None]
        items += [(c, c) for c in NAV]
        items += [("✦  " + c, c) for c in LIVE_CATS]
        items += [None, ("♥  Favorilerim", MIX)]
        items += [(k, k) for k in self.pl_keys]
        tg = self.all_tags()[:8]
        if tg:
            items += [None] + [("#  " + t, "etiket:" + t) for t in tg]
        items += [("＋  Yeni liste / içe aktar", "newlist"), None,
                  ("⬇  İndirilenler", DOWNLOADS), ("Sıradakiler", QUEUE), ("Son çalınanlar", RECENT)]
        return items

    def side_wheel(self, d):
        self.side_scroll = max(0, min(self.side_max, self.side_scroll + d * self.S(36)))
        self.side_cv.schedule(10)

    def home_wheel(self, d):
        self.home_scroll = max(0, min(self.home_max, self.home_scroll + d * self.S(70)))
        self.home_cv.schedule(10)

    def draw_sidebar(self, cv, w, h, base):
        S, F = self.S, self.F
        rowh, gap = S(36), S(12)
        top, bottom = S(98), h - S(64)
        rel, y = [], 0
        for entry in self.nav_items():
            if entry is None:
                y += gap
                continue
            rel.append((y, entry[0], entry[1]))
            y += rowh
        self.side_max = max(0, y - (bottom - top))
        self.side_scroll = min(self.side_scroll, self.side_max)
        rows = [(top + ry - self.side_scroll, label, key) for ry, label, key in rel]
        vis = [r for r in rows if r[0] >= top - S(4) and r[0] + rowh <= bottom + S(4)]
        cv.paint(glass(base, [((0, 0, w - 1, h - 1), S(26), GLASS, 150, "neon")]))
        # etkin satırın arkasındaki kayan seçim hapı (hareketi _anim yapar)
        self.pill_target = next((ry for ry, _, key in vis if key == self.cur_view), None)
        self.side_geo = (S(12), w - S(12), rowh)
        if self.pill_target is not None:
            if self.pill_y is None:
                self.pill_y = float(self.pill_target)
            pcol = _hex(_mix_rgb((22, 16, 48), ACCENT_RGB, 0.22))
            cv.create_polygon(rr_points(S(12), int(self.pill_y) - S(3), w - S(12), int(self.pill_y) + rowh - S(5), S(12)),
                              smooth=True, fill=pcol, outline=ACCENT, width=2, tags="pill")
        tx, tsz = S(24), 26
        lg = self.logo_pil()
        if lg is not None:
            try:
                if getattr(self, "_side_logo_size", None) != S(34):
                    ic = lg.copy()
                    ic.thumbnail((S(34), S(34)))
                    self._side_logo = ImageTk.PhotoImage(ic)
                    self._side_logo_size = S(34)
                cv.create_image(S(22), S(44), image=self._side_logo, anchor="w")
                tx, tsz = S(22) + self._side_logo.width() + S(10), 22
            except Exception:
                traceback.print_exc()
        cv.create_text(tx, S(44), text="GARDAŞ FM", anchor="w", fill=ACCENT, font=F(HEAD_FONT, tsz, "bold"))
        off = self.is_offline()
        cv.create_text(S(24), S(70), text="çevrimdışı mod" if off else (f"Merhaba, {self.profile_name()[:16]}" if self.profile() else "gece yayını açık"), anchor="w",
                       fill=GOLD if off else MUTED, font=F(BODY_FONT, 13))
        for ry, label, key in vis:
            active = key == self.cur_view
            tx0 = S(30)
            if key in (HOME, SEARCH):
                self.nav_icon(cv, key, S(30), ry + S(14), GOLD if active else SOFT)
                tx0 = S(58)
            cv.create_text(tx0, ry + S(14), text=label, anchor="w", fill=GOLD if active else TEXT,
                           font=F(BODY_FONT, 15, "bold" if active else "normal"))
            if key == "newlist":
                cv.add_hit((S(12), ry - S(3), w - S(12), ry + rowh - S(5)), self.new_list_menu)
            elif key == "bul":
                cv.add_hit((S(12), ry - S(3), w - S(12), ry + rowh - S(5)), self.open_song_finder)
            elif key == "yeniui":
                cv.add_hit((S(12), ry - S(3), w - S(12), ry + rowh - S(5)), self.open_webui)
            else:
                rcb = (lambda x, y_, k=key: self.playlist_menu(k, x, y_)) if key in self.pl_keys else None
                cv.add_hit((S(12), ry - S(3), w - S(12), ry + rowh - S(5)), lambda k=key: self.show_view(k), rcb)
        if self.side_scroll > 0:
            cv.create_text(w // 2, top - S(8), text="▴", fill=MUTED, font=F(BODY_FONT, 12))
        if self.side_scroll < self.side_max:
            cv.create_text(w // 2, bottom + S(6), text="▾", fill=MUTED, font=F(BODY_FONT, 12))
        yy = h - S(44)
        cv.create_text(S(30), yy + S(14), text="⚙  Ayarlar", anchor="w", fill=SOFT, font=F(BODY_FONT, 14))
        cv.add_hit((S(12), yy - S(4), w - S(72), yy + S(32)), self.open_settings)
        cv.create_text(w - S(38), yy + S(14), text="«", fill=SOFT, font=F(BODY_FONT, 20, "bold"))
        cv.add_hit((w - S(68), yy - S(4), w - S(12), yy + S(32)), self.toggle_sidebar)

    def nav_icon(self, cv, kind, x, y, col):
        """Menüdeki ev ve arama ikonları (yazı tipine bağlı olmasın diye çizilir)."""
        S = self.S
        w = max(1, S(2))
        if kind == HOME:
            cv.create_line(x, y - S(1), x + S(8), y - S(9), x + S(16), y - S(1), fill=col, width=w,
                           capstyle="round", joinstyle="round")
            cv.create_line(x + S(3), y - S(2), x + S(3), y + S(8), x + S(13), y + S(8), x + S(13), y - S(2),
                           fill=col, width=w, capstyle="round", joinstyle="round")
        else:
            cv.create_oval(x, y - S(9), x + S(11), y + S(2), outline=col, width=w)
            cv.create_line(x + S(9), y, x + S(15), y + S(7), fill=col, width=w, capstyle="round")

    def hero_title(self):
        if self.cur_view.startswith("etiket:"):
            return "#" + self.cur_view.split(":", 1)[1]
        return "Ara" if self.cur_view == SEARCH else self.cur_view

    def hero_sub(self):
        v = self.cur_view
        if v == SEARCH:
            if self.search_busy:
                return "İnternette aranıyor..."
            if not self.search_local and not self.search_online:
                return "Sonuç yok. Başka bir şey dene." if self.search_done else "Bir şarkı ya da sanatçı yaz, Enter'a bas"
            return f"{len(self.lists[SEARCH])} sonuç"
        lst = self.lists.get(v, [])
        tot = sum((it.get("dur") or 0) for it in lst)
        extra = f"  ·  {fmt_total(tot)}" if tot > 60 else ""
        return f"{TAGLINES.get(v, 'Çalma listesi')}  ·  {len(lst)} şarkı{extra}"

    def draw_hero(self, cv, w, h, base):
        S, F = self.S, self.F
        big = self.cur_view == SEARCH
        ph = S(44)
        px1, py1 = S(30), S(104)
        pw = min(S(600 if big else 420), w - S(30) - S(30) - S(104))
        btn = (px1 + pw + S(10), py1, px1 + pw + S(10) + S(88), py1 + ph)
        shapes = [((0, 0, w - 1, h - 1), S(26), GLASS, 95, "neon"),
                  ((px1, py1, px1 + pw, py1 + ph), ph // 2, PANEL_RGB, 255, tuple(NEON2_RGB) + (150,)),
                  (btn, ph // 2, ACCENT_RGB, 255, 0)]
        chips = []
        if big:
            fnt = tkfont.Font(family=BODY_FONT, size=-S(15))
            x, y = S(30), S(168)
            for key, label in (("all", "Hepsi"), ("local", "Katalog"), ("online", "YouTube")):
                cw = fnt.measure(label) + S(30)
                on = self.search_scope == key
                shapes.append(((x, y, x + cw, y + S(32)), S(16), ACCENT_RGB if on else (255, 255, 255),
                               150 if on else 40, 0 if on else 30))
                chips.append((x, y, x + cw, y + S(32), label, lambda k=key: self.set_scope(k), on))
                x += cw + S(8)
            x, y2 = S(30), S(228)
            for q in self.cfg["searches"][:8]:
                cw = fnt.measure(q) + S(30)
                if x + cw > w - S(24):
                    break
                shapes.append(((x, y2, x + cw, y2 + S(32)), S(16), (255, 255, 255), 28, 24))
                chips.append((x, y2, x + cw, y2 + S(32), q, lambda s=q: self.do_search(s), False))
                x += cw + S(8)
        cv.paint(glass(base, shapes))
        vp = self.view_anim_p()
        cv.create_text(S(30), S(46) + int((1 - vp) * S(14)), text=self.hero_title(), anchor="w",
                       fill=_mix("#0e0b22", TEXT, vp), font=F(HEAD_FONT, 38, "bold"))
        cv.create_text(S(32), S(84), text=self.hero_sub(), anchor="w", fill=_mix("#0e0b22", SOFT, vp), font=F(BODY_FONT, 15))
        cv.create_window(px1 + S(18), py1 + S(2), window=self.search_entry, anchor="nw",
                         width=pw - S(36), height=ph - S(4))
        cv.create_text((btn[0] + btn[2]) // 2, (btn[1] + btn[3]) // 2, text="Ara", fill="white",
                       font=F(BODY_FONT, 16, "bold"))
        cv.add_hit(btn, self.do_search)
        if big and self.cfg["searches"]:
            cv.create_text(S(32), S(214), text="SON ARAMALAR", anchor="w", fill=MUTED, font=F(BODY_FONT, 12, "bold"))
        for x1, y1, x2, y2, label, cb, on in chips:
            cv.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=label, fill="white" if on else TEXT,
                           font=F(BODY_FONT, 15, "bold" if on else "normal"))
            cv.add_hit((x1, y1, x2, y2), cb)

    def week_stats(self):
        cut_ts = time.time() - 7 * 86400
        songs, arts = {}, {}
        for p in self.cfg.get("plays", []):
            if p.get("ts", 0) < cut_ts or not p.get("t"):
                continue
            s = songs.setdefault(p["k"], [0, p])
            s[0] += 1
            if p.get("a"):
                arts[p["a"]] = arts.get(p["a"], 0) + 1
        top = sorted(songs.values(), key=lambda x: -x[0])[:5]
        topa = sorted(arts.items(), key=lambda x: -x[1])[:3]
        return top, topa, sum(s[0] for s in songs.values())

    def draw_home(self, cv, w, h, base):
        S, F = self.S, self.F
        now = time.time()
        fc = lambda col, p: _mix("#0e0b22", col, p)       # giriş animasyonunda yazılar yumuşakça belirir
        x0, y0, gap = S(40), S(140), S(14)
        cols = max(1, (w - 2 * x0 + gap) // (S(250) + gap))
        cw = (w - 2 * x0 - (cols - 1) * gap) // cols
        ch = S(96)
        entries = [("shuffle_all", "Karışık çal", "Tüm katalogdan rastgele", True),
                   ("daily", "Bugünün karışığı", "Her gün yeni 25 şarkı", True)]
        entries.append(("radio_now", "Radyo", "Çalan şarkıdan sonsuz yayın", True))
        entries += [("mood:" + n, n, sub, False) for n, sub, _c, _t in MOODS]
        rec = self.lists[RECENT]
        if rec:
            entries.append(("resume", "Kaldığın yerden", rec[0]["title"][:32], False))
        entries += [(c, c, TAGLINES.get(c, ""), False) for c in list(NAV) + list(LIVE_CATS)]
        entries.append((MIX, MIX, TAGLINES[MIX], False))
        entries += [(k, k, TAGLINES.get(k, "Çalma listesi"), False) for k in self.pl_keys]
        entries += [(DOWNLOADS, DOWNLOADS, TAGLINES[DOWNLOADS], False), (RECENT, RECENT, TAGLINES[RECENT], False)]
        rows = (len(entries) + cols - 1) // cols
        top, topa, total = self.week_stats()
        grid_bottom = y0 + rows * (ch + gap)
        panel_h = S(64) + S(26) * len(top) if top else 0
        self.home_max = max(0, grid_bottom + panel_h + S(30) - h)
        self.home_scroll = min(self.home_scroll, self.home_max)
        off = -self.home_scroll
        shapes, boxes = [], []
        for i, (key, name, tag, accent) in enumerate(entries):
            r, c = divmod(i, cols)
            p = _ease((now - self.home_t0 - min(0.05 * i, 0.6)) / 0.35)
            x, y = x0 + c * (cw + gap), y0 + r * (ch + gap) + off + int((1 - p) * S(18))
            shapes.append(((x, y, x + cw, y + ch), S(22), ACCENT_RGB if accent else GLASS,
                           int((175 if accent else 150) * p), 0 if accent else "neon"))
            boxes.append(((x, y, x + cw, y + ch), key, name, tag, accent, p))
        pp = _ease((now - self.home_t0 - 0.5) / 0.4)
        py = grid_bottom + off
        if top:
            shapes.append(((x0, py, w - x0, py + panel_h), S(22), GLASS, int(150 * pp), "neon"))
        cv.paint(glass(base, shapes))
        hour = time.localtime().tm_hour
        selam = "Günaydın" if 5 <= hour < 12 else "İyi günler" if 12 <= hour < 18 else "İyi akşamlar" if hour < 23 else "İyi geceler"
        p0 = _ease((now - self.home_t0) / 0.4)
        cv.create_text(x0, S(58) + off, text="Gardaş FM", anchor="w", fill=fc(TEXT, p0), font=F(HEAD_FONT, 44, "bold"))
        cv.create_text(x0 + S(2), S(102) + off, text=f"{selam}, ne dinliyoruz?", anchor="w", fill=fc(SOFT, p0),
                       font=F(BODY_FONT, 18))
        for (x1, y1, x2, y2), key, name, tag, accent, p in boxes:
            cv.create_text(x1 + S(20), y1 + S(28), text=name, anchor="w", fill=fc("#ffffff" if accent else TEXT, p),
                           font=F(HEAD_FONT, 20, "bold"))
            cv.create_text(x1 + S(20), y1 + S(56), text=tag, anchor="w", fill=fc(SOFT if accent else MUTED, p),
                           font=F(BODY_FONT, 13))
            if key in self.lists:
                cv.create_text(x1 + S(20), y1 + S(77), text=f"{len(self.lists[key])} şarkı", anchor="w",
                               fill=fc(GOLD, p), font=F(BODY_FONT, 12, "bold"))
            if key == "shuffle_all":
                cb = self.play_all_shuffled
            elif key == "daily":
                cb = self.play_daily
            elif key == "radio_now":
                cb = self.radio_from_current
            elif key.startswith("mood:"):
                cb = lambda k=key: self.play_mood(k[5:])
            elif key == "resume":
                cb = lambda: self.play_item_now(self.lists[RECENT][0]) if self.lists[RECENT] else None
            else:
                cb = lambda k=key: self.show_view(k)
            rcb = (lambda x, y_, k=key: self.playlist_menu(k, x, y_)) if key in self.pl_keys else None
            cv.add_hit((x1, y1, x2, y2), cb, rcb)
        if top:
            cv.create_text(x0 + S(22), py + S(28), text=f"BU HAFTA  ·  {total} şarkı dinledin", anchor="w",
                           fill=fc(GOLD, pp), font=F(BODY_FONT, 12, "bold"))
            if topa:
                cv.create_text(w - x0 - S(22), py + S(28), text=("En çok: " + ", ".join(f"{a} ({n})" for a, n in topa))[:60],
                               anchor="e", fill=fc(SOFT, pp), font=F(BODY_FONT, 12))
            for j, (cnt, pl) in enumerate(top):
                yy = py + S(58) + j * S(26)
                txt = f"{j + 1}.  {pl['t']}" + (f"  —  {pl['a']}" if pl.get("a") else "")
                cv.create_text(x0 + S(22), yy, text=txt[:80], anchor="w", fill=fc(TEXT, pp), font=F(BODY_FONT, 14))
                cv.create_text(w - x0 - S(22), yy, text=f"×{cnt}", anchor="e", fill=fc(GOLD, pp), font=F(BODY_FONT, 13, "bold"))
                it = make_item(pl.get("a", ""), pl["t"], pl.get("u"))
                cv.add_hit((x0, yy - S(12), w - x0, yy + S(12)), lambda it=it: self.play_item_now(it))

    def draw_list(self, cv, w, h, base):
        S = self.S
        cv.paint(glass(base, [((0, 0, w - 1, h - 1), S(26), PANEL_RGB, 238, "neon")]))
        cv.create_window(S(12), S(12), window=self.list_inner, anchor="nw", width=w - S(24), height=h - S(24))

    def placeholder_cover(self, side):
        if side in self._ph_cache:
            return self._ph_cache[side]
        mask = Image.linear_gradient("L").resize((side, side))
        im = Image.composite(Image.new("RGB", (side, side), (20, 14, 50)),
                             Image.new("RGB", (side, side), (84, 30, 120)), mask)
        d = ImageDraw.Draw(im)
        c = side // 2
        for r, col in ((0.44, (10, 8, 24)), (0.31, (24, 17, 54)), (0.15, ACCENT_RGB), (0.03, (10, 8, 24))):
            rr = int(side * r)
            d.ellipse((c - rr, c - rr, c + rr, c + rr), fill=col)
        self._ph_cache.clear()
        self._ph_cache[side] = im
        return im

    def draw_np(self, cv, w, h, base):
        S, F = self.S, self.F
        side = max(S(120), min(w - S(56), int(h * 0.36)))
        cx, cy = (w - side) // 2, S(28)
        self.np_geo = (cx, cy, side)
        ly = cy + side + S(138)
        base = glass(base, [((0, 0, w - 1, h - 1), S(26), GLASS, 150, "neon"),
                            ((S(20), ly, w - S(20), h - S(20)), S(18), PANEL_RGB, 238, tuple(NEON2_RGB) + (120,))])
        sq = (ImageOps.fit(self.cover, (side, side), method=Image.Resampling.BILINEAR)
              if self.cover is not None else self.placeholder_cover(side))
        mask = Image.new("L", (side, side), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, side - 1, side - 1), radius=S(18), fill=255)
        base.paste(sq, (cx, cy), mask)
        base = glass(base, [((cx, cy, cx + side - 1, cy + side - 1), S(18), (0, 0, 0), 0, "neon")])     # neon kapak çerçevesi
        cv.paint(base)
        now = self.play_items[self.play_idx] if 0 <= self.play_idx < len(self.play_items) else None
        ty = cy + side + S(22)
        cv.create_text(S(28), ty, text="ŞİMDİ ÇALIYOR", anchor="w", fill=ACCENT, font=F(BODY_FONT, 12, "bold"))
        cv.create_text(w - S(28), ty, text="⤢  Söz modu (L)", anchor="e", fill=SOFT, font=F(BODY_FONT, 12, "bold"))
        cv.add_hit((w - S(170), ty - S(12), w - S(24), ty + S(12)), self.open_lyrics_full)
        title = fit_lines(now["title"] if now else "Henüz bir şarkı seçilmedi", HEAD_FONT, S(20), w - S(56), 2)
        cv.create_text(S(28), ty + S(16), text=title, anchor="nw", fill=TEXT, width=w - S(56),
                       font=F(HEAD_FONT, 20, "bold"))
        cv.create_text(S(28), ty + S(86), text=(now["artist"] if now else "") or "", anchor="w", fill=NEON2,
                       font=F(BODY_FONT, 15))
        cv.create_window(S(30), ly + S(10), window=self.lyrics_inner, anchor="nw",
                         width=w - S(60), height=max(S(60), h - ly - S(40)))

    def draw_bar(self, cv, w, h, base):
        S = self.S
        cv.paint(glass(base, [((0, 0, w - 1, h - 1), S(26), PANEL_RGB, 238, "neon")]))
        cv.create_window(S(12), S(10), window=self.bar_inner, anchor="nw", width=w - S(24), height=h - S(20))

    # ------------------------------------------------------------ sayfa değiştirme ve liste
    def show_view(self, name):
        self.hide_suggestions()
        if name in LIVE_CATS:
            self.ensure_live(name)
        if name.startswith("etiket:"):
            self.refresh_tag_list(name)
        self.cur_view = name
        self.view_t0 = time.time()
        if name == HOME:
            self.home_t0, self.home_scroll = (0.0 if self.cfg.get("anim", "Tam") == "Kapalı" else time.time()), 0       # giriş animasyonu yeniden başlar
            self.hero_cv.grid_remove()
            self.list_cv.grid_remove()
            self.home_cv.grid()
            self.home_cv.schedule(1)
        else:
            self.home_cv.grid_remove()
            self.hero_cv.grid()
            self.list_cv.grid()
            self.hero_cv.configure(height=self.S(270 if name == SEARCH else 160))
            self.hero_cv.schedule(1)
            self.fill_tree()
        self.side_cv.schedule(1)

    def src_text(self, it):
        k = key_of(it)
        if k in self.dl_active:
            return f"⬇ %{int(self.dl_progress.get(k, 0) * 100)}"
        if is_local(it):
            return "Yerel"
        if self.is_downloaded(it):
            return "⬇ İndirildi"
        return "YouTube" if it["url"] else "Katalog"

    def fill_tree(self):
        name = self.cur_view
        if name == SEARCH:
            items = {"local": self.search_local, "online": self.search_online}.get(
                self.search_scope, self.search_local + self.search_online)
            self.lists[SEARCH] = list(items)
        elif name == DOWNLOADS:
            self.lists[DOWNLOADS] = self.dl_items()
        self.view_items = self.lists.get(name, [])
        self.tree.delete(*self.tree.get_children())
        self._playing_iid = None
        if not self.view_items:
            msg = {SEARCH: "Aramak için yukarıdaki kutuya yaz.",
                   MIX: "Henüz favorin yok. Şarkıya sağ tıkla ya da '♥ Favori'ye bas.",
                   MIX2: "Mix listen boş. Şarkıya sağ tıkla → Listeye ekle.",
                   DOWNLOADS: "Henüz indirilen şarkı yok. Şarkıya sağ tıkla → İndir; ya da Diğer → Klasörden müzik ekle.",
                   QUEUE: "Sıra boş. Şarkıya sağ tıkla → Sıraya ekle.",
                   RECENT: "Henüz bir şey çalmadın."}.get(
                name, "Bu liste boş. Şarkıya sağ tıkla → Listeye ekle." if name in self.pl_keys else "Liste boş.")
            self.tree.insert("", "end", values=("", msg, "", "", ""))
            return
        cur = self.play_items[self.play_idx] if 0 <= self.play_idx < len(self.play_items) else None
        favs = {key_of(x) for x in self.lists[MIX]}
        for i, it in enumerate(self.view_items):
            is_cur = cur is not None and key_of(it) == key_of(cur)
            if is_cur:
                self._playing_iid = str(i)
            self.tree.insert("", "end", iid=str(i), tags=("alt",) if i % 2 else (),
                             values=("▶" if is_cur else i + 1, self.title_text(it, favs),
                                     it["artist"], self.dur_text(it), self.src_text(it)))

    def mark_playing(self):
        cur = self.play_items[self.play_idx] if 0 <= self.play_idx < len(self.play_items) else None
        favs = {key_of(x) for x in self.lists[MIX]}
        self._playing_iid = None
        for i, it in enumerate(self.view_items):
            iid = str(i)
            if not self.tree.exists(iid):
                break
            is_cur = cur is not None and key_of(it) == key_of(cur)
            if is_cur:
                self._playing_iid = iid
            self.tree.item(iid, values=("▶" if is_cur else i + 1, self.title_text(it, favs),
                                        it["artist"], self.dur_text(it), self.src_text(it)))

    def selected(self):
        sel = self.tree.selection()
        if sel and sel[0].isdigit() and int(sel[0]) < len(self.view_items):
            return int(sel[0])
        return None

    # ------------------------------------------------------------ liste işlemleri
    def sel_item(self):
        i = self.selected()
        return self.view_items[i] if i is not None else None

    def is_fav(self, it):
        return any(key_of(x) == key_of(it) for x in self.lists[MIX])

    def toggle_fav(self, it=None):
        it = it or self.sel_item()
        if it is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        k = key_of(it)
        if self.is_fav(it):
            self.lists[MIX][:] = [x for x in self.lists[MIX] if key_of(x) != k]
            self.flash("Favorilerden çıkarıldı")
        else:
            self.lists[MIX].append(make_item(it["artist"], it["title"], it["url"], it.get("dur")))
            self.flash("Favorilere eklendi ♥")
        self.save_mix()
        if self.cur_view == MIX:
            self.fill_tree()
        else:
            self.mark_playing()

    def add_to_list(self, key, it=None):
        it = it or self.sel_item()
        if it is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        if key == MIX:
            if not self.is_fav(it):
                self.toggle_fav(it)
            else:
                self.flash("Zaten favorilerinde")
            return
        lst = self.lists[key]
        if any(key_of(x) == key_of(it) for x in lst):
            self.flash("Zaten bu listede")
            return
        lst.append(make_item(it["artist"], it["title"], it["url"], it.get("dur")))
        self.save_playlists()
        self.flash(f"Eklendi: {key.replace(PL_PREFIX, '')}")
        if self.cur_view == key:
            self.fill_tree()

    def remove_selected(self):
        v, i = self.cur_view, self.selected()
        if i is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        if v == DOWNLOADS:
            self.remove_download(self.view_items[i])
            return
        if v == MIX:
            del self.lists[MIX][i]
            self.save_mix()
        elif v in self.pl_keys:
            del self.lists[v][i]
            self.save_playlists()
        elif v == QUEUE:
            del self.queue[i]
        elif v == RECENT:
            del self.lists[RECENT][i]
        else:
            self.flash("Bu sayfadaki şarkılar çıkarılamaz (listeden çıkarmak için favori/liste sayfasına git)", 5000)
            return
        self.fill_tree()

    def enqueue(self, it=None, front=False):
        it = it or self.sel_item()
        if it is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        it = make_item(it["artist"], it["title"], it["url"], it.get("dur"))
        if front:
            self.queue.insert(0, it)
        else:
            self.queue.append(it)
        self.flash("Sıradaki olarak ayarlandı" if front else f"Sıraya eklendi ({len(self.queue)})")
        if self.cur_view == QUEUE:
            self.fill_tree()
        self._shuf_pick = None
        self.prefetch_next()

    def enqueue_all(self):
        for it in self.view_items:
            self.queue.append(make_item(it["artist"], it["title"], it["url"], it.get("dur")))
        self.flash(f"{len(self.view_items)} şarkı sıraya eklendi")
        if self.cur_view == QUEUE:
            self.fill_tree()

    def clear_queue(self):
        self.queue.clear()
        self.flash("Sıra temizlendi")
        if self.cur_view == QUEUE:
            self.fill_tree()

    def open_on_youtube(self, it):
        webbrowser.open(it["url"] if it["url"] and not is_local(it)
                        else "https://www.youtube.com/results?search_query=" + quote_plus(f"{it['artist']} {it['title']}"))

    def copy_name(self, it):
        self.clipboard_clear()
        self.clipboard_append(f"{it['artist']} - {it['title']}" if it["artist"] else it["title"])
        self.flash("Panoya kopyalandı")

    def popup(self, entries, x, y):
        m = tk.Menu(self, tearoff=0, bg=PANEL, fg=TEXT, activebackground=ACCENT, activeforeground="white",
                    bd=0, relief="flat", font=(BODY_FONT, 11))
        for e in entries:
            if e is None:
                m.add_separator()
            elif isinstance(e[1], list):
                sub = tk.Menu(m, tearoff=0, bg=PANEL, fg=TEXT, activebackground=ACCENT, activeforeground="white",
                              bd=0, font=(BODY_FONT, 11))
                for s in e[1]:
                    if s is None:
                        sub.add_separator()
                    else:
                        sub.add_command(label=s[0], command=s[1])
                m.add_cascade(label=e[0], menu=sub)
            else:
                m.add_command(label=e[0], command=e[1])
        try:
            m.tk_popup(x, y)
        finally:
            m.grab_release()

    def list_targets(self, it):
        """'Listeye ekle' alt menüsü: favoriler, tüm çalma listeleri ve yeni liste."""
        out = [("♥  Favorilerim", lambda: self.add_to_list(MIX, it))]
        out += [(k.replace(PL_PREFIX, ""), lambda k=k: self.add_to_list(k, it)) for k in self.pl_keys]
        return out + [None, ("+  Yeni liste...", lambda: self.new_playlist(then_add=it))]

    def item_menu(self, it, x, y):
        dl = self.is_downloaded(it)
        e = [("▶  Çal", self.play_selected),
             ("Sıradaki olarak çal", lambda: self.enqueue(it, front=True)),
             ("Sıraya ekle", lambda: self.enqueue(it)),
             None,
             ("♥  Favorilerden çıkar" if self.is_fav(it) else "♥  Favorilere ekle", lambda: self.toggle_fav(it)),
             ("Listeye ekle", self.list_targets(it)),
             ("#  Etiketler...", lambda: self.edit_tags(it)),
             ("◉  Radyo başlat", lambda: self.radio_start(it)),
             None]
        if is_local(it):
            e.append(("Bu kaydı listeden kaldır", lambda: self.remove_download(it)))
        elif dl:
            e.append(("İndirileni sil (yer aç)", lambda: self.remove_download(it)))
        else:
            e.append(("⬇  İndir (internetsiz dinle)", lambda: self.download(it)))
        e += [None,
              ("Bu sanatçıyı ara", lambda: self.do_search(it["artist"] or it["title"])),
              ("YouTube'da aç", lambda: self.open_on_youtube(it)),
              ("Adını kopyala", lambda: self.copy_name(it))]
        if self.cur_view in (MIX, RECENT, QUEUE, DOWNLOADS, *self.pl_keys):
            e += [None, ("Bu listeden çıkar", self.remove_selected)]
        if self.cur_view == QUEUE and self.queue:
            e.append(("Sırayı temizle", self.clear_queue))
        self.popup(e, x, y)

    def on_tree_menu(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid or not iid.isdigit() or int(iid) >= len(self.view_items):
            return
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        self.item_menu(self.view_items[int(iid)], e.x_root, e.y_root)

    def add_menu(self):
        """Araç çubuğundaki 'Listeye ekle ▾' düğmesi."""
        it = self.sel_item()
        if it is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        x, y = self.winfo_pointerx(), self.winfo_pointery()
        self.popup(self.list_targets(it), x, y)

    # ------------------------------------------------------------ çevrimdışı: indirme ve yerel müzik
    def local_path(self, it):
        d = self.dl_index.get(key_of(it))
        if d and d.get("path") and Path(d["path"]).exists():
            return d["path"]
        return None

    def is_downloaded(self, it):
        return self.local_path(it) is not None

    def dl_items(self):
        rows = sorted(self.dl_index.values(), key=lambda d: d.get("t", 0), reverse=True)
        return [make_item(d.get("artist", ""), d.get("title", "?"), d.get("url"), d.get("dur"))
                for d in rows if d.get("path") and Path(d["path"]).exists()]

    def is_offline(self):
        return bool(self.cfg.get("offline")) or self.net_bad >= 2

    def playable(self, it):
        return not self.is_offline() or self.is_downloaded(it)

    def net_check(self):
        def worker():
            ok = time.time() - getattr(self, "_net_seen", 0.0) < 60     # yakın zamanda bir istek başarılı olduysa internet var
            for host, port in (("www.youtube.com", 443), ("www.google.com", 443), ("lrclib.net", 443),
                               ("1.1.1.1", 443), ("8.8.8.8", 53)):
                if ok:
                    break
                try:
                    socket.create_connection((host, port), timeout=3.5).close()
                    ok = True
                except Exception:
                    continue

            def done():
                was = self.is_offline()
                self.net_bad = 0 if ok else self.net_bad + 1
                if self.is_offline() != was and not self.cfg.get("offline"):
                    self.flash("İnternet yok: indirilen şarkılar çalınır" if self.is_offline()
                               else "Bağlantı geri geldi", 7000)
                    self.side_cv.schedule(1)
                self.after(20000, self.net_check)
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    def download(self, it=None, quiet=False):
        it = it or self.sel_item()
        if it is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        k = key_of(it)
        if is_local(it) or self.is_downloaded(it):
            if not quiet:
                self.flash("Zaten indirilmiş")
            return
        if k in self.dl_active:
            return
        if self.is_offline():
            self.flash("İnternet yok, indirilemez", 5000)
            return
        self.dl_active.add(k)
        self.dl_progress[k] = 0.0
        self.dl_pool.submit(self._dl_job, make_item(it["artist"], it["title"], it["url"], it.get("dur")))
        if not quiet:
            self.flash("İndirme sıraya alındı")
        self.mark_playing()

    def download_many(self, items=None):
        items = self.view_items if items is None else items
        n = 0
        for it in list(items):
            if not (is_local(it) or self.is_downloaded(it)) and key_of(it) not in self.dl_active:
                self.download(it, quiet=True)
                n += 1
        self.flash(f"{n} şarkı indirilecek" if n else "Hepsi zaten indirilmiş", 4000)

    def _dl_job(self, it):
        k = key_of(it)
        label = f"{it['artist']} - {it['title']}" if it["artist"] else it["title"]
        entry, last = None, [0.0]
        try:
            DL_DIR.mkdir(parents=True, exist_ok=True)
            try:
                url = self.target_url(it)
            except Exception as ex:
                print("Sürüm seçilemedi:", ex)
                url = it["url"] or f"ytsearch1:{it['artist']} {it['title']} audio"

            def hook(d):
                if d.get("status") != "downloading":
                    return
                tot = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                if tot:
                    self.dl_progress[k] = min(1.0, d.get("downloaded_bytes", 0) / tot)
                if time.time() - last[0] > 1.0:
                    last[0] = time.time()
                    self.ui(lambda: (self.flash(f"⬇ {label[:30]}  %{int(self.dl_progress.get(k, 0) * 100)}", 2500),
                                     self.mark_playing()))
            opts = {"quiet": True, "no_warnings": True, "format": "bestaudio[ext=m4a]/bestaudio/best",
                    "outtmpl": str(DL_DIR / "%(id)s.%(ext)s"), "noplaylist": True, "progress_hooks": [hook],
                    "socket_timeout": 15, "retries": 3}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if "entries" in info:
                    info = info["entries"][0]
                path = ydl.prepare_filename(info)
            if not Path(path).exists():
                cands = [c for c in DL_DIR.glob(f"{info['id']}.*") if c.suffix not in (".part", ".ytdl")]
                path = str(cands[0]) if cands else None
            if not path:
                raise RuntimeError("indirilen dosya bulunamadı")
            vid = info.get("id")
            self.cover_image(vid, keep=True)          # kapak da saklanır (internetsiz de görünsün)
            self.get_lyrics_entry(it)                # sözler de saklanır
            entry = {"artist": it["artist"], "title": it["title"], "url": it["url"],
                     "dur": info.get("duration") or it.get("dur"), "path": str(path), "id": vid, "t": time.time()}
        except Exception as ex:
            print("İndirme hatası:", ex)

        def done():
            self.dl_active.discard(k)
            self.dl_progress.pop(k, None)
            if entry:
                self.dl_index[k] = entry
                save_json(DL_INDEX_FILE, self.dl_index)
                self.lists[DOWNLOADS] = self.dl_items()
                self.flash(f"⬇ İndirildi: {label[:34]}", 5000)
                if self.cur_view == DOWNLOADS:
                    self.fill_tree()
            else:
                self.flash(f"İndirilemedi: {label[:30]}", 6000)
            self.mark_playing()
        self.ui(done)

    def remove_download(self, it):
        k = key_of(it)
        d = self.dl_index.get(k)
        if not d:
            return
        if not is_local(it):                     # klasörden eklenen kendi dosyaların asla silinmez
            try:
                Path(d["path"]).unlink(missing_ok=True)
            except Exception:
                self.flash("Dosya kullanımda: önce şarkıyı durdur", 5000)
                return
        self.dl_index.pop(k, None)
        save_json(DL_INDEX_FILE, self.dl_index)
        self.lists[DOWNLOADS] = self.dl_items()
        self.flash("Listeden kaldırıldı" if is_local(it) else "İndirilen dosya silindi")
        if self.cur_view == DOWNLOADS:
            self.fill_tree()
        else:
            self.mark_playing()

    def add_local_folder(self):
        d = filedialog.askdirectory(parent=self, title="Müzik klasörünü seç")
        if not d:
            return
        self.flash("Klasör taranıyor...", 30000)

        def worker():
            found = []
            for root, _, files in os.walk(d):
                for fn in files:
                    if Path(fn).suffix.lower() in AUDIO_EXT:
                        found.append(Path(root) / fn)
                if len(found) > 5000:
                    break

            def done():
                n = 0
                for p in found:
                    k = "local:" + str(p)
                    if k in self.dl_index:
                        continue
                    a, t = split_name(p.stem)
                    self.dl_index[k] = {"artist": a, "title": t, "url": k, "dur": None, "path": str(p),
                                        "t": time.time() - n * 0.001}
                    n += 1
                save_json(DL_INDEX_FILE, self.dl_index)
                self.lists[DOWNLOADS] = self.dl_items()
                self.flash(f"{n} yerel şarkı eklendi (İndirilenler sayfasında)" if n else "Yeni şarkı bulunamadı", 6000)
                if self.cur_view == DOWNLOADS:
                    self.fill_tree()
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    def clear_downloads(self):
        n = sum(1 for d in self.dl_index.values() if not str(d.get("url") or "").startswith("local:"))
        if not n or not messagebox.askyesno("Gardaş FM", f"İndirilen {n} şarkı silinsin mi? (klasörden eklediklerin silinmez)"):
            return
        for k in [k for k, d in self.dl_index.items() if not str(d.get("url") or "").startswith("local:")]:
            try:
                Path(self.dl_index[k]["path"]).unlink(missing_ok=True)
            except Exception:
                continue
            self.dl_index.pop(k, None)
        save_json(DL_INDEX_FILE, self.dl_index)
        self.lists[DOWNLOADS] = self.dl_items()
        self.flash("İndirilenler temizlendi")
        self.show_view(self.cur_view)

    def dl_size_text(self):
        try:
            tot = sum(Path(d["path"]).stat().st_size for d in self.dl_index.values()
                      if d.get("path") and not str(d.get("url") or "").startswith("local:") and Path(d["path"]).exists())
        except Exception:
            tot = 0
        return f"{tot / 1048576:.0f} MB"

    # ------------------------------------------------------------ arama
    def set_scope(self, key):
        self.search_scope = key
        if self.cur_view == SEARCH:
            self.show_view(SEARCH)

    def do_search(self, q=None):
        self.hide_suggestions()
        q = (q if isinstance(q, str) else self.search_entry.get()).strip()
        if not q:
            self.flash("Aramak için bir şey yaz")
            return
        hist = [s for s in self.cfg["searches"] if fold(s) != fold(q)]
        self.cfg["searches"] = ([q] + hist)[:8]
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, q)
        self.search_gen += 1
        gen = self.search_gen
        words = fold(q).split()

        def hit(it):                      # Türkçe harfe duyarlı: "imkansizim" -> "İmkansızım"
            hay = fold(f"{it['artist']} {it['title']}")
            return all(w in hay for w in words)
        self.search_local = [it for cat in NAV for it in self.lists[cat] if hit(it)]
        seen = {key_of(x) for x in self.search_local}
        self.search_local += [it for it in self.lists[DOWNLOADS] if hit(it) and key_of(it) not in seen]
        self.search_online = []
        if self.is_offline():
            self.search_busy, self.search_done = False, True
            self.flash("Çevrimdışı: katalog ve indirilenlerde aranıyor", 4000)
            self.show_view(SEARCH)
            return
        self.search_busy, self.search_done = True, False
        self.show_view(SEARCH)

        def worker():
            online = []
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
                    info = ydl.extract_info(f"ytsearch15:{q}", download=False)
                for e in info.get("entries", []):
                    online.append(make_item(e.get("channel") or e.get("uploader") or "", e.get("title", "?"),
                                            e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
                                            e.get("duration")))
            except Exception as ex:
                print("Arama hatası:", ex)

            def done():
                if gen != self.search_gen:
                    return
                self.search_online = online
                self.search_busy, self.search_done = False, True
                if not online and not self.search_local:
                    self.flash("İnternetten sonuç gelmedi, bağlantını kontrol et", 6000)
                if self.cur_view == SEARCH:
                    self.show_view(SEARCH)
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------ çalma
    def remember_id(self, it, vid, dur=None):
        if it["url"] or not vid:
            return
        with self.cache_lock:
            self.id_cache[key_of(it)] = {"id": vid, "dur": dur}
            if len(self.id_cache) > 3000:
                for old in list(self.id_cache)[:500]:
                    self.id_cache.pop(old, None)
            save_json(CACHE_FILE, self.id_cache)

    def target_url(self, it):
        """Çözülecek adres: link varsa o, katalog şarkısıysa önbellekteki video, yoksa akıllı seçim."""
        if it["url"] and not is_local(it):
            return it["url"]
        c = self.id_cache.get(key_of(it))
        if c and c.get("id"):
            return "https://www.youtube.com/watch?v=" + c["id"]
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True,
                               "socket_timeout": 10}) as ydl:
            info = ydl.extract_info(f"ytsearch6:{it['artist']} {it['title']} audio", download=False)
        entries = [e for e in (info or {}).get("entries", []) if e and e.get("id")]
        best = pick_best(entries, it["artist"], it["title"])
        if not best:
            raise RuntimeError("arama sonucu yok")
        self.remember_id(it, best["id"], best.get("duration"))
        return "https://www.youtube.com/watch?v=" + best["id"]

    def resolve_job(self, it):
        p = self.local_path(it)
        if p:                                    # indirilmiş/yerel dosya: internet gerekmez
            d = self.dl_index.get(key_of(it), {})
            return {"stream": p, "local": True, "ts": time.time(), "id": d.get("id"),
                    "dur": d.get("dur") or it.get("dur")}
        if self.cfg.get("offline"):
            raise RuntimeError("çevrimdışı mod: bu şarkı indirilmemiş")
        try:
            query = self.target_url(it)
        except Exception as ex:
            print("Sürüm seçilemedi, ilk sonuca dönülüyor:", ex)
            query = it["url"] or f"ytsearch1:{it['artist']} {it['title']} audio"
        last = None
        for opts in (YDL_FAST, YDL_PLAIN):
            try:
                ydl = getattr(self.tls, "ydl", None)
                if ydl is None or getattr(self.tls, "opts", None) is not opts:
                    ydl = self.tls.ydl = yt_dlp.YoutubeDL(opts)   # örnek her işçide bir kez kurulur
                    self.tls.opts = opts
                info = ydl.extract_info(query, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                self.remember_id(it, info.get("id"), info.get("duration"))
                return {"stream": info["url"], "ts": time.time(), "id": info.get("id"),
                        "dur": info.get("duration")}
            except Exception as ex:
                last = ex
                self.tls.ydl = None
        raise last

    def get_stream_future(self, it):
        k = key_of(it)
        fut = self.futures.get(k)
        if fut is not None:
            if not fut.done():
                return fut
            if fut.exception() is None and time.time() - fut.result()["ts"] < 4 * 3600:
                return fut
        fut = self.pool.submit(self.resolve_job, it)
        self.futures[k] = fut
        if len(self.futures) > 300:   # önbellek sonsuza büyümesin
            for old in list(self.futures)[:100]:
                self.futures.pop(old, None)
        return fut

    def start_play(self, items, idx):
        items = list(items)
        if not items:
            return
        self.play_items, self.play_idx = items, idx
        self._shuf_pick = None
        self.radio_on = False                          # başka bir şey seçilince radyo kapanır
        self.play_current()

    def play_selected(self):
        i = self.selected()
        if i is None:
            self.flash("Önce listeden bir şarkı seç")
            return
        it = self.view_items[i]
        if not self.playable(it):
            self.flash("Çevrimdışısın ve bu şarkı indirilmemiş", 5000)
            return
        if self.cur_view == QUEUE:               # sıradan seçilen şarkı sıradan çıkar, hemen çalar
            self.queue.pop(i)
            self.play_items.insert(self.play_idx + 1, it)
            self.play_idx += 1
            self.fill_tree()
            self.play_current()
            return
        self.start_play(self.view_items, i)

    def shuffle_on(self):
        self.shuffle = True
        self.update_shuffle_btn()

    def play_view_shuffled(self):
        items = [it for it in self.view_items if self.playable(it)]
        if not items:
            self.flash("Çalınacak şarkı yok" + (" (çevrimdışı: sadece indirilenler çalar)" if self.is_offline() else ""), 5000)
            return
        self.shuffle_on()
        self.start_play(items, random.randrange(len(items)))

    def play_all_shuffled(self):
        songs = [it for c in NAV for it in self.lists[c] if self.playable(it)]
        if not songs:
            self.flash("Çalınacak şarkı yok (çevrimdışı: önce şarkı indir)", 5000)
            return
        self.shuffle_on()
        self.start_play(songs, random.randrange(len(songs)))

    def daily_mix(self):
        """Her gün değişen, gün içinde aynı kalan 25 şarkılık karışık liste."""
        rnd = random.Random(time.strftime("%Y-%m-%d"))
        seen, pool = set(), []
        for it in [x for c in NAV for x in self.lists[c]] + self.lists[MIX]:
            k = key_of(it)
            if k not in seen and self.playable(it):
                seen.add(k)
                pool.append(it)
        rnd.shuffle(pool)
        return pool[:25]

    def play_daily(self):
        items = self.daily_mix()
        if not items:
            self.flash("Bugünün karışığı için şarkı yok", 4000)
            return
        self.shuffle = False
        self.update_shuffle_btn()
        self.start_play(items, 0)

    def play_item_now(self, it):
        if self.playable(it):
            self.start_play([it], 0)
        else:
            self.flash("Çevrimdışısın ve bu şarkı indirilmemiş", 5000)

    def play_current(self, push=True):
        if not (0 <= self.play_idx < len(self.play_items)):
            return
        it = self.play_items[self.play_idx]
        if push and self.now_item is not None and key_of(self.now_item) != key_of(it):
            self.history.append(self.now_item)       # geri tuşu için geçmiş
            del self.history[:-50]
        self.now_item = it
        self._shuf_pick = None
        self.radio_check()
        self.apply_song_volume()
        self.token += 1
        token = self.token
        self.player.stop()
        self._cover_prev = self.cover                     # yeni kapak gelince eskisinden yumuşakça geçilir
        self.cover = None
        try:
            if getattr(self, "_toast_after", None) is not None:
                self.after_cancel(self._toast_after)
        except Exception:
            pass
        self._toast_after = self.after(2200, lambda tok=self.token: self._toast_if(tok))
        label = f"{it['artist']} - {it['title']}" if it["artist"] else it["title"]
        self.np_title.configure(text=label[:36])
        self.np_sub.configure(text="Bağlanıyor...", text_color=GOLD)
        self.title(f"{label[:60]} - Gardaş FM")
        self.play_btn.configure(text="…")
        cached = self.lyrics_cache.get(key_of(it))
        if cached:
            self.show_lyrics(cached)
        else:
            self.set_lyrics("Sözler aranıyor...")
            threading.Thread(target=self.fetch_lyrics, args=(it, token), daemon=True).start()
        self.mark_playing()
        self.np_cv.schedule(10)
        fut = self.get_stream_future(it)
        fut.add_done_callback(lambda f, it=it, token=token: self.ui(lambda: self.on_stream_ready(f, it, token)))

    def on_stream_ready(self, fut, it, token):
        if token != self.token:
            return
        try:
            info = fut.result()
        except Exception as ex:
            print("Çalma hatası:", ex)
            self.futures.pop(key_of(it), None)
            self.failed_streak += 1
            self.play_btn.configure(text="▶")
            if self.failed_streak < 5 and len(self.play_items) > 1:
                self.np_sub.configure(text="Çalınamadı, sonrakine geçiliyor...", text_color=ACCENT)
                self.after(1200, lambda: self.next_song(auto=True) if token == self.token else None)
            else:
                self.np_sub.configure(text="Çalınamadı (internet/yt-dlp güncel mi?)", text_color=ACCENT)
            return
        media = (self.vlc_instance.media_new_path(info["stream"]) if info.get("local")
                 else self.vlc_instance.media_new(info["stream"]))
        self.player.set_media(media)
        self.player.play()
        self.play_btn.configure(text="⏸")
        self.np_sub.configure(text="Çalıyor (çevrimdışı)" if info.get("local") else "Çalıyor", text_color=GOLD)
        if info.get("dur") and not it.get("dur"):
            it["dur"] = info["dur"]
            self.mark_playing()
        self.remember_recent(it)
        self.record_play(it)
        self.prefetch_next()
        threading.Thread(target=self.fetch_cover, args=(info.get("id"), token), daemon=True).start()

    def remember_recent(self, it):
        k = key_of(it)
        rec = [x for x in self.lists[RECENT] if key_of(x) != k]
        rec.insert(0, make_item(it["artist"], it["title"], it["url"], it.get("dur")))
        self.lists[RECENT] = rec[:40]

    def record_play(self, it):
        """Haftalık özet için dinleme kaydı; ayarlar her şarkıda kaydedilir (çökse de kaybolmaz)."""
        plays = self.cfg.setdefault("plays", [])
        plays.append({"k": key_of(it), "a": it["artist"], "t": it["title"], "u": it["url"], "ts": int(time.time())})
        del plays[:-600]
        self.save_cfg()

    def _index_of(self, item, skip=None):
        for i, x in enumerate(self.play_items):
            if x is item and i != skip:
                return i
        return None

    def peek_next(self, wrap=False):
        """Sıradaki şarkı: önce kuyruk, sonra karışık/sıralı. (tür, şarkı, indeks) döner; bitti ise None.
        Hazırlık (prefetch) ve gerçek geçiş aynı sonucu kullanır, karışık modda da bekleme olmaz."""
        if self.queue:
            return ("queue", self.queue[0], None)
        n = len(self.play_items)
        if n == 0 or not (0 <= self.play_idx < n):
            return None
        cur = self.play_items[self.play_idx]
        if self.shuffle and n > 1:
            pick = self._shuf_pick
            if pick is None or pick is cur or self._index_of(pick, self.play_idx) is None or not self.playable(pick):
                cands = [x for x in self.play_items if x is not cur and self.playable(x)]
                if not cands:
                    return None
                pick = self._shuf_pick = random.choice(cands)
            return ("list", pick, self._index_of(pick, self.play_idx))
        for step in range(1, n + 1):
            j = self.play_idx + step
            if j >= n:
                if not (wrap or self.repeat == 1):
                    return None
                j %= n
            if self.playable(self.play_items[j]):
                return ("list", self.play_items[j], j)
        return None

    def prefetch_next(self):
        nxt = self.peek_next(wrap=True)
        if nxt and not self.is_downloaded(nxt[1]) and not self.is_offline():
            self.get_stream_future(nxt[1])

    def next_song(self, auto=False):
        """auto=True: şarkı bitince (tekrar ayarına uyar); elle ⏭ basınca liste sonunda başa sarar."""
        nxt = self.peek_next(wrap=not auto)
        if nxt is None:
            if auto and self.play_items:
                self.stop()
                self.np_sub.configure(text="Liste bitti", text_color=MUTED)
            return
        kind, it, idx = nxt
        self._shuf_pick = None
        if kind == "queue":
            self.queue.pop(0)
            self.play_items.insert(self.play_idx + 1, it)
            self.play_idx += 1
            if self.cur_view == QUEUE:
                self.fill_tree()
        else:
            self.play_idx = idx
        self.play_current()

    def prev_song(self):
        if not self.play_items and not self.history:
            return
        if self.player.get_time() > 4000:      # 4 sn'den fazla geçtiyse şarkıyı başa sar
            self.player.set_time(0)
            return
        if self.history:                       # karışık modda da gerçekten önceki şarkıya döner
            it = self.history.pop()
            self.play_idx = max(0, self.play_idx)
            self.play_items.insert(self.play_idx, it)
            self.play_current(push=False)
        elif self.play_items:
            self.play_idx = (self.play_idx - 1) % len(self.play_items)
            self.play_current(push=False)

    # ------------------------------------------------------------ kapak
    def cover_image(self, vid, keep=False):
        if not vid:
            return None
        f = COVER_DIR / f"{vid}.jpg"
        try:
            if f.exists():
                return Image.open(f).convert("RGB")
            r = requests.get(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", timeout=8)
            if r.status_code != 200:
                return None
            im = Image.open(io.BytesIO(r.content)).convert("RGB")
            w, h = im.size
            side = int(h * 0.75)             # 4:3 karedeki siyah bantları at, ortadan kare kes
            left, top = (w - side) // 2, (h - side) // 2
            im = im.crop((left, top, left + side, top + side))
            if keep:
                COVER_DIR.mkdir(parents=True, exist_ok=True)
                im.save(f, "JPEG", quality=88)
            return im
        except Exception as ex:
            print("Kapak alınamadı:", ex)
            return None

    def fetch_cover(self, vid, token):
        im = self.cover_image(vid)
        if im is None:
            return
        col = dominant_color(im)
        self.ui(lambda: self.set_cover(im, token, col))

    def set_cover(self, im, token, col=None):
        if token == self.token:
            if im is not None and self.cfg.get("anim", "Tam") == "Tam":
                self._cover_fade = {"prev": getattr(self, "_cover_prev", None), "t0": time.time()}
            self.cover = im
            if col:
                self.dyn_target = tuple(col)         # animasyon renkleri yumuşakça kapağın rengine geçer
                self.apply_cover_neon(col)
            self.np_cv.schedule(5)

    # ------------------------------------------------------------ kontroller
    def toggle_play(self):
        st = self.player.get_state()
        if st in (vlc.State.Playing, vlc.State.Buffering, vlc.State.Opening):
            self.player.pause()
            self.play_btn.configure(text="▶")
        elif st == vlc.State.Paused:
            self.player.play()
            self.play_btn.configure(text="⏸")
        elif self.play_items:
            self.play_current(push=False)
        else:
            self.play_selected()

    def stop(self):
        self.token += 1
        self.player.stop()
        self.play_btn.configure(text="▶")
        self.np_sub.configure(text="Durduruldu", text_color=MUTED)
        self.slider.set(0)
        self.time_lbl.configure(text="0:00")

    def update_shuffle_btn(self):
        self.shuffle_btn.configure(text_color=GOLD if self.shuffle else MUTED)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self._shuf_pick = None
        self.update_shuffle_btn()
        self.prefetch_next()

    def update_repeat_btn(self):
        self.repeat_btn.configure(text=("Tekrar", "Tekrar: liste", "Tekrar: 1")[self.repeat],
                                  text_color=GOLD if self.repeat else MUTED)

    def toggle_repeat(self):
        self.repeat = (self.repeat + 1) % 3          # kapalı -> liste -> tek şarkı
        self.update_repeat_btn()

    # ------------------------------------------------------------ ekolayzır ve hız
    def apply_audio(self):
        gains = EQ_PRESETS.get(self.cfg.get("eq", "Düz"))
        try:
            if not gains or not any(gains):
                self.player.set_equalizer(None)
                self._eq = None
            else:
                eq = vlc.AudioEqualizer()
                eq.set_preamp(-0.6 * max(gains))      # yükseltilen bantlarda bozulma olmasın
                for i, g in enumerate(gains):
                    eq.set_amp_at_index(float(g), i)
                self.player.set_equalizer(eq)
                self._eq = eq                          # referansı tut
            self.player.set_rate(self.rate)
        except Exception as ex:
            print("Ses ayarı uygulanamadı:", ex)

    def on_volume(self, v):
        self.player.audio_set_volume(int(v))
        if self.cfg.get("song_vol_on") and self.now_item is not None:
            d = self.cfg.setdefault("song_vol", {})
            d[key_of(self.now_item)] = int(float(v))
            if len(d) > 500:
                d.pop(next(iter(d)))

    def on_seek_drag(self, v):
        length = self.player.get_length()
        if self._seeking and length > 0:
            self.time_lbl.configure(text=self.fmt(int(length * float(v))))

    def on_seek_release(self, e):
        self._seeking = False
        if self.player.get_length() > 0:
            self.player.set_position(float(self.slider.get()))

    def update_progress(self):
        try:
            length = self.player.get_length()
            if length > 0 and not self._seeking:
                pos = self.player.get_position()
                self.slider.set(max(0.0, min(pos, 1.0)))
                self.time_lbl.configure(text=self.fmt(int(length * pos)))
                self.total_lbl.configure(text=self.fmt(length))
                cur = self.play_items[self.play_idx] if 0 <= self.play_idx < len(self.play_items) else None
                if cur is not None and not cur.get("dur"):   # listedeki süre sütununu çalarken doldur
                    cur["dur"] = length / 1000
                    self.mark_playing()
            if self.sleep_at and time.time() >= self.sleep_at:   # uyku zamanlayıcısı bitti
                self.sleep_at = None
                self._sleep_min = None
                self.stop()
                self.sleep_btn.configure(text="Uyku: kapalı")
                self.flash("İyi geceler, çalma durduruldu", 6000)
            state = self.player.get_state()
            if self.player.is_playing():
                self.failed_streak = 0
                self.play_btn.configure(text="⏸")
                if abs(self.player.get_rate() - self.rate) > 0.01:      # hız ayarı yeni şarkıda da geçerli kalsın
                    self.player.set_rate(self.rate)
            if state == vlc.State.Ended:
                self.play_current(push=False) if self.repeat == 2 and self.play_items else self.next_song(auto=True)
            elif state == vlc.State.Error:   # bozuk/süresi dolmuş link
                self.failed_streak += 1
                if self.failed_streak < 5 and len(self.play_items) > 1:
                    self.np_sub.configure(text="Çalma hatası, sonrakine geçiliyor...", text_color=ACCENT)
                    self.next_song(auto=True)
                else:
                    self.player.stop()
                    self.np_sub.configure(text="Çalınamadı", text_color=ACCENT)
        except Exception:
            traceback.print_exc()
        finally:
            self.after(500, self.update_progress)

    def cycle_sleep(self):
        opts = [None, 15, 30, 60]
        nxt = opts[(opts.index(self._sleep_min) + 1) % len(opts)]
        self._sleep_min = nxt
        self.sleep_at = time.time() + nxt * 60 if nxt else None
        self.sleep_btn.configure(text=f"Uyku: {nxt} dk" if nxt else "Uyku: kapalı")
        self.flash(f"{nxt} dk sonra müzik durur" if nxt else "Uyku zamanlayıcısı kapatıldı")

    # ------------------------------------------------------------ şarkı sözleri
    def set_lyrics(self, text):
        self.sync, self.sync_idx = [], -1
        self.lyr_lines = text.splitlines() or [text]
        self.lyr_pos = self.lyr_manual = 0.0
        self.lyr_sig = self.lyr_cum_key = None

    def _lyr_wheel(self, e):
        if not self.sync:                              # senkronsuz sözlerde fare tekerleğiyle kaydır
            top = float(max(0, len(self.lyr_lines) - 1))
            self.lyr_manual = max(0.0, min(top, self.lyr_manual + (-1.5 if e.delta > 0 else 1.5)))

    def lyr_tick(self, t):
        """Sağ alttaki söz kutusunu çizer: çalan satır ortada, altın/turuncu renkte; çevresi giderek soluklaşır."""
        cv = self.lyr_cv
        W, H = cv.winfo_width(), cv.winfo_height()
        if W < 60 or H < 60:
            return
        lines, S = self.lyr_lines, self.S
        synced = bool(self.sync)
        target = float(max(0, self.sync_idx)) if synced else self.lyr_manual
        moved = abs(target - self.lyr_pos) > 0.004
        self.lyr_pos = target if not moved else self.lyr_pos + (target - self.lyr_pos) * 0.16
        sig = (id(lines), len(lines), W, H, synced)
        if not moved and sig == self.lyr_sig:
            return
        self.lyr_sig = sig
        wrap = int(W * 0.88)
        fam = BODY_FONT
        if self.lyr_cum_key != sig:                    # her satırın (kaydırılmış) yüksekliği bir kez hesaplanır
            fnt = tkfont.Font(family=fam, size=-S(18), weight="bold")
            ls, cum, acc = fnt.metrics("linespace"), [], 0.0
            for ln in lines:
                n = max(1, int(math.ceil(fnt.measure(ln or "♪") / max(1, wrap))))
                h = n * ls + S(10)
                cum.append(acc + h / 2)
                acc += h
            self.lyr_cum, self.lyr_cum_key = cum, sig
        cum = self.lyr_cum
        if not cum:
            return
        p = max(0.0, min(float(len(cum) - 1), self.lyr_pos))
        i0 = int(p)
        i1 = min(len(cum) - 1, i0 + 1)
        cy = cum[i0] + (cum[i1] - cum[i0]) * (p - i0)
        cv.delete("fg")
        for i, ln in enumerate(lines):
            y = H / 2 + cum[i] - cy
            if y < -S(60) or y > H + S(60):
                continue
            if synced:
                d = abs(i - self.lyr_pos)
                emph = max(0.0, 1.0 - d)
                k = max(0.0, 1.0 - d / 3.6)
                base = _mix_rgb((235, 231, 255), NEON2_RGB, emph)
                col = _hex(_mix_rgb(PANEL_RGB, base, k))
                fnt = self.F(fam, 14 + 4 * emph, "bold" if emph > 0.5 else "normal")
            else:
                edge = max(0.0, 1.0 - max(0.0, abs(y - H / 2) - H * 0.30) / (H * 0.22))
                col = _hex(_mix_rgb(PANEL_RGB, (207, 201, 245), edge))
                fnt = self.F(fam, 14)
            cv.create_text(W // 2, y, text=ln or ("♪" if synced else ""), width=wrap, justify="center",
                           fill=col, font=fnt, tags="fg")

    def show_lyrics(self, entry):
        """entry = {"plain": düz metin, "synced": [(saniye, satır), ...]}"""
        if entry["synced"]:
            self.set_lyrics("\n".join(t or "♪" for _, t in entry["synced"]))
            self.sync = entry["synced"]
            self.lyr_lines = [t or "♪" for _, t in entry["synced"]]
        else:
            self.set_lyrics(entry["plain"])

    def _lyric_tick(self):
        """Çalan satırı altın renkle işaretler ve görünür kalması için kaydırır."""
        try:
            if self.sync and self.player.is_playing():
                t = self.player.get_time() / 1000.0
                off = self.cfg.get("lyr_off", {}).get(key_of(self.now_item), 0.0) if self.now_item else 0.0
                idx = -1
                for i, (ts, _) in enumerate(self.sync):
                    if ts <= t + 0.15 + off:
                        idx = i
                    else:
                        break
                if idx != self.sync_idx:
                    self.sync_idx = idx
        except Exception as ex:
            print("Söz takibi hatası:", ex)
        finally:
            self.after(200, self._lyric_tick)

    def _lrc_search(self, **params):
        """lrclib araması: başlık (User-Agent) gönderir, geçici hatalarda 3 kez dener, liste döndürür."""
        last = None
        for attempt in range(3):
            try:
                r = requests.get("https://lrclib.net/api/search", params=params, timeout=(6, 12),
                                 headers={"User-Agent": "GardasFM/4.0 (https://lrclib.net)"})
                if r.status_code == 200:
                    data = r.json()
                    self._net_seen = time.time()           # istek geçti: internet var demektir
                    return data if isinstance(data, list) else []
                last = RuntimeError(f"HTTP {r.status_code}")
            except Exception as ex:
                last = ex
            time.sleep(0.8 * (attempt + 1))
        raise last

    def get_lyrics_entry(self, it):
        """Söz kaydını döndürür; bulunanlar sozler.json'a yazılır (internetsiz de görünür)."""
        key = key_of(it)
        entry = self.lyrics_cache.get(key)
        if entry is not None:
            return entry
        title = re.sub(r"\(.*?\)|\[.*?\]|official.*|video.*|lyrics.*|sözleri.*|audio.*", "", it["title"],
                       flags=re.I).strip()
        query = title if (it["url"] and not is_local(it)) else f"{it['artist']} {title}".strip()
        tries = [{"q": query}]
        if " - " in title:                                 # "Sanatçı - Şarkı" biçimi: ayrı alanlarla da dene
            art, trk = (x.strip() for x in title.split(" - ", 1))
            if art and trk:
                tries.append({"track_name": trk, "artist_name": art})
                tries.append({"q": trk})
        elif title:
            tries.append({"track_name": title})
        entry = {"plain": "Bu şarkının sözü bulunamadı.", "synced": [], "miss": True}
        try:
            found = False
            for n, params in enumerate(tries):
                try:
                    results = self._lrc_search(**params)
                except Exception:
                    if n == 0:
                        raise
                    continue
                results = [x for x in results if isinstance(x, dict)]
                pick = next((x for x in results if x.get("syncedLyrics")), None)
                if pick:                       # senkronlu söz varsa onu tercih et
                    synced = parse_lrc(pick["syncedLyrics"])
                    plain = pick.get("plainLyrics") or "\n".join(t for _, t in synced)
                    entry, found = {"plain": plain, "synced": synced}, True
                else:
                    pick = next((x for x in results if x.get("plainLyrics")), None)
                    if pick:
                        entry, found = {"plain": pick["plainLyrics"], "synced": []}, True
                if found:
                    break
            self.lyrics_cache[key] = entry
            if not entry.get("miss"):
                with self.cache_lock:
                    if len(self.lyrics_cache) > 400:
                        for old in list(self.lyrics_cache)[:100]:
                            self.lyrics_cache.pop(old, None)
                    save_json(LYRICS_FILE, {k: v for k, v in self.lyrics_cache.items() if not v.get("miss")})
        except Exception as ex:
            print("Söz hatası:", repr(ex))
            entry = {"plain": "Sözler şu an alınamadı, birazdan otomatik tekrar denenecek...", "synced": [],
                     "err": True}
        return entry

    def fetch_lyrics(self, it, token):
        entry = self.get_lyrics_entry(it)
        self.ui(lambda: self.show_lyrics(entry) if token == self.token else None)
        for _ in range(4):                                 # bağlantı hatasıysa arka planda tekrar dene
            if not entry.get("err"):
                return
            time.sleep(6)
            if token != self.token:
                return
            entry = self.get_lyrics_entry(it)
            if not entry.get("err"):
                self.ui(lambda e=entry: self.show_lyrics(e) if token == self.token else None)
                return
        if token == self.token:
            fin = {"plain": "Sözler alınamadı (internet yok olabilir).", "synced": []}
            self.ui(lambda: self.show_lyrics(fin) if token == self.token else None)

    # ------------------------------------------------------------ kısayollar, güncelleme, açılış
    def bind_keys(self):
        def typing():
            try:
                return getattr(self, "_login_wall", None) is not None or isinstance(self.focus_get(), (tk.Entry, tk.Text))
            except Exception:
                return False

        def vol_step(d):
            v = max(0, min(100, int(self.vol.get()) + d))
            self.vol.set(v)
            self.player.audio_set_volume(v)

        def on_space(e):
            if typing():
                return None          # arama kutusuna yazarken boşluk normal çalışsın
            self.toggle_play()
            return "break"

        def go_search(e):
            self.show_view(SEARCH)
            self.after(120, self.search_entry.focus_set)

        self.bind_all("<space>", on_space)
        self.bind_all("<Control-Right>", lambda e: self.next_song())
        self.bind_all("<Control-Left>", lambda e: self.prev_song())
        self.bind_all("<Control-Up>", lambda e: vol_step(10))
        self.bind_all("<Control-Down>", lambda e: vol_step(-10))
        self.bind_all("<Control-f>", go_search)

        def key(fn):
            def h(e):
                if typing():
                    return None
                fn()
                return "break"
            return h
        self.bind_all("<l>", key(self.open_lyrics_full))
        self.bind_all("<m>", key(self.open_mini))
        self.bind_all("<q>", key(lambda: self.enqueue()))
        self.bind_all("<d>", key(lambda: self.download()))
        self.bind_all("<f>", key(lambda: self.toggle_fav()))
        self.bind_all("<F1>", lambda e: self.show_help())
        self.bind_all("<F2>", lambda e: self.open_webui())
        self.bind_all("<r>", key(self.radio_from_current))
        self.bind_all("<bracketleft>", key(lambda: self.shift_lyrics(-0.5)))
        self.bind_all("<bracketright>", key(lambda: self.shift_lyrics(0.5)))

    # ------------------------------------------------------------ 5.0: açılış kontrolü, yazı tipi, animasyon seviyesi
    def boot_ok(self):
        """Açılış sorunsuz bitti: güvenli güncelleme işaretini kaldırır; geri dönüş olduysa haber verir."""
        try:
            if _MARK.exists():
                _MARK.unlink()
            if _NOTICE.exists():
                info = json.loads(_NOTICE.read_text(encoding="utf-8"))
                _NOTICE.unlink()
                bad = str(info.get("bozuk", "?"))
                self.cfg["bad_version"] = bad
                self.save_cfg()
                messagebox.showwarning(
                    "Gardaş FM",
                    f"v{bad} açılırken hata verdi, bu yüzden otomatik olarak v{APP_VERSION} sürümüne geri dönüldü.\n\n"
                    "Favorilerin ve ayarların yerinde. Bozuk sürüm 'gardas_fm.py.bozuk' dosyasında duruyor, "
                    "hata için o dosyayı ve gardas_fm.log'u gönderebilirsin.", parent=self)
        except Exception:
            traceback.print_exc()

    def pick_fonts(self):
        """Başlık yazı tipi: bilgisayarda varsa Bahnschrift (Windows 10+), yoksa Segoe UI Semibold."""
        global HEAD_FONT, _APP
        _APP = self
        try:
            fams = {f.lower(): f for f in tkfont.families(self)}
            for cand in ("Bahnschrift", "Segoe UI Semibold"):
                if cand.lower() in fams:
                    HEAD_FONT = fams[cand.lower()]
                    return
        except Exception:
            traceback.print_exc()

    def view_anim_p(self):
        """Sayfa değişince başlığın süzülerek gelmesi için 0..1 ilerleme (Tam seviyede)."""
        if self.cfg.get("anim", "Tam") != "Tam" or self.cur_view in (HOME, SEARCH):
            return 1.0
        return _ease((time.time() - getattr(self, "view_t0", 0.0)) / 0.4)

    # ------------------------------------------------------------ 5.0: etiketler
    def item_tags(self, it):
        return list(self.cfg.get("tags", {}).get(key_of(it), []))

    def title_text(self, it, favs):
        tg = self.cfg.get("tags", {}).get(key_of(it))
        return ("♥ " if key_of(it) in favs else "") + it["title"] + ("   " + " ".join("#" + t for t in tg) if tg else "")

    def all_tags(self):
        """Kullanılan etiketler, en çok kullanılandan başlayarak."""
        cnt = {}
        for tags in self.cfg.get("tags", {}).values():
            for t in tags:
                cnt[t] = cnt.get(t, 0) + 1
        return [t for t, _ in sorted(cnt.items(), key=lambda x: (-x[1], x[0]))]

    def tagged_items(self, tag):
        out, seen = [], set()
        tags = self.cfg.get("tags", {})
        for c in [*NAV, MIX, *self.pl_keys, RECENT]:
            for it in self.lists.get(c, []):
                k = key_of(it)
                if k not in seen and tag in tags.get(k, []):
                    seen.add(k)
                    out.append(it)
        return out

    def refresh_tag_list(self, name):
        tag = name.split(":", 1)[1]
        self.lists[name] = self.tagged_items(tag)
        TAGLINES[name] = "Etiketli şarkılar"

    def edit_tags(self, it):
        k = key_of(it)
        win = GToplevel(self)
        win.title("Etiketler")
        win.geometry("400x200")
        win.configure(fg_color=PANEL)
        win.transient(self)
        win.after(150, win.lift)
        ctk.CTkLabel(win, text=(it["title"] or "")[:42], font=ctk.CTkFont(HEAD_FONT, 16, "bold"),
                     text_color=GOLD).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(win, text="Etiketleri virgülle ayır (örnek: araba, spor, gece)", text_color=MUTED,
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=22)
        ent = ctk.CTkEntry(win, width=356, height=38)
        ent.pack(padx=22, pady=12)
        ent.insert(0, ", ".join(self.item_tags(it)))

        def save():
            out = []
            for part in ent.get().split(","):
                t = re.sub(r"[#\s]+", " ", part).strip().lower()[:24]
                if t and t not in out:
                    out.append(t)
            tags = self.cfg.setdefault("tags", {})
            if out[:8]:
                tags[k] = out[:8]
            else:
                tags.pop(k, None)
            self.save_cfg()
            win.destroy()
            if self.cur_view.startswith("etiket:"):
                self.refresh_tag_list(self.cur_view)
                self.fill_tree()
            else:
                self.mark_playing()
            self.side_cv.schedule(1)
            self.flash("Etiketler kaydedildi" if out else "Etiketler silindi")
        ent.bind("<Return>", lambda e: save())
        ctk.CTkButton(win, text="Kaydet", height=36, corner_radius=18, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=save).pack(anchor="e", padx=22)
        win.after(250, ent.focus_set)

    # ------------------------------------------------------------ 5.0: ruh haline göre mix
    def play_mood(self, name):
        mood = next((m for m in MOODS if m[0] == name), None)
        if mood is None:
            return
        _n, _sub, cats, tag = mood
        pool, seen = [], set()

        def add(it):
            k = key_of(it)
            if k not in seen and self.playable(it):
                seen.add(k)
                pool.append(it)
        src = [c for c in cats if c in self.lists] or list(NAV)
        for c in src:
            for it in self.lists.get(c, []):
                add(it)
        for it in self.tagged_items(tag):
            add(it)
        if not pool:
            self.flash("Bu karışık için şarkı yok (çevrimdışıysan önce şarkı indir)", 5000)
            return
        random.shuffle(pool)
        items = pool[:25]
        self.shuffle = False
        self.update_shuffle_btn()
        self.start_play(items, 0)
        self.flash(f"{name} karışığı hazır: {len(items)} şarkı", 4000)

    # ------------------------------------------------------------ 5.0: şarkı değişince bildirim kartı
    def _toast_if(self, tok):
        self._toast_after = None
        if tok != self.token or not self.cfg.get("notify", True):
            return
        try:
            if not self.player.is_playing():
                return
            if self.state() != "iconic" and self.winfo_viewable() and self.focus_displayof() is not None:
                return                      # uygulama önde ve odakta: bildirime gerek yok
        except Exception:
            return
        if 0 <= self.play_idx < len(self.play_items):
            self.show_song_toast(self.play_items[self.play_idx])

    def show_song_toast(self, it):
        S, F = self.S, self.F
        old = getattr(self, "_toast_win", None)
        if old is not None:
            try:
                old.destroy()
            except Exception:
                pass
        W, H = S(370), S(96)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y_end = sw - W - S(24), sh - H - S(80)
        lvl = self.cfg.get("anim", "Tam")
        win = tk.Toplevel(self)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.0 if lvl == "Tam" else 0.97)
        win.configure(bg=ACCENT)
        win.geometry(f"{W}x{H}+{x}+{y_end + (S(26) if lvl == 'Tam' else 0)}")
        self._toast_win = win
        body = tk.Frame(win, bg=PANEL)
        body.pack(fill="both", expand=True, padx=2, pady=2)
        src = self.cover if self.cover is not None else self.logo_pil()
        if src is not None:
            try:
                th = ImageOps.fit(src.convert("RGB"), (S(72), S(72)), method=Image.Resampling.BILINEAR)
                win._ph = ImageTk.PhotoImage(th)
                tk.Label(body, image=win._ph, bg=PANEL, bd=0).pack(side="left", padx=(12, 12), pady=10)
            except Exception:
                traceback.print_exc()
        col = tk.Frame(body, bg=PANEL)
        col.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Label(col, text="ŞİMDİ ÇALIYOR", bg=PANEL, fg=ACCENT, font=F(BODY_FONT, 10, "bold"),
                 anchor="w").pack(fill="x", pady=(14, 0))
        tk.Label(col, text=(it.get("title") or "")[:40], bg=PANEL, fg=TEXT, font=F(HEAD_FONT, 14, "bold"),
                 anchor="w", justify="left").pack(fill="x")
        tk.Label(col, text=(it.get("artist") or "")[:40], bg=PANEL, fg=SOFT, font=F(BODY_FONT, 12),
                 anchor="w").pack(fill="x")

        def open_app(_e=None):
            try:
                win.destroy()
            except Exception:
                pass
            self.show_window()
        win.bind("<Button-1>", open_app)

        def step(i, phase):
            try:
                if not win.winfo_exists():
                    return
                if phase == "in":
                    p = _ease(i / 12.0)
                    win.geometry(f"{W}x{H}+{x}+{int(y_end + (1 - p) * S(26))}")
                    win.attributes("-alpha", 0.97 * p)
                    if i < 12:
                        self.after(16, lambda: step(i + 1, "in"))
                    else:
                        self.after(4200, lambda: step(0, "out"))
                else:
                    p = _ease(i / 10.0)
                    win.geometry(f"{W}x{H}+{x}+{int(y_end + p * S(10))}")
                    win.attributes("-alpha", 0.97 * (1 - p))
                    if i < 10:
                        self.after(16, lambda: step(i + 1, "out"))
                    else:
                        win.destroy()
            except Exception:
                pass
        if lvl == "Tam":
            step(0, "in")
        else:
            self.after(4500, lambda: win.destroy() if win.winfo_exists() else None)

    # ------------------------------------------------------------ 5.2: canlı kataloglar (YouTube'dan)
    def ensure_live(self, name, force=False):
        """Canlı katalog ilk açılışta (ya da 3 günden eskiyse / yenile denirse) YouTube'dan yüklenir ve saklanır."""
        if name not in LIVE_CATS:
            return
        c = self.live_cache.get(name)
        if c and not force and time.time() - c.get("t", 0) < (86400 if name == "Senin için yeni" else 3 * 86400):
            return
        if name in self._live_busy:
            return
        if self.is_offline():
            self.flash("Çevrimdışı mod açık: canlı katalog yüklenemez", 5000)
            return
        self._live_busy.add(name)
        self.flash(f"{name} yükleniyor...", 12000)
        _alt, query, allow_long = LIVE_CATS[name]
        if name == "Senin için yeni":
            cnt = {}
            for it in self.lists.get(MIX, []):
                a = (it.get("artist") or "").strip()
                if a:
                    cnt[a] = cnt.get(a, 0) + 1
            arts = [a for a, _ in sorted(cnt.items(), key=lambda x: -x[1])[:4]]
            if not arts:
                self._live_busy.discard(name)
                self.flash("Önce birkaç şarkıyı favorilerine ekle, sonra yeni çıkanları getiririm", 6000)
                return
            queries = [f"ytsearch6:{a} yeni şarkı" for a in arts]
        else:
            queries = [f"ytsearch30:{query}"]

        def worker():
            items, seen = [], set()
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
                    for qq in queries:
                        info = ydl.extract_info(qq, download=False)
                        for e in info.get("entries", []):
                            dur = e.get("duration")
                            if dur and dur > 900 and not allow_long:
                                continue
                            url = e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}"
                            if url in seen:
                                continue
                            seen.add(url)
                            items.append(make_item(e.get("channel") or e.get("uploader") or "", e.get("title", "?"),
                                                   url, dur))
            except Exception as ex:
                print("Canlı katalog hatası:", ex)

            def done():
                self._live_busy.discard(name)
                if items:
                    self.live_cache[name] = {"t": time.time(), "items": items}
                    save_json(LIVE_FILE, self.live_cache)
                    self.lists[name] = items
                    if self.cur_view == name:
                        self.fill_tree()
                    self.flash(f"{name}: {len(items)} şarkı hazır", 4000)
                else:
                    self.flash("Katalog yüklenemedi, internet bağlantını kontrol et", 6000)
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------ 5.2: sol menüyü gizle / göster
    def toggle_sidebar(self):
        opened = not self.cfg.get("side_open", True)
        self.cfg["side_open"] = opened
        self.save_cfg()
        if opened:
            self.side_tab.place_forget()
            self.side_cv.grid()
            self.side_cv.schedule(1)
        else:
            self.side_cv.grid_remove()
            self.side_tab.place(x=2, y=self.S(120))
            self.side_tab.lift()
        for cv in (self.hero_cv, self.home_cv, self.list_cv):
            cv.schedule(1)

    # ------------------------------------------------------------ 5.2: arama önerileri (yazdıkça açılan liste)
    def on_search_key(self, e):
        if e.keysym in ("Up", "Down", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R",
                        "Alt_L", "Alt_R", "Left", "Right", "Home", "End"):
            return
        text = self.search_entry.get().strip()
        try:
            if self._sug_job is not None:
                self.after_cancel(self._sug_job)
        except Exception:
            pass
        self._sug_job = None
        if len(text) < 2:
            self.hide_suggestions()
            return
        self._sug_job = self.after(230, lambda: self.fetch_suggestions(text))

    def fetch_suggestions(self, text):
        self._sug_job = None
        words = fold(text).split()
        local, seen = [], set()
        for c in [*NAV, MIX, RECENT, DOWNLOADS]:
            for it in self.lists.get(c, []):
                k = key_of(it)
                if k in seen:
                    continue
                hay = fold(f"{it['artist']} {it['title']}")
                if all(w in hay for w in words):
                    seen.add(k)
                    local.append((f"{it['artist']} - {it['title']}".strip(" -"), True))
                    if len(local) >= 4:
                        break
            if len(local) >= 4:
                break
        self.show_suggestions(text, local)
        if self.is_offline():
            return

        def worker():
            out = []
            try:
                r = requests.get("https://suggestqueries.google.com/complete/search",
                                 params={"client": "firefox", "ds": "yt", "hl": "tr", "q": text}, timeout=3.5)
                data = r.json()
                out = [str(x) for x in data[1]][:6] if isinstance(data, list) and len(data) > 1 else []
            except Exception as ex:
                print("Öneriler alınamadı:", ex)
            if out:
                self.ui(lambda: self.show_suggestions(text, local + [(s, False) for s in out]))
        threading.Thread(target=worker, daemon=True).start()

    def show_suggestions(self, text, rows):
        if self.search_entry.get().strip() != text or not rows:
            if not rows:
                self.hide_suggestions()
            return
        if self.cur_view not in (SEARCH,) and not self.hero_cv.winfo_ismapped():
            return
        S, F = self.S, self.F
        if self._sug_frame is None:
            self._sug_frame = tk.Frame(self, bg=NEON2, bd=0)
            self._sug_inner = tk.Frame(self._sug_frame, bg=PANEL)
            self._sug_inner.pack(fill="both", expand=True, padx=1, pady=1)
        for w in self._sug_inner.winfo_children():
            w.destroy()
        self._sug_rows = []
        shown, seen = [], set()
        for s, is_local in rows:
            k = fold(s)
            if k in seen:
                continue
            seen.add(k)
            shown.append((s, is_local))
        for s, is_local in shown[:9]:
            lb = tk.Label(self._sug_inner, text=("♪  " if is_local else "     ") + s, anchor="w", bg=PANEL,
                          fg=GOLD if is_local else TEXT, font=F(BODY_FONT, 14), padx=14, pady=7, cursor="hand2")
            lb.pack(fill="x")
            lb.bind("<Button-1>", lambda e, q=s: self.pick_suggestion(q))
            lb.bind("<Enter>", lambda e, i=len(self._sug_rows): self.sug_select(i))
            self._sug_rows.append((s, lb))
        self._sug_idx = -1
        ex, ey = self.search_entry.winfo_rootx() - self.winfo_rootx(), self.search_entry.winfo_rooty() - self.winfo_rooty()
        width = max(S(380), self.search_entry.winfo_width() + S(36))
        self._sug_frame.place(x=max(S(8), ex - S(18)), y=ey + self.search_entry.winfo_height() + S(8), width=width)
        self._sug_frame.lift()

    def sug_select(self, i):
        self._sug_idx = i
        for j, (_s, lb) in enumerate(self._sug_rows):
            lb.configure(bg=_mix(PANEL, ACCENT, 0.30) if j == i else PANEL)

    def hide_suggestions(self):
        self._sug_idx = -1
        if self._sug_frame is not None:
            self._sug_frame.place_forget()

    def pick_suggestion(self, q):
        self.hide_suggestions()
        self.do_search(q)

    def on_search_nav(self, d):
        if self._sug_frame is None or not self._sug_frame.winfo_ismapped() or not self._sug_rows:
            return
        i = (self._sug_idx + d) % len(self._sug_rows)
        self.sug_select(i)
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, self._sug_rows[i][0])
        return "break"

    def on_search_return(self, _e=None):
        self.hide_suggestions()
        self.do_search()

    # ------------------------------------------------------------ 5.2: teşhis paketi
    def make_diag_zip(self):
        """Hata olursa gardas_fm.log ve sürüm bilgisini tek zip'e koyar (kişisel liste ve kimlik bilgisi girmez)."""
        path = filedialog.asksaveasfilename(parent=self, title="Teşhis paketini kaydet", defaultextension=".zip",
                                            initialfile=f"GardasFM_teshis_{time.strftime('%Y-%m-%d_%H%M')}.zip",
                                            filetypes=[("Zip", "*.zip")])
        if not path:
            return
        try:
            import platform
            info = (f"Gardaş FM v{APP_VERSION}\nPython {platform.python_version()} · {platform.platform()}\n"
                    f"Ekran: {self.winfo_screenwidth()}x{self.winfo_screenheight()} · pencere {self.winfo_width()}x{self.winfo_height()}\n"
                    f"Tema: {self.cfg.get('theme')} · animasyon: {self.cfg.get('anim')} · bildirim: {self.cfg.get('notify')} · "
                    f"discord: {self.cfg.get('discord')} · çevrimdışı: {self.cfg.get('offline')}\n"
                    f"Veri klasörü: {DATA_DIR}\nlogo var mı: {self.logo_pil() is not None}\n")
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("bilgi.txt", info)
                if LOG_FILE.exists():
                    zf.writestr("gardas_fm.log", LOG_FILE.read_bytes()[-400_000:])
            self.flash(f"Teşhis paketi kaydedildi: {Path(path).name}", 8000)
        except Exception as ex:
            self.flash(f"Teşhis paketi oluşturulamadı: {ex}", 8000)

    # ------------------------------------------------------------ 5.3: kapak rengi, şarkı bul, yardım
    def apply_cover_neon(self, col):
        """Neon kenarlar çalan şarkının kapak renginde parlar (Ayarlar'dan kapatılabilir)."""
        global _NEON_DYN
        try:
            new = None
            if col and self.cfg.get("cover_color", True):
                h, s_, v = colorsys.rgb_to_hsv(*[c / 255 for c in col])
                if s_ >= 0.15:
                    c1 = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h, max(s_, 0.65), max(v, 0.95)))
                    c2 = tuple(int(x * 255) for x in colorsys.hsv_to_rgb((h + 0.42) % 1.0, 0.7, 1.0))
                    new = (c1, c2)
            if new == _NEON_DYN:
                return
            _NEON_DYN = new
            for cv in (self.side_cv, self.hero_cv, self.list_cv, self.np_cv, self.bar_cv, self.home_cv):
                cv.schedule(8)
        except Exception:
            traceback.print_exc()

    def show_help(self):
        if getattr(self, "_help_win", None) is not None and self._help_win.winfo_exists():
            self._help_win.lift()
            return
        win = GToplevel(self)
        self._help_win = win
        win.title("Kısayollar")
        win.geometry("480x600")
        win.configure(fg_color=PANEL)
        win.transient(self)
        win.after(150, win.lift)
        win.bind("<Escape>", lambda e: win.destroy())
        ctk.CTkLabel(win, text="Kısayollar", font=ctk.CTkFont(HEAD_FONT, 24, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=22, pady=(18, 8))
        box = ctk.CTkFrame(win, fg_color=_mix(PANEL, "#ffffff", 0.06), corner_radius=18, border_width=1,
                           border_color=NEON2_DIM)
        box.pack(fill="x", padx=18)
        rows = [("Boşluk", "Çal / duraklat"), ("Ctrl + →  /  ←", "Sonraki / önceki şarkı"),
                ("Ctrl + ↑  /  ↓", "Sesi aç / kıs"), ("Ctrl + F", "Arama"), ("L", "Tam ekran söz modu"),
                ("M", "Mini oynatıcı"), ("Q", "Seçili şarkıyı sıraya ekle"), ("D", "Seçili şarkıyı indir"),
                ("F", "Favoriye ekle / çıkar"), ("R", "Çalan şarkıdan radyo başlat"), ("[  /  ]", "Sözler geç / erken gelsin (0.5 sn)"), ("F2", "Yeni arayüz (beta)"), ("F1", "Bu pencere"), ("Esc", "Söz modunu ve pencereleri kapat")]
        for k, d in rows:
            r = ctk.CTkFrame(box, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(r, text=k, width=130, anchor="w", text_color=GOLD,
                         font=ctk.CTkFont(BODY_FONT, 13, "bold")).pack(side="left")
            ctk.CTkLabel(r, text=d, anchor="w", text_color=TEXT, font=ctk.CTkFont(BODY_FONT, 13)).pack(side="left")
        ctk.CTkLabel(win, text="İpucu: favorilerde, listelerde ve sırada şarkıyı fareyle tutup taşıyarak sıralayabilirsin. Şarkıya sağ tıkla: etiket, listeye ekle, radyo, indir ve daha fazlası. "
                               "Sol menüyü « düğmesiyle gizleyebilirsin.",
                     text_color=SOFT, wraplength=430, justify="left",
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=22, pady=14)

    def record_audio(self, secs, loopback=True):
        """Bilgisayarın sesini (ya da mikrofonu) kaydedip WAV baytı döndürür. soundcard ilk kullanımda kendi kurulur."""
        try:
            import soundcard as sc
            import numpy as np
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "soundcard", "numpy"],
                           capture_output=True, timeout=300)
            import importlib
            importlib.invalidate_caches()
            import soundcard as sc
            import numpy as np
        rate = 44100
        if loopback:
            spk = sc.default_speaker()
            mic = sc.get_microphone(id=str(spk.name), include_loopback=True)
        else:
            mic = sc.default_microphone()
        with mic.recorder(samplerate=rate, channels=1) as rec:
            data = rec.record(numframes=rate * secs)
        pcm = (np.clip(data[:, 0], -1, 1) * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(pcm.tobytes())
        return buf.getvalue()

    def open_song_finder(self):
        if getattr(self, "_find_win", None) is not None and self._find_win.winfo_exists():
            self._find_win.lift()
            return
        win = GToplevel(self)
        self._find_win = win
        win.title("Şarkı bul")
        win.geometry("580x680")
        win.minsize(520, 560)
        win.configure(fg_color=PANEL)
        win.transient(self)
        win.after(150, win.lift)
        card_bg = _mix(PANEL, "#ffffff", 0.06)
        ctk.CTkLabel(win, text="Şarkı bul", font=ctk.CTkFont(HEAD_FONT, 24, "bold"),
                     text_color=ACCENT).pack(anchor="w", padx=22, pady=(18, 2))
        ctk.CTkLabel(win, text="Aklındaki sözü yaz ya da çalan şarkıyı dinleterek bul.", text_color=SOFT,
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=22)
        mode = ctk.CTkSegmentedButton(win, values=["Sözden bul", "Dinleyerek bul"], fg_color=BTN,
                                      selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
                                      unselected_color=BTN, unselected_hover_color="#33296b")
        mode.pack(anchor="w", padx=22, pady=12)
        pane = ctk.CTkFrame(win, fg_color="transparent")
        pane.pack(fill="x", padx=22)
        status = ctk.CTkLabel(win, text="", text_color=GOLD, wraplength=520, justify="left",
                              font=ctk.CTkFont(BODY_FONT, 12))
        status.pack(anchor="w", padx=22, pady=(8, 4))
        res = ctk.CTkScrollableFrame(win, fg_color=card_bg, corner_radius=16, border_width=1, border_color=NEON2_DIM)
        res.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        def clear_results():
            for w in res.winfo_children():
                w.destroy()

        def add_row(it, note=""):
            r = ctk.CTkFrame(res, fg_color="transparent")
            r.pack(fill="x", padx=8, pady=4)
            ctk.CTkButton(r, text="Çal", width=54, height=32, corner_radius=16, fg_color=ACCENT,
                          hover_color=ACCENT_HOVER, font=ctk.CTkFont(BODY_FONT, 12, "bold"),
                          command=lambda: self.start_play([it], 0)).pack(side="right", padx=(8, 0))
            ctk.CTkLabel(r, text=(note + (it["title"] or ""))[:70], anchor="w", justify="left", text_color=TEXT,
                         wraplength=380, font=ctk.CTkFont(BODY_FONT, 13)).pack(side="left", fill="x", expand=True)
            if it.get("artist"):
                ctk.CTkLabel(r, text=it["artist"][:28], anchor="e", text_color=MUTED,
                             font=ctk.CTkFont(BODY_FONT, 11)).pack(side="right")

        # ---- sözden bul
        p1 = ctk.CTkFrame(pane, fg_color="transparent")
        lyr_box = ctk.CTkTextbox(p1, height=92, corner_radius=14, fg_color=card_bg, border_width=1,
                                 border_color=NEON2_DIM, font=ctk.CTkFont(BODY_FONT, 13))
        lyr_box.pack(fill="x")
        ctk.CTkLabel(p1, text="Şarkıdan hatırladığın birkaç kelimeyi yaz. Sonuçlar YouTube aramasından gelir, "
                              "kesin bulma garantisi yok ama genelde işe yarar.", text_color=MUTED, wraplength=520,
                     justify="left", font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", pady=(6, 6))

        def find_lyrics():
            q = lyr_box.get("1.0", "end").strip()
            if len(q) < 6:
                status.configure(text="Biraz daha uzun bir söz yaz (en az 6 harf).")
                return
            if self.is_offline():
                status.configure(text="Çevrimdışı mod açık, arama yapılamaz.")
                return
            status.configure(text="Aranıyor...")
            clear_results()

            def worker():
                items, seen = [], set()
                try:
                    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
                        for qq in (f"{q} şarkı sözleri", f"\"{q}\" lyrics"):
                            info = ydl.extract_info(f"ytsearch6:{qq}", download=False)
                            for e in info.get("entries", []):
                                url = e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}"
                                if url in seen:
                                    continue
                                seen.add(url)
                                items.append(make_item(e.get("channel") or e.get("uploader") or "",
                                                       e.get("title", "?"), url, e.get("duration")))
                except Exception as ex:
                    print("Sözden arama hatası:", ex)

                def done():
                    if not win.winfo_exists():
                        return
                    clear_results()
                    if items:
                        status.configure(text=f"{len(items)} olası şarkı bulundu. Doğru olanı seçip Çal'a bas.")
                        for it in items[:12]:
                            add_row(it)
                    else:
                        status.configure(text="Sonuç gelmedi. Sözü değiştirip tekrar dene ya da internetini kontrol et.")
                self.ui(done)
            threading.Thread(target=worker, daemon=True).start()
        ctk.CTkButton(p1, text="Şarkıyı bul", height=38, corner_radius=19, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      font=ctk.CTkFont(BODY_FONT, 13, "bold"), command=find_lyrics).pack(anchor="w")

        # ---- dinleyerek bul
        p2 = ctk.CTkFrame(pane, fg_color="transparent")
        src_var = ctk.StringVar(value="Bilgisayarın sesi")
        ctk.CTkLabel(p2, text="Ses kaynağı", text_color=SOFT, font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w")
        ctk.CTkSegmentedButton(p2, values=["Bilgisayarın sesi", "Mikrofon"], variable=src_var, fg_color=BTN,
                               selected_color=ACCENT, selected_hover_color=ACCENT_HOVER, unselected_color=BTN,
                               unselected_hover_color="#33296b").pack(anchor="w", pady=(4, 8))
        ctk.CTkLabel(p2, text="Şarkıyı çal ve butona bas: 12 saniye dinleyip tanır. Şarkı tanıma için AudD "
                              "anahtarı gerekir (Ayarlar > Sistem > Şarkı bulma).", text_color=MUTED, wraplength=520,
                     justify="left", font=ctk.CTkFont(BODY_FONT, 11)).pack(anchor="w", pady=(0, 8))
        listen_btn = ctk.CTkButton(p2, text="Dinlemeye başla", height=38, corner_radius=19, fg_color=ACCENT,
                                   hover_color=ACCENT_HOVER, font=ctk.CTkFont(BODY_FONT, 13, "bold"))
        listen_btn.pack(anchor="w")

        def listen():
            token = (self.cfg.get("audd_token") or "").strip()
            if not token:
                status.configure(text="Önce Ayarlar > Sistem > Şarkı bulma bölümüne AudD anahtarını yapıştır (audd.io).")
                return
            if self.is_offline():
                status.configure(text="Çevrimdışı mod açık, şarkı tanınamaz.")
                return
            listen_btn.configure(state="disabled")
            clear_results()
            status.configure(text="Dinleniyor... 12 saniye. Şarkı çalarken bekle.")
            loop = src_var.get() == "Bilgisayarın sesi"

            def worker():
                found, err = None, None
                try:
                    wav = self.record_audio(12, loopback=loop)
                    self.ui(lambda: status.configure(text="Şarkı aranıyor...") if win.winfo_exists() else None)
                    r = requests.post("https://api.audd.io/", data={"api_token": token},
                                      files={"file": ("kayit.wav", wav, "audio/wav")}, timeout=45)
                    data = r.json()
                    if data.get("status") == "success":
                        found = data.get("result")
                    else:
                        err = (data.get("error") or {}).get("error_message", "servis hatası")
                except Exception as ex:
                    print("Dinleyerek bulma hatası:", ex)
                    err = f"kayıt ya da bağlantı sorunu ({ex})"

                def done():
                    if not win.winfo_exists():
                        return
                    listen_btn.configure(state="normal")
                    clear_results()
                    if found and found.get("title"):
                        status.configure(text="Bulundu!")
                        add_row(make_item(found.get("artist") or "", found["title"]), note="")
                    elif err:
                        status.configure(text=f"Olmadı: {err}. Sorun sürerse Ayarlar > Hakkında > Teşhis paketini gönder.")
                    else:
                        status.configure(text="Şarkı tanınamadı. Sesi biraz aç, şarkının net bir yerinde tekrar dene.")
                self.ui(done)
            threading.Thread(target=worker, daemon=True).start()
        listen_btn.configure(command=listen)

        def on_mode(v):
            p1.pack_forget()
            p2.pack_forget()
            (p1 if v == "Sözden bul" else p2).pack(fill="x")
            clear_results()
            status.configure(text="")
        mode.configure(command=on_mode)
        mode.set("Sözden bul")
        on_mode("Sözden bul")

    # ------------------------------------------------------------ 5.5: radyo modu
    @staticmethod
    def yt_id_of(it):
        m = re.search(r"(?:v=|youtu\.be/|/shorts/)([\w-]{11})", it.get("url") or "")
        return m.group(1) if m else None

    def radio_fetch(self, seed):
        """YouTube'un 'Mix' (radyo) listesinden seed şarkıya benzer şarkıları getirir."""
        vid = self.yt_id_of(seed) or (self.id_cache.get(key_of(seed)) or {}).get("id")
        opts = {"quiet": True, "extract_flat": True, "skip_download": True, "playlistend": 30}
        with yt_dlp.YoutubeDL(opts) as ydl:
            if not vid:
                info = ydl.extract_info(f"ytsearch1:{seed['artist']} {seed['title']}", download=False)
                ents = info.get("entries") or []
                if not ents:
                    return []
                vid = ents[0].get("id")
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}&list=RD{vid}", download=False)
        out, seen = [], {vid}
        for e in info.get("entries") or []:
            eid = e.get("id")
            if not eid or eid in seen:
                continue
            dur = e.get("duration")
            if dur and dur > 900:
                continue
            seen.add(eid)
            out.append(make_item(e.get("channel") or e.get("uploader") or "", e.get("title", "?"),
                                 e.get("url") or f"https://www.youtube.com/watch?v={eid}", dur))
        return out

    def radio_from_current(self):
        if self.now_item is None:
            self.flash("Önce bir şarkı çal, radyo ondan başlasın", 5000)
            return
        self.radio_start(self.now_item)

    def radio_start(self, seed):
        if self.is_offline():
            self.flash("Radyo için internet gerekir (çevrimdışı mod açık)", 5000)
            return
        if getattr(self, "_radio_busy", False):
            return
        self._radio_busy = True
        self.flash(f"Radyo hazırlanıyor: {seed['title'][:40]}...", 12000)
        playing_now = (self.now_item is not None and key_of(self.now_item) == key_of(seed)
                       and self.player.get_state() in (vlc.State.Playing, vlc.State.Paused, vlc.State.Buffering))

        def worker():
            items = []
            try:
                items = self.radio_fetch(seed)
            except Exception as ex:
                print("Radyo hatası:", ex)

            def done():
                self._radio_busy = False
                if not items:
                    self.flash("Radyo başlatılamadı, internet bağlantını kontrol et", 6000)
                    return
                self.shuffle = False
                self.update_shuffle_btn()
                if playing_now:                              # çalan şarkı kesilmeden, devamı radyoya döner
                    self.play_items, self.play_idx = [seed] + items, 0
                    self._shuf_pick = None
                    self.mark_playing()
                else:
                    self.start_play([seed] + items, 0)
                self.radio_on = True
                self._radio_seen = {i.get("url") for i in items}
                self.flash(f"Radyo açık: {seed['title'][:36]} ve benzerleri", 5000)
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    def radio_check(self):
        """Radyo açıkken sıra azalınca (son 4 şarkı) çalan şarkıya benzer yenilerini listeye ekler."""
        if not getattr(self, "radio_on", False) or getattr(self, "_radio_busy", False):
            return
        if len(self.play_items) - self.play_idx > 4 or not (0 <= self.play_idx < len(self.play_items)):
            return
        cur = self.play_items[self.play_idx]
        self._radio_busy = True

        def worker():
            items = []
            try:
                items = self.radio_fetch(cur)
            except Exception as ex:
                print("Radyo uzatma hatası:", ex)

            def done():
                self._radio_busy = False
                new = [i for i in items if i.get("url") not in self._radio_seen]
                for i in new:
                    self._radio_seen.add(i.get("url"))
                if new and self.radio_on:
                    self.play_items.extend(new)
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------ 5.5: şarkılar arası yumuşak geçiş
    def fade_tick(self):
        """Şarkı bitmeden ses azalır, yeni şarkı yavaşça açılır (Ayarlar > Sistem > Ses ve geçiş)."""
        secs = float(self.cfg.get("fade", 0) or 0)
        try:
            base = int(self.vol.get())
            self._wu_vol = base                          # yeni arayüz (başka iş parçacığı) için ses değeri
            if secs <= 0:
                if getattr(self, "_fade_last", None) is not None:
                    self.player.audio_set_volume(base)
                    self._fade_last = None
                return
            if self.player.get_state() != vlc.State.Playing:
                return
            length, cur = self.player.get_length(), self.player.get_time()
            f = 1.0
            if length > secs * 3000 and cur >= 0:
                f = min(f, max(0.0, (length - cur) / (secs * 1000)))        # bitişe doğru azal
                f = min(f, max(0.0, cur / (secs * 700)))                    # başlangıçta yavaş aç
            if f >= 1.0:
                if getattr(self, "_fade_last", None) is not None:       # geçiş bitti: normal sese dön
                    self.player.audio_set_volume(base)
                    self._fade_last = None
                return
            vol = int(base * f)
            if vol != getattr(self, "_fade_last", None):
                self.player.audio_set_volume(vol)
                self._fade_last = vol
        except Exception:
            pass

    # ------------------------------------------------------------ 5.5: sürükle-bırak sıralama
    def _reorderable(self):
        return self.cur_view in (MIX, QUEUE) or self.cur_view in self.pl_keys

    def _drag_press(self, e):
        iid = self.tree.identify_row(e.y)
        ok = iid and self._reorderable() and self.tree.identify_region(e.x, e.y) == "cell"
        self._drag = {"iid": iid, "moved": False} if ok else None

    def _drag_motion(self, e):
        d = getattr(self, "_drag", None)
        if d and self.tree.identify_row(e.y) not in ("", d["iid"]):
            d["moved"] = True
            self.tree.configure(cursor="fleur")

    def _drag_release(self, e):
        d, self._drag = getattr(self, "_drag", None), None
        self.tree.configure(cursor="")
        if not d or not d["moved"]:
            return
        dst = self.tree.identify_row(e.y)
        if not dst or dst == d["iid"]:
            return
        try:
            i, j = int(d["iid"]), int(dst)
        except ValueError:
            return
        lst = self.lists.get(self.cur_view)
        if lst is None or not (0 <= i < len(lst)) or not (0 <= j < len(lst)):
            return
        lst.insert(j, lst.pop(i))
        if self.cur_view == MIX:
            self.save_mix()
        elif self.cur_view in self.pl_keys:
            self.save_playlists()
        self.fill_tree()
        if self.tree.exists(str(j)):
            self.tree.selection_set(str(j))
            self.tree.see(str(j))
        self.flash("Sıra değişti", 2500)

    # ------------------------------------------------------------ 6.0: profil ve Discord ile giriş
    def profile(self):
        return self.cfg.get("profile") or {}

    def founder_of(self, uid=None):
        uid = str(uid if uid is not None else self.profile().get("id", ""))
        return next((f for f in FOUNDERS if f[2] and f[2] == uid), None)

    def profile_name(self):
        p = self.profile()
        if not p:
            return "Dinleyici"
        f = self.founder_of()
        return f"{f[0]} ({f[1]})" if f else (p.get("name") or "Dinleyici")

    def profile_status(self):
        if not self.profile():
            return "Giriş yapılmadı", MUTED
        if self.founder_of():
            return "★ Kurucu · doğrulanmış", GOLD
        if GUILD_ID and self.profile().get("ok"):
            return "✔ Doğrulanmış üye", NEON2
        return "Doğrulanmamış", SOFT

    def avatar_ctk(self, size):
        try:
            if AVATAR_FILE.exists() and self.profile():
                im = Image.open(AVATAR_FILE).convert("RGBA").resize((size * 2, size * 2), Image.Resampling.LANCZOS)
                mk = Image.new("L", im.size, 0)
                ImageDraw.Draw(mk).ellipse((0, 0, im.size[0] - 1, im.size[1] - 1), fill=255)
                im.putalpha(mk)
                return ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))
        except Exception:
            traceback.print_exc()
        return self.logo_ctk(size)

    def discord_login(self, done_cb=None, fail_cb=None):
        """Tarayıcıda Discord girişi açar (yalnızca 'identify' izni: ad ve profil resmi). Anahtar saklanmaz."""
        import webbrowser
        from http.server import BaseHTTPRequestHandler, HTTPServer
        from urllib.parse import parse_qs, quote, urlparse
        cid = self._discord_id()
        if not cid:
            self.flash("Discord uygulama kimliği yok (Ayarlar > Discord)", 6000)
            return
        if getattr(self, "_login_busy", False):
            return
        self._login_busy = True
        self.flash("Tarayıcıda Discord girişi açılıyor...", 10000)
        result = {}
        page = ("<!doctype html><html><head><meta charset='utf-8'><title>Gardaş FM</title></head>"
                "<body style='background:#0e0b22;color:#fff;font-family:Segoe UI,Arial;text-align:center;padding-top:90px'>"
                "<h2 id='m'>Giriş tamamlanıyor...</h2><script>var h=location.hash.substring(1);"
                "if(h.indexOf('access_token')>=0){fetch('/token?'+h).then(function(){document.getElementById('m').innerText="
                "'Giriş tamamlandı! Bu sekmeyi kapatıp Gardaş FM\\'e dönebilirsin.'})}"
                "else{document.getElementById('m').innerText='Giriş yapılamadı. Gardaş FM\\'den tekrar dene.'}"
                "</script></body></html>")

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, body):
                data = body.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                u = urlparse(self.path)
                if u.path == "/token":
                    q = parse_qs(u.query)
                    try:
                        result["exp"] = int((q.get("expires_in") or ["604800"])[0])
                    except ValueError:
                        result["exp"] = 604800
                    result["token"] = (q.get("access_token") or [""])[0]
                    self._send("ok")
                else:
                    self._send(page)

        def finish(msg, ok=False):
            self._login_busy = False
            self.flash(msg, 7000)
            cb = done_cb if ok else fail_cb
            if cb:
                try:
                    cb()
                except Exception:
                    traceback.print_exc()
            try:
                self.side_cv.schedule(1)
            except Exception:
                pass

        def worker():
            try:
                srv = HTTPServer(("127.0.0.1", OAUTH_PORT), H)
            except OSError:
                self.ui(lambda: finish("Giriş için gerekli yerel kapı dolu, Gardaş FM'i kapatıp tekrar dene"))
                return
            srv.timeout = 2
            try:
                webbrowser.open("https://discord.com/oauth2/authorize?client_id=" + cid + "&response_type=token&redirect_uri="
                                + quote(f"http://localhost:{OAUTH_PORT}/", safe="") + ("&scope=identify%20guilds.members.read" if GUILD_ID else "&scope=identify"))
                end = time.time() + 150
                while time.time() < end and not result.get("token"):
                    srv.handle_request()
            finally:
                srv.server_close()
            token = result.get("token")
            if not token:
                self.ui(lambda: finish("Giriş iptal edildi ya da zaman aşımına uğradı"))
                return
            try:
                r = requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": "Bearer " + token}, timeout=12)
                j = r.json()
                uid = str(j["id"])
                name = j.get("global_name") or j.get("username") or "Dinleyici"
                if j.get("avatar"):
                    av = requests.get(f"https://cdn.discordapp.com/avatars/{uid}/{j['avatar']}.png?size=128", timeout=12)
                    if av.status_code == 200:
                        AVATAR_FILE.write_bytes(av.content)
                elif AVATAR_FILE.exists():
                    AVATAR_FILE.unlink()
                prof = {"id": uid, "name": name, "t": int(time.time())}
                if GUILD_ID:                                        # sunucu üyeliği ve rol kontrolü
                    res = self.member_check(token)
                    prof.update({"token": token, "exp": time.time() + result.get("exp", 604800) - 60,
                                 "chk": time.time(), "ok": res is True})
                self.cfg["profile"] = prof
                self.save_cfg()
                self.ui(lambda: finish(f"Giriş yapıldı: {name}", ok=True))
            except Exception as ex:
                print("Discord girişi hatası:", ex)
                self.ui(lambda: finish("Discord bilgileri alınamadı, tekrar dene"))
        threading.Thread(target=worker, daemon=True).start()

    def discord_logout(self):
        self.cfg.pop("profile", None)
        try:
            if AVATAR_FILE.exists():
                AVATAR_FILE.unlink()
        except Exception:
            pass
        self.save_cfg()
        self.side_cv.schedule(1)
        self.flash("Çıkış yapıldı")
        self.after(300, self.require_login)

    # ------------------------------------------------------------ 6.0: dinleme istatistikleri
    def stats_tick(self, t):
        """Çalarken geçen süreyi aylık ve şarkı/sanatçı bazında biriktirir (60 sn'de bir dosyaya yazar)."""
        last, self._st_t = self._st_t, t
        if last is None or t - last > 5 or self.now_item is None:
            return
        try:
            if self.player.get_state() != vlc.State.Playing:
                return
        except Exception:
            return
        dt = t - last
        it = self.now_item
        k = key_of(it)
        m = self.stats.setdefault("months", {}).setdefault(time.strftime("%Y-%m"), {"sec": 0.0, "songs": {}, "artists": {}})
        m["sec"] += dt
        self.stats["total"] = self.stats.get("total", 0.0) + dt
        s = m["songs"].setdefault(k, {"t": it["title"], "a": it["artist"], "sec": 0.0, "n": 0})
        s["sec"] += dt
        a = (it["artist"] or "").strip()
        if a:
            m["artists"][a] = m["artists"].get(a, 0.0) + dt
        if self._st_tok != self.token:
            self._st_tok, self._st_cur = self.token, 0.0
        self._st_cur += dt
        if self._st_cur >= 30 and self._st_counted != self.token:       # 30 sn'den fazla dinlenen = 1 dinleme
            self._st_counted = self.token
            s["n"] += 1
        if t - self._st_saved > 60:
            self._st_saved = t
            save_json(STATS_FILE, self.stats)

    @staticmethod
    def fmt_hm(sec):
        sec = int(sec)
        h, m = sec // 3600, sec % 3600 // 60
        return f"{h} sa {m} dk" if h else f"{m} dk"

    def month_summary(self, ym=None):
        m = self.stats.get("months", {}).get(ym or time.strftime("%Y-%m"), {})
        songs = sorted(m.get("songs", {}).values(), key=lambda x: -x["sec"])[:5]
        arts = sorted(m.get("artists", {}).items(), key=lambda x: -x[1])[:3]
        return {"sec": m.get("sec", 0.0), "songs": songs, "artists": arts}

    def make_month_card(self):
        """Aylık dinleme özetini paylaşmalık bir PNG olarak kaydeder."""
        from PIL import ImageFont
        sm = self.month_summary()
        if sm["sec"] < 60:
            self.flash("Bu ay henüz yeterince dinleme yok, biraz müzik dinleyip tekrar dene", 6000)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Aylık özeti kaydet", defaultextension=".png",
                                            initialfile=f"GardasFM_ozet_{time.strftime('%Y-%m')}.png",
                                            filetypes=[("Resim", "*.png")])
        if not path:
            return

        def font(size, bold=True):
            for n in (("bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf") if bold
                      else ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf")):
                try:
                    return ImageFont.truetype(n, size)
                except Exception:
                    pass
            return ImageFont.load_default()
        try:
            W, H = 1080, 1350
            bg = Image.new("RGB", (W, H), (12, 9, 32))
            d = ImageDraw.Draw(bg)
            for y in range(H):
                d.line((0, y, W, y), fill=(12 + y // 40, 9 + y // 90, 32 + y // 20))
            glow = Image.new("RGB", (W, H), (0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.ellipse((int(W * .4), -300, int(W * 1.3), 500), fill=tuple(int(c * .5) for c in ACCENT_RGB))
            gd.ellipse((-300, int(H * .6), int(W * .6), int(H * 1.3)), fill=tuple(int(c * .4) for c in NEON2_RGB))
            bg = ImageChops.add(bg, glow.filter(ImageFilter.GaussianBlur(160)))
            bg = glass(bg, [((56, 56, W - 56, H - 56), 56, (20, 16, 46), 175, "neon")])
            d = ImageDraw.Draw(bg)
            months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            d.text((110, 110), "GARDAŞ FM", font=font(60), fill=ACCENT)
            d.text((110, 185), f"{months[int(time.strftime('%m')) - 1]} {time.strftime('%Y')} özeti", font=font(40, False), fill=(200, 196, 230))
            x0 = 110
            try:
                if AVATAR_FILE.exists() and self.profile():
                    av = Image.open(AVATAR_FILE).convert("RGBA").resize((120, 120), Image.Resampling.LANCZOS)
                    mk = Image.new("L", (120, 120), 0)
                    ImageDraw.Draw(mk).ellipse((0, 0, 119, 119), fill=255)
                    bg.paste(av, (W - 110 - 120, 100), mk)
            except Exception:
                pass
            d.text((x0, 290), self.profile_name(), font=font(46), fill=(255, 255, 255))
            d.text((x0, 380), self.fmt_hm(sm["sec"]), font=font(120), fill=GOLD)
            d.text((x0, 515), "bu ay müzik dinledin", font=font(36, False), fill=(200, 196, 230))
            y = 605
            if sm["artists"]:
                d.text((x0, y), "EN ÇOK DİNLEDİĞİN SANATÇI", font=font(28), fill=NEON2)
                d.text((x0, y + 42), sm["artists"][0][0][:28], font=font(62), fill=(255, 255, 255))
                y += 140
            d.text((x0, y), "EN ÇOK DİNLEDİĞİN ŞARKILAR", font=font(28), fill=NEON2)
            y += 54
            for i, s_ in enumerate(sm["songs"], 1):
                d.text((x0, y), f"{i}", font=font(34), fill=ACCENT)
                d.text((x0 + 56, y), (s_["t"] or "")[:34], font=font(34, False), fill=(255, 255, 255))
                d.text((x0 + 56, y + 40), f"{(s_['a'] or '')[:30]} · {self.fmt_hm(s_['sec'])}", font=font(24, False), fill=(170, 166, 205))
                y += 84
            d.text((110, H - 125), "Umut · Kayra  |  Gardaş FM", font=font(28, False), fill=(150, 146, 185))
            bg.save(path)
            self.flash(f"Özet resmi kaydedildi: {Path(path).name}", 7000)
        except Exception as ex:
            traceback.print_exc()
            self.flash(f"Özet resmi oluşturulamadı: {ex}", 8000)

    # ------------------------------------------------------------ 6.0: liste paylaşma, dışa aktarma, tekrarları temizleme
    def _cur_list(self):
        return self.lists.get(self.cur_view, []), (self.cur_view[len(PL_PREFIX):] if self.cur_view.startswith(PL_PREFIX) else self.cur_view)

    def export_gfm(self):
        items, name = self._cur_list()
        if not items:
            self.flash("Bu listede şarkı yok", 4000)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Listeyi paylaş", defaultextension=".gfm",
                                            initialfile=f"{re.sub(r'[^0-9A-Za-zÇĞİÖŞÜçğıöşü _-]', '', name)[:40] or 'liste'}.gfm",
                                            filetypes=[("Gardaş FM listesi", "*.gfm")])
        if not path:
            return
        data = {"gardasfm": 1, "ad": name, "by": self.profile_name(),
                "items": [{"artist": i["artist"], "title": i["title"],
                           "url": i["url"] if str(i.get("url") or "").startswith("http") else None} for i in items]}
        try:
            Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            self.flash(f"Liste kaydedildi ({len(items)} şarkı). Dosyayı arkadaşına gönder, o 'Dosyadan içe aktar' desin", 8000)
        except Exception as ex:
            self.flash(f"Kaydedilemedi: {ex}", 6000)

    def import_gfm(self):
        path = filedialog.askopenfilename(parent=self, title="Liste dosyası seç", filetypes=[("Gardaş FM listesi", "*.gfm")])
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
            if data.get("gardasfm") != 1:
                raise ValueError("geçerli bir liste dosyası değil")
            items = [make_item(str(i.get("artist") or ""), str(i.get("title") or "?"), i.get("url") or None, None)
                     for i in data.get("items", []) if i.get("title")][:2000]
            if not items:
                raise ValueError("listede şarkı yok")
            base = (str(data.get("ad") or "İçe aktarılan")[:26]).strip() or "İçe aktarılan"
            name, n = base, 2
            while PL_PREFIX + name in self.lists or name == MIX2:
                name, n = f"{base} ({n})", n + 1
            key = PL_PREFIX + name
            self.lists[key] = items
            self.pl_keys.append(key)
            self.save_playlists()
            self.side_cv.schedule(1)
            self.flash(f"“{name}” eklendi: {len(items)} şarkı ({data.get('by') or 'bilinmeyen'} paylaştı)", 7000)
        except Exception as ex:
            self.flash(f"İçe aktarılamadı: {ex}", 7000)

    def export_text(self, kind):
        items, name = self._cur_list()
        if not items:
            self.flash("Bu listede şarkı yok", 4000)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Listeyi kaydet", defaultextension="." + kind,
                                            initialfile=f"liste.{kind}", filetypes=[(kind.upper(), "*." + kind)])
        if not path:
            return
        try:
            if kind == "m3u":
                lines = ["#EXTM3U"]
                for i in items:
                    lines.append(f"#EXTINF:{int(i.get('dur') or -1)},{i['artist']} - {i['title']}".replace("\n", " "))
                    lines.append(i["url"] if i.get("url") else f"# {i['artist']} - {i['title']}")
            else:
                lines = [f"{k}. {i['artist']} - {i['title']}" if i["artist"] else f"{k}. {i['title']}" for k, i in enumerate(items, 1)]
            Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.flash(f"Kaydedildi: {Path(path).name}", 5000)
        except Exception as ex:
            self.flash(f"Kaydedilemedi: {ex}", 6000)

    def dedupe_current(self):
        v = self.cur_view
        lst = self.lists.get(v)
        if lst is None or not (v == MIX or v in self.pl_keys):
            self.flash("Tekrarlar sadece favorilerde ve kendi listelerinde temizlenir", 5000)
            return
        seen, out = set(), []
        for it in lst:
            k = key_of(it)
            if k not in seen:
                seen.add(k)
                out.append(it)
        removed = len(lst) - len(out)
        if removed:
            lst[:] = out
            (self.save_mix if v == MIX else self.save_playlists)()
            self.fill_tree()
        self.flash(f"{removed} tekrar eden şarkı silindi" if removed else "Tekrar eden şarkı yok", 4500)

    # ------------------------------------------------------------ 6.0: söz kaydırma ve şarkı başına ses
    def shift_lyrics(self, d):
        if self.now_item is None:
            return
        offs = self.cfg.setdefault("lyr_off", {})
        k = key_of(self.now_item)
        v = round(max(-10.0, min(10.0, offs.get(k, 0.0) + d)), 1)
        if v == 0:
            offs.pop(k, None)
        else:
            offs[k] = v
            if len(offs) > 300:
                offs.pop(next(iter(offs)))
        self.save_cfg()
        self.flash(f"Söz kaydırma: {v:+.1f} sn   (] sözler erken gelsin, [ geç gelsin)", 3500)

    def apply_song_volume(self):
        if not self.cfg.get("song_vol_on") or self.now_item is None:
            return
        try:
            stored = self.cfg.get("song_vol", {}).get(key_of(self.now_item))
            if stored is not None:
                if self._vol_base is None:
                    self._vol_base = int(self.vol.get())
                self.vol.set(stored)
                self.player.audio_set_volume(int(stored))
            elif self._vol_base is not None:
                self.vol.set(self._vol_base)
                self.player.audio_set_volume(int(self._vol_base))
                self._vol_base = None
        except Exception:
            traceback.print_exc()

    # ------------------------------------------------------------ 6.2: Discord sunucu rolü kapısı
    def member_check(self, token):
        """Sunucu üyeliği/rol kontrolü. True: izinli, False: değil, "expired": giriş süresi dolmuş, None: ağ hatası."""
        try:
            r = requests.get(f"https://discord.com/api/v10/users/@me/guilds/{GUILD_ID}/member",
                             headers={"Authorization": "Bearer " + token}, timeout=12)
            if r.status_code == 200:
                if not ALLOWED_ROLE_IDS:
                    return True
                return bool({str(x) for x in r.json().get("roles", [])} & {str(x) for x in ALLOWED_ROLE_IDS})
            if r.status_code == 401:
                return "expired"
            if r.status_code in (403, 404):
                return False
        except Exception as ex:
            print("Rol kontrolü yapılamadı:", ex)
        return None

    def has_access(self):
        """Kapı kapalıysa (GUILD_ID boş) herkes girer; kurucular muaf; diğerleri için son 14 günde rol doğrulanmış olmalı."""
        if not GUILD_ID:
            return True
        p = self.profile()
        if not p:
            return False
        if self.founder_of():
            return True
        return bool(p.get("ok")) and time.time() - p.get("chk", 0) < 14 * 86400

    def recheck_access(self, done_cb=None, fail_cb=None):
        """Kayıtlı giriş anahtarıyla rolü yeniden sorar; anahtarın süresi dolduysa yeniden Discord girişi açar."""
        p = self.profile()
        tok = p.get("token")
        if not (tok and time.time() < p.get("exp", 0)):
            self.discord_login(done_cb, fail_cb)
            return

        def worker():
            res = self.member_check(tok)

            def done():
                if res in (True, False):
                    p["ok"], p["chk"] = res, time.time()
                    self.save_cfg()
                    if done_cb:
                        done_cb()
                elif res == "expired":
                    self.discord_login(done_cb, fail_cb)
                elif fail_cb:
                    fail_cb()
            self.ui(done)
        threading.Thread(target=worker, daemon=True).start()

    def recheck_access_silent(self):
        """Açılışta rolü sessizce yeniden kontrol eder; rol alınmışsa giriş duvarını geri getirir."""
        if not GUILD_ID or not self.profile() or self.founder_of():
            return
        p = self.profile()
        tok = p.get("token")
        if tok and time.time() < p.get("exp", 0) and not self.is_offline():
            def worker():
                res = self.member_check(tok)

                def done():
                    if res in (True, False):
                        p["ok"], p["chk"] = res, time.time()
                        self.save_cfg()
                    if not self.has_access():
                        self.require_login()
                self.ui(done)
            threading.Thread(target=worker, daemon=True).start()
        elif not self.has_access():
            self.require_login()

    # ------------------------------------------------------------ 6.1: zorunlu giriş duvarı
    def require_login(self, tries=0):
        """Giriş yapılmadan uygulama kullanılamaz: pencerenin üstüne kapatılamayan bir giriş kartı koyar."""
        if (self.profile() and self.has_access()) or getattr(self, "_login_wall", None) is not None:
            return
        intro = getattr(self, "intro", None)
        if intro is not None and getattr(intro, "alive", False) and tries < 60:      # açılış animasyonu bitsin
            self.after(1000, lambda: self.require_login(tries + 1))
            return
        self._reveal()
        wall = tk.Canvas(self, highlightthickness=0, bg="#07050f")
        wall.place(x=0, y=0, relwidth=1, relheight=1)
        wall.bind("<Button-1>", lambda e: "break")
        wall.bind("<MouseWheel>", lambda e: "break")
        self._login_wall = wall
        card = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=24, border_width=2, border_color=ACCENT)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=34, pady=28)
        import webbrowser
        denied = bool(self.profile())
        title_txt = "Erişim için doğrulama gerekli" if denied else "Devam etmek için Discord ile giriş yap"
        if TIKTOK_NAME:
            steps = ("1) Sunucuya katıl\n2) " + TIKTOK_NAME + " hesabını takip et\n"
                     f"3) Ekran görüntüsünü #{VERIFY_CHANNEL} kanalına at\n4) Rolün verilince \"Tekrar kontrol et\"e bas")
        else:
            steps = (f"1) Sunucuya katıl\n2) #{VERIFY_CHANNEL} kanalına gidip doğrulanmak istediğini yaz\n"
                     "3) Yetkililer rolünü verince \"Tekrar kontrol et\"e bas")
        desc_txt = ("Gardaş FM'i kullanmak için Discord sunucumuzda doğrulanman gerekiyor:\n" + steps) if denied \
            else ("Sadece adın ve profil resmin okunur, şifre ya da başka izin istenmez. "
                  "Bir kere giriş yapman yeterli, sonraki açılışlarda sorulmaz.")
        logo = self.logo_ctk(88)
        if logo is not None:
            ctk.CTkLabel(inner, image=logo, text="").pack(pady=(0, 8))
        ctk.CTkLabel(inner, text="GARDAŞ FM", font=ctk.CTkFont(HEAD_FONT, 30, "bold"), text_color=ACCENT).pack()
        ctk.CTkLabel(inner, text=title_txt, font=ctk.CTkFont(BODY_FONT, 16, "bold"),
                     text_color=TEXT).pack(pady=(8, 4))
        ctk.CTkLabel(inner, text=desc_txt,
                     text_color=SOFT, wraplength=380, justify="center",
                     font=ctk.CTkFont(BODY_FONT, 12)).pack(pady=(0, 10))
        status = ctk.CTkLabel(inner, text="", text_color=GOLD, wraplength=380, justify="center",
                              font=ctk.CTkFont(BODY_FONT, 12))
        status.pack(pady=(0, 8))
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack()
        login_btn = ctk.CTkButton(row, text="Discord ile giriş", height=42, corner_radius=21, fg_color=ACCENT,
                                  hover_color=ACCENT_HOVER, font=ctk.CTkFont(BODY_FONT, 14, "bold"))
        login_btn.pack(side="left", padx=(0, 10))
        if denied:
            login_btn.configure(text="Tekrar kontrol et")
            if INVITE_URL:
                ctk.CTkButton(row, text="Sunucuya katıl", height=42, corner_radius=21, fg_color=BTN, hover_color="#33296b",
                              border_width=1, border_color=NEON2_DIM, font=ctk.CTkFont(BODY_FONT, 14),
                              command=lambda: webbrowser.open(INVITE_URL)).pack(side="left", padx=(0, 10))
        ctk.CTkButton(row, text="Çıkış", height=42, corner_radius=21, fg_color=BTN, hover_color="#33296b",
                      border_width=1, border_color=NEON2_DIM, font=ctk.CTkFont(BODY_FONT, 14),
                      command=self.quit_app).pack(side="left")

        def close_wall():
            for w in (card, wall):
                try:
                    w.destroy()
                except Exception:
                    pass
            self._login_wall = None
            self.flash(f"Hoş geldin, {self.profile_name()}!", 5000)
            self.after(500, self.start_web_mode)

        def failed():
            try:
                login_btn.configure(state="normal", text="Tekrar dene")
                status.configure(text="Giriş tamamlanamadı. İnternet bağlantını kontrol edip tekrar dene (ilk girişte internet gerekir).")
            except Exception:
                pass

        def after_login():
            if self.has_access():
                close_wall()
                return
            try:
                login_btn.configure(state="normal", text="Tekrar kontrol et")
                status.configure(text="Henüz doğrulanmadın. Rolün verildikten sonra tekrar dene.")
            except Exception:
                pass

        def start():
            login_btn.configure(state="disabled")
            if denied:
                status.configure(text="Kontrol ediliyor...")
                self.recheck_access(after_login, failed)
            else:
                status.configure(text="Tarayıcıda Discord girişi açıldı, orada onaylayıp buraya dön...")
                self.discord_login(done_cb=after_login, fail_cb=failed)
        login_btn.configure(command=start)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.lift()

    def _yt_url(self, it):
        u = it.get("url") or ""
        if str(u).startswith("http"):
            return u
        vid = (self.id_cache.get(key_of(it)) or {}).get("id")
        return f"https://www.youtube.com/watch?v={vid}" if vid else ""

    # ------------------------------------------------------------ 7.0: yeni arayüz (beta): yerel web arayüzü
    def webui_state(self):
        it = self.now_item
        try:
            st = self.player.get_state()
            length, cur = max(0, self.player.get_length()), max(0, self.player.get_time())
            playing = st in (vlc.State.Playing, vlc.State.Buffering, vlc.State.Opening)
        except Exception:
            length = cur = 0
            playing = False
        self._wu_last = time.time()
        sync = getattr(self, "sync", None) or []
        lines = list(getattr(self, "lyr_lines", None) or [])[:300]
        if len(sync) != len(lines):                      # eski şarkının zamanları kalmış olabilir: zamansız göster
            sync = []
        off = self.cfg.get("lyr_off", {}).get(key_of(it), 0.0) if it else 0.0
        return {"ok": 1, "title": it["title"] if it else "", "artist": it["artist"] if it else "",
                "dur": (length / 1000.0) or float((it or {}).get("dur") or 0), "pos": cur / 1000.0, "playing": playing,
                "vol": int(getattr(self, "_wu_vol", 70)), "key": key_of(it) if it else "", "idx": self.play_idx,
                "cid": (id(self.cover) % 1000000007) if self.cover is not None else 0,
                "colors": [[int(c) for c in self.dyn_target], [int(c) for c in NEON2_RGB]],
                "lyrics": lines, "lsig": (abs(hash(tuple(lines[:6]))) % 1000000007) + len(lines),
                "fav": bool(it) and self.is_fav(it),
                "times": [float(a) for a, _ in sync][:300] if sync else None, "off": off,
                "queue": [{"t": i["title"], "a": i["artist"], "d": i.get("dur") or 0} for i in self.play_items[:300]],
                "user": self.profile_name()}

    def webui_cover(self):
        im = self.cover
        if im is None:
            return b""
        key = (id(im), im.size)
        if getattr(self, "_wu_cover_key", None) != key:
            buf = io.BytesIO()
            c = im.convert("RGB")
            c.thumbnail((640, 640))
            c.save(buf, "PNG")
            self._wu_cover_png, self._wu_cover_key = buf.getvalue(), key
        return self._wu_cover_png

    def webui_logo(self):
        img = self.logo_pil() or self.generated_icon()
        buf = io.BytesIO()
        img.copy().resize((128, 128)).save(buf, "PNG")
        return buf.getvalue()

    def webui_lists(self):
        lib = [MIX, RECENT, QUEUE, DOWNLOADS]
        out = []
        for n in lib + list(self.pl_keys) + list(NAV) + list(LIVE_CATS):
            if n in self.lists:
                g = 0 if n in lib else (1 if n in self.pl_keys else 2)
                out.append({"n": n, "label": n[len(PL_PREFIX):] if n.startswith(PL_PREFIX) else n,
                            "c": len(self.lists.get(n, [])), "g": g})
        return out

    def webui_new_list(self, name, add_n=None, add_i=None):
        base = re.sub(r"\s+", " ", str(name)).strip()[:30] or "Yeni liste"
        n, k = base, 2
        while PL_PREFIX + n in self.lists or n == MIX2:
            n, k = f"{base} ({k})", k + 1
        key = PL_PREFIX + n
        self.lists[key] = []
        self.pl_keys.append(key)
        if add_n is not None and add_i is not None:
            items = self.webui_items(str(add_n))
            if 0 <= int(add_i) < len(items):
                self.add_to_list(key, items[int(add_i)])
        self.save_playlists()
        self.side_cv.schedule(1)

    def webui_items(self, n):
        return getattr(self, "_wu_results", []) if n == "__ara" else self.lists.get(n, [])

    def webui_rows(self, items):
        favs = {key_of(x) for x in self.lists.get(MIX, [])}
        return [{"t": i["title"], "a": i["artist"], "d": i.get("dur") or 0, "f": key_of(i) in favs} for i in items[:400]]

    def webui_list(self, name):
        return self.webui_rows(self.webui_items(name))

    def webui_home(self):
        cards = [{"id": "shuffle", "t": "Karışık çal", "s": "Tüm katalogdan rastgele"},
                 {"id": "daily", "t": "Bugünün karışığı", "s": "Her gün yeni 25 şarkı"},
                 {"id": "radio", "t": "Radyo", "s": "Çalan şarkıdan sonsuz yayın"}]
        return cards + [{"id": "mood:" + n, "t": n, "s": sub} for n, sub, _c, _t in MOODS]

    def webui_search(self, q):
        """Önce kendi listelerinde, sonra YouTube'da arar; sonuçlar '__ara' listesi olarak saklanır."""
        q = (q or "").strip()[:100]
        if len(q) < 2:
            return []
        words = fold(q).split()
        res, seen = [], set()
        for c in [*NAV, MIX, DOWNLOADS]:
            for it in self.lists.get(c, []):
                k = key_of(it)
                if k not in seen and all(w in fold(f"{it['artist']} {it['title']}") for w in words):
                    seen.add(k)
                    res.append(it)
        res = res[:30]
        if not self.is_offline():
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as ydl:
                    info = ydl.extract_info(f"ytsearch15:{q}", download=False)
                for e in info.get("entries", []):
                    it = make_item(e.get("channel") or e.get("uploader") or "", e.get("title", "?"),
                                   e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}", e.get("duration"))
                    k = key_of(it)
                    if k not in seen:
                        seen.add(k)
                        res.append(it)
            except Exception as ex:
                print("Yeni arayüz araması hatası:", ex)
        self._wu_results = res
        return self.webui_rows(res)

    def webui_cmd(self, c):
        """Yeni arayüzden gelen komutlar: Tk iş parçacığında çalıştırılır."""
        cmd = str(c.get("cmd", ""))
        if cmd == "toggle":
            self.ui(self.toggle_play)
        elif cmd == "next":
            self.ui(self.next_song)
        elif cmd == "prev":
            self.ui(self.prev_song)
        elif cmd == "seek":
            f = max(0.0, min(1.0, float(c.get("f", 0))))
            self.ui(lambda: self.player.set_position(f))
        elif cmd == "vol":
            v = max(0, min(100, int(c.get("v", 70))))
            self._wu_vol = v

            def setv():
                self.vol.set(v)
                self.on_volume(v)
            self.ui(setv)
        elif cmd == "home":
            hid = str(c.get("id", ""))
            if hid == "shuffle":
                self.ui(self.play_all_shuffled)
            elif hid == "daily":
                self.ui(self.play_daily)
            elif hid == "radio":
                self.ui(self.radio_from_current)
            elif hid.startswith("mood:"):
                self.ui(lambda: self.play_mood(hid[5:]))
        elif cmd in ("fav_row", "enqueue"):
            items = self.webui_items(str(c.get("n", "")))
            idx = int(c.get("i", 0))
            if 0 <= idx < len(items):
                it = items[idx]
                self.ui(lambda: self.toggle_fav(it) if cmd == "fav_row" else self.enqueue(it))
        elif cmd == "fav_now":
            it = self.now_item
            if it:
                self.ui(lambda: self.toggle_fav(it))
        elif cmd == "settings":
            self.ui(lambda: (self.show_window(), self.open_settings()))
        elif cmd == "classic":
            self.ui(self.show_window)
        elif cmd == "quit":
            self.ui(self.quit_app)
        elif cmd == "dl_row":
            items = self.webui_items(str(c.get("n", "")))
            idx = int(c.get("i", 0))
            if 0 <= idx < len(items):
                it = items[idx]
                self.ui(lambda: self.download(it))
        elif cmd == "dl_list":
            items = list(self.webui_items(str(c.get("n", ""))))
            if items:
                self.ui(lambda: self.download_many(items))
        elif cmd == "add_to_list":
            items = self.webui_items(str(c.get("n", "")))
            idx, key = int(c.get("i", 0)), str(c.get("t", ""))
            if 0 <= idx < len(items) and (key == MIX or key in self.pl_keys):
                it = items[idx]
                self.ui(lambda: self.add_to_list(key, it))
        elif cmd == "new_list":
            nm, an, ai = str(c.get("name", ""))[:60], c.get("add_n"), c.get("add_i")
            self.ui(lambda: self.webui_new_list(nm, an, ai))
        elif cmd == "play_list":
            lst = list(self.webui_items(str(c.get("n", ""))))
            idx = int(c.get("i", 0))
            if lst and 0 <= idx < len(lst):
                self.ui(lambda: self.start_play(lst, idx))
        elif cmd == "play_queue":
            idx = int(c.get("i", 0))
            if 0 <= idx < len(self.play_items):
                items = list(self.play_items)
                self.ui(lambda: self.start_play(items, idx))

    def webui_start(self):
        """127.0.0.1 üzerinde, oturuma özel gizli anahtarla korunan küçük yerel sunucu."""
        import hmac
        import secrets
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from urllib.parse import parse_qs, urlparse
        app = self
        token = secrets.token_urlsafe(16)

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _auth(self):
                host = (self.headers.get("Host") or "").split(":")[0]
                q = parse_qs(urlparse(self.path).query)
                t = (q.get("t") or [""])[0]
                return host in ("127.0.0.1", "localhost") and hmac.compare_digest(t, token), q

            def _send(self, code, body, ctype="application/json; charset=utf-8"):
                data = body if isinstance(body, bytes) else body.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                ok, q = self._auth()
                if not ok:
                    return self._send(403, "{}")
                path = urlparse(self.path).path
                try:
                    if path == "/":
                        self._send(200, WEBUI_HTML, "text/html; charset=utf-8")
                    elif path == "/api/state":
                        self._send(200, json.dumps(app.webui_state(), ensure_ascii=False))
                    elif path == "/api/cover":
                        png = app.webui_cover()
                        self._send(200 if png else 204, png, "image/png")
                    elif path == "/api/logo":
                        self._send(200, app.webui_logo(), "image/png")
                    elif path == "/api/lists":
                        self._send(200, json.dumps(app.webui_lists(), ensure_ascii=False))
                    elif path == "/api/home":
                        self._send(200, json.dumps(app.webui_home(), ensure_ascii=False))
                    elif path == "/api/search":
                        self._send(200, json.dumps(app.webui_search((q.get("q") or [""])[0]), ensure_ascii=False))
                    elif path == "/api/list":
                        self._send(200, json.dumps(app.webui_list((q.get("n") or [""])[0]), ensure_ascii=False))
                    else:
                        self._send(404, "{}")
                except Exception as ex:
                    traceback.print_exc()
                    self._send(500, json.dumps({"err": f"{type(ex).__name__}: {ex}"[:200]}, ensure_ascii=False))

            def do_POST(self):
                ok, _q = self._auth()
                if not ok or not (self.headers.get("Content-Type") or "").startswith("application/json"):
                    return self._send(403, "{}")
                try:
                    n = min(int(self.headers.get("Content-Length") or 0), 10000)
                    app.webui_cmd(json.loads(self.rfile.read(n).decode("utf-8") or "{}"))
                    self._send(200, '{"ok":1}')
                except Exception as ex:
                    print("Yeni arayüz komutu hatası:", ex)
                    self._send(400, "{}")
        for port in range(53690, 53700):
            try:
                srv = ThreadingHTTPServer(("127.0.0.1", port), H)
                break
            except OSError:
                srv = None
        if srv is None:
            raise OSError("yerel arayüz için boş kapı bulunamadı")
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self._wu_srv, self._wu_port, self._wu_token = srv, port, token

    def start_web_mode(self, tries=0):
        """8.0: Yeni arayüz ana arayüzdür. Açılışta web penceresi açılır, bağlanınca klasik pencere tepsiye küçülür."""
        if getattr(self, "_wm_started", False) or not self.cfg.get("webui_default", True):
            return
        intro = getattr(self, "intro", None)
        if intro is not None and getattr(intro, "alive", False) and tries < 60:
            self.after(1000, lambda: self.start_web_mode(tries + 1))
            return
        if not (self.profile() and self.has_access()) or getattr(self, "_login_wall", None) is not None:
            return                                        # giriş duvarı klasik pencerede kalır
        self._wm_started = True
        self._wu_last = 0
        self.open_webui()
        self.after(1000, lambda: self._wm_check(0))

    def _wm_check(self, n):
        if getattr(self, "_wu_last", 0) > 0:               # yeni arayüz bağlandı: klasik pencereyi gizle
            try:
                if not self.to_tray():
                    self.iconify()
            except Exception:
                self.iconify()
            return
        if n < 20:
            self.after(1000, lambda: self._wm_check(n + 1))
            return
        self._wm_started = False
        self.flash("Yeni arayüz açılamadı, klasik arayüz kullanılıyor", 8000)

    def _reveal(self):
        """Güncelleme ve giriş gibi klasik pencerede gösterilen şeyler için pencereyi geri getirir."""
        try:
            if self.state() in ("withdrawn", "iconic"):
                self.show_window()
        except Exception:
            pass

    def open_webui(self):
        """Yeni arayüzü ayrı bir uygulama penceresinde açar (Edge/Chrome, yoksa tarayıcı)."""
        import webbrowser
        try:
            if getattr(self, "_wu_srv", None) is None:
                self.webui_start()
            url = f"http://127.0.0.1:{self._wu_port}/?t={self._wu_token}"
            cands = [shutil.which("msedge"), shutil.which("chrome"),
                     r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                     r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                     r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
            exe = next((c for c in cands if c and os.path.exists(c)), None)
            if exe:
                subprocess.Popen([exe, f"--app={url}", "--window-size=1320,840"])
            else:
                webbrowser.open(url)
            self.flash("Yeni arayüz (beta) açıldı", 4000)
        except Exception as ex:
            traceback.print_exc()
            self.flash(f"Yeni arayüz açılamadı: {ex}", 7000)

    # ------------------------------------------------------------ yedekle / geri yükle
    def backup_to_zip(self):
        """Favoriler, çalma listeleri, ayarlar ve kayıtlı sözler tek bir zip dosyasına yedeklenir."""
        try:
            self.save_cfg()
            self.save_mix()
            self.save_playlists()
        except Exception:
            traceback.print_exc()
        path = filedialog.asksaveasfilename(parent=self, title="Yedeği kaydet", defaultextension=".zip",
                                            initialfile=f"GardasFM_yedek_{time.strftime('%Y-%m-%d')}.zip",
                                            filetypes=[("Gardaş FM yedeği", "*.zip")])
        if not path:
            return
        try:
            n_ok = 0
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("yedek_bilgi.json", json.dumps(
                    {"uygulama": "GardasFM", "surum": APP_VERSION, "tarih": time.strftime("%Y-%m-%d %H:%M:%S")},
                    ensure_ascii=False))
                for n in RESTORE_FILES:
                    f = DATA_DIR / n
                    if f.exists():
                        zf.write(f, n)
                        n_ok += 1
            self.flash(f"Yedek kaydedildi ({n_ok} dosya): {Path(path).name}", 7000)
        except Exception as ex:
            self.flash(f"Yedek alınamadı: {ex}", 8000)

    def restore_from_zip(self):
        path = filedialog.askopenfilename(parent=self, title="Yedek dosyasını seç",
                                          filetypes=[("Gardaş FM yedeği", "*.zip")])
        if not path:
            return
        try:
            files = _read_backup_zip(path)
        except Exception:
            files = None
        if not files:
            messagebox.showerror("Gardaş FM", "Bu dosya geçerli bir Gardaş FM yedeği değil.", parent=self)
            return
        if not messagebox.askyesno(
                "Yedekten geri yükle",
                "Yedekteki favoriler, listeler ve ayarlar şu anki verilerinin yerine geçecek "
                "(şu anki verilerin 'yedek' klasörüne kopyalanır).\n\n"
                "Bunun için uygulama kapanacak, sonra tekrar açmalısın. Devam edilsin mi?", parent=self):
            return
        try:
            shutil.copy2(path, PENDING_RESTORE)
        except Exception as ex:
            self.flash(f"Geri yükleme hazırlanamadı: {ex}", 8000)
            return
        self.quit_app()

    # ------------------------------------------------------------ "Neler yeni" penceresi
    def show_whats_new(self, only_new=False):
        last = self.cfg.get("last_seen", "")
        if only_new:
            items = [x for x in WHATS_NEW if self._ver_tuple(x[0]) > self._ver_tuple(last)] if last else WHATS_NEW[:1]
        else:
            items = WHATS_NEW
        if not items:
            return
        win = GToplevel(self)
        win.title("Neler yeni")
        win.geometry("460x500")
        win.configure(fg_color=PANEL)
        win.transient(self)
        win.after(150, win.lift)
        box = ctk.CTkScrollableFrame(win, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=6, pady=(6, 0))
        lg = self.logo_ctk(64)
        if lg is not None:
            ctk.CTkLabel(box, image=lg, text="").pack(anchor="w", padx=18, pady=(12, 0))
        ctk.CTkLabel(box, text=f"Gardaş FM {APP_VERSION} - neler yeni", font=ctk.CTkFont(HEAD_FONT, 20, "bold"),
                     text_color=GOLD).pack(anchor="w", padx=18, pady=(14, 8))
        for v, lines in items:
            ctk.CTkLabel(box, text=f"Sürüm {v}", text_color=ACCENT,
                         font=ctk.CTkFont(BODY_FONT, 13, "bold")).pack(anchor="w", padx=18, pady=(12, 2))
            for ln in lines:
                ctk.CTkLabel(box, text="•  " + ln, text_color=SOFT, wraplength=380, justify="left", anchor="w",
                             font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", padx=22, pady=3)
        ctk.CTkButton(win, text="Tamam", height=36, corner_radius=18, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=win.destroy).pack(anchor="e", padx=24, pady=12)

    def maybe_show_whats_new(self, tries=0):
        """Güncellemeden sonraki ilk açılışta yenilikleri gösterir (açılış animasyonu bitince)."""
        if self.cfg.get("last_seen") == APP_VERSION:
            return
        intro = getattr(self, "intro", None)
        if intro is not None and getattr(intro, "alive", False) and tries < 40:
            self.after(2000, lambda: self.maybe_show_whats_new(tries + 1))
            return
        try:
            self.show_whats_new(only_new=True)
        except Exception:
            traceback.print_exc()
        self.cfg["last_seen"] = APP_VERSION
        self.save_cfg()

    # ------------------------------------------------------------ Discord durumu (Rich Presence)
    def _discord_id(self):
        return re.sub(r"\D", "", str(self.cfg.get("discord_id") or DISCORD_CLIENT_ID or ""))

    def discord_toggled(self):
        self._dc_key = None
        self._dc_fail = 0.0
        if not self.cfg.get("discord"):
            threading.Thread(target=self.discord_close, daemon=True).start()
        elif not self._discord_id():
            self.flash("Önce aşağıya Discord uygulama kimliğini yazıp Kaydet'e bas", 8000)

    def discord_tick(self):
        """5 sn'de bir bakar; şarkı ya da çalıyor/duraklatıldı durumu değiştiyse Discord'a bildirir."""
        try:
            if self.cfg.get("discord") and self._discord_id() and time.time() >= self._dc_fail:
                cur = self.play_items[self.play_idx] if 0 <= self.play_idx < len(self.play_items) else None
                state = self.player.get_state()
                playing = bool(self.player.is_playing()) or state in (vlc.State.Opening, vlc.State.Buffering)
                if cur is None or state in (vlc.State.Stopped, vlc.State.Ended, vlc.State.NothingSpecial):
                    key = None
                else:
                    key = (cur.get("title"), cur.get("artist"), playing)
                if key != self._dc_key and time.time() - self._dc_last >= 15:      # Discord ~15 sn'de bir güncelleme kabul eder
                    payload = None
                    if key is not None:
                        length = self.player.get_length()
                        pos = max(0.0, self.player.get_position()) * length / 1000 if length > 0 else 0
                        payload = {"title": cur.get("title"), "artist": cur.get("artist"),
                                   "playing": playing, "start": int(time.time() - pos), "url": self._yt_url(cur)}
                    self._dc_key = key
                    self._dc_last = time.time()
                    threading.Thread(target=self.discord_push, args=(payload,), daemon=True).start()
        except Exception:
            traceback.print_exc()
        finally:
            self.after(5000, self.discord_tick)

    def discord_push(self, payload):
        with self._dc_lock:
            try:
                if self._dc_rpc is None:
                    if payload is None:
                        return
                    try:
                        from pypresence import Presence
                    except ImportError:
                        subprocess.run([sys.executable, "-m", "pip", "install", "pypresence"],
                                       capture_output=True, timeout=180)
                        import importlib
                        importlib.invalidate_caches()
                        from pypresence import Presence
                    rpc = Presence(self._discord_id())
                    rpc.connect()
                    self._dc_rpc = rpc
                if payload is None:
                    self._dc_rpc.clear()
                    return

                def fit(txt, default):
                    txt = (txt or "").strip() or default
                    txt = txt[:120]
                    return txt if len(txt) >= 2 else txt + " "
                artist = fit(payload.get("artist"), "Gardaş FM")
                kw = {"details": fit(payload.get("title"), "Şarkı"),
                      "state": artist if payload["playing"] else fit(artist + " (duraklatıldı)", "Duraklatıldı"),
                      "large_text": f"{self.profile_name()} · Gardaş FM", "large_image": "logo"}
                if payload["playing"]:
                    kw["start"] = payload["start"]
                if str(payload.get("url") or "").startswith("http"):
                    kw["buttons"] = [{"label": "YouTube'da dinle", "url": payload["url"]}]
                try:
                    from pypresence import ActivityType
                    kw["activity_type"] = ActivityType.LISTENING      # "Gardaş FM dinliyor"
                except Exception:
                    pass
                try:
                    self._dc_rpc.update(**kw)
                except TypeError:
                    kw.pop("activity_type", None)
                    self._dc_rpc.update(**kw)
            except Exception as ex:
                print("Discord durumu güncellenemedi:", ex)
                try:
                    if self._dc_rpc is not None:
                        self._dc_rpc.close()
                except Exception:
                    pass
                self._dc_rpc = None
                self._dc_key = None
                self._dc_fail = time.time() + 60
                if not self._dc_warned:
                    self._dc_warned = True
                    self.ui(lambda: self.flash("Discord'a bağlanılamadı (Discord açık mı? Kimlik doğru mu?)", 8000))

    def discord_close(self):
        try:
            if self._dc_rpc is not None:
                try:
                    self._dc_rpc.clear()
                except Exception:
                    pass
                self._dc_rpc.close()
        except Exception:
            pass
        self._dc_rpc = None

    # ------------------------------------------------------------ uygulama güncellemesi (GitHub)
    @staticmethod
    def _ver_tuple(v):
        try:
            return tuple(int(x) for x in str(v).strip().split("."))
        except Exception:
            return (0,)

    def maybe_update_app(self):
        """Günde bir kez GitHub'a bakar; yeni sürüm varsa indirip kurar (veriler önce yedeklenir, dokunulmaz)."""
        if not self.cfg.get("auto_update", True) or self.is_offline():
            return
        if "KULLANICI_ADIN" in GITHUB_REPO:
            return                      # depo adı henüz yazılmamış
        if time.time() - float(self.cfg.get("update_day", 0) or 0) < 86400:
            return
        self.cfg["update_day"] = time.time()
        self.save_cfg()
        self.update_app(silent=True)

    def backup_user_data(self):
        return _backup_user_data()

    def _remote_notes(self, code, new_v):
        """Uzaktaki dosyadaki WHATS_NEW'den, bu sürümle yeni sürüm arasındaki notları çıkarır (kod çalıştırılmaz)."""
        try:
            for node in ast.parse(code).body:
                if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "WHATS_NEW" for t in node.targets):
                    out = []
                    for v, lines in ast.literal_eval(node.value):
                        if self._ver_tuple(APP_VERSION) < self._ver_tuple(v) <= self._ver_tuple(new_v):
                            out += list(lines)
                    return out
        except Exception as ex:
            print("Sürüm notları okunamadı:", ex)
        return []

    def update_app(self, silent=False):
        """GitHub'a bakar; yeni sürüm varsa ekranın ortasında güncelleme kartını açar (kurulum karttan yapılır)."""
        if "KULLANICI_ADIN" in GITHUB_REPO:
            if not silent:
                self.flash("gardas_fm.py içindeki GITHUB_REPO satırına GitHub depo adını yaz", 8000)
            return
        if not silent:
            self.flash("Güncelleme denetleniyor...", 30000)

        def job():
            msg = None
            try:
                url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FILE}"
                r = requests.get(url, timeout=20, headers={"User-Agent": "GardasFM-updater"})
                if r.status_code != 200:
                    raise RuntimeError(f"GitHub yanıtı: {r.status_code}")
                code = r.content.decode("utf-8")
                m = re.search(r'^APP_VERSION\s*=\s*"([0-9.]+)"', code, re.M)
                if not m:
                    raise RuntimeError("Uzaktaki dosyada APP_VERSION yok")
                new_v = m.group(1)
                if self._ver_tuple(new_v) <= self._ver_tuple(APP_VERSION):
                    msg = None if silent else f"Zaten en yeni sürümdesin (v{APP_VERSION})"
                elif silent and new_v == str(self.cfg.get("bad_version", "")):
                    pass                                      # bu sürüm daha önce açılmadı ve geri alındı: tekrar önerme
                else:
                    compile(code, GITHUB_FILE, "exec")        # bozuk dosya inmişse kurma
                    fm = re.search(r'^FORCE_UPDATE_BELOW\s*=\s*"([0-9.]+)"', code, re.M)
                    forced = bool(fm) and self._ver_tuple(APP_VERSION) < self._ver_tuple(fm.group(1))
                    info = {"version": new_v, "code": code, "notes": self._remote_notes(code, new_v), "forced": forced}
                    self.ui(lambda: (self.flash(f"Yeni sürüm bulundu: v{new_v}", 3000), self.show_update_card(info)))
            except Exception as ex:
                print("Uygulama güncellemesi başarısız:", ex)
                msg = None if silent else "Güncelleme denetlenemedi (internet / GitHub depo adı?)"
            if msg:
                self.ui(lambda: self.flash(msg, 10000))
        threading.Thread(target=job, daemon=True).start()

    # ------------------------------------------------------------ logo
    def logo_pil(self):
        """Önce uygulama klasöründeki logo.png, yoksa koda gömülü LOGO_B64. Yoksa None."""
        if getattr(self, "_logo_cache", False) is not False:
            return self._logo_cache
        img = None
        try:
            for f in (Path(__file__).resolve().parent / "logo.png", DATA_DIR / "logo.png"):
                if f.exists():
                    img = Image.open(f).convert("RGBA")
                    break
            if img is None and LOGO_B64:
                img = Image.open(io.BytesIO(base64.b64decode(LOGO_B64))).convert("RGBA")
        except Exception as ex:
            print("Logo yüklenemedi:", ex)
            img = None
        self._logo_cache = img
        return img

    def logo_ctk(self, size):
        img = self.logo_pil()
        if img is None:
            return None
        k = size / max(img.width, img.height)
        w, h = max(1, int(img.width * k)), max(1, int(img.height * k))
        big = img.resize((w * 2, h * 2), Image.LANCZOS)
        return ctk.CTkImage(light_image=big, dark_image=big, size=(w, h))

    def generated_icon(self):
        """Logo dosyası yoksa neon geçişli bir 'G' simgesi üretir (kısayol/pencere Python simgesi göstermesin)."""
        if getattr(self, "_gen_icon", None) is not None:
            return self._gen_icon
        from PIL import ImageFont
        S = 256
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        grad = Image.new("RGB", (S, S))
        gd = ImageDraw.Draw(grad)
        for y in range(S):
            t = y / (S - 1)
            gd.line((0, y, S, y), fill=tuple(int(a + (b - a) * t) for a, b in zip(ACCENT_RGB, NEON2_RGB)))
        mk = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mk).rounded_rectangle((8, 8, S - 9, S - 9), radius=56, fill=255)
        img.paste(grad, (0, 0), mk)
        d = ImageDraw.Draw(img)
        font = None
        for n in ("bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
            try:
                font = ImageFont.truetype(n, 150)
                break
            except Exception:
                pass
        try:
            d.text((S // 2, S // 2 + 6), "G", font=font or ImageFont.load_default(), fill=(255, 255, 255, 255), anchor="mm")
        except Exception:
            d.text((S // 2 - 40, S // 2 - 60), "G", font=font or ImageFont.load_default(), fill=(255, 255, 255, 255))
        self._gen_icon = img
        return img

    def apply_logo_icon(self):
        img = self.logo_pil() or self.generated_icon()
        if img is None:
            return
        try:
            ic = img.copy()
            ic.thumbnail((64, 64))
            self._icon_photo = ImageTk.PhotoImage(ic)
            self.iconphoto(True, self._icon_photo)
        except Exception as ex:
            print("Pencere simgesi ayarlanamadı:", ex)

    def make_desktop_shortcut(self):
        """Masaüstüne 'Gardaş FM' kısayolu koyar: konsol penceresi açmaz, logo varsa simge olur."""
        if os.name != "nt":
            self.flash("Kısayol sadece Windows'ta oluşturulur", 6000)
            return
        self.flash("Kısayol oluşturuluyor...", 10000)

        def job():
            try:
                me = Path(__file__).resolve()
                exe = Path(sys.executable)
                target = exe.with_name("pythonw.exe")
                if not target.exists():
                    target = exe
                launcher = _os.environ.get("GARDAS_LAUNCHER")
                use_launcher = bool(launcher) and Path(launcher).exists()
                if use_launcher:
                    target = Path(launcher)
                icon = str(target)
                img = self.logo_pil() or self.generated_icon()
                if img is not None:
                    sq = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                    k = 256 / max(img.size)
                    r = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
                    sq.paste(r, ((256 - r.width) // 2, (256 - r.height) // 2), r)
                    ico = DATA_DIR / "logo.ico"
                    sq.save(ico, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                    icon = str(ico)
                q = lambda x: str(x).replace("'", "''")
                argtxt = "" if use_launcher else '"' + q(me) + '"'
                ps = DATA_DIR / "kisayol.ps1"
                ps.write_text(
                    "$d = [Environment]::GetFolderPath('Desktop')\n"
                    "$s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Gardaş FM.lnk'))\n"
                    f"$s.TargetPath = '{q(target)}'\n"
                    f"$s.Arguments = '{argtxt}'\n"
                    f"$s.WorkingDirectory = '{q(me.parent)}'\n"
                    f"$s.IconLocation = '{q(icon)}'\n"
                    "$s.Description = 'Gardaş FM'\n"
                    "$s.Save()\n", encoding="utf-8-sig")
                res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
                                     capture_output=True, timeout=40, creationflags=0x08000000)
                try:
                    ps.unlink()
                except Exception:
                    pass
                if res.returncode != 0:
                    raise RuntimeError((res.stderr or b"").decode("utf-8", "ignore")[:150] or "PowerShell hatası")
                msg = "Masaüstüne 'Gardaş FM' kısayolu eklendi"
            except Exception as ex:
                print("Kısayol oluşturulamadı:", ex)
                msg = f"Kısayol oluşturulamadı: {ex}"
            self.ui(lambda: self.flash(msg, 9000))
        threading.Thread(target=job, daemon=True).start()

    # ------------------------------------------------------------ güncelleme kartı
    def show_update_card(self, info):
        """Güncelleme duvarı: pencere kilitlenir (bulanık, karartılmış ekran), ortada logolu kart çıkar."""
        old = getattr(self, "_upd_card", None)
        if old is not None:
            try:
                if old.winfo_exists():
                    old.lift()
                    return
            except Exception:
                pass
            self._upd_card = None
        intro = getattr(self, "intro", None)
        if intro is not None and getattr(intro, "alive", False):      # açılış animasyonu bitsin
            self.after(1500, lambda: self.show_update_card(info))
            return
        self._upd_info = info
        self._reveal()
        shot = None
        try:
            self.update_idletasks()
            if self.state() == "normal" and self.focus_displayof() is not None:
                from PIL import ImageGrab
                x0, y0, ww, hh = self.winfo_rootx(), self.winfo_rooty(), self.winfo_width(), self.winfo_height()
                im = ImageGrab.grab(bbox=(x0, y0, x0 + ww, y0 + hh))
                shot = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(7))).enhance(0.35)
        except Exception as ex:
            print("Duvar görüntüsü alınamadı:", ex)
        wall = tk.Canvas(self, highlightthickness=0, bg="#07050f")
        self._upd_wall = wall
        if shot is not None:
            self._wall_photo = ImageTk.PhotoImage(shot)
            wall.create_image(0, 0, image=self._wall_photo, anchor="nw")
        wall.place(x=0, y=0, relwidth=1, relheight=1)
        wall.bind("<Button-1>", lambda e: "break")
        wall.bind("<MouseWheel>", lambda e: "break")
        if not info.get("forced"):
            wall.bind("<Escape>", lambda e: self.close_update_card())
        wall.focus_set()
        card = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=24, border_width=2, border_color=ACCENT)
        self._upd_card = card
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=24)
        logo = self.logo_ctk(88)
        if logo is not None:
            ctk.CTkLabel(inner, image=logo, text="").pack(pady=(0, 8))
        else:
            ctk.CTkLabel(inner, text="GARDAŞ FM", font=ctk.CTkFont(HEAD_FONT, 26, "bold"),
                         text_color=GOLD).pack(pady=(0, 8))
        ctk.CTkLabel(inner, text="Yeni sürüm geldi!", font=ctk.CTkFont(HEAD_FONT, 22, "bold"),
                     text_color=GOLD).pack()
        ctk.CTkLabel(inner, text=f"v{APP_VERSION}   →   v{info['version']}", text_color=ACCENT,
                     font=ctk.CTkFont(BODY_FONT, 14, "bold")).pack(pady=(2, 4))
        ctk.CTkLabel(inner, text="Devam etmek için güncellemen gerekiyor." if info.get("forced")
                     else "Güncellemek istiyor musun?", text_color=TEXT,
                     font=ctk.CTkFont(BODY_FONT, 14)).pack(pady=(0, 8))
        for ln in (info.get("notes") or [])[:5]:
            ctk.CTkLabel(inner, text="•  " + ln, text_color=SOFT, wraplength=360, justify="left", anchor="w",
                         font=ctk.CTkFont(BODY_FONT, 12)).pack(anchor="w", pady=2)
        self._upd_status = ctk.CTkLabel(
            inner, text="Favorilerin, mixlerin ve ayarların korunur. Güncelleme bitince uygulama kendini yeniden başlatır.",
            text_color=MUTED, wraplength=360, justify="center", font=ctk.CTkFont(BODY_FONT, 11))
        self._upd_status.pack(pady=(10, 0))
        self._upd_bar = ctk.CTkProgressBar(inner, width=360, height=10, progress_color=ACCENT, fg_color=BTN)
        self._upd_bar.set(0)
        self._upd_btns = ctk.CTkFrame(inner, fg_color="transparent")
        self._upd_btns.pack(pady=(14, 0))
        self._upd_go = ctk.CTkButton(self._upd_btns, text="Şimdi güncelle", height=40, corner_radius=20,
                                     fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                     font=ctk.CTkFont(BODY_FONT, 14, "bold"), command=self.start_update_install)
        self._upd_go.pack(side="left", padx=(0, 10))
        self._upd_later = ctk.CTkButton(self._upd_btns, text="Sonra", height=40, corner_radius=20, fg_color=BTN,
                                        hover_color="#33296b", font=ctk.CTkFont(BODY_FONT, 14),
                                        border_width=1, border_color=NEON2_DIM, command=self.close_update_card)
        if not info.get("forced"):
            self._upd_later.pack(side="left")
        card.place(relx=0.5, rely=0.60, anchor="center")
        card.lift()
        self._slide_card(0)

    def _slide_card(self, i):
        """Kart aşağıdan yumuşakça kayarak ortaya gelir."""
        card = getattr(self, "_upd_card", None)
        if card is None:
            return
        try:
            if not card.winfo_exists():
                return
            p = min(1.0, i / 12.0)
            card.place_configure(rely=0.60 - 0.10 * (1 - (1 - p) ** 3))
            card.lift()
            if p < 1.0:
                self.after(16, lambda: self._slide_card(i + 1))
        except Exception:
            pass

    def close_update_card(self):
        card, self._upd_card = getattr(self, "_upd_card", None), None
        wall, self._upd_wall = getattr(self, "_upd_wall", None), None
        for w in (card, wall):
            if w is not None:
                try:
                    w.destroy()
                except Exception:
                    pass

    def start_update_install(self):
        info = self._upd_info
        self._upd_go.configure(state="disabled")
        self._upd_later.configure(state="disabled")
        self._upd_bar.pack(pady=(12, 0), before=self._upd_btns)
        self._upd_shown = 0.0
        self._upd_target = 0.0
        self._upd_tick()
        threading.Thread(target=self._upd_job, args=(info,), daemon=True).start()

    def _upd_set(self, target, text=None):
        self._upd_target = target
        if text:
            try:
                self._upd_status.configure(text=text)
            except Exception:
                pass

    def _upd_tick(self):
        """İlerleme çubuğu hedefe doğru yumuşakça akar."""
        try:
            if getattr(self, "_upd_card", None) is None or not self._upd_bar.winfo_exists():
                return
            self._upd_shown += (self._upd_target - self._upd_shown) * 0.18
            if abs(self._upd_target - self._upd_shown) < 0.002:
                self._upd_shown = self._upd_target
            self._upd_bar.set(self._upd_shown)
            if self._upd_shown >= 1.0:
                return
        except Exception:
            return
        self.after(20, self._upd_tick)

    def _upd_job(self, info):
        preview = bool(info.get("preview"))
        ver = info["version"]
        try:
            self.ui(lambda: self._upd_set(0.30, "Yeni sürüm indirildi ✓"))
            time.sleep(0.4)
            self.ui(lambda: self._upd_set(0.55, "Favoriler ve ayarlar yedekleniyor..."))
            if not preview:
                self.backup_user_data()
            time.sleep(0.4)
            self.ui(lambda: self._upd_set(0.85, "Yeni sürüm kuruluyor..."))
            if not preview:
                me = Path(__file__).resolve()
                _MARK.write_text(json.dumps({"yeni": ver, "tamam": False, "zaman": time.time()}), encoding="utf-8")
                shutil.copy2(me, me.with_suffix(".py.eski"))
                tmp = me.with_suffix(".py.yeni")
                tmp.write_bytes(info["code"].encode("utf-8"))
                os.replace(tmp, me)
            time.sleep(0.4)
            self.ui(lambda: (self._upd_set(1.0, f"Hazır! v{ver} kuruldu ✓" if not preview else "Önizleme bitti ✓"),
                             self._upd_finished(preview)))
        except Exception as ex:
            print("Güncelleme kurulamadı:", ex)
            err = str(ex)
            self.ui(lambda: (self._upd_set(self._upd_target, f"Kurulamadı: {err}"),
                             self._upd_fail()))

    def _upd_finished(self, preview):
        try:
            if preview:
                self._upd_go.configure(state="normal", text="Tamam", command=self.close_update_card)
                self._upd_later.pack_forget()
            else:
                self._upd_go.configure(state="normal", text="Şimdi yeniden başlat", command=self.restart_app)
                self._upd_later.pack_forget()
                self._auto_restart(3)
        except Exception:
            pass

    def _auto_restart(self, n):
        """Kurulum bitince kendini otomatik yeniden başlatır (3 saniyelik geri sayımla)."""
        try:
            if getattr(self, "_upd_card", None) is None:
                return
            if n <= 0:
                self.restart_app()
                return
            self._upd_status.configure(text=f"Güncelleme tamam. Yeniden başlatılıyor... {n}")
            self.after(1000, lambda: self._auto_restart(n - 1))
        except Exception:
            pass

    def _upd_fail(self):
        try:
            self._upd_go.configure(state="normal", text="Tekrar dene")
            self._upd_later.configure(state="normal", text="Kapat", command=self.close_update_card)
            self._upd_later.pack(side="left")
        except Exception:
            pass

    def restart_app(self):
        """Uygulamayı yeni sürümle yeniden başlatır (Windows'ta konsol penceresi açmadan)."""
        me = Path(__file__).resolve()
        exe, flags = sys.executable, 0
        if os.name == "nt":
            pw = Path(exe).with_name("pythonw.exe")
            if pw.exists():
                exe = str(pw)
            flags = 0x00000008 | 0x00000200            # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        try:
            self.save_cfg()
            self.save_mix()
            self.save_playlists()              # yeni süreç açılırken güncel veriyi okusun
        except Exception:
            traceback.print_exc()
        try:
            subprocess.Popen([exe, str(me)], cwd=str(me.parent), creationflags=flags, close_fds=True)
        except Exception as ex:
            self.flash(f"Yeniden başlatılamadı, uygulamayı kapatıp elle aç ({ex})", 9000)
            return
        self.quit_app()

    def maybe_update_ytdlp(self):
        """Şarkılar çalmayınca çoğu zaman sebep eski yt-dlp'dir: haftada bir sessizce güncellenir."""
        if time.time() - float(self.cfg.get("ytdlp_day", 0) or 0) < 7 * 86400 or self.is_offline():
            return
        self.cfg["ytdlp_day"] = time.time()
        self.save_cfg()
        self.update_ytdlp(silent=True)

    def update_ytdlp(self, silent=False):
        if not silent:
            self.flash("yt-dlp güncelleniyor...", 60000)

        def job():
            try:
                r = subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                                   capture_output=True, text=True, timeout=180)
                ok = r.returncode == 0
            except Exception as ex:
                print("yt-dlp güncellenemedi:", ex)
                ok = False
            msg = "yt-dlp güncellendi, uygulamayı kapatıp aç" if ok else "Güncelleme başarısız (internet/pip?)"
            if not (silent and not ok):
                self.ui(lambda: self.flash(msg, 8000))
        threading.Thread(target=job, daemon=True).start()

    # ------------------------------------------------------------ animasyonlar
    def _anim(self):
        """~25 kare/sn: kapak dalgaları + ses çubukları, kayan menü hapı, ana sayfa girişi, söz modu, mini oynatıcı."""
        lvl = self.cfg.get("anim", "Tam")
        delay = {"Tam": 40, "Hafif": 66}.get(lvl, 110)
        try:
            self._frame_i += 1
            t = time.time()
            self.fade_tick()
            self.stats_tick(t)
            main_vis = self.state() != "iconic" and self.winfo_viewable()
            if main_vis:
                playing = bool(self.player.is_playing())
                self.dyn_rgb = tuple(c + (g - c) * 0.10 for c, g in zip(self.dyn_rgb, self.dyn_target))
                if lvl != "Kapalı":
                    self.anim_np(t, playing)
                else:
                    self.np_cv.delete("anim")
                self.lyr_tick(t)
                self.anim_pill()
                if self._frame_i % 2 == 0 and self.cur_view == HOME and t - self.home_t0 < 1.3:
                    self.home_cv.redraw()
                if lvl == "Tam" and self._frame_i % 2 == 0 and self.cur_view not in (HOME, SEARCH) \
                        and t - getattr(self, "view_t0", 0.0) < 0.5:
                    self.hero_cv.redraw()                            # başlık süzülerek gelir
                if self._frame_i % 7 == 0:
                    self.anim_row(t, playing)
            if self._lf is not None:
                self.lf_tick(t)
            if self._mini is not None and self._frame_i % 12 == 0:
                self.mini_tick()
            if not main_vis and self._lf is None:
                delay = 200 if self._mini is None else 80
        except Exception:
            traceback.print_exc()
        finally:
            self.after(delay, self._anim)

    def anim_np(self, t, playing):
        """Kapağın etrafında yayılan dalgalar ve kapağın altında oynayan ses çubukları (kapağın renginde).
        Not: VLC gerçek ses spektrumu vermediği için hareket çalma durumuna ve ses seviyesine bağlı bir canlandırmadır."""
        cv = self.np_cv
        cv.delete("anim")
        g = self.np_geo
        if not g or cv.winfo_width() < 20:
            return
        S = self.S
        cx, cy, side = g
        vol = 0.35 + 0.65 * (float(self.vol.get()) / 100.0)
        n = len(self.bars)
        beat = max(0.0, math.sin(t * math.pi * 2.0)) ** 3            # 120 bpm'lik sahte vuruş
        fd = getattr(self, "_cover_fade", None)
        if fd is not None:                                           # kapak değişince eski kapaktan yeniye geçiş
            p = (t - fd["t0"]) / 0.6
            if p >= 1.0 or self.cover is None or self.cfg.get("anim", "Tam") != "Tam":
                self._cover_fade = None
            else:
                try:
                    new = ImageOps.fit(self.cover.convert("RGB"), (side, side), method=Image.Resampling.BILINEAR)
                    old = (ImageOps.fit(fd["prev"].convert("RGB"), (side, side), method=Image.Resampling.BILINEAR)
                           if fd.get("prev") is not None else self.placeholder_cover(side))
                    blend = Image.blend(old.convert("RGB"), new, _ease(p))
                    if getattr(self, "_fade_mask_side", 0) != side:
                        mk = Image.new("L", (side, side), 0)
                        ImageDraw.Draw(mk).rounded_rectangle((0, 0, side - 1, side - 1), radius=S(18), fill=255)
                        self._fade_mask, self._fade_mask_side = mk, side
                    blend.putalpha(self._fade_mask)
                    self._fade_photo = ImageTk.PhotoImage(blend)
                    cv.create_image(cx, cy, image=self._fade_photo, anchor="nw", tags="anim")
                except Exception:
                    traceback.print_exc()
                    self._cover_fade = None
        left, right_ = cx + S(14), cx + side - S(14)
        bw = (right_ - left) / n
        base_y, maxh = cy + side - S(10), side * 0.28
        for i in range(n):
            if playing:
                wave = (math.sin(t * (2.3 + i * 0.41) + i * 1.9) * 0.5 + 0.5) * (math.sin(t * 1.3 + i * 0.5) * 0.3 + 0.7)
                target = (0.18 + 0.82 * wave * (0.55 + 0.45 * beat)) * vol
            else:
                target = 0.0
            self.bars[i] += (target - self.bars[i]) * (0.45 if target > self.bars[i] else 0.18)
        if max(self.bars) > 0.04:
            for i, b in enumerate(self.bars):
                x = left + i * bw
                cv.create_rectangle(x, base_y - max(S(2), b * maxh), x + max(1, bw - S(3)), base_y,
                                    fill=_hex(_mix_rgb(self.dyn_rgb, GOLD_RGB, b)), outline="", tags="anim")
        if playing:
            for k in range(2):
                ph = (t * 0.55 + k * 0.5) % 1.0
                inf = S(3) + ph * S(14)
                col = _hex(_mix_rgb((30, 24, 70), self.dyn_rgb, (1 - ph) ** 1.6 * 0.85))
                cv.create_polygon(rr_poly(int(cx - inf), int(cy - inf), int(cx + side + inf), int(cy + side + inf),
                                          S(18) + int(inf)), outline=col, fill="", width=max(1, S(2)), tags="anim")

    def anim_pill(self):
        if self.pill_target is None or self.side_geo is None:
            return
        if self.pill_y is None:
            self.pill_y = float(self.pill_target)
        d = self.pill_target - self.pill_y
        if abs(d) < 0.5:
            if abs(d) < 1e-6:
                return
            self.pill_y = float(self.pill_target)
        else:
            self.pill_y += d * {"Tam": 0.28, "Hafif": 0.5}.get(self.cfg.get("anim", "Tam"), 1.0)      # yumuşak kayma
        x1, x2, rowh = self.side_geo
        S, y = self.S, int(self.pill_y)
        self.side_cv.coords("pill", *rr_points(x1, y - S(3), x2, y + rowh - S(5), S(12)))
        self.side_cv.coords("pillbar", *rr_points(x1, y + S(5), x1 + S(4), y + rowh - S(13), S(2)))

    def anim_row(self, t, playing):
        iid = self._playing_iid
        if not iid or self.cur_view == HOME:
            return
        try:
            frames = ("♪", "♫") if playing else ("▶",)
            self.tree.set(iid, "no", frames[int(t * 2) % len(frames)])
        except Exception:
            pass

    # ------------------------------------------------------------ tam ekran söz modu
    def open_lyrics_full(self):
        if self._lf is not None:
            self.close_lyrics_full()
            return
        win = tk.Toplevel(self)
        win.configure(bg="#07050f")
        win.attributes("-fullscreen", True)
        cv = tk.Canvas(win, bg="#07050f", highlightthickness=0)
        cv.pack(fill="both", expand=True)
        self._lf = {"win": win, "cv": cv, "pos": 0.0, "manual": 0.0, "bg_key": None, "photo": None,
                    "lines": [], "lines_t": -99}
        win.bind("<Escape>", lambda e: self.close_lyrics_full())
        win.bind("<Right>", lambda e: self.next_song())
        win.bind("<Left>", lambda e: self.prev_song())
        win.protocol("WM_DELETE_WINDOW", self.close_lyrics_full)

        def click(e):
            if e.x > cv.winfo_width() - self.S(90) and e.y < self.S(90):
                self.close_lyrics_full()
        cv.bind("<Button-1>", click)

        def wheel(e):
            lf = self._lf
            if lf and not self.sync:
                lf["manual"] = max(0.0, min(float(max(0, len(lf["lines"]) - 1)), lf["manual"] + (-1 if e.delta > 0 else 1)))
        win.bind("<MouseWheel>", wheel)
        win.focus_force()

    def close_lyrics_full(self):
        lf, self._lf = self._lf, None
        if lf:
            try:
                lf["win"].destroy()
            except Exception:
                pass

    def lf_tick(self, t):
        lf = self._lf
        if not lf or not lf["win"].winfo_exists():
            self._lf = None
            return
        cv, S = lf["cv"], self.S
        W, H = cv.winfo_width(), cv.winfo_height()
        if W < 100 or H < 100:
            return
        key = (id(self.cover), W, H)
        if lf["bg_key"] != key:                       # arka plan: kapağın bulanık ve karartılmış hali
            if self.cover is not None:
                bg = ImageOps.fit(self.cover, (W, H), method=Image.Resampling.BILINEAR)
                bg = bg.resize((max(1, W // 8), max(1, H // 8))).filter(ImageFilter.GaussianBlur(6))
                bg = ImageEnhance.Brightness(bg.resize((W, H), Image.Resampling.BILINEAR)).enhance(0.28)
            else:
                bg = ImageEnhance.Brightness(default_bg(W, H)).enhance(0.7)
            lf["photo"], lf["bg_key"] = ImageTk.PhotoImage(bg), key
            cv.delete("bg")
            cv.create_image(0, 0, image=lf["photo"], anchor="nw", tags="bg")
            cv.tag_lower("bg")
        if t - lf["lines_t"] > 0.5:
            lf["lines_t"] = t
            lf["lines"] = ([x or "♪" for _, x in self.sync] if self.sync
                           else list(self.lyr_lines))
        lines = lf["lines"]
        cv.delete("fg")
        target = max(0, self.sync_idx) if self.sync else lf["manual"]
        lf["pos"] += (target - lf["pos"]) * 0.14        # yumuşak kaydırma
        pos, step, cx = lf["pos"], S(76), W // 2
        for i in range(max(0, int(pos) - 5), min(len(lines), int(pos) + 7)):
            d = abs(i - pos)
            emph = max(0.0, 1.0 - d)
            k = max(0.0, 1.0 - d / 4.2)
            base = _mix_rgb((235, 231, 255), NEON2_RGB, emph)
            col = _hex(_mix_rgb((24, 18, 44), base, k))
            cv.create_text(cx, H * 0.5 + (i - pos) * step, text=lines[i], width=int(W * 0.78), justify="center",
                           fill=col, font=self.F(BODY_FONT, int(28 + 14 * emph), "bold" if emph > 0.5 else "normal"),
                           tags="fg")
        it = self.now_item
        if it:
            cv.create_text(S(40), S(40), text=it["title"][:60], anchor="w", fill="#ffffff",
                           font=self.F(HEAD_FONT, 24, "bold"), tags="fg")
            cv.create_text(S(42), S(74), text=it["artist"] or "", anchor="w", fill=_hex(self.dyn_rgb),
                           font=self.F(BODY_FONT, 16), tags="fg")
        cv.create_text(W - S(44), S(40), text="✕", fill="#cfc9f5", font=self.F(BODY_FONT, 24), tags="fg")
        cv.create_text(cx, H - S(30), text="Esc: kapat   ·   Boşluk: oynat/duraklat   ·   ← →: şarkı", fill="#7d77a8",
                       font=self.F(BODY_FONT, 12), tags="fg")
        if self.player.get_length() > 0:
            cv.create_rectangle(0, H - S(5), int(W * max(0.0, min(1.0, self.player.get_position()))), H,
                                fill=_hex(self.dyn_rgb), outline="", tags="fg")

    # ------------------------------------------------------------ mini oynatıcı
    def open_mini(self):
        if self._mini is not None:
            self.close_mini()
            return
        win = GToplevel(self)
        win.title("Gardaş FM")
        win.geometry("372x104")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.configure(fg_color=PANEL)
        m = self._mini = {"win": win, "cover_id": None}
        m["cover"] = ctk.CTkLabel(win, text="♪", width=80, height=80, fg_color=BTN, corner_radius=10,
                                  text_color=ACCENT, font=ctk.CTkFont(BODY_FONT, 28))
        m["cover"].grid(row=0, column=0, rowspan=3, padx=(10, 8), pady=10)
        m["title"] = ctk.CTkLabel(win, text="", anchor="w", width=260, text_color=TEXT,
                                  font=ctk.CTkFont(BODY_FONT, 13, "bold"))
        m["title"].grid(row=0, column=1, sticky="w", pady=(12, 0))
        bf = ctk.CTkFrame(win, fg_color="transparent")
        bf.grid(row=1, column=1, sticky="w")
        for txt, cmd in (("⏮", self.prev_song), ("▶", self.toggle_play), ("⏭", lambda: self.next_song()),
                         ("⤢", self.close_mini)):
            b = ctk.CTkButton(bf, text=txt, width=40, height=32, corner_radius=16, fg_color=ACCENT if txt == "▶" else BTN,
                              hover_color=ACCENT_HOVER if txt == "▶" else "#33296b", text_color=TEXT, command=cmd)
            b.pack(side="left", padx=(0, 6))
            if txt == "▶":
                m["play"] = b
        m["bar"] = ctk.CTkProgressBar(win, width=260, height=6, progress_color=ACCENT, fg_color=BTN)
        m["bar"].set(0)
        m["bar"].grid(row=2, column=1, sticky="w", pady=(0, 8))
        win.protocol("WM_DELETE_WINDOW", self.close_mini)
        self.withdraw()                         # ana pencere gizlenir, sadece mini oynatıcı kalır
        self.mini_tick()

    def close_mini(self):
        m, self._mini = self._mini, None
        if m:
            try:
                m["win"].destroy()
            except Exception:
                pass
        self.deiconify()
        self.lift()

    def mini_tick(self):
        m = self._mini
        if not m or not m["win"].winfo_exists():
            self._mini = None
            return
        it = self.now_item
        label = (f"{it['artist']} - {it['title']}" if it["artist"] else it["title"]) if it else "Bir şarkı seç"
        m["title"].configure(text=label[:38])
        m["play"].configure(text="⏸" if self.player.is_playing() else "▶")
        m["bar"].set(max(0.0, min(1.0, self.player.get_position())) if self.player.get_length() > 0 else 0)
        if m["cover_id"] != id(self.cover):
            m["cover_id"] = id(self.cover)
            try:
                if self.cover is not None:
                    m["img"] = ctk.CTkImage(light_image=self.cover, dark_image=self.cover, size=(80, 80))
                    m["cover"].configure(image=m["img"], text="")
                else:
                    m["cover"].configure(image=None, text="♪")
            except Exception as ex:
                print("Mini kapak:", ex)

    def start_media_keys(self):
        """Klavyedeki oynat/duraklat, sonraki, önceki tuşları (uygulama arkadayken de) çalışır. Sadece Windows."""
        if sys.platform != "win32":
            return

        def loop():
            try:
                import ctypes
                from ctypes import wintypes
                u = ctypes.windll.user32
                acts = {1: (0xB3, self.toggle_play), 2: (0xB0, lambda: self.next_song()), 3: (0xB1, self.prev_song)}
                for i, (vk, _) in acts.items():
                    u.RegisterHotKey(None, i, 0x4000, vk)        # MOD_NOREPEAT
                msg = wintypes.MSG()
                while u.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == 0x0312 and msg.wParam in acts:     # WM_HOTKEY
                        self.ui(acts[msg.wParam][1])
            except Exception as ex:
                print("Medya tuşları kurulamadı:", ex)
        self._hk_thread = threading.Thread(target=loop, daemon=True)
        self._hk_thread.start()

    def to_tray(self):
        """Pencereyi kapatınca sistem tepsisine küçülür, müzik çalmaya devam eder (pystray kuruluysa)."""
        try:
            import pystray
        except Exception:
            self.flash("Tepsi için: py -m pip install pystray", 6000)
            return False
        try:
            if self._tray is None:
                im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                d = ImageDraw.Draw(im)
                d.ellipse((2, 2, 62, 62), fill=ACCENT_RGB + (255,))
                d.ellipse((24, 24, 40, 40), fill=(20, 12, 40, 255))
                menu = pystray.Menu(
                    pystray.MenuItem("Gardaş FM'i göster", lambda: self.ui(self.show_window), default=True),
                    pystray.MenuItem("Oynat / duraklat", lambda: self.ui(self.toggle_play)),
                    pystray.MenuItem("Sonraki şarkı", lambda: self.ui(lambda: self.next_song())),
                    pystray.MenuItem("Çık", lambda: self.ui(self.quit_app)))
                self._tray = pystray.Icon("GardasFM", im, "Gardaş FM", menu)
                self._tray.run_detached()
            self.withdraw()
            return True
        except Exception as ex:
            print("Tepsi açılamadı:", ex)
            return False

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def start_intro(self):
        """Sinematik açılış (Uzay -> Türkiye -> şehir). Tıklayınca ya da Esc ile geçilir."""
        self.intro = None
        if not self.cfg.get("intro", True) or not INTRO_OK:
            return
        try:
            self.update_idletasks()
            self.intro = CinematicIntro(self)
        except Exception as ex:
            print("Açılış animasyonu başlatılamadı:", ex)


if __name__ == "__main__":
    GardasFM().mainloop()
