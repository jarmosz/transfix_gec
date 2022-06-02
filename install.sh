#!/bin/bash -v

mkdir -p tools

# download moses
if [ ! -e backend/translation/tools/moses-scripts ]; then
    cd backend/translation/tools
    git clone https://github.com/marian-nmt/moses-scripts
    cd ..
fi

# download subword-nmt
if [ ! -e backend/translation/tools/subword-nmt ]; then
    cd backend/translation/tool
    git clone https://github.com/rsennrich/subword-nmt
    cd ..
fi

# download and compile marian-nmt with webserver
if [ ! -e tools/marian ]; then
    cd tools
    git clone https://github.com/marian-nmt/marian
    mkdir marian/build
    cd marian/build
    cmake -DCOMPILE_SERVER=on ..
    make -j4
    cd ..
fi
