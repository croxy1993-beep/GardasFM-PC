"""Gardaş FM kurulum ve başlatıcı (EXE).
İlk çalıştırmada eksik her şeyi (Python, VLC, paketler, uygulama) kullanıcı klasörüne kurar, sonra uygulamayı açar.
Kuruluysa pencere göstermeden doğrudan uygulamayı açar. Yönetici izni gerekmez."""
import ctypes
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import zipfile
from pathlib import Path

BASE = Path(os.environ.get("GARDAS_BASE") or (Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "GardasFM"))
PY_DIR, VLC_DIR = BASE / "python", BASE / "vlc"
APP_PY, LOG, MARK = BASE / "gardas_fm.py", BASE / "kurulum.log", BASE / "hazir.json"
RAW = "https://raw.githubusercontent.com/croxy1993-beep/GardasFM-PC/main/gardas_fm.py"
PY_URL = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
VLC_URL = "https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.zip"
PACKAGES = ["customtkinter", "python-vlc", "yt-dlp", "requests", "Pillow", "pystray", "pypresence"]
IMPORT_TEST = "import customtkinter, vlc, yt_dlp, requests, PIL, pystray, pypresence"
NOWIN = 0x08000000                                   # CREATE_NO_WINDOW
DETACH = 0x00000008 | 0x00000200                     # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP


def log(msg):
    try:
        BASE.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg) + "\n")
    except Exception:
        pass


def download(url, dest, cb=None):
    """url -> dest (ilerleme cb(yüzde) ile bildirilir)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "GardasFM-kurulum"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        got = 0
        while True:
            chunk = r.read(256 * 1024)
            if not chunk:
                break
            f.write(chunk)
            got += len(chunk)
            if cb and total:
                cb(got * 100 // total)
    return dest


def run(cmd, **kw):
    log("çalıştır: " + " ".join(map(str, cmd)))
    return subprocess.run(cmd, capture_output=True, creationflags=NOWIN if os.name == "nt" else 0, **kw)


def ensure_python(say, prog):
    if (PY_DIR / "pythonw.exe").exists():
        return
    say("Python indiriliyor...")
    setup = download(PY_URL, BASE / "py_kurulum.exe", prog)
    say("Python kuruluyor (1-2 dakika)...")
    prog(-1)
    r = run([str(setup), "/quiet", "InstallAllUsers=0", "PrependPath=0", "Include_launcher=0", "Include_test=0",
             "Include_doc=0", "Include_tcltk=1", "Include_pip=1", f"TargetDir={PY_DIR}"])
    log(f"python kurulum çıkış kodu: {r.returncode}")
    if not (PY_DIR / "pythonw.exe").exists():
        raise RuntimeError("Python kurulamadı. İnternet bağlantını ve disk alanını kontrol et.")
    try:
        setup.unlink()
    except Exception:
        pass


def ensure_vlc(say, prog):
    if (VLC_DIR / "libvlc.dll").exists():
        return
    say("VLC (ses motoru) indiriliyor...")
    z = download(VLC_URL, BASE / "vlc.zip", prog)
    say("VLC açılıyor...")
    prog(-1)
    tmp = BASE / "vlc_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(z) as zf:
        zf.extractall(tmp)
    inner = next((p for p in tmp.iterdir() if p.is_dir()), tmp)
    shutil.rmtree(VLC_DIR, ignore_errors=True)
    shutil.move(str(inner), str(VLC_DIR))
    shutil.rmtree(tmp, ignore_errors=True)
    try:
        z.unlink()
    except Exception:
        pass
    if not (VLC_DIR / "libvlc.dll").exists():
        raise RuntimeError("VLC kurulamadı.")


def py_env():
    env = dict(os.environ)
    env["GARDAS_LAUNCHER"] = str(BASE / "GardasFM.exe")
    if (VLC_DIR / "libvlc.dll").exists():
        env["PYTHON_VLC_LIB_PATH"] = str(VLC_DIR / "libvlc.dll")
        env["PYTHON_VLC_MODULE_PATH"] = str(VLC_DIR / "plugins")
    return env


def ensure_packages(say, prog):
    py = str(PY_DIR / "python.exe")
    if run([py, "-c", IMPORT_TEST], env=py_env()).returncode == 0:
        return
    say("Gerekli paketler kuruluyor (birkaç dakika sürebilir)...")
    prog(-1)
    r = run([py, "-m", "pip", "install", "--disable-pip-version-check", "-U", *PACKAGES])
    log("pip çıkış kodu: %s %s" % (r.returncode, (r.stderr or b"")[-300:].decode("utf-8", "ignore")))
    if run([py, "-c", IMPORT_TEST], env=py_env()).returncode != 0:
        raise RuntimeError("Paketler kurulamadı. İnternet bağlantını kontrol edip tekrar dene.")


def ensure_app(say, prog):
    if APP_PY.exists():
        return
    say("Gardaş FM indiriliyor...")
    download(RAW, APP_PY, prog)
    if not APP_PY.exists() or APP_PY.stat().st_size < 50000:
        raise RuntimeError("Uygulama dosyası indirilemedi.")


def make_shortcut():
    exe = BASE / "GardasFM.exe"
    if os.name != "nt" or not exe.exists():
        return
    ps = BASE / "kisayol.ps1"
    ps.write_text("$d=[Environment]::GetFolderPath('Desktop')\n$s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'Gardaş FM.lnk'))\n"
                  f"$s.TargetPath='{exe}'\n$s.WorkingDirectory='{BASE}'\n$s.IconLocation='{exe},0'\n$s.Description='Gardaş FM'\n$s.Save()\n",
                  encoding="utf-8-sig")
    run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)])
    try:
        ps.unlink()
    except Exception:
        pass


def install_all(say, prog):
    BASE.mkdir(parents=True, exist_ok=True)
    me = Path(sys.executable)
    if getattr(sys, "frozen", False) and me.resolve() != (BASE / "GardasFM.exe").resolve():
        shutil.copy2(me, BASE / "GardasFM.exe")          # kısayol indirilenler klasörüne bağlı kalmasın
    ensure_python(say, prog)
    ensure_vlc(say, prog)
    ensure_packages(say, prog)
    ensure_app(say, prog)
    make_shortcut()
    MARK.write_text(json.dumps({"t": time.time()}), encoding="utf-8")


def is_ready():
    return MARK.exists() and (PY_DIR / "pythonw.exe").exists() and (VLC_DIR / "libvlc.dll").exists() and APP_PY.exists()


def launch():
    p = subprocess.Popen([str(PY_DIR / "pythonw.exe"), str(APP_PY)], cwd=str(BASE), env=py_env(),
                         creationflags=DETACH if os.name == "nt" else 0)
    log("uygulama başlatıldı")
    return p


def start_app_checked():
    """Uygulamayı açar; 4 saniye içinde hemen kapanırsa (bozuk kurulum) False döner."""
    p = launch()
    for _ in range(8):
        time.sleep(0.5)
        if p.poll() is not None:
            log(f"uygulama erken kapandı, kod {p.returncode}")
            return False
    return True


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if is_ready():                                       # kuruluysa: sadece uygulamayı aç
        if start_app_checked():
            return
        MARK.unlink(missing_ok=True)                     # açılmadı: onarım için kurulumu yeniden çalıştır
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    root.title("Gardaş FM Kurulum")
    root.geometry("460x250")
    root.resizable(False, False)
    root.configure(bg="#0e0b22")
    try:
        ico = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "logo.png"
        root._ico = tk.PhotoImage(file=str(ico))
        root.iconphoto(True, root._ico)
        tk.Label(root, image=root._ico.subsample(6, 6), bg="#0e0b22").pack(pady=(14, 0))
    except Exception:
        tk.Label(root, text="GARDAŞ FM", fg="#ff4f8b", bg="#0e0b22", font=("Segoe UI", 20, "bold")).pack(pady=(18, 0))
    status = tk.Label(root, text="Hazırlanıyor...", fg="#f3f0ff", bg="#0e0b22", font=("Segoe UI", 11), wraplength=420)
    status.pack(pady=(10, 8))
    bar = ttk.Progressbar(root, length=380, mode="determinate")
    bar.pack()
    info = tk.Label(root, text="İlk kurulum internet ister ve birkaç dakika sürer. Sonraki açılışlar anında olur.",
                    fg="#8a85b5", bg="#0e0b22", font=("Segoe UI", 9), wraplength=420)
    info.pack(pady=10)
    btns = tk.Frame(root, bg="#0e0b22")
    btns.pack()

    def say(t):
        root.after(0, lambda: status.config(text=t))

    def prog(p):
        def f():
            if p < 0:
                bar.config(mode="indeterminate")
                bar.start(12)
            else:
                bar.stop()
                bar.config(mode="determinate", value=p)
        root.after(0, f)

    def worker():
        try:
            install_all(say, prog)
            say("Gardaş FM açılıyor...")
            start_app_checked()
            root.after(0, root.destroy)
        except Exception as ex:
            log(traceback.format_exc())
            root.after(0, lambda: fail(str(ex)))

    def fail(msg):
        bar.stop()
        status.config(text="Hata: " + msg, fg="#ff7a7a")
        info.config(text=f"Ayrıntı: {LOG}")
        for w in btns.winfo_children():
            w.destroy()
        tk.Button(btns, text="Tekrar dene", command=retry).pack(side="left", padx=6)
        tk.Button(btns, text="Kapat", command=root.destroy).pack(side="left", padx=6)

    def retry():
        for w in btns.winfo_children():
            w.destroy()
        status.config(fg="#f3f0ff")
        threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=worker, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()
