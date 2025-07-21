#!/usr/bin/env python3
"""
Test script to verify healpy installation and basic functionality
Run this before using LoopScan to ensure everything works
"""

import sys
import traceback

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    packages = [
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('scipy', None),
        ('astropy', None),
        ('skimage', None),
        ('pandas', 'pd'),
        ('healpy', 'hp')
    ]
    
    failed_imports = []
    
    for package, alias in packages:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"  ✓ {package}")
        except ImportError as e:
            print(f"  ✗ {package} - {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_healpy_basic():
    """Test basic healpy functionality"""
    print("\nTesting healpy basic functionality...")
    
    try:
        import healpy as hp
        import numpy as np
        
        # Test nside calculations
        nside = 32
        npix = hp.nside2npix(nside)
        print(f"  ✓ nside={nside} -> npix={npix}")
        
        # Test map creation
        test_map = np.random.randn(npix)
        print(f"  ✓ Created random map with {len(test_map)} pixels")
        
        # Test coordinate conversions
        theta, phi = hp.pix2ang(nside, 0)
        pixel = hp.ang2pix(nside, theta, phi)
        print(f"  ✓ Coordinate conversion: pixel 0 -> ({theta:.3f}, {phi:.3f}) -> pixel {pixel}")
        
        # Test angular distance
        vec1 = hp.ang2vec(0, 0)
        vec2 = hp.ang2vec(np.pi/2, 0)
        dist = hp.rotator.angdist(vec1, vec2)
        print(f"  ✓ Angular distance calculation: {np.degrees(dist):.1f}°")
        
        return True
        
    except Exception as e:
        print(f"  ✗ healpy basic test failed: {e}")
        traceback.print_exc()
        return False

def test_healpy_visualization():
    """Test healpy visualization capabilities"""
    print("\nTesting healpy visualization...")
    
    try:
        import healpy as hp
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create test map
        nside = 32
        npix = hp.nside2npix(nside)
        test_map = np.random.randn(npix)
        
        # Test mollweide projection
        plt.figure(figsize=(10, 6))
        hp.mollview(test_map, title="Test Map", cbar=True)
        
        # Try to save plot
        plt.savefig("test_healpy_plot.png", dpi=150, bbox_inches='tight')
        print("  ✓ Mollweide projection created and saved")
        
        plt.close()
        return True
        
    except Exception as e:
        print(f"  ✗ healpy visualization test failed: {e}")
        traceback.print_exc()
        return False

def test_fits_io():
    """Test FITS file I/O capabilities"""
    print("\nTesting FITS file I/O...")
    
    try:
        import healpy as hp
        import numpy as np
        from pathlib import Path
        
        # Create test data
        nside = 32
        npix = hp.nside2npix(nside)
        test_map = np.random.randn(npix)
        
        # Test writing FITS file
        test_file = "test_map.fits"
        hp.write_map(test_file, test_map, overwrite=True)
        print(f"  ✓ Wrote test map to {test_file}")
        
        # Test reading FITS file
        loaded_map = hp.read_map(test_file, verbose=False)
        print(f"  ✓ Read test map from {test_file}")
        
        # Verify data integrity
        if np.allclose(test_map, loaded_map):
            print("  ✓ Data integrity verified")
        else:
            print("  ✗ Data integrity check failed")
            return False
        
        # Clean up
        Path(test_file).unlink()
        print("  ✓ Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FITS I/O test failed: {e}")
        traceback.print_exc()
        return False

def test_loopscan_modules():
    """Test LoopScan module imports"""
    print("\nTesting LoopScan module imports...")
    
    try:
        sys.path.append('src')
        
        from data_loader import CMBDataLoader
        print("  ✓ data_loader module")
        
        from echo_detector import EchoDetector
        print("  ✓ echo_detector module")
        
        from visualizer import CMBVisualizer
        print("  ✓ visualizer module")
        
        from synthetic_data import SyntheticCMBGenerator
        print("  ✓ synthetic_data module")
        
        return True
        
    except Exception as e:
        print(f"  ✗ LoopScan module import failed: {e}")
        traceback.print_exc()
        return False

def test_synthetic_generation():
    """Test synthetic CMB generation"""
    print("\nTesting synthetic CMB generation...")
    
    try:
        sys.path.append('src')
        from synthetic_data import SyntheticCMBGenerator
        import numpy as np
        
        # Create generator
        generator = SyntheticCMBGenerator(nside=32)
        print("  ✓ Created SyntheticCMBGenerator")
        
        # Generate random CMB
        cmb_map = generator.generate_random_cmb(seed=42)
        print(f"  ✓ Generated random CMB map with {len(cmb_map)} pixels")
        
        # Add echo pattern
        center1 = (np.pi/4, 0)  # 45° colatitude, 0° longitude
        center2 = (3*np.pi/4, np.pi)  # 135° colatitude, 180° longitude
        
        echo_map = generator.add_echo_pattern(
            cmb_map, center1, center2, 
            pattern_strength=50.0, 
            pattern_size=np.radians(10)
        )
        print("  ✓ Added echo pattern to CMB map")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Synthetic generation test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🌀 LoopScan healpy Installation Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("HEALPix Basic", test_healpy_basic),
        ("HEALPix Visualization", test_healpy_visualization),
        ("FITS I/O", test_fits_io),
        ("LoopScan Modules", test_loopscan_modules),
        ("Synthetic Generation", test_synthetic_generation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        if test_name == "Package Imports":
            failed_imports = test_func()
            results[test_name] = len(failed_imports) == 0
            if failed_imports:
                print(f"\nFailed imports: {', '.join(failed_imports)}")
                print("Install missing packages with:")
                print("  conda install -c conda-forge " + " ".join(failed_imports))
                print("  or")
                print("  pip install " + " ".join(failed_imports))
        else:
            results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:25} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! LoopScan is ready to use.")
        print("\nNext steps:")
        print("1. Download CMB data (see data/README.md)")
        print("2. Run: python loopscan.py synthetic --plot")
        print("3. Run: python loopscan.py real --data-file your_cmb.fits --plot")
    else:
        print("❌ SOME TESTS FAILED. Please fix issues before using LoopScan.")
        print("\nSee SETUP.md for detailed installation instructions.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)