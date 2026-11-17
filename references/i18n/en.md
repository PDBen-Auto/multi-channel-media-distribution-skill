# Coordinated multi-channel media

`multi-channel-media-distribution` · English

## Purpose and scope

Turn one verified campaign brief into adapted content for Facebook, Reddit, TikTok, YouTube, X, Instagram and LinkedIn, using the user's selected subset.

## Implementation Basis and Dependencies

Agent host, evidence, rights-cleared assets and writable output. Python 3.10+ for local helpers; media tools/FFmpeg and current rules as needed. Live stages require verified account identity, available browser/API and explicit action permission.

## Inputs

Brief with audience, goal, language, CTA and channel order; assets with rights; per-channel editor/submission permissions; destination, visibility, current rules and any prior ledger. Default: no external writes.

## Outputs

Shared evidence/creative baseline, channel copy and real assets, review/handoff records, execution ledger and relocatable Markdown/self-contained HTML report under input/work/output.

## Workflow

1. Recover latest requirements.
2. Verify claims, assets and affiliation.
3. Produce shared creative and channel adaptations.
4. Review actual bytes, playback and mobile readability.
5. Prepare editors serially
6. verify uploaded count/order.
7. Stop before user-only submit.
8. Verify submission, manager and public detail separately
9. reconcile uncertain actions before retry.

## Boundaries and stopping conditions

A script is not a video, an editor is not a published post and synthetic demos prove no real publication. Stop the affected stage on missing authority, CAPTCHA, unsupported upload or policy denial; continue independent local work.

## Example request

Use `$multi-channel-media-distribution` — Prepare seven English channel packages from verified product facts; stage each editor in order and leave final submission to the user; respond in English and preserve evidence, unknowns and action boundaries.

## Complete specification

[Skill entrypoint and detailed references](../../SKILL.md).

Use the user's explicitly requested output language; otherwise follow the request language. Keep commands, skill IDs, JSON keys, enum values, units and source quotations unchanged. Separate translations from originals. Never infer country, currency or jurisdiction from language. Read the relevant detailed references in the complete specification and retain all existing validation and authorization gates.

Before delivery reconcile inputs, evidence, missing values, files and the original completion criteria. Mark unexecuted steps unverified; a successful script exit is not business validation.

## Language coverage and validation

This localized operating guide covers purpose, prerequisites, inputs, outputs, workflow, examples and boundaries; it is not a line-by-line translation of every reference. Detailed technical references, historical cases, script errors, example interfaces and images retain their original language. The assistant can explain them in the requested language. Structural, link and key-constraint checks are performed; native-speaker editorial review for each language is not claimed.

