# Coordinated multi-channel media

[简体中文](README.zh-CN.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Español](README.es.md) | [Português](README.pt.md)

Use the user's explicitly requested output language; otherwise follow the request language. Keep commands, skill IDs, JSON keys, enum values, units and source quotations unchanged. Separate translations from originals. Never infer country, currency or jurisdiction from language. Read the relevant detailed references in the complete specification and retain all existing validation and authorization gates.

## Installation and use

Download or clone the repository and copy the indicated skill directory, including its existing references, scripts, assets and other dependencies, into your host's skill directory. Keep its name and SKILL.md. Changing the documentation language does not require another installation. Commands are installation options, not evidence of installation or activation.

```sh
git clone https://github.com/PDBen-Auto/multi-channel-media-distribution-skill.git
```

## Coordinated multi-channel media

`multi-channel-media-distribution`

Turn one verified campaign brief into adapted content for Facebook, Reddit, TikTok, YouTube, X, Instagram and LinkedIn, using the user's selected subset.

Skill directory: `.`

**Implementation Basis and Dependencies**

Agent host, evidence, rights-cleared assets and writable output. Python 3.10+ for local helpers; media tools/FFmpeg and current rules as needed. Live stages require verified account identity, available browser/API and explicit action permission.

**Inputs**

Brief with audience, goal, language, CTA and channel order; assets with rights; per-channel editor/submission permissions; destination, visibility, current rules and any prior ledger. Default: no external writes.

**Outputs**

Shared evidence/creative baseline, channel copy and real assets, review/handoff records, execution ledger and relocatable Markdown/self-contained HTML report under input/work/output.

[Workflow · Boundaries and stopping conditions · Example request](references/i18n/en.md)

> Use `$multi-channel-media-distribution` — Prepare seven English channel packages from verified product facts; stage each editor in order and leave final submission to the user; respond in English and preserve evidence, unknowns and action boundaries.

## Language coverage and validation

This localized operating guide covers purpose, prerequisites, inputs, outputs, workflow, examples and boundaries; it is not a line-by-line translation of every reference. Detailed technical references, historical cases, script errors, example interfaces and images retain their original language. The assistant can explain them in the requested language. Structural, link and key-constraint checks are performed; native-speaker editorial review for each language is not claimed.

Before delivery reconcile inputs, evidence, missing values, files and the original completion criteria. Mark unexecuted steps unverified; a successful script exit is not business validation.
