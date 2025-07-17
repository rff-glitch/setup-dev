# Save as installer.py and run on Windows
import subprocess, requests, zipfile, os, threading
from tkinter import Tk, Frame, Label, Button, Canvas, Scrollbar, ttk
from pathlib import Path

APPS = {
    "neofetch": "neofetch",
    "Google Chrome": "Google.Chrome",
    "Visual Studio Code": "Microsoft.VisualStudioCode",
    "Git": "Git.Git",
    "Visual Studio 2022": "Microsoft.VisualStudio.2022.Community",
    "Android Studio": "Google.AndroidStudio",
    "Python 3": "Python.Python.3",
    "NodeJS": "OpenJS.NodeJS",
    "Ruby": "RubyInstallerTeam.Ruby",
    "CMake": "Kitware.CMake",
    "Temurin JDK 17": "EclipseAdoptium.Temurin.17.JDK",
    "WinRAR": "RARLab.WinRAR",
}

GRADLE_VERSION = "8.5"
GRADLE_DIR = Path(f"C:/Gradle/gradle-{GRADLE_VERSION}")

def is_installed(package_id):
    result = subprocess.run(["winget", "list", package_id], capture_output=True, text=True, shell=True)
    return package_id.lower() in result.stdout.lower()

def install_app(package_id, label, progress):
    def task():
        if is_installed(package_id):
            label.config(text="✅ Already Installed")
            progress["value"] = 100
            return

        label.config(text="Installing...")
        process = subprocess.Popen([
            "winget", "install", package_id,
            "--accept-source-agreements", "--accept-package-agreements"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

        total_lines = 80
        for i, line in enumerate(process.stdout):
            pct = min(int((i / total_lines) * 100), 100)
            progress["value"] = pct
        process.wait()

        if process.returncode == 0:
            label.config(text="✅ Installed")
            progress["value"] = 100
        else:
            label.config(text="❌ Failed")

    threading.Thread(target=task).start()

def check_gradle_installed():
    return GRADLE_DIR.exists()

def install_gradle(progress, label):
    def task():
        if check_gradle_installed():
            label.config(text="✅ Already Installed")
            progress["value"] = 100
            return

        zip_name = f"gradle-{GRADLE_VERSION}-bin.zip"
        zip_url = f"https://services.gradle.org/distributions/{zip_name}"

        label.config(text="Downloading...")
        with requests.get(zip_url, stream=True) as r:
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(zip_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    pct = int((downloaded / total) * 100)
                    progress["value"] = pct

        label.config(text="Extracting...")
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            zip_ref.extractall(GRADLE_DIR.parent)

        os.remove(zip_name)
        label.config(text="✅ Installed")
        progress["value"] = 100

    threading.Thread(target=task).start()

# GUI
root = Tk()
root.title(" Raef's Dev Tools Installer")
root.geometry("660x700")
root.configure(bg="#1a1a1a")

canvas = Canvas(root, bg="#1a1a1a", highlightthickness=0)
scrollbar = Scrollbar(root, command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

content = Frame(canvas, bg="#1a1a1a")
canvas.create_window((0, 0), window=content, anchor="nw")

def update_scroll(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
content.bind("<Configure>", update_scroll)

Label(content, text="🛠️ Raef Dev Setup", bg="#1a1a1a", fg="red", font=("Segoe UI", 16, "bold")).pack(pady=10)

def add_tool_ui(name, package_id):
    box = Frame(content, bg="#2a2a2a", padx=10, pady=5)
    box.pack(fill="x", padx=10, pady=5)

    Label(box, text=name, bg="#2a2a2a", fg="white", width=20, anchor="w", font=("Segoe UI", 11)).pack(side="left")
    status = Label(box, text="🔍 Checking...", fg="gray", bg="#2a2a2a", width=20)
    status.pack(side="right", padx=5)
    progress = ttk.Progressbar(box, length=100)
    progress.pack(side="right", padx=5)
    Button(box, text="Install", bg="red", fg="white", command=lambda: install_app(package_id, status, progress)).pack(side="right")

    def check_status():
        status.config(text="✅ Already Installed" if is_installed(package_id) else "❌ Not Installed")
    threading.Thread(target=check_status).start()

for name, pkg in APPS.items():
    add_tool_ui(name, pkg)

# Gradle UI
gradle_box = Frame(content, bg="#2a2a2a", padx=10, pady=5)
gradle_box.pack(fill="x", padx=10, pady=5)
Label(gradle_box, text="Gradle", bg="#2a2a2a", fg="white", width=20, anchor="w", font=("Segoe UI", 11)).pack(side="left")
gradle_status = Label(gradle_box, text="🔍 Checking...", fg="gray", bg="#2a2a2a", width=20)
gradle_status.pack(side="right", padx=5)
gradle_progress = ttk.Progressbar(gradle_box, length=100)
gradle_progress.pack(side="right", padx=5)
Button(gradle_box, text="Install", bg="red", fg="white", command=lambda: install_gradle(gradle_progress, gradle_status)).pack(side="right")
threading.Thread(target=lambda: gradle_status.config(text="✅ Already Installed" if check_gradle_installed() else "❌ Not Installed")).start()

root.mainloop()
