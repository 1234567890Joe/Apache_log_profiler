import argparse
import collections
import datetime
import glob
import sys

import apache_log_parser
from tqdm import tqdm


def day_checker(date):
    try:
        return datetime.datetime.strptime(date, '%Y/%m/%d')
    except ValueError:
        print("Please input correct date format")
        print("Correct format is YYYY/MM/dd, like {}".format(
            datetime.datetime.now().strftime("%Y/%m/%d")))
        sys.exit()


def write_csv(name, save_dict):
    with open(name, 'w') as f:
        f.write("time,# access\n")

        for key in save_dict.keys():
            f.write("%s,%s\n" % (key, save_dict[key]))
    print("save csv!")


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
    parser.add_argument('--output_name', default='time_result.csv',
                        help="Input output file name")

    args = parser.parse_args()
    # firstとlastの指定があっているかのエラー
    date_first = day_checker(args.start)
    date_end = day_checker(args.end)
    log_line_data = []
    line_parser = apache_log_parser.make_parser(
        "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"")
    if args.file is not None:
        for file_path in args.file:
            with open(file_path) as f:
                log = f.readlines()
            for i in log:
                log_line_data.append(line_parser(i))
    if args.directory is not None:
        for dir_path in args.directory:
            for file_path in tqdm(glob.glob(dir_path + "*"), desc='file loading...'):
                with open(file_path) as f:
                    log = f.readlines()
                for i in log:
                    log_line_data.append(line_parser(i))
    l_time = sorted([d.get('time_received_datetimeobj').replace(minute=0, second=0, microsecond=0)
                     for d in log_line_data if date_first <= d.get('time_received_datetimeobj') and d.get('time_received_datetimeobj') <= date_end])
    c_time = collections.Counter(l_time)
    l_host = sorted([d.get('remote_host') for d in log_line_data if date_first <= d.get(
        'time_received_datetimeobj') and d.get('time_received_datetimeobj') <= date_end])
    c_host = collections.Counter(l_host)
    write_csv(args.output_name, c_time)
    for host, count in c_host.most_common():
        print("ホスト名:{}, アクセス回数:{}".format(host, count))


if __name__ == '__main__':
    main()
