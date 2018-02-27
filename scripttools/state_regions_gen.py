#!/usr/bin/env python

from decouple import config, Csv
from pymongo import MongoClient

import collections
import requests
import json
import ast


states = ['Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará',
          'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão',
          'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará',
          'Paraíba', 'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro',
          'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondônia', 'Roraima',
          'Santa Catarina', 'São Paulo', 'Sergipe', 'Tocantins']


regions = {'Norte': ['Amazonas', 'Roraima', 'Amapá', 'Pará', 'Tocantins',
                     'Rondônia', 'Acre'],
           'Nordeste': ['Maranhão', 'Piauí', 'Ceará', 'Rio Grande do Norte',
                        'Pernambuco', 'Paraíba', 'Sergipe', 'Alagoas',
                        'Bahia'],
           'Centro Oeste': ['Mato Grosso', 'Mato Grosso do Sul', 'Goias',
                            'Distrito Federal'],
           'Sudeste': ['São Paulo', 'Rio de Janeiro', 'Espírito Santo',
                       'Minas Gerais'],
           'Sul': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']}


def affiliates(entity, entity_name):
    Affiliate = collections.namedtuple('Affiliate',
                                       'affiliate_id name country '
                                       'region city state')

    result = mongo.affiliatedb.find({entity: entity_name})
    response = [Affiliate(a["affiliate_id"], a["name"], a["country"],
                          "Latin America", a["city"], a["state"])._asdict()
                for a in result]

    return response


def create_states_leaderboards():
    for state in states:
        affiliates_list = affiliates('state', state)
        cf_entities = [{'id': af['affiliate_id'], 'name': af['name']}
                       for af in affiliates_list]

        data = {'name': state,
                'owner': 'João Paulo Canário',
                'entities': cf_entities}

        uuid = str(mongo.entitydb.insert_one(data).inserted_id)
        print({'uuid': uuid, 'board_name': state})


def create_regions_leaderboards():
    for region, states in regions.items():
        cf_entities = []

        for state in states:
            affiliates_list = affiliates('state', state)
            cf_entities += [{'id': af['affiliate_id'], 'name': af['name']}
                            for af in affiliates_list]

        data = {'name': region,
                'owner': 'João Paulo Canário',
                'entities': cf_entities}

        uuid = str(mongo.entitydb.insert_one(data).inserted_id)
        print({'uuid': uuid, 'board_name': region})


if __name__ == '__main__':
    client = MongoClient(config('MONGO_URI'))
    mongo = client[config('MONGO_DBNAME')]

    print('Creating leaderboard by state')
    create_states_leaderboards(mongo)

    print('Creating leaderboard by region')
    create_regions_leaderboards(mongo)
