import os
import re
import gzip
import heapq

REG_INIT_STAMP = re.compile("^([0-9]+):([0-9]+): .+\n")
REG_OP_STAMP = re.compile("^([0-9]+):([a-zA-Z][a-zA-Z0-9]+): ([0-9]+)\n")


def log_data(target_dir, regex):
        # walk down target_dir looking for matching files
        # initialize heap
        #

        filenames = dict()
        offsets = dict()

        def read_op_entry(f):
            line = f.readline()
            m = REG_OP_STAMP.match(line)
            if m:
                return (int(m.group(1))+offsets[f],
                    int(m.group(3)), m.group(2), filenames[f])
            return None
        
        files = list()
        reg = re.compile(regex)

        for (cwd, dnames, fnames) in os.walk(target_dir):
            for fn in filter(reg.match, fnames):
                f = gzip.open(os.path.join(cwd, fn))
                line = f.readline()
                m = REG_INIT_STAMP.match(line)
                real_offset = 0
                while m:
                    real_offset = int(m.group(2)) - int(m.group(1))
                    line = f.readline()
                    m = REG_INIT_STAMP.match(line)
                line_len = len(line)
                if line_len > 0:
                    f.seek(-line_len, os.SEEK_CUR)
                    filenames[f] = fn
                    offsets[f] = real_offset


        heap = filter(lambda x: x[0] is not None,
            map(lambda f: (read_op_entry(f), f), filenames.keys()))
        heapq.heapify(heap)
        
        oldest_item = heapq.heappop(heap)
        base_offset = oldest_item[0][0]
        heapq.heappush(heap, oldest_item)

        while True:
            try:
                (item, f) = heapq.heappop(heap)
                new_entry = (read_op_entry(f), f)
                if new_entry[0] is not None:
                    heapq.heappush(heap, new_entry)
                yield tuple([item[0]-base_offset] + list(item[1:]))
            except IndexError:
                raise StopIteration
