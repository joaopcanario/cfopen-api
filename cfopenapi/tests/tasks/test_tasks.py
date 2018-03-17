from cfopenapi import tasks


def test_refresh_empty_boards(app):
    app.config['OPEN_BOARDS'] = []

    result = tasks.refresh_boards()

    assert result == 'Success rankings uuids: []'
