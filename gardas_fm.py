"""
Gardaş FM 5.5 - mp3 gerekmez (SON SÜRÜM), şarkılar internetten (YouTube) çalınır; istersen indirip internetsiz dinlersin.

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
APP_VERSION = "5.5"
GITHUB_REPO = "croxy1993-beep/GardasFM-PC"   # GitHub deposu: kullanici/depo
GITHUB_BRANCH = "main"
GITHUB_FILE = "gardas_fm.py"                 # depoda uygulama dosyasının yolu (kökteyse böyle kalsın)
BACKUP_DIR = DATA_DIR / "yedek"
USER_DATA_FILES = ["mix_listem.json", "calma_listeleri.json", "ayarlar.json", "indirilenler.json", "sozler.json"]
RESTORE_FILES = ["mix_listem.json", "calma_listeleri.json", "ayarlar.json", "sozler.json"]   # "Yedekle" dosyasına girenler
PENDING_RESTORE = DATA_DIR / "geri_yukle.zip"          # geri yüklenecek yedek: bir sonraki açılışta uygulanır
LOGO_B64 = ""                                          # gömülü logo (PNG, base64); uygulama klasöründe logo.png varsa o kullanılır
DISCORD_CLIENT_ID = ""                                 # boş bırak; kimliği Ayarlar > Discord bölümünden de girebilirsin

FORCE_UPDATE_BELOW = ""          # yeni sürümde doldurulursa (örn. "5.3") bundan eski sürümlerde güncelleme duvarında "Sonra" düğmesi gizlenir
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
               "anim": "Tam", "notify": True, "tags": {}, "bad_version": "", "side_open": True, "cover_color": True, "audd_token": "", "fade": 0}

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
        self.after(6500, self.boot_ok)
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
        segf.pack(anchor="w", padx=18, pady=(2, 14))

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
        if self.cur_view == QUEUE:
            e += [None, ("Sırayı temizle", self.clear_queue)]
        self.popup(e, self.winfo_pointerx(), self.winfo_pointery())

    def new_list_menu(self):
        self.popup([("+  Boş çalma listesi", self.new_playlist),
                    ("YouTube playlist'ten içe aktar", self.import_playlist),
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
        items = [("Ana sayfa", HOME), ("Arama", SEARCH), ("♫  Şarkı bul", "bul"), None]
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
        cv.create_text(S(24), S(70), text="çevrimdışı mod" if off else "gece yayını açık", anchor="w",
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
                idx = -1
                for i, (ts, _) in enumerate(self.sync):
                    if ts <= t + 0.15:
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
                return isinstance(self.focus_get(), (tk.Entry, tk.Text))
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
        self.bind_all("<r>", key(self.radio_from_current))

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
                ("F", "Favoriye ekle / çıkar"), ("R", "Çalan şarkıdan radyo başlat"), ("F1", "Bu pencere"), ("Esc", "Söz modunu ve pencereleri kapat")]
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
                                   "playing": playing, "start": int(time.time() - pos)}
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
                      "large_text": "Gardaş FM", "large_image": "logo"}
                if payload["playing"]:
                    kw["start"] = payload["start"]
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

    def apply_logo_icon(self):
        img = self.logo_pil()
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
                icon = str(target)
                img = self.logo_pil()
                if img is not None:
                    sq = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                    k = 256 / max(img.size)
                    r = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
                    sq.paste(r, ((256 - r.width) // 2, (256 - r.height) // 2), r)
                    ico = DATA_DIR / "logo.ico"
                    sq.save(ico, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                    icon = str(ico)
                q = lambda x: str(x).replace("'", "''")
                ps = DATA_DIR / "kisayol.ps1"
                ps.write_text(
                    "$d = [Environment]::GetFolderPath('Desktop')\n"
                    "$s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Gardaş FM.lnk'))\n"
                    f"$s.TargetPath = '{q(target)}'\n"
                    f"$s.Arguments = '\"{q(me)}\"'\n"
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
