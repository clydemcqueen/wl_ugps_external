#!/usr/bin/env python3

"""
Listen to a UDP port for NMEA 0183 GGA and HDM sentences and call /api/v1/external/master on the G2 topside box.
"""

import argparse
import socket
import threading
import time

import pynmea2
from loguru import logger

from ugps_connection import UgpsConnection


class TopsidePosition:
    """
    Current topside position
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.gps_received = False
        self.hdm_received = False

        # Fields required to call /api/v/external/master
        self.cog = 0
        self.fix_quality = 0
        self.hdop = 0
        self.lat = 0
        self.lon = 0
        self.numsats = 0
        self.orientation = 0
        self.sog = 0

    def recv_sentence(self, data):
        sentence = pynmea2.parse(data.decode())
        if sentence.sentence_type == 'GGA':
            self.recv_gga(sentence)
        elif sentence.sentence_type == 'HDM':
            self.recv_hdm(sentence)
        else:
            logger.debug(f'ignoring {sentence}')

    def recv_gga(self, sentence):
        with self.lock:
            if not self.gps_received:
                logger.info(f'got GGA: {sentence.data}')
                self.gps_received = True

            self.fix_quality = sentence.data[5]
            self.hdop = sentence.data[7]
            self.lat = sentence.latitude
            self.lon = sentence.longitude
            self.numsats = sentence.data[6]

    def recv_hdm(self, sentence):
        with self.lock:
            if not self.hdm_received:
                logger.info(f'got HDM: {sentence.data}')
                self.hdm_received = True

            self.orientation = float(sentence.data[0])

    def get_json(self) -> dict | None:
        with self.lock:
            if self.gps_received and self.hdm_received:
                return {
                    'cog': self.cog,
                    'fix_quality': self.fix_quality,
                    'hdop': self.hdop,
                    'lat': self.lat,
                    'lon': self.lon,
                    'numsats': self.numsats,
                    'orientation': self.orientation,
                    'sog': self.sog,
                }
            else:
                return None


class SocketThread(threading.Thread):
    """
    UDP listener
    """

    def __init__(self, sock, ip: str, port: int, topside_position: TopsidePosition):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.topside_position = topside_position

    def run(self):
        # Set timeout, this makes it easy to handle Ctrl-C
        self.sock.settimeout(0.1)

        # Bind to ip:port
        self.sock.bind((self.ip, self.port))

        logger.info(f'Listening for NMEA messages on {self.ip}:{self.port}')

        while True:
            try:
                data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
                self.topside_position.recv_sentence(data)

            except socket.timeout:
                continue

            except socket.error:
                logger.debug('Socket closed, quitting')
                break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--udp_ip', type=str, default='127.0.0.1', help='listen on this IP address')
    parser.add_argument('--udp_port', type=int, default='27000', help='listen on this port')
    parser.add_argument('--g2_url', type=str, default='https://demo.waterlinked.com', help='G2 url')
    parser.add_argument('--rate', type=float, default='2.0', help='sent to G2 at this rate')
    parser.add_argument('--log', action="store_true", help="save output in a log")
    args = parser.parse_args()

    if args.log:
        logger.add("log_{time}.txt")

    period = 1.0 / args.rate

    # Keep track of the boat's position
    topside_position = TopsidePosition()

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # The GGA and HDM messages may arrive from different sensors at different rates.
    # Run the UDP listener on a separate thread so that we can call the G2 API at a consistent rate.
    sock_thread = SocketThread(sock, args.udp_ip, args.udp_port, topside_position)
    sock_thread.start()

    # Run until interrupted
    try:
        # Get connection to the G2 topside box
        ugps = UgpsConnection(host=args.g2_url)
        ugps.wait_for_connection()

        logger.info(f'Sending external position to {args.g2_url} at {args.rate} Hz')
        logger.info('Press Ctrl-C to stop')

        while True:
            json = topside_position.get_json()
            if json is not None:
                logger.debug(json)
                ugps.send_ugps_topside_position(json)
            time.sleep(period)

    except KeyboardInterrupt:
        logger.info('Ctrl-C detected, quitting')
        sock.close()
        sock_thread.join()


if __name__ == '__main__':
    main()
