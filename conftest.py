import os
import numpy
import pytest
import random as rand
import medleyalchemy as m


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


@pytest.fixture(scope="session")
def medleydb():
    os.environ['MEDLEYDB_PATH']


@pytest.fixture(scope="session", autouse=True)
def session(medleydb):
    _session = m.session(ephemeral=True)
    m.from_medleydb(_session, limit=2)
    return _session
