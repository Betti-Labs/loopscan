# LoopScan Setup Guide

## HEALPix and healpy Installation

### Common healpy Installation Issues & Solutions

#### 1. **Windows Installation Issues**

**Problem**: healpy fails to install on Windows due to missing C++ compiler
```
error: Microsoft Visual C++ 14.0 is required
```

**Solutions**:
```bash
# Option A: Use conda (recommended for Windows)
conda install -c conda-forge healpy

# Option B: Install Visual Studio Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Then: pip install healpy

# Option C: Use pre-compiled wheels
pip install --only-binary=healpy healpy
```

#### 2. **macOS Installation Issues**

**Problem**: Compilation errors with Xcode command line tools
```bash
# Install Xcode command line tools first
xcode-select --install

# Then install healpy
pip install healpy

# If still failing, use conda
conda install -c conda-forge healpy
```

#### 3. **Linux Installation Issues**

**Problem**: Missing system dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential gfortran libcfitsio-dev

# CentOS/RHEL/Fedora
sudo yum install gcc-gfortran cfitsio-devel
# or for newer versions:
sudo dnf install gcc-gfortran cfitsio-devel

# Then install healpy
pip install healpy
```

#### 4. **Memory Issues with Large Maps**

**Problem**: Out of memory errors with high-resolution maps
```python
# Use lower resolution for testing
nside = 256  # instead of 2048
# This reduces memory from ~8GB to ~64MB

# Or use memory mapping for large files
import healpy as hp
map_data = hp.read_map("large_file.fits", memmap=True)
```

### Recommended Installation Method

```bash
# Create virtual environment
python -m venv loopscan_env
source loopscan_env/bin/activate  # Linux/Mac
# or
loopscan_env\Scripts\activate     # Windows

# Install using conda (most reliable)
conda install -c conda-forge healpy numpy matplotlib scipy astropy scikit-image pandas jupyter seaborn tqdm

# Or using pip with specific versions
pip install healpy>=1.16.0 numpy>=1.21.0 matplotlib>=3.5.0 scipy>=1.7.0 astropy>=5.0.0 scikit-image>=0.19.0 pandas>=1.3.0 jupyter>=1.0.0 seaborn>=0.11.0 tqdm>=4.62.0
```

### Testing healpy Installation

```python
# Test script to verify healpy works
import healpy as hp
import numpy as np

# Test basic functionality
nside = 32
npix = hp.nside2npix(nside)
print(f"nside={nside}, npix={npix}")

# Generate test map
test_map = np.random.randn(npix)
print(f"Generated map with {len(test_map)} pixels")

# Test visualization
import matplotlib.pyplot as plt
hp.mollview(test_map, title="Test Map")
plt.savefig("test_healpy.png")
print("healpy installation successful!")
```

### CMB Data Sources

#### Planck Data
```bash
# Download Planck CMB temperature map (1.2GB)
wget "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-commander_2048_R3.00_full.fits" -O data/planck_cmb_commander_2048.fits

# Download lower resolution version for testing (smaller file)
wget "https://pla.esac.esa.int/pla/aio/product-action?MAP.MAP_ID=COM_CMB_IQU-commander_1024_R3.00_full.fits" -O data/planck_cmb_commander_1024.fits
```

#### WMAP Data
```bash
# WMAP 9-year temperature map
wget "https://lambda.gsfc.nasa.gov/data/map/dr5/maps/nine_year/wmap_ilc_9yr_v5.fits" -O data/wmap_ilc_9yr.fits
```

### Performance Optimization

#### For Large-Scale Analysis
```python
# Use multiprocessing for correlation calculations
from multiprocessing import Pool
import healpy as hp

def parallel_correlation(args):
    """Function for parallel processing"""
    patch1, patch2 = args
    return np.corrcoef(patch1, patch2)[0,1]

# Process multiple correlations in parallel
with Pool() as pool:
    correlations = pool.map(parallel_correlation, patch_pairs)
```

#### Memory Management
```python
# For very large maps, process in chunks
def process_map_chunks(cmb_map, chunk_size=1000000):
    """Process large maps in smaller chunks"""
    npix = len(cmb_map)
    for i in range(0, npix, chunk_size):
        chunk = cmb_map[i:i+chunk_size]
        # Process chunk
        yield process_chunk(chunk)
```

### Troubleshooting Common Runtime Errors

#### 1. **FITS File Reading Errors**
```python
# Check file exists and is readable
import os
from pathlib import Path

fits_file = "data/cmb_map.fits"
if not Path(fits_file).exists():
    print(f"File not found: {fits_file}")
    
# Try reading with error handling
try:
    cmb_map = hp.read_map(fits_file, verbose=False)
    print(f"Successfully loaded map with {len(cmb_map)} pixels")
except Exception as e:
    print(f"Error reading FITS file: {e}")
    print("Try downloading the file again or check file permissions")
```

#### 2. **Coordinate System Issues**
```python
# Ensure consistent coordinate systems
# Planck data is usually in Galactic coordinates
# Convert if needed:
import healpy as hp

# Rotate from Galactic to Equatorial if needed
rotator = hp.Rotator(coord=['G', 'C'])  # Galactic to Celestial
rotated_map = rotator.rotate_map_pixel(cmb_map)
```

#### 3. **Visualization Backend Issues**
```python
# If plots don't show, try different backends
import matplotlib
matplotlib.use('Agg')  # For headless systems
# or
matplotlib.use('TkAgg')  # For interactive plots

import matplotlib.pyplot as plt
```

### Docker Setup (Alternative)

If installation continues to be problematic, use Docker:

```dockerfile
# Dockerfile for LoopScan
FROM continuumio/miniconda3

RUN conda install -c conda-forge healpy numpy matplotlib scipy astropy scikit-image pandas jupyter seaborn tqdm

WORKDIR /loopscan
COPY . .

CMD ["python", "loopscan.py", "synthetic", "--plot"]
```

```bash
# Build and run
docker build -t loopscan .
docker run -v $(pwd)/outputs:/loopscan/outputs loopscan
```

### Verification Checklist

- [ ] healpy imports without errors
- [ ] Can create and visualize test maps
- [ ] Can read FITS files
- [ ] Matplotlib plots display correctly
- [ ] All dependencies installed
- [ ] CMB data files downloaded
- [ ] Sufficient RAM for chosen nside resolution

Run the test script above to verify your installation before proceeding with LoopScan analysis.