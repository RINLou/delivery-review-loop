# delivery-review-loop

A **framework-agnostic** 3-layer delivery review loop for any AI / coding agent: **contract → evidence → independent reviewer**. Not tied to any product.

> Originated from a user request (2026-10-07): apply a "goal + contract + independent review" closing loop to *all* of an agent's substantial work. Later rewritten to be portable across agent frameworks (WorkBuddy, DeepSeek Harness / DSH, Claude Code, Codex, Cursor, generic Agents SDK, …), then hardened against an external structural review (see "Hardening notes" below).

## The three layers

1. **Contract (定标准)** — for substantial tasks, write a short contract (goal / scope incl. "won't do" / verifiable acceptance criteria / key assumptions); confirm before acting.
2. **Evidence (证据说话)** — on delivery, attach verifiable evidence; "I think it's done" is forbidden. Include an acceptance-criteria evidence matrix.
3. **Independent review (独立挑刺)** — before delivery, by default spawn an independent reviewer that cannot see the main conversation; pass the raw requirement verbatim + an excluded-materials list; fix per its list, re-review; disclose any unresolvable fatal and let the human decide.

## When to run

- **Substantial** (any of): writes/modifies files · runs commands · produces data/outputs · gives external-facing or consequential conclusions → full 3 layers (incl. independent reviewer).
- **Trivial**: one-liner, unambiguous, no file/command/output, no external conclusion → skip contract, light self-check, no reviewer.

## Install / adapt

This skill is framework-agnostic. See **SKILL.md → "Adapt to your framework"** for mappings to DeepSeek Harness (DSH), WorkBuddy, Claude Code / Codex / Cursor, generic Agents SDK, and a no-sub-agent fallback.

Quick start (generic):
Paste `SKILL.md` into your agent's skill / instruction set, and wire Layer 3 to your framework's sub-agent mechanism (see "Adapt to your framework").

Quick start (WorkBuddy example):
```bash
mkdir -p ~/.workbuddy/skills/delivery-review-loop
cp SKILL.md ~/.workbuddy/skills/delivery-review-loop/
```
For cross-session enforcement on WorkBuddy, also add a "工作闭环" section to your `SOUL.md` (persona file).

Quick start (DeepSeek Harness example):
```bash
mkdir -p ~/.agents/skills/delivery-review-loop
cp SKILL.md ~/.agents/skills/delivery-review-loop/
```
DSH picks the skill up live (no restart/plugin needed). Independent reviewer = the `subagent` tool — **never `subagent_fork`** (it inherits all turns and kills independence).

## Enforcement: from discipline to mechanism

The self-check is "must" by norm. This repo ships three artifacts that make it *mechanical* wherever deliveries are files/PRs:

- **`validate_delivery.py`** — parses a delivery markdown and exits non-zero if the mandatory self-check block (contract / evidence / reviewer) is missing. Stdlib-only.
  ```bash
  python3 validate_delivery.py DELIVERY.md          # gate on the 3 required elements
  python3 validate_delivery.py DELIVERY.md --strict # also require an AC evidence matrix
  ```
- **`.github/workflows/review-gate.yml`** — CI gate: on PR/push to `main`, if `DELIVERY.md` exists at repo root, validates it (strict); blocks merge on a missing self-check. Opt-in (skips if no `DELIVERY.md`).
- **`hooks/delivery-gate.sh`** — optional git pre-commit hook; blocks commit if a staged `DELIVERY.md` fails validation.
  ```bash
  cp hooks/delivery-gate.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
  ```

For chat-only deliveries (no artifact file) the self-check stays disciplined text — wire important deliveries to a `DELIVERY.md` so the hook can enforce them.

## Architecture honesty

There is **no system-level forced hook by default** — skipping the loop raises no alert, it's discipline. The validator + CI/pre-commit hooks above close that gap *where tooling permits* (file/PR deliveries). For pure-chat deliveries the honesty note from SKILL.md still applies.

## Hardening notes (2026-10-07 external review)

An external reviewer found the original version was "discipline, not a closed loop". Five structural flaws were fixed:
1. *Normative "must" vs no forced hook* → added `validate_delivery.py` + CI/pre-commit (mechanism-level enforcement).
2. *Reviewer only isolated from chat, not from material-selection bias* → prompt now requires the **raw requirement verbatim** + an **excluded-materials list**, and lets the reviewer challenge the contract itself.
3. *"Never write to disk" vs "run a test" contradiction* → replaced with a precise **non-mutating verification** rule (`--basetemp` to OS temp, cleaned up; no writes to tracked dirs).
4. *Dangling "see numbers must add up" reference* → added the **"Numbers must add up"** subsection under Layer 2.
5. *Fatal handling wording contradiction* → formal delivery = zero fatal; human override must be labeled **`DELIVERED WITH UNCLEARED FATAL (human override)`**.

Plus soft-tension fixes: contract-confirmation fallback (provisional, unconfirmed label), a clearer substantial/trivial decision test, evidence-unobtainable escalation (block + escalate), and an embedded reviewer rating rubric for consistent judgments.

## License

MIT
