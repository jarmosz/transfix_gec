#!/bin/bash -v                                                                                                                                                                                             

# path to moses decoder: https://github.com/moses-smt/mosesdecoder                                                                                                                                         
mosesdecoder=./tools/moses-scripts

# path to subword segmentation scripts: https://github.com/rsennrich/subword-nmt                                                                                                                           
subword_nmt=./tools/subword-nmt

MARIAN_DECODER=./marian/build/marian-decoder

cat $1 \
    | $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l pl \
    | $mosesdecoder/scripts/tokenizer/tokenizer.perl -a -l pl \
    | $mosesdecoder/scripts/recaser/truecase.perl -model model/tc.er \
    | $subword_nmt/apply_bpe.py -c model/erco.bpe \
    | $MARIAN_DECODER -c model/ens/model.npz.decoder.yml -m model/ens/model.npz -d 0 -b 12 -n -w 6000 \
    | sed 's/\@\@ //g' \
    | ./tools/moses-scripts/scripts/recaser/detruecase.perl 2>/dev/null \
    | ./tools/moses-scripts/scripts/tokenizer/detokenizer.perl -l pl 2>/dev/null \
    | cat
