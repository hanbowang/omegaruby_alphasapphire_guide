#!/usr/bin/env python3
"""Generate Markdown/HTML guides for Pokémon Omega Ruby / Alpha Sapphire."""

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
OUTPUT_FILE = ROOT / "docs" / "guide.md"
OUTPUT_HTML_FILE = ROOT / "docs" / "guide.html"

def format_moves_table(
    learnset: list[dict],
    moves_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
    contest_categories_db: dict[str, dict],
) -> str:
    header = (
        "| <nobr>等级</nobr> | <nobr>招式</nobr> | <nobr>特殊效果</nobr> | <nobr>属性</nobr> | <nobr>分类</nobr> | <nobr>类别</nobr> | <nobr>威力</nobr> | <nobr>命中</nobr> | <nobr>PP</nobr> | <nobr>表演</nobr> | <nobr>妨害</nobr> |\n"
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

        move_name = f"<nobr>{move['name']['zh']}</nobr><br><nobr>{move['name']['en']}</nobr>"
        effect = move.get("effect", "")
        effect_text = effect if effect else ""
        type_name = f"<nobr>{types_db[type_id]['name']['zh']}</nobr>"
        category_id = move["category_id"]
        if category_id not in categories_db:
            raise KeyError(f"Unknown category_id '{category_id}' in moves database.")

        move_category = f"<nobr>{categories_db[category_id]['name']['zh']}</nobr>"
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
        rows.append(
            "| {level} | {move_name} | {effect} | {type_} | {category} | {contest_category} | {power} | {accuracy} | {pp} | {appeal} | {jam} |".format(
                level=learn["level"],
                move_name=move_name,
                effect=effect_text,
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
    evo_target_number = entry["evolution"]["to_number"]
    evo_target = pokedex_db.get(evo_target_number)
    if evo_target is None:
        evolution_to = f"#{evo_target_number}"
    else:
        evolution_to = (
            f"{evo_target['name']['zh']} / {evo_target['name']['en']}"
            f" (#{evo_target_number})"
        )

    zh_types = format_pokemon_types(entry, types_db)
    abilities_lines = [
        f"- {format_ability(ability_id, abilities_db)}" for ability_id in entry["abilities"]
    ]
    lines = [
        f"### #{entry['number']} {entry['name']['zh']} / {entry['name']['en']} | {zh_types} | {entry['evolution']['condition']} -> {evolution_to}",
        "",
        "**特性**：",
        *abilities_lines,
        "",
        "**招式表**",
        "",
        format_moves_table(
            entry["moves"],
            moves_db,
            types_db,
            categories_db,
            contest_categories_db,
        ),
        "",
    ]
    return "\n".join(lines)


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html_lines = [
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
    ]

    in_list = False
    in_table = False
    table_header_done = False

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            is_separator = all(set(cell) <= {"-", ":"} and cell for cell in cells)

            if is_separator:
                continue

            if in_list:
                html_lines.append("</ul>")
                in_list = False

            if not in_table:
                html_lines.append("<table>")
                in_table = True
                table_header_done = False

            tag = "th" if not table_header_done else "td"
            html_lines.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>")
            table_header_done = True
            continue

        if in_table:
            html_lines.append("</table>")
            in_table = False

        stripped = line.strip()
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br />")
            continue

        if line.startswith("### "):
            html_lines.append(f"<h3>{line[4:].strip()}</h3>")
            continue
        if line.startswith("## "):
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
            continue
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:].strip()}</h1>")
            continue
        if line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:].strip()}</blockquote>")
            continue
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{line[2:].strip()}</li>")
            continue

        text = line.replace("**", "")
        html_lines.append(f"<p>{text}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</table>")

    html_lines.extend(["</body>", "</html>"])
    return "\n".join(html_lines) + "\n"


def main() -> None:
    pokedex = json.loads(POKEDEX_FILE.read_text(encoding="utf-8"))
    pokedex_db = {pokemon["number"]: pokemon for pokemon in pokedex}
    moves_db = load_moves_db()
    abilities_db = load_abilities_db()
    types_db = load_types_db()
    categories_db = load_categories_db()
    contest_categories_db = load_contest_categories_db()

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
            render_pokemon(
                pokemon,
                pokedex_db,
                moves_db,
                abilities_db,
                types_db,
                categories_db,
                contest_categories_db,
            )
        )

    markdown = "\n".join(sections).rstrip() + "\n"
    OUTPUT_FILE.write_text(markdown, encoding="utf-8")
    OUTPUT_HTML_FILE.write_text(markdown_to_html(markdown), encoding="utf-8")


if __name__ == "__main__":
    main()
