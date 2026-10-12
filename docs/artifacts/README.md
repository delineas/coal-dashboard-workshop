# Artifacts

This folder contains artifacts from the workshop sessions.

## spec-writer.zip

`spec-writer.zip` contains the `spec-writer` skill. We made this skill in session 1.

The skill turns a feature request into a spec in `docs/`. It does these steps:

1. It examines the code and the data in the repository.
2. It asks you multiple-choice questions until no implementation question remains.
3. It writes the spec with Given/When/Then acceptance criteria and an out-of-scope section.
4. It commits the spec on a feature branch.

The repository does not include the skill in `.claude/skills/`. To use it, extract the zip into that folder:

```sh
mkdir -p .claude/skills
unzip docs/artifacts/spec-writer.zip -d .claude/skills
```

Then start a new Claude Code session. The skill is available as `/spec-writer`.
