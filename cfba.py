def main():
    from oauth2client.service_account import ServiceAccountCredentials as SAC

    from collections import namedtuple

    from pymongo import UpdateOne

    import gspread

    SCOPE = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = SAC.from_json_keyfile_name(
        '.cfba-leaderboard.json', SCOPE)

    SHT_KEY = '1oFARk7B5gKDQBIIuYGiQPtIXyD45KNwIS2InzQwElVQ'

    Athlete = namedtuple('Athlete', ['name', 'surname', 'gender'])
    WOD = namedtuple('WOD', ['reps', 'tiebreak', 'scaled',
                             'has_tiebreak', 'timecap', 'max_reps'])

    def connect(uri="MONGO_URI"):
        from pymongo import MongoClient
        from decouple import config

        client = MongoClient(config(uri), retryWrites=False)
        mongo = client[config('MONGO_DBNAME')]

        return mongo

    def tiebreak_to_value(t):
        if isinstance(t, str):
            if ':' in t:
                minutes, seconds = t.split(':')
                return int(minutes) * 60 + int(seconds)

            if not t:
                return 0

        return int(t)

    def calculate_score(wod):
        if wod.reps:
            rx = int(not wod.scaled)
            s = ' - s' if wod.scaled else ''
            reps = wod.max_reps if ':' in wod.reps else wod.reps

            if wod.has_tiebreak:
                time = tiebreak_to_value(wod.tiebreak)
                t = wod.timecap - time
            elif ':' in wod.reps:
                time = tiebreak_to_value(wod.reps)
                t = wod.timecap - time
            else:
                t = 0

            score = f'{rx}{int(reps):04}{t:04}'

            if not wod.has_tiebreak:
                if int(reps) == wod.max_reps:
                    display = f'{wod.reps}'
                elif int(reps) < wod.max_reps:
                    display = f'{reps} reps{s}'
            elif wod.has_tiebreak:
                if int(reps) < wod.max_reps:
                    display = f'{reps} reps{s}'
                elif int(reps) == wod.max_reps:
                    display = f'{wod.tiebreak}{s}'
        else:
            display = '--'
            score = 0

        return score, display

    gc = gspread.authorize(credentials)

    cfba_sht = gc.open_by_key(SHT_KEY)
    worksheet = cfba_sht.sheet1

    content = worksheet.get_all_values()

    athletes = []

    for i, r in enumerate(content[1:]):
        atlhete = Athlete(name=r[0], surname=r[1], gender=r[2])

        wod_1 = WOD(reps=r[3], tiebreak=0, scaled=int(r[4].upper() == "SIM"),
                    has_tiebreak=False, timecap=900, max_reps=180)
        sc_1, ds_1 = calculate_score(wod_1)

        wod_2 = WOD(reps=r[5], tiebreak=0, scaled=int(r[6].upper() == "SIM"),
                    has_tiebreak=False, timecap=1200, max_reps=10000000)
        sc_2, ds_2 = calculate_score(wod_2)

        wod_3 = WOD(reps=r[7], tiebreak=r[8],
                    scaled=int(r[9].upper() == "SIM"),
                    has_tiebreak=True, timecap=540, max_reps=165)
        sc_3, ds_3 = calculate_score(wod_3)
        # wod_4 = WOD(reps=r[11], tiebreak=r[12], scaled=int(r[13] == "SIM"))

        athlete = {
            "entrant": {
                "competitorId": str(i),
                "competitorName": f'{atlhete.name} {atlhete.surname}',
                "profilePicS3key": "pukie.png",
                "affiliateName": "CFBA Barra",
                "divisionId": "1" if atlhete.gender == "M" else "2",
                "gender": atlhete.gender
            },
            "scores": [
                {
                    "ordinal": 0,
                    "rank": 0,
                    "score": sc_1,
                    "scoreDisplay": ds_1,
                    "scaled": wod_1.scaled,
                    "time": tiebreak_to_value(wod_1.tiebreak),
                    "dumb": False
                },
                {
                    "ordinal": 1,
                    "rank": 0,
                    "score": sc_2,
                    "scoreDisplay": ds_2,
                    "scaled": wod_2.scaled,
                    "time": tiebreak_to_value(wod_2.tiebreak),
                    "dumb": False
                },
                {
                    "ordinal": 2,
                    "rank": 0,
                    "score": sc_3,
                    "scoreDisplay": ds_3,
                    "scaled": wod_3.scaled,
                    "time": tiebreak_to_value(wod_3.tiebreak),
                    "dumb": False
                },
                # {
                #     "ordinal": 3,
                #     "rank": 0,
                #     "score": sc_4,
                #     "scoreDisplay": ds_4,
                #     "scaled": wod_4.scaled,
                #     "time": tiebreak_to_value(wod_4.tiebreak),
                #     "dumb": False
                # },
                # {
                #     "ordinal": 4,
                #     "scoreDisplay": "--",
                #     "score": "0",
                #     "time": 0,
                #     "scaled": 0,
                #     "rank": 0,
                #     "dumb": True
                # }
            ]
        }

        athletes.append(athlete)

    athletescfba_db = connect().athletescfbadb

    operations = []

    for cid, athlete in enumerate(athletes):
        operations += [UpdateOne({'entrant.competitorId': str(cid)},
                                 {"$set": athlete},
                                 upsert=True)]

    athletescfba_db.bulk_write(operations)


if __name__ == '__main__':
    main()
