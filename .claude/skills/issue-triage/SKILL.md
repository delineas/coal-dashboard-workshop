---
name: issue-triage
description: Triage an issue (severity, owner team, architecture layers with file:line, work path) and then verify that it is real by reproducing every claim with tests, scripts or curl, without changing the code. Use this skill whenever the user asks to triage, classify, assess, prioritize or analyze an issue, ticket or bug report ("haz triaje de la issue #N", "qué gravedad tiene", "quién se encarga de esto", "qué capas toca", "comprueba que el bug es real", "reproduce this issue", "is this bug real?", "what path does this issue follow"), or pastes a bug report and asks what to do with it, even if the word "triage" does not appear. Use it before any fix, plan or spec for an issue.
---

# Issue triage and verification

This skill has two phases:

1. **Triage**: read the issue and the code, then classify the issue.
2. **Verification**: reproduce each claim in the issue and find the real root cause.

The user can ask for one phase or for both. If they ask only for triage, stop after phase 1 and offer the verification in one line.

Do not change project code, data or configuration in either phase. Triage is an input to a decision. If you fix something during triage, the user cannot make that decision. Put all temporary files (rebuilt databases, logs, scripts) in the scratchpad directory or in the work-documents directory that the repository rules name.

Follow the rules of the repository (AGENTS.md, CLAUDE.md). They can forbid tools (for example a browser) or set the language of the answer.

## Phase 1: Triage

### 1. Read the full issue

Use `gh issue view <N> --json title,body,labels,comments,author`. The plain `gh issue view` can fail on some repositories. Read the comments too. Make a list of the separate claims in the issue: each "Actual" line, each number, each "other cases" item. You verify each claim separately in phase 2.

### 2. Find the layers

Discover the architecture of this repository. Do not assume a stack. Look at the README, the specs, the ADRs and the directory tree. A typical data application has these layers:

source data → ETL or import → database or storage → API → frontend

Other repositories can have other layers (queue, worker, cache, CLI). Use the real layers of the repository.

For each layer, follow the data of the issue from the screen back to the source. Identify the role of each layer:

- **Cause**: the layer makes the wrong value or the wrong behavior.
- **Propagates**: the layer changes or combines the wrong value (for example a view that aggregates it).
- **Shows**: the layer makes the problem visible (for example two numbers from different fields side by side).
- **Passes through**: the layer only moves the data. Say so explicitly. This prevents a fix in the wrong place.

Give `file:line` for each layer that has a role. For source data, give the file and the row key (the ID), because line numbers in large data files are not useful.

Look at the raw source data, not only at the code. Many bugs come from a wrong assumption about the data (an ID that is reused, a row that is missing, a renamed category). The code can be correct for the data that the developer expected.

For a performance issue, follow the time, not only the data. The causes are often in the order of the work, not in one layer. Find out:

- Which requests the page makes, and which request must finish before the next one starts (a component that mounts only after other data arrives makes a waterfall).
- Which components fetch data while they are hidden with CSS. They still mount and fetch.
- What the build includes in the first load (one chunk, or code splitting).
- If the server compresses responses. Look for a middleware or a proxy configuration. If deployment is out of scope, nobody owns compression in production. That is a product decision.
- What happens only in development mode (for example React `StrictMode` runs each effect two times). Ask in which mode the reporter measured.

Look for causes that the issue does not name. A reporter lists what DevTools shows. A waterfall does not show as one line in the list.

### 3. Classify

**Severity**: one of critical, high, medium or low, with one sentence of reason.

| Severity | Use it when |
|---|---|
| Critical | The application is not available, data is lost or corrupted, or there is a security problem. |
| High | The application shows wrong results that users trust, or the error spreads to aggregates, or a main flow is blocked. |
| Medium | A feature is incomplete or difficult to use, but the results are correct and there is a workaround. |
| Low | Cosmetic problem, small improvement or internal quality work with no user effect. |

Wrong numbers in an analytics product are usually high. A contradiction on the screen makes users distrust all the numbers, not only the wrong one.

**Owner team**: one of data, backend, frontend or product. Choose the team that owns the cause, not the team that shows the symptom. If the expected behavior is not defined, the owner is product.

**Path**: choose one main path. If the issue mixes causes, name the main path and list the secondary parts with their own path.

| Path | Use it when | Verification method |
|---|---|---|
| Bug | The code does not do what the spec or the obvious intent says. | A failing test or a request that gives the wrong result. |
| Data bug | The code does what the spec says, but the source data breaks an assumption of the code. | Compare the raw rows with the stored and the served values. |
| Requirement | The expected behavior is not defined, or the issue asks for new behavior. | Find the gap in the spec. List the questions for product. |
| Interface | The data is correct, but the presentation is wrong or difficult to use. | Show that the API data is correct. Find the component and the styles. |
| Legacy | The code works but it has no tests or it is difficult to change safely. | Find the untested rules and the existing test setup. |
| Performance | The result is correct, but it is too slow or too large. | Measure: time, payload size, number of requests, query plan. |

If a performance issue gives a target (for example "less than 2 s") and the spec has no target, add a secondary requirement path. Product must set the target and the network profile, or the fix has no acceptance criterion.

To separate bug from data bug: if you can describe the wrong behavior with the words of the spec ("the spec says X, the code does Y"), it is a bug. If you need the words "the data has a case that nobody expected", it is a data bug.

## Phase 2: Verification

The goal is to show the evidence for each claim. Do not stop at "I can reproduce it": an issue can contain one real problem, one wrong claim and one different problem.

### 1. Make sure that the state is fresh

Generated artifacts (databases, caches, builds) can be older than the code. Rebuild them in the scratchpad and compare them with the current ones. If the values are the same, you know that the result does not come from old state. Do not overwrite the project artifacts.

- Call the build function of the ETL with an output path in the scratchpad, instead of the CLI entry point that writes the project file.
- If the application reads a fixed path (for example a module constant `DB_PATH`), start the server from a wrapper script in the scratchpad. The script sets the path to the rebuilt artifact and then starts the server. Do not edit the configuration.
- Build the frontend with an output directory in the scratchpad (for example `vite build --outDir <scratchpad>/dist --emptyOutDir`).
- Run `git status` at the end to show that the working tree has no changes.

### 2. Reproduce at the layer that the user sees

Use the test suite, scripts and `curl` against the API. If a server is necessary and it is not running, start it on a free port that the project does not use, in the background, with its log in the scratchpad. Wait until it answers (poll; do not use a fixed sleep), and stop it when you are done. Do not stop servers that the user started.

Use a browser only if the repository rules and the user permit it.

For a performance issue without a browser, measure each part and add the parts into a time budget:

- Size: `curl -s -o /dev/null -w "%{size_download}"`. Then send `Accept-Encoding: gzip, br` and look at `content-encoding` and `content-length` in the headers. Measure the compressed size with `gzip -6 | wc -c` to show the possible gain.
- Slow network: `curl --limit-rate` simulates only the bandwidth. Add the round-trip time for each request yourself. DevTools "Slow 4G" is about 1.6 Mbps (200 kB/s) and 562.5 ms latency.
- Budget: add the transfer time and the latency for each request that must wait for the previous one (HTML → JS → first data → data that depends on it). If the sum is near the number in the issue, the waterfall explains the symptom.
- Count requests from the code when you cannot use a browser: list each component that fetches the same URL on the same route. Mark the verdict as "confirmed by code".

Check the units. DevTools shows kB with base 1024 in some places: 454,685 bytes is "444 kB". Write the bytes in the report.

### 3. Check each claim separately

For each claim, record one of these verdicts:

- **Confirmed**: the evidence shows the claim.
- **Confirmed, different cause**: the symptom is real, but the cause is not the same as in the main case.
- **Not reproduced**: the evidence contradicts the claim. Say what the evidence shows and a possible reason (an older version, a client-side filter, a wrong step in the issue). Do not change your conclusion without evidence.
- **Not checked**: say why.

Add the causes that you found and that the issue does not name as extra rows, with the verdict "new".

Check the "other cases" of the issue too. They often look the same but have a different root cause. A different cause can mean a different owner or a different path.

### 4. Separate code problems from decisions

Some causes are not defects. They are questions that a person must answer (for example "does a mothballed unit count as capacity?"). Mark them as product decisions. Do not hide them in the bug fix.

## Report

Write the report in the language of the conversation. Keep it short. Use this structure:

**Triage**
1. Severity: level, and one sentence of reason.
2. Owner team, and why.
3. Layers: the number of layers with a role and their names. Then one line per layer with its role and `file:line`. Include the layers that only pass the data through.
4. Path, and the secondary paths if the issue has more than one.

**Verification**
- One line that says if the bug is real.
- A table or list of claims with verdict and evidence (values from the requests or queries).
- The causes, in groups: code or data defects, and decisions for product.
- What you did not check, and what you did to clean up (server stopped, files in the scratchpad).

Do not propose a fix unless the user asks. If a fix direction is obvious, give it in one line at the end.

## Example

Issue: "A 'Retired' plant shows 125 MW → 125 MW in 2023. The country table shows 824 → 824 MW but −125 MW with a down arrow."

Triage result:
- Severity high: the same page shows a label and numbers that contradict each other, and the error goes into the country total.
- Owner data: the ETL joins the 2017 and 2023 units by tracker ID, and the 2023 CSV uses the same ID for a different unit.
- Layers 4 of 5: source data (cause, CSV rows `G107694` and `G113456`), ETL (cause, join at `etl.py:241-249`), database views (propagate, `etl.py:81-89`), API (passes through, `main.py:54`), frontend (shows, the label uses comparable values and the numbers use totals, `PlantPage.tsx:35-37`).
- Path: data bug.

Verification result:
- The rebuilt database gave the same values as the current one. `curl /api/plants/L101867` returned `mw17=125, mw23=125, cmp23=0, change=retired`. Confirmed.
- The claim "the unit table does not show the other unit" was not reproduced: the API returns both units.
- Of the "other cases", one had the same cause (changed IDs). One had a different cause: the units are missing from the 2023 file, and that needs a product decision. One was a product decision ("mothballed" is not counted as operating).
