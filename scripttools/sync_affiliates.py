from decouple import config, Csv
from geopy.geocoders import Nominatim
from pymongo import MongoClient

import collections
import requests
import json
import ast

Location = collections.namedtuple('Location',
                                  'country city state coordinates')

initials = {'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
            'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
            'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba',
            'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
            'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima',
            'SC': 'Santa Catarina', 'SP': 'São Paulo', 'SE': 'Sergipe',
            'TO': 'Tocantins'}

def _retrieve_location(lat, lng):
    try:
        location = Nominatim().reverse(f'{lat}, {lng}', timeout=2)
        address = location.raw['address']

        country = address.get("country", '')
        state = address.get("state", '')
        city = address.get("city", '')

        if country in ['Brazil', 'Brasil']:
            state = initials.get(state)

            if city == 'SSA':
                city = 'Salvador'
            elif city == 'SP':
                city = 'São Paulo'

        coordinates = {"latitude": lat, "longitude": lng}

        return Location(country, city, state, coordinates)
    except Exception as e:
        return Location('None', 'None', 'None', 'None')


if __name__ == '__main__':
    content = requests.get('https://maps.crossfit.com/getAllAffiliates.php')
    crossfit_affiliates = ast.literal_eval(content.text)

    countries = config('CF_COUNTRIES', default=[], cast=Csv())

    print(f'Countries: {countries}')
    print(f'Number of affiliates: {len(crossfit_affiliates)}')

    data = []
    for aff in crossfit_affiliates:
        lat, lng = aff[:2]
        location = _retrieve_location(lat, lng)

        print(f"{aff[2]} from {location.country}")
        if location.country in countries:
            print(f"Added!")
            data.append({"affiliate_id": aff[3],
                         "name": aff[2],
                         "country": location.country,
                         "city": location.city,
                         "state": location.state,
                         "coordinates": location.coordinates})

    print(f'Data size: {len(data)}')

    client = MongoClient(config('MONGO_URI'))
    mongo = client[config('MONGO_DBNAME')]

    affiliates = mongo.affiliatedb
    affiliates.insert_many(data, bypass_document_validation=True)

    # affiliates.update(
    #    { 'city': "SP" },
    #    { '$set': {'city': "São Paulo"} },
    #    multi=True
    # )
