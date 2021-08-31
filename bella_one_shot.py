#!/usr/bin/env python3

"""
This script archives one day's data on Google Drive
For example, to archive the data generated on 2021-04-06 on GDrive, run:
bella_one_shot.py 2021 4 6
"""

import logging
import argparse
import sys
from shutil import make_archive
import subprocess
import os
import os.path
import datetime

def archive_to_gdrive(mount, root_dir, base_dir, gdrive):
    # zip file will be temporarily stored in /data
    base = '/data/' + base_dir
    zip_file = base + '.zip'

    # src_dir is where raw data is located, something like /bella/pw/Y2021/04-Apr/21_0406
    src_dir = mount + root_dir + '/' + base_dir

    # check if there is raw data in src_dir
    if not os.path.isdir(src_dir):
        logging.info('Source directory {} does not exist'.format(src_dir))
        return

    if len(os.listdir(src_dir)) == 0:
        logging.info('There is no data in the source directory {}'.format(src_dir))
        return

    logging.info("Archive data in " + src_dir)
    root_dir2 = mount + root_dir
    make_archive(base, 'zip', root_dir=root_dir2, base_dir=base_dir)

    # dest_path is something like bellapw:data/Y021/04-Apr
    dest_path = '{}/{}'.format(gdrive, root_dir)

    # make the path on Google Drive if it doesn't already exist
    sub = subprocess.run(['/usr/bin/rclone', 'mkdir', dest_path])

    # upload the zip file to Google Drive
    logging.info("Upload the zip file to Google Drive at {}".format(dest_path))
    sub = subprocess.run(['/usr/bin/rclone', 'copy', zip_file, dest_path])
    if sub.returncode != 0:
        logging.error("Failed to upload the zip file to Google Drive")

    # check if the files in the source and destination match
    logging.info("Check if the files in the source and destination match")
    sub = subprocess.run(['/usr/bin/rclone', 'check', '--size-only', zip_file, dest_path])
    if sub.returncode == 0:
        logging.info("Files in the source and destination match do match!")
        # delete the temporary zip file
        os.remove(zip_file)
    else:
        logging.error("Files in the source and destination match do not match!")

def date_to_dirs(date=datetime.date.today):
    """Convert a date to root_dir & base_dir"""
    
    mon = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') 
    # root_dir is something like Y2021/04-Apr (Yyyyy/mm-Mon)
    root_dir = 'Y{:04d}/{:02d}-{}'.format(date.year, date.month, mon[date.month-1])
    # base_dir is something like 21_0406 (yy_mmdd)
    base_dir = '{:02d}_{:02d}{:02d}'.format(date.year - 2000, date.month, date.day)
    return root_dir, base_dir

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    conf = [{'mount': '/bella/pw/', 
             'dirs': ['', 'p2/', 'PWlaserData/'],
             'gdrive': 'bellapw:data'},
            {'mount': '/bella/htw/',
             'dirs': ['Undulator/', 'Thomson/', 'TestStand/', 
                      'LaserUpstairs/', 'kHzLPA/'],
             'gdrive': 'bellahtw:data'}]

    parser = argparse.ArgumentParser(
                 description='example: bella_one_shot.py 2021 4 6')
    parser.add_argument('y', type=int, help='year')
    parser.add_argument('m', type=int, help='month')
    parser.add_argument('d', type=int, help='day')

    args = parser.parse_args()
    year = args.y
    month = args.m
    day = args.d
    date = datetime.date(year, month, day)

    root_dir, base_dir = date_to_dirs(date)
    for c in conf:
        if os.path.ismount(c['mount']):
            for d in c['dirs']: 
                root_dir2 = d + root_dir
                archive_to_gdrive(c['mount'], root_dir2, base_dir, c['gdrive'])
        else:
            logging.error('NetApp is not mounted at {}!'.format(c['mount']))
    
