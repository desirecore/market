---
name: zh-editor
description: 润色或审阅已有中文稿件和译稿，理顺句子并保留作者语气、事实和限定条件。Edit existing Chinese drafts and translations.
license: MIT
version: 1.0.0
type: procedural
risk_level: low
status: enabled
disable-model-invocation: true
tags:
  - writing
  - editing
  - chinese
metadata:
  author: desirecore
  updated_at: '2026-11-22'
  i18n:
    default_locale: en-US
    source_locale: zh-CN
    locales:
      - zh-CN
      - en-US
    zh-CN:
      name: 中文编辑
      short_desc: 润色中文稿和译稿，理顺句子，保留作者语气、事实与限定条件
      description: 适合文章、邮件、公告和文档正文。轻改翻译腔和套话，核对责任主体、审批条件、范围和承诺。需要时查阅中文改写示例。
      body: ./SKILL.zh-CN.md
    en-US:
      name: Chinese Editing
      short_desc: Polish Chinese drafts and translations while preserving author voice, facts, and conditions
      description: Edit articles, emails, announcements, and document prose. Smooth awkward phrasing while keeping responsibilities, approval conditions, scope, and commitments intact. Consult Chinese examples for tricky passages.
      body: ./SKILL.md
      source_hash: sha256:589cad5f4969e318
market:
  category: creative
  maintainer:
    name: DesireCore Official
    verified: true
  channel: latest
---

# Chinese Editing

Identify the audience, purpose, and passages the user wants edited. By default, change only awkward, repetitive, or empty wording. When the user asks for a final or copy-ready draft, start with its first sentence and end with its last.

- **Preserve fact-bearing phrases.** Keep a person, role qualifier, and count together in the original wording. For example, retain “two on-site colleagues” in full even if the draft already mentions that they are on-site. Keep times, scope, negation, attribution, completion status, and certainty aligned with the source. “Maintenance may proceed only after the person in charge confirms” can become “Wait for the person in charge to confirm before carrying out the maintenance.” “The maintenance time is pending confirmation” changes the condition. Keep the original wording if an equivalent rewrite is unclear.
- **Work with Chinese sentence patterns.** Connect each sentence through a topic the reader already knows. Omit an unnecessary pronoun when the subject is clear, and name the known actor when the subject changes or responsibility could be confused. Split hard-to-read modifiers and use direct verbs. For example, shorten “审批通过后对座位表进行更新” to “审批通过后更新座位表.”
- **Fit the genre.** Cut setup without independent information, repetition, and unsupported emphasis. Keep useful connectors, terminology, and distinct points in lists. Maintain the formality and courtesy the genre calls for, as well as the script and regional usage. Use author samples to match syntax, diction, and rhythm.
- **Check the draft before delivery.** Check which action each condition governs. Use only reasons, experiences, plans, and commitments supplied by the source, including any promise to notify readers or investigate. State facts separately when the source gives no relationship. Remove “Here is the draft,” change notes, and invitations for follow-up from a final draft. For review, identify the passage and give advice only. Write back to files only when requested, preserving quotes, code, link destinations, data, and heading anchors.

When tone, responsibility, or conditions are difficult to resolve, consult the relevant [Chinese examples](references/examples.md).
