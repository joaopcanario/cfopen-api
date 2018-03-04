from cfopenapi import tasks

import pytest
import json


def test_refresh_empty_boards(app):
    app.config['OPEN_BOARDS'] = []

    result = tasks.refresh_boards()

    assert result == 'Success rankings uuids: []'
