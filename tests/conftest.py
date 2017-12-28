import pytest
import sys
sys.path.insert(0, './')
import _hydra_ctypes

@pytest.fixture(scope="session", autouse=True)
def hydra_service(request):
    directory = b'.hydra'
    hydra_node = _hydra_ctypes.Hydra(directory)
    hydra_node.start()

    def end_service():
        del hydra_node
    request.addfinalizer(end_service)
    return hydra_node


def pytest_addoption(parser):
    parser.addoption("--eye", action="store_true",
        help="show image generated from unicode overlay test")
