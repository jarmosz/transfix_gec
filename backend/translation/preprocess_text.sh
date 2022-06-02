#!/bin/sh

# path to moses decoder: https://github.com/moses-smt/mosesdecoder                                                                                                                                         
mosesdecoder=/home/zary/Desktop/grammatical-error-correction-system/backend/translation/tools/moses-scripts

# path to subword segmentation scripts: https://github.com/rsennrich/subword-nmt                                                                                                                           
subword_nmt=/home/zary/Desktop/grammatical-error-correction-system/backend/translation/tools/subword-nmt

cat $1 \
    | $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l pl \
    | $mosesdecoder/scripts/tokenizer/tokenizer.perl -a -l pl \
    | $mosesdecoder/scripts/recaser/truecase.perl -model /home/zary/Desktop/grammatical-error-correction-system/backend/translation/model/tc.er \
    | $subword_nmt/apply_bpe.py -c /home/zary/Desktop/grammatical-error-correction-system/backend/translation/model/erco.bpe 2> /dev/null