"""
Yahoo Fantasy Sports MCP server.

Tools wrap yahoo_fantasy_api and return its plain dicts/lists (JSON-ready) directly.
Reads cover leagues, teams, rosters, matchups, players, stats, drafts, and transactions;
writes cover lineup changes, add/drop, waiver claims, and trade accept/reject. Works
across NFL/NHL/NBA/MLB -- the sport is implied by the league key, except list_leagues
which takes a game_code.

League/team keys are optional on most tools; see client.py for the defaulting rules.
"""

import datetime as dt

from mcp.server.fastmcp import FastMCP

from .client import client

mcp = FastMCP("yahoo")


def _time_frame(week, date):
    """Yahoo lineup/stat windows: a week number (NFL) or a calendar date (daily sports)."""
    if week is not None:
        return int(week)
    if date:
        return dt.date.fromisoformat(date)
    return None


# --- League reads -----------------------------------------------------------------


@mcp.tool()
def list_leagues(game_code: str, year: int | None = None) -> dict:
    """List the authenticated user's league keys for a sport.

    game_code is one of nfl, nhl, nba, mlb. year filters to a season (e.g. 2024).
    Returns the game id and the league keys (e.g. "449.l.365083") to pass to other tools.
    """
    game = client.game(game_code)
    # game_codes filters to this sport; without it Yahoo returns every game's leagues.
    return {
        "game_code": game_code,
        "game_id": game.game_id(),
        "league_keys": game.league_ids(year=year, game_codes=[game_code]),
    }


@mcp.tool()
def league_settings(league_key: str | None = None) -> dict:
    """League settings: scoring type, roster size, current/start/end week, FAAB, etc."""
    return client.league(league_key).settings()


@mcp.tool()
def league_standings(league_key: str | None = None) -> list:
    """League standings, ordered first place to last, with records and games back."""
    return client.league(league_key).standings()


@mcp.tool()
def league_teams(league_key: str | None = None) -> dict:
    """All teams in the league, keyed by team key, with managers and metadata."""
    return client.league(league_key).teams()


@mcp.tool()
def league_matchups(week: int | None = None, league_key: str | None = None) -> dict:
    """Raw scoreboard/matchup data for a week (defaults to the current week)."""
    return client.league(league_key).matchups(week)


@mcp.tool()
def league_draft_results(league_key: str | None = None) -> list:
    """Draft results: pick, round, team key, player id (and cost for auction leagues)."""
    return client.league(league_key).draft_results()


@mcp.tool()
def league_transactions(
    tran_types: str = "add,drop,trade",
    count: int = 25,
    league_key: str | None = None,
) -> list:
    """Recent transactions. tran_types is a comma list of add, drop, commish, trade."""
    return client.league(league_key).transactions(tran_types, str(count))


@mcp.tool()
def league_stat_categories(league_key: str | None = None) -> list:
    """The league's scoring stat categories (display name + position type)."""
    return client.league(league_key).stat_categories()


@mcp.tool()
def league_roster_positions(league_key: str | None = None) -> dict:
    """Roster position slots and counts (e.g. C, RW, BN, IR)."""
    return client.league(league_key).positions()


@mcp.tool()
def current_week(league_key: str | None = None) -> dict:
    """The league's current and final week numbers."""
    league = client.league(league_key)
    return {"current_week": league.current_week(), "end_week": league.end_week()}


# --- Player reads -----------------------------------------------------------------


@mcp.tool()
def free_agents(position: str, league_key: str | None = None) -> list:
    """Available free agents at a position (e.g. "C", "RW", "QB", or "B"/"P" for type)."""
    return client.league(league_key).free_agents(position)


@mcp.tool()
def waivers(position: str | None = None, league_key: str | None = None) -> list:
    """Players currently on waivers, optionally filtered by position."""
    return client.league(league_key).waivers(position)


@mcp.tool()
def taken_players(league_key: str | None = None) -> list:
    """All players currently rostered by some team in the league."""
    return client.league(league_key).taken_players()


@mcp.tool()
def player_details(player: str, league_key: str | None = None) -> list:
    """Look up players by name (search) or by numeric player id."""
    query = int(player) if player.isdigit() else player
    return client.league(league_key).player_details(query)


@mcp.tool()
def player_stats(
    player_ids: list[int],
    req_type: str = "season",
    week: int | None = None,
    date: str | None = None,
    season: int | None = None,
    league_key: str | None = None,
) -> list:
    """Stats for players. req_type is one of season, average_season, lastweek, lastmonth,
    date, week. Pass week (NFL), date (YYYY-MM-DD), or season as required by req_type.
    """
    parsed_date = dt.date.fromisoformat(date) if date else None
    return client.league(league_key).player_stats(
        player_ids, req_type, date=parsed_date, week=week, season=season
    )


@mcp.tool()
def percent_owned(player_ids: list[int], league_key: str | None = None) -> list:
    """Ownership percentage across the Yahoo player pool for the given player ids."""
    return client.league(league_key).percent_owned(player_ids)


# --- Team reads -------------------------------------------------------------------


@mcp.tool()
def my_team_key(league_key: str | None = None) -> str:
    """The authenticated user's own team key in the league."""
    return client.team_key(None, league_key)


@mcp.tool()
def team_details(team_key: str | None = None, league_key: str | None = None) -> dict:
    """Team metadata. Defaults to the authenticated user's team."""
    return client.team(team_key, league_key).details()


@mcp.tool()
def team_roster(
    week: int | None = None,
    date: str | None = None,
    team_key: str | None = None,
    league_key: str | None = None,
) -> list:
    """A team's roster with each player's selected position. Defaults to your team and
    today; pass week or date (YYYY-MM-DD) for a different point in time.
    """
    parsed_date = dt.date.fromisoformat(date) if date else None
    return client.team(team_key, league_key).roster(week=week, day=parsed_date)


@mcp.tool()
def team_matchup_opponent(
    week: int, team_key: str | None = None, league_key: str | None = None
) -> str:
    """The opponent team key a team faces in a given week. Defaults to your team."""
    return client.team(team_key, league_key).matchup(week)


@mcp.tool()
def proposed_trades(team_key: str | None = None, league_key: str | None = None) -> list:
    """Pending trade proposals involving a team, with their transaction keys."""
    return client.team(team_key, league_key).proposed_trades()


# --- Writes -----------------------------------------------------------------------


@mcp.tool()
def set_lineup(
    lineup: list[dict],
    week: int | None = None,
    date: str | None = None,
    team_key: str | None = None,
    league_key: str | None = None,
) -> dict:
    """Set a team's starting lineup. lineup is a list of {player_id, selected_position}
    (e.g. [{"player_id": 5981, "selected_position": "BN"}]). Provide week (NFL) or date
    (YYYY-MM-DD, daily sports). Defaults to the authenticated user's team.
    """
    time_frame = _time_frame(week, date)
    if time_frame is None:
        raise ValueError("Provide either week (NFL) or date (YYYY-MM-DD).")
    modified = [
        {"player_id": int(p["player_id"]), "selected_position": p["selected_position"]}
        for p in lineup
    ]
    client.team(team_key, league_key).change_positions(time_frame, modified)
    return {"status": "ok", "changed": len(modified)}


@mcp.tool()
def add_player(
    player_id: int, team_key: str | None = None, league_key: str | None = None
) -> dict:
    """Add a free agent to a team. Defaults to the authenticated user's team."""
    client.team(team_key, league_key).add_player(player_id)
    return {"status": "ok", "added": player_id}


@mcp.tool()
def drop_player(
    player_id: int, team_key: str | None = None, league_key: str | None = None
) -> dict:
    """Drop a player from a team. Defaults to the authenticated user's team."""
    client.team(team_key, league_key).drop_player(player_id)
    return {"status": "ok", "dropped": player_id}


@mcp.tool()
def add_and_drop_players(
    add_player_id: int,
    drop_player_id: int,
    team_key: str | None = None,
    league_key: str | None = None,
) -> dict:
    """Add one player and drop another in a single transaction."""
    client.team(team_key, league_key).add_and_drop_players(add_player_id, drop_player_id)
    return {"status": "ok", "added": add_player_id, "dropped": drop_player_id}


@mcp.tool()
def claim_player(
    player_id: int,
    faab: int | None = None,
    team_key: str | None = None,
    league_key: str | None = None,
) -> dict:
    """Claim a player off waivers, optionally with a FAAB bid (dollars)."""
    client.team(team_key, league_key).claim_player(player_id, faab=faab)
    return {"status": "ok", "claimed": player_id, "faab": faab}


@mcp.tool()
def claim_and_drop_players(
    add_player_id: int,
    drop_player_id: int,
    faab: int | None = None,
    team_key: str | None = None,
    league_key: str | None = None,
) -> dict:
    """Claim a waiver player and drop another in one transaction, optional FAAB bid."""
    client.team(team_key, league_key).claim_and_drop_players(
        add_player_id, drop_player_id, faab=faab
    )
    return {"status": "ok", "added": add_player_id, "dropped": drop_player_id, "faab": faab}


@mcp.tool()
def accept_trade(
    transaction_key: str,
    trade_note: str = "",
    team_key: str | None = None,
    league_key: str | None = None,
) -> dict:
    """Accept a pending trade by its transaction key (see proposed_trades)."""
    client.team(team_key, league_key).accept_trade(transaction_key, trade_note)
    return {"status": "ok", "accepted": transaction_key}


@mcp.tool()
def reject_trade(
    transaction_key: str,
    trade_note: str = "",
    team_key: str | None = None,
    league_key: str | None = None,
) -> dict:
    """Reject a pending trade by its transaction key (see proposed_trades)."""
    client.team(team_key, league_key).reject_trade(transaction_key, trade_note)
    return {"status": "ok", "rejected": transaction_key}
