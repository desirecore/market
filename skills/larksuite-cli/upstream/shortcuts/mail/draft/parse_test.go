// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package draft

import (
	"encoding/base64"
	"testing"
)

func TestParseReplyDraftPrimaryBodies(t *testing.T) {
	raw := DraftRaw{
		DraftID: "d-1",
		RawEML: encodeFixtureEML(`Subject: =?UTF-8?B?VGVzdA==?=
From: Alice <alice@example.com>
To: Bob <bob@example.com>
Reply-To: Team <reply@example.com>
Message-ID: <draft-1@example.com>
In-Reply-To: <orig-1@example.com>
References: <root@example.com> <orig-1@example.com>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary=alt

--alt
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 7bit

hello
--alt
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

<p>hello</p>
--alt--
`),
	}

	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Subject != "Test" {
		t.Fatalf("Subject = %q, want Test", snapshot.Subject)
	}
	if snapshot.InReplyTo != "<orig-1@example.com>" {
		t.Fatalf("InReplyTo = %q", snapshot.InReplyTo)
	}
	if snapshot.References != "<root@example.com> <orig-1@example.com>" {
		t.Fatalf("References = %q", snapshot.References)
	}
	if snapshot.PrimaryTextPartID != "1.1" {
		t.Fatalf("PrimaryTextPartID = %q", snapshot.PrimaryTextPartID)
	}
	if snapshot.PrimaryHTMLPartID != "1.2" {
		t.Fatalf("PrimaryHTMLPartID = %q", snapshot.PrimaryHTMLPartID)
	}
}

func TestParsePreservesRepeatedHeadersAndNestedPartIDs(t *testing.T) {
	raw := DraftRaw{
		DraftID: "d-2",
		RawEML: encodeFixtureEML(`Subject: Nested
From: Alice <alice@example.com>
To: Bob <bob@example.com>
X-Custom: one
X-Custom: two
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=mix

--mix
Content-Type: multipart/alternative; boundary=alt

--alt
Content-Type: text/plain; charset=UTF-8

hello
--alt
Content-Type: text/html; charset=UTF-8

<p>hello</p>
--alt--
--mix
Content-Type: application/octet-stream; name=file.bin
Content-Disposition: attachment; filename=file.bin
Content-Transfer-Encoding: base64

YQ==
--mix--
`),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if got := headerValue(snapshot.Headers, "X-Custom"); got != "one" {
		t.Fatalf("first X-Custom = %q", got)
	}
	if len(snapshot.Headers) < 5 || snapshot.Headers[4].Value != "two" {
		t.Fatalf("expected repeated header to be preserved in order: %#v", snapshot.Headers)
	}
	if snapshot.PrimaryTextPartID != "1.1.1" {
		t.Fatalf("PrimaryTextPartID = %q", snapshot.PrimaryTextPartID)
	}
	if snapshot.PrimaryHTMLPartID != "1.1.2" {
		t.Fatalf("PrimaryHTMLPartID = %q", snapshot.PrimaryHTMLPartID)
	}
	if part := findPart(snapshot.Body, "1.2"); part == nil || part.FileName() != "file.bin" {
		t.Fatalf("attachment part mismatch: %#v", part)
	}
}

func TestParseDecodesQuotedPrintableTextBodyToUTF8(t *testing.T) {
	raw := DraftRaw{
		DraftID: "d-qp",
		RawEML: encodeFixtureEML(`Subject: Encoded body
From: Alice <alice@example.com>
To: Bob <bob@example.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

caf=E9
`),
	}

	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	part := findPart(snapshot.Body, snapshot.PrimaryTextPartID)
	if part == nil {
		t.Fatalf("primary text part missing")
	}
	if got := string(part.Body); got != "café\n" {
		t.Fatalf("decoded text body = %q", got)
	}
}

func TestParseSignedDraftDoesNotExposeEditablePrimaryBody(t *testing.T) {
	snapshot := mustParseFixtureDraft(t, mustReadFixture(t, "testdata/multipart_signed_draft.eml"))
	if snapshot.PrimaryTextPartID != "" {
		t.Fatalf("PrimaryTextPartID = %q, want empty for multipart/signed", snapshot.PrimaryTextPartID)
	}
	if snapshot.PrimaryHTMLPartID != "" {
		t.Fatalf("PrimaryHTMLPartID = %q, want empty for multipart/signed", snapshot.PrimaryHTMLPartID)
	}
	if part := findPart(snapshot.Body, "1.1"); part == nil || part.MediaType != "text/plain" {
		t.Fatalf("signed text part mismatch: %#v", part)
	}
}

func TestParseMultipartPreservesPreambleAndEpilogue(t *testing.T) {
	snapshot := mustParseFixtureDraft(t, mustReadFixture(t, "testdata/dirty_multipart_preamble.eml"))
	if got := string(snapshot.Body.Preamble); got != "This is a preamble line.\nStill preamble.\n" {
		t.Fatalf("preamble = %q", got)
	}
	if got := string(snapshot.Body.Epilogue); got != "This is an epilogue line.\nTrailing dirty text.\n" {
		t.Fatalf("epilogue = %q", got)
	}
	if got := headerValue(snapshot.Headers, "X-Trace"); got != "first second" {
		t.Fatalf("folded header = %q", got)
	}
}

func TestParseMultipartWithEmptyBodyPart(t *testing.T) {
	// Regression: bytes.TrimSpace in parseMultipartChildren stripped the
	// header/body separator when a MIME part had headers but an empty body,
	// causing "invalid EML: missing header/body separator".
	raw := DraftRaw{
		DraftID: "d-empty-body",
		RawEML:  encodeFixtureEML("Subject: Empty body part\r\nFrom: alice@example.com\r\nMime-Version: 1.0\r\nContent-Type: multipart/alternative;\r\n boundary=bound1\r\n\r\n--bound1\r\nContent-Transfer-Encoding: 7bit\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n\r\n--bound1\r\nContent-Transfer-Encoding: 7bit\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<p>hello</p>\r\n--bound1--\r\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Subject != "Empty body part" {
		t.Fatalf("Subject = %q", snapshot.Subject)
	}
	if snapshot.PrimaryTextPartID == "" {
		t.Fatalf("PrimaryTextPartID should not be empty")
	}
	textPart := findPart(snapshot.Body, snapshot.PrimaryTextPartID)
	if textPart == nil {
		t.Fatalf("text part not found")
	}
	if len(textPart.Body) != 0 {
		t.Fatalf("text part body should be empty, got %q", string(textPart.Body))
	}
}

func TestParseMultipartChildBodyNotCorruptedByLaterParts(t *testing.T) {
	// Regression: flush() in parseMultipartChildren returned Body slices
	// aliased to the shared bytes.Buffer backing array. When the next MIME
	// part was written to the buffer (after Reset), earlier children's Body
	// data was silently overwritten.
	raw := DraftRaw{
		DraftID: "d-alias",
		RawEML: encodeFixtureEML(`Subject: Alias test
From: alice@example.com
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary=alt

--alt
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 7bit

hello plain
--alt
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

<p>hello html</p>
--alt--
`),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	textPart := findPart(snapshot.Body, snapshot.PrimaryTextPartID)
	if textPart == nil {
		t.Fatalf("primary text part missing")
	}
	if got := string(textPart.Body); got != "hello plain" {
		t.Fatalf("text body corrupted: got %q, want %q", got, "hello plain")
	}
	htmlPart := findPart(snapshot.Body, snapshot.PrimaryHTMLPartID)
	if htmlPart == nil {
		t.Fatalf("primary html part missing")
	}
	if got := string(htmlPart.Body); got != "<p>hello html</p>" {
		t.Fatalf("html body = %q", got)
	}
}

func TestParseMultipartChildWithNoHeaders(t *testing.T) {
	// A MIME part with no headers (starts with blank line then body) is valid
	// per RFC 2046 and defaults to text/plain.
	raw := DraftRaw{
		DraftID: "d-noheader",
		RawEML:  encodeFixtureEML("Subject: No header part\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=mix\n\n--mix\n\njust body text\n--mix--\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Body == nil || len(snapshot.Body.Children) == 0 {
		t.Fatalf("expected at least one child part")
	}
	child := snapshot.Body.Children[0]
	if child.MediaType != "text/plain" {
		t.Fatalf("MediaType = %q, want text/plain", child.MediaType)
	}
	if got := string(child.Body); got != "just body text" {
		t.Fatalf("body = %q, want %q", got, "just body text")
	}
}

func TestParseMultipartHeaderlessPartWithDoubleNewlineInBody(t *testing.T) {
	// A header-less part whose body contains \n\n should not confuse the
	// parser into treating body text as headers.
	raw := DraftRaw{
		DraftID: "d-noheader-dblnl",
		RawEML:  encodeFixtureEML("Subject: HeaderlessDoubleNL\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=mix\n\n--mix\n\nfirst paragraph\n\nsecond paragraph\n--mix--\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Body == nil || len(snapshot.Body.Children) == 0 {
		t.Fatalf("expected at least one child part")
	}
	child := snapshot.Body.Children[0]
	if got := string(child.Body); got != "first paragraph\n\nsecond paragraph" {
		t.Fatalf("body = %q, want %q", got, "first paragraph\n\nsecond paragraph")
	}
}

func TestParseMalformedContentType(t *testing.T) {
	// A part with an unparseable Content-Type should fallback to
	// application/octet-stream instead of crashing the entire parse.
	raw := DraftRaw{
		DraftID: "d-badct",
		RawEML:  encodeFixtureEML("Subject: Bad CT\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=mix\n\n--mix\nContent-Type: text/plain; charset=UTF-8\n\nhello\n--mix\nContent-Type: totally broken content type !!!\n\nsome data\n--mix--\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	badPart := findPart(snapshot.Body, "1.2")
	if badPart == nil {
		t.Fatalf("expected part 1.2 to exist")
	}
	if badPart.MediaType != "application/octet-stream" {
		t.Fatalf("MediaType = %q, want application/octet-stream", badPart.MediaType)
	}
	if !badPart.EncodingProblem {
		t.Fatalf("EncodingProblem should be true for malformed Content-Type")
	}
}

func TestParseMalformedContentDisposition(t *testing.T) {
	// A part with an unparseable Content-Disposition should still parse
	// successfully, just without structured disposition info.
	raw := DraftRaw{
		DraftID: "d-baddisp",
		RawEML:  encodeFixtureEML("Subject: Bad Disp\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=mix\n\n--mix\nContent-Type: text/plain; charset=UTF-8\n\nhello\n--mix\nContent-Type: application/pdf\nContent-Disposition: attachment; filename=my file.txt\nContent-Transfer-Encoding: base64\n\nYQ==\n--mix--\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	part := findPart(snapshot.Body, "1.2")
	if part == nil {
		t.Fatalf("expected part 1.2 to exist")
	}
	// Disposition is empty because it failed to parse, but the part is accessible.
	if part.ContentDisposition != "" {
		t.Fatalf("ContentDisposition = %q, want empty (parse failed)", part.ContentDisposition)
	}
}

func TestParseMalformedBase64Attachment(t *testing.T) {
	// A part with corrupted base64 should not crash the entire parse.
	// The raw bytes are kept so the part can still round-trip via RawEntity.
	raw := DraftRaw{
		DraftID: "d-badbase64",
		RawEML:  encodeFixtureEML("Subject: Bad base64\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=mix\n\n--mix\nContent-Type: text/plain; charset=UTF-8\n\nhello\n--mix\nContent-Type: application/pdf; name=report.pdf\nContent-Disposition: attachment; filename=report.pdf\nContent-Transfer-Encoding: base64\n\n!!!not-valid-base64!!!\n--mix--\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	textPart := findPart(snapshot.Body, snapshot.PrimaryTextPartID)
	if textPart == nil || string(textPart.Body) != "hello" {
		t.Fatalf("text body = %q", string(textPart.Body))
	}
	// The broken attachment part still exists and is flagged.
	attachment := findPart(snapshot.Body, "1.2")
	if attachment == nil {
		t.Fatalf("expected broken attachment part to exist")
	}
	if !attachment.EncodingProblem {
		t.Fatalf("EncodingProblem should be true for corrupted base64")
	}
}

func TestParseMalformedBase64NoPadding(t *testing.T) {
	// base64 without padding (e.g. "YQ" instead of "YQ==") should decode via
	// RawStdEncoding fallback.
	raw := DraftRaw{
		DraftID: "d-nopad",
		RawEML:  encodeFixtureEML("Subject: No padding\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: application/octet-stream\nContent-Transfer-Encoding: base64\n\nYQ\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if got := string(snapshot.Body.Body); got != "a" {
		t.Fatalf("body = %q, want %q", got, "a")
	}
}

func TestParseMalformedAddressHeader(t *testing.T) {
	// Malformed address headers should not prevent parsing the draft.
	raw := DraftRaw{
		DraftID: "d-badaddr",
		RawEML:  encodeFixtureEML("Subject: Bad addr\nFrom: not a valid address @@\nTo: also broken <<>>\nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\n\nhello\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Subject != "Bad addr" {
		t.Fatalf("Subject = %q", snapshot.Subject)
	}
	// Addresses are nil because they couldn't be parsed, but the raw
	// header values are preserved.
	if snapshot.From != nil {
		t.Fatalf("From = %v, want nil", snapshot.From)
	}
	if got := headerValue(snapshot.Headers, "From"); got != "not a valid address @@" {
		t.Fatalf("raw From header = %q", got)
	}
}

func TestParsePrimaryBodyPartTie(t *testing.T) {
	// Two text/plain parts with the same score should not crash.
	// The first match is returned.
	raw := DraftRaw{
		DraftID: "d-tie",
		RawEML:  encodeFixtureEML("Subject: Tie\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=mix\n\n--mix\nContent-Type: text/plain; charset=UTF-8\n\nfirst\n--mix\nContent-Type: text/plain; charset=UTF-8\n\nsecond\n--mix--\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.PrimaryTextPartID == "" {
		t.Fatalf("PrimaryTextPartID should not be empty")
	}
	part := findPart(snapshot.Body, snapshot.PrimaryTextPartID)
	if part == nil {
		t.Fatalf("primary text part not found")
	}
	if got := string(part.Body); got != "first" {
		t.Fatalf("body = %q, want first match", got)
	}
}

func TestParseBrokenInlineCIDNotError(t *testing.T) {
	// A draft whose HTML references a CID that doesn't exist should still
	// parse successfully. The broken reference is surfaced as a warning in
	// Project(), not as a parse error.
	raw := DraftRaw{
		DraftID: "d-brokencid",
		RawEML: encodeFixtureEML(`Subject: Broken CID
From: alice@example.com
MIME-Version: 1.0
Content-Type: multipart/related; boundary=rel

--rel
Content-Type: text/html; charset=UTF-8

<p>hello <img src="cid:nonexistent"></p>
--rel--
`),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.PrimaryHTMLPartID == "" {
		t.Fatalf("PrimaryHTMLPartID should not be empty")
	}
}

func TestParseMalformedQuotedPrintableDoesNotCrash(t *testing.T) {
	// Go's quotedprintable.Reader is lenient (e.g. =ZZ passes through).
	// Verify that even with garbage QP content, parsing always succeeds and
	// the body is non-empty.
	raw := DraftRaw{
		DraftID: "d-badqp",
		RawEML:  encodeFixtureEML("Subject: Bad QP\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: quoted-printable\n\nhello =ZZ world\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Body == nil {
		t.Fatalf("body part missing")
	}
	if len(snapshot.Body.Body) == 0 {
		t.Fatalf("body should not be empty")
	}
}

func TestParseBoundaryNotFound(t *testing.T) {
	// A multipart that declares a boundary but the body doesn't contain it
	// should be reclassified as text rather than producing an empty multipart.
	raw := DraftRaw{
		DraftID: "d-noboundary",
		RawEML:  encodeFixtureEML("Subject: No boundary\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary=nonexistent\n\nThis body has no boundary markers at all.\nJust plain text.\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Body == nil {
		t.Fatalf("body part missing")
	}
	// Should be reclassified from multipart/mixed to text/plain.
	if snapshot.Body.MediaType != "text/plain" {
		t.Fatalf("MediaType = %q, want text/plain (reclassified)", snapshot.Body.MediaType)
	}
	if !snapshot.Body.EncodingProblem {
		t.Fatalf("EncodingProblem should be true for reclassified multipart")
	}
	if len(snapshot.Body.Children) != 0 {
		t.Fatalf("Children should be empty after reclassification")
	}
	if len(snapshot.Body.Body) == 0 {
		t.Fatalf("body should contain the text content")
	}
}

func TestParseHeaderLineWithoutColon(t *testing.T) {
	// Header lines without a colon should be silently skipped.
	raw := DraftRaw{
		DraftID: "d-nocolon",
		RawEML:  encodeFixtureEML("Subject: With garbage\nThis line has no colon\nFrom: alice@example.com\nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\n\nhello\n"),
	}
	snapshot, err := Parse(raw)
	if err != nil {
		t.Fatalf("Parse() error = %v", err)
	}
	if snapshot.Subject != "With garbage" {
		t.Fatalf("Subject = %q", snapshot.Subject)
	}
	if got := string(snapshot.Body.Body); got != "hello\n" {
		t.Fatalf("body = %q", got)
	}
}

func encodeFixtureEML(raw string) string {
	return base64.URLEncoding.EncodeToString([]byte(raw))
}
