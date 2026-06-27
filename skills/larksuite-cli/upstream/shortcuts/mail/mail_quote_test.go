// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package mail

import (
	"strings"
	"testing"
)

func sampleOriginalMessage() originalMessage {
	return originalMessage{
		subject:      "Mail Shortcuts & Workflows 脑暴方案",
		headFrom:     "alice@example.com",
		headFromName: "Alice",
		headDate:     "Sat, 21 Mar 2026 08:30:00 GMT",
		toAddresses:  []string{"bob@example.com", "carol@example.com"},
		ccAddresses:  []string{"dave@example.com"},
		toAddressesFull: []mailAddressPair{
			{Email: "bob@example.com", Name: "Bob"},
			{Email: "carol@example.com", Name: "Carol"},
		},
		ccAddressesFull: []mailAddressPair{
			{Email: "dave@example.com", Name: "Dave"},
		},
		bodyRaw: "<div>hello <b>world</b></div>",
	}
}

func sampleEnglishOriginalMessage() originalMessage {
	orig := sampleOriginalMessage()
	orig.subject = "Project Update"
	return orig
}

func TestQuoteMetaLabelsDefaultEnglish(t *testing.T) {
	labels := quoteMetaLabels("Project Update")
	if labels.From != "From" || labels.Date != "Date" || labels.Subject != "Subject" || labels.To != "To" || labels.Cc != "Cc" {
		t.Fatalf("unexpected default labels: %+v", labels)
	}
}

func TestQuoteMetaLabelsChinese(t *testing.T) {
	labels := quoteMetaLabels("脑暴方案")
	if labels.From != "发件人" || labels.Date != "时间" || labels.Subject != "主题" || labels.To != "收件人" || labels.Cc != "抄送" {
		t.Fatalf("unexpected Chinese labels: %+v", labels)
	}
	if labels.Separator != "--------- 转发消息 ---------" {
		t.Fatalf("unexpected Chinese separator: %q", labels.Separator)
	}
	if labels.Colon != "：" {
		t.Fatalf("unexpected Chinese colon: %q", labels.Colon)
	}
}

func TestBuildReplyQuoteHTMLStructure(t *testing.T) {
	orig := sampleOriginalMessage() // subject contains Chinese
	html := buildReplyQuoteHTML(&orig)

	mustContain(t, html, `class="history-quote-wrapper"`)
	mustContain(t, html, `data-html-block="quote"`)
	mustContain(t, html, `data-mail-html-ignore=""`)
	mustContain(t, html, `class="adit-html-block adit-html-block--collapsed"`)
	mustContain(t, html, `style="border-left: none; padding-left: 0px;"`)
	mustContain(t, html, `class="adit-html-block__attr history-quote-meta-wrapper history-quote-gap-tag"`)
	mustContain(t, html, `padding: 12px; background: rgb(245, 246, 247); color: rgb(31, 35, 41); border-radius: 4px; margin-bottom: 12px;`)
	mustContain(t, html, `class="lme-line-signal"`)
	mustContain(t, html, `class="quote-head-meta-mailto"`)
	mustContain(t, html, `data-mailto="mailto:alice@example.com"`)

	// Chinese labels because subject contains CJK
	mustContain(t, html, `发件人: `)
	mustContain(t, html, `时间: `)
	mustContain(t, html, `主题: `)
	mustContain(t, html, `收件人: `)
	mustContain(t, html, `抄送: `)

	// New <a> style: text-decoration: none (not underline)
	mustContain(t, html, `text-decoration: none`)
	mustContain(t, html, `white-space: pre-wrap`)
	mustContain(t, html, `cursor: pointer`)

	// Address with display name: "Bob"<a>bob@example.com</a>
	mustContain(t, html, `"Bob"&lt;<a class="quote-head-meta-mailto"`)
	mustContain(t, html, `data-mailto="mailto:bob@example.com"`)

	// Each recipient wrapped in <span>
	mustContain(t, html, `<span>"Bob"&lt;`)
	mustContain(t, html, `<span>"Carol"&lt;`)

	// Body is plain <div> (not wrapped in lme-line-signal)
	mustContain(t, html, `<div><div>hello <b>world</b></div></div>`)
	mustNotContain(t, html, `<div class="lme-line-signal"><div>hello`)

	// Field order: 发件人 < 时间 < 主题 < 收件人 < 抄送
	assertFieldOrder(t, html, []string{`发件人: `, `时间: `, `主题: `, `收件人: `, `抄送: `})
}

func TestBuildReplyQuoteHTMLEnglishLabels(t *testing.T) {
	orig := sampleEnglishOriginalMessage()
	html := buildReplyQuoteHTML(&orig)

	mustContain(t, html, `From: `)
	mustContain(t, html, `Date: `)
	mustContain(t, html, `Subject: `)
	mustContain(t, html, `To: `)
	mustContain(t, html, `Cc: `)
	mustNotContain(t, html, `发件人`)
}

func TestBuildForwardQuoteHTMLStructure(t *testing.T) {
	orig := sampleOriginalMessage() // subject contains Chinese
	html := buildForwardQuoteHTML(&orig)

	mustContain(t, html, `class="history-quote-wrapper"`)
	mustContain(t, html, `class="adit-html-block adit-html-block--header"`)
	mustContain(t, html, `style="border-left: none; padding-left: 0px;"`)

	// Forward meta wrapper class (not adit-html-block__attr)
	mustContain(t, html, `class="adit-html-block__header history-quote-meta-after-forward-title history-quote-meta-wrapper"`)
	mustNotContain(t, html, `class="adit-html-block__attr`)

	// separator has margin-top: 24px; meta block has margin-top: 2px
	mustContain(t, html, `margin-top: 24px`)
	mustContain(t, html, `margin-top: 2px`)

	// Separator is outside meta wrapper, uses correct class
	mustContain(t, html, `class="history-quote-forward-title lme-line-signal history-quote-gap-tag"`)
	mustContain(t, html, `--------- 转发消息 ---------`) // Chinese because subject has CJK

	// Chinese labels
	mustContain(t, html, `发件人: `)
	mustContain(t, html, `时间: `)
	mustContain(t, html, `主题: `)
	mustContain(t, html, `收件人: `)
	mustContain(t, html, `抄送: `)

	// IDs present with lark-mail-quote-cli prefix
	mustContain(t, html, `id="lark-mail-quote-cli`)
	mustContain(t, html, `id="lark-mail-meta-cli`)

	// Separator before meta block
	sepIdx := strings.Index(html, `--------- 转发消息 ---------`)
	metaIdx := strings.Index(html, `adit-html-block__header history-quote-meta-after-forward-title`)
	if sepIdx > metaIdx {
		t.Fatalf("separator should appear before meta block: sep=%d meta=%d", sepIdx, metaIdx)
	}

	// Field order
	assertFieldOrder(t, html, []string{`发件人: `, `时间: `, `主题: `, `收件人: `, `抄送: `})
}

func TestBuildForwardQuoteHTMLEnglishSeparator(t *testing.T) {
	orig := sampleEnglishOriginalMessage()
	html := buildForwardQuoteHTML(&orig)

	mustContain(t, html, `---------- Forwarded message ---------`)
	mustNotContain(t, html, `转发消息`)
	mustContain(t, html, `From: `)
}

func TestBuildReplyPrefixHTMLNoCcWhenEmpty(t *testing.T) {
	orig := sampleOriginalMessage()
	orig.ccAddresses = nil
	orig.ccAddressesFull = nil
	prefix := buildReplyPrefixHTML(&orig)
	mustNotContain(t, prefix, `抄送: `)
	mustNotContain(t, prefix, `Cc: `)
}

func TestBuildAddressHTMLWithName(t *testing.T) {
	html := buildAddressHTML("Alice", "alice@example.com")
	mustContain(t, html, `"Alice"&lt;`)
	mustContain(t, html, `&gt;`)
	mustContain(t, html, `href="mailto:alice@example.com"`)
}

func TestBuildAddressHTMLWithoutName(t *testing.T) {
	html := buildAddressHTML("", "alice@example.com")
	mustContain(t, html, `&lt;<a`)
	mustContain(t, html, `&gt;`)
	mustNotContain(t, html, `""`)
}

func assertFieldOrder(t *testing.T, html string, fields []string) {
	t.Helper()
	prev := 0
	for i := 1; i < len(fields); i++ {
		a := strings.Index(html, fields[i-1])
		b := strings.Index(html, fields[i])
		if a < 0 || b < 0 || a >= b {
			t.Fatalf("expected %q (pos %d) before %q (pos %d)", fields[i-1], a, fields[i], b)
		}
		_ = prev
		prev = a
	}
}

func mustContain(t *testing.T, s, sub string) {
	t.Helper()
	if !strings.Contains(s, sub) {
		t.Fatalf("expected content to contain %q, got: %s", sub, s)
	}
}

func mustNotContain(t *testing.T, s, sub string) {
	t.Helper()
	if strings.Contains(s, sub) {
		t.Fatalf("expected content to not contain %q, got: %s", sub, s)
	}
}

// ---------------------------------------------------------------------------
// Plain-text quote format tests
// ---------------------------------------------------------------------------

func TestQuoteForReplyPlainTextChineseMeta(t *testing.T) {
	orig := sampleOriginalMessage() // subject contains Chinese
	quote := quoteForReply(&orig, false)

	// Should start with two newlines
	if !strings.HasPrefix(quote, "\n\n") {
		t.Fatalf("expected quote to start with \\n\\n, got: %q", quote[:20])
	}

	// Chinese labels because subject has CJK
	mustContain(t, quote, "> 发件人：")
	mustContain(t, quote, "> 主题：")
	mustContain(t, quote, "> 时间：")
	mustContain(t, quote, "> 收件人：")
	mustContain(t, quote, "> 抄送：")

	// Blank separator line before body
	mustContain(t, quote, ">\n")

	// Body lines should be prefixed with "> "
	mustContain(t, quote, "> hello world\n")
}

func TestQuoteForReplyPlainTextEnglishMeta(t *testing.T) {
	orig := sampleEnglishOriginalMessage()
	quote := quoteForReply(&orig, false)

	// English labels
	mustContain(t, quote, "> From: ")
	mustContain(t, quote, "> Subject: ")
	mustContain(t, quote, "> Date: ")
	mustContain(t, quote, "> To: ")
	mustContain(t, quote, "> Cc: ")

	// Should not contain Chinese labels
	mustNotContain(t, quote, "发件人")
	mustNotContain(t, quote, "主题")
}

func TestQuoteForReplyPlainTextNoCc(t *testing.T) {
	orig := sampleOriginalMessage()
	orig.ccAddresses = nil
	orig.ccAddressesFull = nil
	quote := quoteForReply(&orig, false)

	// Should not contain Cc line when empty
	mustNotContain(t, quote, "> 抄送：")
	mustNotContain(t, quote, "> Cc: ")
}

func TestQuoteForReplyPlainTextFieldOrder(t *testing.T) {
	orig := sampleOriginalMessage()
	quote := quoteForReply(&orig, false)

	// Field order should match HTML: From, Date, Subject, To, Cc
	assertFieldOrder(t, quote, []string{
		"> 发件人：",
		"> 时间：",
		"> 主题：",
		"> 收件人：",
		"> 抄送：",
	})
}

func TestBuildReplyMetaPlainTextAddressFormat(t *testing.T) {
	orig := originalMessage{
		subject:         "Test",
		headFrom:        "alice@example.com",
		headFromName:    "Alice",
		headDate:        "Mon, 01 Jan 2026 12:00:00 +0000",
		toAddressesFull: []mailAddressPair{{Email: "bob@example.com", Name: "Bob"}},
		bodyRaw:         "Hello",
	}
	quote := quoteForReply(&orig, false)

	// Address format should be "Name" <email>
	mustContain(t, quote, `> From: "Alice" <alice@example.com>`)
	mustContain(t, quote, `> To: "Bob" <bob@example.com>`)
}

func TestBuildReplyMetaPlainTextAddressWithoutName(t *testing.T) {
	orig := originalMessage{
		subject:      "Test",
		headFrom:     "alice@example.com",
		headFromName: "",
		headDate:     "Mon, 01 Jan 2026 12:00:00 +0000",
		bodyRaw:      "Hello",
	}
	quote := quoteForReply(&orig, false)

	// Without name, should just be <email>
	mustContain(t, quote, `> From: <alice@example.com>`)
	mustNotContain(t, quote, `"" <`)
}

// ---------------------------------------------------------------------------
// bodyIsHTML tests
// ---------------------------------------------------------------------------

func TestBodyIsHTML(t *testing.T) {
	tests := []struct {
		name string
		in   string
		want bool
	}{
		// Should detect as HTML
		{"div tag", "<div>hello</div>", true},
		{"div with attrs", `<div class="x">hello</div>`, true},
		{"p tag", "<p>paragraph</p>", true},
		{"br self-close", "line1<br/>line2", true},
		{"br space-close", "line1<br />line2", true},
		{"br angle", "line1<br>line2", true},
		{"html tag", "<html><body>hi</body></html>", true},
		{"doctype", "<!DOCTYPE html><html>", true},
		{"doctype lower", "<!doctype html><html>", true},
		{"comment", "<!-- comment -->", true},
		{"img", `<img src="x.png">`, true},
		{"table", "<table><tr><td>1</td></tr></table>", true},
		{"span", "<span>text</span>", true},
		{"h1", "<h1>Title</h1>", true},
		{"strong", "<strong>bold</strong>", true},
		{"blockquote", "<blockquote>quoted</blockquote>", true},
		{"pre", "<pre>code</pre>", true},
		{"hr", "<hr/>", true},
		{"case insensitive", "<DIV>hello</DIV>", true},
		{"mixed case", "<Div>hello</Div>", true},

		// Should NOT detect as HTML (false positive prevention)
		{"plain text", "hello world", false},
		{"angle brackets math", "price < 100 & qty > 50", false},
		{"filename in angles", "see <brief.pdf> for details", false},
		{"brand tag-like", "the <brand> is strong", false},
		{"email angle", "contact <user@example.com>", false},
		{"empty", "", false},
		{"just angle", "<", false},
		{"unclosed angle", "<not a tag", false},
		{"no terminator", "<divx>content</divx>", false},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := bodyIsHTML(tc.in); got != tc.want {
				t.Errorf("bodyIsHTML(%q) = %v, want %v", tc.in, got, tc.want)
			}
		})
	}
}

func TestBuildBodyDivEmpty(t *testing.T) {
	if got := buildBodyDiv("", false); got != "" {
		t.Fatalf("expected empty, got %q", got)
	}
	if got := buildBodyDiv("", true); got != "" {
		t.Fatalf("expected empty, got %q", got)
	}
}

func TestBuildBodyDivPlainTextNewlines(t *testing.T) {
	got := buildBodyDiv("line1\nline2\nline3", false)
	mustContain(t, got, "line1<br>line2<br>line3")
	mustNotContain(t, got, "\n")
}

func TestBuildBodyDivPlainTextEscapesHTML(t *testing.T) {
	got := buildBodyDiv("<script>alert('xss')</script>", false)
	mustNotContain(t, got, "<script>")
	mustContain(t, got, "&lt;script&gt;")
}

func TestBuildBodyDivHTMLPassthrough(t *testing.T) {
	html := `<p>hello</p>`
	got := buildBodyDiv(html, true)
	mustContain(t, got, `<p>hello</p>`)
}
