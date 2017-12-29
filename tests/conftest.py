import pytest
import sys
sys.path.insert(0, './')
import _hydra_ctypes
import binascii

@pytest.fixture(scope="session", autouse=True)
def hydra_service(request):
    directory = b'.hydra'
    hydra_node = _hydra_ctypes.Hydra(directory)
    hydra_node.start()
    yield hydra_node
    # end hydra service 
    # at end of tests
    del hydra_node

def pytest_addoption(parser):
    parser.addoption("--eye", action="store_true",
        help="show image generated from unicode overlay test")

@pytest.fixture(scope="session", autouse=True)
def reference_jpeg(request):
    # a 15 x 15 jpeg resized from the
    # multilingual_plane_caption test
    str_hex_jpg = """
    ffd8ffe000104a46494600010100000100010000ffdb004300
    080606070605080707070909080a0c140d0c0b0b0c1912130f
    141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c3031
    3434341f27393d38323c2e333432ffdb0043010909090c0b0c
    180d0d1832211c213232323232323232323232323232323232
    32323232323232323232323232323232323232323232323232
    3232323232323232ffc0001108000f000f0301220002110103
    1101ffc4001f00000105010101010101000000000000000001
    02030405060708090a0bffc400b51000020103030204030505
    04040000017d01020300041105122131410613516107227114
    328191a1082342b1c11552d1f02433627282090a161718191a
    25262728292a3435363738393a434445464748494a53545556
    5758595a636465666768696a737475767778797a8384858687
    88898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5
    b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2
    e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f010003
    0101010101010101010000000000000102030405060708090a
    0bffc400b51100020102040403040705040400010277000102
    031104052131061241510761711322328108144291a1b1c109
    233352f0156272d10a162434e125f11718191a262728292a35
    363738393a434445464748494a535455565758595a63646566
    6768696a737475767778797a82838485868788898a92939495
    969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3
    c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9ea
    f2f3f4f5f6f7f8f9faffda000c03010002110311003f00f0ff
    00b5335ac28b38561d7773df8aae618cf26e63c93e87fc2abd
    1401ffd9
    """
    # JPEG image data,
    # JFIF standard 1.01,
    # aspect ratio,
    # density 1x1,
    # segment length 16,
    # baseline,
    # precision 8,
    # 15x15,
    # frames 3

    str_hex_jpg = ''.join(str_hex_jpg)
    str_hex_jpg = str_hex_jpg.replace(" ","")
    str_hex_jpg = str_hex_jpg.replace("\n","")
    str_hex_jpg = str_hex_jpg.strip()

    return binascii.unhexlify(str_hex_jpg)