import json
import os
import shutil
import sys

def append_evidence_saving_block(file_path: str):
    code_block = '''
# region inserted by Replicators
    labels.append(int(test_data[i]["target"]))
    preds.append(0 if "non-vulnerable" in response.lower() else 1)
    if "non-vulnerable" not in response.lower() and "vulnerable" not in response.lower():
        print(
            f"Warning: Response for index {i} does not contain 'non-vulnerable' or 'vulnerable'. Response: {response}",
            f"Config: {option}, Model: {model}, Top-k: {top_k}",
        )

score_dict = {}
score_dict["model"] = model
score_dict["prompt"] = option
score_dict["k"] = top_k
# score calcualtion copied from evaluator()
try:
    score_dict["accuracy"] = round(accuracy(preds, labels), 4)
except Exception as e:
    print(f"Error calculating accuracy: {e}")
    score_dict["accuracy"] = np.nan
try:
    score_dict["precision"] = round(precision(preds, labels), 4)
except Exception as e:
    print(f"Error calculating precision: {e}")
    score_dict["precision"] = np.nan
try:
    score_dict["recall"] = round(recall(preds, labels), 4)
except Exception as e:
    print(f"Error calculating recall: {e}")
    score_dict["recall"] = np.nan
try:
    score_dict["f1"] = round(f1_score(labels, preds), 4)
except Exception as e:
    print(f"Error calculating f1 score: {e}")
    score_dict["f1"] = np.nan
try:
    score_dict["f0.5"] = round(
        fbeta_score(labels, preds, average=None, beta=0.5)[1], 4
    )
except Exception as e:
    print(f"Error calculating f0.5 score: {e}")
    score_dict["f0.5"] = np.nan
f_save_result = open('generated_results/'+ model + '_' + option + '_' + str(top_k) + '.json','w')
f_save_result.write(json.dumps(score_dict, indent=4))
f_save.close()
f_save_result.close()
# endregion inserted by Replicators
    '''
    with open(file_path, "a") as f:
        f.write("\n" + code_block)

def comment_out_code_block(file_path: str):
    start_marker = "top_k ="
    end_marker_content = "#f_save.write(str(i)"

    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    in_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not in_block and stripped.startswith(start_marker):
            in_block = True
            new_lines.append("# region commented by Replicators\n")
        
        if in_block:
            if not stripped.startswith("#"):
                new_lines.append("# " + line)
            else:
                new_lines.append(line)
            if end_marker_content in stripped:
                new_lines.append("# endregion commented by Replicators\n")
                in_block = False
        else:
            new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)

def add_f05_print_after_f1(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()

    new_lines = []
    inserted = False
    target_line_snippet = "print(\"F1: \", f1_score(labels, preds))"

    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and target_line_snippet in line.replace("'", '"').strip():
            # Insert new print statement after this line, preserving indentation
            indent = line[:len(line) - len(line.lstrip())]  # one extra indent level
            new_lines.append(
                indent + "print(\n" +
                indent + '    "F0.5: ", fbeta_score(labels, preds, average=None, beta=0.5)[1]\n' +
                indent + ")  # added by Replicators\n"
            )
            inserted = True

    if not inserted:
        print("Warning: target print statement not found. No changes made.")
    else:
        with open(filepath, "w") as f:
            f.writelines(new_lines)

def replace_insert_stuff(filepath, topk, option):
    replacements = {
        "test_file_ = '../dataset/test_for_codexglue_binary.json'":
        'test_file_ = "dataset/test_for_codexglue_binary.json"',

        "train_file_ = '../dataset/train_for_codexglue_binary.json'":
        'train_file_ = "dataset/train_for_codexglue_binary.json"',
        "import pickle":"""import pickle
from sklearn.metrics import fbeta_score # added by Replicators
from dotenv import load_dotenv  # added by Replicators""",
    """key = '' ## Your KEY here""":"""key = ""  ## Your KEY here
load_dotenv()  # added by Replicators""",
"""with open('retrieval_pos_neg.pkl', 'rb') as f:""":"""        with open("ChatGPT_exp/retrieval_pos_neg.pkl", "rb") as f:""",
'openai.api_key = key':"""# openai.api_key = key # commented out by Replicators
openai.api_key = os.getenv("OPENAI_API_KEY")  # added by Replicators""",
"top_k = 5":f"""# Create output directory and files (added by Replicators)
output_dir = "generated_results" # added by Replicators
os.makedirs(output_dir, exist_ok=True) # added by Replicators\n
top_k = {topk}  # modified value by Replicators""",
"option = 'A5'":f"option = '{option}'  # modified value by Replicators",
"""#f_save = open('generated_results/'+ model + '_' + option + '_' + str(top_k) + '.txt','w')""":"""f_save = open('generated_results/'+ model + '_' + option + '_' + str(top_k) + '.txt','w')   # uncommented by Replicators""",
"for i in range(239, 260):": "# for i in range(239, 260):  # commented out by Replicators",
"#for i in range(len(test_data)):": "labels, preds = [], [] # added by Replicators\nfor i in range(len(test_data)): # uncommented by Replicators",
"#response = call_chatgpt(P, i)":"    response = call_chatgpt(P, i)",
"""#f_save.write(str(i) + ':\\t' + str(test_data[i]['target']) + '\\t' + response.strip().replace('\\n', 't') + '\\n')""":"""    f_save.write(str(i) + ':\\t' + str(test_data[i]['target']) + '\\t' + response.strip().replace('\\n', 't') + '\\n') # uncommented by Replicators""",
    }

    with open(filepath, "r") as f:
        lines = f.readlines()

    with open(filepath, "w") as f:
        for line in lines:
            stripped = line.strip()
            if stripped in replacements:
                f.write(replacements[stripped] + "\n")
            else:
                f.write(line)

def add_A54_code_block(file_path: str):
    find_str = """    elif option == 'A5':
    
        P = "Now you need to identify whether a method contains any potential vulnerability or not. If has vulnerability, output: 'this code is vulnerable'. Otherwise, output: 'this code is non-vulnerable'. You only to give the prior two answers."
        with open('retrieval_pos_neg.pkl', 'rb') as f:
            retrieval_methods = pickle.load(f)
    
        retrieval_method = retrieval_methods[idx]
        for retrieval_ in retrieval_method[0:topk]:
             print (retrieval_[1])
             if int(retrieval_[1]) == 0 : 
                #P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:1000] + "\\n Let's Start: this code is non-vulnerable. "
                P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:2000] + "\\n Let's Start: this code is non-vulnerable. " 
             else:
                #P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:1000] + "\\n Let's Start: this code is vulnerable. "
                P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:2000] + "\\n Let's Start: this code is vulnerable. "
        P = P + "The Code is: \\n " + input_ + "\\n Let's Start: \""""
    insert_str = """    elif option == 'A5':
    
        P = "Now you need to identify whether a method contains any potential vulnerability or not. If has vulnerability, output: 'this code is vulnerable'. Otherwise, output: 'this code is non-vulnerable'. You only to give the prior two answers."
        with open("ChatGPT_exp/retrieval_pos_neg.pkl", "rb") as f:
            retrieval_methods = pickle.load(f)
    
        retrieval_method = retrieval_methods[idx]
        for retrieval_ in retrieval_method[0:topk]:
             print (retrieval_[1])
             if int(retrieval_[1]) == 0 : 
                #P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:1000] + "\\n Let's Start: this code is non-vulnerable. "
                P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:2000] + "\\n Let's Start: this code is non-vulnerable. " 
             else:
                #P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:1000] + "\\n Let's Start: this code is vulnerable. "
                P = P + "The Code is: " + remove_spaces(retrieval_[0])[0:2000] + "\\n Let's Start: this code is vulnerable. "
        P = P + "The Code is: \\n " + input_ + "\\n Let's Start: \"
    # region inserted by Replicators -> the following case was copied from the original file ChatGPT_on_binary_vulner_detection_run54
    elif option == "A54":
        P = ""
        for ijj in range(10, 13):
            P = (
                P
                + "The Code is: \\n "
                + remove_spaces(vulnerable_functions[ijj])
                + "\\n Let's Start: this code is vulnerable. "
            )

        with (
            open("ChatGPT_exp/retrieval_pos_neg.pkl", "rb") as f
        ):  # modified by Replicators renamed from 'retrieval_pos_neg_codebert_top5_bp' to 'retrieval_pos_neg'
            retrieval_methods = pickle.load(f)

        retrieval_method = retrieval_methods[idx]
        for retrieval_ in retrieval_method[0:3]:
            # print (retrieval_[1]) # commented out by Replicators
            if int(retrieval_[1]) == 0:
                P = (
                    P
                    + "The Code is: "
                    + remove_spaces(retrieval_[0])
                    + "\\n Let's Start: this code is non-vulnerable. "
                )
            else:
                P = (
                    P
                    + "The Code is: "
                    + remove_spaces(retrieval_[0])
                    + "\\n Let's Start: this code is vulnerable. "
                )

        # P = P + "The Code is: \\n " + clean_functions[0] + "\\n Let's Start: this code is non-vulnerable."

        P = (
            P
            + "You need to identify whether a method contains any potential vulnerability or not. If has any potential vulnerability, output: 'this code is vulnerable'. Otherwise, output: 'this code is non-vulnerable'. The Code is: \\n "
            + input_
            + "\\n Let's Start: "
        )
    # endregion inserted by Replicators"""
    with open(file_path, "r") as f:
        content = f.read()
    if find_str in content:
        content = content.replace(find_str, insert_str)
        with open(file_path, "w") as f:
            f.write(content)

def apply_modifications(original_file_path: str = '/home/amougou/LLM-RepliKit/replikit/studies/007/ChatGPT_exp/original.py'):
    with open("replication_config.json", "r") as f:
        configs = json.load(f)
    for config in configs["gpt3dot5"]:
        top_k = config.get("top_k", 1)
        option = config.get("option", "basic")
        os.makedirs("scripts", exist_ok=True)
        target_file = f"scripts/vulner_detector_gpt3dot5_{option}_{top_k}.py"
        shutil.copy(original_file_path, target_file)

        add_f05_print_after_f1(target_file)
        add_A54_code_block(target_file)
        replace_insert_stuff(target_file, top_k, option)
        append_evidence_saving_block(target_file)
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        original_file_path = sys.argv[1]
        apply_modifications(original_file_path)
    else:
        print("Usage: python modifier.py <path_to_original_file>")
    