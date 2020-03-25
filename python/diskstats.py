#!/usr/bin/python3
# based on https://gist.github.com/mmalone/1081615/a37b09ce1d6ac6960742444c50f99728bffc9859
def diskstats():
    file_path = '/proc/diskstats'

    # https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats
    columns = ['major_dev_num', 'minor_dev_num', 'device', 'reads', 'reads_merged', 'sectors_read', 'ms_reading',
               'writes', 'writes_merged', 'sectors_written', 'ms_writing', 'current_ios', 'ms_doing_io',
               'weighted_ms_doing_io', 'discards_completed', 'discards_merged', 'sectors_discarded', 'ms_discarding',
               'flushes_completed', 'ms_flushing']

    result = {}
    for line in (l for l in open(file_path, 'r') if l != ''):
        parts = line.split()
        data = dict(zip(columns, parts))
        result[data['device']] = dict((k, int(v)) for k, v in data.items() if k != 'device')
    return result

if __name__ == '__main__':
    ds = diskstats()
    for device in ds:
        stats = ds[device]
        print(device)
        for name, stat in stats.items():
            print('    %s: %s' % (name.replace('_', ' '), stat))
