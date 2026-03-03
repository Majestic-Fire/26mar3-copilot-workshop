#!/usr/bin/env python3
"""
check_ingredients.py — Cross-check a recipe's ingredients against a pantry/shopping list.

Usage:
    python check_ingredients.py recipe.json pantry.json
    python check_ingredients.py --example   (run with built-in example data)

Outputs:
  - Ingredients you already have
  - Ingredients you need to buy
  - Allergen summary
"""

import json
import sys
import os

EXAMPLE_RECIPE = {
    "name": "Beef Stew",
    "ingredients": [
        {"name": "beef chuck", "qty": 800, "unit": "g", "allergen": None},
        {"name": "potatoes", "qty": 3, "unit": "pcs", "allergen": None},
        {"name": "carrots", "qty": 2, "unit": "pcs", "allergen": None},
        {"name": "onion", "qty": 1, "unit": "pc", "allergen": None},
        {"name": "beef broth", "qty": 2, "unit": "cups", "allergen": None},
        {"name": "tomato paste", "qty": 2, "unit": "tbsp", "allergen": None},
        {"name": "flour", "qty": 2, "unit": "tbsp", "allergen": "gluten"},
    ],
}

EXAMPLE_PANTRY = {
    "items": ["potatoes", "onion", "tomato paste", "flour", "salt", "pepper", "olive oil"]
}


def check_ingredients(recipe: dict, pantry: dict) -> dict:
    """Compare recipe ingredients against pantry. Returns categorized results."""
    pantry_items = {item.lower() for item in pantry.get("items", [])}
    ingredients = recipe.get("ingredients", [])

    have = []
    need = []
    allergens = []

    for ing in ingredients:
        name = ing.get("name", "").lower()
        qty = ing.get("qty", "?")
        unit = ing.get("unit", "")
        allergen = ing.get("allergen")

        entry = f"{qty} {unit} {name}".strip()

        if name in pantry_items:
            have.append(entry)
        else:
            need.append(entry)

        if allergen:
            allergens.append(f"{name} ({allergen})")

    return {
        "recipe_name": recipe.get("name", "Unknown"),
        "total_ingredients": len(ingredients),
        "already_have": have,
        "need_to_buy": need,
        "allergens": allergens,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_ingredients.py <recipe.json> <pantry.json>")
        print("       python check_ingredients.py --example")
        sys.exit(1)

    if sys.argv[1] == "--example":
        recipe = EXAMPLE_RECIPE
        pantry = EXAMPLE_PANTRY
        print("Running with built-in example data...")
    else:
        recipe_path = sys.argv[1]
        pantry_path = sys.argv[2] if len(sys.argv) > 2 else None

        if not os.path.isfile(recipe_path):
            print(f"Error: Recipe file not found: {recipe_path}")
            sys.exit(1)
        with open(recipe_path, "r", encoding="utf-8") as f:
            recipe = json.load(f)

        if pantry_path and os.path.isfile(pantry_path):
            with open(pantry_path, "r", encoding="utf-8") as f:
                pantry = json.load(f)
        else:
            print("No pantry file provided — all ingredients will be listed as 'need to buy'.")
            pantry = {"items": []}

    result = check_ingredients(recipe, pantry)

    print(f"\n{'='*50}")
    print(f"  Recipe: {result['recipe_name']}")
    print(f"  Total ingredients: {result['total_ingredients']}")
    print(f"{'='*50}")

    print(f"\n✅ Already have ({len(result['already_have'])}):")
    for item in result["already_have"]:
        print(f"   - {item}")

    print(f"\n🛒 Need to buy ({len(result['need_to_buy'])}):")
    for item in result["need_to_buy"]:
        print(f"   - {item}")

    if result["allergens"]:
        print(f"\n⚠️  Allergens ({len(result['allergens'])}):")
        for a in result["allergens"]:
            print(f"   - {a}")
    else:
        print("\n✅ No allergens detected.")

    print()


if __name__ == "__main__":
    main()
