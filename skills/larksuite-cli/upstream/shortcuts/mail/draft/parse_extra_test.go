// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package draft

import (
	"strings"
	"testing"
)

// ---------------------------------------------------------------------------
// Parse — empty/invalid raw EML
// ---------------------------------------------------------------------------

func TestParseEmptyRawEML(t *testing.T) {
	_, err := Parse(DraftRaw{DraftID: "d-1", RawEML: ""})
	if err == nil || !strings.Contains(err.Error(), "empty") {
		t.Fatalf("error = %v, want empty error", err)
	}
}

func TestParseInvalidBase64(t *testing.T) {
	_, err := Parse(DraftRaw{DraftID: "d-1", RawEML: "!!!not-base64!!!"})
	if err == nil || !strings.Contains(err.Error(), "not valid base64") {
		t.Fatalf("error = %v, want base64 error", err)
	}
}

func TestParseMissingHeaderBodySeparator(t *testing.T) {
	_, err := Parse(DraftRaw{
		DraftID: "d-1",
		RawEML:  encodeFixtureEML("Subject: Test\nno body separator here"),
	})
	if err == nil || !strings.Contains(err.Error(), "missing header/body separator") {
		t.Fatalf("error = %v, want separator error", err)
	}
}

// ---------------------------------------------------------------------------
// Parse — no Content-Type header defaults to text/plain
// ---------------------------------------------------------------------------

func TestParseNoContentTypeDefaultsToPlainText(t *testing.T) {
	snapshot, err := Parse(DraftRaw{
		DraftID: "d-noct",
		RawEML:  encodeFixtureEML("Subject: Bare\nFrom: alice@example.com\n\nhello world\n"),
	})
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Body.MediaType != "text/plain" {
		t.Fatalf("MediaType = %q, want text/plain", snapshot.Body.MediaType)
	}
	if got := string(snapshot.Body.Body); got != "hello world\n" {
		t.Fatalf("body = %q", got)
	}
}

// ---------------------------------------------------------------------------
// Parse — multipart/mixed with missing boundary param
// ---------------------------------------------------------------------------

func TestParseMultipartMissingBoundaryReturnsError(t *testing.T) {
	_, err := Parse(DraftRaw{
		DraftID: "d-nobnd",
		RawEML:  encodeFixtureEML("Subject: Test\nContent-Type: multipart/mixed\n\nsome body\n"),
	})
	if err == nil || !strings.Contains(err.Error(), "missing boundary") {
		t.Fatalf("error = %v, want missing boundary error", err)
	}
}

// ---------------------------------------------------------------------------
// Parse — charset decoding of non-UTF-8 charset
// ---------------------------------------------------------------------------

func TestParseMalformedCharsetGracefulDegradation(t *testing.T) {
	snapshot, err := Parse(DraftRaw{
		DraftID: "d-badcharset",
		RawEML:  encodeFixtureEML("Subject: Bad charset\nContent-Type: text/plain; charset=X-UNKNOWN-CHARSET-999\n\nhello\n"),
	})
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if !snapshot.Body.EncodingProblem {
		t.Fatalf("EncodingProblem should be true for unknown charset")
	}
	// Body should still have content (raw bytes fallback)
	if len(snapshot.Body.Body) == 0 {
		t.Fatalf("body should not be empty")
	}
}

// ---------------------------------------------------------------------------
// Parse — message/rfc822 part is preserved as opaque
// ---------------------------------------------------------------------------

func TestParseMessageRFC822Preserved(t *testing.T) {
	snapshot, err := Parse(DraftRaw{
		DraftID: "d-rfc822",
		RawEML:  mustReadFixtureEML(t, "testdata/message_rfc822_draft.eml"),
	})
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	// Should find an attachment part with message/rfc822
	found := false
	for _, child := range snapshot.Body.Children {
		if child != nil && child.MediaType == "message/rfc822" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected message/rfc822 child part")
	}
}

// ---------------------------------------------------------------------------
// Parse — unknown transfer encoding preserves raw bytes
// ---------------------------------------------------------------------------

func TestParseUnknownTransferEncodingPreservesRawBytes(t *testing.T) {
	snapshot, err := Parse(DraftRaw{
		DraftID: "d-unknowncte",
		RawEML: encodeFixtureEML(`Subject: Unknown CTE
From: alice@example.com
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: x-custom-encoding

raw body content here
`),
	})
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if got := string(snapshot.Body.Body); got != "raw body content here\n" {
		t.Fatalf("body = %q, want raw bytes preserved", got)
	}
}

// ---------------------------------------------------------------------------
// Parse — text/plain with disposition=attachment is not primary body
// ---------------------------------------------------------------------------

func TestParseTextPlainAttachmentNotSelectedAsPrimaryBody(t *testing.T) {
	snapshot, err := Parse(DraftRaw{
		DraftID: "d-txtattach",
		RawEML: encodeFixtureEML(`Subject: Text attachment
From: alice@example.com
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=mix

--mix
Content-Type: text/html; charset=UTF-8

<p>real body</p>
--mix
Content-Type: text/plain; charset=UTF-8
Content-Disposition: attachment; filename=notes.txt

This is an attached text file, not the body.
--mix--
`),
	})
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	// The text/plain with disposition=attachment should NOT be the primary text part
	if snapshot.PrimaryTextPartID != "" {
		textPart := findPart(snapshot.Body, snapshot.PrimaryTextPartID)
		if textPart != nil && strings.EqualFold(textPart.ContentDisposition, "attachment") {
			t.Fatalf("attachment text/plain should not be selected as primary body, got part %q", snapshot.PrimaryTextPartID)
		}
	}
	// The text/html should be the primary HTML part
	if snapshot.PrimaryHTMLPartID == "" {
		t.Fatalf("PrimaryHTMLPartID should not be empty")
	}
	htmlPart := findPart(snapshot.Body, snapshot.PrimaryHTMLPartID)
	if got := string(htmlPart.Body); got != "<p>real body</p>" {
		t.Fatalf("html body = %q", got)
	}
}

// ---------------------------------------------------------------------------
// Parse — inline image disposition is not selected as primary body
// ---------------------------------------------------------------------------

func TestParseInlineImageNotSelectedAsPrimaryBody(t *testing.T) {
	snapshot, err := Parse(DraftRaw{
		DraftID: "d-inlineskip",
		RawEML: encodeFixtureEML(`Subject: Inline skip
From: alice@example.com
MIME-Version: 1.0
Content-Type: multipart/related; boundary=rel

--rel
Content-Type: text/html; charset=UTF-8

<p>body <img src="cid:logo"></p>
--rel
Content-Type: text/plain
Content-Disposition: inline; filename=logo.txt
Content-ID: <logo>

logo-placeholder
--rel--
`),
	})
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	// The inline text/plain with CID should NOT be the primary text part
	if snapshot.PrimaryTextPartID != "" {
		t.Fatalf("PrimaryTextPartID = %q, want empty (inline parts skipped)", snapshot.PrimaryTextPartID)
	}
	if snapshot.PrimaryHTMLPartID == "" {
		t.Fatalf("PrimaryHTMLPartID should not be empty")
	}
}

func mustReadFixtureEML(t *testing.T, path string) string {
	t.Helper()
	return encodeFixtureEML(mustReadFixture(t, path))
}
