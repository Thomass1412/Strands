---
name: math-helper
description: Solve arithmetic and multi-step math word problems accurately using the calculator tool. Use when the user asks to calculate, convert, compare prices, split costs, or work out percentages.
---

# Math helper

Never do arithmetic in your head. Every calculation goes through the `calculator` tool, one operation at a time.

## Steps

1. Restate the problem as a list of single operations (add, subtract, multiply, divide, power).
2. Call `calculator` once per operation, feeding each result into the next step.
3. Give the final answer first, in bold, then show the steps briefly.
4. Before answering, call `verify_answer` with the question and your answer.
   If it returns WRONG, redo the calculation and verify again (at most twice).


## Rules

- Percentages: convert to a decimal first (15% → divide 15 by 100), then multiply.
- Round money to 2 decimals, and only at the end.
- If the calculator returns an error (such as division by zero), tell the user plainly instead of guessing.
- If the problem is ambiguous (for example "split the bill" without saying how many people), ask before calculating.

## Example

User: "Dinner was 840 kr and we're 3 people, plus a 10% tip. How much each?"

1. `calculator(10, 100, "divide")` → 0.1
2. `calculator(840, 0.1, "multiply")` → 84
3. `calculator(840, 84, "add")` → 924
4. `calculator(924, 3, "divide")` → 308

**308 kr each** (840 + 84 tip = 924, split 3 ways).
