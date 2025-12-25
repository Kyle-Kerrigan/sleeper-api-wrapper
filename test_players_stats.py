#!/usr/bin/env python3
"""Test script to fetch all players with their stats for 2025 week 16."""

from sleeper_wrapper import Stats
import json

def main():
    print("Fetching all players with stats for 2025 week 16...")
    print("=" * 60)
    
    # Create Stats instance
    stats = Stats()
    
    # Get all players with stats for 2025 week 16
    # Note: Using "regular" season type - adjust if needed
    try:
        print("\n1. Fetching all players...")
        players_with_stats = stats.get_all_players_with_stats(
            season_type="regular",
            season=2025,
            sport="nfl"
        )
        
        print(f"   ✓ Retrieved {len(players_with_stats)} players")
        
        # Get week 16 stats
        print("\n2. Fetching week 16 stats...")
        week_stats = stats.get_week_stats(
            season_type="regular",
            season=2025,
            week=16
        )
        
        print(f"   ✓ Retrieved stats for {len(week_stats)} players in week 16")
        
        # Combine week 16 stats with player data
        print("\n3. Combining player data with week 16 stats...")
        players_with_week_stats = {}
        for player_id, player_info in players_with_stats.items():
            players_with_week_stats[player_id] = {
                **player_info,
                "week_16_stats": week_stats.get(player_id, {})
            }
        
        print(f"   ✓ Combined data for {len(players_with_week_stats)} players")
        
        # Show a sample player
        print("\n4. Sample player data:")
        print("-" * 60)
        sample_player_id = list(players_with_week_stats.keys())[0]
        sample_player = players_with_week_stats[sample_player_id]
        
        print(f"Player ID: {sample_player_id}")
        print(f"Name: {sample_player.get('full_name', 'N/A')}")
        print(f"Position: {sample_player.get('position', 'N/A')}")
        print(f"Team: {sample_player.get('team', 'N/A')}")
        
        if sample_player.get('week_16_stats'):
            week_16 = sample_player['week_16_stats']
            print(f"\nWeek 16 Stats:")
            print(f"  Standard Points: {week_16.get('pts_std', 'N/A')}")
            print(f"  PPR Points: {week_16.get('pts_ppr', 'N/A')}")
            print(f"  Half PPR Points: {week_16.get('pts_half_ppr', 'N/A')}")
        else:
            print("\nNo week 16 stats available for this player")
        
        # Count players with week 16 stats
        players_with_stats_count = sum(
            1 for p in players_with_week_stats.values() 
            if p.get('week_16_stats')
        )
        print(f"\n5. Summary:")
        print(f"   Total players: {len(players_with_week_stats)}")
        print(f"   Players with week 16 stats: {players_with_stats_count}")
        
        # Optionally save to file
        print("\n6. Saving to file...")
        with open("players_week16_2025.json", "w") as f:
            json.dump(players_with_week_stats, f, indent=2)
        print("   ✓ Saved to players_week16_2025.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

