import pandas as pd
import plotly.express as px
import streamlit as st


class VisualizationStrategy:
	def render(self, df: pd.DataFrame):
		raise NotImplementedError


class ProtocolPieChart(VisualizationStrategy):
	def render(self, df: pd.DataFrame):
		protocol_counts = df['protocol'].value_counts()
		fig = px.pie(
			values=protocol_counts.values,
			names=protocol_counts.index,
			title="Protocol Distribution"
		)
		st.plotly_chart(fig, use_container_width=True)


class PacketsTimelineChart(VisualizationStrategy):
	def render(self, df: pd.DataFrame):
		df['timestamp'] = pd.to_datetime(df['timestamp'])
		df_grouped = df.groupby(df['timestamp'].dt.floor('S')).size() # type: ignore
		fig = px.line(
			x=df_grouped.index,
			y=df_grouped.values,
			title="Packets per Second"
		)
		st.plotly_chart(fig, use_container_width=True)


class TopSourceIPsBarChart(VisualizationStrategy):
	def render(self, df: pd.DataFrame):
		top_sources = df['source'].value_counts().head(10)
		fig = px.bar(
			x=top_sources.index,
			y=top_sources.values,
			title="Top Source IP Addresses"
		)
		st.plotly_chart(fig, use_container_width=True)


def create_visualizations(df: pd.DataFrame):
	"""Create all dashboard visualizations using strategies"""
	if len(df) == 0:
		st.info("No data to visualize.")
		return

	strategies = [
		ProtocolPieChart(),
		PacketsTimelineChart(),
		TopSourceIPsBarChart(),
	]
	for strategy in strategies:
		strategy.render(df)
