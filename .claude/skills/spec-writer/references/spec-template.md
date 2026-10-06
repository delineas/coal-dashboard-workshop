# Spec template

Copy this structure. Remove the sections that do not apply (for example, "Data sources" for a feature with no data files). Keep the numbering.

```markdown
# Spec: <feature name>

## 1. Goal

<Two or three sentences: what the feature does and for whom.>

## 2. Data sources

| File | Release or version | Rows | Row = |
|---|---|---|---|

<Encoding, separators and other format facts that the code must handle.>

## 3. Definitions

| Term | Definition |
|---|---|

## 4. Data rules

### 4.1 Process
### 4.2 <Normalization>
### 4.3 <Bad rows>
### 4.4 <Matching across sources>
### 4.5 <Derived fields and classifications>

## 5. API

| Method and path | Response |
|---|---|

<Error codes and filters.>

## 6. Frontend

### 6.1 Stack
### 6.2 Visual direction
### 6.3 Routes or screens
### 6.4 <Main component, for example the map>

## 7. Acceptance criteria

### 7.1 <Area>

**AC-<AREA>-1: <short title>**
- Given <a precondition with real values>
- When <one action>
- Then <an observable result>
- And <one more result, if necessary>

## 8. Tests

## 9. Delivery

<Branches in sequence, merge strategy, commit rules.>

## 10. Out of scope

- <Item>

## 11. Open items

- **<Topic>:** <what is pending> — decide before <branch or milestone>.
```

## Acceptance criteria rules

- One "When" for each criterion. If you need two actions, write two criteria.
- The "Then" must be observable by a test or by a person on the screen. Do not write "works correctly".
- Use real numbers and real example records from the data. A criterion like "Then the total is 2,095,083 MW" finds bugs; "Then the total is correct" does not.
- Cover each edge case that a question decided (zero values, nulls, records in one source only, not found).
- Include one general criterion for the quality checks (test, lint, build command).
