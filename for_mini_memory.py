import argparse
import collections
import datetime
import glob
import linecache
import matplotlib
import os
import shutil
import sys

import apache_log_parser
import pandas as pd
from tqdm import tqdm

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def day_checker(date):
    try:
        return datetime.datetime.strptime(date, '%Y/%m/%d')
    except ValueError:
        print("Please input correct date format")
        print("Correct format is YYYY/MM/dd, like {}".format(
            datetime.datetime.now().strftime("%Y/%m/%d")))
        sys.exit()


def write_csv(name, save_dict, mode):
    with open("tmp/" + name, 'w') as f:
        f.write("{},# access\n".format(mode))
        for key in save_dict.keys():
            f.write("%s,%s\n" % (key, save_dict[key]))


def updater(items, index_list, mode, _min_dex):
    index_list[_min_dex] += 1
    str_ = linecache.getline('tmp/{}_{}.csv'.format(
        mode, _min_dex), index_list[_min_dex]).split(",")
    if len(str_) > 1:
        items.insert(_min_dex, [str_[0], int(str_[1][:-1])])
    else:
        items.insert(_min_dex, ["ZfjQZUKMLumYjNQVrLJUSkrxkwAEiy", int(0)])


def merge_csv(csv_num, mode):
    index_list = [2 for i in range(csv_num+1)]
    items = []
    for i in range(csv_num):
        str_ = linecache.getline(
            'tmp/{}_{}.csv'.format(mode, i), index_list[i]).split(",")
        if len(str_) > 1:
            items.append([str_[0], int(str_[1][:-1])])

    with open("result_{}.csv".format(mode), 'w') as f:
        f.write("{},# access\n".format(mode))
        while len(items) != items.count(["ZfjQZUKMLumYjNQVrLJUSkrxkwAEiy", int(0)]):
            _min = min(items)
            _min_dex = items.index(_min)
            _min_item = items.pop(_min_dex)
            if len(items) == 0:
                f.write("%s,%s\n" % (_min_item[0], _min_item[1]))
                updater(items, index_list, mode, _min_dex)
                print(items)
                continue
            _min2 = min(items)
            _min_dex2 = items.index(_min2)
            if _min[0] == _min2[0]:
                items[_min_dex2][1] += _min_item[1]
                updater(items, index_list, mode, _min_dex)
            else:
                f.write("%s,%s\n" % (_min_item[0], _min_item[1]))
                updater(items, index_list, mode, _min_dex)


def make_mini_csv(log_line_data, date_first, date_end, rep):
    l_time = sorted([d.get('time_received_datetimeobj').replace(minute=0, second=0, microsecond=0)
                     for d in log_line_data if date_first <= d.get('time_received_datetimeobj') and d.get('time_received_datetimeobj') <= date_end])
    c_time = collections.Counter(l_time)
    l_host = sorted([d.get('remote_host') for d in log_line_data if date_first <= d.get(
        'time_received_datetimeobj') and d.get('time_received_datetimeobj') <= date_end])
    c_host = collections.Counter(l_host)
    write_csv("time_{}.csv".format(rep), c_time, "time")
    write_csv("host_{}.csv".format(rep), c_host, "host")


def main():
    parser = argparse.ArgumentParser(description='Appach log profiler')

    parser.add_argument('--file', '-f', action='append',
                        help="Input log file path")
    parser.add_argument('--directory', '-d', action='append',
                        help="Input directory path in log files")
    parser.add_argument('--start', default='1976/03/25',
                        help="Input the first day of the period you want to profile")
    parser.add_argument('--end', default='2020/06/26',
                        help="Input the last day of the period you want to profile")

    args = parser.parse_args()
    # firstとlastの指定があっているかのエラー
    date_first = day_checker(args.start)
    date_end = day_checker(args.end)
    line_parser = apache_log_parser.make_parser(
        "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"")
    rep = 0
    os.makedirs("tmp", exist_ok=True)
    if args.file is not None:
        for file_path in args.file:
            with open(file_path) as f:
                log = f.readlines()
            log_line_data = []
            for i in log:
                log_line_data.append(line_parser(i))
            make_mini_csv(log_line_data, date_first, date_end, rep)
            rep += 1

    if args.directory is not None:
        for dir_path in args.directory:
            for file_path in tqdm(glob.glob(dir_path + "*"), desc='file loading...'):
                with open(file_path) as f:
                    log = f.readlines()
                log_line_data = []
                for i in log:
                    log_line_data.append(line_parser(i))
                make_mini_csv(log_line_data, date_first, date_end, rep)
                rep += 1

    merge_csv(rep, "time")
    merge_csv(rep, "host")
    shutil.rmtree('tmp')

    df_sorted = pd.read_csv('result_host.csv').sort_values(
        '# access', ascending=False)
    print(df_sorted.to_string(index=False))
    df_sorted = pd.read_csv('result_time.csv').sort_values(
        '# access', ascending=False).set_index("time").head(10)
    df_sorted.plot.bar(y="# access", figsize=(len(df_sorted)*2, 7))
    plt.xticks(rotation=0)
    plt.savefig('top10_time.png')


if __name__ == '__main__':
    main()
