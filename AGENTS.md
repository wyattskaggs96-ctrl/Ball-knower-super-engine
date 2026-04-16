# AGENTS.md

## Purpose
Ball Knower Engine is a creator-first sports content workflow tool. Keep changes fast to review, easy to ship, and useful for daily content production.

## Working rules
- Always start from a clean `main` before beginning work.
- One task = one focused change.
- Prefer additive edits over large refactors.
- Avoid unrelated file churn.
- Never leave merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).

## Product priority
Optimize for the daily creator workflow: idea to publish with minimal friction.

## Current phase
Execution-first: ship small, practical improvements that creators can use immediately.

## Repo expectations
- Keep diffs minimal and scoped.
- Preserve existing behavior unless the task explicitly changes it.
- Do not rename/move files unless required.

## Output expectations
Creator-facing outputs must be practical, concise, and easy to edit.

## Coding conventions
- Match existing project style and naming.
- Keep implementation straightforward; avoid overengineering.
- Add only the comments or docs needed to maintain clarity.

## Before opening a PR
- Confirm branch is up to date with `main`.
- Check changed files are directly related to the task.
- Run required checks/tests for touched code.
- Re-scan for conflict markers.

## Definition of done
Done means: focused diff, clean branch, passing checks, and a mergeable PR that improves creator workflow without extra complexity.
