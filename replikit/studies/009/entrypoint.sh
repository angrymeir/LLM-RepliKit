#!/bin/bash

languages=("Java" "Python" "C++" "C" "Go")

for src in "${languages[@]}"; do
    for tgt in "${languages[@]}"; do
        if [ "$src" != "$tgt" ]; then
            echo "Translating from $src to $tgt"
            bash scripts/translate.sh GPT-4 codenet "$src" "$tgt" 50 0.95 0.7 0 && \
            bash scripts/test_codenet.sh "$src" "$tgt" GPT-4 fix_reports 1
            cp -r fix_reports /tmp/
        fi
    done
done