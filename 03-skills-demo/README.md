# 03 — Skills Demo (Cooking Theme)

A demo showing how to structure an **AI agent skill folder** — using **cooking recipes** as the topic.

This mirrors the pattern used in Claude/Copilot skill directories like `~/.claude/skills/react-component-review/`.

## Folder Structure

```
03-skills-demo/
├── SKILL.md                     # Core instructions + metadata
│
├── templates/                   # Reusable formats (agent reads on demand)
│   ├── recipe-card.md           #   Standard recipe card template
│   └── meal-plan.md             #   Weekly meal plan template
│
├── examples/                    # Good & bad examples (teach the agent standards)
│   ├── good-recipes.md          #   10 complete, well-formatted recipes
│   └── anti-patterns.md         #   8 common mistakes to avoid
│
├── references/                  # Domain knowledge & rules
│   ├── cooking-methods.md       #   10 cooking methods explained
│   └── temperature-guide.md     #   USDA safe temps, oil temps, oven names
│
└── scripts/                     # Executable validation tools
    ├── validate_recipe.py       #   Validate a recipe JSON against all rules
    └── check_ingredients.py     #   Cross-check recipe vs pantry/shopping list
```

## The 10 Demo Recipes

| #  | Dish                     | Method     | Temp (°C/°F)  |
|----|--------------------------|------------|---------------|
| 1  | Grilled Salmon           | Grilling   | 200°C / 400°F |
| 2  | Roast Chicken            | Roasting   | 190°C / 375°F |
| 3  | Beef Stew                | Braising   | 160°C / 325°F |
| 4  | Stir-Fry Vegetables      | Stir-fry   | 230°C / 450°F |
| 5  | Baked Pasta              | Baking     | 180°C / 350°F |
| 6  | Pan-Seared Steak         | Pan-sear   | 220°C / 430°F |
| 7  | Steamed Dumplings        | Steaming   | 100°C / 212°F |
| 8  | Deep-Fried Chicken Wings | Deep-fry   | 180°C / 350°F |
| 9  | Slow-Cooked Pulled Pork  | Slow-cook  | 120°C / 250°F |
| 10 | Poached Eggs             | Poaching   | 85°C / 185°F  |

## Try the Scripts

```bash
# Validate the built-in example recipe
python 03-skills-demo/scripts/validate_recipe.py --example

# Check ingredients against a pantry
python 03-skills-demo/scripts/check_ingredients.py --example
```

## How This Maps to a Real Skill

| This Demo                  | Real Skill (e.g. React Review)         |
|----------------------------|----------------------------------------|
| `SKILL.md`                 | Core prompt + rules                    |
| `templates/recipe-card.md` | `templates/functional.tsx.md`          |
| `examples/good-recipes.md` | `examples/good.md`                     |
| `examples/anti-patterns.md`| `examples/anti-pattern.md`             |
| `references/cooking-methods.md` | `references/hooks-rules.md`       |
| `references/temperature-guide.md` | `references/naming-convention.md`|
| `scripts/validate_recipe.py` | `scripts/validate-props.py`          |
| `scripts/check_ingredients.py` | `scripts/check-cycle-deps.sh`      |
