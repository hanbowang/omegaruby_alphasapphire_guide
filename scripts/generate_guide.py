#!/usr/bin/env python3
"""Generate HTML guide for Pokémon Omega Ruby / Alpha Sapphire."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POKEDEX_FILE = ROOT / "data" / "pokedex.json"
MOVES_FILE = ROOT / "data" / "moves.json"
ABILITIES_FILE = ROOT / "data" / "abilities.json"
TYPES_FILE = ROOT / "data" / "types.json"
CATEGORIES_FILE = ROOT / "data" / "categories.json"
CONTEST_CATEGORIES_FILE = ROOT / "data" / "contest_categories.json"
OUTPUT_HTML_FILE = ROOT / "docs" / "index.html"


def format_moves_table(
    learnset: list[dict],
    moves_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
    contest_categories_db: dict[str, dict],
) -> str:
    header_cells = [
        "<nobr>等级</nobr>",
        "<nobr>招式</nobr>",
        "<nobr>特殊效果</nobr>",
        "<nobr>属性</nobr>",
        "<nobr>分类</nobr>",
        "<nobr>类别</nobr>",
        "<nobr>威力</nobr>",
        "<nobr>命中</nobr>",
        "<nobr>PP</nobr>",
        "<nobr>表演</nobr>",
        "<nobr>妨害</nobr>",
    ]
    lines = [
        "<table>",
        "<tr>" + "".join(f"<th>{cell}</th>" for cell in header_cells) + "</tr>",
    ]

    for learn in learnset:
        move_id = learn["move_id"]
        if move_id not in moves_db:
            raise KeyError(f"Unknown move_id '{move_id}' in pokedex learnset.")

        move = moves_db[move_id]
        type_id = move["type_id"]
        if type_id not in types_db:
            raise KeyError(f"Unknown type_id '{type_id}' in moves database.")

        category_id = move["category_id"]
        if category_id not in categories_db:
            raise KeyError(f"Unknown category_id '{category_id}' in moves database.")

        contest_category_id = move.get("contest_category_id")
        if contest_category_id is None:
            contest_category = "<nobr>—</nobr>"
        else:
            if contest_category_id not in contest_categories_db:
                raise KeyError(
                    f"Unknown contest_category_id '{contest_category_id}' in moves database."
                )
            contest_category = (
                f"<nobr>{contest_categories_db[contest_category_id]['name']['zh']}</nobr>"
            )

        cells = [
            learn["level"],
            f"<nobr>{move['name']['zh']}</nobr><br><nobr>{move['name']['en']}</nobr>",
            move.get("effect", ""),
            f"<nobr>{types_db[type_id]['name']['zh']}</nobr>",
            f"<nobr>{categories_db[category_id]['name']['zh']}</nobr>",
            contest_category,
            move["power"],
            move["accuracy"],
            move["pp"],
            move["appeal"],
            move["jam"],
        ]
        lines.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")

    lines.append("</table>")
    return "\n".join(lines)


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


def load_contest_categories_db() -> dict[str, dict]:
    contest_categories = json.loads(CONTEST_CATEGORIES_FILE.read_text(encoding="utf-8"))
    return {
        contest_category["id"]: contest_category for contest_category in contest_categories
    }


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
    pokedex_db: dict[str, dict],
    moves_db: dict[str, dict],
    abilities_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
    contest_categories_db: dict[str, dict],
) -> str:
    evolution = entry.get("evolution")
    evolution_text = None
    if evolution is not None:
        evo_target_number = evolution["to_number"]
        evo_target = pokedex_db.get(evo_target_number)
        if evo_target is None:
            evolution_to = f"#{evo_target_number}"
        else:
            evolution_to = (
                f"{evo_target['name']['zh']} / {evo_target['name']['en']}"
                f" (#{evo_target_number})"
            )
        evolution_text = f"{evolution['condition']} -> {evolution_to}"

    zh_types = format_pokemon_types(entry, types_db)
    title = f"#{entry['number']} {entry['name']['zh']} / {entry['name']['en']} | {zh_types}"
    if evolution_text is not None:
        title = f"{title} | {evolution_text}"

    abilities_html = "\n".join(
        f"<li>{format_ability(ability_id, abilities_db)}</li>" for ability_id in entry["abilities"]
    )

    lines = [
        f"<h3>{title}</h3>",
        "<p><strong>特性</strong>：</p>",
        "<ul>",
        abilities_html,
        "</ul>",
        "<p><strong>招式表</strong></p>",
        format_moves_table(
            entry["moves"],
            moves_db,
            types_db,
            categories_db,
            contest_categories_db,
        ),
    ]
    return "\n".join(lines)


def render_html(content_sections: list[str]) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang='zh-CN'>",
            "<head>",
            "  <meta charset='utf-8' />",
            "  <meta name='viewport' content='width=device-width, initial-scale=1' />",
            "  <title>ORAS Guide</title>",
            "  <style>",
            "    body { font-family: sans-serif; font-size: 14px; line-height: 1.35; margin: 1rem auto; max-width: 1100px; padding: 0 0.5rem; }",
            "    h1, h2, h3 { line-height: 1.25; margin: 0.6rem 0; }",
            "    p { margin: 0.4rem 0; }",
            "    ul { margin: 0.3rem 0 0.5rem; padding-left: 1.2rem; }",
            "    table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; }",
            "    th, td { border: 1px solid #d0d7de; padding: 0.25rem 0.35rem; vertical-align: top; }",
            "    th { background: #f6f8fa; white-space: nowrap; }",
            "    blockquote { margin: 0.6rem 0; padding: 0.35rem 0.75rem; border-left: 4px solid #d0d7de; color: #57606a; }",
            "    @media print { body { font-size: 12.5px; margin: 0; padding: 0; max-width: none; } table { margin: 0.35rem 0; } th, td { padding: 0.2rem 0.3rem; } }",
            "  </style>",
            "</head>",
            "<body>",
            "<h1>宝可梦 欧米伽红宝石／阿尔法蓝宝石 攻略 / Pokémon Omega Ruby & Alpha Sapphire Guide</h1>",
            "<h2>图鉴 / Pokédex</h2>",
            "<blockquote>本章节为首版骨架，展示图鉴条目结构。后续可扩展为完整全国图鉴与招式来源。</blockquote>",
            *content_sections,
            "</body>",
            "</html>",
            "",
        ]
    )


def main() -> None:
    pokedex = json.loads(POKEDEX_FILE.read_text(encoding="utf-8"))
    pokedex_db = {pokemon["number"]: pokemon for pokemon in pokedex}
    moves_db = load_moves_db()
    abilities_db = load_abilities_db()
    types_db = load_types_db()
    categories_db = load_categories_db()
    contest_categories_db = load_contest_categories_db()

    sections = [
        render_pokemon(
            pokemon,
            pokedex_db,
            moves_db,
            abilities_db,
            types_db,
            categories_db,
            contest_categories_db,
        )
        for pokemon in pokedex
    ]

    OUTPUT_HTML_FILE.write_text(render_html(sections), encoding="utf-8")


if __name__ == "__main__":
    main()
