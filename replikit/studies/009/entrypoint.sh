#!/bin/bash

languages=("Java" "C++" "C" "Go")

for tgt in "${languages[@]}"; do
    echo "Translating from Python to $tgt"
    bash scripts/translate.sh GPT-4 codenet Python "$tgt" 50 0.95 0.7 0 && \
    bash scripts/test_codenet.sh Python "$tgt" GPT-4 fix_reports 1
    cp -r fix_reports /tmp/
done