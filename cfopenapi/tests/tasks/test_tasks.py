from cfopenapi import tasks


def test_refresh_empty_boards(app):
    app.config['OPEN_BOARDS'] = []

    result = tasks.refresh_boards()

    assert result == 'Success rankings uuids: []'


# def test_add_cfba_athlete():
#     data = json.load(open('data/fake_cfba_athlete_data.json'))
#     expected_athlete = json.load(open('data/expected_cfba_athlete_19_2.json'))

#     athletes = Athlete.from_list(data, 5)

#     assert expected_athlete == athletes
