# Agent rules

These rules apply to all agents that work in this repository.

## Language

- Talk to the user in Spanish. Use simplified technical Spanish.
- Write all project content in English. This includes code, comments, documentation, specs, plans, ADRs, commit messages and pull requests.
- Use ASD-STE100 Simplified Technical English for all project content.

## Branches

- Use one branch for each feature.
- Start the branch name with `feature/`. Do not use `feat/`.

## Commits

- Make small, atomic commits.
- Use the Conventional Commits format.
- Do not add signature or co-author lines (for example, `Co-Authored-By`).

## Code

- Do not write comments that repeat what the code does.
- Do not add defensive checks that the domain does not need.
- Use `tools/codegraph.py` (run `build` first) before you read whole files. Use `find`, `outline`, `show`, `callers` and `endpoint` to locate code.

## Decisions

- Write an ADR in `docs/decisions/` when you add a dependency or an architecture pattern, or when you make a decision that is hard to reverse.
- State in the ADR if the decision is reversible.
- Do not write an ADR for a routine fix or for a preference that a linter already checks.

## Plans

- Make each step small. Each step adds one thing and is integrated with the previous steps.
- Do not leave orphan code. Each export must have a user.

## Browser tools

- Do not use the Chrome DevTools MCP unless the user gives permission for the task.
- Use the test suite and `curl` to check your work in all other cases.

## Work documents

- Put work documents that you do not need after the session in `.scratchpad/`.
- Git ignores `.scratchpad/`. Do not commit its contents.
