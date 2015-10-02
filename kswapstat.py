import copy
import signal
import sys
import time


SLEEP_INTERVAL = 2
KEYS = [
    'pgscan_kswapd_dma',
    'pgscan_kswapd_dma32',
    'pgscan_kswapd_normal',
    'pgscan_kswapd_movable',
    'kswapd_steal',
    'kswapd_inodesteal',
    'kswapd_low_wmark_hit_quickly',
    'kswapd_high_wmark_hit_quickly',
    'kswapd_skip_congestion_wait'
]


_done = False


def sig_handler(num, frame):
    global _done
    if num == signal.SIGINT:
        _done = True


def print_ln(data):
    for i, k in enumerate(sorted(KEYS)):
        print ('%%-%ds' % (len(k))) % (data[i]),
    print


def main():
    interval = SLEEP_INTERVAL
    if len(sys.argv) > 1:
        interval = int(sys.argv[-1])

    signal.signal(signal.SIGINT, sig_handler)

    last_run_time = None
    last_run_data = None

    print_ln(sorted(KEYS))

    while not _done:
        data = {k: int(v) for k, v in
                    [l.strip().split(' ', 1) for l in
                        filter(lambda l: len(l.strip()) > 0 and l.strip().split()[0] in KEYS,
                                open('/proc/vmstat').readlines())]}

        now = time.time()
        if last_run_data is not None:
            rates = {k: (data[k] - last_run_data[k]) / (now - last_run_time)
                     for k in data}
            print_ln(['%d/s' % (rates[k]) for k in sorted(KEYS)])

        last_run_data = data
        last_run_time = now
        time.sleep(interval)


if __name__ == '__main__':
    sys.exit(main())
