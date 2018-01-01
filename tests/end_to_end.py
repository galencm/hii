# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import time
import os
sys.path.insert(0, './')
import imp
hii = imp.load_source('hii', './hii')
import shutil
import _hydra_ctypes
import glob
import os


# usage:
# python3 ./tests/end_to_end.py 

# Notes:
# hydra must be running on another peer
# hydrad in verbose mode is useful:
# ./hydra/hydrad -v

# standalone due to error as pytest test,
# TODO integrate with pytest

# General Outline:
# Create a post with content of various sizes
# Wait for post to be shared with peers
# Stop service
# Clear peers,posts,blobs directories
# Restart service
# Check for blobs in directory, created via peer resharing


content_test_sizes = [
    1024,
    1024*1024,
    1024*1024 * 10
    ]

def wait(amount):
    print("waiting for {} seconds...".format(amount))
    time.sleep(amount)
    return amount

def main():
    # Problem: starting and stopping hydra service leads
    #         to nested directories .hydra/.hydra/.hydra
    # Solution: change directory after del using os.chdir
    directory = '.hydra'
    peer_share_wait = 5
    shutdown_wait = 2
    shared_blobs = []
    for chunk in content_test_sizes:
        total_wait = 0
        print("starting server to create chunksize: {}".format(chunk))
        hydra_node = _hydra_ctypes.Hydra(directory.encode())
        hydra_node.start()
        blob_sha1 = hydra_post(directory,hydra_node,chunk)
        total_wait += wait(peer_share_wait)

        print("stopping server and cleaning directory")
        del hydra_node
        total_wait += wait(shutdown_wait)
        cleanup(directory)

        print("starting service to see if any will be shared back")
        os.chdir('../')
        hydra_node = _hydra_ctypes.Hydra(directory.encode())
        hydra_node.start()
        total_wait += wait(peer_share_wait)

        print("stopping server and checking for shared")
        del hydra_node
        total_wait += wait(shutdown_wait)

        shared_blobs.append((blob_sha1,chunk,total_wait))
        check_returns_from_peers(directory,shared_blobs)
        os.chdir('../')

def check_returns_from_peers(directory,shared):
    print("----------------------------")
    print()
    print("found?    size    waited    path")
    for blob_sha1,blob_size,total_wait in shared:
        blob = '../{0}/posts/blobs/{1}'.format(directory,blob_sha1)
        print("{1}    {2}    {3}    {0} ".format(blob,
                                                os.path.isfile(blob),
                                                blob_size,
                                                total_wait))
 
def hydra_post(directory,hydra_service,filesize):
    post = {}
    post['subject'] = "contains contents of {} size".format(filesize)
    post['parent_id'] = ""
    post['mime_type'] = "*/*"
    post['contents'] = bytes(bytearray(filesize))
    post_id = hii.hydra_chunk_post(hydra_service,**post)

    content_sha1 = hii.calc_sha1(post['contents'])
    blob = '../{0}/posts/blobs/{1}'.format(directory,content_sha1)
    assert os.path.isfile(blob)
    return content_sha1

def cleanup(directory):
    if directory.startswith("."):
        try:
            shutil.rmtree('../{}/peers'.format(directory))
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree('../{}/posts'.format(directory))
        except FileNotFoundError:
            pass

main()