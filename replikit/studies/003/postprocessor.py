from base.postprocessor import StudyPostprocessor
import os
import re
import numpy as np
import glob
from collections import defaultdict
import re
import pandas as pd
from io import StringIO

class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)
        self.languages = ['Python']

    def _configure(self):
        pass

    def postprocess(self, statistics_only):
        evidence_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'evidence')

        files = glob.glob(os.path.join(evidence_dir, "**", "container_logs.txt"), recursive=True)
        df = None
        for file in files:
            run_number = file.split("/")[-2]
            with open(file, 'r') as output_log:
                lines = output_log.readlines()
            
            start_idx = None
            for i, line in enumerate(lines):
                if "Table" in line and "ChatGPT 4" in line:
                    start_idx = i
                    break
            if start_idx is None:
                raise ValueError("Could not find start index for ChatGPT 4 results")
            
            table_lines = lines[start_idx:]
            table_text = ''.join(table_lines)

            df_tmp = pd.read_fwf(StringIO(table_text))[['Table', 'ChatGPT 4']]
            df_tmp.rename(columns={'ChatGPT 4': 'Run {}'.format(run_number)}, inplace=True)

            if df is None:
                df = df_tmp
            else:
                df = pd.merge(df, df_tmp, on='Table', how='outer')

            # set the index to the table name
            df.set_index('Table', inplace=True)

        quants = []
        for i, row in df.iterrows():
            self._plot_distribution(row.values, os.path.join(evidence_dir, f"{i}.png"))
            quantiles, posterior_quantiles = self._calculate_quantils(row.values)
            q_tmp = {}
            for q in quantiles:
                q_tmp[f"Posterior {int(q*100)}th percentile"] = np.mean(posterior_quantiles[q])
            quants.append(q_tmp)
        quants_df = pd.DataFrame(quants, index=df.index)
        print(quants_df)

        quants_df.to_csv(os.path.join(evidence_dir, "quantiles.csv"))

        # Compute average accuracy per language
        averages = {}
        for lang in self.languages:
            all_accuracies = [acc for data in results.values() if lang in data for acc in data[lang]]
            averages[lang] = np.mean(all_accuracies) if all_accuracies else 0.0

        print("Average accuracies across all studies:")
        for lang, avg in averages.items():
            print(f"{lang}: {avg:.2f}")

        # Prepare for posterior quantile computation
        language_accuracies = defaultdict(list)
        for data in results.values():
            for lang, accuracies in data.items():
                language_accuracies[lang].append(np.mean(accuracies))

        quantiles, posterior_quantiles = self._calculate_quantils(language_accuracies['Python'])

        self._plot_distribution(language_accuracies['Python'], os.path.join(evidence_dir, 'distribution.png'))
        
        # Write report
        with open(os.path.join(evidence_dir, 'report.txt'), 'w') as report:
            report.write("# Average accuracies across all studies:\n")
            for lang, avg in averages.items():
                report.write(f"{lang}: {avg:.2f}\n")

            report.write("\n# Posterior Percentiles\n")
            for q in quantiles:
                print(f"Posterior {int(q*100)}th percentile: {np.mean(posterior_quantiles[q]):.4f}")
                report.write(f"Posterior {int(q*100)}th percentile: {np.mean(posterior_quantiles[q]):.4f}\n")

            report.write("\n\n# Detailed results per experiment run:\n")
            for repetition, data in results.items():
                report.write(f"Repetition: {repetition}\n")
                for lang, accs in data.items():
                    report.write(f"{lang}: {', '.join(map(str, accs))}\n")
