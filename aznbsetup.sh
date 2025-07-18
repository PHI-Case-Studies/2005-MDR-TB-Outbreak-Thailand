#!/bin/bash

# Initialize conda
source /opt/conda/etc/profile.d/conda.sh

# Activate base environment
conda activate base

# Install required packages using mamba
mamba install -y -c conda-forge \
    plotly \
    folium=0.14.0 \
    branca=0.6.0 \
    ipywidgets \
    ipython \
    ipykernel \
    jupyterlab \
    nodejs \
    jinja2=3.1.2 \
    xlrd \
    networkx=3.2 \
    missingno=0.5.2 \
    bokeh=3.3 \
    pandas=2.2 \
    numpy

# Deactivate
conda deactivate

