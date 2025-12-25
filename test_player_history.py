#!/usr/bin/env python3
"""Test script to fetch complete player history (all seasons and all games)."""

from sleeper_wrapper import Stats
import json

def main():
    print("Fetching complete history for Josh Allen...")
    print("=" * 60)
    
    # Create Stats instance
    stats = Stats()
    
    try:
        # Get complete history for Josh Allen
        # Can use either player_id="4984" or player_name="Josh Allen"
        print("\n1. Fetching complete player history...")
        print("   (This may take a few minutes as it fetches all seasons and weeks)")
        
        # Using player_id for Josh Allen (QB, Buffalo Bills)
        # You can also use player_name="Josh Allen" but there might be multiple players
        player_history = stats.get_player_complete_history(
            player_id="4984",  # Josh Allen (QB, BUF)
            start_season=2018,  # Josh Allen's rookie year
            end_season=2025,
            sport="nfl"
        )
        
        print(f"\n2. Data retrieved successfully!")
        print(f"   Player: {player_history['player_info'].get('full_name')}")
        print(f"   Player ID: {player_history['player_id']}")
        print(f"   Seasons with data: {len(player_history['seasons'])}")
        
        # Show summary for each season
        print("\n3. Season Summary:")
        print("-" * 60)
        for season, season_data in sorted(player_history['seasons'].items()):
            season_totals = season_data.get('season_totals', {})
            weeks = season_data.get('weeks', {})
            
            print(f"\n{season} Season:")
            if 'regular' in season_totals:
                reg_stats = season_totals['regular']
                print(f"  Regular Season Totals:")
                print(f"    Games Played: {reg_stats.get('gp', 'N/A')}")
                print(f"    Passing Yards: {reg_stats.get('pass_yd', 'N/A')}")
                print(f"    Passing TDs: {reg_stats.get('pass_td', 'N/A')}")
                print(f"    Rushing Yards: {reg_stats.get('rush_yd', 'N/A')}")
                print(f"    Rushing TDs: {reg_stats.get('rush_td', 'N/A')}")
                print(f"    Fantasy Points (PPR): {reg_stats.get('pts_ppr', 'N/A')}")
            
            print(f"  Games Played: {len(weeks)} weeks")
            
            # Show a sample week
            if weeks:
                sample_week = list(weeks.keys())[0]
                week_data = weeks[sample_week]
                print(f"  Sample Week {sample_week}:")
                print(f"    Passing Yards: {week_data.get('pass_yd', 'N/A')}")
                print(f"    Passing TDs: {week_data.get('pass_td', 'N/A')}")
                print(f"    Fantasy Points: {week_data.get('pts_ppr', 'N/A')}")
        
        # Count total games
        total_games = sum(len(s['weeks']) for s in player_history['seasons'].values())
        print(f"\n4. Summary:")
        print(f"   Total seasons: {len(player_history['seasons'])}")
        print(f"   Total games: {total_games}")
        
        # Save to file
        print("\n5. Saving to file...")
        filename = f"josh_allen_complete_history.json"
        with open(filename, "w") as f:
            json.dump(player_history, f, indent=2)
        print(f"   ✓ Saved to {filename}")
        
        # Show structure
        print("\n6. Data Structure:")
        print("   - player_info: Player biographical data")
        print("   - player_id: Player ID")
        print("   - seasons: Dictionary keyed by year")
        print("     - season_totals: Season aggregate stats by type (regular/pre/post)")
        print("     - weeks: Week-by-week game stats (keyed by week number)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

