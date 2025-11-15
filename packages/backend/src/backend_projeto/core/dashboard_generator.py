"""
This module provides functionalities for generating various types of financial dashboards.

It includes the `DashboardGenerator` class which can create:
- Static HTML dashboards from processed analysis data.
- Interactive dashboards leveraging an `InteractiveVisualizer`.
- Sector-specific visualizations.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os
from typing import List, Dict, Any, Optional
import json # Import json for decoding Plotly figures
import numpy as np # Import numpy

from ..utils.config import Settings # Import Settings

# Import the InteractiveVisualizer
from .visualizations.interactive_visualization import InteractiveVisualizer

# Set default Plotly template
pio.templates.default = "plotly_white"

class DashboardGenerator:
    """
    Generates comprehensive financial dashboards from portfolio analysis data.
    """
    def __init__(self, config: Settings, output_path: str = "generated_dashboards"):
        """
        Initializes the DashboardGenerator.

        Args:
            config (Settings): Configuration object for the application.
            output_path (str): Directory to save generated dashboards. Defaults to "generated_dashboards".
        """
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        self.interactive_visualizer = InteractiveVisualizer()

    def generate_portfolio_dashboard_html(self,
                                          performance_data: pd.DataFrame,
                                          risk_return_data: pd.DataFrame,
                                          allocation_data: Dict[str, float],
                                          drawdown_data: pd.DataFrame,
                                          dashboard_name: str = "portfolio_dashboard") -> str:
        """
        Generates a comprehensive static HTML dashboard from various portfolio analysis data.

        This dashboard typically includes charts for cumulative performance, risk vs. return,
        asset allocation (pie chart), and drawdown.

        Args:
            performance_data (pd.DataFrame): DataFrame containing cumulative performance data.
                                             Expected columns are portfolio names, index is date.
            risk_return_data (pd.DataFrame): DataFrame with risk and return metrics for different portfolios.
                                             Expected columns: 'Risk', 'Return', 'Sharpe Ratio', 'Portfolio'.
            allocation_data (Dict[str, float]): Dictionary where keys are asset names and values are their allocations.
            drawdown_data (pd.DataFrame): DataFrame containing drawdown series. Expected column: 'Drawdown', index is date.
            dashboard_name (str): The name of the dashboard, used in the title.

        Returns:
            str: The HTML content of the generated dashboard.
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Cumulative Performance", "Risk vs. Return", "Asset Allocation", "Drawdown"),
            specs=[[{"type": "xy"}, {"type": "xy"}],
                   [{"type": "domain"}, {"type": "xy"}]]
        )

        # Cumulative Performance
        if not performance_data.empty:
            for column in performance_data.columns:
                fig.add_trace(go.Scatter(x=performance_data.index, y=performance_data[column], mode='lines', name=column), row=1, col=1)

        # Risk vs. Return
        if not risk_return_data.empty:
            fig.add_trace(go.Scatter(x=risk_return_data['Risk'], y=risk_return_data['Return'], mode='markers',
                                     marker=dict(size=10, color=risk_return_data['Sharpe Ratio'], colorscale='Viridis', showscale=True,
                                                 colorbar=dict(title='Sharpe Ratio')),
                                     text=risk_return_data['Portfolio'], hoverinfo='text'), row=1, col=2)

        # Asset Allocation
        if allocation_data:
            labels = list(allocation_data.keys())
            values = list(allocation_data.values())
            fig.add_trace(go.Pie(labels=labels, values=values, hole=.3), row=2, col=1)

        # Drawdown
        if not drawdown_data.empty:
            fig.add_trace(go.Scatter(x=drawdown_data.index, y=drawdown_data['Drawdown'], fill='tozeroy', mode='lines', name='Drawdown'), row=2, col=2)

        fig.update_layout(title_text=f"Portfolio Analysis Dashboard: {dashboard_name}", height=900, showlegend=True)

        # Return HTML string
        return pio.to_html(fig, full_html=True, include_plotlyjs='cdn')

    def generate_interactive_dashboard(self,
                                       returns: pd.DataFrame,
                                       assets: List[str],
                                       benchmark: Optional[pd.Series] = None,
                                       dashboard_type: str = "portfolio_analysis") -> str:
        """
        Generates an interactive dashboard using the `InteractiveVisualizer`.

        This method delegates the creation of interactive Plotly figures to an
        `InteractiveVisualizer` instance based on the specified `dashboard_type`.
        The generated figure is then converted to an HTML string.

        Args:
            returns (pd.DataFrame): DataFrame of asset returns.
            assets (List[str]): List of assets to include in the dashboard.
            benchmark (Optional[pd.Series]): Optional benchmark returns series for comparison.
            dashboard_type (str): The type of interactive dashboard to generate.
                                  Supported types include "portfolio_analysis", "efficient_frontier",
                                  "risk_metrics", "correlation_matrix".

        Returns:
            str: The HTML content of the generated interactive dashboard.

        Raises:
            ValueError: If an unsupported dashboard type is provided.
        """
        fig_json_bytes = b'' # Initialize with empty bytes

        if dashboard_type == "portfolio_analysis":
            fig_json_bytes = self.interactive_visualizer.plot_interactive_portfolio_analysis(returns, assets, benchmark)
        elif dashboard_type == "efficient_frontier":
            fig_json_bytes = self.interactive_visualizer.plot_interactive_efficient_frontier(returns, assets)
        elif dashboard_type == "risk_metrics":
            fig_json_bytes = self.interactive_visualizer.plot_interactive_risk_metrics(returns, assets)
        elif dashboard_type == "correlation_matrix":
            fig_json_bytes = self.interactive_visualizer.plot_interactive_correlation_matrix(returns, assets)
        # Add other dashboard types as needed
        else:
            raise ValueError(f"Unsupported dashboard type: {dashboard_type}")

        # Convert JSON bytes to Plotly Figure object
        fig_dict = json.loads(fig_json_bytes.decode('utf-8'))
        fig = go.Figure(fig_dict)

        return pio.to_html(fig, full_html=True, include_plotlyjs='cdn')

    def generate_sector_dashboard(self, prices: pd.DataFrame, asset_info: Dict[str, Dict[str, str]]) -> bytes:
        """
        Generates a bar chart visualizing the count of assets by sector.

        Args:
            prices (pd.DataFrame): DataFrame of asset prices (used for context, but not directly in this visualization).
            asset_info (Dict[str, Dict[str, str]]): Dictionary containing information about assets,
                                                    where keys are asset tickers and values are dictionaries
                                                    that must include a 'sector' key.

        Returns:
            bytes: The generated chart as a PNG image in bytes format.
        """
        sectors = [info.get('sector', 'N/A') for info in asset_info.values()]
        sector_counts = pd.Series(sectors).value_counts()

        fig = go.Figure(data=[go.Bar(x=sector_counts.index, y=sector_counts.values)])
        fig.update_layout(title_text="Asset Count by Sector")

        return pio.to_image(fig, format="png")

# Example Usage (for testing purposes, will be removed or modified for FastAPI integration)
# This block demonstrates how to use the DashboardGenerator class independently.
# It generates sample data and creates both static HTML and interactive dashboards.
if __name__ == '__main__':
    # Sample Data Generation (replace with actual analysis results)
    dates = pd.date_range(start='2020-01-01', periods=100)
    performance_data_sample = pd.DataFrame({
        'Portfolio A': (1 + 0.01 * pd.Series(range(100)).cumsum() / 100).cumprod(),
        'Portfolio B': (1 + 0.008 * pd.Series(range(100)).cumsum() / 100).cumprod()
    }, index=dates)

    risk_return_data_sample = pd.DataFrame({
        'Portfolio': ['Portfolio A', 'Portfolio B', 'Portfolio C'],
        'Risk': [0.15, 0.10, 0.20],
        'Return': [0.12, 0.08, 0.18],
        'Sharpe Ratio': [0.8, 0.8, 0.9]
    })

    allocation_data_sample = {'AAPL': 0.3, 'GOOG': 0.2, 'MSFT': 0.25, 'AMZN': 0.25}

    drawdown_data_sample = pd.DataFrame({
        'Drawdown': -pd.Series([0.0, 0.01, 0.05, 0.02, 0.08, 0.03, 0.0, 0.04, 0.06, 0.01] * 10).cumsum()
    }, index=dates)

    # Instantiate and generate a single dashboard
    generator = DashboardGenerator()
    html_dashboard = generator.generate_portfolio_dashboard_html(
        performance_data_sample,
        risk_return_data_sample,
        allocation_data_sample,
        drawdown_data_sample,
        "my_portfolio_dashboard_html"
    )

    # Save to a file to view
    with open("my_portfolio_dashboard.html", "w") as f:
        f.write(html_dashboard)
    print("HTML Dashboard generated at my_portfolio_dashboard.html")

    # Example of using interactive visualizer
    sample_returns = pd.DataFrame(np.random.rand(100, 3) - 0.5, columns=['Asset1', 'Asset2', 'Asset3'], index=dates)
    interactive_html = generator.generate_interactive_dashboard(sample_returns, ['Asset1', 'Asset2'], dashboard_type="portfolio_analysis")
    with open("interactive_portfolio_dashboard.html", "w") as f:
        f.write(interactive_html)
    print("Interactive HTML Dashboard generated at interactive_portfolio_dashboard.html")
