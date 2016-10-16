#!/bin/sh

if [ ! -d "$HOME/data/MedleyDB_sample" ]; then
    mkdir -p $HOME/data
    wget http://marl.smusic.nyu.edu/medleydb_webfiles/MedleyDB_sample.tar.gz -O $HOME/data/MedleyDB_sample.tar.gz
    gzip -d $HOME/data/MedleyDB_sample.tar.gz
    tar xvf $HOME/data/MedleyDB_sample.tar -C $HOME/data/
fi