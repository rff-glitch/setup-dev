
import subprocess, requests, zipfile, os, threading, time
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
    "Go Lang": "GoLang.Go",
}

GRADLE_VERSION = "8.5"
GRADLE_DIR = Path(f"C:/Gradle/gradle-{GRADLE_VERSION}")

# Environment variables configuration
ENV_VARS = {
    "JAVA_HOME": [
        "C:/Program Files/Eclipse Adoptium/jdk-17*",
        "C:/Program Files/Java/jdk-17*",
        "C:/Program Files/OpenJDK/jdk-17*"
    ],
    "ANDROID_HOME": [
        os.path.expanduser("~/AppData/Local/Android/Sdk"),
        "C:/Users/*/AppData/Local/Android/Sdk"
    ],
    "ANDROID_SDK_ROOT": [
        os.path.expanduser("~/AppData/Local/Android/Sdk"),
        "C:/Users/*/AppData/Local/Android/Sdk"
    ],
    "GOPATH": [
        os.path.expanduser("~/go"),
        "C:/Users/*/go"
    ],
    "GOROOT": [
        "C:/Program Files/Go",
        "C:/Go"
    ]
}

def find_installation_path(possible_paths):
    import glob
    for path_pattern in possible_paths:
        if '*' in path_pattern:
            matches = glob.glob(path_pattern)
            if matches:
                return matches[0]
        else:
            if os.path.exists(path_pattern):
                return path_pattern
    return None

def set_environment_variable(var_name, var_value):
    try:
        os.environ[var_name] = var_value
        subprocess.run([
            "setx", var_name, var_value, "/M"
        ], check=True, capture_output=True)

        if var_name in ["JAVA_HOME", "GOROOT"]:
            bin_path = os.path.join(var_value, "bin")
            if os.path.exists(bin_path):
                subprocess.run([
                    "setx", "PATH", f"%PATH%;{bin_path}", "/M"
                ], capture_output=True)
        return True
    except Exception as e:
        print(f"Error setting {var_name}: {e}")
        return False

def setup_environment_variables():
    results = {}
    for var_name, possible_paths in ENV_VARS.items():
        actual_path = find_installation_path(possible_paths)
        if actual_path:
            success = set_environment_variable(var_name, actual_path)
            results[var_name] = {"path": actual_path, "success": success}
        else:
            results[var_name] = {"path": None, "success": False}

    if GRADLE_DIR.exists():
        gradle_bin = str(GRADLE_DIR / "bin")
        success = set_environment_variable("GRADLE_HOME", str(GRADLE_DIR))
        if success:
            subprocess.run([
                "setx", "PATH", f"%PATH%;{gradle_bin}", "/M"
            ], capture_output=True)
        results["GRADLE_HOME"] = {"path": str(GRADLE_DIR), "success": success}

    return results

def is_installed(package_id):
    result = subprocess.run(["winget", "list", package_id], capture_output=True, text=True, shell=True)
    return package_id.lower() in result.stdout.lower()

def install_app(package_id, status, progress):
    def task():
        if is_installed(package_id):
            status.config(text="✅ Already Installed", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")
            return

        status.config(text="Installing...", fg="yellow")
        progress["value"] = 0
        progress.config(style="installing.Horizontal.TProgressbar")

        process = subprocess.Popen([
            "winget", "install", package_id,
            "--accept-source-agreements", "--accept-package-agreements"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

        phases = [
            ("📋 Preparing...", 10),
            ("⬇️ Downloading...", 30),
            ("📦 Extracting...", 60),
            ("⚙️ Installing...", 80),
            ("🔧 Finalizing...", 95)
        ] 

        phase_index = 0
        line_count = 0

        for line in process.stdout:
            line_count += 1
            if line_count % 15 == 0 and phase_index < len(phases):
                phase_text, target_progress = phases[phase_index]
                status.config(text=phase_text, fg="yellow")
                current = progress["value"]
                for i in range(int(current), target_progress + 1):
                    progress["value"] = i
                    root.update_idletasks()
                    time.sleep(0.02)
                phase_index += 1

        process.wait()

        if process.returncode == 0:
            status.config(text="✅ Installed Successfully", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")
        else:
            status.config(text="❌ Installation Failed", fg="#FF6666")
            progress["value"] = 0
            progress.config(style="error.Horizontal.TProgressbar")

    threading.Thread(target=task, daemon=True).start()

def install_tor_browser(status, progress):
    """Custom install for Tor Browser with special winget command"""
    def task():
        package_id = "TorProject.TorBrowser"
        if is_installed(package_id):
            status.config(text="✅ Already Installed", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")
            return

        status.config(text=" Installing Tor Browser...", fg="yellow")
        progress["value"] = 0
        progress.config(style="installing.Horizontal.TProgressbar")

        process = subprocess.Popen([
            "winget", "install", "--id=TorProject.TorBrowser", "-e", "--accept-source-agreements", "--accept-package-agreements"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

        line_count = 0
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line_count += 1
            if line_count % 15 == 0:
                # Fake progress animation for Tor install
                current = progress["value"]
                target = min(current + 15, 95)
                for i in range(current, target + 1):
                    progress["value"] = i
                    root.update_idletasks()
                    time.sleep(0.02)

        process.wait()

        if process.returncode == 0:
            status.config(text="✅ Installed Successfully", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")
        else:
            status.config(text="❌ Installation Failed", fg="#FF6666")
            progress["value"] = 0
            progress.config(style="error.Horizontal.TProgressbar")

    threading.Thread(target=task, daemon=True).start()

def check_gradle_installed():
    return GRADLE_DIR.exists()

def install_gradle(progress, label):
    def task():
        if check_gradle_installed():
            label.config(text="✅ Already Installed", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")
            return

        try:
            zip_name = f"gradle-{GRADLE_VERSION}-bin.zip"
            zip_url = f"https://services.gradle.org/distributions/{zip_name}"

            label.config(text="⬇️ Downloading...", fg="yellow")
            progress["value"] = 0
            progress.config(style="installing.Horizontal.TProgressbar")

            with requests.get(zip_url, stream=True) as r:
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(zip_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = int((downloaded / total) * 70)  # 70% for download
                            progress["value"] = pct
                            root.update_idletasks()

            label.config(text="📦 Extracting...", fg="yellow")
            progress["value"] = 75
            root.update_idletasks()

            with zipfile.ZipFile(zip_name, 'r') as zip_ref:
                zip_ref.extractall(GRADLE_DIR.parent)

            progress["value"] = 95
            root.update_idletasks()

            os.remove(zip_name)
            label.config(text="✅ Installed Successfully", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")

        except Exception as e:
            label.config(text="❌ Installation Failed", fg="#FF6666")
            progress["value"] = 0
            progress.config(style="error.Horizontal.TProgressbar")

    threading.Thread(target=task, daemon=True).start()

# GUI Setup
root = Tk()
root.title(" Tools Installer")
root.geometry("610x700")
root.configure(bg="#1a1a1a")

# Configure styles with red theme
style = ttk.Style()
style.theme_use('clam')

style.configure("installing.Horizontal.TProgressbar", 
               background="red", 
               troughcolor="#333333",
               borderwidth=0,
               lightcolor="red",
               darkcolor="red")

style.configure("success.Horizontal.TProgressbar", 
               background="#00AA00", 
               troughcolor="#333333",
               borderwidth=0,
               lightcolor="#00AA00",
               darkcolor="#00AA00")

style.configure("error.Horizontal.TProgressbar", 
               background="#AA0000", 
               troughcolor="#333333",
               borderwidth=0,
               lightcolor="#AA0000",
               darkcolor="#AA0000")

# Scrollable content area
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

def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", on_mousewheel)

Label(content, text="🛠️ Raef ", bg="#1a1a1a", fg="red", font=("Segoe UI", 16, "bold")).pack(pady=10)

def add_tool_ui(name, package_id):
    box = Frame(content, bg="#2a2a2a", padx=15, pady=8, relief="flat", bd=1)
    box.pack(fill="x", padx=10, pady=6)

    Label(box, text=name, bg="#2a2a2a", fg="white", 
          width=20, anchor="w", font=("Segoe UI", 11, "bold")).pack(side="left")

    Button(box, text="Install", bg="red", fg="white", 
           font=("Segoe UI", 10, "bold"), relief="flat", bd=0, padx=15, pady=3,
           activebackground="#cc0000", activeforeground="white",
           command=lambda: install_app(package_id, status, progress)).pack(side="right")

    progress = ttk.Progressbar(box, length=120, mode='determinate')
    progress.pack(side="right", padx=8)

    status = Label(box, text="🔍 Checking...", fg="gray", bg="#2a2a2a", 
                  width=18, font=("Segoe UI", 10))
    status.pack(side="right", padx=5)

    def check_status():
        if is_installed(package_id):
            status.config(text="✅ Already Installed", fg="#00AA00")
            progress["value"] = 100
            progress.config(style="success.Horizontal.TProgressbar")
        else:
            status.config(text="❌ Not Installed", fg="#FF6666")
            progress["value"] = 0

    threading.Thread(target=check_status, daemon=True).start()

# Add all regular applications
for name, pkg in APPS.items():
    add_tool_ui(name, pkg)

# Special case for Tor Browser
tor_box = Frame(content, bg="#2a2a2a", padx=15, pady=8, relief="flat", bd=1)
tor_box.pack(fill="x", padx=10, pady=6)

Label(tor_box, text="Tor Browser", bg="#2a2a2a", fg="white", 
      width=20, anchor="w", font=("Segoe UI", 11, "bold")).pack(side="left")

Button(tor_box, text="Install", bg="red", fg="white", 
       font=("Segoe UI", 10, "bold"), relief="flat", bd=0, padx=15, pady=3,
       activebackground="#cc0000", activeforeground="white",
       command=lambda: install_tor_browser(tor_status, tor_progress)).pack(side="right")

tor_progress = ttk.Progressbar(tor_box, length=120, mode='determinate')
tor_progress.pack(side="right", padx=8)

tor_status = Label(tor_box, text="🔍 Checking...", fg="gray", bg="#2a2a2a", 
                   width=18, font=("Segoe UI", 10))
tor_status.pack(side="right", padx=5)

def check_tor_status():
    if is_installed("TorProject.TorBrowser"):
        tor_status.config(text="✅ Already Installed", fg="#00AA00")
        tor_progress["value"] = 100
        tor_progress.config(style="success.Horizontal.TProgressbar")
    else:
        tor_status.config(text="❌ Not Installed", fg="#FF6666")
        tor_progress["value"] = 0

threading.Thread(target=check_tor_status, daemon=True).start()

# Gradle special case
gradle_box = Frame(content, bg="#2a2a2a", padx=15, pady=8, relief="flat", bd=1)
gradle_box.pack(fill="x", padx=10, pady=6)

Label(gradle_box, text="Gradle", bg="#2a2a2a", fg="white", 
      width=20, anchor="w", font=("Segoe UI", 11, "bold")).pack(side="left")

Button(gradle_box, text="Install", bg="red", fg="white", 
       font=("Segoe UI", 10, "bold"), relief="flat", bd=0, padx=15, pady=3,
       activebackground="#cc0000", activeforeground="white",
       command=lambda: install_gradle(gradle_progress, gradle_status)).pack(side="right")

gradle_progress = ttk.Progressbar(gradle_box, length=120, mode='determinate')
gradle_progress.pack(side="right", padx=8)

gradle_status = Label(gradle_box, text="🔍 Checking...", fg="gray", bg="#2a2a2a", 
                     width=18, font=("Segoe UI", 10))
gradle_status.pack(side="right", padx=5)

def check_gradle_status():
    if check_gradle_installed():
        gradle_status.config(text="✅ Already Installed", fg="#00AA00")
        gradle_progress["value"] = 100
        gradle_progress.config(style="success.Horizontal.TProgressbar")
    else:
        gradle_status.config(text="❌ Not Installed", fg="#FF6666")
        gradle_progress["value"] = 0

threading.Thread(target=check_gradle_status, daemon=True).start()

root.mainloop()
