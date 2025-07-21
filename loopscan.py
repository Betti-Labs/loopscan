#!/usr/bin/env python3
"""
LoopScan: Pattern Echo Detection in the CMB
Main CLI interface for the Flat Loop Universe analysis tool
"""

import argparse
import logging
import sys
from pathlib import Path
import json
import numpy as np

# Add src to path
sys.path.append('src')

from data_loader import CMBDataLoader
from echo_detector import EchoDetector
from visualizer import CMBVisualizer
from synthetic_data import SyntheticCMBGenerator

def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_synthetic_test(args):
    """Run synthetic data test"""
    print("🌀 LoopScan: Synthetic Echo Detection Test")
    print("=" * 50)
    
    # Generate synthetic data
    generator = SyntheticCMBGenerator(nside=args.nside)
    synthetic_map, echo_locations = generator.create_toroidal_test_map(
        n_echo_pairs=args.n_echoes,
        pattern_strength=args.strength,
        seed=42
    )
    
    print(f"Generated synthetic CMB with {len(echo_locations)} echo pairs")
    
    # Run detection
    detector = EchoDetector(nside=args.nside)
    
    # Antipodal search
    antipodal_matches = detector.detect_antipodal_echoes(
        synthetic_map,
        patch_radius=np.radians(args.patch_size),
        min_correlation=args.min_corr,
        n_samples=args.n_samples
    )
    
    # Toroidal search
    shift_angles = [np.radians(angle) for angle in args.shift_angles]
    toroidal_matches = detector.detect_toroidal_echoes(
        synthetic_map,
        shift_angles=shift_angles,
        patch_radius=np.radians(args.patch_size),
        min_correlation=args.min_corr,
        n_samples=args.n_samples // 2
    )
    
    all_matches = antipodal_matches + toroidal_matches
    
    print(f"\nDetection Results:")
    print(f"  Antipodal matches: {len(antipodal_matches)}")
    print(f"  Toroidal matches: {len(toroidal_matches)}")
    print(f"  Total matches: {len(all_matches)}")
    
    if all_matches:
        # Sort by correlation
        all_matches.sort(key=lambda x: abs(x.correlation_score), reverse=True)
        
        print(f"\nTop 5 Detections:")
        for i, match in enumerate(all_matches[:5]):
            print(f"  {i+1}. Correlation: {match.correlation_score:.3f}, "
                  f"Separation: {np.degrees(match.angular_separation):.1f}°")
    
    # Visualization
    if args.plot:
        viz = CMBVisualizer()
        viz.plot_mollweide(synthetic_map, "Synthetic CMB with Echoes", 
                          save_path="synthetic_cmb.png")
        
        if all_matches:
            viz.plot_echo_matches(synthetic_map, all_matches,
                                 save_path="synthetic_detections.png")
            viz.plot_correlation_histogram(all_matches,
                                         save_path="synthetic_correlations.png")
    
    # Save results
    if args.output:
        results = {
            'n_echo_pairs_planted': len(echo_locations),
            'n_matches_found': len(all_matches),
            'detection_parameters': {
                'nside': args.nside,
                'patch_size_deg': args.patch_size,
                'min_correlation': args.min_corr,
                'n_samples': args.n_samples
            },
            'matches': []
        }
        
        for match in all_matches:
            results['matches'].append({
                'region1_center_deg': [np.degrees(match.region1_center[0]), 
                                     np.degrees(match.region1_center[1])],
                'region2_center_deg': [np.degrees(match.region2_center[0]), 
                                     np.degrees(match.region2_center[1])],
                'angular_separation_deg': np.degrees(match.angular_separation),
                'correlation_score': match.correlation_score,
                'method': match.method
            })
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {args.output}")

def run_real_data_analysis(args):
    """Run analysis on real CMB data"""
    print("🌀 LoopScan: Real CMB Data Analysis")
    print("=" * 50)
    
    # Load CMB data
    loader = CMBDataLoader()
    
    try:
        cmb_map = loader.load_planck_map(args.data_file)
        print(f"Loaded CMB map: {loader.get_map_statistics(cmb_map)}")
        
        # Downsample if requested
        import healpy as hp
        if args.nside < hp.npix2nside(len(cmb_map)):
            cmb_map = loader.downsample_map(cmb_map, args.nside)
        
        # Clean map
        cmb_map = loader.remove_monopole_dipole(cmb_map)
        
        # Run detection
        detector = EchoDetector(nside=args.nside)
        
        print("Searching for echo patterns...")
        
        # Antipodal search
        antipodal_matches = detector.detect_antipodal_echoes(
            cmb_map,
            patch_radius=np.radians(args.patch_size),
            min_correlation=args.min_corr,
            n_samples=args.n_samples
        )
        
        # Toroidal search
        shift_angles = [np.radians(90), np.radians(180), np.radians(120)]
        toroidal_matches = detector.detect_toroidal_echoes(
            cmb_map,
            shift_angles=shift_angles,
            patch_radius=np.radians(args.patch_size),
            min_correlation=args.min_corr,
            n_samples=args.n_samples // 2
        )
        
        all_matches = antipodal_matches + toroidal_matches
        
        print(f"\nDetection Results:")
        print(f"  Antipodal matches: {len(antipodal_matches)}")
        print(f"  Toroidal matches: {len(toroidal_matches)}")
        print(f"  Total matches: {len(all_matches)}")
        
        if all_matches:
            all_matches.sort(key=lambda x: abs(x.correlation_score), reverse=True)
            print(f"\nTop 5 Detections:")
            for i, match in enumerate(all_matches[:5]):
                print(f"  {i+1}. Correlation: {match.correlation_score:.3f}, "
                      f"Separation: {np.degrees(match.angular_separation):.1f}°")
        
        # Visualization
        if args.plot:
            viz = CMBVisualizer()
            viz.plot_mollweide(cmb_map, f"CMB Map - {args.data_file}", 
                              save_path="real_cmb.png")
            
            if all_matches:
                viz.plot_echo_matches(cmb_map, all_matches,
                                     save_path="real_detections.png")
                viz.plot_correlation_histogram(all_matches,
                                             save_path="real_correlations.png")
        
        # Save results
        if args.output:
            results = {
                'data_file': args.data_file,
                'n_matches_found': len(all_matches),
                'detection_parameters': {
                    'nside': args.nside,
                    'patch_size_deg': args.patch_size,
                    'min_correlation': args.min_corr,
                    'n_samples': args.n_samples
                },
                'matches': []
            }
            
            for match in all_matches:
                results['matches'].append({
                    'region1_center_deg': [np.degrees(match.region1_center[0]), 
                                         np.degrees(match.region1_center[1])],
                    'region2_center_deg': [np.degrees(match.region2_center[0]), 
                                         np.degrees(match.region2_center[1])],
                    'angular_separation_deg': np.degrees(match.angular_separation),
                    'correlation_score': match.correlation_score,
                    'method': match.method
                })
            
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\nResults saved to {args.output}")
        
        print("Real data analysis complete!")
        
    except FileNotFoundError:
        print(f"Error: CMB data file '{args.data_file}' not found in data/ directory")
        print("Please download CMB data files first. See data/README.md for instructions.")

def main():
    parser = argparse.ArgumentParser(
        description="LoopScan: Search for echo patterns in CMB data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run synthetic test with default parameters
  python loopscan.py synthetic --plot
  
  # Run with custom parameters
  python loopscan.py synthetic --nside 512 --n-echoes 5 --strength 200 --plot
  
  # Analyze real Planck data
  python loopscan.py real --data-file planck_cmb_commander.fits --nside 256
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='mode', help='Analysis mode')
    
    # Synthetic data mode
    synthetic_parser = subparsers.add_parser('synthetic', 
                                           help='Test with synthetic data')
    synthetic_parser.add_argument('--nside', type=int, default=256,
                                help='HEALPix resolution parameter')
    synthetic_parser.add_argument('--n-echoes', type=int, default=3,
                                help='Number of echo pairs to plant')
    synthetic_parser.add_argument('--strength', type=float, default=100.0,
                                help='Echo pattern strength (μK)')
    synthetic_parser.add_argument('--patch-size', type=float, default=10.0,
                                help='Patch radius in degrees')
    synthetic_parser.add_argument('--min-corr', type=float, default=0.2,
                                help='Minimum correlation threshold')
    synthetic_parser.add_argument('--n-samples', type=int, default=2000,
                                help='Number of sample points')
    synthetic_parser.add_argument('--shift-angles', nargs='+', type=float,
                                default=[90.0, 180.0, 120.0],
                                help='Angular shifts to test (degrees)')
    synthetic_parser.add_argument('--plot', action='store_true',
                                help='Generate visualization plots')
    synthetic_parser.add_argument('--output', type=str,
                                help='Save results to JSON file')
    
    # Real data mode
    real_parser = subparsers.add_parser('real', help='Analyze real CMB data')
    real_parser.add_argument('--data-file', type=str, required=True,
                           help='CMB .fits file in data/ directory')
    real_parser.add_argument('--nside', type=int, default=512,
                           help='Target resolution (will downsample if needed)')
    real_parser.add_argument('--patch-size', type=float, default=10.0,
                           help='Patch radius in degrees')
    real_parser.add_argument('--min-corr', type=float, default=0.3,
                           help='Minimum correlation threshold')
    real_parser.add_argument('--n-samples', type=int, default=5000,
                           help='Number of sample points')
    real_parser.add_argument('--plot', action='store_true',
                           help='Generate visualization plots')
    real_parser.add_argument('--output', type=str,
                           help='Save results to JSON file')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        return
    
    setup_logging(args.verbose)
    
    if args.mode == 'synthetic':
        run_synthetic_test(args)
    elif args.mode == 'real':
        run_real_data_analysis(args)

if __name__ == '__main__':
    main()