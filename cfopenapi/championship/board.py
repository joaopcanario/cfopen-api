from collections import namedtuple


divisions = {'1': 'Men (18-34)', '2': 'Women (18-34)',
             '3': 'Men (45-49)', '4': 'Women (45-49)',
             '5': 'Men (50-54)', '6': 'Women (50-54)',
             '7': 'Men (55-59)', '8': 'Women (55-59)',
             '9': 'Men (60+)', '10': 'Women (60+)',
             # '11': 'Team',
             '12': 'Men (40-44)', '13': 'Women (40-44)',
             '14': 'Boys (14-15)', '15': 'Girls (14-15)',
             '16': 'Boys (16-17)', '17': 'Girls (16-17)',
             '18': 'Men (35-39)', '19': 'Women (35-39)',

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

Ranking = namedtuple('Ranking', 'uuid name last_update athletes')

dumb_score = {"score": "0", "scoreDisplay": ""}


class Base(object):

    def __init__(self):
        super().__init__()

    def asdict(self):
        return vars(self)


class Score(Base):
    def __init__(self, ordinal, score, dumb):
        super().__init__()

        self.ordinal = ordinal

        self.score = score.get("score")

        self.time = score.get("time", 0)
        self.time = self.time if self.time else 0

        self.scoreDisplay = score.get("scoreDisplay")
        self.scoreDisplay = self.scoreDisplay if self.scoreDisplay else '--'

        self.scaled = ' - s' in self.scoreDisplay
        self.rank = 0

        self.dumb = dumb

    def _score_from_display(self):
        import re

        pattern = re.compile(r'( - s)|( reps)')
        self.scoreDisplay = pattern.sub("", self.scoreDisplay)

        if ':' in self.scoreDisplay:
            ddisplay = enumerate(reversed(self.scoreDisplay.split(":")))
            seconds = sum(int(x) * 60 ** i for i, x in ddisplay)

            return (max_reps[self.ordinal] / seconds) + max_reps[self.ordinal]

        return int(self.scoreDisplay)


class Athlete(Base):
    def __init__(self, competitor_id, competitor_name, affiliate_name,
                 division, profile_pic, scores, overall_score=0,
                 num_of_ordinals=5):
        super().__init__()

        # _profilepicsbucket = "https://profilepicsbucket.crossfit.com"

        self.competitorId = competitor_id
        self.competitorName = competitor_name
        self.affiliateName = affiliate_name

        self.divisionId = division
        self.division = divisions.get(self.divisionId)
        self.profilePicS3key = profile_pic
        self.overallScore = overall_score

        self.scores = [Score(ord, score, score.get("dumb", False)).asdict()
                       for ord, score in enumerate(scores)]

        for i in range(len(self.scores), num_of_ordinals):
            self.scores.append(Score(i, dumb_score, True).asdict())

    @classmethod
    def from_list(cls, athletes, ordinal):
        athletes_page = []

        for atl in athletes:
            scores = atl["scores"]

            atl = atl.get('entrant', atl)

            athlete = cls(atl["competitorId"],
                          atl["competitorName"],
                          atl["affiliateName"],
                          atl['divisionId'],
                          atl["profilePicS3key"],
                          scores,
                          num_of_ordinals=ordinal).asdict()

            athletes_page.append(athlete)

        return athletes_page


class Board(Base):
    def __init__(self, athletes, num_of_ordinals=5):
        super().__init__()

        self.athletes = athletes
        self.boards = {}
        self.ranks = []
        self.ordinals = num_of_ordinals

    def _sort(self, board):
        for w in range(0, self.ordinals):
            # RX
            rx = [athl for athl in board
                  if not athl["scores"][w]['scaled'] and
                     not athl["scores"][w]['scoreDisplay'] == '--' and
                     not athl["scores"][w]['dumb']]
            rx = sorted(rx, key=lambda x: (int(x["scores"][w]['score']),
                                           x["scores"][w]['time']),
                        reverse=True)

            # SCALE
            scale = [athl for athl in board
                     if athl["scores"][w]['scaled'] and
                        not athl["scores"][w]['scoreDisplay'] == '--' and
                        not athl["scores"][w]['dumb']]
            scale = sorted(scale, key=lambda x: (int(x["scores"][w]['score']),
                                                 x["scores"][w]['time']),
                           reverse=True)

            # NOT PERFORMED
            not_performed = [athl for athl in board
                             if athl["scores"][w]['scoreDisplay'] == '--' and
                                not athl["scores"][w]['dumb']]

            self._update_athletes_rank(rx + scale + not_performed, w)

        # OVERALL SCORE
        for athlete in board:
            athlete["overallScore"] = sum([athlete['scores'][w]["rank"]
                                           for w in range(0, self.ordinals)])

        return sorted(board, key=lambda x: x['overallScore'])

    def _update_athletes_rank(self, all_athletes, score):
        prev_rank = 1
        prev_score = (0, 0)

        for position, athlete in enumerate(all_athletes):
            atl_wod = athlete["scores"][score]
            rank = position + 1

            actual_score = (atl_wod["score"], atl_wod["time"])

            if actual_score == prev_score:
                rank = prev_rank
            else:
                prev_rank = rank

            prev_score = (atl_wod["score"], atl_wod["time"])
            atl_wod["rank"] = rank

    def generate_ranks(self, uuid):
        from datetime import datetime

        for division_id, division in divisions.items():
            athletes = [athlete for athlete in self.athletes
                        if athlete['division'] in division]

            board = Athlete.from_list(athletes, self.ordinals)

            if division_id in ["Masculino", "Feminino"]:
                division = division_id

            board = self._sort(board)
            self.boards[division] = board

            rankg_uuid = f"{uuid}_{division}"
            last_update = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')

            ranking = Ranking(rankg_uuid, division, last_update, board)
            self.ranks.append(ranking)


class CFGamesBoard(Board):
    def __init__(self, entities, ordinals=5):
        divs = [i for i, _ in divisions.items()
                if i not in ["Masculino", "Feminino"]]

        all_athletes = []

        for e in entities:
            for div in divs:
                for athletes_page in self._fetch(e["id"], div, ordinals):
                    all_athletes += athletes_page

        super().__init__(all_athletes, ordinals)

    def _fetch(self, entity, division, ordinal):
        '''
        Fetch athletes from specific box (entity) and division
        '''
        from .external import load_from_api

        page, total_pages = 1, 1

        while page <= total_pages:
            athletes, total_pages = load_from_api(entity, page, division)
            page += 1

            athletes_page = Athlete.from_list(athletes, ordinal)

            yield [athlete for athlete in athletes_page
                   if athlete["divisionId"] == division]
