from flask import current_app as app

import celery


@celery.task()
def refresh_boards():
    from ..database import connect
    from ..championship.board import CFGamesBoard

    from pymongo import UpdateOne
    from bson.objectid import ObjectId
    from datetime import datetime

    with app.app_context():
        available_boards = app.config.get('OPEN_BOARDS')

    entity_db = connect("MONGO_READONLY").entitydb
    ranking_db = connect().rankingdb

    open_boards = entity_db.find({"name": {"$in": available_boards}})

    uuids = [result["_id"] for result in open_boards]

    ranks_uuids = []

    for uuid in uuids:
        result = entity_db.find_one({"_id": ObjectId(uuid)})

        cf_board = CFGamesBoard(result['entities'])
        cf_board.generate_ranks(uuid)

        operations = []

        for ranking in cf_board.ranks:
            ranks_uuids.append(ranking.uuid)

            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                                     upsert=True)]

        ranking_db.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        ranking_db.update_one({'uuid': 'db_last_update'},
                              {"$set": {'updated_on': last_update}},
                              upsert=True)

    return f'Success rankings uuids: {ranks_uuids}'


@celery.task()
def refresh_cfbaboards():
    from ..database import connect
    from ..championship.board import Board, Athlete

    from pymongo import UpdateOne
    from datetime import datetime

    athletescfba_db = connect("MONGO_READONLY").athletescfbadb
    rankingcfba_db = connect().rankingcfbadb

    uuids = ["dj8bd2j7et4fjxa01f"]

    ranks_uuids = []

    for uuid in uuids:
        result = athletescfba_db.find({})
        athletes = Athlete.from_list(result, ordinal=5)

        board = Board(athletes, num_of_ordinals=5)
        board.generate_ranks(uuid)

        operations = []

        for ranking in board.ranks:
            ranks_uuids.append(ranking.uuid)

            operations += [UpdateOne({"uuid": ranking.uuid},
                                     {"$set": ranking._asdict()},
                                     upsert=True)]

        rankingcfba_db.bulk_write(operations)

    if uuids:
        last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

        rankingcfba_db.update_one({'uuid': 'db_last_update'},
                                  {"$set": {'updated_on': last_update}},
                                  upsert=True)

    return f'Success rankings uuids: {ranks_uuids}'


# @celery.task()
# def retrieve_cfba_data():
#     from __future__ import print_function
#     import pickle
#     import os.path
#     from googleapiclient.discovery import build
#     from google_auth_oauthlib.flow import InstalledAppFlow
#     from google.auth.transport.requests import Request

#     # If modifying these scopes, delete the file token.pickle.
#     SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

#     # The ID and range of a sample spreadsheet.
#     SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
#     SAMPLE_RANGE_NAME = 'Class Data!A2:E'

#     def main():
#         """Shows basic usage of the Sheets API.
#         Prints values from a sample spreadsheet.
#         """
#         creds = None
#         # The file token.pickle stores the user's access and refresh tokens, and is
#         # created automatically when the authorization flow completes for the first
#         # time.
#         if os.path.exists('token.pickle'):
#             with open('token.pickle', 'rb') as token:
#                 creds = pickle.load(token)
#         # If there are no (valid) credentials available, let the user log in.
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     'credentials.json', SCOPES)
#                 creds = flow.run_local_server()
#             # Save the credentials for the next run
#             with open('token.pickle', 'wb') as token:
#                 pickle.dump(creds, token)

#         service = build('sheets', 'v4', credentials=creds)

#         # Call the Sheets API
#         sheet = service.spreadsheets()
#         result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#                                     range=SAMPLE_RANGE_NAME).execute()
#         values = result.get('values', [])

#         if not values:
#             print('No data found.')
#         else:
#             print('Name, Major:')
#             for row in values:
#                 # Print columns A and E, which correspond to indices 0 and 4.
#                 print('%s, %s' % (row[0], row[4]))

#     main()
