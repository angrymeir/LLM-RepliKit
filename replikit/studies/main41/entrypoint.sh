#!/bin/bash

SCRIPT_DIR=/home/runner/scripts
DATA_ROOT=/home/runner
: "${EVIDENCE_DIR:="/tmp/evidence"}"  # Use default if not provided as ENV
mkdir -p $EVIDENCE_DIR
echo "saving evidence to $EVIDENCE_DIR"
cd $EVIDENCE_DIR

# Run experiments
echo "Starting experiments..."
date
## Java
### baseline
python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Java_data --model turbo --mode BM25 --use_repo no --use_id no --use_dfg no --pause_duration 0  --language Java >Java_BM25.log &
sleep 5
### ASAP
python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Java_data --model turbo --mode BM25 --use_repo yes --use_id id3 --use_dfg yes --pause_duration 0  --language Java >Java_ASAP.log &
### other
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Java_data --model turbo --mode BM25 --use_repo yes --use_id no --use_dfg no --pause_duration 0  --language Java &
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Java_data --model turbo --mode BM25 --use_repo no --use_id id3 --use_dfg no --pause_duration 0  --language Java &
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Java_data --model turbo --mode BM25 --use_repo no --use_id no --use_dfg yes --pause_duration 0  --language Java &

## Python
### baseline
python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Python_data --model turbo --mode BM25 --use_repo no --use_id no --use_dfg no --pause_duration 0  --language Python >Python_BM25.log &
sleep 5
# ASAP
python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Python_data --model turbo --mode BM25 --use_repo yes --use_id id3 --use_dfg yes --pause_duration 0  --language Python >Python_ASAP.log &
# other
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Python_data --model turbo --mode BM25 --use_repo yes --use_id no --use_dfg no --pause_duration 0  --language Python &
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Python_data --model turbo --mode BM25 --use_repo no --use_id id3 --use_dfg no --pause_duration 0  --language Python &
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/Python_data --model turbo --mode BM25 --use_repo no --use_id no --use_dfg yes --pause_duration 0  --language Python &

## PHP
### baseline
python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/PHP_data --model turbo --mode BM25 --use_repo no --use_id no --use_dfg no --pause_duration 0  --language PHP >PHP_BM25.log &
sleep 5
# ASAP
python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/PHP_data --model turbo --mode BM25 --use_repo yes --use_id id3 --use_dfg yes --pause_duration 0  --language PHP > PHP_ASAP.log &
# other
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/PHP_data --model turbo --mode BM25 --use_repo yes --use_id no --use_dfg no --pause_duration 0  --language PHP &
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/PHP_data --model turbo --mode BM25 --use_repo no --use_id id3 --use_dfg no --pause_duration 0  --language PHP &
# python $SCRIPT_DIR/turbo.py --open_key $OPENAI_API_KEY --data_folder $DATA_ROOT/PHP_data --model turbo --mode BM25 --use_repo no --use_id no --use_dfg yes --pause_duration 0  --language PHP &


## wait for all to finish
echo "... running ..."
wait
echo "... finished!"
date


# calculate bleu scores - turbo_BM25.txt  turbo_BM25_dfg.txt  turbo_BM25_id3.txt  turbo_BM25_repo.txt turbo_BM25_repo_dfg_id3.txt
echo "calculate bleu scores"
## Java
cd Java_result/
python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25.txt --ref_file=$DATA_ROOT/Java_result/final_1.gold > turbo_BM25.score
python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_repo_dfg_id3.txt --ref_file=$DATA_ROOT/Java_result/final_1.gold > turbo_BM25_repo_dfg_id3.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_repo.txt --ref_file=$DATA_ROOT/Java_result/final_1.gold > turbo_BM25_repo.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_id3.txt --ref_file=$DATA_ROOT/Java_result/final_1.gold > turbo_BM25_id3.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_dfg.txt --ref_file=$DATA_ROOT/Java_result/final_1.gold > turbo_BM25_dfg.score

## Python
cd ../Python_result
python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25.txt --ref_file=$DATA_ROOT/Python_result/final_1.gold > turbo_BM25.score
python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_repo_dfg_id3.txt --ref_file=$DATA_ROOT/Python_result/final_1.gold > turbo_BM25_repo_dfg_id3.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_repo.txt --ref_file=$DATA_ROOT/Python_result/final_1.gold > turbo_BM25_repo.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_id3.txt --ref_file=$DATA_ROOT/Python_result/final_1.gold > turbo_BM25_id3.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_dfg.txt --ref_file=$DATA_ROOT/Python_result/final_1.gold > turbo_BM25_dfg.score

## Python
cd ../PHP_result
python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25.txt --ref_file=$DATA_ROOT/PHP_result/final_1.gold > turbo_BM25.score
python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_repo_dfg_id3.txt --ref_file=$DATA_ROOT/PHP_result/final_1.gold > turbo_BM25_repo_dfg_id3.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_repo.txt --ref_file=$DATA_ROOT/PHP_result/final_1.gold > turbo_BM25_repo.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_id3.txt --ref_file=$DATA_ROOT/PHP_result/final_1.gold > turbo_BM25_id3.score
# python $SCRIPT_DIR/BLEU.py --model_output=turbo_BM25_dfg.txt --ref_file=$DATA_ROOT/PHP_result/final_1.gold > turbo_BM25_dfg.score



cd ..

echo "done!"
date

echo
echo "|      |     BM25     |     ASAP     |" | tee result.md
echo "|------|--------------|--------------|" | tee -a result.md
echo "| Java | $(cat Java_result/turbo_BM25.score) | $(cat Java_result/turbo_BM25_repo_dfg_id3.score) |" | tee -a result.md
echo "|Python| $(cat Python_result/turbo_BM25.score) | $(cat Python_result/turbo_BM25_repo_dfg_id3.score) |" | tee -a result.md
echo "| PHP  | $(cat PHP_result/turbo_BM25.score) | $(cat PHP_result/turbo_BM25_repo_dfg_id3.score) |" | tee -a result.md
