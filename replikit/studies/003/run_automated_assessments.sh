# Original code

source .env/bin/activate

cd expert_vs_gpt_vs_doxpy/code/gpt_based_approach/marketplaces/

# Delete evidence of previous runs
rm -rf ./*.pkl
python3 ./gpt4_assessment.py

cd ../search_engines/
rm -rf ./*.pkl
python3 ./gpt4_assessment.py
