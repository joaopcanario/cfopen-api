from pymongo import MongoClient, UpdateOne
from collections import namedtuple
from decouple import config, Csv

import requests
import click
import ast


regions = {'Norte': ['Amazonas', 'Roraima', 'Amapá', 'Pará', 'Tocantins',
                     'Rondônia', 'Acre'],
           'Nordeste': ['Maranhão', 'Piauí', 'Ceará', 'Rio Grande do Norte',
                        'Pernambuco', 'Paraíba', 'Sergipe', 'Alagoas',
                        'Bahia'],
           'Centro-Oeste': ['Mato Grosso', 'Mato Grosso do Sul', 'Goias',
                            'Distrito Federal'],
           'Sudeste': ['São Paulo', 'Rio de Janeiro', 'Espírito Santo',
                       'Minas Gerais'],
           'Sul': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']}


abbrv = {'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
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


@click.group()
def main():
    pass


@main.command('upboards', help='Update Ranking DB with last athletes results.')
def upboards():
    from cfopenapi.championship.board import CFGamesBoard
    from bson.objectid import ObjectId
    from datetime import datetime

    entity_db = connect("MONGO_READONLY").entitydb
    ranking_db = connect().rankingdb

    available_boards = config('OPEN_BOARDS', default=[], cast=Csv())
    open_boards = entity_db.find({"name": {"$in": available_boards}})

    uuids = [result["_id"] for result in open_boards]

    for uuid in uuids:
        result = entity_db.find_one({"_id": ObjectId(uuid)})

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                                     upsert=True)]

        ranking_db.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        ranking_db.update_one({'uuid': 'db_last_update'},
                              {"$set": {'updated_on': last_update}},
                              upsert=True)


@main.command('affiliates', help='Retrieves the affiliates data of '
                                 'assigned countries on .env file and '
                                 'generate the Affiliate DB.')
def affiliates():
    from geopy.geocoders import Nominatim

    Location = namedtuple('Location', 'country city state coordinates')

    content = requests.get('https://maps.crossfit.com/getAllAffiliates.php')
    crossfit_affiliates = ast.literal_eval(content.text)

    countries = config('CF_COUNTRIES', default=[], cast=Csv())

    click.echo(f'Countries: {countries}')
    click.echo(f'Number of affiliates: {len(crossfit_affiliates)}')

    geocode = Nominatim()

    data = []
    for aff in crossfit_affiliates:
        lat_lng = ", ".join(map(str, aff[:2]))

        try:
            address = geocode.reverse(lat_lng, timeout=2).raw['address']

            country = address.get("country", '')
            state = address.get("state", '')
            city = address.get("city", '')

            if country in ['Brazil', 'Brasil']:
                state = abbrv.get(state)

                if city == 'SSA':
                    city = 'Salvador'
                elif city == 'SP':
                    city = 'São Paulo'

            location = Location(country, city, state,
                                {"latitude": aff[:2][0],
                                 "longitude": aff[:2][1]})
        except Exception as e:
            location = Location('None', 'None', 'None', 'None')

        click.echo(f"{aff[2]} from {location.country}")

        if location.country in countries:
            click.echo("Added!")
            data.append({"affiliate_id": aff[3],
                         "name": aff[2],
                         "country": location.country,
                         "city": location.city,
                         "state": location.state,
                         "coordinates": location.coordinates})

    click.echo(f'Data size: {len(data)}')
    connect().affiliatedb.insert_many(data, bypass_document_validation=True)


@main.command('entities', help='Generate the Entities DB of Brazil separeted '
                               'by states and regions.')
def entities():
    mongo = connect()

    def affiliates(entity, entity_name):
        Affiliate = namedtuple('Affiliate', 'affiliate_id name country '
                                            'region city state')

        return [Affiliate(a["affiliate_id"], a["name"], a["country"],
                          "Latin America", a["city"], a["state"])._asdict()
                for a in mongo.affiliatedb.find({entity: entity_name})]

    def insert_data(db_name, db_entities):
        data = {'name': db_name, 'entities': db_entities}

        uuid = str(mongo.entitydb.insert_one(data).inserted_id)
        click.echo({'uuid': uuid, 'board_name': db_name})

    def states_leaderboards():
        states = [states for _, states in abbrv.items()]

        for state in states:
            cf_entities = [{'id': af['affiliate_id'], 'name': af['name']}
                           for af in affiliates('state', state)]

            click.echo(f'Added {len(cf_entities)} affiliates from {state}')
            insert_data(state, cf_entities)

    def regions_leaderboards():
        for region, states in regions.items():
            cf_entities = [{'id': af['affiliate_id'], 'name': af['name']}
                           for state in states
                           for af in affiliates('state', state)]

            click.echo(f'Added {len(cf_entities)} affiliates from {region}')
            insert_data(region, cf_entities)

    click.echo('\nAdding affiliates arranged by Brazilian states\n')
    states_leaderboards()

    click.echo('\n\nAdding affiliates arranged by Brazilian regions\n')
    regions_leaderboards()


if __name__ == '__main__':
    main()
