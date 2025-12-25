#!/usr/bin/env python3
"""
Fetch complete history for ALL NFL players from Sleeper API.
Exports data to JSON and CSV formats for easy import into other systems.
Organizes data into season-specific folders (e.g. 2023/, 2024/).
"""

import argparse
import json
import csv
import os
import time
import datetime
from typing import Dict, Any, List
from sleeper_wrapper import Stats, Players

def setup_args():
    parser = argparse.ArgumentParser(description="Fetch complete NFL player history from Sleeper")
    parser.add_argument("--start-year", type=int, default=2010, help="Start year (default: 2010)")
    parser.add_argument("--end-year", type=int, default=datetime.datetime.now().year, help="End year (default: current year)")
    parser.add_argument("--output-dir", type=str, default="nfl_data_export", help="Root output directory")
    parser.add_argument("--format", type=str, choices=["json", "csv", "both"], default="both", help="Output format")
    return parser.parse_args()

def save_json(data: Any, filepath: str):
    """Helper to save data to JSON file"""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def save_players_csv(players: Dict, filepath: str):
    """Helper to save players metadata to CSV"""
    headers = ["player_id", "full_name", "position", "team", "age", "years_exp", "college", "fantasy_positions"]
    
    with open(filepath, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for pid, p_data in players.items():
            # Handle potential None values
            exp = p_data.get('years_exp')
            if exp is None: exp = 0
            
            fantasy_pos = ",".join(p_data.get('fantasy_positions', []) or [])
            
            row = [
                pid,
                p_data.get('full_name'),
                p_data.get('position'),
                p_data.get('team'),
                p_data.get('age'),
                exp,
                p_data.get('college'),
                fantasy_pos
            ]
            writer.writerow(row)

def save_stats_csv(stat_type: str, year: int, stats_data: Dict, players: Dict, filepath: str):
    """Helper to save either season or weekly stats to CSV"""
    
    # 1. Collect all potential headers dynamically
    all_keys = set()
    
    if stat_type == "season":
        # Data structure: { player_id: stats_dict }
        for p_stats in stats_data.values():
            all_keys.update(p_stats.keys())
    elif stat_type == "weekly":
        # Data structure: { week: { player_id: stats_dict } }
        for week_data in stats_data.values():
            for p_stats in week_data.values():
                all_keys.update(p_stats.keys())
                
    stat_headers = sorted(list(all_keys))
    
    # Base headers depend on type
    if stat_type == "season":
        base_headers = ["year", "player_id", "player_name", "team", "position"]
    else:
        base_headers = ["year", "week", "player_id", "player_name", "team", "position"]

    with open(filepath, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(base_headers + stat_headers)
        
        if stat_type == "season":
            for pid, stats in stats_data.items():
                p_info = players.get(pid, {})
                row = [
                    year,
                    pid,
                    p_info.get("full_name", "Unknown"),
                    p_info.get("team", "N/A"),
                    p_info.get("position", "N/A")
                ]
                for k in stat_headers:
                    row.append(stats.get(k, 0))
                writer.writerow(row)
                
        elif stat_type == "weekly":
            # Loop through sorted weeks
            for week in sorted(stats_data.keys()):
                week_stats_map = stats_data[week]
                for pid, stats in week_stats_map.items():
                    p_info = players.get(pid, {})
                    row = [
                        year,
                        week,
                        pid,
                        p_info.get("full_name", "Unknown"),
                        p_info.get("team", "N/A"),
                        p_info.get("position", "N/A")
                    ]
                    for k in stat_headers:
                        row.append(stats.get(k, 0))
                    writer.writerow(row)


def process_year(year: int, all_players: Dict, output_root: str, fmt: str):
    """Process a single year: fetch stats, create folder, save files."""
    stats_api = Stats()
    
    # Create year directory
    year_dir = os.path.join(output_root, str(year))
    os.makedirs(year_dir, exist_ok=True)
    
    print(f"\n📅 Processing {year} Season -> Saving to {year_dir}/")
    
    # --- 1. Season Totals ---
    print(f"   Fetching season totals...")
    season_totals = {}
    try:
        # User primarily wants regular season for "history" typically
        reg_stats = stats_api.get_all_stats("regular", year)
        if reg_stats:
            season_totals = reg_stats
            print(f"     ✓ Regular season: {len(reg_stats)} records")
        else:
            print(f"     ⚠️ No regular season stats found")
    except Exception as e:
        print(f"     ❌ Error fetching regular season stats: {e}")

    # --- 2. Weekly Stats ---
    print(f"   Fetching weekly stats (Weeks 1-18)...")
    weekly_stats = {} # { week_num: { player_id: stats } }
    max_weeks = 18
    for week in range(1, max_weeks + 1):
        try:
            w_stats = stats_api.get_week_stats("regular", year, week)
            if w_stats:
                weekly_stats[week] = w_stats
                print(f"     Week {week}: {len(w_stats)} records", end="\r")
        except Exception as e:
            pass # Silent fail for specific weeks (e.g. future weeks)
    print("") # Newline

    # --- 3. Save Files ---
    
    # Need player metadata in this folder? 
    # Yes, self-contained folders are best.
    if fmt in ["json", "both"]:
        print(f"   💾 Saving JSON...")
        save_json(all_players, os.path.join(year_dir, "players_metadata.json"))
        save_json(season_totals, os.path.join(year_dir, "season_stats.json"))
        save_json(weekly_stats, os.path.join(year_dir, "weekly_stats.json"))

    if fmt in ["csv", "both"]:
        print(f"   📊 Saving CSV...")
        save_players_csv(all_players, os.path.join(year_dir, "players.csv"))
        if season_totals:
            save_stats_csv("season", year, season_totals, all_players, os.path.join(year_dir, "season_stats.csv"))
        if weekly_stats:
            save_stats_csv("weekly", year, weekly_stats, all_players, os.path.join(year_dir, "weekly_stats.csv"))

def main():
    args = setup_args()
    
    print(f"🚀 Starting bulk fetch for years {args.start_year}-{args.end_year}")
    
    # 1. Fetch Player Metadata ONE TIME at the start
    # (Checking if we should fetch strictly for that year? Sleeper mostly gives current players + retired. 
    #  Fetching once is fine/efficient.)
    print("\n1️⃣  Fetching player metadata...")
    players_api = Players()
    all_players = players_api.get_all_players("nfl")
    print(f"   ✓ Retrieved {len(all_players)} players")
    
    # 2. Loop Years
    for year in range(args.start_year, args.end_year + 1):
        process_year(year, all_players, args.output_dir, args.format)
        
    print("\n🎉 Done! Data download complete.")

if __name__ == "__main__":
    main()
