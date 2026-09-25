# Skills used

| Skill | SKILL.md path | Why relevant | Guidance applied |
|---|---|---|---|
| Web application testing | `anthropics/skills/skills/webapp-testing/SKILL.md` | The demo requires rendered browser validation | Native Python Playwright; wait for `networkidle`; inspect rendered state; capture screenshots and console messages; close the browser |
| Frontend design | `anthropics/skills/skills/frontend-design/SKILL.md` | The one-screen conference UI needs a deliberate visual hierarchy | Subject-specific visual language; compact color/type/layout tokens; one memorable change indicator; restrained motion; keyboard focus; reduced-motion and mobile support; screenshot critique |
| Skill creator (Anthropic) | `anthropics/skills/skills/skill-creator/SKILL.md` | The repository requires two local skills | Clear trigger descriptions, imperative instructions, self-contained files, progressive disclosure, and no unused support directories |
| Skill creator (Codex) | `C:/Users/aksha/.codex/skills/.system/skill-creator/SKILL.md` | Local validation and Codex-compatible skill structure | Minimal frontmatter, concise decision-changing guidance, no speculative resources, and bundled validation |

The three Anthropic files were read from the official
[`anthropics/skills`](https://github.com/anthropics/skills) repository on
2026-09-25. Their instructions were used as guidance; no helper source code was
copied. The repository's license governs those source files, while this project only
records and applies the general workflow described above.
