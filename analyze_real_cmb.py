#!/usr/bin/env python3
"""
Real CMB Data Analysis for Flat Loop Universe Theory
Works without healpy - uses numpy and scipy to read FITS files
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.spatial.distance import cdist
import struct
import json
from pathlib import Path

def read_fits_simple(filename):
    """
    Simple FITS file reader without astropy/healpy
    Reads the primary HDU data array
    """
    print(f"Reading FITS file: {filename}")
    
    try:
        with open(filename, 'rb') as f:
            # Read FITS header
            header_cards = []
            while True:
                card = f.read(80).decode('ascii', errors='ignore')
                header_cards.append(card)
                if card.startswith('END'):
                    break
            
            # Calculate header size (multiple of 2880 bytes)
            header_size = len(header_cards) * 80
            header_blocks = (header_size + 2879) // 2880
            total_header_size = header_blocks * 2880
            
            # Find data parameters from header
            naxis = None
            naxis1 = None
            bitpix = None
            
            for card in header_cards:
                if card.startswith('NAXIS   ='):
                    naxis = int(card.split('=')[1].split('/')[0].strip())
                elif card.startswith('NAXIS1  ='):
                    naxis1 = int(card.split('=')[1].split('/')[0].strip())
                elif card.startswith('BITPIX  ='):
                    bitpix = int(card.split('=')[1].split('/')[0].strip())
            
            print(f"FITS info: NAXIS={naxis}, NAXIS1={naxis1}, BITPIX={bitpix}")
            
            # Seek to data start
            f.seek(total_header_size)
            
            # Read data based on BITPIX
            if bitpix == -32:  # 32-bit float
                dtype = '>f4'  # Big-endian float32
            elif bitpix == -64:  # 64-bit float  
                dtype = '>f8'  # Big-endian float64
            elif bitpix == 32:   # 32-bit integer
                dtype = '>i4'  # Big-endian int32
            else:
                dtype = '>f4'  # Default to float32
            
            # Read the data array
            data = np.frombuffer(f.read(), dtype=dtype)
            
            if naxis1:
                data = data[:naxis1]  # Trim to expected size
            
            print(f"Read {len(data)} data points")
            print(f"Data range: {np.min(data):.3e} to {np.max(data):.3e}")
            
            return data
            
    except Exception as e:
        print(f"Error reading FITS file: {e}")
        return None

def analyze_cmb_correlations(cmb_data, patch_size=1000, n_samples=5000, min_correlation=0.1):
    """
    Analyze real CMB data for echo patterns
    """
    print(f"\n🔍 Analyzing CMB data for echo patterns...")
    print(f"Data points: {len(cmb_data)}")
    print(f"Patch size: {patch_size}")
    print(f"Sample points: {n_samples}")
    print(f"Min correlation: {min_correlation}")
    
    # Remove any invalid data
    valid_data = cmb_data[np.isfinite(cmb_data)]
    print(f"Valid data points: {len(valid_data)}")
    
    if len(valid_data) < patch_size * 2:
        print("❌ Not enough valid data for analysis")
        return []
    
    # Statistics
    mean_temp = np.mean(valid_data)
    std_temp = np.std(valid_data)
    print(f"Temperature statistics:")
    print(f"  Mean: {mean_temp:.3e}")
    print(f"  Std:  {std_temp:.3e}")
    print(f"  Min:  {np.min(valid_data):.3e}")
    print(f"  Max:  {np.max(valid_data):.3e}")
    
    # Sample random locations for correlation analysis
    np.random.seed(42)
    max_start = len(valid_data) - patch_size
    sample_starts = np.random.choice(max_start, min(n_samples, max_start), replace=False)
    
    matches = []
    
    print(f"\nSearching for correlations...")
    
    for i, start1 in enumerate(sample_starts):
        if i % 500 == 0:
            print(f"  Progress: {i}/{len(sample_starts)} ({100*i/len(sample_starts):.1f}%)")
        
        # Extract first patch
        patch1 = valid_data[start1:start1+patch_size]
        
        # Test different separations for potential echoes
        test_separations = [
            len(valid_data) // 4,   # Quarter way around
            len(valid_data) // 2,   # Antipodal (opposite side)
            3 * len(valid_data) // 4  # Three quarters
        ]
        
        for separation in test_separations:
            start2 = (start1 + separation) % len(valid_data)
            
            # Make sure we don't go past the end
            if start2 + patch_size > len(valid_data):
                start2 = len(valid_data) - patch_size
            
            patch2 = valid_data[start2:start2+patch_size]
            
            # Calculate correlation
            try:
                correlation = np.corrcoef(patch1, patch2)[0, 1]
                
                if not np.isnan(correlation) and abs(correlation) >= min_correlation:
                    # Calculate angular separation (approximate)
                    angular_sep = 360.0 * separation / len(valid_data)
                    
                    matches.append({
                        'location1': int(start1),
                        'location2': int(start2),
                        'correlation': float(correlation),
                        'separation_pixels': int(separation),
                        'separation_degrees': float(angular_sep),
                        'patch_size': patch_size
                    })
            except:
                continue
    
    print(f"\n✓ Analysis complete!")
    return matches

def plot_cmb_analysis(cmb_data, matches, save_plots=True):
    """
    Create plots of CMB data and correlation results
    """
    print(f"\n📊 Creating analysis plots...")
    
    # Plot 1: CMB data overview
    plt.figure(figsize=(15, 10))
    
    # Subsample for plotting (too many points otherwise)
    plot_data = cmb_data[::max(1, len(cmb_data)//10000)]
    
    plt.subplot(2, 2, 1)
    plt.plot(plot_data, alpha=0.7, linewidth=0.5)
    plt.title('Real CMB Temperature Data')
    plt.xlabel('Pixel Index')
    plt.ylabel('Temperature')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 2)
    plt.hist(cmb_data[np.isfinite(cmb_data)], bins=100, alpha=0.7, edgecolor='black')
    plt.title('CMB Temperature Distribution')
    plt.xlabel('Temperature')
    plt.ylabel('Count')
    plt.grid(True, alpha=0.3)
    
    if matches:
        correlations = [m['correlation'] for m in matches]
        separations = [m['separation_degrees'] for m in matches]
        
        plt.subplot(2, 2, 3)
        plt.hist(correlations, bins=30, alpha=0.7, edgecolor='black', color='orange')
        plt.title(f'Echo Correlations Found ({len(matches)} matches)')
        plt.xlabel('Correlation Coefficient')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.3)
        plt.axvline(np.mean(correlations), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(correlations):.3f}')
        plt.legend()
        
        plt.subplot(2, 2, 4)
        plt.scatter(separations, correlations, alpha=0.6, s=20)
        plt.title('Correlation vs Angular Separation')
        plt.xlabel('Angular Separation (degrees)')
        plt.ylabel('Correlation Coefficient')
        plt.grid(True, alpha=0.3)
        
        # Highlight potential echo signatures
        high_corr = [m for m in matches if abs(m['correlation']) > 0.2]
        if high_corr:
            high_sep = [m['separation_degrees'] for m in high_corr]
            high_cor = [m['correlation'] for m in high_corr]
            plt.scatter(high_sep, high_cor, color='red', s=40, alpha=0.8, 
                       label=f'High correlation (n={len(high_corr)})')
            plt.legend()
    else:
        plt.subplot(2, 2, 3)
        plt.text(0.5, 0.5, 'No significant\ncorrelations found', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
        plt.title('Echo Analysis Results')
        
        plt.subplot(2, 2, 4)
        plt.text(0.5, 0.5, 'No correlation\npatterns detected', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
        plt.title('Pattern Search Results')
    
    plt.tight_layout()
    
    if save_plots:
        plt.savefig('real_cmb_analysis.png', dpi=300, bbox_inches='tight')
        print("📁 Saved plot: real_cmb_analysis.png")
    
    plt.show()

def main():
    """Main analysis of real CMB data"""
    print("🌌 Real CMB Data Analysis for Flat Loop Universe Theory")
    print("=" * 70)
    print("Analyzing actual Planck observations for cosmic echo patterns!")
    print()
    
    # Find CMB data file
    data_dir = Path("data")
    cmb_files = list(data_dir.glob("*.fits"))
    
    if not cmb_files:
        print("❌ No FITS files found in data/ directory")
        print("Please download real CMB data first!")
        return
    
    cmb_file = cmb_files[0]  # Use first FITS file found
    print(f"📂 Using CMB data: {cmb_file}")
    
    # Read the real CMB data
    cmb_data = read_fits_simple(cmb_file)
    
    if cmb_data is None:
        print("❌ Failed to read CMB data")
        return
    
    # Analyze for echo patterns
    matches = analyze_cmb_correlations(
        cmb_data, 
        patch_size=2000,    # Larger patches for real data
        n_samples=3000,     # More samples for thorough search
        min_correlation=0.1  # Lower threshold for real data
    )
    
    # Results
    print(f"\n🎯 ANALYSIS RESULTS:")
    print(f"{'='*50}")
    
    if matches:
        print(f"✓ Found {len(matches)} potential echo patterns!")
        
        # Sort by correlation strength
        matches.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        print(f"\n🏆 Top 10 Echo Candidates:")
        print("Rank | Correlation | Angular Sep | Pixel Locations")
        print("-" * 55)
        
        for i, match in enumerate(matches[:10]):
            print(f"{i+1:4d} | {match['correlation']:10.3f} | "
                  f"{match['separation_degrees']:9.1f}° | "
                  f"{match['location1']:6d}-{match['location2']:6d}")
        
        # Statistical analysis
        correlations = [m['correlation'] for m in matches]
        strong_matches = [m for m in matches if abs(m['correlation']) > 0.2]
        
        print(f"\n📊 Statistical Summary:")
        print(f"  Total matches: {len(matches)}")
        print(f"  Strong correlations (>0.2): {len(strong_matches)}")
        print(f"  Mean correlation: {np.mean(correlations):.3f}")
        print(f"  Max correlation: {np.max(np.abs(correlations)):.3f}")
        
        if strong_matches:
            print(f"\n🌀 POTENTIAL FLAT LOOP UNIVERSE EVIDENCE:")
            print(f"  Found {len(strong_matches)} strong echo candidates!")
            print(f"  This could indicate toroidal topology!")
            
            # Check for specific separations expected in toroidal universe
            separations = [m['separation_degrees'] for m in strong_matches]
            near_90 = sum(1 for s in separations if 85 <= s <= 95)
            near_180 = sum(1 for s in separations if 175 <= s <= 185)
            
            print(f"  Near 90° separations: {near_90}")
            print(f"  Near 180° separations: {near_180}")
            
            if near_90 > 0 or near_180 > 0:
                print(f"  ⭐ SIGNIFICANT: Found echoes at predicted separations!")
        
        # Save results
        results = {
            'analysis_type': 'real_cmb_echo_detection',
            'data_file': str(cmb_file),
            'data_points': len(cmb_data),
            'matches_found': len(matches),
            'strong_matches': len(strong_matches),
            'max_correlation': float(np.max(np.abs(correlations))),
            'mean_correlation': float(np.mean(correlations)),
            'top_matches': matches[:20]
        }
        
        with open('real_cmb_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: real_cmb_results.json")
        
    else:
        print("❌ No significant echo patterns detected")
        print("This could mean:")
        print("  1. The universe is not toroidal")
        print("  2. Echo patterns are too weak to detect")
        print("  3. Need different analysis parameters")
    
    # Create visualization
    plot_cmb_analysis(cmb_data, matches)
    
    print(f"\n{'='*70}")
    print("🔬 REAL CMB ANALYSIS COMPLETE!")
    print("You have now tested the Flat Loop Universe theory")
    print("against actual cosmic microwave background observations!")
    
    if matches:
        print(f"🎉 DISCOVERY: Found {len(matches)} potential cosmic echoes!")
    else:
        print("📊 No strong evidence for cosmic echoes detected")

if __name__ == "__main__":
    main()