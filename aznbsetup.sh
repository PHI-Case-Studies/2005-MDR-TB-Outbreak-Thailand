#!/bin/bash

# Activate environment
source /home/nbuser/anaconda3_420/bin/activate

# Install packages
conda update -c conda-forge conda conda-build
conda install -y -c conda-forge folium=0.9.1 jinja2=2.10* xlrd networkx=2.3* missingno=0.4* bokeh

pip install --upgrade pip
pip install pandas==0.24.2 plotly==4.0.0

source /home/nbuser/anaconda3_420/bin/deactivate
