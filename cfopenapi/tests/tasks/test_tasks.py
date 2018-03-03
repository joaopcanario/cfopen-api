from cfopenapi import tasks

import pytest
import json


def test_refresh_empty_boards(app):
    app.config['OPEN_BOARDS'] = []

    result = tasks.refresh_boards()

    assert result == 'Success rankings uuids: []'


def test_refresh_uuid_boards(app):
    app.config['OPEN_BOARDS'] = ['Bahia']
    expected_uuids = json.load(open('data/expected_ranks_uuids.json'))

    result = tasks.refresh_boards(False)

    assert result == f'Success rankings uuids: {expected_uuids}'