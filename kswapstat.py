import copy
import signal
import sys
import time

from datetime import datetime


SLEEP_INTERVAL = 2
WIDTH = 20
# need kernel by kernel versions of this
KEYS = {
    'pgscan_kswapd_dma': {
        'short': 'scan_dma',
    },
    'pgscan_kswapd_dma32': {
        'short': 'scan_dma32',
    },
    'pgscan_kswapd_normal': {
        'short': 'scan_normal',
    },
    'pgscan_kswapd_movable': {
        'short': 'scan_movable',
    },
    'kswapd_steal': {
        'short': 'steal',
    },
    'kswapd_inodesteal': {
        'short': 'inode_steal',
    },
    'kswapd_low_wmark_hit_quickly': {
        'short': 'lwmark_hit_quickly',
    },
    'kswapd_high_wmark_hit_quickly': {
        'short': 'hwmark_hit_quickly',
    },
    'kswapd_skip_congestion_wait': {
        'short': 'skip_cong_wait',
    }
}
ALIASES = {
}

_done = False


def sig_handler(num, frame):
    global _done
    if num == signal.SIGINT:
        _done = True


def print_header():
    print ('{:<27}').format('timestamp'),
    for k in sorted(KEYS):
        _k = KEYS[k].get('short', k)
        print ('{:<' + str(max(WIDTH, len(_k))) + '}').format(_k),
    print


def print_ln(data):
    print ('{:<27}').format(datetime.utcnow().isoformat()),
    for i, k in enumerate(sorted(KEYS)):
        _k = KEYS[k].get('short', k)
        print ('{:<' + str(max(WIDTH, len(_k))) + '}').format(
                '{data[0]:.1f}/s {data[1]:d}'.format(data=data[i])),
    print


def main():
    interval = SLEEP_INTERVAL
    if len(sys.argv) > 1:
        interval = int(sys.argv[-1])

    signal.signal(signal.SIGINT, sig_handler)

    last_run_time = None
    last_run_data = None
    totals = {}
    iterations = 0

    while not _done:
        if iterations % 40 == 0:
            print_header()
        iterations += 1
        data = {ALIASES.get(k, k): int(v) for k, v in
                    [l.strip().split(' ', 1) for l in
                        filter(lambda l: len(l.strip()) > 0 and
                                         (l.strip().split()[0] in KEYS or
                                          l.strip().split()[0] in ALIASES),
                                open('/proc/vmstat').readlines())]}

        now = time.time()
        if last_run_data is not None:
            for k in data:
                if k not in totals:
                    totals[k] = 0
                totals[k] += data[k] - last_run_data[k]
            rates = {k: (data[k] - last_run_data[k]) / (now - last_run_time)
                     for k in data}
            print_ln([(rates[k] if k in rates else 'n/a', totals[k]) for k in sorted(KEYS)])

        last_run_data = data
        last_run_time = now
        time.sleep(interval)


if __name__ == '__main__':
    sys.exit(main())
