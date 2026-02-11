from logger_config import logger
from datetime import datetime
import threading
from scapy.layers.inet import IP, TCP, UDP
import pandas as pd

class PacketProcessor:
    """
    Process and analye network packets
    """
    def __init__(self):
        self.protocol_map = {
            1: "ICMP",
            6: "TCP",
            17: "UDP"
        }

        self.packet_data = []
        self.start_time = datetime.now()
        self.packet_count = 0
        self.lock = threading.Lock()

    def get_protocol_name(self, protocol_num: int) -> str:
        """
        Convert protocol number to name

        Looks in protocol map and returns name based on protocol number
        """
        return self.protocol_map.get(protocol_num, f'OTHER({protocol_num})')
    
    def process_packet(self, packet) -> None:
        """
        Process a single packet and extract relevant information
        
        """

        try:
            if IP in packet:
                with self.lock:
                    packet_info = {
                        'timestamp': datetime.now(),
                        'source': packet[IP].src,
                        'destination': packet[IP].dst,
                        'protocol': self.get_protocol_name(packet[IP].proto),
                        'size': len(packet),
                        'time_relative': (datetime.now() - self.start_time).total_seconds()
                    }

                    # Adding TCP-specific information
                    if TCP in packet:
                        packet_info.update({
                            'src_port': packet[TCP].sport,
                            'dst_port': packet[TCP].dport,
                            'tcp_flags': str(packet[TCP].flags)
                        })
                    # Adding UDP-specific information
                    elif UDP in packet:
                        packet_info.update({
                            'src_port': packet[UDP].sport,
                            'dst_port': packet[UDP].dport,
                        })

                    self.packet_data.append(packet_info)
                    self.packet_count += 1

                    # Maintaining only last 10000 packets to prevent memory issues
                    if len(self.packet_data) > 10000:
                        self.packet_data.pop(0)

        except Exception as e:
            logger.error(f"Error processing packet: {str(e)}")

    def get_dataframe(self) -> pd.DataFrame:
        """
        Converting processed packet data to pandas dataframe
        """
        with self.lock:
            return pd.DataFrame(self.packet_data)


