// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package validate

import (
	"strings"
	"testing"
)

func TestResourceName_RejectsInjectionPatterns(t *testing.T) {
	for _, tt := range []struct {
		name    string
		input   string
		flag    string
		wantErr bool
	}{
		// ── GIVEN: normal API identifiers → THEN: allowed ──
		{"normal id", "om_abc123", "--message", false},
		{"file token", "boxcnXYZ789", "--file-token", false},
		{"with slash", "files/abc", "--resource", false},
		{"with underscore", "om_xxx_yyy", "--message", false},
		{"with hyphen", "file-token-123", "--file-token", false},
		{"single char", "a", "--id", false},
		{"slash only", "/", "--id", false},

		// ── GIVEN: path traversal attempts → THEN: rejected ──
		{"dot-dot traversal", "../admin/secret", "--message", true},
		{"mid path traversal", "files/../admin", "--message", true},
		{"bare dot-dot", "..", "--message", true},

		// ── GIVEN: URL special characters → THEN: rejected ──
		{"question mark", "id?admin=true", "--id", true},
		{"hash fragment", "id#section", "--id", true},
		{"percent encoding", "id%2e%2e", "--id", true},

		// ── GIVEN: control characters → THEN: rejected ──
		{"null byte", "id\x00rest", "--id", true},
		{"newline", "id\nrest", "--id", true},
		{"tab", "id\trest", "--id", true},
		{"escape char", "id\x1brest", "--id", true},

		// ── GIVEN: dangerous Unicode → THEN: rejected ──
		{"bidi RLO", "om_\u202Exxx", "--message", true},
		{"zero width space", "om_\u200Bxxx", "--message", true},
		{"BOM", "om_\uFEFFxxx", "--message", true},

		// ── GIVEN: empty input → THEN: rejected ──
		{"empty string", "", "--message", true},
	} {
		t.Run(tt.name, func(t *testing.T) {
			// WHEN: ResourceName validates the identifier
			err := ResourceName(tt.input, tt.flag)

			// THEN: error matches expectation
			if (err != nil) != tt.wantErr {
				t.Errorf("ResourceName(%q, %q) error = %v, wantErr %v",
					tt.input, tt.flag, err, tt.wantErr)
			}
		})
	}
}

func TestResourceName_ErrorMessageContainsFlagName(t *testing.T) {
	// GIVEN: an empty resource name with flag "--file-token"

	// WHEN: ResourceName rejects it
	err := ResourceName("", "--file-token")

	// THEN: the error message contains the flag name for user-facing diagnostics
	if err == nil {
		t.Fatal("expected error")
	}
	if !strings.Contains(err.Error(), "--file-token") {
		t.Errorf("error should contain flag name, got: %s", err.Error())
	}
}

func TestEncodePathSegment_EncodesSpecialCharacters(t *testing.T) {
	for _, tt := range []struct {
		name  string
		input string
		want  string
	}{
		// ── GIVEN: safe characters → THEN: unchanged ──
		{"normal", "om_abc123", "om_abc123"},
		{"empty", "", ""},

		// ── GIVEN: URL-special characters → THEN: percent-encoded ──
		{"slash", "a/b", "a%2Fb"},
		{"space", "hello world", "hello%20world"},
		{"question mark", "id?foo", "id%3Ffoo"},
		{"hash", "id#bar", "id%23bar"},
		{"dot-dot", "../admin", "..%2Fadmin"},
		{"percent", "50%done", "50%25done"},
		{"unicode", "报告", "%E6%8A%A5%E5%91%8A"},
	} {
		t.Run(tt.name, func(t *testing.T) {
			// WHEN: EncodePathSegment encodes the input
			got := EncodePathSegment(tt.input)

			// THEN: output matches expected encoding
			if got != tt.want {
				t.Errorf("EncodePathSegment(%q) = %q, want %q", tt.input, got, tt.want)
			}
		})
	}
}
