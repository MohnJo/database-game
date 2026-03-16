# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is this project?
A Pokémon collecting game built as a learning project. Users draw random Pokémon
on a cooldown timer, manage their collection, and trade with other users.
Inspired by the Discord bot Mudae. For public release, Pokémon will be replaced
with original creatures (see roadmap V3.0).

## Tech Stack
- Python 3 + sqlite3 (V0.1)
- SQLite as local database
- PokéAPI (pokeapi.co) as data source
- Git + GitHub (MohnJo/database-game)

## Current Status (V0.1 — CLI Prototype)
- [x] Schema designed (5 tables: user, pokemon, user_pokemon, trade, trade_item)
- [x] schema.sql written and pushed to GitHub
- [x] Python script: create DB from schema.sql (`scripts/init_db.py`)
- [ ] Python script: import Pokémon from PokéAPI
- [ ] CLI draw mechanic: draw Pokémon and display collection

## Coding Conventions
- All code, comments, commit messages, and docs in English
- Variable and function names: snake_case
- Each file starts with a brief docstring explaining its purpose
- No over-engineering: keep it simple and readable, learning comes first
- Commits should be small and descriptive

## Technical Notes
- SQLite database file: db/dbg.db (NOT committed to Git — in .gitignore)
- No external dependencies except `requests` (for PokéAPI)
- The developer is a beginner — code should be well-commented and easy to follow
- Architecture decisions are documented in Notion (ADR page)

## Database Schema (5 tables)
- `user` — registered users
- `pokemon` — Pokémon templates (name, types, stats, rarity, image_url)
- `user_pokemon` — individual drawn instances (links user + pokemon, has nickname, is_favorite, drawn_at)
- `trade` — trade sessions between two users (status tracking)
- `trade_item` — items in a trade (composite PK: trade_id + user_pokemon_id, side: offered/requested)