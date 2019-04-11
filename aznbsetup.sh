#!/bin/bash
source /home/nbuser/anaconda3_420/bin/activate
conda config --add channels conda-forge
conda install -y xlrd folium=0.8* networkx=2.1*
