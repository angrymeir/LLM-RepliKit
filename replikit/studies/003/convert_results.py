import pandas as pd
from collections import defaultdict
import os
from numbers_parser import Document

def get_results_files(evidence_dirs):
    evidence_files = defaultdict(list)
    for evidence_dir in evidence_dirs:
        filenames = os.listdir(evidence_dir)
        for filename in filenames:
            if filename.endswith(".csv"):
                platform = filename.split("_")[0] 
                evidence_files[platform].append(evidence_dir + filename)
    return evidence_files

def parse_results(evidence_files, results_dir):
    for platform, filenames in evidence_files.items():
        assessment = defaultdict(list)
        for filename in filenames:
            df = pd.read_csv(filename)
            # get all checklist entries and their scores and put them into assessment
            df.drop(columns=['Explanation'], inplace=True)
            for _, row in df.iterrows():
                assessment[row['Question']].append(row['Score'])
        
        # generate a dataframe from the assessment
        df = pd.DataFrame(assessment).transpose()
        # rename the columns from 0, 1, .., n to doc0, doc1, ..., docn
        df.columns = [f"doc{i}" for i in range(len(df.columns))]
        # append the max value of the row to the dataframe
        df['Score'] = df.max(axis=1)

        # save the dataframe to a new csv file
        filename = f"{results_dir}{platform}-{platform}.csv"
        df.to_csv(filename, index=True, index_label='Checklist')
    
def map_questions():
    question_mapping = {}
    with open("expert_vs_gpt_vs_doxpy/data/checklist/checklist_for_marketplaces.txt", "r") as original_questions_marketplaces:
        original_questions_ma = original_questions_marketplaces.readlines()
    with open("expert_vs_gpt_vs_doxpy/data/checklist/p2b_questions_for_marketplaces.txt", "r") as new_questions_marketplaces:
        new_questions_ma = new_questions_marketplaces.readlines()

    for i in range(len(original_questions_ma)):
        question_mapping[original_questions_ma[i].strip()] = new_questions_ma[i].strip()

    # All but three questions are the same for the search engine and the marketplaces
    with open("expert_vs_gpt_vs_doxpy/data/checklist/checklist_for_search_engines.txt", "r") as original_questions_search_engines:
        original_questions_se = original_questions_search_engines.readlines()
    with open("expert_vs_gpt_vs_doxpy/data/checklist/p2b_questions_for_search_engines.txt", "r") as new_questions_search_engines:
        new_questions_se = new_questions_search_engines.readlines()

    for i in range(len(original_questions_se)):
        question_mapping[original_questions_se[i].strip()] = new_questions_se[i].strip()

    return question_mapping

def generate_data_analysis_table(results_dir):
    question_mapping = map_questions()
    doc = Document("expert_vs_gpt_vs_doxpy/data/assessment_results/all_results.numbers")
    sheets = doc.sheets
    for file in os.listdir(results_dir):
        if file.endswith(".csv"):
            platform = file.split("-")[0]
            df = pd.read_csv(results_dir + '/' + file)
            df.sort_values(by=['Checklist'], inplace=True)
            
            # drop all columns that have "doc" in the name, as we only look at the ChatGPT 4 column
            df.drop(columns=[col for col in df.columns if "doc" in col], inplace=True)
            df.rename(columns={'Score': 'ChatGPT 4'}, inplace=True)
            # change entries in ChatGPT 4 column. If value is below 3 insert N-value, otherwise insert Y-value

            # The extra step of checking if the value is actually is an integer is necessary, as the authors originally also did not classify floats with Y or N.
            def convert_entry(x):
                if x-int(x) == 0:
                    if x < 3:
                        return 'N-{}'.format(int(x))
                    else:
                        return 'Y-{}'.format(int(x))
                else:
                    return x

            df['ChatGPT 4'] = df['ChatGPT 4'].apply(lambda x: convert_entry(x))

            checklists = df['Checklist'].to_list() 
            questions = [question_mapping[question] for question in checklists]
            df['Questions'] = questions

            sheet = sheets[platform]
            table = sheet.tables
            data = table[0].rows(values_only=True)
            columns = data[0]
            reponses = data[1:]
            new_df = pd.DataFrame(reponses, columns=columns)
            
            exp1 = []
            exp2 = []
            exp3 = []
            for question in df['Checklist'].to_list():
                resp0 = new_df[new_df['Checklist'] == question]['Expert 1'].values[0]
                resp1 = new_df[new_df['Checklist'] == question]['Expert 2'].values[0]
                resp2 = new_df[new_df['Checklist'] == question]['Expert 3'].values[0]
                exp1.append(resp0)
                exp2.append(resp1)
                exp3.append(resp2)
            df['Expert 1'] = exp1
            df['Expert 2'] = exp2
            df['Expert 3'] = exp3
            df['Expert 1'] = df['Expert 1'].astype(int)
            df['Expert 2'] = df['Expert 2'].astype(int)
            df['Expert 3'] = df['Expert 3'].astype(int)

            # As we don't replicate those values, we set them to 0 and empty string and don't mind them. This has no impact on the analysis of the GPT-4 values.
            df['Explanatory Relevance Score'] = [0]*df.shape[0]
            df['DoX Score'] = [0]*df.shape[0]
            df['Pertinence Score'] = [0]*df.shape[0]
            df['ChatGPT 3.5'] = ["N-0"]*df.shape[0]
            df['DoXpert'] = [""]*df.shape[0]

            # save the dataframe to a new csv file
            filename = f"expert_vs_gpt_vs_doxpy/code/data_analysis/experts_vs_tools/tables/{platform}-{platform}.csv"
            df.to_csv(filename, index=False)

evidence_dirs = ["expert_vs_gpt_vs_doxpy/code/gpt_based_approach/search_engines/results/gpt4/",
                 "expert_vs_gpt_vs_doxpy/code/gpt_based_approach/marketplaces/results/gpt4/"]
results_dir = "expert_vs_gpt_vs_doxpy/data/assessment_results/chatgpt-based/GPT-4/"


# We read all results for the gpt 4 models experiments
evidence_files = get_results_files(evidence_dirs)
# We parse the results and put them into the general assessment_results directory
parse_results(evidence_files, results_dir)
# We transform the results stored in the general assessment_results directory into tables for the data analysis
generate_data_analysis_table(results_dir)