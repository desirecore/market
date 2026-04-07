# Common Research Workflows

Reusable templates for multi-step research tasks. Adapt the queries and URLs to the specific topic.

---

## 1. Technical Documentation Lookup

**Goal**: Find the authoritative answer to a "how do I X with library Y" question.

```
Step 1: WebSearch("<library> <feature> documentation site:<official-domain>")
        ↓ if no results, drop the site: filter
Step 2: WebFetch the top 1-2 official doc pages
Step 3: If example code is incomplete, also fetch the GitHub README or examples folder:
        Bash: gh api repos/<owner>/<repo>/contents/examples
Step 4: Synthesize a concise answer with one runnable code block
```

**Tip**: Always check the doc version matches the user's installed version. Look for version selectors in the page.

---

## 2. Competitor / Product Comparison

**Goal**: Build a structured comparison of 2-N similar products.

```
Step 1: WebSearch("<product-A> vs <product-B> comparison <year>")
Step 2: WebSearch("<product-A> features pricing")  ─┐ parallel
Step 3: WebSearch("<product-B> features pricing")  ─┘
Step 4: WebFetch official pricing/features pages for each (parallel)
Step 5: WebFetch 1 third-party comparison article (parallel)
Step 6: Build markdown table with consistent dimensions:
        | Dimension | Product A | Product B |
        |-----------|-----------|-----------|
        | Pricing   | ...       | ...       |
        | Features  | ...       | ...       |
        | License   | ...       | ...       |
Step 7: Add a "Recommendation" paragraph based on user's stated needs
```

**Tip**: When dimensions differ between sources, prefer the official source over third-party.

---

## 3. News Aggregation & Timeline

**Goal**: Build a chronological summary of recent events on a topic.

```
Step 1: WebSearch("<topic> news <year>", max_results=10)
Step 2: Skim snippets, group by date
Step 3: WebFetch the 3-5 most substantive articles (parallel)
Step 4: Build timeline:
        ## YYYY-MM-DD - Event headline
        - Key fact 1 [source](url)
        - Key fact 2 [source](url)
Step 5: End with a "Current State" paragraph
```

**Tip**: Use `allowed_domains` to constrain to authoritative news sources if needed.

---

## 4. Library Version Investigation

**Goal**: Find the latest version, breaking changes, and migration notes.

```
Step 1: Get latest version via API (faster than scraping):
        Python: curl https://pypi.org/pypi/<package>/json | jq .info.version
        Node:   curl https://registry.npmjs.org/<package>/latest | jq .version
        Rust:   curl https://crates.io/api/v1/crates/<crate> | jq .crate.max_version

Step 2: Get changelog:
        gh api repos/<owner>/<repo>/releases/latest

Step 3: If migration is needed, search:
        WebSearch("<package> migration guide v<old> to v<new>")
        WebFetch the official migration doc

Step 4: Summarize: latest version, breaking changes (bullet list), 1-2 code diffs
```

---

## 5. API Endpoint Discovery

**Goal**: Find a specific API endpoint and its parameters.

```
Step 1: WebSearch("<service> API <action> reference")
Step 2: WebFetch official API reference page
Step 3: If response includes "Try it" / "Sandbox" link, mention it
Step 4: Extract:
        - Endpoint URL
        - HTTP method
        - Required headers (auth)
        - Request body schema
        - Response schema
        - Example curl command
Step 5: Format as a self-contained code block the user can copy-paste
```

---

## 6. Quick Fact Check

**Goal**: Verify a single specific claim.

```
Step 1: WebSearch("<exact claim phrase>")
Step 2: If 2+ authoritative sources agree → confirmed
Step 3: If sources disagree → report both sides + which is more authoritative
Step 4: If no sources found → say "could not verify" — do NOT guess
```

**Tip**: For numeric facts, find the primary source (official report, paper) rather than secondary citations.

---

## Parallelization Cheat Sheet

When you need multiple independent fetches, **always batch them in a single message with multiple tool calls** rather than sequentially. Examples:

```
✅ Single message with:
   - WebFetch(url1)
   - WebFetch(url2)
   - WebFetch(url3)

❌ Three separate messages, each with one WebFetch
```

This applies equally to WebSearch with different queries, and to mixed Search+Fetch when you have URLs from previous searches.
