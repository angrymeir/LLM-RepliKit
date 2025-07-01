from base.postprocessor import StudyPostprocessor
import pandas as pd
import numpy as np
import os
import glob


class PostProcessor(StudyPostprocessor):

    def __init__(self, config):
        super().__init__(config)

    def _configure(self):
        self.study_dir = os.path.dirname(os.path.abspath(__file__))
        self.evidence_dir = os.path.join(self.study_dir, "evidence")

    def postprocess(self, statistics_only):
        print("Postprocessing everything...")
        
        run_dirs = glob.glob(os.path.join(self.evidence_dir, "[0-9]*"))
        run_dirs.sort(key=lambda x: int(os.path.basename(x)))
        
        all_summaries = []
        
        for run_dir in run_dirs:
            run_number = os.path.basename(run_dir)
            summary_file = os.path.join(run_dir, "summary_2k.csv")
            
            if os.path.exists(summary_file):
                df = pd.read_csv(summary_file)
                df['run'] = run_number
                all_summaries.append(df)
                print(f"Loaded summary from run {run_number}")
        
        if all_summaries:
            combined_df = pd.concat(all_summaries, ignore_index=True)
            print(f"Combined {len(all_summaries)} runs into dataframe with {len(combined_df)} rows")
            
            # Calculate interquartiles for each metric by dataset
            numeric_columns = ['invacation_time', 'parsing_time', 'identified_templates', 
                             'ground_templates', 'GA', 'PA', 'FGA', 'FTA', 'ED']
            
            # Filter out the 'Average' rows for statistical analysis
            analysis_df = combined_df[combined_df['Dataset'] != 'Average']
            
            # Get unique datasets
            datasets = analysis_df['Dataset'].unique()
            quantiles_df = pd.DataFrame()
            for dataset in datasets:
                print(f"\n=== {dataset} Dataset Statistics ===")
                dataset_df = analysis_df[analysis_df['Dataset'] == dataset]
                
                for column in numeric_columns:
                    if column in dataset_df.columns:
                        values = dataset_df[column].dropna().tolist()
                        if values and len(values) > 1:
                            quantiles, posterior_quantiles = self._calculate_quantils(values)
                            columns = [f"Posterior {int(q*100)}th percentile" for q in quantiles]
                            columns.append("Metric")
                            data = [np.mean(posterior_quantiles[q]) for q in quantiles]
                            data.append(f"{dataset}_{column}")
                            if quantiles_df.empty:
                                quantiles_df = pd.DataFrame(data=[data], columns=columns)
                            else:
                                quantiles_df = pd.concat([quantiles_df, pd.DataFrame(data=[data], columns=columns)])
                            
                            # ensure distribution plot path exists
                            plot_dir = os.path.join(self.evidence_dir, "distributions")
                            os.makedirs(plot_dir, exist_ok=True)
 
                            # Plot distribution for each dataset-metric combination
                            plot_path = f"{plot_dir}/{dataset}_{column}_distribution.png"
                            self._plot_distribution(values, plot_path)
                            print(f"Distribution plot saved to: {plot_path}")
            
            quantiles_df.to_csv(os.path.join(self.evidence_dir, "quantiles.csv"), index=False)
            return quantiles_df
        else:
            print("No summary files found")
            return None

