#!/usr/bin/env python3

import logging
import datetime
import os
import os.path
import sys
from shutil import make_archive
import subprocess

logging.basicConfig(filename='/tmp/bella.log', level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s')
today = datetime.date.today()
# yesterday = today - datetime.timedelta(days=1)
logging.info('Today is {}'.format(today))

mon = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') 
# base_dir is something like 21_0406 (yy_mmdd)
base_dir = '{:02d}_{:02d}{:02d}'.format(today.year - 2000, today.month, today.day)
# root_dir is something like /netapp/Y2021/04-Apr (Yyyyy/mm-Mon)
root_dir = '/netapp/Y{:04d}/{:02d}-{}'.format(today.year, today.month, mon[today.month-1])
# zip file will be temporarily stored in /data
base = '/data/' + base_dir
zip_file = base + '.zip'

# src_dir is where raw data is located, something like /netapp/Y2021/04-Apr/21_0406
src_dir = root_dir + '/' + base_dir

# check if there is raw data for today
if not os.path.isdir(src_dir):
    logging.error('Source directory {} does not exist'.format(src_dir))
    logging.error('Abort!')
    sys.exit(1)

if len(os.listdir(src_dir)) == 0:
    logging.error('There is no data in the source directory {}'.format(src_dir))
    logging.error('Abort!')
    sys.exit(1)

# archive today's data
logging.info("Archive today's data")
make_archive(base, 'zip', root_dir=root_dir, base_dir=base_dir)

# dest_path is something like bella:data/Y021/04-Apr
dest_path = 'bella:data/Y{:04d}/{:02d}-{}'.format(today.year, today.month, mon[today.month-1])

# make the path on Google Drive if it doesn't already exist
logging.info("Make the path on Google Drive if it doesn't already exist")
sub = subprocess.run(['/usr/bin/rclone', 'mkdir', dest_path])

# upload the zip file to Google Drive
logging.info("Upload the zip file to Google Drive at {}".format(dest_path))
sub = subprocess.run(['/usr/bin/rclone', 'copy', zip_file, dest_path])
if sub.returncode != 0:
    logging.info("Failed to upload the zip file to Google Drive")
    logging.info('Abort!')
    sys.exit(1)

# check if the files in the source and destination match
logging.info("Check if the files in the source and destination match")
sub = subprocess.run(['/usr/bin/rclone', 'check', '--size-only', zip_file, dest_path])
if sub.returncode == 0:
    logging.info("Files in the source and destination match do match!")
    # delete the temporary zip file
    os.remove(zip_file)
else:
    logging.error("Files in the source and destination match do not match!")
    sys.exit(1)
