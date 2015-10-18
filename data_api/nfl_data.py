import nflgame

class NFLGames(object):
    def __init__(self):
        self.scr_summary = None
        self.current_score = None

    def get_games_by_year(self, year, week=None):
        """Returns all games for a given year.

        Args:
            year (int) : year to get games from
            week (Optional[int]) : if week is specified, retrieve games just
                from week
        """
        if week:
            games = nflgame.games(year, week=week)
        else:
            games = nflgames.games(year)
        return games

    def parse_game(self, game):
        """Flatten game info for home and away teams into a dictionary.

        Args:
            game (nflgame.game.Game) : instance of nfl game

        Returns:
            game_info (dict) : flattend game info
        """
        game_info = {}
        game_info.update(game.schedule)
        game_info['nflgame_id'] = game.gamekey
        game_info['winner'] = game.winner
        game_info['loser'] = game.loser
        game_info['score_home'] = game.score_home
        game_info['score_away'] = game.score_away
        game_info.update(self._add_team_stats(game.stats_home, 'home'))
        game_info.update(self._add_team_stats(game.stats_away, 'away'))
        game_info.update(self._add_quarter_scores(game, 'home'))
        game_info.update(self._add_quarter_scores(game, 'away'))
        return game_info

    def _add_quarter_scores(self, game, key):
        """get quarterly scores, add them to a dictionary
        Args:
            game (nflgame.game.Game) : game instance
            key (str) : 'home' or 'away'
        """
        quarters = ['q1', 'q2', 'q3', 'q4', 'q5']
        quarter_scores = {}
        for quarter in quarters:
            score_key = "score_{0}_{1}".format(key, quarter)
            quarter_scores[score_key] = getattr(game, score_key)
        return quarter_scores


    def _add_team_stats(self, stats, key):
        """flatten team stats and prepend keys with `key`.
        Args:
            stats (OrderedDict) : team stats
            key (str) : 'home' or 'away'

        Returns:
            flat_stats (dict) : flattend team stats with modified key
        """
        flat_stats = {}
        for k, v in stats.__dict__.iteritems():
            if k == 'pos_time':
                v = v.total_seconds()
            stat_key = "game_{0}_{1}".format(key, k)
            flat_stats[stat_key] = v
        return flat_stats

    def _flatten_drive(self, drive):
        flat_drive = {}
        for k, v in drive.__dict__.iteritems():
            if k == 'pos_time':
                v = v.total_seconds()
            elif k in ['field_start', 'field_end']:
                if v:
                    v = v.offset
            elif k in ['time_start', 'time_end']:
                v = v.__dict__
                for each in v:
                    flat_drive["drive_{0}_{1}".format(k, each)] = v[each]
                continue
            elif k in ['_Drive__plays', 'plays', 'game']:
                continue

            flat_drive["drive_{0}".format(k)] = v
        return flat_drive

    def _flatten_plays(self, drive):
        plays = [d for d in drive.plays]
        exclude_keys = ['players', 'events', 'drive', 'data', '_stats', '_Play__players']
        flat_plays = []
        for p in plays:
            flat_play = {}
            play_info = p.__dict__
            for each, val in play_info.iteritems():
                if each in exclude_keys:
                    continue
                if each == 'time':
                    if val:
                        val = val.__dict__
                        val.pop('_GameClock__qtr')
                        for i, v in val.items():
                            k = "play_{}".format(i)
                            flat_play[k] = v
                    continue

                if each == 'yardline':
                    if val:
                        val = val.offset

                k = "play_{}".format(each)
                flat_play[k] = val
            playid = str(p.playid)
            if playid in self.scr_summary:
                result = self.scr_summary[playid]
                team = result['team']
                score_type = result['type']
                desc = result['desc']
                if score_type == 'TD':
                    self.current_score[team] += 6
                    if 'kick is good' in desc:
                        self.current_score[team] += 1
                    else:
                        has_2point_info = desc.split("(")
                        if len(has_2point_info) > 1:
                            two_point_info = has_2point_info[1].split(")")[0].split(" ")
                            two_point = True
                            for each in [u"failed,", "failed", "blocked", "missed", "aborted"]:
                                if each in two_point_info:
                                    two_point = False
                            if two_point:
                                if 'run' in two_point_info or 'pass' in two_point_info:
                                    self.current_score[team] += 2


                elif score_type == 'FG':
                    self.current_score[team] += 3

                elif score_type == 'SAF':
                    self.current_score[team] += 2
                else:
                    print "WARNING found play", team, score_type, desc
            for team, score in self.current_score.items():
                if team == drive.team:
                    flat_play['score_offense'] = score
                else:
                    flat_play['score_defense'] = score
            flat_plays.append(flat_play)
        return flat_plays

    def gather_all_info_for_all_plays(self, game):
        self.scr_summary = game.data['scrsummary']
        self.current_score = {game.home: 0, game.away: 0}
        all_plays = []
        game_info = self.parse_game(game)
    #     print game
        fail = False
        for drive in game.drives:
            drive_info = self._flatten_drive(drive)
            drive_plays = self._flatten_plays(drive)

            for play_info in drive_plays:
                combined = {}
                combined.update(game_info)
                combined.update(drive_info)
                combined.update(play_info)
                all_plays.append(combined)


        if self.current_score[game.home] != game.score_home:
            fail = True
        if self.current_score[game.away] != game.score_away:
            fail = True
        if fail:
            print "miss matched scores ", game.eid

        return all_plays






"""
In [18]: with open("nflplays.csv", 'w') as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for p in all_p:
        w.writerow(p)
   ....:
"""


nflgames = NFLGames()


all_games = []
WEEKS = 17
for y in [2011,2012,2013]:
    for i in range(1, WEEKS):
        week_games = nflgames.get_games_by_year(y, i)
        for game in week_games:
            game_info = nflgames.gather_all_info_for_all_plays(game)
            all_games.append(game_info)

print len(all_games)
