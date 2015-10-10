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
            stat_key = "{0}_{1}".format(key, k)
            flat_stats[stat_key] = v
        return flat_stats

nflgames = NFLGames()
week1_2013_games = nflgames.get_games_by_year(2013, 1)
g = week1_2013_games[0]

game_info = [nflgames.parse_game(g) for g in week1_2013_games]
