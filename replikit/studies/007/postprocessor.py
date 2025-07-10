from glob import glob
import json
import os
import re
from collections import defaultdict

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from base.postprocessor import StudyPostprocessor


class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        pass

    def create_csv_files(self):
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence')
        
        subdirs = [d for d in os.listdir(evidence_dir) if os.path.isdir(os.path.join(evidence_dir, d))]
        
        for subdir in subdirs:
            subdir_path = os.path.join(evidence_dir, subdir)
            json_files = glob(os.path.join(subdir_path, '*.json'))

            if not json_files:
                continue
            
            dfs = []
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)

                    if isinstance(data, dict):
                        df = pd.DataFrame([data])
                        df.fillna(0, inplace=True) # TODO is this valid in our case?
                        dfs.append(df)
                except Exception as e:
                    continue  # Skip files that cannot be read or parsed
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                csv_path = os.path.join(subdir_path, 'results_table.csv')
                combined_df.to_csv(csv_path, index=False)

    def postprocess(self, statistics_only):
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence')
        plots_dir = os.path.join(evidence_dir, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        self.create_csv_files()
        csv_paths = glob(os.path.join(evidence_dir, '**/results_table.csv'), recursive=True)
        dfs = []
        for path in csv_paths:
            df = pd.read_csv(path)
            dfs.append(df)
        all_data = pd.concat(dfs, ignore_index=True)

        # Ensure correct types
        for col in ['accuracy', 'precision', 'recall', 'f1', 'f0.5']:
            all_data[col] = pd.to_numeric(all_data[col], errors='coerce')

        # Aggregation
        group_cols = ['model', 'prompt', 'k']
        aggregated = all_data.groupby(group_cols, as_index=False).agg({
            'accuracy': 'mean',
            'precision': 'mean',
            'recall': 'mean',
            'f1': 'mean',
            'f0.5': 'mean'
        })

        # Save aggregated
        aggregated.to_csv(f'{evidence_dir}/aggregated_results.csv', index=False)

        # Report generation
        report_path = os.path.join(evidence_dir, 'report.txt')
        with open(report_path, 'w') as report_file:
            report_file.write("Average scores across all studies:\n")
            report_file.write(aggregated.to_string(index=False))
            report_file.write("\n\n")
            report_file.write("Posterior Percentiles (Quintiles) by configuration:\n")
            for group_key, group_df in all_data.groupby(group_cols):
                model, prompt, k = group_key
                report_file.write(f"\n=== Configuration: model={model}, prompt={prompt}, k={k} ===\n")
                for metric in ['accuracy', 'precision', 'recall', 'f1', 'f0.5']:
                    values = group_df[metric].dropna()
                    values = values[values >= 0]
                    if len(values) > 0:
                        quantiles, posterior_quantiles = self._calculate_quantils(values)
                        report_file.write(f"\nMetric: {metric}\n")
                        for q in quantiles:
                            percentile_value = np.mean(posterior_quantiles[q])
                            report_file.write(f"Posterior {int(q * 100)}th percentile: {percentile_value:.4f}\n")

                        # Save plot
                        plot_name = f"{model}_{prompt}_k{k}_{metric}_distribution.png".replace(" ", "_").replace("/", "_")
                        plot_path = os.path.join(plots_dir, plot_name)
                        self._plot_distribution(values, plot_path)
                    else:
                        report_file.write(f"\nMetric: {metric} — No valid data.\n")

            report_file.write("\n\nDetailed results per experiment run:\n")
            for idx, df in enumerate(dfs):
                report_file.write(f"Repetition: {idx}\n")
                report_file.write(df.to_string(index=False))
                report_file.write("\n" + "=" * 40 + "\n")

        print("Postprocessing completed. Results saved to aggregated_results.csv, report.txt, and plots/.")
