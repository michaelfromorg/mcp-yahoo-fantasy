"""
Thin wrapper over yahoo_fantasy_api that owns authentication, object caching, and the
"which league/team?" defaults so the MCP tools stay one-liners.

Yahoo identifies things by key:
  - league key, e.g. "449.l.365083"   (the leading number is the game/season id)
  - team key,   e.g. "449.l.365083.t.5"

Most tools take an optional league_key/team_key. When omitted we fall back to the
$YAHOO_LEAGUE_KEY env var, and for team operations to the authenticated user's own team
in that league -- so a configured single-league setup needs no ids passed at all.
"""

import os

import yahoo_fantasy_api as yfa

from . import auth


class YahooClient:
    def __init__(self):
        self._sc = None
        self._games = {}
        self._leagues = {}

    @property
    def sc(self):
        if self._sc is None:
            self._sc = auth.session()
        return self._sc

    def game(self, game_code):
        if game_code not in self._games:
            self._games[game_code] = yfa.Game(self.sc, game_code)
        return self._games[game_code]

    def league(self, league_key=None):
        key = league_key or os.environ.get("YAHOO_LEAGUE_KEY")
        if not key:
            raise ValueError(
                "No league_key provided and YAHOO_LEAGUE_KEY is not set. "
                "Use list_leagues to find your league key."
            )
        if key not in self._leagues:
            self._leagues[key] = yfa.League(self.sc, key)
        return self._leagues[key]

    def team_key(self, team_key=None, league_key=None):
        """Resolve a team key, defaulting to the authenticated user's own team."""
        return team_key or self.league(league_key).team_key()

    def team(self, team_key=None, league_key=None):
        return yfa.Team(self.sc, self.team_key(team_key, league_key))


client = YahooClient()
