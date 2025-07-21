#!/usr/bin/env python3
"""
LoopScan Installation Script
Handles healpy installation issues across different platforms
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"Running: {cmd}")
    if description:
        print(f"  {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"  ✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed: {e}")
        if e.stdout:
            print(f"  stdout: {e.stdout}")
        if e.stderr:
            print(f"  stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required for LoopScan")
        return False
    
    print("✓ Python version compatible")
    return True

def detect_platform():
    """Detect the operating system and architecture"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print(f"Platform: {system} {machine}")
    
    platform_info = {
        'system': system,
        'machine': machine,
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin',
        'is_linux': system == 'linux',
        'is_arm': 'arm' in machine or 'aarch64' in machine
    }
    
    return platform_info

def check_conda_available():
    """Check if conda is available"""
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Conda available: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("ℹ Conda not available")
    return False

def install_with_conda():
    """Install packages using conda"""
    print("\n🔧 Installing with conda...")
    
    packages = [
        "numpy", "scipy", "matplotlib", "pandas", "jupyter",
        "astropy", "scikit-image", "seaborn", "tqdm", "numba"
    ]
    
    # Install healpy separately from conda-forge
    if not run_command("conda install -c conda-forge healpy -y", 
                      "Installing healpy from conda-forge"):
        return False
    
    # Install other packages
    package_str = " ".join(packages)
    if not run_command(f"conda install {package_str} -y", 
                      "Installing other packages"):
        return False
    
    return True

def install_system_dependencies_linux():
    """Install system dependencies on Linux"""
    print("\n🔧 Installing Linux system dependencies...")
    
    # Try different package managers
    commands = [
        # Ubuntu/Debian
        "sudo apt-get update && sudo apt-get install -y build-essential gfortran libcfitsio-dev pkg-config",
        # CentOS/RHEL (older)
        "sudo yum install -y gcc-gfortran cfitsio-devel pkgconfig",
        # Fedora/CentOS (newer)
        "sudo dnf install -y gcc-gfortran cfitsio-devel pkgconfig"
    ]
    
    for cmd in commands:
        if run_command(cmd, "Installing system dependencies"):
            return True
    
    print("⚠ Could not install system dependencies automatically")
    print("Please install manually:")
    print("  Ubuntu/Debian: sudo apt-get install build-essential gfortran libcfitsio-dev")
    print("  CentOS/RHEL: sudo yum install gcc-gfortran cfitsio-devel")
    print("  Fedora: sudo dnf install gcc-gfortran cfitsio-devel")
    
    return False

def install_system_dependencies_macos():
    """Install system dependencies on macOS"""
    print("\n🔧 Installing macOS system dependencies...")
    
    # Check for Xcode command line tools
    if not run_command("xcode-select -p", "Checking Xcode tools"):
        print("Installing Xcode command line tools...")
        if not run_command("xcode-select --install", "Installing Xcode tools"):
            print("⚠ Please install Xcode command line tools manually")
            return False
    
    # Try to install cfitsio with Homebrew
    if run_command("brew --version", "Checking Homebrew"):
        run_command("brew install cfitsio", "Installing cfitsio")
    
    return True

def install_with_pip(platform_info):
    """Install packages using pip"""
    print("\n🔧 Installing with pip...")
    
    # Install system dependencies first
    if platform_info['is_linux']:
        install_system_dependencies_linux()
    elif platform_info['is_macos']:
        install_system_dependencies_macos()
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", 
                "Upgrading pip")
    
    # Try different healpy installation methods
    healpy_methods = [
        # Method 1: Try pre-compiled wheel
        f"{sys.executable} -m pip install --only-binary=healpy healpy",
        # Method 2: Standard installation
        f"{sys.executable} -m pip install healpy",
        # Method 3: No cache (sometimes helps)
        f"{sys.executable} -m pip install --no-cache-dir healpy",
        # Method 4: Force reinstall
        f"{sys.executable} -m pip install --force-reinstall healpy"
    ]
    
    healpy_installed = False
    for method in healpy_methods:
        print(f"\nTrying healpy installation method...")
        if run_command(method, "Installing healpy"):
            healpy_installed = True
            break
        print("Method failed, trying next...")
    
    if not healpy_installed:
        print("❌ All healpy installation methods failed")
        return False
    
    # Install other requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing other requirements"):
        print("⚠ Some packages may have failed to install")
    
    return True

def create_conda_environment():
    """Create a dedicated conda environment for LoopScan"""
    print("\n🔧 Creating conda environment...")
    
    env_name = "loopscan"
    
    # Remove existing environment if it exists
    run_command(f"conda env remove -n {env_name} -y", 
                "Removing existing environment")
    
    # Create new environment
    if not run_command(f"conda create -n {env_name} python=3.9 -y", 
                      "Creating new environment"):
        return False
    
    # Activate and install packages
    activate_cmd = f"conda activate {env_name} && "
    
    if not run_command(f"{activate_cmd}conda install -c conda-forge healpy numpy scipy matplotlib astropy scikit-image pandas jupyter seaborn tqdm numba -y", 
                      "Installing packages in environment"):
        return False
    
    print(f"\n✓ Created conda environment '{env_name}'")
    print(f"To use LoopScan, activate the environment:")
    print(f"  conda activate {env_name}")
    
    return True

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing installation...")
    
    # Run the test script
    if Path("test_healpy.py").exists():
        return run_command(f"{sys.executable} test_healpy.py", 
                          "Running installation tests")
    else:
        # Quick inline test
        test_code = """
import healpy as hp
import numpy as np
import matplotlib.pyplot as plt
print("✓ All imports successful")
nside = 32
test_map = np.random.randn(hp.nside2npix(nside))
print(f"✓ Created test map with {len(test_map)} pixels")
"""
        
        try:
            exec(test_code)
            print("✓ Basic functionality test passed")
            return True
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False

def main():
    """Main installation routine"""
    print("🌀 LoopScan Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Detect platform
    platform_info = detect_platform()
    
    # Check for conda
    has_conda = check_conda_available()
    
    # Installation strategy
    if has_conda:
        print("\n📋 Installation Strategy: Conda (Recommended)")
        print("Conda provides the most reliable healpy installation")
        
        choice = input("\nChoose installation method:\n"
                      "1. Install in current environment\n"
                      "2. Create new conda environment (recommended)\n"
                      "3. Use pip instead\n"
                      "Enter choice (1-3): ").strip()
        
        if choice == "2":
            success = create_conda_environment()
        elif choice == "1":
            success = install_with_conda()
        else:
            success = install_with_pip(platform_info)
    else:
        print("\n📋 Installation Strategy: Pip")
        print("Conda not available, using pip installation")
        success = install_with_pip(platform_info)
    
    if success:
        print("\n✅ Installation completed!")
        
        # Test installation
        if test_installation():
            print("\n🎉 LoopScan is ready to use!")
            print("\nNext steps:")
            print("1. python loopscan.py synthetic --plot")
            print("2. Download CMB data (see data/README.md)")
            print("3. python loopscan.py real --data-file your_data.fits")
        else:
            print("\n⚠ Installation completed but tests failed")
            print("Try running: python test_healpy.py")
    else:
        print("\n❌ Installation failed!")
        print("\nTroubleshooting:")
        print("1. Check SETUP.md for detailed instructions")
        print("2. Try conda installation if using pip")
        print("3. Install system dependencies manually")
        print("4. Use Docker as alternative (see SETUP.md)")

if __name__ == "__main__":
    main()