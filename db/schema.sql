CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    last_draw_at TIMESTAMP NOT NULL
)


CREATE TABLE pokemon (
    pokemon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    typ_1 VARCHAR(50) NOT NULL,
    typ_2 VARCHAR(50),
    rarity VARCHAR(20) NOT NULL,
    base_attack INTEGER NOT NULL,
    base_hp INTEGER NOT NULL,
    base_defense INTEGER NOT NULL,
    base_speed INTEGER NOT NULL,
    image_url VARCHAR(255)
)

CREATE TABLE user_pokemon (
    user_pokemon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pokemon_id INTEGER NOT NULL,
    draw_at TIMESTAMP NOT NULL,
    is_favorite BOOLEAN NOT NULL,
    nickname VARCHAR(50)
)

CREATE TABLE trade (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiator_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
)

CREATE TABLE trade_item (
    trade_id INTEGER PRIMARY KEY,
    user_pokemon_id INTEGER PRIMARY KEY,
    side VARCHAR(10) NOT NULL CHECK (side IN ('offered', 'requested')),
    PRIMARY KEY (trade_id, user_pokemon_id),
    FOREIGN KEY (trade_id) REFERENCES trade(trade_id),
    FOREIGN KEY (user_pokemon_id) REFERENCES user_pokemon(user_pokemon_id)
)