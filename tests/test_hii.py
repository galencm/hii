import sys
#since hii lacks .py use imp
#insert path for pytest
sys.path.insert(0, './')
import imp
hii = imp.load_source('hii', './hii')
import pytest
import glob
import os
import io
from PIL import Image
import shutil
import czmq
import ctypes
import hashlib
import textwrap

@pytest.fixture()
def show_created_onscreen(request):
    return request.config.getoption('--eye')

def test_generate_words():
    words = hii.generate_words()
    assert type(words) is str
    assert len(words) > 0

def test_unicode_basic_multilingual_plane_caption(show_created_onscreen):
    viewer_program = "display"
    bmp_string = textwrap.dedent("""1) आदर्श (p. 38)
    â-darsá seeing;
    mirror;
    image;
    copy;
    -pustaka, n. copy, manuscript;
    -maya, a. being altogether mirror.""")
    # A Practical Sanskrit Dictionary, Macdonell, 1929
    # http://dsal.uchicago.edu/dictionaries/macdonell/

    if show_created_onscreen is True:
        if shutil.which(viewer_program) is None:
            pytest.fail("program: {program_name} not found by which\n install {program_name} or run without --eye ".format(program_name=viewer_program))

    image_bytes = hii.generate_image_bytes(caption_overlay=bmp_string,
                                        display_created_image=show_created_onscreen)
def test_generate_image_bytes():
    image_bytes = hii.generate_image_bytes()
    assert type(image_bytes) is bytes
    image = Image.open(io.BytesIO(image_bytes))
    image_extension = image.format
    image.close()
    assert image_extension =="JPEG" 

def test_basic_multilingual_plane_string_post(hydra_service):
    bmp_subject = "आदर्श"
    bmp_contents = textwrap.dedent("""1) आदर्श (p. 38)
    â-darsá seeing;
    mirror;
    image; copy;
    -pustaka, n. copy, manuscript;
    -maya, a. being altogether mirror.""")

    post = {}
    post['subject'] = bmp_subject
    post['contents'] = bmp_contents
    post = hii.make_string_post(hydra_service,**post)

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
    #encode unicode before compare with bytes
    try:
        post['contents'] = post['contents'].encode()
    except AttributeError:
        pass
    assert len(post['contents']) == os.path.getsize(chunk_blob)
    #check contents

    with open(chunk_blob,'rb') as f:
        assert f.read() == post['contents']

    #cleanup post/blob
    os.remove(latest_post)
    os.remove(chunk_blob)

def parse_zpl(file):
    # ZeroMQ Property Language
    # https://rfc.zeromq.org/spec:4/ZPL/
    # 
    # this just returns a dict by splitting strings 
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

def test_fail_on_post_metadata_not_in_data_model():
    # service is not passed in since
    # just testing that post dict is rejected
    # before calling service    

    post = {}
    hydra_service = None

    post['not_in_hydra_data_model'] = "see data model," \
                                        "in hydra README"
    with pytest.raises(TypeError):
        post = hii.make_string_post(hydra_service,**post)

    with pytest.raises(TypeError):
        post = hii.make_chunk_post(hydra_service,**post)

def test_accept_post_metadata_in_data_model():
    # service is not passed in since
    # just testing that post dict is accepted
    # before calling service

    post = {}
    hydra_service = None

    post['subject'] = "..."
    post['contents'] = "..."
    post['mime_type'] = "text/plain"
    #optional
    post['parent_id'] = ""

    # post is good so an AttributeError 
    # should be raised while trying to call
    # hydra_service
    with pytest.raises(AttributeError):
        post = hii.make_string_post(hydra_service)

    with pytest.raises(AttributeError):
        post = hii.make_chunk_post(hydra_service)

def test_chunk_post(hydra_service):

    post = hii.make_chunk_post(hydra_service)

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
    try:
        post['contents'] = post['contents'].encode()
    except AttributeError:
        pass
    assert len(post['contents']) == os.path.getsize(chunk_blob)

    # having trouble getting Zchunk_read to work
    # involves FILE* in python3 
    # so: read bytes from file, create Zchunk with bytes
    # calculate sha1 using Zchunk digest, calulate sha1 on read byes
    raw_chunk = b''
    with open(chunk_blob,'rb') as f:
        raw_chunk = f.read()
    p = ctypes.c_char_p(raw_chunk)
    chunk = czmq.Zchunk(ctypes.string_at(p,size=len(raw_chunk)),len(raw_chunk))

    # currently hyra code assumes 1 chunk for blobs
    # though multipart is discussed in code
    # from hydra docs: 
    # README.txt:Every post has a content of zero or more octets. 
    #            Hydra does not support multipart contents.
    # README.txt-//TODO: extend to support multiple content parts.//

    #TODO zchunk.read returns byte *
    assert raw_chunk == bytearray.fromhex(chunk.strhex().decode())

def test_string_post(hydra_service):

    post = hii.make_string_post(hydra_service)

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
    try:
        post['contents'] = post['contents'].encode()
    except AttributeError:
        pass
    assert len(post['contents']) == os.path.getsize(chunk_blob)
    #check contents

    with open(chunk_blob,'rb') as f:
        assert f.read() == post['contents']

def calc_sha1(hash_this):
    # return sha1 in uppercase hex
    try:
        hash_this = hash_this.encode()
    except AttributeError:
        pass

    sha1_hash = hashlib.sha1()
    sha1_hash.update(hash_this)
    return sha1_hash.hexdigest().upper()

def test_duplicate_content_chunk_string(hydra_service):
    # post the same content multiple times
    # should create / overwrite one blob
    # with correct sha1

    repetitive_posts = 3

    #clear post directory
    try:
        shutil.rmtree('../.hydra/posts')
    except FileNotFoundError:
        pass

    for _ in range(repetitive_posts):
        post = {}
        # supply content string
        post['contents'] = "contents for a blob!"
        post_id = hii.make_chunk_post(hydra_service,**post)

    blobs = glob.glob('../.hydra/posts/blobs/*')
    assert len(blobs) == 1
    blob = blobs[0]

    with open(blob,'rb') as f:
        blob_contents = f.read()
    assert blob_contents

    blob_fname_sha1 = blob.rsplit("/")[-1].upper()
    blob_fcontents_sha1 = calc_sha1(blob_contents)
    blob_source_sha1  = calc_sha1(post['contents'])

    print("all hashes should be the same:\n")
    print("sha1 source (correct):     {}".format(blob_source_sha1))
    print("sha1 filename:             {}".format(blob_fname_sha1))
    print("sha1 file contents:        {}".format(blob_fcontents_sha1))
    assert blob_fname_sha1 == blob_fcontents_sha1 == blob_source_sha1

def test_duplicate_content_chunk_image(hydra_service,reference_jpeg):
    # post the same content multiple times
    # should create / overwrite one blob
    # with correct sha1

    repetitive_posts = 3
    post = {}

    #clear post directory
    try:
        shutil.rmtree('../.hydra/posts')
    except FileNotFoundError:
        pass

    for _ in range(repetitive_posts):
        post = {}
        # supply content image bytes
        post['contents'] = reference_jpeg
        post_id = hii.make_chunk_post(hydra_service,**post)

    blobs = glob.glob('../.hydra/posts/blobs/*')
    assert len(blobs) == 1
    blob = blobs[0]

    with open(blob,'rb') as f:
        blob_contents = f.read()
    assert blob_contents

    blob_fname_sha1 = blob.rsplit("/")[-1].upper()
    blob_fcontents_sha1 = calc_sha1(blob_contents)
    blob_source_sha1  = calc_sha1(post['contents'])

    print("all hashes should be the same:\n")
    print("sha1 source (correct):     {}".format(blob_source_sha1))
    print("sha1 filename:             {}".format(blob_fname_sha1))
    print("sha1 file contents:        {}".format(blob_fcontents_sha1))
    assert blob_fname_sha1 == blob_fcontents_sha1 == blob_source_sha1
