#!/bin/sh

if [ ! -d "$HOME/data/MedleyDB_sample" ]; then
    mkdir -p $HOME/data
    wget https://zenodo.org/record/1438309/files/MedleyDB_Sample.tar.gz?download=1 -O $HOME/data/MedleyDB_sample.tar.gz
    ls $HOME/data/*
    gzip -d $HOME/data/MedleyDB_sample.tar.gz
    tar xvf $HOME/data/MedleyDB_sample.tar -C $HOME/data/
fi
