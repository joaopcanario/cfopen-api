from flask import url_for


def test_not_pass_query_params(client):
    res = client.get(url_for('cfopen_bp.leaderboards'))

    assert res.status_code == 200
    assert res.json == (f'Missing required parameters: name=None, '
                        f'division=None')


def test_get_bahia_men_60_plus_leaderboard(client):
    res = client.get(url_for('cfopen_bp.leaderboards',
                             name='Bahia',
                             division='Men (60+)'))

    assert res.status_code == 200
    assert res.json == []


def test_root_without_documentation(client):
    res = client.get(url_for('core_bp.root'))

    assert res.status_code == 200
    assert res.json == "API Documentation isn't loaded!"


def test_ping(client):
    res = client.get(url_for('debug_bp.ping'))

    assert res.status_code == 200
    assert res.json == 'Pong!'


def test_version(client):
    res = client.get(url_for('debug_bp.version'))

    assert res.status_code == 200
    assert res.json == 'API version: 1.0.0'
