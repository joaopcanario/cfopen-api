from collections import namedtuple


divisions = {1: 'Men (18-34)', 2: 'Women (18-34)',
             3: 'Men (45-49)', 4: 'Women (45-49)',
             5: 'Men (50-54)', 6: 'Women (50-54)',
             7: 'Men (55-59)', 8: 'Women (55-59)',
             9: 'Men (60+)', 10: 'Women (60+)',
             # 11: 'Team',
             12: 'Men (40-44)', 13: 'Women (40-44)',
             14: 'Boys (14-15)', 15: 'Girls (14-15)',
             16: 'Boys (16-17)', 17: 'Girls (16-17)',
             18: 'Men (35-39)', 19: 'Women (35-39)',

             # Leaderboards combination
             # Male
             "Masculino":'Men (18-34) Men (45-49) Men (50-54) Men (55-59) '
                         'Men (60+) Men (40-44) Boys (14-15) Boys (16-17) '
                         'Men (35-39)',

             # Male
             "Feminino": 'Women (18-34) Women (45-49) Women (50-54) '
                         'Women (55-59) Women (60+) Women (40-44) '
                         'Girls (14-15) Girls (16-17) Women (35-39)'}


# 2017
# max_reps = [225, 0, 216, 0, 440]

# 2018
max_reps = [0, 0, 0, 0, 0]

Ranking = namedtuple('Ranking', 'uuid name athletes')

dumb_score = {"ordinal": 1, "rank": "", "score": "0", "scoreDisplay": "",
              "mobileScoreDisplay": "", "scoreIdentifier": "", "scaled": "0",
              "video": "0", "judge": "", "affiliate": "", "time": "",
              "breakdown": "", "heat": "", "lane": ""}


class Base(object):

    def __init__(self):
        super().__init__()

    def asdict(self):
        return vars(self)


class Score(Base):
    def __init__(self, ordinal, score, dumb=False):
        super().__init__()

        self.ordinal = ordinal
        self.display = score.get("scoreDisplay")
        # self.wod_score = self._score_from_display()

        # if score.get("scoredetails"):
        #     self.tiebreak = score.get("scoredetails").get('time', 'null')
        # else:
        #     self.tiebreak = "null"

        self.wod_score = score.get("score")
        self.tiebreak = self.wod_score

        self.scale = score.get("scaled") == "1"
        self.rank = 0

        self.dumb = dumb

    def _score_from_display(self):
        import re

        pattern = re.compile(r'( - s)|( reps)')
        self.display = pattern.sub("", self.display)

        if ':' in self.display:
            ddisplay = enumerate(reversed(self.display.split(":")))
            seconds = sum(int(x) * 60 ** i for i, x in ddisplay)
            return (max_reps[self.ordinal] / seconds) + max_reps[self.ordinal]

        return int(self.display)


class Athlete(Base):
    def __init__(self, user_id, name, affiliate, division, profile_pic,
                 scores, overallscore=0):
        super().__init__()

        _profilepicsbucket = "https://profilepicsbucket.crossfit.com"

        self.user_id = user_id
        self.name = name
        self.affiliate = affiliate

        self.division = divisions.get(int(division))
        self.profile_pic = f"{_profilepicsbucket}/{profile_pic}"
        self.overallscore = overallscore

        self.scores = [Score(ordinal, score).asdict()
                       for ordinal, score in enumerate(scores)]

        for i in range(len(self.scores), 5):
            self.scores.append(Score(i, dumb_score, True).asdict())


class Board(Base):
    def __init__(self, athletes):
        super().__init__()

        self.athletes = athletes
        self.boards = {}
        self.ranks = []
        self.ordinals = 5

    def _sort(self, board):
        for w in range(0, 5):
            # RX
            rx = [athlete for athlete in board
                  if not athlete["scores"][w]['scale'] and
                     not athlete["scores"][w]['tiebreak'] == 'null' and
                     not athlete["scores"][w]['dumb']]
            rx = sorted(rx,
                        key=lambda x: (x["scores"][w]['wod_score'],
                                       x["scores"][w]['tiebreak']),
                        reverse=True)

            # SCALE
            scale = [athlete for athlete in board
                     if athlete["scores"][w]['scale'] and
                        not athlete["scores"][w]['tiebreak'] == 'null' and
                        not athlete["scores"][w]['dumb']]
            scale = sorted(scale,
                           key=lambda x: (x["scores"][w]['wod_score'],
                                          x["scores"][w]['tiebreak']),
                           reverse=True)

            # NOT PERFORMED
            not_performed = [athlete for athlete in board
                             if athlete["scores"][w]['tiebreak'] == 'null' and
                                not athlete["scores"][w]['dumb']]

            self._update_athletes_rank(rx + scale + not_performed, w)

        # OVERALL SCORE
        for athlete in board:
            athlete["overallscore"] = sum([athlete['scores'][w]["rank"]
                                           for w in range(0, 5)])

        return sorted(board, key=lambda x: x['overallscore'])

    def _update_athletes_rank(self, all_athletes, wod_score):
        prev_rank = 1
        prev_score = (0, 0)

        for position, athlete in enumerate(all_athletes):
            atl_wod = athlete["scores"][wod_score]
            rank = position + 1

            actual_score = (atl_wod["wod_score"], atl_wod["tiebreak"])

            if actual_score == prev_score:
                rank = prev_rank
            else:
                prev_rank = rank

            prev_score = (atl_wod["wod_score"], atl_wod["tiebreak"])
            atl_wod["rank"] = rank

    def generate_ranks(self, uuid):
        for key, div in divisions.items():
            board = [athlete for athlete in self.athletes
                     if athlete['division'] in div]

            if key in ["Masculino", "Feminino"]:
                div = key

            board = self._sort(board)

            self.boards[div] = board
            self.ranks.append(Ranking(f"{uuid}_" + div, div, board))


class CFGamesBoard(Board):
    def __init__(self, entities):
        def _board_page(id, name, div):
            from .external import load_from_api

            page, total_pages = 1, 1

            while page <= total_pages:
                athletes, total_pages = load_from_api(id, page, div)
                page += 1

                athletes_page = []

                for a in athletes:
                    entrant = a["entrant"]

                    if entrant["divisionId"] == str(div):
                        athlete = Athlete(entrant["competitorId"],
                                          entrant["competitorName"],
                                          name, div,
                                          entrant["profilePicS3key"],
                                          a["scores"]).asdict()

                        athletes_page.append(athlete)

                yield athletes_page

        divs = [i for i, _ in divisions.items()
                if i not in ["Masculino", "Feminino"]]

        all_athletes = []

        for entity in entities:
            for div in divs:
                for athletes_page in _board_page(entity["id"],
                                                 entity["name"], div):

                    all_athletes += athletes_page

        super().__init__(all_athletes)

