#!/usr/bin/env python3
"""Generate a Markdown guide for Pokémon Omega Ruby / Alpha Sapphire."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POKEDEX_FILE = ROOT / "data" / "pokedex.json"
MOVES_FILE = ROOT / "data" / "moves.json"
ABILITIES_FILE = ROOT / "data" / "abilities.json"
TYPES_FILE = ROOT / "data" / "types.json"
CATEGORIES_FILE = ROOT / "data" / "categories.json"
OUTPUT_FILE = ROOT / "docs" / "guide.md"


def format_moves_table(
    learnset: list[dict],
    moves_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
) -> str:
    header = (
        "| 等级 | 招式 | 特殊效果 | 属性 | 分类 | 类别 | 威力 | 命中 | PP | 表演 | 妨害 |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    rows = []
    for learn in learnset:
        move_id = learn["move_id"]
        if move_id not in moves_db:
            raise KeyError(f"Unknown move_id '{move_id}' in pokedex learnset.")

        move = moves_db[move_id]
        type_id = move["type_id"]
        if type_id not in types_db:
            raise KeyError(f"Unknown type_id '{type_id}' in moves database.")

        move_name = f"{move['name']['zh']}<br>{move['name']['en']}"
        type_name = f"<nobr>{types_db[type_id]['name']['zh']}</nobr>"
        category_id = move["category_id"]
        if category_id not in categories_db:
            raise KeyError(f"Unknown category_id '{category_id}' in moves database.")

        move_category = f"<nobr>{categories_db[category_id]['name']['zh']}</nobr>"
        contest_category = f"<nobr>{move.get('contest_category', '—')}</nobr>"
        rows.append(
            "| {level} | {move_name} | {effect} | {type_} | {category} | {contest_category} | {power} | {accuracy} | {pp} | {appeal} | {jam} |".format(
                level=learn["level"],
                move_name=move_name,
                effect=move.get("effect", ""),
                type_=type_name,
                category=move_category,
                contest_category=contest_category,
                power=move["power"],
                accuracy=move["accuracy"],
                pp=move["pp"],
                appeal=move["appeal"],
                jam=move["jam"],
            )
        )
    return header + "\n".join(rows)


def load_moves_db() -> dict[str, dict]:
    moves = json.loads(MOVES_FILE.read_text(encoding="utf-8"))
    return {move["id"]: move for move in moves}


def load_abilities_db() -> dict[str, dict]:
    abilities = json.loads(ABILITIES_FILE.read_text(encoding="utf-8"))
    return {ability["id"]: ability for ability in abilities}


def load_types_db() -> dict[str, dict]:
    types = json.loads(TYPES_FILE.read_text(encoding="utf-8"))
    return {pokemon_type["id"]: pokemon_type for pokemon_type in types}


def load_categories_db() -> dict[str, dict]:
    categories = json.loads(CATEGORIES_FILE.read_text(encoding="utf-8"))
    return {category["id"]: category for category in categories}


def format_ability(ability_id: str, abilities_db: dict[str, dict]) -> str:
    if ability_id not in abilities_db:
        raise KeyError(f"Unknown ability_id '{ability_id}' in pokedex abilities.")
    ability = abilities_db[ability_id]
    return f"{ability['name']['zh']} / {ability['name']['en']} - {ability['description']}"


def format_pokemon_types(entry: dict, types_db: dict[str, dict]) -> str:
    zh_types = []
    for raw_type in entry["types"]:
        if raw_type in types_db:
            zh_types.append(types_db[raw_type]["name"]["zh"])
            continue

        if "/" in raw_type:
            zh_types.append(raw_type.split("/", 1)[0])
            continue

        raise KeyError(f"Unknown type '{raw_type}' in pokedex entry #{entry['number']}.")
    return " / ".join(zh_types)


def render_pokemon(
    entry: dict,
    moves_db: dict[str, dict],
    abilities_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
) -> str:
    zh_types = format_pokemon_types(entry, types_db)
    abilities_lines = [
        f"- {format_ability(ability_id, abilities_db)}" for ability_id in entry["abilities"]
    ]
    lines = [
        f"### #{entry['number']} {entry['name']['zh']} / {entry['name']['en']} | {zh_types} | {entry['evolution']['condition']} -> {entry['evolution']['to']}",
        "",
        "**特性**：",
        *abilities_lines,
        "",
        "**招式表**",
        "",
        format_moves_table(entry["moves"], moves_db, types_db, categories_db),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    pokedex = json.loads(POKEDEX_FILE.read_text(encoding="utf-8"))
    moves_db = load_moves_db()
    abilities_db = load_abilities_db()
    types_db = load_types_db()
    categories_db = load_categories_db()

    sections = [
        "# 宝可梦 欧米伽红宝石／阿尔法蓝宝石 攻略 / Pokémon Omega Ruby & Alpha Sapphire Guide",
        "",
        "## 图鉴 / Pokédex",
        "",
        "> 本章节为首版骨架，展示图鉴条目结构。后续可扩展为完整全国图鉴与招式来源。",
        "",
    ]

    for pokemon in pokedex:
        sections.append(
            render_pokemon(pokemon, moves_db, abilities_db, types_db, categories_db)
        )

    OUTPUT_FILE.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
