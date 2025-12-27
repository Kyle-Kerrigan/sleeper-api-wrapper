#!/usr/bin/env python3
"""Test script to fetch Tom Brady's complete history from Sleeper API."""

import json
from sleeper_wrapper import Stats, Players

def main():
    print("🏈 Fetching Tom Brady's Historical Data from Sleeper API")
    print("=" * 60)
    
    # First, find Tom Brady's player ID
    print("\n1. Finding Tom Brady's player ID...")
    players = Players()
    all_players = players.get_all_players("nfl")
    
    tom_brady_id = None
    tom_brady_info = None
    for pid, p_info in all_players.items():
        if p_info.get("full_name", "").lower() == "tom brady":
            tom_brady_id = pid
            tom_brady_info = p_info
            break
    
    if tom_brady_id:
        print(f"   ✓ Found Tom Brady: ID = {tom_brady_id}")
        print(f"   Position: {tom_brady_info.get('position')}")
        print(f"   Team: {tom_brady_info.get('team')}")
        print(f"   Years Experience: {tom_brady_info.get('years_exp')}")
        print(f"   College: {tom_brady_info.get('college')}")
    else:
        print("   ❌ Tom Brady not found in database!")
        return
    
    # Now fetch his complete history
    print("\n2. Fetching complete historical stats...")
    stats = Stats()
    
    # Test how far back data goes by trying from 1999 (Brady's draft year was 2000)
    years_with_data = []
    all_data = {}
    
    print("\n   Testing years 1999-2023 (Brady's career)...")
    for year in range(1999, 2024):
        try:
            season_stats = stats.get_all_stats("regular", year)
            brady_stats = season_stats.get(tom_brady_id)
            
            if brady_stats:
                years_with_data.append(year)
                all_data[year] = brady_stats
                
                # Show key stats
                gp = brady_stats.get('gp', 'N/A')
                pass_yd = brady_stats.get('pass_yd', 'N/A') 
                pass_td = brady_stats.get('pass_td', 'N/A')
                pts_ppr = brady_stats.get('pts_ppr', 'N/A')
                
                print(f"   {year}: GP={gp}, Pass Yds={pass_yd}, Pass TDs={pass_td}, PPR Pts={pts_ppr}")
        except Exception as e:
            pass  # No data for this year
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if years_with_data:
        print(f"\n✓ Found data for {len(years_with_data)} seasons")
        print(f"  Earliest season: {min(years_with_data)}")
        print(f"  Latest season: {max(years_with_data)}")
        print(f"  Years with data: {years_with_data}")
    else:
        print("❌ No historical data found for Tom Brady")
    
    # Also test weeks for earliest year with data
    if years_with_data:
        earliest_year = min(years_with_data)
        print(f"\n3. Testing week-by-week data for {earliest_year}...")
        weeks_with_data = []
        for week in range(1, 19):
            try:
                week_stats = stats.get_week_stats("regular", earliest_year, week)
                brady_week = week_stats.get(tom_brady_id)
                if brady_week:
                    weeks_with_data.append(week)
            except:
                pass
        
        print(f"   Weeks with data in {earliest_year}: {weeks_with_data}")
    
    # Save full data to file
    output = {
        "player_id": tom_brady_id,
        "player_info": tom_brady_info,
        "years_with_data": years_with_data,
        "earliest_season": min(years_with_data) if years_with_data else None,
        "latest_season": max(years_with_data) if years_with_data else None,
        "season_stats": all_data
    }
    
    with open("tom_brady_complete_history.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Complete data saved to tom_brady_complete_history.json")

if __name__ == "__main__":
    main()
