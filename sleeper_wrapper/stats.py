import logging
from typing import Union

from sleeper_wrapper.base_api import BaseApi
from sleeper_wrapper.players import Players

logger = logging.getLogger(__name__)

warning_message = "The Stats API is no longer included in Sleeper's documentation, therefore we cannot guarantee that this class will continue working."

class Stats(BaseApi):
	"""Retrieves stats and projections from Sleeper's stats provider.

	Can retrieve stats and projections for Sleeper, though it is no longer
	officially documented and supported. Both stats and projections include
	box score and detailed stats as well as rollups to fantasy scores in
	standard scoring formats (standard, ppr, half ppr).
	"""

	def __init__(self):
		"""Initializes the instance for getting the stats."""
		logger.warn(warning_message)
		self._base_url = "https://api.sleeper.app/v1/stats/{}".format("nfl")
		self._projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")

	def get_all_stats(self, season_type: str, season: Union[str, int]) -> dict:
		"""Retrieves all statistics for the given season.

		It supports detailed data going back until 2010 before only providing
		ranks for the various scoring formats. The detailed data contains information
		such as passing yards per attempt, field goal makes and misses by 10 yard
		buckets, snaps played, red zone statistics, and more.

		Arguments:
		  season_type: str
		    The type of season for pulling the stats. Supports "regular", "pre",
		    and "post".
		  season: Union[str, int]
		    The year of the season for pulling the stats.

		Returns:
		  A dictionary with each player and their statistics for the season.
		"""
		# season_type: "regular" works..."reg", "regular_season", "playoffs", and "preseason" don't seem to work
		return self._call("{}/{}/{}".format(self._base_url, season_type, season))

	def get_week_stats(self, season_type: str, season: Union[str, int], week: str) -> dict:
		"""Retrieves all statistics for the given season and week.

		It supports detailed data going back until 2010 before only providing
		ranks for the various scoring formats. The detailed data contains information
		such as passing yards per attempt, field goal makes and misses by 10 yard
		buckets, snaps played, red zone statistics, and more.

		Arguments:
		  season_type: str
		    The type of season for pulling the stats. Supports "regular", "pre",
		    and "post".
		  season: Union[str, int]
		    The year of the season for pulling the stats.
		  week: Union[str, int]
		    The week of the season for pulling the stats.

		Returns:
		  A dictionary with each player and their statistics for the season's week.
		"""
		return self._call("{}/{}/{}/{}".format(self._base_url, season_type, season, week))

	def get_all_projections(self, season_type: str, season: Union[str, int]) -> dict:
		"""Retrieves all projections for the given season.

		It supports data going back until 2018 and contains information such as
		passing yards per attempt, field goal makes and misses by 10 yard buckets,
		ADP, games played, and more.

		Arguments:
		  season_type: str
		    The type of season for pulling the projections. Supports "regular",
		    "pre", and "post".
		  season: Union[str, int]
		    The year of the season for pulling the projections.

		Returns:
		  A dictionary with each player and their projections for the year.
		"""
		return self._call("{}/{}/{}".format(self._projections_base_url, season_type, season))

	def get_week_projections(self, season_type: str, season: Union[str, int], week: str) -> dict:
		"""Retrieves all projections for the given season and week.

		It supports data going back until 2018 and contains information such as
		passing yards per attempt, field goal makes and misses by 10 yard buckets,
		ADP, games played, and more.

		Arguments:
		  season_type: str
		    The type of season for pulling the projections. Supports "regular", 
		    "pre", and "post".
		  season: Union[str, int]
		    The year of the season for pulling the projections.
		  week: Union[str, int]
		    The week of the season for pulling the projections.

		Returns:
		  A dictionary with each player and their projections for the year.
		"""
		return self._call("{}/{}/{}/{}".format(self._projections_base_url, season_type, season, week))

	def get_player_week_stats(self, stats: dict, player_id: str) -> Union[dict, None]:
		"""Gets a player's stats or projections from the given dictionary.

		Arguments:
		  stats: dict
		    Either stats or projections returned by the API. Can be for the whole
		    season or a single week.
		  player_id: str
		    The ID for the player of interest.

		Returns:
		  A dictionary of the player's stats or projections for the time period
		  associated with the dictionary provided to the function.
		"""

		return stats.get(player_id, None)


	def get_player_week_score(self, stats: dict, player_id: str) -> Union[dict, None]:
		"""Retrieves a player's points scored for the primary scoring formats.

		Arguments:
		  stats: dict
		    Either stats or projections returned by the API. Can be for the whole
		    season or a single week.
		  player_id: str
		    The ID for the player of interest.

		Returns:
		  A dictionary with the points scored for standard, PPR, and half PPR
		  scoring formats.
		"""
		result_dict = {}
		player_stats = stats.get(player_id, None)

		if player_stats:
			result_dict["pts_ppr"] = player_stats.get("pts_ppr", None)
			result_dict["pts_std"] = player_stats.get("pts_std", None)
			result_dict["pts_half_ppr"] = player_stats.get("pts_half_ppr", None)

		return result_dict

	def get_player_complete_history(
		self, 
		player_id: str = None, 
		player_name: str = None,
		start_season: int = 2010,
		end_season: int = None,
		sport: str = "nfl",
		season_types: list = None
	) -> dict:
		"""Retrieves complete historical data for a player across all seasons and games.

		Fetches all available statistics for a player including:
		- Player information
		- Season totals for each season
		- Week-by-week game statistics

		Arguments:
		  player_id: str
		    The player ID. If not provided, will search by player_name.
		  player_name: str
		    The player's full name (e.g., "Josh Allen"). Used to find player_id
		    if player_id is not provided.
		  start_season: int
		    The first season to retrieve data for. Defaults to 2010 (earliest
		    available detailed stats).
		  end_season: int
		    The last season to retrieve data for. Defaults to current year if None.
		  sport: str
		    The sport. Options include "nfl", "nba", and "lcs". Defaults to "nfl".
		  season_types: list
		    List of season types to retrieve. Defaults to ["regular", "pre", "post"].
		    Options: "regular", "pre", "post".

		Returns:
		  A dictionary containing:
		  - "player_info": Player biographical information
		  - "seasons": Dictionary keyed by season year, each containing:
		    - "season_totals": Season aggregate stats
		    - "weeks": Dictionary keyed by week number, each containing game stats
		"""
		import datetime
		
		# Default values
		if end_season is None:
			end_season = datetime.datetime.now().year
		if season_types is None:
			season_types = ["regular", "pre", "post"]
		
		# Get player ID if not provided
		if player_id is None:
			if player_name is None:
				raise ValueError("Either player_id or player_name must be provided")
			
			players = Players()
			all_players = players.get_all_players(sport=sport)
			
			# Search for player by name (case-insensitive)
			player_id = None
			search_name = player_name.lower().strip()
			for pid, p_info in all_players.items():
				if p_info.get("full_name", "").lower() == search_name:
					player_id = pid
					break
            
			if player_id is None:
				raise ValueError(f"Player '{player_name}' not found")
		
		# Get player information
		players = Players()
		all_players = players.get_all_players(sport=sport)
		player_info = all_players.get(player_id, {})
		
		if not player_info:
			raise ValueError(f"Player ID '{player_id}' not found")
		
		# Structure to hold all data
		result = {
			"player_info": player_info,
			"player_id": player_id,
			"seasons": {}
		}
		
		# Iterate through each season
		for season in range(start_season, end_season + 1):
			season_data = {
				"season_totals": {},
				"weeks": {}
			}
			
			# Get season totals for each season type
			for season_type in season_types:
				try:
					all_stats = self.get_all_stats(season_type, season)
					player_season_stats = all_stats.get(player_id)
					if player_season_stats:
						season_data["season_totals"][season_type] = player_season_stats
				except Exception as e:
					logger.debug(f"No {season_type} stats for {season}: {e}")
			
			# Get week-by-week stats for regular season (weeks 1-18)
			# Try weeks 1-18, but handle cases where fewer weeks exist
			for week in range(1, 19):
				try:
					week_stats = self.get_week_stats("regular", season, week)
					player_week_stats = week_stats.get(player_id)
					if player_week_stats:
						season_data["weeks"][week] = player_week_stats
				except Exception as e:
					# If we get an error, likely no more weeks exist for this season
					logger.debug(f"No week {week} stats for {season}: {e}")
					# Continue trying other weeks
			
			# Only add season if we have any data
			if season_data["season_totals"] or season_data["weeks"]:
				result["seasons"][season] = season_data
		
		return result

	def get_all_players_with_stats(self, season_type: str, season: Union[str, int], sport: str = "nfl") -> dict:
		"""Retrieves all players and their statistics for the given season.

		Combines player information (from Players API) with their statistics
		(from Stats API) into a single dictionary. Each player entry contains
		both their biographical/team information and their season statistics.

		Arguments:
		  season_type: str
		    The type of season for pulling the stats. Supports "regular", "pre",
		    and "post".
		  season: Union[str, int]
		    The year of the season for pulling the stats.
		  sport: str
		    The sport to retrieve the players. Options include "nfl",
		    "nba", and "lcs". Defaults to "nfl".

		Returns:
		  A dictionary with each player ID as the key, and the value containing
		  both player information and their statistics for the season. Players
		  without stats will still be included with their player info but no
		  stats data.
		"""
		# Get all players
		players = Players()
		all_players = players.get_all_players(sport=sport)
		
		# Get all stats for the season
		all_stats = self.get_all_stats(season_type, season)
		
		# Combine players with their stats
		players_with_stats = {}
		for player_id, player_info in all_players.items():
			players_with_stats[player_id] = {
				**player_info,  # Include all player information
				"stats": all_stats.get(player_id, {})  # Add stats if available
			}
		
		return players_with_stats

