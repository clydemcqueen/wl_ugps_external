# Waterlinked UGPS External Position and Heading Bridge

Provide external (vessel) position and heading information to the
[Waterlinked Underwater GPS G2 system](https://waterlinked.com/underwater-gps-g2).

## Typical Configuration

The vessel must have a sensors that will generate NMEA 2000 position and heading messages.

Add a [NMEA 2000 Ethernet Gateway](https://yachtdevicesus.com/products/nmea-2000-ethernet-gateway-yden-02) to the vessel's network.
* Configure it to have a static IP address on the 192.168.2.X subnet
* Configure it to forward GGA and HDM sentences to the topside computer via UDP

Configure the G2 to use an external position.

Run the [nmea_injector](nmea_injector.py) script on the topside computer.

## Testing

Run the NMEA emulator in terminal 1:
~~~
$ python3 nmea_emulator.py 
Sending packets to 127.0.0.1:27000
Press Ctrl-C to stop
Sending "$GPGGA,150948.49,4736.4547,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*6E" and "$GPHDM,105.3,M*32"
Sending "$GPGGA,150949.49,4736.4548,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*60" and "$GPHDM,105.3,M*32"
Sending "$GPGGA,150950.49,4736.4550,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*61" and "$GPHDM,105.3,M*32"
Sending "$GPGGA,150951.49,4736.4551,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*61" and "$GPHDM,105.3,M*32"
...
~~~

Run the injector in terminal 2:
~~~
$ python3 nmea_injector.py
2023-06-19 08:13:42.673 | INFO     | ugps_connection:wait_for_connection:41 - Scanning for Water Linked underwater GPS...
2023-06-19 08:13:42.674 | INFO     | __main__:run:95 - Listening for NMEA messages on 127.0.0.1:27000
2023-06-19 08:13:43.703 | INFO     | __main__:main:140 - Sending external position to https://demo.waterlinked.com at 2.0 Hz
2023-06-19 08:13:43.704 | INFO     | __main__:main:141 - Press Ctrl-C to stop
2023-06-19 08:15:10.464 | INFO     | __main__:recv_gga:46 - got GGA: ['151510.46', '4736.4547', 'N', '12220.6343', 'W', '1', '14', '3.1', '0.0', 'M', '', 'M', '', '']
2023-06-19 08:15:10.464 | INFO     | __main__:recv_hdm:58 - got HDM: ['105.3', 'M']
2023-06-19 08:15:10.819 | DEBUG    | __main__:main:146 - {'cog': 0, 'fix_quality': '1', 'hdop': '3.1', 'lat': 47.607578333333336, 'lon': -122.343905, 'numsats': '14', 'orientation': 105.3, 'sog': 0}
2023-06-19 08:15:10.819 | DEBUG    | ugps_connection:put:22 - Request url: https://demo.waterlinked.com/api/v1/external/master json: {'cog': 0, 'fix_quality': '1', 'hdop': '3.1', 'lat': 47.607578333333336, 'lon': -122.343905, 'numsats': '14', 'orientation': 105.3, 'sog': 0}
...
~~~

Note that the https://demo.waterlinked.com will reject the PUT requests, you'll need a real G2 box for a full test.