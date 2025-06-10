import ast
from base.postprocessor import StudyPostprocessor
import os
import re
import pandas as pd

class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)
        self.languages = ['Python']

    def _configure(self):
        pass

    def postprocess(self):
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence')
        # TODO use another dataframe structure to store the results
        combined_results = { # all dfs need also a "type" column and run number column
            "dfa": pd.DataFrame(columns=["type", "run_number","DFA-EQ@1", "DFA-EQ@3", "DFA-EQ@10"]),
            "em": pd.DataFrame(columns=["type", "run_number","EM"]),
            "pass_at_k": pd.DataFrame(columns=["type", "run_number","pass_at_1", "pass_at_3", "pass_at_10"]),
            "vul_rescue": pd.DataFrame(columns=["type", "run_number","vul@1_rescue", "vul@3_rescue", "vul@10_rescue"]),
            "vul_redos_hunter": pd.DataFrame(columns=["type", "run_number","vul@1_redos", "vul@3_redos", "vul@10_redos"])
        }

        # Loop through directories in evidence_dir
        for dir_name in os.listdir(evidence_dir):
            dir_path = os.path.join(evidence_dir, dir_name)
            result = { # all dfs need also a "type" column and run number column
                "dfa": pd.DataFrame(columns=["type", "run_number","DFA-EQ@1", "DFA-EQ@3", "DFA-EQ@10"]),
                "em": pd.DataFrame(columns=["type", "run_number","EM"]),
                "pass_at_k": pd.DataFrame(columns=["type", "run_number","pass_at_1", "pass_at_3", "pass_at_10"]),
                "vul_rescue": pd.DataFrame(columns=["type", "run_number","vul@1_rescue", "vul@3_rescue", "vul@10_rescue"]),
                "vul_redos_hunter": pd.DataFrame(columns=["type", "run_number","vul@1_redos", "vul@3_redos", "vul@10_redos"])
            }
            if os.path.isdir(dir_path):
                file_path = os.path.join(dir_path, 'dfa_eq_k.txt')
                with open(file_path, 'r') as f:
                    content = f.read()
                    pattern = re.compile(
                        r'GPT3\.5_(?P<type>[\w]+)_Output\n'
                        r'DFA-EQ@1:\s*(?P<eq1>[\d.]+)\n'
                        r'DFA-EQ@3:\s*(?P<eq3>[\d.]+)\n'
                        r'DFA-EQ@10:\s*(?P<eq10>[\d.]+)',
                        re.MULTILINE
                    )
                    matches = pattern.finditer(content)
                    for m in matches:
                        dict_row = {
                            "type": m.group('type'),
                            "run_number": dir_name,
                            "DFA-EQ@1": float(m.group('eq1')),
                            "DFA-EQ@3": float(m.group('eq3')),
                            "DFA-EQ@10": float(m.group('eq10'))
                        }
                        result['dfa'] = pd.concat([result['dfa'], pd.DataFrame([dict_row])], ignore_index=True)
                        combined_results['dfa'] = pd.concat([combined_results['dfa'], pd.DataFrame([dict_row])], ignore_index=True)
                        
                file_path = os.path.join(dir_path, 'em_eval.txt')
                with open(file_path, 'r') as f:
                    content = f.read()
                    pattern = re.compile(r'GPT3\.5_([\w]+)_Output\n([\d.]+)', re.MULTILINE)
                    matches = pattern.findall(content)
                    for type, score in matches:
                        result['em'] = pd.concat([result['em'], pd.DataFrame([{
                            "type": type,
                            "run_number": dir_name,
                            "EM": float(score)
                        }])], ignore_index=True)
                        combined_results['em'] = pd.concat([combined_results['em'], pd.DataFrame([{
                            "type": type,
                            "run_number": dir_name,
                            "EM": float(score)
                        }])], ignore_index=True)
                file_path = os.path.join(dir_path, 'pass_at_k.txt')
                with open(file_path, 'r') as f:
                # first one is raw secon refined type always, parse as dict
                    for idx, line in enumerate(f):
                        d = ast.literal_eval(line.strip())
                        if idx == 0:
                            type_ = "Raw"
                        elif idx == 1:
                            type_ = "Refined"
                        else:
                            continue  # skip extra lines
                        dict_row = {
                            "type": type_,
                            "run_number": dir_name,
                            "pass_at_1": d.get('pass@1'),
                            "pass_at_3": d.get('pass@3'),
                            "pass_at_10": d.get('pass@10')
                        }
                        result['pass_at_k'] = pd.concat([result['pass_at_k'], pd.DataFrame([dict_row])], ignore_index=True)
                        combined_results['pass_at_k'] = pd.concat([combined_results['pass_at_k'], pd.DataFrame([dict_row])], ignore_index=True)
                file_path = os.path.join(dir_path, 'rescure_analysis.txt')
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if line.strip().startswith('{'):
                            d = ast.literal_eval(line.strip())
                            if idx == 1:
                                type_ = "Raw"
                            elif idx == 3:
                                type_ = "Refined"
                            else:
                                continue
                            dict_row = {
                                "type": type_,
                                "run_number": dir_name,
                                "vul@1_rescue": d.get('pass@1'),
                                "vul@3_rescue": d.get('pass@5'),
                                "vul@10_rescue": d.get('pass@10')
                            }
                            result['vul_rescue'] = pd.concat([result['vul_rescue'], pd.DataFrame([dict_row])], ignore_index=True)
                            combined_results['vul_rescue'] = pd.concat([combined_results['vul_rescue'], pd.DataFrame([dict_row])], ignore_index=True)
                file_path = os.path.join(dir_path, 'redoshunter_analysis.txt')
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if line.strip().startswith('{'):
                            d = ast.literal_eval(line.strip())
                            if idx == 1:
                                type_ = "Raw"
                            elif idx == 3:
                                type_ = "Refined"
                            else:
                                continue
                            dict_row = {
                                "type": type_,
                                "run_number": dir_name,
                                "vul@1_redos": d.get('pass@1'),
                                "vul@3_redos": d.get('pass@3'),
                                "vul@10_redos": d.get('pass@10')
                            }
                            result['vul_redos_hunter'] = pd.concat([result['vul_redos_hunter'], pd.DataFrame([dict_row])], ignore_index=True)
                            combined_results['vul_redos_hunter'] = pd.concat([combined_results['vul_redos_hunter'], pd.DataFrame([dict_row])], ignore_index=True)
            for key, df in result.items():
                if not df.empty:
                    df.to_csv(os.path.join(dir_path, f"{key}_results.csv"), index=False)
                else:
                    print(f"No data found for {key}, skipping CSV creation.")
        # Save combined results & cacl averages and put them in a report.txt
        report_path = os.path.join(evidence_dir, 'report.txt')
        with open(report_path, 'w') as report_file:
            for key, df in combined_results.items():
                if not df.empty:
                    df.to_csv(os.path.join(evidence_dir, f"{key}_combined_results.csv"), index=False)
                    averages = df.groupby("type", as_index=False).mean() # TODO need to verify this output
                    report_file.write(f"{key} Averages:\n")
                    for k, v in averages.items():
                        report_file.write(f"{k}: {v}\n")
                    report_file.write("\n")
                else:
                    report_file.write(f"No data found for {key}, skipping CSV creation.\n")
        print("Postprocessing completed. Results saved in evidence directory.")
