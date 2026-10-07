---
name: delivery-review-loop
description: A framework-agnostic 3-layer delivery review loop (contract → evidence → independent reviewer) for any AI/coding agent. Load this skill whenever a task produces files, changes code, runs commands, gives external conclusions, or outputs data — to enforce a quality gate before delivery.
---

# Delivery Review Loop（交付审查闭环）

A portable quality-closing loop **any AI agent can adopt**. Not tied to any product. Core idea (from a "goal + contract + independent review" workflow): before you declare any substantial work done, (1) agree on a written contract, (2) show evidence it's actually done, (3) have an *independent* reviewer — one that cannot see the main conversation — poke holes.

> ⚠️ Architecture honesty: there is **no system-level forced hook** (no pre-commit, no CI gate, no hard pre-delivery block). Enforcement relies on: ① the loop being written into the agent's system prompt / persona file (so it's reminded every session), ② this skill being actively loaded, ③ a mandatory self-check block in every delivery message. If the loop is skipped, nothing alerts you — it's discipline, not a mechanism.

## When to run the loop
- **Substantial tasks** (run the full 3 layers, including the independent reviewer): anything that produces files, changes code, runs commands, gives external-facing conclusions, or outputs data.
- **Trivial tasks** (skip the contract, light self-check only, no independent reviewer): one-liner, unambiguous, no file/command changes (e.g. "translate this sentence"). If unsure whether it's substantial, default to writing a contract.

## The three layers

### Layer 1 — Contract (定标准)
Trigger: only for substantial tasks.
- Write a short contract using the **Contract template** below; get the human's confirmation before acting.
- Four required elements: Goal / Scope (incl. explicit "won't do") / Verifiable acceptance criteria / Key assumptions.
- No filler, no long preamble; bullet list is fine.

### Layer 2 — Evidence (证据说话)
On delivery, you **must** attach verifiable evidence. "I think it's done" is forbidden.
- Code: real output of tests/build/lint (`pytest` green, `tsc --noEmit` passes, `node --check` passes).
- Data: extraction caliber, field mapping, verification by **back-checking against known real values**; state mismatches explicitly, never fabricate (see "numbers must add up").
- Docs/analysis: sources, basis, derivation chain for key conclusions.
- Judgment/consulting tasks ("is this plan OK?", "which to pick?"): evidence must include at least [source of basis + counterexamples ruled out]; never just a conclusion.
- Insufficient evidence → **do not claim done**; go get the evidence.

### Layer 3 — Independent review (独立挑刺)
Before delivering any substantial task, **by default** spawn an independent reviewer (note: not automatic by the system — enforced by this skill). Key: the reviewer **cannot see the main conversation history**; it only gets "contract + deliverables + original requirement", so it's truly independent. Self-reviewing = no review.
- How to spawn (framework-specific — see "Adapt to your framework" below): e.g. WorkBuddy `Agent` tool in plan mode; Claude Code/Codex subagent; a fresh context with materials pasted in.
- The reviewer returns a structured issue list (fatal / important / minor + fix suggestions).
- **You fix per the list → re-run the reviewer.** If a fatal item can't be cleared after one fix round (needs human decision / lacks external resource / is a design-level flaw you can't fix), then **stop retrying, disclose the fatal item and why, transparently, and let the human decide deliver-vs-rollback**. Do not fake-clear or loop forever. Only after confirming no fatal do you formally deliver, and attach the reviewer's final conclusion.

## Contract template (copy-fill)
```
【Task Contract】
Goal: <one sentence>
Scope: do <A, B, C>; explicitly NOT do <X, Y, Z>
Acceptance criteria (verifiable):
  1. <testable condition, e.g. "pytest all green" / "output file exists and contains field F" / "data back-checked against 3 known values, all match">
  2. ...
Key assumptions: <preconditions, e.g. "source format unchanged" / "network available">
```
> Paste the contract in the conversation for the human to confirm. Skip for trivial tasks.

## Independent reviewer prompt template (copy-fill)
```
You are a strict, independent deliverables reviewer. You **cannot see** the main conversation history; you only review from the materials below. Do NOT modify any files.
**This review sub-agent does not load the delivery-review-loop skill and spawns no further sub-agents (prevent recursion).**

## Task contract (standard)
<paste the contract: goal / scope incl. won't-do / acceptance criteria / key assumptions>

## Original requirement (one sentence)
<brief original requirement>

## Deliverables to review (Read these files/paths first)
<one path per line: code files, generated artifacts, data files, etc.>
**Lightweight instruction**: only Read parts directly relevant to the acceptance criteria; for large files (>200 lines or >50KB) don't read line-by-line, skim key functions/boundaries to save cost.

## Your job
1. Against the contract's acceptance criteria, judge line-by-line whether deliverables truly meet them. Mark insufficient evidence as "insufficient".
2. Find logic errors, missing edge cases, uncovered exceptions, scope over/under-runs vs the contract.
3. Verify evidence is real and sufficient (tests actually run? data actually back-checked? conclusions sourced?).
4. **Review only, don't fix**: don't modify files; read-only verification (e.g. `node --check`, read files, run a test to see output) is fine, but never write to disk, never call edit tools.

## Output format (strict)
### Fatal issues (must fix before delivery)
- [description + why fatal + fix suggestion]
### Important issues (should fix)
- ...
### Minor / suggestions
- ...
### Evidence check
- AC1: met / not met / insufficient (basis…)
- AC2: …
### Overall conclusion
Pass / Needs revision (fatal N · important M)
```

## Adapt to your framework
The three layers are framework-agnostic. Map the mechanisms to your tooling:

- **WorkBuddy**: install to `~/.workbuddy/skills/delivery-review-loop/`; load via the Skill tool. For cross-session enforcement, also add a "工作闭环" section to `SOUL.md` (persona). Independent reviewer = `Agent` tool with `subagent_type=general-purpose`, `mode=plan` (read-only), `max_turns=8`; in the prompt explicitly state the reviewer does not load this skill and spawns no sub-agents.
- **Claude Code / Codex / Cursor**: use the platform's sub-agent / `/review` / separate-context feature. Paste the contract + deliverable paths into the sub-agent; forbid it from reading the main thread. Write the loop into `CLAUDE.md` / agent config for cross-session recall.
- **Generic Agents SDK (OpenAI Agents, LangGraph, etc.)**: implement Layer 3 as a separate agent/context with no access to the orchestrator's message history; hand it only the contract + artifact references.
- **No sub-agent support?** Fallback: do Layer 1 + Layer 2, then a written self-check list (possible failure points / boundaries / unverified items) for the human to sign off. Less rigorous, but better than nothing.

## Notes
- The reviewer is read-only; still emphasize "review only, don't fix" in the prompt (double safety), and explicitly forbid loading this skill / spawning sub-agents (prevent recursion).
- If the reviewer misjudges due to missing context, include its question and your explanation as evidence, then decide — don't blindly obey, don't ignore.
- The loop costs time + tokens, but for substantial tasks the cost of one wrong delivery >> the cost of prevention. If the human says "skip the reviewer this time", downgrade to Layer 2 + self-check list.
- **Every delivery message must include a mandatory self-check block (not optional)**: ① whether a contract was issued / why skipped ② evidence highlights ③ reviewer conclusion (fatal/important counts, cleared?; any undisclosed fatal must be transparently disclosed). Missing it = loop not finished. For trivial tasks the block still appears, but ③ simply reads "no independent reviewer (trivial)" — lightweight, not a full review.
