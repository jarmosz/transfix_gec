#!/bin/sh

# path to moses decoder: https://github.com/moses-smt/mosesdecoder                                                                                                                                         
mosesdecoder=/home/zary/Desktop/grammatical-error-correction-system/backend/translation/tools/moses-scripts

# path to subword segmentation scripts: https://github.com/rsennrich/subword-nmt                                                                                                                           
subword_nmt=/home/zary/Desktop/grammatical-error-correction-system/backend/translation/tools/subword-nmt

cat $1 \
    | sed 's/\@\@ //g' \
    | /home/zary/Desktop/grammatical-error-correction-system/backend/translation/tools/moses-scripts/scripts/recaser/detruecase.perl 2>/dev/null \
    | /home/zary/Desktop/grammatical-error-correction-system/backend/translation/tools/moses-scripts/scripts/tokenizer/detokenizer.perl -l pl 2>/dev/null