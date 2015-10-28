import gzip
import sys
import argparse
import log_stream
from datetime import date, time, datetime, timedelta

REG_TRACE = {
    'client': '^ASLClient.+.gz',
    'middleware': '^ASLMW.+.gz'
}

DELTA=5000

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('command', type=str, help='command')
    argparser.add_argument('source_dir', type=str, help='source directory')
    argparser.add_argument('typ', type=str, help='')
    args = argparser.parse_args()
    stream = log_stream.log_data(args.source_dir, REG_TRACE[args.typ])

    def command_calc_throughput_rt():
        cur_item = stream.next()
        cur_thresh = cur_item[0] + DELTA
        rt_sum = cur_item[1]
        count = 0
        t = datetime.combine(date.today(), time(hour=0, minute=0))
        for item in stream:
            count += 1
            rt_sum += item[1]
            if item[0] > cur_thresh:
                t += timedelta(milliseconds=DELTA)
                cur_thresh = item[0] + DELTA
                thput = float(count) / (DELTA/1000)
                print t.time(), thput, float(rt_sum) / (count)
                count = 0
                rt_sum = 0

    locals()['command_'+args.command]()

if __name__=="__main__":
    main()
