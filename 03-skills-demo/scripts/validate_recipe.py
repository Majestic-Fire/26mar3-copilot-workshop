#!/usr/bin/env python3
"""
validate_recipe.py — Validates a recipe JSON file against the cooking skill rules.

Usage:
    python validate_recipe.py recipe.json
    python validate_recipe.py --example   (run with a built-in example)

Rules checked:
  1. Has ingredients list with quantities
  2. Has cooking method
  3. Temperature in both °C and °F
  4. Cook time is a range (min-max)
  5. Allergens are flagged
  6. Meat dishes have internal safe temp
"""

import json
import sys
import os

# Safe internal temperatures (°C) by protein type
SAFE_TEMPS_C = {
    "chicken": 74,
    "turkey": 74,
    "pork": 63,
    "beef": 63,
    "lamb": 63,
    "fish": 63,
    "salmon": 63,
    "shrimp": 63,
}

KNOWN_ALLERGENS = [
    "gluten", "dairy", "eggs", "fish", "shellfish",
    "peanuts", "tree nuts", "soy", "sesame", "wheat",
]

VALID_METHODS = [
    "grilling", "roasting", "braising", "stir-fry", "baking",
    "pan-sear", "steaming", "deep-fry", "slow-cook", "poaching",
]

EXAMPLE_RECIPE = {
    "name": "Grilled Salmon",
    "servings": 2,
    "prep_time_min": 10,
    "cook_time_min": 12,
    "cook_time_max": 15,
    "method": "grilling",
    "temp_c": 200,
    "temp_f": 400,
    "internal_temp_c": 63,
    "internal_temp_f": 145,
    "ingredients": [
        {"name": "salmon fillets", "qty": 2, "unit": "pcs", "allergen": "fish"},
        {"name": "olive oil", "qty": 2, "unit": "tbsp", "allergen": None},
        {"name": "garlic powder", "qty": 1, "unit": "tsp", "allergen": None},
        {"name": "lemon", "qty": 1, "unit": "pc", "allergen": None},
        {"name": "salt & pepper", "qty": 1, "unit": "pinch", "allergen": None},
    ],
    "contains_meat": True,
    "steps": [
        "Preheat grill to 200°C / 400°F.",
        "Brush salmon with olive oil, season.",
        "Grill skin-side down 6-7 min, flip, cook 5-6 min.",
        "Check internal temp reaches 63°C / 145°F.",
        "Squeeze lemon and serve.",
    ],
}


def validate_recipe(recipe: dict) -> list[str]:
    """Validate a recipe dict. Returns a list of error messages (empty = valid)."""
    errors = []

    # Rule 1: Ingredients with quantities
    ingredients = recipe.get("ingredients", [])
    if not ingredients:
        errors.append("[FAIL] No ingredients list found.")
    else:
        for i, ing in enumerate(ingredients):
            if not ing.get("name"):
                errors.append(f"[FAIL] Ingredient #{i+1} has no name.")
            if ing.get("qty") is None:
                errors.append(f"[FAIL] Ingredient '{ing.get('name', '?')}' has no quantity.")

    # Rule 2: Cooking method
    method = recipe.get("method", "").lower()
    if not method:
        errors.append("[FAIL] No cooking method specified.")
    elif method not in VALID_METHODS:
        errors.append(f"[WARN] Unknown cooking method: '{method}'. Valid: {VALID_METHODS}")

    # Rule 3: Temperature in both units
    temp_c = recipe.get("temp_c")
    temp_f = recipe.get("temp_f")
    if temp_c is None and temp_f is None:
        errors.append("[FAIL] No cooking temperature specified.")
    elif temp_c is None:
        errors.append("[FAIL] Missing temperature in °C.")
    elif temp_f is None:
        errors.append("[FAIL] Missing temperature in °F.")

    # Rule 4: Cook time as range
    cook_min = recipe.get("cook_time_min")
    cook_max = recipe.get("cook_time_max")
    if cook_min is None or cook_max is None:
        errors.append("[FAIL] Cook time must be a range (cook_time_min and cook_time_max).")
    elif cook_min >= cook_max:
        errors.append("[FAIL] cook_time_min must be less than cook_time_max.")

    # Rule 5: Allergens flagged
    allergen_count = sum(1 for ing in ingredients if ing.get("allergen"))
    has_potential_allergens = any(
        any(a in ing.get("name", "").lower() for a in KNOWN_ALLERGENS)
        for ing in ingredients
    )
    if has_potential_allergens and allergen_count == 0:
        errors.append("[WARN] Ingredients may contain allergens but none are flagged.")

    # Rule 6: Meat dishes need internal safe temp
    if recipe.get("contains_meat"):
        internal_c = recipe.get("internal_temp_c")
        internal_f = recipe.get("internal_temp_f")
        if internal_c is None or internal_f is None:
            errors.append("[FAIL] Meat dish must specify internal safe temperature (°C and °F).")
        elif internal_c and method:
            # Check against known safe temps
            for protein, safe in SAFE_TEMPS_C.items():
                if protein in recipe.get("name", "").lower():
                    if internal_c < safe:
                        errors.append(
                            f"[FAIL] Internal temp {internal_c}°C is below safe minimum "
                            f"{safe}°C for {protein}."
                        )

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_recipe.py <recipe.json>")
        print("       python validate_recipe.py --example")
        sys.exit(1)

    if sys.argv[1] == "--example":
        recipe = EXAMPLE_RECIPE
        print(f"Validating built-in example: {recipe['name']}")
    else:
        filepath = sys.argv[1]
        if not os.path.isfile(filepath):
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8") as f:
            recipe = json.load(f)
        print(f"Validating: {recipe.get('name', 'Unknown Recipe')}")

    print("-" * 50)
    errors = validate_recipe(recipe)

    if not errors:
        print("✅ All checks passed! Recipe is valid.")
    else:
        for err in errors:
            print(f"  {err}")
        print(f"\n❌ {len(errors)} issue(s) found.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
