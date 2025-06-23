import ast
import copy
import json

import numpy as np
from base.postprocessor import StudyPostprocessor
import os
import re
import pandas as pd


class PostProcessor(StudyPostprocessor):
    def __init__(self, config):
        super().__init__(config)
        self.languages = ["Python"]

    def _configure(self):
        pass

    def compute_parseable_ratio(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        passed_count = sum(item["passed"] for item in data)
        total_count = len(data)
        return passed_count / total_count if total_count > 0 else 0
    
    def remove_old_summary_files(self):
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, "evidence")

        if not os.path.exists(evidence_dir):
            return

        print("Removing old summary files...")
        for filename in ['all_runs_scores.csv', 'average_scores.csv', 'report.txt']:
            file_path = os.path.join(evidence_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

        for subdir in ['raw_plots', 'refined_plots']:
            dir_path = os.path.join(evidence_dir, subdir)
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(dir_path)


    def postprocess(self, statistics_only):
        if self.config.get("use_kubernetes", False):
            return
        print("Starting postprocessing...")
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, "evidence")
        self.remove_old_summary_files()
        base_row = {
            "run_number": "0",
            "parseable": 0.0,
            "EM": 0.0,
            "DFA-EQ@1": 0.0,
            "DFA-EQ@3": 0.0,
            "DFA-EQ@10": 0.0,
            "pass_at_1": 0.0,
            "pass_at_3": 0.0,
            "pass_at_10": 0.0,
            "vul@1_rescue": 0.0,
            "vul@3_rescue": 0.0,
            "vul@10_rescue": 0.0,
            "vul@1_redos": 0.0,
            "vul@3_redos": 0.0,
            "vul@10_redos": 0.0,
        }

        df_all_runs = None
        # Loop through directories in evidence_dir
        for dir_name in os.listdir(evidence_dir):
            dir_path = os.path.join(evidence_dir, dir_name)
            if os.path.isdir(dir_path):
                raw_row = copy.deepcopy(base_row)
                raw_row["type"] = "raw"
                refined_row = copy.deepcopy(base_row)
                refined_row["type"] = "refined"
                df_single_run = pd.DataFrame([raw_row, refined_row]).set_index("type")
                # run_number
                df_single_run.at["raw", "run_number"] = str(dir_name)
                df_single_run.at["refined", "run_number"] = str(dir_name)
                # parseable
                raw_file = os.path.join(
                    dir_path, "GPT3.5_Raw_Output_Compiled_Result.json"
                )
                refined_file = os.path.join(
                    dir_path, "GPT3.5_Refined_Output_Compiled_Result.json"
                )

                df_single_run.at["raw", "parseable"] = self.compute_parseable_ratio(
                    raw_file
                )
                df_single_run.at["refined", "parseable"] = self.compute_parseable_ratio(
                    refined_file
                )
                # DFA_EQ@k
                file_path = os.path.join(dir_path, "dfa_eq_k.txt")
                with open(file_path, "r") as f:
                    content = f.read()
                    pattern = re.compile(
                        r"GPT3\.5_(?P<type>[\w]+)_Output\n"
                        r"DFA-EQ@1:\s*(?P<eq1>[\d.]+)\n"
                        r"DFA-EQ@3:\s*(?P<eq3>[\d.]+)\n"
                        r"DFA-EQ@10:\s*(?P<eq10>[\d.]+)",
                        re.MULTILINE,
                    )
                    matches = pattern.finditer(content)
                    for m in matches:
                        df_single_run.loc[
                            m.group("type").lower(),
                            ["DFA-EQ@1", "DFA-EQ@3", "DFA-EQ@10"],
                        ] = [
                            float(m.group("eq1")),
                            float(m.group("eq3")),
                            float(m.group("eq10")),
                        ]
                # EM
                file_path = os.path.join(dir_path, "em_eval.txt")
                with open(file_path, "r") as f:
                    content = f.read()
                    pattern = re.compile(
                        r"GPT3\.5_([\w]+)_Output\n([\d.]+)", re.MULTILINE
                    )
                    matches = pattern.findall(content)
                    for type, score in matches:
                        df_single_run.at[type.lower(), "EM"] = float(score)
                # Pass@k
                file_path = os.path.join(dir_path, "pass_at_k.txt")
                with open(file_path, "r") as f:
                    # first one is raw secon refined type always, parse as dict
                    for idx, line in enumerate(f):
                        d = ast.literal_eval(line.strip())
                        if idx == 0:
                            type_ = "raw"
                        elif idx == 1:
                            type_ = "refined"
                        else:
                            continue  # skip extra lines
                        df_single_run.at[type_, "pass_at_1"] = d.get("pass@1", -1.0)
                        df_single_run.at[type_, "pass_at_3"] = d.get("pass@3", -1.0)
                        df_single_run.at[type_, "pass_at_10"] = d.get("pass@10", -1.0)
                # Rescue
                file_path = os.path.join(dir_path, "rescure_analysis.txt")
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if line.strip().startswith("{"):
                            d = ast.literal_eval(line.strip())
                            if idx == 1:
                                type_ = "raw"
                            elif idx == 3:
                                type_ = "refined"
                            else:
                                continue
                            df_single_run.at[type_, "vul@1_rescue"] = d.get(
                                "pass@1", -1.0
                            )
                            df_single_run.at[type_, "vul@3_rescue"] = d.get(
                                "pass@5", -1.0
                            )
                            df_single_run.at[type_, "vul@10_rescue"] = d.get(
                                "pass@10", -1.0
                            )
                # Redos Hunter
                file_path = os.path.join(dir_path, "redoshunter_analysis.txt")
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if line.strip().startswith("{"):
                            d = ast.literal_eval(line.strip())
                            if idx == 1:
                                type_ = "raw"
                            elif idx == 3:
                                type_ = "refined"
                            else:
                                continue
                            df_single_run.at[type_, "vul@1_redos"] = d.get(
                                "pass@1", -1.0
                            )
                            df_single_run.at[type_, "vul@3_redos"] = d.get(
                                "pass@3", -1.0
                            )
                            df_single_run.at[type_, "vul@10_redos"] = d.get(
                                "pass@10", -1.0
                            )
            # store single run dataframe as csv
            if not df_single_run.empty:
                df_single_run.to_csv(os.path.join(dir_path, "scores.csv"), index=True)
            else:
                print(f"No data found for folder {dir_name}, skipping CSV creation.")
            # append single run dataframe to the all runs dataframe
            df_single_run_reset = (
                df_single_run.reset_index()
            )  # reset index to have 'type' as a column
            if df_all_runs is None:
                df_all_runs = df_single_run_reset
            else:
                df_all_runs = pd.concat(
                    [df_all_runs, df_single_run_reset], ignore_index=True
                )
        df_all_runs.to_csv(
            os.path.join(evidence_dir, "all_runs_scores.csv"), index=False
        )
        # calc averages and put them in a report.txt
        grouped_averages = df_all_runs.groupby("type").mean(numeric_only=True)
        grouped_averages.to_csv(
            os.path.join(evidence_dir, "average_scores.csv"), index=True
        )
        report_path = os.path.join(evidence_dir, "report.txt")
        with open(report_path, "w") as report_file:
            report_file.write("Averages by type across all study runs:\n")
            for run_type, row in grouped_averages.iterrows():
                report_file.write(f"\nType: {run_type}\n")
                for col, avg in row.items():
                    report_file.write(f"{col}: {avg:.4f}\n")

            report_file.write("\n\nOverall Averages:\n")
            report_file.write(grouped_averages.to_string(index=True) + "\n")

            report_file.write("\n\nPosterior Percentiles for Metrics by Type:\n")
            numeric_cols = grouped_averages.columns
            run_types = ["raw", "refined"]

            for run_type in run_types:
                report_file.write(f"\n\nType: {run_type}\n")
                filtered_df = df_all_runs[df_all_runs["type"] == run_type]

                for col in numeric_cols:
                    values = filtered_df[col].dropna()
                    values = values[values >= 0].values  # Skip invalid entries
                    if len(values) > 0:
                        quantiles, posterior_quantiles = self._calculate_quantils(values)
                        plot_dir = os.path.join(
                            evidence_dir, f"{run_type}_plots"
                        )
                        os.makedirs(plot_dir, exist_ok=True)
                        self._plot_distribution(
                            values, file_path=os.path.join(plot_dir, f"{col}_distribution.png")
                        )
                        report_file.write(f"\nMetric: {col}\n")
                        for q in quantiles:
                            print(f"Posterior {int(q*100)}th percentile: {np.mean(posterior_quantiles[q]):.4f}")
                            report_file.write(f"Posterior {int(q*100)}th percentile: {np.mean(posterior_quantiles[q]):.4f}\n")
                    else:
                        report_file.write(f"\nMetric: {col} — No valid data.\n")

            report_file.write("\n\nDetailed Scores:\n")
            report_file.write(df_all_runs.to_string(index=False))

        print("Postprocessing completed. Results saved in evidence directory.")
