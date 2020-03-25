#!/usr/bin/python3
import getopt, sys
import pnd
import time
import diskstats

class DeviceStat:
  __slots__ = ["read",
               "write"
              ]

  def __init__(self, read, write):
    self.read = read
    self.write = write

class DeviceRate:
  __slots__ = ["device",
               "threshold",         # threshold of read+write per second
               "previous",          # previous DeviceStat measurement
               "current",           # current  DeviceStat measurement
               "update",            # method for updating DeviceStat
              ]

  def __init__(self, device, threshold, update):
    self.device = device
    self.threshold = threshold
    self.update = update

    init_state = self.update(self.device)
    self.previous = init_state
    self.current = init_state

  def calc_rate(self, interval):
    rate =  int((self.current.read -
             self.previous.read) / interval)
    rate += int((self.current.write -
             self.previous.write) / interval)
    return rate

  def below_threshold(self, interval):
    return self.calc_rate(interval) < self.threshold

  def update_current(self):
    self.previous = self.current
    self.current = self.update(self.device)

def usage(name):
  print(name + " - Measure network and disk activity and exit all of them fall below threshold for given time frame.\n")
  print("[-i <interface>]\t Watch network interface for idleness, may be specified multiple times.")
  print("[-b <blockdev>]\t Watch block device for idleness, may be specified multiple times.")
  print("[-t <B/second>]\t Threshold of network activity in B/s (RX + TX).")
  print("[-r <B/second>]\t Threshold of disk data rate in B/s (reads + writes).")
  print("[-w <seconds>]\t Window, timeframe where amount of transferred bytes is below threshold (default: 10).")

def devstat_net(device):
  rx = 'receive'
  tx = 'transmit'
  p = pnd.ProcNetDev()[device]

  return DeviceStat(p[rx]['bytes'],
                    p[tx]['bytes'])

def devstat_blockdev(device):
  read  = 'sectors_read'
  write = 'sectors_written'
  sector_size = 512
  ds = diskstats.diskstats()
  return DeviceStat(int(ds[device][read]  * sector_size),
                    int(ds[device][write] * sector_size))

# Create DeviceRate entries for each of the provided interfaces, if they do not already exist.
def create_net_rates(interfaces, threshold, device_rates):
  for i in interfaces:
    if i not in device_rates:
      try:
        device_rates[i] = DeviceRate(
                   i,
                   threshold,
                   devstat_net)
        break
      except KeyError:
        print("Warning: interface " + i + " does not exist, not watching it")

# Create DeviceRate entries for each of the provided blockdevs, if they do not already exist.
def create_blockdev_rates(blockdevs, threshold, device_rates):
  for i in blockdevs:
    if i not in device_rates:
      try:
        device_rates[i] = DeviceRate(
                   i,
                   threshold,
                   devstat_blockdev)
        break
      except KeyError:
        print("Warning: blockdev " + i + " does not exist, not watching it")

def idle_check(name, interval, period, device_rates):
  idle = True

  for dev in device_rates:
    dr = device_rates[dev]

    dr.update_current()
    rate = dr.calc_rate(period)
    print(name + ": Average rate on device " + dev + " in the last " + str(period) + " seconds was " + str(rate) + " B/s")

    idle = idle and dr.below_threshold(period)

  if idle:
    print(name + ": All devices were below their threshold for the last period")
    return interval + 1
  else:
    return 0

def main():
  name = sys.argv[0]

  try:
    opts, args = getopt.getopt(sys.argv[1:], "i:b:t:r:w:", ["interface=", "threshold=", "window="])
  except getopt.GetoptError as err:
    print(err)
    usage(name)
    sys.exit(2)

  interfaces         = []
  blockdevs          = []
  threshold_net      = None
  threshold_blockdev = None
  window             = None

  for o, a in opts:
    if o in ("-i", "--interface") :
        interfaces.append(a)
    elif o in ("-b", "--blockdev") :
        blockdevs.append(a)
    elif o in ("-t", "--threshold"):
        threshold_net = int(a)
    elif o in ("-r", "--rate"):
        threshold_blockdev = int(a)
    elif o in ("-w", "--window"):
        window = int(a)
    else:
        assert False, "unhandled option"

  if len(interfaces) > 0 and threshold_net is None:
    print("Error: interface(s) were specified, but no threshold (-t) given!\n")
    usage(name)
    sys.exit(2)
  if len(blockdevs) > 0 and threshold_blockdev is None:
    print("Error: block device(s) were specified, but no rate (-r) given!\n")
    usage(name)
    sys.exit(2)

  # rate measuring every period seconds
  period = 10
  window = period if window is None or window < period else window

  # round up measurement intervals
  intervals = (window // period) + (window % period > 0)

  device_rates = {}

  i = 0
  while i < intervals:
    create_net_rates(interfaces, threshold_net, device_rates)
    create_blockdev_rates(blockdevs, threshold_blockdev, device_rates)

    time.sleep(period)
    i = idle_check(name, i, period, device_rates)

  print(name + ": All devices were below their threshold for " +
        str(int(intervals)) + " period(s) of " + str(period) + " seconds - exiting")

if __name__ == "__main__":
    main()
