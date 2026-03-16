"""
import_pokemon.py — Fetches Pokémon data from PokéAPI and inserts it into the database.

Usage:
    python scripts/import_pokemon.py           # imports first 151 Pokémon
    python scripts/import_pokemon.py --limit 20  # imports first 20 Pokémon

Run from the project root directory.
"""

import sqlite3
import argparse
import requests
import sys
import os

# File paths (relative to the project root)
DB_PATH = "db/dbg.db"
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"


# ---------------------------------------------------------------------------
# Data fetching — PokéAPI-specific code is isolated here.
# To swap the data source later, replace these two functions only.
# ---------------------------------------------------------------------------

def fetch_pokemon_from_api(pokemon_id):
    """
    Fetches raw data for a single Pokémon from PokéAPI.
    Returns a dict with the raw API response, or None if the request failed.
    """
    url = f"{POKEAPI_BASE_URL}/{pokemon_id}"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print(f"  Warning: could not fetch Pokémon #{pokemon_id} (status {response.status_code})")
        return None

    return response.json()


def parse_pokemon(raw_data):
    """
    Extracts the relevant fields from a raw PokéAPI response dict.
    Returns a clean dict that matches our database schema.

    This function is the 'translation layer' between the API and our DB.
    If we ever switch to a different data source, only this function needs
    to change — the rest of the import logic stays the same.
    """
    # --- Name ---
    name = raw_data["name"]

    # --- Types ---
    # PokéAPI returns a list of type slots; slot 1 = primary, slot 2 = secondary
    types = raw_data["types"]
    type_1 = None
    type_2 = None
    for entry in types:
        if entry["slot"] == 1:
            type_1 = entry["type"]["name"]
        elif entry["slot"] == 2:
            type_2 = entry["type"]["name"]

    # --- Base stats ---
    # PokéAPI returns a list of stats; we pick out all six
    stats = {s["stat"]["name"]: s["base_stat"] for s in raw_data["stats"]}
    hp         = stats.get("hp", 0)
    attack     = stats.get("attack", 0)
    defense    = stats.get("defense", 0)
    sp_attack  = stats.get("special-attack", 0)
    sp_defense = stats.get("special-defense", 0)
    speed      = stats.get("speed", 0)

    # --- Sprite URLs ---
    sprites = raw_data.get("sprites", {})
    image_url       = sprites.get("front_default")
    shiny_image_url = sprites.get("front_shiny")

    return {
        "name":            name,
        "type_1":          type_1,
        "type_2":          type_2,
        "hp":              hp,
        "attack":          attack,
        "defense":         defense,
        "sp_attack":       sp_attack,
        "sp_defense":      sp_defense,
        "speed":           speed,
        "image_url":       image_url,
        "shiny_image_url": shiny_image_url,
    }


# ---------------------------------------------------------------------------
# Rarity logic — based on total base stats (hp + attack + defense + speed)
# ---------------------------------------------------------------------------

def assign_rarity(hp, attack, defense, sp_attack, sp_defense, speed):
    """
    Determines rarity based on BST (Base Stat Total — all 6 stats combined).

    BST < 400     → Common
    400–474       → Uncommon
    475–524       → Rare
    525–579       → Epic
    580+          → Legendary
    """
    bst = hp + attack + defense + sp_attack + sp_defense + speed

    if bst >= 580:
        return "Legendary"
    elif bst >= 525:
        return "Epic"
    elif bst >= 475:
        return "Rare"
    elif bst >= 400:
        return "Uncommon"
    else:
        return "Common"


# ---------------------------------------------------------------------------
# Database insertion
# ---------------------------------------------------------------------------

def insert_pokemon(cursor, pokemon):
    """
    Inserts a single parsed Pokémon dict into the pokemon table.
    pokemon must have: name, type_1, type_2, hp, attack, defense,
                       sp_attack, sp_defense, speed, image_url, shiny_image_url
    """
    rarity = assign_rarity(
        pokemon["hp"],
        pokemon["attack"],
        pokemon["defense"],
        pokemon["sp_attack"],
        pokemon["sp_defense"],
        pokemon["speed"],
    )

    cursor.execute(
        """
        INSERT INTO pokemon
            (name, typ_1, typ_2, rarity,
             base_hp, base_attack, base_defense,
             base_sp_attack, base_sp_defense, base_speed,
             image_url, shiny_image_url)
        VALUES
            (?, ?, ?, ?,
             ?, ?, ?,
             ?, ?, ?,
             ?, ?)
        """,
        (
            pokemon["name"],
            pokemon["type_1"],
            pokemon["type_2"],
            rarity,
            pokemon["hp"],
            pokemon["attack"],
            pokemon["defense"],
            pokemon["sp_attack"],
            pokemon["sp_defense"],
            pokemon["speed"],
            pokemon["image_url"],
            pokemon["shiny_image_url"],
        ),
    )


# ---------------------------------------------------------------------------
# Main import flow
# ---------------------------------------------------------------------------

def import_pokemon(limit):
    """
    Fetches `limit` Pokémon from the data source and inserts them into the DB.
    """
    # Make sure the database file exists
    if not os.path.exists(DB_PATH):
        print(f"Error: database not found at '{DB_PATH}'.")
        print("Please run 'python scripts/init_db.py' first.")
        sys.exit(1)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    success_count = 0
    skip_count = 0

    for i in range(1, limit + 1):
        # --- Fetch raw data from the API ---
        raw_data = fetch_pokemon_from_api(i)
        if raw_data is None:
            skip_count += 1
            continue

        # --- Parse into a clean dict ---
        pokemon = parse_pokemon(raw_data)

        # --- Progress indicator ---
        print(f"Importing {i}/{limit}: {pokemon['name']}...")

        # --- Insert into the database ---
        insert_pokemon(cursor, pokemon)
        success_count += 1

    # Save all inserts at once
    connection.commit()
    connection.close()

    # Summary
    print(f"\nDone! Imported {success_count} Pokémon into '{DB_PATH}'.")
    if skip_count > 0:
        print(f"Skipped {skip_count} Pokémon due to fetch errors.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # --- First, reset the database to a clean state ---
    print("Step 1: Initialising a fresh database...")
    # Import init_db so we can call it directly instead of spawning a subprocess
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from init_db import init_db
    init_db()
    print()

    # --- Parse command-line arguments ---
    parser = argparse.ArgumentParser(
        description="Import Pokémon from PokéAPI into the local database."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=151,
        help="Number of Pokémon to import (default: 151)",
    )
    args = parser.parse_args()

    # --- Run the import ---
    print(f"Step 2: Fetching {args.limit} Pokémon from PokéAPI...\n")
    import_pokemon(args.limit)
