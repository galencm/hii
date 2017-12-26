import sys
#since hii lacks .py use imp
#insert path for pytest
sys.path.insert(0, './')
import imp
hii = imp.load_source('hii', './hii')
import _hydra_ctypes
import pytest
import glob
import os
import io
from PIL import Image

def test_generate_words(word_count=3):
    assert len(hii.generate_words().split(" ")) == 3

def test_generate_image_bytes():
    image_bytes = hii.generate_image_bytes()
    assert type(image_bytes) is bytes
    image = Image.open(io.BytesIO(image_bytes))
    image_extension = image.format
    image.close()
    assert image_extension =="JPEG" 

def parse_zpl(file):
    zpl_parsed =  {}
    lines = []
    with open(file,'r') as f:
        for line in f.readlines():
            kv = line.partition("=")
            if kv[-1] != "":
                key = kv[0].strip()
                value = kv[-1].replace('"','').strip()
                zpl_parsed[key] = value
    return zpl_parsed

def test_chunk_post():
    directory = b'.hydra'
    hydra_service = _hydra_ctypes.Hydra(directory)
    hydra_service.start()
    post = hii.make_chunk_post(hydra_service)
    #stop service
    del hydra_service

    assert 'ident' in post
    assert len(post['ident']) > 0
    stored_posts = glob.glob('../.hydra/posts/[0-9]*')
    latest_post = max(stored_posts, key=os.path.getctime)
    disk_post = parse_zpl(latest_post)
    print(disk_post)
    assert disk_post['ident'] == post['ident']
    chunk_blob = os.path.join("../.hydra",disk_post['location'])
    assert os.path.isfile(chunk_blob)
    assert os.path.getsize(chunk_blob) == int(disk_post['content-size'])
    assert len(post['contents']) == os.path.getsize(chunk_blob)
    os.remove(latest_post)
    os.remove(chunk_blob)

def test_string_post():
    directory = b'.hydra'
    hydra_service = _hydra_ctypes.Hydra(directory)
    hydra_service.start()
    post = hii.make_string_post(hydra_service)
    #stop service
    del hydra_service

    assert 'ident' in post
    assert len(post['ident']) > 0
    stored_posts = glob.glob('../.hydra/posts/[0-9]*')
    latest_post = max(stored_posts, key=os.path.getctime)
    disk_post = parse_zpl(latest_post)
    print(disk_post)
    assert disk_post['ident'] == post['ident']
    chunk_blob = os.path.join("../.hydra",disk_post['location'])
    assert os.path.isfile(chunk_blob)
    assert os.path.getsize(chunk_blob) == int(disk_post['content-size'])
    assert len(post['contents']) == os.path.getsize(chunk_blob)
    os.remove(latest_post)
    os.remove(chunk_blob)

def test_b64_post():
    directory = b'.hydra'
    hydra_service = _hydra_ctypes.Hydra(directory)
    hydra_service.start()
    post = hii.make_b64_post(hydra_service)
    #stop service
    del hydra_service

    assert 'ident' in post
    assert len(post['ident']) > 0
    stored_posts = glob.glob('../.hydra/posts/[0-9]*')
    latest_post = max(stored_posts, key=os.path.getctime)
    disk_post = parse_zpl(latest_post)
    print(disk_post)
    assert disk_post['ident'] == post['ident']
    chunk_blob = os.path.join("../.hydra",disk_post['location'])
    assert os.path.isfile(chunk_blob)
    assert os.path.getsize(chunk_blob) == int(disk_post['content-size'])
    assert len(post['contents']) == os.path.getsize(chunk_blob)
    os.remove(latest_post)
    os.remove(chunk_blob)

