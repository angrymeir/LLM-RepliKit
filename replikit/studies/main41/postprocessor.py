import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from base.postprocessor import StudyPostprocessor

class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)
        self.reported_data_points = {
            # Data reported in main41, Table 6
            'Java_BM25': 16.68,
            'Java_ASAP': 16.96,
            'Python_BM25': 15.01,
            'Python_ASAP': 16.38,
            'PHP_BM25': 18.48,
            'PHP_ASAP': 19.99,
        }

    def _configure(self):
        pass

    @staticmethod
    def read_score_from_file(file_path: str) -> float:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        return float(content)

    def read_all_scores(self, evidence_dir: str) -> pd.DataFrame:
        """
        Reads the score of each run and experiment from the evidence directory.
        """
        results = {
            'Java_BM25': [],
            'Java_ASAP': [],
            'Python_BM25': [],
            'Python_ASAP': [],
            'PHP_BM25': [],
            'PHP_ASAP': []
        }

        for subdir in os.listdir(evidence_dir):
            run_dir = os.path.join(evidence_dir, subdir)
            if not os.path.isdir(run_dir):
                continue

            java_dir = os.path.join(run_dir, 'Java_result')
            python_dir = os.path.join(run_dir, 'Python_result')
            php_dir = os.path.join(run_dir, 'PHP_result')

            asap_file_name = 'turbo_BM25_repo_dfg_id3.score'
            bm25_file_name = 'turbo_BM25.score'

            results['Java_BM25'].append(self.read_score_from_file(os.path.join(java_dir, bm25_file_name)))
            results['Java_ASAP'].append(self.read_score_from_file(os.path.join(java_dir, asap_file_name)))
            results['Python_BM25'].append(self.read_score_from_file(os.path.join(python_dir, bm25_file_name)))
            results['Python_ASAP'].append(self.read_score_from_file(os.path.join(python_dir, asap_file_name)))
            results['PHP_BM25'].append(self.read_score_from_file(os.path.join(php_dir, bm25_file_name)))
            results['PHP_ASAP'].append(self.read_score_from_file(os.path.join(php_dir, asap_file_name)))

        return pd.DataFrame.from_dict(results)


    def create_boxplot(self, df: pd.DataFrame) -> plt.Figure:
        """
        Create a box plot of the evidence. Also adds the originally reported values as red dots.
        """
        # Create a box plot for all columns
        fig = plt.figure(figsize=(12, 8))
        ax = df.boxplot()

        # Add the new data points as red circles
        for i, col in enumerate(df.columns):
            if col in self.reported_data_points:
                # Get the x-position for the current column's box plot
                # The boxplot function typically places boxes at x-coordinates 1, 2, 3...
                # so we can use the 1-based index of the column
                col_index = list(df.columns).index(col)
                x_position = i + 1  # x-positions are 1-indexed for boxplots

                # Plotting a red circle at the specific point
                ax.plot(x_position, self.reported_data_points[col], 'ro', markersize=8)

        plt.title('Box-plot of the experiments outcome-dsitribution. Author-reported values in red.')
        plt.ylabel('Values')
        plt.xlabel('Columns')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return fig

    def report_quantiles(self, df: pd.DataFrame, report_path: str) -> None:

        posterior_quantiles = {col: self._calculate_quantils(df[col].to_numpy())[1] for col in df.columns}
        quantiles = list(posterior_quantiles[df.columns[0]].keys())
        n_quantiles = len(quantiles)

        # result table
        with open(report_path, 'a+') as f:
            f.write(f"## Posterior Quantiles\n")
            # Table header
            f.write(f"|    | claimed / originally reported value|")
            for q in quantiles:
                f.write(f" {q*100}th posterior percentile |")
            f.write("\n")
            f.write("|---|---|" + "---|" * n_quantiles + "\n")

            # table
            for col in df.columns:
                f.write(f"| {col} | {self.reported_data_points[col]} |")
                exp_pq = posterior_quantiles[col]
                for q in quantiles:
                    f.write(f" {np.mean(exp_pq[q]):.3f} |")
                f.write("\n")
            f.write("\n")

    def report_all_runs(self, df: pd.DataFrame, report_path: str) -> None:
        with open(report_path, 'a+') as f:
            f.write(f"## Results from each run\n\n")
            f.write("| run id |")
            for col in df.columns:
                f.write(f" {col} |")
            f.write("\n")
            f.write("|---|" + "---|" * len(df.columns) + "\n")

            for i in df.index:
                f.write(f"| {i} |")
                for col in df.columns:
                    f.write(f" {df.loc[i, col]:.03f} |")
                f.write("\n")
            f.write("\n")


    def postprocess(self, statistics_only: bool):
        print("Postprocessing everything...")

        parent_dir = os.path.dirname(os.path.abspath(__file__))
        evidence_dir = os.path.join(parent_dir, 'evidence')
        report_path = os.path.join(evidence_dir, 'report.md')

        with open(report_path, 'w+') as f:
            f.write("# Report for reproduction runs of main41\n\n")

        df = self.read_all_scores(evidence_dir)

        self.report_quantiles(df, report_path)

        fig = self.create_boxplot(df)
        fig.savefig(os.path.join(evidence_dir, 'result_boxplot.png'))
        with open(report_path, 'a+') as f:
            f.write("## Boxplot\n\n![image](result_boxplot.png)\n\n")

        if not statistics_only:
            self.report_all_runs(df, report_path)

        print(f"Done, find results in {report_path}")
