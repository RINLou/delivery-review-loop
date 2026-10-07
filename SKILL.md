---
name: delivery-review-loop
description: A framework-agnostic 3-layer delivery review loop (contract -> evidence -> independent reviewer) for any AI/coding agent. Load this skill whenever a task produces files, changes code, runs commands, gives external conclusions, or outputs data — to enforce a quality gate before delivery. Ships a validator script + CI/pre-commit hooks so the self-check becomes mechanical, not just disciplinary.
---

# Delivery Review Loop（交付审查闭环）

A portable quality-closing loop **any AI agent can adopt**. Not tied to any product. Core idea (from a "goal + contract + independent review" workflow): before you declare any substantial work done, (1) agree on a written contract, (2) show evidence it's actually done, (3) have an *independent* reviewer — one that cannot see the main conversation — poke holes.

> ⚠️ Architecture honesty: by itself there is **no system-level forced hook** (no pre-commit, no CI gate, no hard pre-delivery block) — skipping the loop raises no alert, it's discipline. **This version ships a mechanism to close that gap** (see "From discipline to mechanism"): `validate_delivery.py` + a pre-commit hook (and an optional CI gate you can enable) make the self-check *mechanical* wherever deliveries are files/PRs. For chat-only deliveries (no artifact file) the self-check stays disciplined text — the mechanism can't parse a chat, so the honesty note still applies there.

## When to run the loop

Decision test — a task is **substantial** if ANY of these is true:
- writes or modifies files / code
- runs shell commands or scripts
- produces data or other outputs (reports, generated artifacts)
- gives an external-facing or consequential conclusion (goes to a user, a client, or production)

If none apply → **trivial** (one-liner, unambiguous, no file/command/output, no external conclusion): skip the contract, light self-check only, no independent reviewer. When in doubt, write a contract — over-reviewing a trivial task costs little, under-reviewing a substantial one costs a lot.

## The three layers

### Layer 1 — Contract (定标准)
Trigger: only for substantial tasks.
- Write a short contract using the **Contract template** below; get the human's confirmation before acting.
- Four required elements: Goal / Scope (incl. explicit "won't do") / Verifiable acceptance criteria / Key assumptions.
- No filler, no long preamble; bullet list is fine.
- **Confirmation fallback (unattended / async / no human reply)**: if the human is unreachable or doesn't respond within the agreed window, proceed under a **provisional contract** (self-approved) — but label it `"contract NOT human-confirmed"` in the delivery and document the assumptions you ran with. Do not silently skip the contract.

### Layer 2 — Evidence (证据说话)
On delivery, you **must** attach verifiable evidence. "I think it's done" is forbidden.
- Code: real output of tests/build/lint (`pytest` green, `tsc --noEmit` passes, `node --check` passes).
- Data: extraction caliber, field mapping, verification by **back-checking against known real values**; state mismatches explicitly, never fabricate.
- Docs/analysis: sources, basis, derivation chain for key conclusions.
- Judgment/consulting tasks ("is this plan OK?", "which to pick?"): evidence must include at least [source of basis + counterexamples ruled out]; never just a conclusion.
- **Acceptance-criteria evidence matrix** (attach on delivery): a table mapping each acceptance criterion to its evidence source and a verified Y/N. See the contract template. This is the "AC evidence matrix" that turns vague "evidence" into a checkable grid.
- **Insufficient / unobtainable evidence → block delivery and escalate to the human.** Do not downgrade to "done" or claim completion on faith. State exactly what evidence is missing and why (external resource down, no access, etc.).

#### Numbers must add up（数字必须对得上）
When the deliverable contains quantities, money, counts, rates, or any computed figure, you must back-check before claiming correctness:
- State the caliber/source of every number (where it came from, how computed).
- Cross-verify against at least one independent **known real value**; if it doesn't reconcile, say so — never silently adjust to "make it match".
- Fabricating or rounding to hide a mismatch = fatal.

### Layer 3 — Independent review (独立挑刺)
Before delivering any substantial task, **by default** spawn an independent reviewer (note: not automatic by the system — enforced by this skill + the hooks below). Key: the reviewer **cannot see the main conversation history**; it only gets "contract + deliverables + original requirement", so it's truly independent. Self-reviewing = no review.
- How to spawn (framework-specific — see "Adapt to your framework" below): e.g. DSH `subagent` (a separate context that cannot see this conversation — **never `subagent_fork`**, it inherits every completed turn and independence drops to zero); WorkBuddy `Agent` tool in plan mode; Claude Code/Codex subagent; a fresh context with materials pasted in.
- The reviewer returns a structured issue list (fatal / important / minor + fix suggestions).
- **You fix per the list → re-run the reviewer.** If a fatal item can't be cleared after one fix round (needs human decision / lacks external resource / is a design-level flaw you can't fix), then **stop retrying, disclose the fatal item and why, transparently, and let the human decide deliver-vs-rollback**.

#### Material-selection bias (the reviewer only sees what you choose to show)
To keep the review *independent* and not just *isolated from chat history*:
- Pass the **original raw user message verbatim** (not your paraphrase) as "Original requirement".
- Pass an explicit **Excluded materials** list: what you did NOT show the reviewer and why (e.g. "internal logs, unrelated modules"). If nothing was excluded, state `"none"`.
- Instruct the reviewer to challenge the contract itself if the raw requirement appears mis-scoped — it must be able to flag "the contract misunderstood the ask", not just "the deliverable missed the contract".

#### Non-mutating verification (resolves the read-only vs run-tests contradiction)
- The reviewer does **review only, don't fix**: it must not edit deliverable files and must not call edit tools.
- It **MAY run non-mutating checks** that don't change deliverables or repo state: `node --check`, `python -m py_compile`, `tsc --noEmit`, or `pytest` with `--basetemp` pointed at an **OS temp dir that is cleaned up afterward**.
- It MUST NOT write to the project/repo tracked directories. Any temporary artifact goes only to OS temp and is removed before the reviewer replies. (This replaces the old contradictory "never write to disk" with a precise rule.)

#### Fatal handling — formal vs override delivery
- **Formal delivery** = zero fatal cleared.
- If a fatal cannot be cleared and the human decides to deliver anyway, you MUST label the delivery **`DELIVERED WITH UNCLEARED FATAL (human override)`** and list the fatal verbatim in the self-check block. Do not call it a clean pass.
- Only after confirming no fatal (or an explicit human override, labeled as above) do you attach the reviewer's final conclusion.

## From discipline to mechanism

The self-check is "must" by norm. To make it *mechanical* wherever deliveries are files/PRs, this repo ships two enforceable artifacts:
- **`validate_delivery.py`** — parses a delivery artifact (markdown) and exits **non-zero** if the mandatory self-check block (contract / evidence / reviewer) is missing. Run locally or in CI.
- **`hooks/delivery-gate.sh`** — optional git pre-commit hook; blocks commit if a staged `DELIVERY.md` fails validation.

**Optional CI gate** (not committed here): `.github/workflows/review-gate.yml` is provided in the repo working tree but cannot be pushed with a PAT lacking the `workflow` scope. To enable it, either paste the file into GitHub's web UI (Actions → New workflow) or push with a PAT that has the `workflow` scope. It validates `DELIVERY.md` on PR/push and blocks merge on a missing self-check.

> Note: the validator is **structural only** — it confirms the self-check block exists and contains the three required elements; it cannot verify the contract was truly human-confirmed, the evidence is real, or an independent review actually happened. Pair it with human sign-off for high-risk deliveries.

For chat-only deliveries (no artifact file) the self-check remains disciplined text — the mechanism can't parse a chat. Wire the validator into your pipeline by writing deliveries that matter to a `DELIVERY.md` (or equivalent) so the hook can enforce them.

## Contract template (copy-fill)
```
【Task Contract】
Goal: <one sentence>
Scope: do <A, B, C>; explicitly NOT do <X, Y, Z>
Acceptance criteria (verifiable):
  1. <testable condition, e.g. "pytest all green" / "output file exists and contains field F" / "data back-checked against 3 known values, all match">
  2. ...
Key assumptions: <preconditions, e.g. "source format unchanged" / "network available">

Acceptance-criteria evidence matrix (fill on delivery):
  | AC# | Criterion            | Evidence source            | Verified |
  | 1   | pytest all green     | ci run #123 / local output  | ✅       |
  | 2   | output contains F    | grep F out.json             | ✅       |
```
> Paste the contract in the conversation for the human to confirm. Skip for trivial tasks (or use the confirmation fallback above).

## Independent reviewer prompt template (copy-fill)
```
You are a strict, independent deliverables reviewer. You **cannot see** the main conversation history; you only review from the materials below. Do NOT modify any deliverable files and do NOT call edit tools.
**This review sub-agent does not load the delivery-review-loop skill and spawns no further sub-agents (prevent recursion).**

## Rating rubric (apply consistently)
- Fatal: breaks a verifiable acceptance criterion, leaks a secret, or makes the deliverable unsafe/wrong to use. Must fix before delivery.
- Important: real defect or missing requirement, not fatal but should fix.
- Minor: style, clarity, suggestion.

## Task contract (standard)
<paste the contract: goal / scope incl. won't-do / acceptance criteria / key assumptions>

## Original requirement (VERBATIM — paste the human's raw message, do not paraphrase)
<raw user message>

## Excluded materials (what was NOT shown to you, and why; "none" if nothing)
<list or "none">

## Deliverables to review (Read these files/paths first)
<one path per line: code files, generated artifacts, data files, etc.>
**Lightweight instruction**: only Read parts directly relevant to the acceptance criteria; for large files (>200 lines or >50KB) don't read line-by-line, skim key functions/boundaries to save cost.

## Your job
1. Against the contract's acceptance criteria, judge line-by-line whether deliverables truly meet them. Mark insufficient evidence as "insufficient".
2. Compare the raw requirement vs the contract: if the contract mis-scoped the ask, flag it as a fatal/important (the reviewer must catch contract-level misunderstanding, not just deliverable-vs-contract gaps).
3. Find logic errors, missing edge cases, uncovered exceptions, scope over/under-runs vs the contract.
4. Verify evidence is real and sufficient (tests actually run? data actually back-checked? conclusions sourced? numbers reconciled against known values?).
5. **Review only, don't fix**: don't edit deliverable files, don't call edit tools. You MAY run non-mutating checks (`node --check`, `python -m py_compile`, `tsc --noEmit`, `pytest --basetemp <os-temp>` cleaned up after). You MUST NOT write to the project/repo tracked directories.

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

- **DeepSeek Harness (DSH)**: drop this skill into the user skill root `~/.agents/skills/delivery-review-loop/SKILL.md` — DSH picks it up live, no restart and no plugin required (the directory is created on first use). Alternatively ship it inside a plugin package as `<pkg>/skills/<name>/SKILL.md`, registered through the host-provided `@deepseek-ai/dsh-skill` service. Independent reviewer = the `subagent` tool (separate context, cannot see this session); **do not use `subagent_fork`** (it inherits all completed turns, so independence drops to zero), and do not use an Agency expert/team as the reviewer because fork providers may inherit context. For cross-session recall, write the loop into the DSH system prompt / persona config.
- **WorkBuddy**: install to `~/.workbuddy/skills/delivery-review-loop/`; load via the Skill tool. For cross-session enforcement, also add a "工作闭环" section to `SOUL.md` (persona). Independent reviewer = `Agent` tool with `subagent_type=general-purpose`, `mode=plan` (read-only), `max_turns=8`; in the prompt explicitly state the reviewer does not load this skill and spawns no sub-agents. The validator/hook can be wired into a pre-delivery step.
- **Claude Code / Codex / Cursor**: use the platform's sub-agent / `/review` / separate-context feature. Paste the contract + raw requirement + deliverable paths into the sub-agent; forbid it from reading the main thread. Write the loop into `CLAUDE.md` / agent config for cross-session recall. Wire `validate_delivery.py` as a CI step or pre-commit.
- **Generic Agents SDK (OpenAI Agents, LangGraph, etc.)**: implement Layer 3 as a separate agent/context with no access to the orchestrator's message history; hand it only the contract + raw requirement + artifact references + excluded-materials list.
- **No sub-agent support?** Fallback: do Layer 1 + Layer 2, then a written self-check list (possible failure points / boundaries / unverified items) for the human to sign off. Less rigorous, but better than nothing.

## Notes
- The reviewer is read-only; still emphasize "review only, don't fix" in the prompt (double safety), and explicitly forbid loading this skill / spawning sub-agents (prevent recursion).
- If the reviewer misjudges due to missing context, include its question and your explanation as evidence, then decide — don't blindly obey, don't ignore.
- The loop costs time + tokens, but for substantial tasks the cost of one wrong delivery >> the cost of prevention. If the human says "skip the reviewer this time", downgrade to Layer 2 + self-check list (and label it).
- **Every delivery message must include a mandatory self-check block (not optional)**: ① whether a contract was issued / why skipped (or "provisional, NOT human-confirmed") ② evidence highlights (incl. AC matrix summary) ③ reviewer conclusion (fatal/important counts, cleared?; any undisclosed fatal must be transparently disclosed; if delivered with uncleared fatal, label it). Missing it = loop not finished. For trivial tasks the block still appears, but ③ simply reads "no independent reviewer (trivial)" — lightweight, not a full review.
- **Mechanism-level enforcement**: for file/PR deliveries, run `validate_delivery.py` (or the CI/pre-commit hook) so a missing self-check block fails the gate instead of relying on memory. This is how flaw #1 ("must" is only normative) is closed where tooling permits.
