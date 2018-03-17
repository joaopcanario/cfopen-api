from cfopenapi.championship.board import (Athlete, Board,
                                          CFGamesBoard, divisions)

import json


def test_load_athlete():
    data = json.load(open('data/fake_athletes_18_2.json'))
    expected_athlete = json.load(open('data/expected_athlete.json'))

    athletes = Athlete.from_list(data, 6)

    assert athletes[0] == expected_athlete


def test_create_entity_board():
    entities = json.load(open('data/fake_entity.json'))
    ordinals = 6

    cfboard = CFGamesBoard(entities, ordinals)

    assert cfboard.athletes
    assert not cfboard.boards
    assert not cfboard.ranks
    assert cfboard.ordinals == ordinals


def test_rank_board():
    data = json.load(open('data/fake_athletes_18_2.json'))
    expected_rank = json.load(open('data/expected_rank_18_2.json'))

    ordinals = 6
    uuid = '1234'

    board = Board(Athlete.from_list(data, ordinals), ordinals)
    board.generate_ranks(uuid)

    generated_rank = [ranking._asdict() for ranking in board.ranks
                      if ranking.uuid == '1234_Men (18-34)'][0]

    assert generated_rank['uuid'] == expected_rank['uuid']
    assert generated_rank['name'] == expected_rank['name']

    assert len(generated_rank['athletes']) == len(expected_rank['athletes'])

    assert generated_rank['athletes'][0] == expected_rank['athletes'][0]
    assert generated_rank['athletes'][1] == expected_rank['athletes'][1]
    assert generated_rank['athletes'][2] == expected_rank['athletes'][2]
    assert generated_rank['athletes'][3] == expected_rank['athletes'][3]
    assert generated_rank['athletes'][4] == expected_rank['athletes'][4]
    assert generated_rank['athletes'][5] == expected_rank['athletes'][5]
    assert generated_rank['athletes'][6] == expected_rank['athletes'][6]


def test_ranks_uuids():
    data = json.load(open('data/fake_athletes_18_2.json'))

    ordinals = 6
    uuid = '1234'

    athletes = Athlete.from_list(data, ordinals)

    expected_uuids = ['1234_Men (18-34)', '1234_Women (18-34)',
                      '1234_Men (45-49)', '1234_Women (45-49)',
                      '1234_Men (50-54)', '1234_Women (50-54)',
                      '1234_Men (55-59)', '1234_Women (55-59)',
                      '1234_Men (60+)', '1234_Women (60+)',
                      '1234_Men (40-44)', '1234_Women (40-44)',
                      '1234_Boys (14-15)', '1234_Girls (14-15)',
                      '1234_Boys (16-17)', '1234_Girls (16-17)',
                      '1234_Men (35-39)', '1234_Women (35-39)',
                      '1234_Masculino', '1234_Feminino']

    uuids = []

    for division_id, division in divisions.items():
        athletes = [athlete for athlete in athletes
                    if athlete['division'] in division]

        if division_id in ["Masculino", "Feminino"]:
            division = division_id

        rank_uuid = f"{uuid}_{division}"
        uuids.append(rank_uuid)

    assert uuids == expected_uuids


def test_from_list_to_leaderboard():
    rank = json.load(open('data/expected_rank_18_2.json'))
    expected_response = json.load(open('data/expected_leaderboard_18.2.json'))

    response = Athlete.from_list_to_leaderboard(rank['athletes'])

    assert expected_response == response
