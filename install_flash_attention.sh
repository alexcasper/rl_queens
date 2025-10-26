#!/usr/bin/env bash
set -e
git clone https://github.com/ROCm/flash-attention.git /tmp/flash-attention
cd /tmp/flash-attention
git checkout v2.7.4-cktile
python setup.py install
git clone https://github.com/ROCm/xformers.git /tmp/xformers
cd /tmp/xformers
git submodule update --init --recursive
python setup.py install