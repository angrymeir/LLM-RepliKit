from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
from typing import Any

class StudyPostprocessor:
    """
    A base class for postprocessing a study replication package.

    This class outlines the steps required for postprocessing:
    - Aggregating all evidence collected during the study.
    - Structuring the aggregated evidence.
    - Analyzing the structured results.
    - Generating reports from the analysis.

    Subclasses should implement all internal methods to define the actual behavior.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize the StudyPostprocessor.

        Args:
            config (Any): Configuration data for the postprocessor.
        """
        self.config = config
        self._configure()

    def postprocess(self, statistics_only: bool) -> None:
        """
        Execute the postprocessing of the study.

        This method should orchestrate the entire postprocessing workflow,
        including evidence aggregation, structuring, analysis, and report generation.

        Args:
            statistics_only (bool): Whether to perform changes or only compute statistics.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _calculate_quantils(self, results: list, quantiles=[0.025,0.1,0.25,0.5,0.75,0.9,0.975]) -> list:
        """
        Estimate posterior quantiles from the given results using the Bayesian bootstrap.
        
        Args:
            results (list): List of numeric results from the study.
            quantiles (list, optional): List of quantile levels to compute. Defaults to [0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.975].
        
        Returns:
            tuple: A tuple where the first element is the list of quantiles,
                   and the second is a dictionary mapping each quantile to its estimated posterior samples.
        """
        if type(results) != np.array:
            results = np.array(results)
        n = len(results)
        n_samples = 10000

        posterior_quantiles = {q: [] for q in quantiles}
        for _ in range(n_samples):
            weights = np.random.dirichlet(np.ones(n))
            sorted_idx = np.argsort(results)
            sorted_vals = results[sorted_idx]
            sorted_weights = weights[sorted_idx]
            cum_weights = np.cumsum(sorted_weights)
            for q in quantiles:
                idx = np.searchsorted(cum_weights, q)
                posterior_quantiles[q].append(sorted_vals[min(idx, n-1)])
        return quantiles, posterior_quantiles

    def _plot_distribution(self, results: list, file_path: str) -> None:
        """
        Generate and save a histogram plot of the result distribution.

        Args:
            results (list): List of numerical results to be plotted.
            file_path (str): File path where the plot will be saved.
        """
        sns.set_context("paper", font_scale=1.3)
        plot = sns.displot(results, bins=100, label='Distribution', height=3, aspect=1.5)
        plot.figure.savefig(file_path)
        plt.close(plot.figure)


    def _configure(self) -> None:
        """
        Configure the postprocessor using the provided configuration.

        This method should prepare any internal structures or parameters needed
        for postprocessing.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def _aggregate_evidence(self, evidence: Any) -> Any:
        """
        Aggregate all evidence from the study.

        Args:
            evidence (Any): Raw evidence data collected during the study.

        Returns:
            Any: Aggregated evidence suitable for structuring.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def _structure_evidence(self, evidence: Any) -> Any:
        """
        Structure the aggregated evidence into a usable format.

        Args:
            evidence (Any): Aggregated evidence data.

        Returns:
            Any: Structured evidence ready for analysis.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def _analyze_results(self, evidence: Any) -> Any:
        """
        Analyze the structured evidence to extract results.

        Args:
            evidence (Any): Structured evidence data.

        Returns:
            Any: Analytical results derived from the evidence.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    
    def _generate_report(self, analysis: Any) -> Any:
        """
        Generate a report based on the analysis results.

        Args:
            analysis (Any): Results from the analysis phase.

        Returns:
            Any: Final report or summary output.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
