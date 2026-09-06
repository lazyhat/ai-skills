# Personal Codex Skills

This repository contains the local skill set used by Codex on this machine.

## Layout

- `skills/<name>/SKILL.md` is the entry point for each skill.
- Skill-local support files, prompts, scripts, and references stay next to the skill that uses them.

## Usage

Codex discovers this user-scoped skill set through:

```text
~/.agents/skills
```

Keep that path as a symlink to this repository's `skills/` directory. For example, after cloning the
repository, create the link with absolute paths:

```bash
ln -s /absolute/path/to/ai-skills/skills ~/.agents/skills
```

Verify the installation before relying on it:

```bash
readlink -f ~/.agents/skills
```

The resolved path must be this checkout's `skills/` directory. Recreate the link when the checkout moves;
do not maintain a second copied installation that can drift from this repository.
