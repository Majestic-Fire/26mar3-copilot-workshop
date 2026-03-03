# Anti-Patterns — Bad Recipe Examples

These examples show **what NOT to do** when writing recipes. Each one violates one or more rules from SKILL.md.

---

## Anti-Pattern 1: Missing Temperature

> "Bake the chicken until it looks done."

**Problem:** No temperature specified. No way to set the oven or verify doneness.
**Fix:** Always state oven temp (e.g., 190°C / 375°F) AND internal safe temp for meat (74°C / 165°F).

---

## Anti-Pattern 2: Vague Quantities

> "Add some flour, a bit of butter, and enough milk."

**Problem:** "Some," "a bit," and "enough" are not measurable.
**Fix:** Use exact quantities — `200g flour`, `30g butter`, `250ml milk`.

---

## Anti-Pattern 3: Missing Allergen Info

> Ingredients: peanut oil, soy sauce, shrimp paste, wheat noodles

**Problem:** Four allergens (peanuts, soy, shellfish, gluten) — none flagged.
**Fix:** Mark each allergen in the ingredients table.

---

## Anti-Pattern 4: Single Temperature Unit

> "Preheat oven to 350°F"

**Problem:** Only Fahrenheit. International users need Celsius too.
**Fix:** Always provide both — `180°C / 350°F`.

---

## Anti-Pattern 5: No Cooking Method Stated

> 1. Put meat in pot.
> 2. Add water.
> 3. Wait until done.

**Problem:** Is this braising? Boiling? Steaming? The method is unclear.
**Fix:** Explicitly state the cooking method at the top of the recipe.

---

## Anti-Pattern 6: Exact Time Instead of Range

> "Cook for exactly 12 minutes."

**Problem:** Ovens and stovetops vary. A fixed time may under/over-cook.
**Fix:** Use a range — `10-14 minutes` — plus a doneness check.

---

## Anti-Pattern 7: Unsafe Meat Temperature

> "Cook the pork chops until they're slightly pink inside — that's the best texture."

**Problem:** Pork must reach 63°C / 145°F minimum. "Slightly pink" is not a measurement.
**Fix:** Specify minimum internal temperature and recommend using a meat thermometer.

---

## Anti-Pattern 8: No Equipment Listed

> "Sear the steak at very high heat."

**Problem:** What pan? What heat source? Cast iron? Non-stick? Grill?
**Fix:** State equipment — `Cast iron skillet on stovetop, preheated to 220°C / 430°F`.

---

## Summary — Rules These Break

| Anti-Pattern | Rule Violated                        |
|--------------|--------------------------------------|
| 1            | Temperature required                 |
| 2            | Exact quantities required            |
| 3            | Allergens must be flagged            |
| 4            | Dual temperature units (°C and °F)   |
| 5            | Cooking method must be stated        |
| 6            | Cook time must be a range            |
| 7            | Safe internal temp for meat          |
| 8            | Equipment must be specified          |
