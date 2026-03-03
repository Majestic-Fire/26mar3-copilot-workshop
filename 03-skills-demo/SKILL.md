---
name: cooking-recipe-review
description: Review, generate, and validate cooking recipes with proper ingredients, methods, and temperatures.
version: 1.0.0
author: workshop-demo
tags: [cooking, recipes, food-safety, temperature]
---

# Cooking Recipe Review Skill

## Purpose

This skill helps you **create, review, and validate** cooking recipes.
It ensures every recipe has correct ingredients, proper cooking methods, and safe temperatures.

## When to Use

- Generating a new recipe
- Reviewing an existing recipe for completeness
- Checking food-safety temperatures
- Planning meals with proper cooking techniques

## Core Rules

1. Every recipe MUST include: **ingredients list**, **cooking method**, and **temperature** (if heat is involved).
2. Temperatures MUST be in both Celsius and Fahrenheit.
3. Meat dishes MUST specify internal safe temperature.
4. Allergens MUST be flagged (e.g., nuts, gluten, dairy).
5. Cooking times MUST be provided as a range (e.g., 25-30 minutes).

## Folder Structure

| Folder        | Purpose                                      |
|---------------|----------------------------------------------|
| `templates/`  | Reusable recipe card and meal plan formats   |
| `examples/`   | 10 good recipe examples + common anti-patterns|
| `references/` | Cooking methods guide + temperature chart    |
| `scripts/`    | Python validators for recipes                |

## Workflow

```
1. Read templates/recipe-card.md for the standard format
2. Check references/temperature-guide.md for safe temps
3. Check references/cooking-methods.md for method descriptions
4. Use scripts/validate_recipe.py to validate a recipe JSON
5. Compare against examples/good-recipes.md for quality
6. Avoid patterns in examples/anti-patterns.md
```

## Quick Reference — The 10 Demo Recipes

| #  | Dish                    | Key Ingredient     | Method   | Temp (°C/°F)   |
|----|-------------------------|--------------------|----------|-----------------|
| 1  | Grilled Salmon          | Salmon fillet      | Grilling | 200°C / 400°F  |
| 2  | Roast Chicken           | Whole chicken      | Roasting | 190°C / 375°F  |
| 3  | Beef Stew               | Beef chuck         | Braising | 160°C / 325°F  |
| 4  | Stir-Fry Vegetables     | Mixed vegetables   | Stir-fry | 230°C / 450°F  |
| 5  | Baked Pasta             | Penne pasta        | Baking   | 180°C / 350°F  |
| 6  | Pan-Seared Steak        | Ribeye steak       | Pan-sear | 220°C / 430°F  |
| 7  | Steamed Dumplings       | Pork filling       | Steaming | 100°C / 212°F  |
| 8  | Deep-Fried Chicken Wings| Chicken wings      | Deep-fry | 180°C / 350°F  |
| 9  | Slow-Cooked Pulled Pork | Pork shoulder      | Slow-cook| 120°C / 250°F  |
| 10 | Poached Eggs            | Eggs               | Poaching | 85°C / 185°F   |
