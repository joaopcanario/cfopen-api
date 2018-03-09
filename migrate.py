from pymongo import MongoClient, UpdateOne
from collections import namedtuple
from decouple import config, Csv

import requests
import click
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


br_initials = {'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
               'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
               'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
               'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
               'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba',
               'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
               'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
               'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima',
               'SC': 'Santa Catarina', 'SP': 'São Paulo', 'SE': 'Sergipe',
               'TO': 'Tocantins'}


def connect(uri="MONGO_URI"):
    client = MongoClient(config(uri))
    mongo = client[config('MONGO_DBNAME')]

    return mongo


def retrieve_location(lat, lng):
    from geopy.geocoders import Nominatim

    Location = namedtuple('Location', 'country city state coordinates')

    try:
        location = Nominatim().reverse(f'{lat}, {lng}', timeout=2)
        address = location.raw['address']

        country = address.get("country", '')
        state = address.get("state", '')
        city = address.get("city", '')

        if country in ['Brazil', 'Brasil']:
            state = br_initials.get(state)

            if city == 'SSA':
                city = 'Salvador'
            elif city == 'SP':
                city = 'São Paulo'

        coordinates = {"latitude": lat, "longitude": lng}

        return Location(country, city, state, coordinates)
    except Exception as e:
        return Location('None', 'None', 'None', 'None')


@click.group()
def main():
   pass


@main.command()
def refresh_boards():
    from cfopenapi.championship.board import CFGamesBoard
    from bson.objectid import ObjectId
    from datetime import datetime

    available_boards = config('OPEN_BOARDS', default=[], cast=Csv())

    filter = {"name": { "$in": available_boards }}
    open_boards = connect("MONGO_READONLY").entitydb.find(filter)

    uuids = [result["_id"] for result in open_boards]

    for uuid in uuids:
        filter = {"_id": ObjectId(uuid)}

        result = connect("MONGO_READONLY").entitydb.find_one(filter)

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                           upsert=True)]

        connect().rankingdb.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        data = {'uuid': 'db_last_update', 'updated_on': last_update}
        connect().rankingdb.insert_one(data)


@main.command()
def fetch_affiliates():
    content = requests.get('https://maps.crossfit.com/getAllAffiliates.php')
    crossfit_affiliates = ast.literal_eval(content.text)

    countries = config('CF_COUNTRIES', default=[], cast=Csv())

    print(f'Countries: {countries}')
    print(f'Number of affiliates: {len(crossfit_affiliates)}')

    data = []
    for aff in crossfit_affiliates:
        lat, lng = aff[:2]
        location = retrieve_location(lat, lng)

        print(f"{aff[2]} from {location.country}")
        if location.country in countries:
            print("Added!")
            data.append({"affiliate_id": aff[3],
                         "name": aff[2],
                         "country": location.country,
                         "city": location.city,
                         "state": location.state,
                         "coordinates": location.coordinates})

    print(f'Data size: {len(data)}')
    connect().affiliatedb.insert_many(data, bypass_document_validation=True)


@main.command()
def generate_entities():
    def affiliates(entity, entity_name):
        Affiliate = namedtuple('Affiliate', 'affiliate_id name country '
                                            'region city state')

        result = connect().affiliatedb.find({entity: entity_name})
        response = [Affiliate(a["affiliate_id"], a["name"], a["country"],
                              "Latin America", a["city"], a["state"])._asdict()
                    for a in result]

        return response

    def insert_data(db_name, db_entities):
        data = {'name': db_name, 'entities': db_entities}

        uuid = str(connect().entitydb.insert_one(data).inserted_id)
        print({'uuid': uuid, 'board_name': db_name})

    def states_leaderboards():
        for state in states:
            cf_entities = [{'id': af['affiliate_id'], 'name': af['name']}
                           for af in affiliates('state', state)]
            insert_data(state, cf_entities)


    def regions_leaderboards():
        for region, states in regions.items():
            cf_entities = [{'id': af['affiliate_id'], 'name': af['name']}
                           for af in affiliates('state', state)
                           for state in states]
            insert_data(region, cf_entities)

    print('Creating leaderboard by state')
    states_leaderboards()

    print('Creating leaderboard by region')
    regions_leaderboards()


if __name__ == '__main__':
    main()
