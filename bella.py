#!/usr/bin/env python3

import logging
import datetime
import os
import os.path
import sys
from shutil import make_archive
import subprocess
import smtplib

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
        logging.info("Files in the source and destination do match!")
        # delete the temporary zip file
        os.remove(zip_file)
        # send an email to the data owner
        send_email(root_dir, base_dir)
    else:
        logging.error("Files in the source and destination do not match!")

def send_email(root_dir, base_dir):
    sender = 'sfd@lbl.gov'
    base = root_dir.split('/')[0]

    if base[:3] == 'Y20':
        folder = 'bdna1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella PW Data'
        email = 'MarleneTurner@lbl.gov'
        first_name = 'Marlene'
    elif base == 'p2':
        folder = 'bdna1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella PW Data'
        email = 'MarleneTurner@lbl.gov'
        first_name = 'Marlene'
    elif base == 'kHzLPA':
        folder = 'vol1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella HTW Data'
        email = 'Hao.Ding@lbl.gov'
        first_name = 'Hao'
    elif base == 'LaserUpstairs':
        folder = 'vol1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella HTW Data'
        email = 'LFanChiang@lbl.gov'
        first_name = 'Liona'
    elif base == 'Magnet Test Bench':
        folder = 'vol1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella HTW Data'
        email = 'SBarber@lbl.gov'
        first_name = 'Sam'
    elif base == 'TestStand':
        folder = 'vol1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella HTW Data'
        email = 'jastackhouse@lbl.gov'
        first_name = 'Joshua'
    elif base == 'Thomson':
        folder = 'vol1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella HTW Data'
        email = 'TMOstermayr@lbl.gov'
        first_name = 'Tobias'
    elif base == 'Undulator':
        folder = 'vol1/data/' + root_dir + '/' + base_dir
        gdrive = 'Bella HTW Data'
        email = 'SBarber@lbl.gov'
        first_name = 'Sam'
    else:
        return
        
    receivers = [email, 'sfd@lbl.gov']
    message = f'''From: Shawfeng Dong <sfd@lbl.gov>
To: {email}
CC: sfd@lbl.gov
Subject: [bella] backup log

Dear {first_name},

FYI. Your data in the folder "{folder}" on the Netapp file server have been backed up to the shared Google Drive "{gdrive}".

Cheers,
Shaw
'''
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(sender, receivers, message)
    smtp.quit()

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
    log = '/tmp/bella.log'
    logging.basicConfig(filename=log, filemode='w', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    conf = [{'mount': '/bella/pw/', 
             'dirs': ['', 'p2/', 'PWlaserData/'],
             'gdrive': 'bellapw:data'},
            {'mount': '/bella/htw/',
             'dirs': ['Undulator/', 'Thomson/', 'TestStand/', 
                      'LaserUpstairs/', 'kHzLPA/', 'Magnet Test Bench/'],
             'gdrive': 'bellahtw:data'}]

    # get yesterday's date (everyday, we back up previous day's data) 
    # date = datetime.date(2021, 8, 19)
    date = datetime.date.today() - datetime.timedelta(days=1)

    root_dir, base_dir = date_to_dirs(date)
    for c in conf:
        if os.path.ismount(c['mount']):
            for d in c['dirs']: 
                root_dir2 = d + root_dir
                archive_to_gdrive(c['mount'], root_dir2, base_dir, c['gdrive'])
        else:
            logging.error('NetApp is not mounted at {}!'.format(c['mount']))
    
    # send out email notification
    # sender = 'sfd@belladata-migration.lbl.gov'
    sender = 'sfd@lbl.gov'
    receivers = ['bella-icus@lbl.gov', 'sfd@lbl.gov']

    message = """From: Shawfeng Dong <sfd@lbl.gov>
To: bella-icus@lbl.gov
CC: sfd@lbl.gov
Subject: [bella] daily archive log

"""

    with open(log) as f:
        message += f.read()
        # print(message)

    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(sender, receivers, message)
        smtp.quit()
        print("Successfully sent email")
    except smtplib.SMTPException:
        print("Error: unable to send email")
