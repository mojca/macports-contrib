#! /bin/sh
""":"
exec python $0 ${1+"$@"}
"""
__doc__ = """...Tester Script for pypi2port..."""

# -*- coding: utf-8 -*-
#! /usr/bin/env python

import urllib2
#import urllib
import hashlib
import argparse
import sys
import os
import zipfile
from progressbar import *
try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')

def list_all():
    list_packages = client.list_packages()
    for package in list_packages:
        print package

def search(pkg_name):
    print "\n"
    values=client.search({'name':pkg_name})
    for value in values:
        for key in value.keys():
            print key,'-->',value[key]
        print "\n"

def data(pkg_name,pkg_versions=None):
    print "\n"
    if not pkg_versions:
        version = client.search({'name':pkg_name})[0]['version']
        values = client.release_data(pkg_name,version)
#        print values
        if values:
            for key in values.keys():
                print key,'-->',values[key]
        else:
            print "No such package found."
            print "Please specify the exact package name."
    else:
        for version in pkg_versions:
            values = client.release_data(pkg_name,version)
#            print values
            if values:
                for key in values.keys():
                    print key,'-->',values[key]
            else:
                print "No such package found."
                print "Please specify the exact package name."
    print "\n"

def fetch(pkg_name,url):
    checksum_md5 = url.split('#')[-1].split('=')[-1]
    parent_dir = './sources/'
    src_dir = parent_dir + "/"+pkg_name+"/"
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        if not os.path.exists(src_dir):
            os.makedirs(src_dir)

    file_name = src_dir + url.split('/')[-1].split('#')[0]

#    urllib.urlretrieve(url,file_name)
    u = urllib2.urlopen(url)
    f = open(file_name,'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    widgets = ['Fetching: ', Percentage(), ' ', Bar(marker=RotatingMarker(),left='[',right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=int(file_size))
    pbar.start()

    file_size_dl = 0
    block_sz = 1024
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        pbar.update(file_size_dl)

    pbar.finish()
    print
    f.close()

    checksum_md5_calc = hashlib.md5(open(file_name).read()).hexdigest()
    if str(checksum_md5_calc) == str(checksum_md5):
        print 'Successfully fetched\n'
    else:
        print 'Aborting due to inconsistency on checksums\n'
        try:
            os.remove(file_name)
        except OSError, e:
            print "Error: %s - %s." % (e.filename,e.strerror)



def fetch_egg(url):
    checksum_md5 = url.split('#')[-1].split('=')[-1]
    parent_dir = './sources/'
    pkg_name = url.split('/')[-2]
    src_dir = parent_dir +pkg_name+"/"
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        if not os.path.exists(src_dir):
            os.makedirs(src_dir)

    file_name = src_dir + url.split('/')[-1].split('#')[0]
    print file_name


    u = urllib2.urlopen(url)
    f = open(file_name,'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    widgets = ['Fetching: ', Percentage(), ' ', Bar(marker=RotatingMarker(),left='[',right=']'), ' ', ETA(), ' ', FileTransferSpeed()]
    pbar = ProgressBar(widgets=widgets, maxval=int(file_size))
    pbar.start()

    file_size_dl = 0
    block_sz = 1024
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        pbar.update(file_size_dl)

    pbar.finish()
    print
    f.close()

    checksum_md5_calc = hashlib.md5(open(file_name).read()).hexdigest()
    if str(checksum_md5_calc) == str(checksum_md5):
        print 'Successfully fetched\n'
        zip = zipfile.ZipFile(file_name)
        for name in zip.namelist():
            if name.split("/")[0] == "EGG-INFO":
                print name
                zip.extract(name,src_dir)

    else:
        print 'Aborting due to inconsistency on checksums\n'
        try:
            os.remove(file_name)
        except OSError, e:
            print "Error: %s - %s." % (e.filename,e.strerror)

    return



def main():
    parser = argparse.ArgumentParser(description='pip2port tester script.')

    parser.add_argument('package_name', 
                       metavar='package_name', type=str, nargs='?', 
                       help='Package_Name')
#    parser.add_argument('package_version', 
#                       metavar='package_version', type=str, nargs='*', 
#                       help='Package_Version(s)')
    parser.add_argument('package_url', 
                       metavar='package_url', type=str, nargs='?', 
                       help='Package_Url')
    parser.add_argument('-l', '--list_packages', action='store_const', 
                       dest='action', const='list_packages', required=False,
                       help='List all packages')
    parser.add_argument('-s', '--search', action='store_const',
                       dest='action', const='search', required=False,
                       help='Search for a package by <package_name>')
    parser.add_argument('-d', '--data', action='store_const',
                       dest='action', const='data', required=False,
                       help='Releases data for a package by <package_name>')
    parser.add_argument('-f', '--fetch', action='store_const',
                       dest='action', const='fetch', required=False,
                       help='Fetches distfile for a package by <package_url>')
    parser.add_argument('-fe', '--fetch_egg', action='store_const',
                       dest='action', const='fetch_egg', required=False,
                       help='Fetches distfile for a package by <package_url>')
    

    options=parser.parse_args()
#    print options

    if options.action == 'list_packages':
        list_all()
        return

    if options.action == 'search':
        if options.package_name == None:
            parser.error("No package name specified")
        else:
            search(options.package_name)
        return

    if options.action == 'data':
        if options.package_name == None:
            parser.error("No package name specified")
        else:
#            if options.package_version == None:
#                data(options.package_name)
#            else:
#                data(options.package_name,options.package_version)
             data(options.package_name)
        return

    if options.action == 'fetch':
#        print options,"\n"
        if options.package_name == None:
            if options.package_url == None:
                parser.error("No package name and url specified")
            else:
                parser.error("No package name specified")
        elif options.package_url == None:
            parser.error("No url specified")
        else:
#            print options
            fetch(options.package_name,options.package_url)
        return

    if options.action == 'fetch_egg':
#        print options,"\n"
        if options.package_name == None:
            parser.error("No <package>.egg url specified")
        else:
#            print options
            fetch_egg(options.package_name)
        return
    else:
        parser.print_help()
        parser.error("No input specified")


if __name__ == "__main__":
    main()