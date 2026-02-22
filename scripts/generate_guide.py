#!/usr/bin/env python3
"""Generate a Markdown guide for Pokémon Omega Ruby / Alpha Sapphire."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POKEDEX_FILE = ROOT / "data" / "pokedex.json"
MOVES_FILE = ROOT / "data" / "moves.json"
OUTPUT_FILE = ROOT / "docs" / "guide.md"


def format_moves_table(learnset: list[dict], moves_db: dict[str, dict]) -> str:
    header = (
        "| 等级/Level | 招式（中文/English） | 属性/Type | 分类/Category | 威力/Power | 命中/Accuracy | PP |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    rows = []
    for learn in learnset:
        move_id = learn["move_id"]
        if move_id not in moves_db:
            raise KeyError(f"Unknown move_id '{move_id}' in pokedex learnset.")
        move = moves_db[move_id]
        rows.append(
            "| {level} | {zh} / {en} | {type_} | {category} | {power} | {accuracy} | {pp} |".format(
                level=learn["level"],
                zh=move["name"]["zh"],
                en=move["name"]["en"],
                type_=move["type"],
                category=move["category"],
                power=move["power"],
                accuracy=move["accuracy"],
                pp=move["pp"],
            )
        )
    return header + "\n".join(rows)


def render_pokemon(entry: dict, moves_db: dict[str, dict]) -> str:
    lines = [
        f"### No.{entry['number']} {entry['name']['zh']} / {entry['name']['en']}",
        "",
        f"- **属性/Type**：{', '.join(entry['types'])}",
        f"- **进化/Evolution**：{entry['evolution']['condition']} → {entry['evolution']['to']}",
        "",
        "**招式表/Moves**",
        "",
        format_moves_table(entry["moves"], moves_db),
        "",
    ]
    return "\n".join(lines)


def load_moves_db() -> dict[str, dict]:
    moves = json.loads(MOVES_FILE.read_text(encoding="utf-8"))
    return {move["id"]: move for move in moves}


def main() -> None:
    pokedex = json.loads(POKEDEX_FILE.read_text(encoding="utf-8"))
    moves_db = load_moves_db()

    sections = [
        "# 宝可梦 欧米伽红宝石／阿尔法蓝宝石 攻略 / Pokémon Omega Ruby & Alpha Sapphire Guide",
        "",
        "## 图鉴 / Pokédex",
        "",
        "> 本章节为首版骨架，展示图鉴条目结构。后续可扩展为完整全国图鉴与招式来源。",
        "",
    ]

    for pokemon in pokedex:
        sections.append(render_pokemon(pokemon, moves_db))

    OUTPUT_FILE.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
