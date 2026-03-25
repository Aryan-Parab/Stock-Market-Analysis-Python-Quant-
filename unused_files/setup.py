import os
import subprocess
import sys
import urllib.request
import shutil
from pathlib import Path

def install_miniconda():
    """
    Download and install Miniconda on Windows
    """
    
    # Determine OS and architecture
    if sys.platform == "win32":
        installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
        installer_filename = "Miniconda3-latest-Windows-x86_64.exe"
    elif sys.platform == "darwin":  # macOS
        installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
        installer_filename = "Miniconda3-latest-MacOSX-x86_64.sh"
    elif sys.platform == "linux":
        installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        installer_filename = "Miniconda3-latest-Linux-x86_64.sh"
    else:
        print(f"Unsupported OS: {sys.platform}")
        return False
    
    # Check if Miniconda is already installed
    if shutil.which("conda") is not None:
        print("Miniconda is already installed!")
        return True
    
    # Download Miniconda
    print(f"Downloading Miniconda from {installer_url}...")
    try:
        urllib.request.urlretrieve(installer_url, installer_filename)
        print(f"Downloaded {installer_filename}")
    except Exception as e:
        print(f"Error downloading Miniconda: {e}")
        return False
    
    # Install Miniconda
    print("Installing Miniconda...")
    try:
        if sys.platform == "win32":
            # For Windows, run the .exe installer
            subprocess.run(
                [installer_filename, "/InstallationType=JustMe", "/AddToPath=1", "/RegisterPython=1"],
                check=True
            )
        else:
            # For macOS and Linux, run the .sh installer
            os.chmod(installer_filename, 0o755)
            subprocess.run(
                ["bash", installer_filename, "-b", "-p", os.path.expanduser("~/miniconda3")],
                check=True
            )
        
        print("Miniconda installed successfully!")
        
        # Clean up installer
        if os.path.exists(installer_filename):
            os.remove(installer_filename)
            print(f"Cleaned up {installer_filename}")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error installing Miniconda: {e}")
        return False


def install_docker():
    """
    Download and install Docker on Windows, macOS, or Linux
    """
    
    if sys.platform == "win32":
        return install_docker_windows()
    elif sys.platform == "darwin":  # macOS
        return install_docker_macos()
    elif sys.platform == "linux":
        return install_docker_linux()
    else:
        print(f"Unsupported OS: {sys.platform}")
        return False


def install_docker_windows():
    """
    Install Docker Desktop on Windows
    """
    print("Installing Docker Desktop for Windows...")
    
    # Check if Docker is already installed
    if shutil.which("docker") is not None:
        print("Docker is already installed!")
        return True
    
    try:
        # Download Docker Desktop installer
        installer_url = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"
        installer_filename = "DockerDesktopInstaller.exe"
        
        print(f"Downloading Docker Desktop from {installer_url}...")
        urllib.request.urlretrieve(installer_url, installer_filename)
        print(f"Downloaded {installer_filename}")
        
        # Run the installer
        print("Running Docker Desktop installer...")
        subprocess.run(
            [installer_filename, "install", "--quiet"],
            check=True
        )
        
        print("Docker Desktop installed successfully!")
        print("Note: You may need to restart your computer and enable WSL 2 (Windows Subsystem for Linux)")
        
        # Clean up
        if os.path.exists(installer_filename):
            os.remove(installer_filename)
            print(f"Cleaned up {installer_filename}")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error installing Docker: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def install_docker_macos():
    """
    Install Docker Desktop on macOS
    """
    print("Installing Docker Desktop for macOS...")
    
    # Check if Docker is already installed
    if shutil.which("docker") is not None:
        print("Docker is already installed!")
        return True
    
    try:
        # Check if Homebrew is installed
        if shutil.which("brew") is None:
            print("Homebrew is not installed. Installing Homebrew first...")
            subprocess.run(
                ["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"],
                check=True
            )
        
        # Install Docker using Homebrew
        print("Installing Docker using Homebrew...")
        subprocess.run(["brew", "install", "--cask", "docker"], check=True)
        
        print("Docker Desktop installed successfully!")
        print("Note: Docker Desktop application needs to be started from Applications folder")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error installing Docker: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def install_docker_linux():
    """
    Install Docker on Linux (Ubuntu/Debian)
    """
    print("Installing Docker on Linux...")
    
    # Check if Docker is already installed
    if shutil.which("docker") is not None:
        print("Docker is already installed!")
        return True
    
    try:
        # Update package manager
        print("Updating package manager...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        
        # Install Docker
        print("Installing Docker...")
        subprocess.run(
            ["sudo", "apt-get", "install", "-y", "docker.io"],
            check=True
        )
        
        # Add current user to docker group
        print("Adding current user to docker group...")
        subprocess.run(
            ["sudo", "usermod", "-aG", "docker", os.getenv("USER")],
            check=True
        )
        
        # Start Docker service
        print("Starting Docker service...")
        subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)
        
        # Enable Docker service on boot
        print("Enabling Docker service on boot...")
        subprocess.run(["sudo", "systemctl", "enable", "docker"], check=True)
        
        print("Docker installed successfully!")
        print("Note: You may need to restart your terminal or log out and back in for group changes to take effect")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error installing Docker: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def verify_installation():
    """
    Verify both Miniconda and Docker installation
    """
    print("\n" + "="*60)
    print("VERIFYING INSTALLATIONS")
    print("="*60)
    
    # Verify Miniconda
    try:
        result = subprocess.run(
            ["conda", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Miniconda: {result.stdout.strip()}")
    except Exception as e:
        print(f"✗ Miniconda verification failed: {e}")
    
    # Verify Docker
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Docker: {result.stdout.strip()}")
    except Exception as e:
        print(f"✗ Docker verification failed: {e}")
    
    print("="*60)


def main():
    """
    Main installation flow
    """
    print("="*60)
    print("COMBINED MINICONDA & DOCKER INSTALLER")
    print("="*60)
    print()
    
    # Install Miniconda
    print("[1/2] Installing Miniconda...")
    print("-" * 60)
    miniconda_success = install_miniconda()
    print()
    
    # Install Docker
    print("[2/2] Installing Docker...")
    print("-" * 60)
    docker_success = install_docker()
    print()
    
    # Verify installations
    verify_installation()
    
    # Summary
    print("\nSUMMARY")
    print("="*60)
    print(f"Miniconda: {'✓ Installed' if miniconda_success else '✗ Failed'}")
    print(f"Docker:    {'✓ Installed' if docker_success else '✗ Failed'}")
    print("="*60)
    
    return miniconda_success and docker_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
