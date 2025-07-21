# Contributing to LoopScan

Thank you for your interest in contributing to the LoopScan project! This software has enabled the first detection of cosmic echo patterns in CMB data, and we welcome contributions to advance this groundbreaking research.

## How to Contribute

### 🔬 Scientific Contributions
- **Independent validation** with other CMB datasets (WMAP, ACT, SPT)
- **Algorithm improvements** for enhanced echo detection sensitivity
- **Statistical methods** for better significance testing
- **Theoretical modeling** of echo formation mechanisms

### 💻 Technical Contributions
- **Code optimization** for faster analysis
- **Visualization improvements** for clearer result presentation
- **Documentation enhancements** for better usability
- **Testing framework** development

### 📊 Data Contributions
- **Cross-validation** with polarization data
- **Multi-frequency analysis** using different Planck channels
- **Systematic error studies** with simulation data
- **Parameter space exploration** for optimal detection

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/Betti-Labs/loopscan.git
   cd loopscan
   ```

2. **Set up development environment**
   ```bash
   conda create -n loopscan-dev python=3.9
   conda activate loopscan-dev
   conda install -c conda-forge healpy numpy scipy matplotlib astropy scikit-image pandas jupyter seaborn tqdm pytest
   ```

3. **Run tests to ensure everything works**
   ```bash
   python test_healpy.py
   python -m pytest tests/  # When test suite is available
   ```

## Contribution Guidelines

### Code Standards
- **Python 3.8+** compatibility required
- **PEP 8** style guidelines
- **Type hints** for function signatures
- **Docstrings** for all public functions
- **Unit tests** for new functionality

### Scientific Standards
- **Reproducible results** with fixed random seeds
- **Statistical significance** testing for all claims
- **Systematic error** analysis for new methods
- **Peer review** quality documentation

### Example Code Structure
```python
def detect_echoes(cmb_map: np.ndarray, 
                 patch_size: int = 2000,
                 min_correlation: float = 0.1) -> List[EchoMatch]:
    """
    Detect cosmic echo patterns in CMB data.
    
    Parameters
    ----------
    cmb_map : np.ndarray
        HEALPix CMB temperature map
    patch_size : int, optional
        Size of correlation patches in pixels
    min_correlation : float, optional
        Minimum correlation threshold
        
    Returns
    -------
    List[EchoMatch]
        List of detected echo patterns
        
    Notes
    -----
    This function implements the core LoopScan algorithm
    for detecting cosmic topology signatures.
    """
    # Implementation here
    pass
```

## Research Areas

### High Priority
1. **Independent Validation**
   - Reproduce results with WMAP 9-year data
   - Cross-check with Planck polarization maps
   - Validate with ACT/SPT high-resolution data

2. **Statistical Robustness**
   - Bayesian parameter estimation
   - Bootstrap confidence intervals
   - Multiple comparison corrections

3. **Systematic Error Analysis**
   - Instrumental systematic studies
   - Foreground contamination effects
   - Analysis pipeline validation

### Medium Priority
1. **Algorithm Optimization**
   - Parallel processing implementation
   - Memory usage optimization
   - GPU acceleration for large datasets

2. **Extended Analysis**
   - Multi-scale correlation analysis
   - Non-Gaussian signature detection
   - Cross-correlation with galaxy surveys

### Future Directions
1. **Next-Generation Data**
   - CMB-S4 survey preparation
   - LiteBIRD mission analysis
   - Simons Observatory integration

2. **Theoretical Development**
   - Quantum gravity implications
   - Inflation model constraints
   - Dark energy topology effects

## Submission Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Make changes with tests**
   - Add new functionality
   - Include comprehensive tests
   - Update documentation

3. **Submit pull request**
   - Clear description of changes
   - Reference relevant issues
   - Include test results

4. **Code review process**
   - Scientific validity check
   - Code quality review
   - Performance testing

## Recognition

Contributors will be acknowledged in:
- **Repository contributors list**
- **Scientific publications** (for significant contributions)
- **Conference presentations**
- **Project documentation**

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, or identity. Please:

- **Be respectful** in all interactions
- **Focus on scientific merit** in discussions
- **Provide constructive feedback**
- **Help newcomers** learn and contribute

## Questions?

- **Scientific questions:** Open an issue with the "science" label
- **Technical questions:** Open an issue with the "technical" label
- **General discussion:** Use GitHub Discussions
- **Direct contact:** gregory@betti-labs.com

## License

By contributing to LoopScan, you agree that your contributions will be licensed under the MIT License.

---

**Together, we're advancing our understanding of cosmic topology and the fundamental nature of the universe!** 🌌