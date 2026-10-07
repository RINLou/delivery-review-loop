# delivery-review-loop

A **framework-agnostic** 3-layer delivery review loop for any AI / coding agent: **contract → evidence → independent reviewer**. Not tied to any product.

> Originated from a user request (2026-10-07): apply a "goal + contract + independent review" closing loop to *all* of an agent's substantial work. Later rewritten to be portable across agent frameworks (WorkBuddy, Claude Code, Codex, Cursor, generic Agents SDK, …).

## The three layers

1. **Contract (定标准)** — for substantial tasks, write a short contract (goal / scope incl. "won't do" / verifiable acceptance criteria / key assumptions); confirm before acting.
2. **Evidence (证据说话)** — on delivery, attach verifiable evidence; "I think it's done" is forbidden.
3. **Independent review (独立挑刺)** — before delivery, by default spawn an independent reviewer that cannot see the main conversation; fix per its list, re-review; disclose any unresolvable fatal and let the human decide.

## When to run

- **Substantial**: produces files / changes code / runs commands / gives external conclusions / outputs data → full 3 layers (incl. independent reviewer).
- **Trivial**: one-liner, unambiguous, no file/command → skip contract, light self-check, no reviewer.

## Install / adapt

This skill is framework-agnostic. See **SKILL.md → "Adapt to your framework"** for mappings to DSH (DeepSeek Harness), WorkBuddy, Claude Code / Codex / Cursor, generic Agents SDK, and a no-sub-agent fallback.

Quick start (generic):
Paste `SKILL.md` into your agent's skill / instruction set, and wire Layer 3 to your framework's sub-agent mechanism (see "Adapt to your framework").

Quick start (WorkBuddy example):
```bash
mkdir -p ~/.workbuddy/skills/delivery-review-loop
cp SKILL.md ~/.workbuddy/skills/delivery-review-loop/
```
For cross-session enforcement on WorkBuddy, also add a "工作闭环" section to your `SOUL.md` (persona file).

## Architecture honesty

There is **no system-level forced hook**. Enforcement relies on the loop living in your agent's system prompt + this skill being loaded + a mandatory self-check block in every delivery. Skipping it raises no alert — it's discipline.

## License

MIT
