# ORAS Guide Generator

本仓库用于生成《宝可梦 欧米伽红宝石／阿尔法蓝宝石》中文攻略书（Markdown）。

## 目录结构

- `data/pokedex.json`：图鉴数据（每只宝可梦的基础信息与等级招式学习表）。
- `data/moves.json`：可复用的招式数据库（中英名称与战斗参数）。
- `data/types.json`：属性数据库（供招式与其他资料通过 `type_id` 引用）。
- `scripts/`：生成 Markdown 书籍的脚本。
- `docs/`：生成后的攻略书内容。

## 当前已实现

- 图鉴（Pokédex）章节骨架：
  - 宝可梦编号
  - 中文/英文名称
  - 属性（通过 `type_id` 关联属性数据库）
  - 进化条件与去向
  - 招式表（通过 `move_id` 关联招式数据库，并保留每只宝可梦的学习等级）
  - 招式表包含“特殊效果”列（位于“招式”后）；无额外效果时留空
  - 招式表新增“类别”列（例如：强壮、可爱）

## 数据设计说明

- `moves.json` 负责维护招式主数据，可被多只宝可梦复用。
  - 使用 `type_id` 引用 `types.json`，避免在招式表中重复维护属性文案
  - 可选 `effect` 字段：仅在招式存在额外效果时填写（例如：可能灼伤、降能力等）
  - `contest_category` 字段：类别（强壮/聪明/美丽/可爱/帅气/机灵）
- `types.json` 负责维护属性主数据（中英名称），供 `moves.json` 等数据表引用。
- `pokedex.json` 的 `types` 字段使用 `type_id`（如 `grass`、`fire`）引用 `types.json`。
- `pokedex.json` 的 `moves` 字段仅保留：
  - `level`：该宝可梦学习该招式的等级
  - `move_id`：引用 `moves.json` 的招式 ID

## 生成方法

```bash
python3 scripts/generate_guide.py
```

生成文件：`docs/guide.md`
