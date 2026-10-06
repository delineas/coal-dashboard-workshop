---
name: spec-writer
description: Turn a feature request into an implementation-ready spec in docs/. First profile the repo code and data, then grill the user in rounds of multiple-choice questions (recommended option marked) until no implementation doubt remains, then write the spec with Given/When/Then acceptance criteria and an out-of-scope section, and commit it on a feature branch. Use this skill whenever the user asks for a spec, a requirements document, acceptance criteria, a PRD, or a design doc for a feature, or says "grill me", "fríeme a preguntas", "ask me until there are no doubts", "define the requirement", "turn what we decided into a spec", even if they do not say the word "spec".
---

# Spec writer

You turn a short requirement plus the project's own knowledge (code, data, docs, earlier decisions) into a spec that a developer can implement without asking more questions.

The spec is only as good as the decisions behind it. Most of the value comes from two things: you find the real facts before you ask, and you ask until each implementation choice has an owner. The document comes last.

## 0. Read the house rules

Before anything else, read `AGENTS.md`, `CLAUDE.md` and any files they import, plus `docs/` if it exists. Look for:

- The language to talk to the user in, and the language and style for written project content (for example, "ASD-STE100 Simplified Technical English").
- Branch naming (for example, `feature/` prefix), commit format, and whether commits carry signature lines.
- Where scratch documents go (for example, `.scratchpad/`).
- Existing specs, so the new one matches their structure.

Obey these rules for the full task. If there are no rules: talk in the user's language, write the spec in the user's language, use `docs/spec-<topic>.md`, and use Conventional Commits.

## 1. Profile before you ask

Questions grounded in real numbers get better answers and expose problems the user did not know about. So, before the first question, inspect what the requirement touches:

- **Code**: stack, entry points, existing patterns, the base project the user names, test and build commands.
- **Data**: for each data file, count rows, list columns, and check the things that break joins and totals — inconsistent categories (case, spelling), renamed values between versions, duplicate keys, empty or malformed rows, missing coordinates, keys that match across files and keys that do not. Write the profiling script in the session scratchpad and run it with `python3 -I`, passing data paths as arguments.

Give the user a short list of the facts that matter for the decisions (with numbers), then start the questions. Do not dump the full profile.

## 2. Grill the user in rounds

Use the AskUserQuestion tool. Each round has up to 4 questions; each question has 2–4 options.

- Put the option you recommend first and add "(Recommended)" to its label, translated to the conversation language (for example, "(Recomendada)").
- In each option description, give the consequence and the trade-off, with real numbers from the profile when you have them ("2,380 units only exist in 2023"). The user decides faster when the cost of each choice is visible.
- Do not ask what you can find out from the code or data. Ask only about decisions that belong to the user.
- Before each round, say in one line what this round covers.

Go from foundations to details, because later choices depend on earlier ones:

1. **Foundations**: base project or stack, how data gets in, the core definitions (what counts, what a key metric means).
2. **Data rules and edge cases**: normalization, matching across sources, bad rows, records present in one source only, null and zero cases.
3. **Views and interaction**: pages or routes, components, libraries, what each view shows.
4. **Interfaces and delivery**: API shape, payload size, tests, branch plan, merge strategy, generated files and git.
5. **Leftovers**: every doubt that is still open.

Adapt the surface of each round to the answers. When the user picks a non-recommended option, look for the consequences it creates and ask about them in the next round. (Example: the user picks a map library without native clustering colors, so the next round asks how clusters show categories.) When an answer opens a new edge case in the data, check it in the data, then ask.

Stop when you can answer "yes" to all of these:

- Each term in the requirement has one definition.
- Each data edge case found in the profile has a rule.
- Each view has its content, its route and its empty or not-found state.
- The libraries, API endpoints and storage are selected.
- The test level and the delivery plan (branches, merge) are selected.

If the user is in a hurry or stops the rounds early, do not continue to ask. Take the recommended option for each open point, write the spec, and list these points as "Decided by default" in the report so the user can change them.

If you make a small decision yourself instead of asking (for example, an allow list for two values), write it down and report it at the end. Hidden decisions cause surprises later.

## 3. Write the spec

**Read `references/spec-template.md` completely before you write.** It has the section structure and the rules for acceptance criteria. Load `references/ste-checklist.md` only if the house rules ask for ASD-STE100 or Simplified Technical English; otherwise do not load it.

- Write in the language and style from the house rules.
- Use tables for mappings, rules and endpoints. Put exact rules in the spec, not summaries ("`L17-` + first 8 hex chars of SHA-1 of `<plant>|<country>`", not "a stable ID").
- **Acceptance criteria** in Given / When / Then, grouped by area (data, API, UI, general), each with an ID (`AC-ETL-1`). Make them testable: use real values from the data (totals, counts, an example record for each edge case). Before you commit, run a script that recomputes every number you put in a criterion, so the spec does not contain a wrong value.
- **Out of scope**: list what the user declined in the questions, what the requirement could imply but you did not plan, and the things a reader could reasonably expect (other years, exports, auth, dark mode, i18n, deploy). A clear "no" prevents scope creep.
- **Open items**: decisions that are still pending, with the latest moment to decide them.

## Do not do these things

- **Do not trust column names or category values that you did not inspect.** Real files have trailing spaces in headers (`Plant `), mixed case in statuses (`Operating` / `operating`) and renamed categories between versions (`Turkey` / `Türkiye`). Each of these silently breaks a join or a total.
- **Do not ask a question that the data or the code can answer.** It wastes a round and shows that you did not look. Check first, then ask about the decision that the fact creates.
- **Do not offer options without consequences.** "Option A / Option B" with no trade-off makes the user guess. The description of each option must say what changes.
- **Do not change the recommended option after the user picks another one.** Accept the answer and ask about the new consequences in the next round. Do not try to convince the user.
- **Do not write the spec before the stop checklist passes**, except when the user is in a hurry (see above). A spec with "TBD" in a core rule moves the questions into the implementation, where they cost more.
- **Do not put unverified numbers in acceptance criteria.** A wrong total in a criterion makes a correct implementation fail its test. Recompute each number with a script.
- **Do not hide your own decisions.** Each choice you made without asking goes in the final report.
- **Do not merge the spec branch, and do not start implementation, without explicit approval.** The spec is a proposal until the user accepts it.

## 4. Deliver

- Create a branch with the house prefix (for example, `feature/<topic>-spec`), commit the spec as one atomic commit (for example, `docs(spec): add the <topic> spec`), and do not merge without user approval.
- Report to the user, in their language: where the spec is, the commit, a short list of its sections and the number of criteria, **the decisions you made yourself**, and a question about the next step (merge, review, start the first branch).
