from base.postprocessor import StudyPostprocessor
import os
import re
import numpy as np
from collections import defaultdict

class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)
        self.languages = ['Python']

    def _configure(self):
        pass

    def postprocess(self):
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence')

        results = {}
        pattern = re.compile(
            r"^GPT-4_codenet_compileReport_from_(?P<source>Python|Java|C\+\+|C|Go)_to_(?P<target>Python|Java|C\+\+|C|Go)\.txt$"
        )

        for root, _, files in os.walk(evidence_dir):
            temp_results = defaultdict(list)
            for file_name in files:
                match = pattern.match(file_name)
                if match:
                    source_lang = match.group('source')
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r') as file:
                        content = file.read()
                        accuracy_match = re.search(r"Accuracy:\s*([\d.]+)", content)
                        if accuracy_match:
                            temp_results[source_lang].append(float(accuracy_match.group(1)))
            if temp_results:
                results[os.path.basename(root)] = temp_results

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

        observed_precisions = np.array(language_accuracies['Python'])
        quantiles = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
        n = len(observed_precisions)
        n_samples = 10000

        posterior_quantiles = {q: [] for q in quantiles}
        for _ in range(n_samples):
            weights = np.random.dirichlet(np.ones(n))
            sorted_idx = np.argsort(observed_precisions)
            sorted_vals = observed_precisions[sorted_idx]
            sorted_weights = weights[sorted_idx]
            cum_weights = np.cumsum(sorted_weights)
            for q in quantiles:
                idx = np.searchsorted(cum_weights, q)
                posterior_quantiles[q].append(sorted_vals[min(idx, n-1)])

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
