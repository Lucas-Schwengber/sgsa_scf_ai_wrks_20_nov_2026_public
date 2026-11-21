---
title: Tutorial
created: 2026-11-19
updated: 2026-11-20
authors: Lucas da Rocha Schwengber (L), CLAUDE (C)
---

# Skills

## References (C)

Introductory:

- [Introducing Agent Skills](https://claude.com/resources/articles/skills): short intro, same article series as the subagents one.
- [Skills in Claude Code (docs)](https://code.claude.com/docs/en/skills): official docs; `SKILL.md` format, where skills live, frontmatter, `/skill-name` invocation.

Deeper:

- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16): engineering post on the design, in particular progressive disclosure (only name and description are loaded until the skill is needed).
- [A complete guide to building skills for Claude](https://claude.com/resources/articles/complete-guide-to-building-skills-for-claude) (2026-01-29): building, testing and distributing skills; candidate for "Anthropic's tutorial on using skills" in the [workshop talk](ai_workshop_talk.md).
- [Lessons from building Claude Code: How we use skills](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills): how Anthropic uses skills internally (not opened, found through search).

Ecosystem:

- [agentskills.io](https://agentskills.io): the open Agent Skills standard Claude Code follows.
- [anthropics/skills](https://github.com/anthropics/skills): Anthropic's repo of example skills.

## Examples and context (L)

Simplest example: docstrings.

Development cycle:
- free prompt
- detect demand
- add skill (highly recommend through Claude to anticipate edge cases and have a second look)
- test usage with fork ablation.
- make edit to skill (possibly through Claude) for further iteration

## Best practices (C+L)

Most of this comes from two pages: the [Claude Code skills docs](https://code.claude.com/docs/en/skills) and Anthropic's [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

### Format

A skill is a folder whose only required file is `SKILL.md`:

```text
my-skill/
├── SKILL.md          # frontmatter + short instructions (always loaded when the skill runs)
├── reference.md      # detail, read only when needed
└── scripts/check.py  # run, not read, so its code costs no context
```

**Frontmatter fields worth knowing**
- **`description`** is the most important line. Until the skill runs, it is the only part Claude sees, and Claude decides whether to load the skill from it. Claude Code cuts `description` plus `when_to_use` off at 1,536 characters. The cross-platform spec allows at most 1,024 characters for `description` alone.
- **`name`** becomes the `/command`; without it, the folder name is used. The spec allows up to 64 characters: lowercase letters, digits and hyphens.
- **`disable-model-invocation: true`** means only you can run the skill. Use it for anything with side effects: deploys, commits, job submission.
- **`user-invocable: false`** hides the skill from the `/` menu, for background knowledge that only Claude should load.
- **`allowed-tools`, `argument-hint`, `$ARGUMENTS`**: pre-approve tools, show an autocomplete hint, and pass arguments in.
- **`context: fork`** (with `agent:`) runs the skill in a subagent. The subagent can't see the conversation, so the skill must be a complete, self-contained task.
- **Shell injection**: a command written inside `` !`…` `` runs before Claude reads the skill, and its output replaces it. This is useful for pulling in live state such as `git diff`.

**Size and layout**
- Keep `SKILL.md` under 500 lines.
- Put detail in sibling files linked directly from `SKILL.md`, one level deep. Claude may only skim files that are linked from other linked files.
- Refer to bundled files with `${CLAUDE_SKILL_DIR}`, never a hard-coded path.

### Practices

1. **Write the description as the trigger.** Say what the skill does and when to use it, in the third person. Include the words a user would actually type ("PDF", "figure", "savefig"). Put the main use case first.
2. **Write only what Claude doesn't already know.** Once loaded, the skill stays in context for the rest of the session, so every line costs tokens on every turn. Skip explanations of NumPy, matplotlib or git; keep your own conventions and decisions.
3. **Match strictness to how fragile the task is.** For open-ended work like reviews, give loose guidance. For fragile steps like migrations or cluster jobs, give the exact command and say "don't change it".
4. **Give a default, not a menu.** "Use X; for case Y use Z" works better than "you could use A, B, C or D."
5. **Use concrete examples and templates.** Input/output pairs or an output skeleton beat adjectives like "make it professional."
6. **For multi-step tasks, write a workflow with a check at the end.** Use numbered steps, and finish with "run the validator → fix → rerun until it passes."
7. **Use scripts for deterministic steps.** They're more reliable than code Claude writes fresh, and only their output uses context. Say whether Claude should run a script or read it.
8. **Use one term per concept, and leave out dates.** Write "the v2 endpoint", not "after August use…".
9. **Test against a baseline.** Run the task in a fresh session with and without the skill, then revise the skill based on what goes wrong. This matches the "fork ablation" step in your talk outline. A good habit is to have one Claude write the skill and a fresh one use it.

### Bad example

```markdown
---
name: plots
description: I can help you make nice plots.
---

# Plotting Skill

Matplotlib is a popular Python plotting library first released in 2003. It
supports line plots, scatter plots, histograms and many other chart types...

You could use matplotlib, seaborn or plotly depending on preference. Try to
make figures look professional, with good colors and appropriate font sizes,
and save them somewhere sensible.

For more details see style.md (which links to colors.md and fonts.md).

Since the NeurIPS deadline is next month, use the new template.
```

What's wrong with it:
- **Description:** it's in the first person, says nothing about when to use it, and has no trigger words.
- **Lecture:** the first paragraph explains matplotlib, which Claude already knows.
- **No default:** it offers three libraries and picks none.
- **Vague rules:** "professional", "good colors", "somewhere sensible" are adjectives Claude can't check.
- **Nested links:** style.md links to further files, so Claude may only skim them.
- **Dated:** the deadline line goes stale.
- **No check:** nothing confirms the figure is right.

### Good example

```markdown
---
name: paper-figures
description: Formats matplotlib figures for the group's papers and slides: size, fonts, palette, file names and export. Use when creating or editing a plot or figure for a paper, preprint, poster or talk, or when the user mentions figures/, savefig, or "publication-ready".
---

# Paper figures

## Defaults
- Start every script with `plt.style.use("${CLAUDE_SKILL_DIR}/paper.mplstyle")`.
  It sets fonts, sizes and palette; do not override them inline.
- Width: 3.25 in (one column) or 6.75 in (two columns). Height = width / 1.6.
- Label every axis with quantity and unit, e.g. `Sample size $n$`, `Time (s)`.
- Save vector PDF to `figures/<script>_<what>.pdf`. Add a 300 dpi PNG only for slides.

## Workflow
1. Put the plotting code in `scripts/plots/<name>.py`, not in a notebook.
2. Run it.
3. Run `python ${CLAUDE_SKILL_DIR}/check_figure.py figures/<file>.pdf`.
   It flags non-embedded fonts, text under 7 pt, and the wrong width.
4. Fix what it reports; rerun until it prints `OK`.

## More
- Multi-panel layouts (panel labels, shared axes): [panels.md](panels.md)
- Colour-blind-safe palettes for more than 6 series: [palettes.md](palettes.md)
```

The style file, `check_figure.py` and the linked pages are made up for the example. Why it works:
- **Description:** it names the task, when to use it, and the words people type.
- **Only your conventions:** every rule is a group choice Claude couldn't guess.
- **One default:** a single style file instead of a list of libraries.
- **Checkable rules:** each one is concrete.
- **Script check:** the workflow ends with a check that loops until it passes.
- **Short:** rarely needed detail sits one link away.

## Hooks (C+L)

- [Hooks guide](https://code.claude.com/docs/en/hooks-guide): getting started, common uses (e.g. auto-format after edits), checking a hook is registered.
- [Hooks reference](https://code.claude.com/docs/en/hooks): every event, input/output JSON, security notes.
- [How to configure hooks](https://claude.com/blog/how-to-configure-hooks) (2025-12-11): blog walkthrough of events, config files, matchers and debugging.
- [DataCamp: Claude Code hooks tutorial](https://www.datacamp.com/tutorial/claude-code-hooks): third-party tutorial with examples.

I personally use them less. By I found one to be very useful: one that rewrites fork titles.

Hooks are literally shell commands that run under an event on Claude Code (it's a harness property).

Can add a "matcher" to filter out output from event.

## Skill creation example (L)

mute-analysis: un experiments but draw no conclusions, explanations nor next steps, just state what as run in the most neutral way possible. Whenever some major design decision requiring strong inferences and predictions needs to made, refer back to the user. (suggest by Bobby).

## Keeping skills synched (L)

Github repo with install.sh + git pull hook.

Given access of claude to all repos, it can manually add and commit to the skills repo directly.

# Using across devices (L)

Claude code can be used equivalently through: terminal, claude-desktop app, VSCODE, (etc.).

It can be used via the webapp as well via the remote control option.

Claude code can also be spawned on an ssh server.

A cheap way of having persistent sessions to manage across devices asynchronously is to spawn a tmux on an ssh server and link it through the remote-control option.

# Managing context with .md files (L)

See (sgsa_scf_ai_wrks_20_nov_2026/README.md)[sgsa_scf_ai_wrks_20_nov_2026/README.md].

Some notes will likely remain agents only (e.g. the cached notes Claude uses), and other human only (digest files and personal notes). 

But the gist is that it's easier for agents and humans to work on top of each other's work if there is a shared note system understandable by both.

# Work cycle (L)

One possible work cycle is: 

```
  user description
         |
         v
discussion with model <-----+
         |                  |
         v                  |
      plan.md               |
         |                  |  further
         v                  |  iterations
   task execution           |
         |                  |
         v                  |
     report.md -------------+
         |
         v
  notes / summaries
```
