import pytest

import medleydb as mdb


@pytest.fixture(params=(
    'violin',
))
def instrument(request):
    return request.param


def test_instrument(instrument):
    assert mdb.is_valid_instrument(instrument)


def test_instrument_files(instrument):
    assert len(list(mdb.get_files_for_instrument(instrument))) > 0
