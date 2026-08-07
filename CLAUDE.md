# CLAUDE.md

This repository is a public marketplace. Every contribution must be reusable,
customer-neutral, and safe to index publicly.

## Public information boundary

- Never put a tenant, customer, prospect, partner, or other confidential identity
  in tracked files, paths, filenames, Agent or Skill IDs, frontmatter, descriptions,
  examples, fixtures, memories, generated artifacts, or screenshots.
- Apply the same rule to Git metadata and collaboration text: branch names, commit
  subjects and bodies, PR or issue titles and bodies, comments, and review replies.
- Describe reusable capabilities with domain-neutral roles and entities. Put
  customer-specific prompts, facts, mappings, examples, data, and deployment
  settings only in private AgentFS homes, private repositories, or private runtime
  configuration.
- Do not add a real confidential token to a denylist, test fixture, documentation,
  or example. A literal denylist in a public repository creates a second leak.

## External dependency disclosure

- A Skill or Agent that relies on separately licensed, purchased, hosted, or
  deployed third-party software must disclose that dependency in its discovery
  description, `compatibility` field, localized marketplace text, and execution
  instructions.
- Distinguish an included connector or adapter Tool from the external product it
  accesses. Never imply that registering a Tool bundles, licenses, installs, pays
  for, or operates the third-party product.
- State the operator prerequisites, applicable licensing or usage terms, separate
  costs when relevant, connection readiness checks, and safe degraded behavior.
  If the dependency is unavailable, stop before the external call and never
  fabricate a successful result.

## Required pre-publication check

Before committing or opening/updating a PR:

1. Obtain the sensitive tokens through a private channel and keep them outside the
   repository.
2. Scan the complete working tree, including hidden files while excluding `.git`.
3. Scan new path names, branch names, commit subjects and bodies, and the proposed
   PR/issue/review text.
4. Review examples semantically: changing a proper noun is insufficient when an
   example still exposes a customer-specific organization shape or private fact.
5. Run the repository validation and translation-freshness checks documented in
   `README.md`.

A zero-result scan is a release requirement. Record only that the check passed;
never persist the confidential search tokens or command history in the repository.

## Incident response

If confidential identity or data reaches the public repository:

1. Stop the merge or release and neutralize all editable GitHub metadata.
2. Replace the public content with a genuinely reusable abstraction; do not merely
   rename the customer.
3. If reachable Git history is affected, make a mirror backup, rewrite only the
   affected history, verify expected tree objects, push with an exact lease, and
   restore branch protections immediately.
4. Treat pull-request refs, cached views, reviews, notifications, and search-engine
   caches as separate surfaces. Follow the hosting provider's sensitive-data
   removal process instead of claiming that a force-push removed them.
5. Re-run all publication checks before reopening or merging work.

## Instruction synchronization

`AGENTS.md` and `CLAUDE.md` are equivalent repository policy entrypoints. Any
substantive change to one must be made to the other in the same commit.
