# idle.py
  
Determine if a Linux system is idle, based on network and disk activity.
Combined with wakeup methods (such as Wake on LAN) this is useful to reduce power consumption of server systems.

## Goals

* minimal dependencies
* python3 compatibility

## Usage Examples

```sh

# Consider idle state when eth0 network interface had a rate under 10kB/s on average in the last 10 seconds.
$ ./python/idle.py -i eth0 -t $(expr 10 \* 1024) -w 10

# Consider idle state when eth0, eth1 network interfaces both were below 100kB/s on average in the last 40 seconds.
$ ./python/idle.py -i eth0 -i eth1 -t $(expr 100 \* 1024) -w 40

# Consider idle state when eth0 network interface on average had a rate under 10kB/s and sda had a rate under 5MB/s the last 20 seconds.
$ ./python/idle.py -i eth0 -t $(expr 10 \* 1024) -b sda -r $(expr 5 \* 1024 \* 1024) -w 100

```
*Note*: It makes sense to check idleness of block devices for longer timeframes (-w), because of OS level buffering.

# System Service

An example for using this as a (systemd) system service is provided inside the `service` directory.
Use `sudo ./service/install-service.sh` to install it. Afterwards enable the service with
`sudo systemctl daemon-reload && systemctl enable powersave-on-idle && systemctl start powersave-on-idle`.

For customizing this, have a look into `/etc/powersave-on-idle/powersave-on-idle.conf`.
*Warning*: Be conservative with those values, otherwise your system may continously go to power saving!

# Pull requests

Improvements are happily welcome - please adhere to the above goals.
