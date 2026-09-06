---
name: brainstorming
description: Use when the user explicitly wants to explore or design an idea, or when implementation has unresolved product, architecture, interface, or scope decisions. Do not use for clearly specified localized changes.
---

# Brainstorming

Turn meaningful uncertainty into a clear design while preserving the user's authorization and momentum.

## Boundary

Use this skill when the user asks to brainstorm, compare approaches, or design something, or when a
requested implementation contains choices that could materially change architecture, public interfaces,
product behavior, or scope.

Skip it for clearly specified localized fixes, routine refactors, documentation or configuration edits,
and implementation whose important decisions are already settled. If hidden complexity introduces a
material design choice, pause the affected work and use this skill for that choice.

## Authorization

A direct request to add, implement, change, or fix something already authorizes implementation within
the stated scope. Do not require a second approval merely because you summarized the approach.

Ask for a decision before implementation only when:

- multiple plausible choices would produce materially different outcomes;
- the recommended design expands or redirects the requested scope; or
- applicable repository or user instructions require design review.

When the user explicitly asks only to explore, discuss, or design, deliver the design without assuming
authorization to implement it. A user's selection of a proposed option counts as approval of that option.

## Workflow

1. Read applicable repository instructions and only enough relevant context to understand the decision.
2. Ask questions whose answers could materially change the design. Infer routine details from context;
   group closely related questions when that is easier to answer.
3. Offer multiple approaches only when they are genuinely distinct. Lead with the recommendation and
   explain the consequential trade-offs.
4. Present a design proportional to the uncertainty. Cover boundaries, interfaces, data flow, failure
   behavior, and verification only where relevant.
5. Resolve remaining material decisions. If the original request authorized implementation, continue
   without a ceremonial confirmation. If it requested discussion only, stop with the design and offer
   implementation as a separate next step.

For architecturally significant work in a roadmap-tracked repository, use `using-github-roadmap` as
required by repository policy. Write a durable specification only for architecture-scale work or when the
user requests one; follow repository instructions for its location and publication. Use `writing-plans`
after an accepted design when the implementation is sufficiently multi-step to benefit from a plan.
