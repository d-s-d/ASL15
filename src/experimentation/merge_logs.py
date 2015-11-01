import gzip
import sys
import argparse
import log_stream
from datetime import date, time, datetime, timedelta

REG_TRACE = {
    'client': '^ASLClient.+trace.+\.gz$',
    'middleware': '^ASLMW.+trace.+\.gz'
}

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('command', type=str, help='command')
    argparser.add_argument('source_dir', type=str, help='source directory')
    argparser.add_argument('typ', type=str, help='')
    argparser.add_argument('-bs', '--bucket-size', type=int, help='bucket size in ms (default: 5000 ms)')
    argparser.add_argument("--readable-time", help='output time in humand readable format (instead of ms)')
    args = argparser.parse_args()
    stream = log_stream.log_data(args.source_dir, REG_TRACE[args.typ])

    BUCKET_SIZE = 5000
    if args.bucket_size:
        BUCKET_SIZE = args.bucket_size

    def command_calc_tp_rt():
        cur_item = stream.next()
        cur_thresh = cur_item[0] + BUCKET_SIZE
        rt_sum = cur_item[1]
        count = 0
        t = datetime.combine(date.today(), time(hour=0, minute=0))
        for item in stream:
            count += 1
            rt_sum += item[1]
            if item[0] > cur_thresh:
                t += timedelta(milliseconds=BUCKET_SIZE)
                cur_thresh = item[0] + BUCKET_SIZE
                thput = float(count) / (BUCKET_SIZE/1000)
                if args.readable_time:
                    print t.time(), thput, float(rt_sum) / (count)
                else:
                    print cur_thresh, thput, float(rt_sum) / (count)
                count = 0
                rt_sum = 0

    locals()['command_'+args.command]()

if __name__=="__main__":
    main()
