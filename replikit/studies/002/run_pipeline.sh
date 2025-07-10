#!/bin/bash
set -e

echo "[Init] Creating config.json from OPENAI_API_KEY env variable..."
cat <<EOF > /workspace/RegexEval/Generation/config.json
{
  "OPENAI_KEY": "${OPENAI_API_KEY}"
}
EOF

# we are only interested in gpt results
for file in \
    /workspace/RegexEval/Evaluation/Compilation.py \
    /workspace/RegexEval/Evaluation/Pass_at_k_Evaluation.py \
    /workspace/RegexEval/Evaluation/DFA_Equ_Evaluation.py \
    /workspace/RegexEval/Evaluation/EM_Evaluation.py \
    /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReDoS_Dataset_Creation.py \
    /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReScure_Result_Analysis.py \
    /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReDoSHunter_Result_Analysis.py
do
    sed -i 's/names = \[.*\]/names = ["GPT3.5_Raw_Output","GPT3.5_Refined_Output"]/' "$file"
done

cd /workspace/RegexEval/Generation

echo "[Step 1] Running GPT3.5 generation..."
# Limit processing to first 2 items in gpt35.py # TODO: remove after testing when doin experiment runs
#sed -i 's/^for item in data:/for item in data[:2]:/' gpt35.py
python3 gpt35.py # gives prompt_type raw
python3 gpt35.py --prompt_type refined
cp /workspace/RegexEval/Generation/Output/GPT3.5_Raw_Output.json /workspace/output/GPT3.5_Raw_Output.json
cp /workspace/RegexEval/Generation/Output/GPT3.5_Refined_Output.json /workspace/output/GPT3.5_Refined_Output.json

echo "[Step 2] Running Compilation evaluation..."
cd /workspace/RegexEval/Evaluation
python3 Compilation.py
cp /workspace/RegexEval/Evaluation/Output/GPT3.5_Raw_Output_Compiled_Result.json /workspace/output/GPT3.5_Raw_Output_Compiled_Result.json
cp /workspace/RegexEval/Evaluation/Output/GPT3.5_Refined_Output_Compiled_Result.json /workspace/output/GPT3.5_Refined_Output_Compiled_Result.json

echo "[Step 3] Running Pass@K evaluation..."
python3 Pass_at_k_Evaluation.py > /workspace/output/pass_at_k.txt

echo "[Step 4] Running DFA-EQ@K evaluation..."
python3 DFA_Equ_Evaluation.py > /workspace/output/dfa_eq_k.txt

echo "[Step 5] Running EM evaluation..."
python3 EM_Evaluation.py > /workspace/output/em_eval.txt # output is filename and score in next line

echo "[Step 6] Creating ReDoS dataset..."
cd /workspace/RegexEval/Evaluation/ReDoSEvaluation
python3 ReDoS_Dataset_Creation.py # no useable prints

echo "[Step 7] Running ReScue..."
cd /workspace/ReScue
mkdir -p test/data
cp /workspace/RegexEval/Evaluation/ReDoSEvaluation/Input_Data/GPT3.5_Raw_Output.txt ./test/data/
cp /workspace/RegexEval/Evaluation/ReDoSEvaluation/Input_Data/GPT3.5_Refined_Output.txt ./test/data/
cd test
# Raw
python3 batchtester.py -a -reg GPT3.5_Raw_Output.txt
LOGDIR=$(ls -td ./logs/ReScue.jar/GPT3.5_Raw_Output.txt/* | head -n 1)
python3 batchtester.py -c -logDir "$LOGDIR" -reg GPT3.5_Raw_Output.txt
cp "$LOGDIR/collect_summary.txt" /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReScue_Results/GPT3.5_Raw_Output_full_result.txt
truncate -s -1 /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReScue_Results/GPT3.5_Raw_Output_full_result.txt # remove empty last newline, otherwise execution fails later in result analysis
# Refined
python3 batchtester.py -a -reg GPT3.5_Refined_Output.txt
LOGDIR=$(ls -td ./logs/ReScue.jar/GPT3.5_Refined_Output.txt/* | head -n 1)
python3 batchtester.py -c -logDir "$LOGDIR" -reg GPT3.5_Refined_Output.txt
cp "$LOGDIR/collect_summary.txt" /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReScue_Results/GPT3.5_Refined_Output_full_result.txt
truncate -s -1 /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReScue_Results/GPT3.5_Refined_Output_full_result.txt

echo "[Step 8] Analyzing ReScure results..."
cd /workspace/RegexEval/Evaluation/ReDoSEvaluation
python3 ReScure_Result_Analysis.py > /workspace/output/rescure_analysis.txt # I think: iff pass@k = 0 it is good bc it means that the model did not find any vulnerabilities
# the file is with name and scores so we dont need to match later

echo "[Step 9] Running ReDoSHunter..."
cd /workspace/ReDoSHunter
# Raw
cp /workspace/RegexEval/Evaluation/ReDoSEvaluation/Input_Data/GPT3.5_Raw_Output.txt ./data/paper_dataset/regexlib.txt
mvn exec:java -Dexec.mainClass="cn.ac.ios.Test"
latest_file=$(ls -t ./data/expr/regexlib_redos_s_java*.txt | head -n 1)
cp "$latest_file" /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReDoSHunter_Results/GPT3.5_Raw_Output_full_result.txt
rm "$latest_file" # just to be sure we do not use the same file for the next run
# Refined
cp /workspace/RegexEval/Evaluation/ReDoSEvaluation/Input_Data/GPT3.5_Refined_Output.txt ./data/paper_dataset/regexlib.txt
mvn exec:java -Dexec.mainClass="cn.ac.ios.Test"
latest_file=$(ls -t ./data/expr/regexlib_redos_s_java*.txt | head -n 1)
cp "$latest_file" /workspace/RegexEval/Evaluation/ReDoSEvaluation/ReDoSHunter_Results/GPT3.5_Refined_Output_full_result.txt

echo "[Step 10] Analyzing ReDoSHunter results..."
cd /workspace/RegexEval/Evaluation/ReDoSEvaluation
python3 ReDoSHunter_Result_Analysis.py > /workspace/output/redoshunter_analysis.txt

echo "[✓] All steps completed. Outputs are in /workspace/output"
