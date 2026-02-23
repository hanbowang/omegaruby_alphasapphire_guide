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

MOVES_CENTER_BOTH_INDICES = {0, 3, 4, 5, 6, 7, 8, 9, 10}
MOVES_CENTER_VERTICAL_ONLY_INDICES = {1, 2}
MOVES_NOWRAP_INDICES = {0, 1, 3, 4, 8}


def format_attrs(*, classes: list[str] | None = None, style: str | None = None) -> str:
    attrs: list[str] = []
    if classes:
        attrs.append(f"class='{' '.join(classes)}'")
    if style:
        attrs.append(f"style='{style}'")
    return f" {' '.join(attrs)}" if attrs else ""


def render_css() -> str:
    return "\n".join(
        [
            "body { font-family: sans-serif; font-size: 14px; line-height: 1.35; margin: 1rem auto; max-width: 1100px; padding: 0 0.5rem; }",
            "h1, h2, h3 { line-height: 1.25; margin: 0.6rem 0; }",
            "p { margin: 0.4rem 0; }",
            "ul { margin: 0.3rem 0 0.5rem; padding-left: 1.2rem; }",
            ".guide-table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; }",
            ".guide-table th, .guide-table td { border: 1px solid #d0d7de; padding: 0.25rem 0.35rem; vertical-align: top; }",
            ".guide-table th { background: #f6f8fa; white-space: nowrap; }",
            ".ta-center { text-align: center; }",
            ".va-middle { vertical-align: middle; }",
            ".nowrap { white-space: nowrap; }",
            ".table-scroll { overflow-x: auto; }",
            ".type-chart .multiplier-2x { background: #b7eb8f; }",
            ".type-chart .multiplier-half { background: #ffb3b3; }",
            ".type-chart .multiplier-zero { background: #4a4a4a; color: #ffffff; }",
            "blockquote { margin: 0.6rem 0; padding: 0.35rem 0.75rem; border-left: 4px solid #d0d7de; color: #57606a; }",
            "@media print { body { font-size: 12.5px; margin: 0; padding: 0; max-width: none; } .guide-table { margin: 0.35rem 0; } .guide-table th, .guide-table td { padding: 0.2rem 0.3rem; } }",
            "",
        ]
    )


def render_table(
    headers: list[str],
    rows: list[list[str]],
    table_class: str,
    header_cell_class: str,
    cell_class: str,
    first_col_as_header: bool = False,
) -> str:
    header_classes = header_cell_class.split()
    cell_classes = cell_class.split()

    lines = [f"<table class='{table_class}'>", "<tr>"]
    lines.extend(
        f"<th{format_attrs(classes=header_classes)}>{header}</th>" for header in headers
    )
    lines.append("</tr>")

    for row in rows:
        lines.append("<tr>")
        for index, cell in enumerate(row):
            if first_col_as_header and index == 0:
                lines.append(f"<th{format_attrs(classes=header_classes)}>{cell}</th>")
            else:
                lines.append(f"<td{format_attrs(classes=cell_classes)}>{cell}</td>")
        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def get_moves_header_cell_classes(index: int) -> list[str]:
    classes: list[str] = []
    if index in MOVES_CENTER_BOTH_INDICES:
        classes.extend(["ta-center", "va-middle"])
    elif index in MOVES_CENTER_VERTICAL_ONLY_INDICES:
        classes.append("va-middle")
    return classes


def get_moves_row_cell_classes(index: int) -> list[str]:
    return get_moves_header_cell_classes(index)


def format_moves_table(
    learnset: list[dict],
    moves_db: dict[str, dict],
    types_db: dict[str, dict],
    categories_db: dict[str, dict],
    contest_categories_db: dict[str, dict],
    pokemon_types: set[str],
) -> str:
    header_cells = ["等级", "招式", "特殊效果", "属性", "分类", "威力", "命中", "PP", "类别", "表演", "妨害"]
    header_row = []
    for i, cell in enumerate(header_cells):
        classes = get_moves_header_cell_classes(i)
        if i in MOVES_NOWRAP_INDICES:
            classes = [*classes, "nowrap"]
        header_row.append(f"<th{format_attrs(classes=classes)}>{cell}</th>")

    lines = [
        "<table class='guide-table moves-table'>",
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
            contest_category = "—"
            contest_category_color = None
        else:
            if contest_category_id not in contest_categories_db:
                raise KeyError(
                    f"Unknown contest_category_id '{contest_category_id}' in moves database."
                )
            contest_category = contest_categories_db[contest_category_id]["name"]["zh"]
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
            types_db[type_id]["name"]["zh"],
            categories_db[category_id]["name"]["zh"],
            displayed_power,
            move["accuracy"],
            move["pp"],
            contest_category,
            move["appeal"],
            move["jam"],
        ]
        row_cells = []
        for i, cell in enumerate(cells):
            classes = get_moves_row_cell_classes(i)
            if i in MOVES_NOWRAP_INDICES:
                classes = [*classes, "nowrap"]

            style = None
            if i == 3:
                style = f"background-color: {type_color};"
            if i == 4:
                style = f"background-color: {category_color};"
            if i == 8 and contest_category_color:
                style = f"background-color: {contest_category_color};"

            row_cells.append(f"<td{format_attrs(classes=classes, style=style)}>{cell}</td>")
        lines.append("<tr>" + "".join(row_cells) + "</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def load_json_indexed_by_id(path: Path) -> dict[str, dict]:
    records = json.loads(path.read_text(encoding="utf-8"))
    return {record["id"]: record for record in records}


def load_moves_db() -> dict[str, dict]:
    return load_json_indexed_by_id(MOVES_FILE)


def load_abilities_db() -> dict[str, dict]:
    return load_json_indexed_by_id(ABILITIES_FILE)


def load_types_db() -> dict[str, dict]:
    return load_json_indexed_by_id(TYPES_FILE)


def load_categories_db() -> dict[str, dict]:
    return load_json_indexed_by_id(CATEGORIES_FILE)


def load_contest_categories_db() -> dict[str, dict]:
    return load_json_indexed_by_id(CONTEST_CATEGORIES_FILE)


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
            zh_types.append(f"<span style='color: {type_color};'>{type_name}</span>")
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

    table_headers = ["↑\\↓", *column_headers]
    table_rows = [[row_header, *row] for row_header, row in zip(row_headers, rows)]

    return "\n".join([
        "<h2>性格 / Natures</h2>",
        render_table(
            table_headers,
            table_rows,
            "guide-table natures-table",
            "ta-center va-middle",
            "ta-center va-middle",
            first_col_as_header=True,
        ),
    ])


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
        "<table class='guide-table type-chart'>",
        "<tr>",
        "<th class='ta-center va-middle'>攻\\守</th>",
    ]

    for defender_type in ordered_types:
        defender = types_db[defender_type]
        lines.append(
            "<th class='ta-center va-middle' "
            f"style='background-color: {defender.get('color', '#f6f8fa')};'>{defender['name']['zh']}</th>"
        )

    lines.append("</tr>")

    for attacker_type in ordered_types:
        attacker = types_db[attacker_type]
        lines.append("<tr>")
        lines.append(
            "<th class='ta-center va-middle' "
            f"style='background-color: {attacker.get('color', '#f6f8fa')};'>{attacker['name']['zh']}</th>"
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

    return "\n".join([
        "<h2>个性 / Personality</h2>",
        "<p>个性由最高的个体值决定，个体值的范围是0-31，参考下表</p>",
        render_table(
            headers,
            rows,
            "guide-table personality-table",
            "ta-center va-middle",
            "ta-center va-middle",
        ),
    ])


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
