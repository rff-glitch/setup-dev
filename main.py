import requests, zipfile, os, shutil, subprocess
from pathlib import Path

def IsAppInstalled(Package_ID):
    result = subprocess.run([
        "winget", "list", Package_ID],
        shell=True, capture_output=True, text=True )
    return Package_ID.lower() in result.stdout.lower()


def installAppUsingWinget(Package_ID):
    if IsAppInstalled(Package_ID):
        print(f"{Package_ID} is already installed.")
        return
    
    print(f"Installing {Package_ID}...")
    result = subprocess.run([
            "winget" , "install" , Package_ID ,
            "--accept-source-agreements",
            "--accept-package-agreements"
        ], shell=True , capture_output=True, text=True)
        
    if result.returncode == 0:
        print(f"{Package_ID} installed successfully.")
    else:
        print(f"Failed to install {Package_ID}. Error: {result.stderr}")


#Install APPS
apps = [
    "neofetch",
    "Google.Chrome",
    "Microsoft.VisualStudioCode",
    "Git.Git",
    "Microsoft.VisualStudio.2022.Community",
    "Google.AndroidStudio",
    "Python.Python.3",
    "OpenJS.NodeJS",
    "RubyInstallerTeam.Ruby",
    "Kitware.CMake",
    "EclipseAdoptium.Temurin.17.JDK",
    "RARLab.WinRAR",
    
]

for app in apps :
    installAppUsingWinget(app)


#install Gradle

def install_gradle(version="8.5"):
    gradle_dir = Path(f"C:/Gradle")
    gradle_subdir = gradle_dir / f"gradle-{version}"
    gradle_bin = gradle_subdir / "bin"
    zip_name = f"gradle-{version}-bin.zip"
    zip_url = f"https://services.gradle.org/distributions/{zip_name}"
    
    # Check if  installed
    if gradle_subdir.exists():
        print(f"Gradle {version} already extracted.")
    else:
        print(f" Downloading Gradle {version}...")
        r = requests.get(zip_url, stream=True)
        with open(zip_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        print(" Extracting...")
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            zip_ref.extractall(gradle_dir)

        os.remove(zip_name)
        print(f"Gradle {version} installed to {gradle_subdir}")


install_gradle()