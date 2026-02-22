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
OUTPUT_CSS_FILE = ROOT / "docs" / "styles.css"


def render_css() -> str:
    return "\n".join(
        [
            ":root { --cell-bg-default: transparent; --multiplier-2x-bg: #b7eb8f; --multiplier-half-bg: #ffb3b3; --multiplier-zero-bg: #4a4a4a; --multiplier-zero-text: #ffffff; --multiplier-normal-bg: transparent; }",
            "body { font-family: sans-serif; font-size: 14px; line-height: 1.35; margin: 1rem auto; max-width: 1100px; padding: 0 0.5rem; }",
            "h1, h2, h3 { line-height: 1.25; margin: 0.6rem 0; }",
            "p { margin: 0.4rem 0; }",
            "ul { margin: 0.3rem 0 0.5rem; padding-left: 1.2rem; }",
            "table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; }",
            "th, td { border: 1px solid #d0d7de; padding: 0.25rem 0.35rem; vertical-align: top; }",
            "th { background: #f6f8fa; white-space: nowrap; }",
            ".ta-center { text-align: center; }",
            ".va-middle { vertical-align: middle; }",
            ".nowrap { white-space: nowrap; }",
            ".bg-dynamic { background: var(--cell-bg, var(--cell-bg-default)); }",
            ".text-type { color: var(--text-color, inherit); }",
            ".table-scroll { overflow-x: auto; }",
            ".type-chart th, .natures-table th, .personality-table th, .moves-table th { background: #f6f8fa; }",
            ".type-chart .multiplier-2x { background: var(--multiplier-2x-bg); }",
            ".type-chart .multiplier-half { background: var(--multiplier-half-bg); }",
            ".type-chart .multiplier-zero { background: var(--multiplier-zero-bg); color: var(--multiplier-zero-text); }",
            ".type-chart .multiplier-normal { background: var(--multiplier-normal-bg); }",
            "blockquote { margin: 0.6rem 0; padding: 0.35rem 0.75rem; border-left: 4px solid #d0d7de; color: #57606a; }",
            "@media (prefers-color-scheme: dark) {",
            "  :root { --cell-bg-default: transparent; --multiplier-2x-bg: #355c2b; --multiplier-half-bg: #6b2f2f; --multiplier-zero-bg: #1f1f1f; --multiplier-zero-text: #f5f5f5; --multiplier-normal-bg: transparent; }",
            "}",
            "@media print { body { font-size: 12.5px; margin: 0; padding: 0; max-width: none; } table { margin: 0.35rem 0; } th, td { padding: 0.2rem 0.3rem; } }",
            "",
        ]
    )


def format_moves_table(
    learnset: list[dict],
    moves_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
    contest_categories_db: dict[str, dict],
    pokemon_types: set[str],
) -> str:
    center_both_indices = {0, 3, 4, 5, 6, 7, 8, 9, 10}
    center_vertical_only_indices = {1, 2}

    header_cells = [
        "<span class='nowrap'>等级</span>",
        "<span class='nowrap'>招式</span>",
        "<span class='nowrap'>特殊效果</span>",
        "<span class='nowrap'>属性</span>",
        "<span class='nowrap'>分类</span>",
        "<span class='nowrap'>威力</span>",
        "<span class='nowrap'>命中</span>",
        "<span class='nowrap'>PP</span>",
        "<span class='nowrap'>类别</span>",
        "<span class='nowrap'>表演</span>",
        "<span class='nowrap'>妨害</span>",
    ]
    header_row = []
    for i, cell in enumerate(header_cells):
        classes = []
        if i in center_both_indices:
            classes.extend(["ta-center", "va-middle"])
        elif i in center_vertical_only_indices:
            classes.append("va-middle")
        class_attr = f" class='{' '.join(classes)}'" if classes else ""
        header_row.append(f"<th{class_attr}>{cell}</th>")

    lines = [
        "<table class='moves-table'>",
        "<tr>" + "".join(header_row) + "</tr>",
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
            contest_category = "<span class='nowrap'>—</span>"
            contest_category_color = None
        else:
            if contest_category_id not in contest_categories_db:
                raise KeyError(
                    f"Unknown contest_category_id '{contest_category_id}' in moves database."
                )
            contest_category = (
                f"<span class='nowrap'>{contest_categories_db[contest_category_id]['name']['zh']}</span>"
            )
            contest_category_color = contest_categories_db[contest_category_id].get("color")

        type_color = types_db[type_id].get("color", "#FFFFFF")
        category_color = categories_db[category_id].get("color", "#FFFFFF")
        displayed_power = move["power"]
        if (
            type_id in pokemon_types
            and isinstance(move["power"], str)
            and move["power"].isdigit()
        ):
            displayed_power = f"<strong>{int(move['power']) * 3 // 2}</strong>"

        cells = [
            learn["level"],
            f"<span class='nowrap'>{move['name']['zh']}</span><br><span class='nowrap'>{move['name']['en']}</span>",
            move.get("effect", ""),
            f"<span class='nowrap'>{types_db[type_id]['name']['zh']}</span>",
            f"<span class='nowrap'>{categories_db[category_id]['name']['zh']}</span>",
            displayed_power,
            move["accuracy"],
            move["pp"],
            contest_category,
            move["appeal"],
            move["jam"],
        ]
        row_cells = []
        for i, cell in enumerate(cells):
            classes = []
            style_attr = ""
            if i in center_both_indices:
                classes.extend(["ta-center", "va-middle"])
            elif i in center_vertical_only_indices:
                classes.append("va-middle")

            if i == 3:
                classes.append("bg-dynamic")
                style_attr = f" style='--cell-bg: {type_color};'"
            if i == 4:
                classes.append("bg-dynamic")
                style_attr = f" style='--cell-bg: {category_color};'"
            if i == 8 and contest_category_color:
                classes.append("bg-dynamic")
                style_attr = f" style='--cell-bg: {contest_category_color};'"

            class_attr = f" class='{' '.join(classes)}'" if classes else ""
            row_cells.append(f"<td{class_attr}{style_attr}>{cell}</td>")
        lines.append("<tr>" + "".join(row_cells) + "</tr>")

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


def parse_ability_entry(ability_entry: str | dict) -> tuple[str, bool]:
    if isinstance(ability_entry, str):
        return ability_entry, False

    ability_id = ability_entry.get("id")
    if not ability_id:
        raise KeyError("Ability entry object must include non-empty 'id'.")
    return ability_id, bool(ability_entry.get("hidden", False))


def format_ability(ability_entry: str | dict, abilities_db: dict[str, dict]) -> str:
    ability_id, is_hidden = parse_ability_entry(ability_entry)
    if ability_id not in abilities_db:
        raise KeyError(f"Unknown ability_id '{ability_id}' in pokedex abilities.")
    ability = abilities_db[ability_id]
    hidden_prefix = "[隐藏] " if is_hidden else ""
    return (
        f"<strong>{hidden_prefix}{ability['name']['zh']} / {ability['name']['en']}</strong>"
        f" - {ability['description']}"
    )


def format_pokemon_types(entry: dict, types_db: dict[str, dict]) -> str:
    zh_types = []
    for raw_type in entry["types"]:
        if raw_type in types_db:
            type_name = types_db[raw_type]["name"]["zh"]
            type_color = types_db[raw_type].get("color", "inherit")
            zh_types.append(f"<span class='text-type' style='--text-color: {type_color};'>{type_name}</span>")
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
    pokemon_types = {pokemon_type for pokemon_type in entry["types"] if pokemon_type in types_db}
    title = f"#{entry['number']} {entry['name']['zh']} / {entry['name']['en']} | {zh_types}"

    abilities_html = "\n".join(
        f"<li>{format_ability(ability_entry, abilities_db)}</li>"
        for ability_entry in entry["abilities"]
    )

    lines = [
        f"<h3>{title}</h3>",
    ]

    if evolution_text is not None:
        lines.append(f"<p><strong>进化</strong>：{evolution_text}</p>")

    lines.extend([
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
            pokemon_types,
        ),
    ])
    return "\n".join(lines)


def render_natures_section() -> str:
    column_headers = ["攻击↓（辣）", "防御↓（酸）", "速度↓（甜）", "特攻↓（涩）", "特防↓（苦）"]
    row_headers = ["攻击↑（辣）", "防御↑（酸）", "速度↑（甜）", "特攻↑（涩）", "特防↑（苦）"]
    rows = [
        ["勤奋/Hardy", "怕寂寞/Lonely", "勇敢/Brave", "固执/Adamant", "顽皮/Naughty"],
        ["大胆/Bold", "坦率/Docile", "悠闲/Relaxed", "淘气/Impish", "乐天/Lax"],
        ["胆小/Timid", "急躁/Hasty", "认真/Serious", "爽朗/Jolly", "天真/Naive"],
        ["内敛/Modest", "慢吞吞/Mild", "冷静/Quiet", "害羞/Bashful", "马虎/Rash"],
        ["温和/Calm", "温顺/Gentle", "自大/Sassy", "慎重/Careful", "浮躁/Quirky"],
    ]

    lines = [
        "<h2>性格 / Natures</h2>",
        "<table class='natures-table'>",
        "<tr>",
        "<th class='ta-center va-middle'>↑\↓</th>",
        *[
            f"<th class='ta-center va-middle'>{header}</th>"
            for header in column_headers
        ],
        "</tr>",
    ]

    for row_header, row in zip(row_headers, rows):
        lines.append("<tr>")
        lines.append(f"<th class='ta-center va-middle'>{row_header}</th>")
        lines.extend(f"<td class='ta-center va-middle'>{nature}</td>" for nature in row)
        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def format_multiplier(multiplier: float) -> str:
    if multiplier == 0:
        return "0×"
    if multiplier == 0.5:
        return "½×"
    if multiplier == 2:
        return "2×"
    return "1×"


def get_multiplier_cell_style(multiplier: float) -> str:
    if multiplier == 2:
        return "multiplier-2x"
    if multiplier == 0.5:
        return "multiplier-half"
    if multiplier == 0:
        return "multiplier-zero"
    return "multiplier-normal"


def render_type_chart_section(types_db: dict[str, dict]) -> str:
    ordered_types = [
        "normal",
        "fighting",
        "flying",
        "poison",
        "ground",
        "rock",
        "bug",
        "ghost",
        "steel",
        "fire",
        "water",
        "grass",
        "electric",
        "psychic",
        "ice",
        "dragon",
        "dark",
        "fairy",
    ]

    for type_id in ordered_types:
        if type_id not in types_db:
            raise KeyError(f"Unknown type_id '{type_id}' in types database.")
        if "attack_multipliers" not in types_db[type_id]:
            raise KeyError(f"Missing attack_multipliers for type_id '{type_id}'.")

    lines = [
        "<h2>属性相克表 / Type Effectiveness</h2>",
        "<p>行表示攻击招式属性，列表示防御方宝可梦属性。</p>",
        "<div class='table-scroll'>",
        "<table class='type-chart'>",
        "<tr>",
        "<th class='ta-center va-middle'>攻\\守</th>",
    ]

    for defender_type in ordered_types:
        defender = types_db[defender_type]
        lines.append(
            "<th class='ta-center va-middle bg-dynamic' "
            f"style='--cell-bg: {defender.get('color', '#f6f8fa')};'>{defender['name']['zh']}</th>"
        )

    lines.append("</tr>")

    for attacker_type in ordered_types:
        attacker = types_db[attacker_type]
        lines.append("<tr>")
        lines.append(
            "<th class='ta-center va-middle bg-dynamic' "
            f"style='--cell-bg: {attacker.get('color', '#f6f8fa')};'>{attacker['name']['zh']}</th>"
        )

        attack_multipliers = attacker["attack_multipliers"]
        for defender_type in ordered_types:
            if defender_type not in attack_multipliers:
                raise KeyError(
                    f"Missing multiplier: attack '{attacker_type}' -> defend '{defender_type}'."
                )
            multiplier = attack_multipliers[defender_type]
            classes = " ".join([
                "ta-center",
                "va-middle",
                get_multiplier_cell_style(multiplier),
            ])
            lines.append(
                f"<td class='{classes}'>{format_multiplier(multiplier)}</td>"
            )

        lines.append("</tr>")

    lines.extend(["</table>", "</div>"])
    return "\n".join(lines)


def render_personality_section() -> str:
    headers = ["个体值 % 5", "HP", "攻击", "防御", "特攻", "特防", "速度"]
    rows = [
        [
            "0",
            "非常喜欢吃东西<br>Loves to eat",
            "以力气大为傲<br>Proud of its power",
            "身体强壮<br>Sturdy body",
            "好奇心强<br>Highly curious",
            "性格强势<br>Strong willed",
            "喜欢比谁跑得快<br>Likes to run",
        ],
        [
            "1",
            "经常睡午觉<br>Takes plenty of siestas",
            "喜欢胡闹<br>Likes to thrash about",
            "抗打能力强<br>Capable of taking hits",
            "喜欢恶作剧<br>Mischievous",
            "有一点点爱慕虚荣<br>Somewhat vain",
            "对声音敏感<br>Alert to sounds",
        ],
        [
            "2",
            "常常打瞌睡<br>Nods off a lot",
            "有点容易生气<br>A little quick tempered",
            "顽强不屈<br>Highly persistent",
            "做事万无一失<br>Thoroughly cunning",
            "争强好胜<br>Strongly defiant",
            "冒冒失失<br>Impetuous and silly",
        ],
        [
            "3",
            "经常乱扔东西<br>Scatters things often",
            "喜欢打架<br>Likes to fight",
            "能吃苦耐劳<br>Good endurance",
            "经常思考<br>Often lost in thought",
            "不服输<br>Hates to lose",
            "有点容易得意忘形<br>Somewhat of a clown",
        ],
        [
            "4",
            "喜欢悠然自在<br>Likes to relax",
            "血气方刚<br>Quick tempered",
            "善于忍耐<br>Good perseverance",
            "一丝不苟<br>Very finicky",
            "有一点点固执<br>Somewhat stubborn",
            "逃得快<br>Quick to flee",
        ],
    ]

    lines = [
        "<h2>个性 / Personality</h2>",
        "<p>个性由最高的个体值决定，个体值的范围是0-31，参考下表</p>",
        "<table class='personality-table'>",
        "<tr>",
    ]
    lines.extend(f"<th class='ta-center va-middle'>{header}</th>" for header in headers)
    lines.append("</tr>")

    for row in rows:
        lines.append("<tr>")
        lines.extend(f"<td class='ta-center va-middle'>{cell}</td>" for cell in row)
        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def render_html(content_sections: list[str], types_db: dict[str, dict]) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang='zh-CN'>",
            "<head>",
            "  <meta charset='utf-8' />",
            "  <meta name='viewport' content='width=device-width, initial-scale=1' />",
            "  <title>ORAS Guide</title>",
            "  <link rel='stylesheet' href='styles.css' />",
            "</head>",
            "<body>",
            "<h1>宝可梦 欧米伽红宝石／阿尔法蓝宝石 攻略 / Pokémon Omega Ruby & Alpha Sapphire Guide</h1>",
            render_type_chart_section(types_db),
            render_natures_section(),
            render_personality_section(),
            "<h2>图鉴 / Pokédex</h2>",
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

    OUTPUT_HTML_FILE.write_text(render_html(sections, types_db), encoding="utf-8")
    OUTPUT_CSS_FILE.write_text(render_css(), encoding="utf-8")


if __name__ == "__main__":
    main()
