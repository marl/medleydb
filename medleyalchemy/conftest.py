import numpy
import pytest
import random as rand


@pytest.fixture(params=(44100, 16000))
def fs(request):
    return request.param


@pytest.fixture(params=(1,))
def sig(request, fs, random):
    l = 1

    return numpy.squeeze(
        numpy.random.uniform(-1.0, 1.0, (l * fs, request.param))
    )


@pytest.fixture
def random():
    rand.seed(0)
    numpy.random.seed(0)
