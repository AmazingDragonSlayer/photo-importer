#!/usr/bin/env python
# coding=utf8
import argparse, os
from glob import glob
import PIL.Image
import shutil
from datetime import datetime
import re
import hashlib
import fnmatch

# Exif Tags reference: http://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif.html

def date_file_modified(file):
    return datetime.fromtimestamp(os.path.getmtime(file))
    
def date_file_created(file):
    return datetime.fromtimestamp(os.path.getctime(file))

def parse_date(str):
    return datetime.strptime(str, '%Y:%m:%d %H:%M:%S')

def parse_date_from_name(file):
    m = re.search('([21][09]\d\d)[-_]?([01]\d)[-_]?([0123]\d)', file)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 1,1)
    return False

def get_file_lowest_date(file):
    dates = [datetime.now()]
    fd = parse_date_from_name(file)
    if fd != False:
        dates.append(fd)
    dates.append(date_file_modified(file))
    dates.append(date_file_created(file))
    dates = dates + get_exif_dates(file)
    return min(dates)

def has_exif_data(file):
    sp = os.path.splitext(file)
    fe = ['.JPG','.JPEG','.TIFF','.PNG']    
    return sp[1].upper() in fe

def get_exif_dates(file):
    result = []   
    if not has_exif_data(file):
        return result
    img = PIL.Image.open(file)
    exif_data = img._getexif()
    if exif_data:
        if 36867 in exif_data:
            result.append(parse_date(exif_data[36867]))
        if 36868 in exif_data:
            result.append(parse_date(exif_data[36868]))
    return result

def normalize_dst_path(dst):
    if dst[-1] != '/':
        dst += '/'
    return dst

def normalize_src_path(src):
    if src[-1] == '/':
        src += '*.jpg'
    return src

def get_file_md5(file, blocksize=65536):
    hash = hashlib.md5()
    with open(file, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def is_same_file(file1, file2):
    if os.path.getsize(file1) != os.path.getsize(file2):
        return False
    if get_file_md5(file1) == get_file_md5(file2):
         return True
    return False
    

parser = argparse.ArgumentParser(description='Import photos from directory to certain location and create date-based directory structure.')
parser.add_argument('-m', '--method', action='store', default='cp', choices=['cp','mv'], help='Whether to copy or move files from location.', dest='method')
parser.add_argument('-o', '--overwrite', action='store_true', help='Whether to overwrite if target image exists', dest='overwrite')
parser.add_argument('-r', '--recursive', action='store_true', help='Recursive search', dest='recursive')
parser.add_argument('src', help='Which files to process.')
parser.add_argument('dst', help='Top level directory to which files will be copied (moved). Inside it apropriate subdirectories (YYYY/MM/DD) will be created.' )
#@todo minimum file size / resolution?
#@todo maybe check if file is not elsewhere (in other possible date-based locations)
args = parser.parse_args()

if not os.path.isdir(args.dst):
    raise IOError(args.dst + " does not exists")

args.src = normalize_src_path(args.src)
args.dst = normalize_dst_path(args.dst)

files = []

if args.recursive:
    for root, dirnames, filenames in os.walk(os.path.dirname(args.src)):
        for filename in fnmatch.filter(filenames, os.path.basename(args.src)):
            files.append(os.path.join(root, filename))
else:
    files = glob(args.src)

if len(files) == 0:
    raise IOError("No files found")

action_desc = ('Copying', 'Moving')[args.method == 'mv']

for file in files:
    file_date = get_file_lowest_date(file)
    file_target_dir = args.dst + ("%s/%s/%s/" % (file_date.year, '{0:02d}'.format(file_date.month), '{0:02d}'.format(file_date.day)))
    file_target_path = file_target_dir + os.path.basename(file) 
    if not os.path.exists(file_target_dir):
        os.makedirs(file_target_dir)

    
    if os.path.exists(file_target_path):
        if is_same_file(file, file_target_path):
            if args.overwrite == False:
                print file, ' already exists... skipping'
                continue

    i_cnt = 2
    while os.path.exists(file_target_path):
        sp = os.path.splitext(file_target_path)
        file_target_path = sp[0] + "-" + str(i_cnt) + sp[1]
        
    if args.method == 'cp':
        shutil.copyfile(file, file_target_path)

    elif args.method == 'mv':
        shutil.move(file, file_target_path)

    print "%s file %s to %s" % (action_desc, file, file_target_path)
    

