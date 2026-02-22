# ORAS Guide Generator

本仓库用于生成《宝可梦 欧米伽红宝石／阿尔法蓝宝石》中文攻略书（Markdown）。

## 目录结构

- `data/pokedex.json`：图鉴数据（每只宝可梦的基础信息与等级招式学习表）。
- `data/moves.json`：可复用的招式数据库（中英名称与战斗参数）。
- `scripts/`：生成 Markdown 书籍的脚本。
- `docs/`：生成后的攻略书内容。

## 当前已实现

- 图鉴（Pokédex）章节骨架：
  - 宝可梦编号
  - 中文/英文名称
  - 属性
  - 进化条件与去向
  - 招式表（通过 `move_id` 关联招式数据库，并保留每只宝可梦的学习等级）

## 数据设计说明

- `moves.json` 负责维护招式主数据，可被多只宝可梦复用。
- `pokedex.json` 的 `moves` 字段仅保留：
  - `level`：该宝可梦学习该招式的等级
  - `move_id`：引用 `moves.json` 的招式 ID

## 生成方法

```bash
python3 scripts/generate_guide.py
```

生成文件：`docs/guide.md`
