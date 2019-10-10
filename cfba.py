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
    # WOD = namedtuple('WOD', ['reps', 'tiebreak', 'scaled'])

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

    def calculate_score(reps, scaled, tiebreak, timecap,
                        has_tiebreak, max_reps):
        if reps:
            rx = int(not scaled)
            time = tiebreak_to_value(tiebreak)
            t = timecap - time if has_tiebreak else time
            s = ' - s' if scaled else ''

            score = f'{rx}{int(reps):03}{t:04}'

            if not has_tiebreak:
                display = f'{reps} reps{s}'
            elif has_tiebreak:
                if int(reps) < max_reps:
                    display = f'{reps} reps{s}'
                elif int(reps) == max_reps:
                    display = f'{tiebreak}{s}'
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
        # wod_1 = WOD(reps=r[3], tiebreak=0, scaled=int(r[4] == "SIM"))
        # wod_2 = WOD(reps=r[5], tiebreak=r[6], scaled=int(r[7] == "SIM"))
        # wod_3 = WOD(reps=r[8], tiebreak=r[9], scaled=int(r[10] == "SIM"))
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
                # {
                #     "ordinal": 0,
                #     "rank": 0,
                #     "score": calculate_score(wod_1.reps,
                #                              wod_1.scaled,
                #                              tiebreak=0,
                #                              timecap=480,
                #                              has_tiebreak=False,
                #                              max_reps=1000000)[0],
                #     "scoreDisplay": calculate_score(wod_1.reps,
                #                                     wod_1.scaled,
                #                                     tiebreak=0,
                #                                     timecap=480,
                #                                     has_tiebreak=False,
                #                                     max_reps=1000000)[1],
                #     "scaled": wod_1.scaled,
                #     "time": 0,
                #     "dumb": False
                # },
                # {
                #     "ordinal": 1,
                #     "rank": 0,
                #     "score": calculate_score(wod_2.reps,
                #                              wod_2.scaled,
                #                              wod_2.tiebreak,
                #                              timecap=1200,
                #                              has_tiebreak=True,
                #                              max_reps=430)[0],
                #     "scoreDisplay": calculate_score(wod_2.reps,
                #                                     wod_2.scaled,
                #                                     wod_2.tiebreak,
                #                                     timecap=1200,
                #                                     has_tiebreak=True,
                #                                     max_reps=430)[1],
                #     "scaled": wod_2.scaled,
                #     "time": tiebreak_to_value(wod_2.tiebreak),
                #     "dumb": False
                # },
                # {
                #     "ordinal": 2,
                #     "rank": 0,
                #     "score": calculate_score(wod_3.reps,
                #                              wod_3.scaled,
                #                              wod_3.tiebreak,
                #                              timecap=600,
                #                              has_tiebreak=True,
                #                              max_reps=180)[0],
                #     "scoreDisplay": calculate_score(wod_3.reps,
                #                                     wod_3.scaled,
                #                                     wod_3.tiebreak,
                #                                     timecap=600,
                #                                     has_tiebreak=True,
                #                                     max_reps=180)[1],
                #     "scaled": wod_3.scaled,
                #     "time": tiebreak_to_value(wod_3.tiebreak),
                #     "dumb": False
                # },
                # {
                #     "ordinal": 3,
                #     "rank": 0,
                #     "score": calculate_score(wod_4.reps,
                #                              wod_4.scaled,
                #                              wod_4.tiebreak,
                #                              timecap=720,
                #                              has_tiebreak=True,
                #                              max_reps=132)[0],
                #     "scoreDisplay": calculate_score(wod_4.reps,
                #                                     wod_4.scaled,
                #                                     wod_4.tiebreak,
                #                                     timecap=720,
                #                                     has_tiebreak=True,
                #                                     max_reps=132)[1],
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
