from base.postprocessor import StudyPostprocessor
import os
import re
from collections import defaultdict

class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)
        self.languages = ['Python', 'Java', 'C++', 'C', 'Go']

    def _configure(self):
        pass

    def postprocess(self):
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence'.format(
        ))
        
        results = {}
        for root, dirs, files in os.walk(evidence_dir):
            if len(dirs) == 0 and len(files) != 0:
                # get all files with pattern GPT-4_codenet_compileReport_from_<language>_to_<language>.txt
                pattern = re.compile(
                    r"^GPT-4_codenet_compileReport_from_(?P<source>Python|Java|C\+\+|C|Go)_to_(?P<target>Python|Java|C\+\+|C|Go)\.txt$"
                )
                temp_results = defaultdict(list)
                grouped_files = defaultdict(list)
                for file_name in files:
                    match = pattern.match(file_name)
                    if match:
                        source_lang = match.group('source')
                        full_path = os.path.join(root, file_name)
                        grouped_files[source_lang].append(full_path)

                for source, files in grouped_files.items():
                    for f in files:
                        with open(f, 'r') as file:
                            content = file.read()
                            # extract the number behind "Accuracy:"
                            match = re.search(r"Accuracy:\s*([\d.]+)", content)
                            if match:
                                accuracy = float(match.group(1))
                                temp_results[source].append(accuracy)
                results[root.split('/')[-1]] = temp_results
        # calculate the average accuracy for each language
        averages = {}
        for lang in self.languages:
            total = 0
            count = 0
            for study, data in results.items():
                if lang in data:
                    total += sum(data[lang])
                    count += len(data[lang])
            averages[lang] = total / count if count > 0 else 0
        print("Average accuracies across all studies:")
        for lang, avg in averages.items():
            print(f"{lang}: {avg:.2f}")
        with open(os.path.join(evidence_dir, 'report.txt'), 'w') as report_file:
            report_file.write("Average accuracies across all studies:\n")
            for lang, avg in averages.items():
                report_file.write(f"{lang}: {avg:.2f}\n")
            report_file.write("\nDetailed results per experiment run:\n")
            for repetition, data in results.items():
                report_file.write(f"Repetition: {repetition}\n")
                for lang, accuracies in data.items():
                    report_file.write(f"{lang}: {', '.join(map(str, accuracies))}\n")
                        
