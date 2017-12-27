import pytest

def pytest_addoption(parser):
    parser.addoption("--eye", action="store_true",
        help="show image generated from unicode overlay test")
