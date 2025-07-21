FROM continuumio/miniconda3

# Install healpy and all dependencies
RUN conda install -c conda-forge healpy numpy scipy matplotlib astropy scikit-image pandas jupyter seaborn tqdm numba -y

# Set working directory
WORKDIR /loopscan

# Copy LoopScan files
COPY . .

# Default command
CMD ["python", "loopscan.py", "synthetic", "--plot"]