
import subprocess

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
    "Google.AndroidPlatformTools",
    "Google.AndroidSdk.CommandlineTools",
    "Python.Python.3",
    "OpenJS.NodeJS",
    "RubyInstallerTeam.Ruby",
    "gradle",
    "Kitware.CMake",
    "EclipseAdoptium.Temurin.17.JDK",
    "RARLab.WinRAR",
    
]

for app in apps :
    installAppUsingWinget(app)