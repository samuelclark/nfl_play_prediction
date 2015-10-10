import nflgame

class NFLGames(object):
    def __init__(self):
        pass

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
        """Fatten game info for home and away teams into a dicktionary.

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
            flat_plays.append(flat_play)
        return flat_plays

    def gather_all_info_for_all_plays(self, game):
        all_plays = []
        game_info = self.parse_game(game)
        for drive in game.drives:
            drive_info = self._flatten_drive(drive)
            drive_plays = self._flatten_plays(drive)
            for play_info in drive_plays:
                combined = {}
                combined.update(game_info)
                print " game ", combined.keys()
                combined.update(drive_info)
                print " drive ", combined.keys()
                combined.update(play_info)
                print " play ", combined.keys()
                all_plays.append(combined)
        return all_plays









nflgames = NFLGames()
week1_2013_games = nflgames.get_games_by_year(2013, 1)
g = week1_2013_games[0]

game_info = nflgames.gather_all_info_for_all_plays(g)
