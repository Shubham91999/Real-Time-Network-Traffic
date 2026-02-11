import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scapy.all import sniff, Packet
from collections import defaultdict
from typing import Dict, List, Optional
import socket
import threading
import time

from logger_config import logger
from packet_processor import PacketProcessor
from visualizations import create_visualizations


def start_packet_capture() -> Optional[PacketProcessor]:
    """
    Start packet capture in a separate thread
    """
    processor = PacketProcessor()

    def capture_packets():
        sniff(prn=processor.process_packet, store=False)

    capture_thread = threading.Thread(target=capture_packets, daemon=True)
    capture_thread.start()

    return processor

def main():
    """
    main function to start the packet capture thread and display streamlit dashboard
    """

    # Basic streamlit config
    st.set_page_config(page_title="Network Traffic Analysis", layout="wide")
    st.title("Real-time Network Traffic Analysis")

    # Intialize packet processor in session state 
    if 'processor' not in st.session_state:
        st.session_state.processor = start_packet_capture()
        st.session_state.start_time = time.time()

    # Dashboard layout
    col1, col2 = st.columns(2)

    # Fetching current data
    processor = st.session_state.get('processor', None)
    if processor is not None:
        df = processor.get_dataframe()
    else:
        st.warning("Packet processor is not initialized.")
        df = pd.DataFrame()
    
    # Display metrics
    with col1:
        st.metric("Total Packets", len(df))
    with col2:
        duration = time.time() - st.session_state.start_time
        st.metric("Capture Duration", f"{duration:.2f}s")

    # Debug: Show DataFrame in Streamlit
    st.write("Current DataFrame:", df)

    # Call create_visualizations function to display charts
    create_visualizations(df)

    # Display recent packets
    st.subheader("Recent Packets")
    if len(df) > 0:
        st.dataframe(
            df.tail(10)[['timestamp', 'source', 'destination', 'protocol', 'size']],
            use_container_width=True
        )

    # Add refresh button
    if st.button('Refresh Data'):
        st.rerun()

    # Auto refresh
    time.sleep(2)
    st.rerun()


if __name__ == '__main__':
    main()

