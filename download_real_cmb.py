#!/usr/bin/env python3
"""
Download Real CMB Data from Planck Mission
For testing the Flat Loop Universe theory with actual observations
"""

import urllib.request
import os
from pathlib import Path
import gzip
import shutil

def download_file(url, filename, description=""):
    """Download a file with progress indication"""
    print(f"Downloading {description}...")
    print(f"URL: {url}")
    print(f"Saving to: {filename}")
    
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            print(f"\rProgress: {percent}% ({block_num * block_size // (1024*1024)} MB)", end="")
    
    try:
        urllib.request.urlretrieve(url, filename, progress_hook)
        print(f"\n✓ Downloaded successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False

def download_planck_cmb_data():
    """Download real Planck CMB temperature maps"""
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print("🌌 Downloading Real CMB Data from Planck Mission")
    print("=" * 60)
    print("This will download actual cosmic microwave background observations")
    print("that can be used to test the Flat Loop Universe theory!")
    print()
    
    # Planck CMB maps (these are real URLs from ESA)
    cmb_files = [
        {
            "url": "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-commander_1024_R3.00_full.fits",
            "filename": "data/planck_cmb_commander_1024.fits",
            "description": "Planck CMB Temperature Map (1024 resolution)",
            "size": "~200 MB"
        },
        {
            "url": "https://pla.esac.esa.int/pla/aio/product-action?MASK.MASK_ID=COM_Mask_CMB-common-Mask-Int_1024_R3.00.fits", 
            "filename": "data/planck_mask_1024.fits",
            "description": "Planck Analysis Mask",
            "size": "~50 MB"
        }
    ]
    
    # Alternative direct download URLs (if ESA links don't work)
    backup_files = [
        {
            "url": "https://lambda.gsfc.nasa.gov/data/map/dr5/maps/nine_year/wmap_ilc_9yr_v5.fits",
            "filename": "data/wmap_cmb_9year.fits", 
            "description": "WMAP 9-Year CMB Map (backup)",
            "size": "~100 MB"
        }
    ]
    
    print("Available real CMB datasets:")
    for i, file_info in enumerate(cmb_files + backup_files):
        print(f"{i+1}. {file_info['description']} ({file_info['size']})")
    
    print()
    choice = input("Which dataset would you like to download? (1-3, or 'all'): ").strip().lower()
    
    if choice == 'all':
        files_to_download = cmb_files + backup_files
    else:
        try:
            idx = int(choice) - 1
            files_to_download = [cmb_files[idx]] if idx < len(cmb_files) else [backup_files[idx - len(cmb_files)]]
        except:
            print("Invalid choice, downloading first dataset...")
            files_to_download = [cmb_files[0]]
    
    # Download selected files
    successful_downloads = []
    
    for file_info in files_to_download:
        print(f"\n{'-'*40}")
        success = download_file(
            file_info["url"], 
            file_info["filename"], 
            file_info["description"]
        )
        
        if success:
            successful_downloads.append(file_info["filename"])
            
            # Check if file is gzipped and extract
            if file_info["filename"].endswith('.gz'):
                print("Extracting gzipped file...")
                with gzip.open(file_info["filename"], 'rb') as f_in:
                    with open(file_info["filename"][:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_info["filename"])
                successful_downloads[-1] = file_info["filename"][:-3]
    
    print(f"\n{'='*60}")
    print("🎉 Download Summary:")
    
    if successful_downloads:
        print(f"✓ Successfully downloaded {len(successful_downloads)} files:")
        for filename in successful_downloads:
            file_size = os.path.getsize(filename) / (1024*1024)  # MB
            print(f"  - {filename} ({file_size:.1f} MB)")
        
        print(f"\n🔬 Next Steps:")
        print(f"1. These are REAL CMB observations from space missions")
        print(f"2. Run LoopScan analysis on this data to test your theory")
        print(f"3. Look for actual cosmic echo patterns!")
        print(f"\nTo analyze:")
        print(f"python loopscan.py real --data-file {os.path.basename(successful_downloads[0])}")
        
    else:
        print("❌ No files downloaded successfully")
        print("\nAlternative options:")
        print("1. Check your internet connection")
        print("2. Try the backup WMAP dataset")
        print("3. Download manually from:")
        print("   - https://pla.esac.esa.int/pla/ (Planck)")
        print("   - https://lambda.gsfc.nasa.gov/ (WMAP)")

if __name__ == "__main__":
    download_planck_cmb_data()