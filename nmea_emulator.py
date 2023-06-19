#!/usr/bin/env python3

"""
Send fake NMEA 0183 GGA and HDT sentences to a UDP port.
"""

import argparse
import socket
import time
from datetime import datetime

from nmeasim.models import TZ_LOCAL
from nmeasim.simulator import Simulator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='target IP address')
    parser.add_argument('--port', type=int, default='27000', help='target port')
    args = parser.parse_args()

    print(f'Sending packets to {args.ip}:{args.port}')
    print('Press Ctrl-C to stop')

    # Initialize NMEA simulator
    sim = Simulator()
    with sim.lock:
        # Can re-order or drop some
        sim.gps.output = ('GGA', 'HDM')
        sim.gps.num_sats = 14
        sim.gps.lat = 47.6075779801547
        sim.gps.lon = -122.34390446166833
        sim.gps.altitude = 0
        sim.gps.kph = 1.0
        sim.gps.orientation = 90.0
        sim.gps.mag_heading = 105.33
        sim.gps.date_time = datetime.now(TZ_LOCAL)  # PC current time, local time zone
        sim.gps.hdop = 3.1
        sim.gps.vdop = 5.0
        sim.gps.pdop = (sim.gps.hdop ** 2 + sim.gps.vdop ** 2) ** 0.5
        # Precision decimal points for various measurements
        sim.gps.horizontal_dp = 4
        sim.gps.vertical_dp = 1
        sim.gps.speed_dp = 1
        sim.gps.time_dp = 2
        sim.gps.angle_dp = 1
        # Heading variation affects the lat/lon, but not the compass heading
        sim.heading_variation = 10

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:

        while True:
            gga_str, hdm_str = list(sim.get_output(1))
            print(f'Sending "{gga_str}" and "{hdm_str}"')
            sock.sendto(str.encode(gga_str), (args.ip, args.port))
            sock.sendto(str.encode(hdm_str), (args.ip, args.port))
            time.sleep(1)

    except KeyboardInterrupt:
        print('Ctrl-C detected, stopping')


if __name__ == '__main__':
    main()
