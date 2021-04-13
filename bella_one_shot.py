#!/usr/bin/env python3

"""
This script archives one day's data on Google Drive
For example, to archive the data generated on 2021-04-06 on GDrive, run:
bella_one_shot.py 2021 4 6
"""

import argparse
import sys
from shutil import make_archive
import subprocess
import os
import os.path

parser = argparse.ArgumentParser(
        description='example: bella_one_shot.py 2021 4 6')
parser.add_argument('y', type=int, help='year')
parser.add_argument('m', type=int, help='month')
parser.add_argument('d', type=int, help='day')

args = parser.parse_args()
year = args.y
month = args.m
day = args.d

if month > 12 or month < 1:
    sys.exit("Month must be an integer between 1 and 12")

mon = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

# base_dir is something like 21_0406 (yy_mmdd)
base_dir = '{:02d}_{:02d}{:02d}'.format(year - 2000, month, day)
# root_dir is something like /netapp/Y2021/04-Apr (Yyyyy/mm-Mon)
root_dir = '/netapp/Y{:04d}/{:02d}-{}'.format(year, month, mon[month-1])
# zip file will be temporarily stored in /data
base = '/data/' + base_dir
zip_file = base + '.zip'

# src_dir is where raw data is located, something like /netapp/Y2021/04-Apr/21_0406
src_dir = root_dir + '/' + base_dir

# check if there is raw data for that day
if not os.path.isdir(src_dir):
    sys.exit('Source directory {} does not exist'.format(src_dir))

if len(os.listdir(src_dir)) == 0:
    sys.exit('There is no data in the source directory {}'.format(src_dir))

# archive that day's data
print("Archive that day's data")
make_archive(base, 'zip', root_dir=root_dir, base_dir=base_dir)

# dest_path is something like bella:data/Y021/04-Apr
dest_path = 'bella:data/Y{:04d}/{:02d}-{}'.format(year, month, mon[month-1])

# make the path on Google Drive if it doesn't already exist
sub = subprocess.run(['/usr/bin/rclone', 'mkdir', dest_path])

# upload the zip file to Google Drive
print("Upload the zip file to Google Drive at {}".format(dest_path))
sub = subprocess.run(['/usr/bin/rclone', 'copy', zip_file, dest_path])

# check if the files in the source and destination match
sub = subprocess.run(['/usr/bin/rclone', 'check', '--size-only', zip_file, dest_path])

# delete the temporary zip file
os.remove(zip_file)
