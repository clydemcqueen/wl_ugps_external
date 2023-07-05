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

## Testing with the software emulator

Run the [NMEA emulator](nmea_emulator.py) in terminal 1:
~~~
$ python3 nmea_emulator.py 
Sending packets to 127.0.0.1:10110
Press Ctrl-C to stop
Sending "$GPGGA,150948.49,4736.4547,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*6E" and "$GPHDM,105.3,M*32"
Sending "$GPGGA,150949.49,4736.4548,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*60" and "$GPHDM,105.3,M*32"
Sending "$GPGGA,150950.49,4736.4550,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*61" and "$GPHDM,105.3,M*32"
Sending "$GPGGA,150951.49,4736.4551,N,12220.6343,W,1,14,3.1,0.0,M,,M,,*61" and "$GPHDM,105.3,M*32"
...
~~~

Run the [injector](nmea_injector.py) in terminal 2:
~~~
$ python3 nmea_injector.py --log
2023-06-19 08:13:42.673 | INFO     | ugps_connection:wait_for_connection:41 - Scanning for Water Linked underwater GPS...
2023-06-19 08:13:42.674 | INFO     | __main__:run:95 - Listening for NMEA messages on 127.0.0.1:10110
2023-06-19 08:13:43.703 | INFO     | __main__:main:140 - Sending external position to https://demo.waterlinked.com at 2.0 Hz
2023-06-19 08:13:43.704 | INFO     | __main__:main:141 - Press Ctrl-C to stop
2023-06-19 08:15:10.464 | INFO     | __main__:recv_gga:46 - got GGA: ['151510.46', '4736.4547', 'N', '12220.6343', 'W', '1', '14', '3.1', '0.0', 'M', '', 'M', '', '']
2023-06-19 08:15:10.464 | INFO     | __main__:recv_hdm:58 - got HDM: ['105.3', 'M']
2023-06-19 08:15:10.819 | DEBUG    | __main__:main:146 - {'cog': 0, 'fix_quality': '1', 'hdop': '3.1', 'lat': 47.607578333333336, 'lon': -122.343905, 'numsats': '14', 'orientation': 105.3, 'sog': 0}
2023-06-19 08:15:10.819 | DEBUG    | ugps_connection:put:22 - Request url: https://demo.waterlinked.com/api/v1/external/master json: {'cog': 0, 'fix_quality': '1', 'hdop': '3.1', 'lat': 47.607578333333336, 'lon': -122.343905, 'numsats': '14', 'orientation': 105.3, 'sog': 0}
...
~~~

## Test results: add a YDEN gateway to a NMEA 2000 network

A team from the Seattle Aquarium successfully tested the injector on a vessel with an NMEA 2000 network and a YDEN Ethernet gateway.

These were the messages that we saw on the network:
~~~
$ message_summary.py *.txt
Processing 18 files
-------------------
log_2023-06-26_09-28-51_799743.txt
2129 sentences received in 109 seconds
Type    Count     Hz  Description
$YDDBS    109   1.00  Depth below surface
$YDDBT    109   1.00  Depth below transducer
$YDDPT    217   1.99  Depth of water
$YDGGA      0   0.00  Global positioning system fix data
$YDGLL    109   1.00  Geographic position lat/lon
$YDGRS     67   0.61  GPS range residuals
$YDGSA    108   0.99  GPS DOP and active satellites
$YDGSV    324   2.97  Satellites in view
$YDHDG    217   1.99  Heading, deviation and variation
$YDHDM      0   0.00  Heading, magnetic
$YDHDT    109   1.00  Heading, true
$YDMDA    108   0.99  Meteorological composite
$YDMTW    109   1.00  Mean temperature of water
$YDRMC    109   1.00  Recommended minimum navigation information
$YDROT    109   1.00  Rate of turn
$YDVTG    217   1.99  Track made good and ground speed
$YDZDA    108   0.99  Time and date
...
~~~

The injector sent the heading and GPS position to the G2 box at 1Hz.

We used a [logging tool](https://github.com/clydemcqueen/ardusub_log_tools/blob/main/wl_ugps_logger.py) to poll and log
the position of the G2 box and the U1, and used a [mapping tool](https://github.com/clydemcqueen/ardusub_log_tools/blob/main/wl_ugps_process.py)
to build maps of the results.

### Caveats

* The G2 box still needs a GPS fix to synchronize clocks

### Open questions / future work

* How fast can we call /api/v/external/master? Can we inject external readings at 20Hz?
* The APIs position/acoustic/raw and position/acoustic/filtered returned identical results. Why?
* We'd like to move this to a BlueOS extension, or add it to the [existing WL UGPS extension](https://github.com/waterlinked/blueos-ugps-extension/issues/2)