// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package output

import "testing"

func TestParseFormat(t *testing.T) {
	tests := []struct {
		input  string
		want   Format
		wantOK bool
	}{
		{"json", FormatJSON, true},
		{"JSON", FormatJSON, true},
		{"Json", FormatJSON, true},
		{"ndjson", FormatNDJSON, true},
		{"NDJSON", FormatNDJSON, true},
		{"Ndjson", FormatNDJSON, true},
		{"table", FormatTable, true},
		{"TABLE", FormatTable, true},
		{"Table", FormatTable, true},
		{"csv", FormatCSV, true},
		{"CSV", FormatCSV, true},
		{"Csv", FormatCSV, true},
		{"", FormatJSON, true},
		// Legacy/unknown values fall back to JSON with ok=false
		{"data", FormatJSON, false},
		{"raw", FormatJSON, false},
		{"RAW", FormatJSON, false},
		{"DATA", FormatJSON, false},
		{"foobar", FormatJSON, false},
		{"xml", FormatJSON, false},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got, ok := ParseFormat(tt.input)
			if got != tt.want {
				t.Errorf("ParseFormat(%q) format = %v, want %v", tt.input, got, tt.want)
			}
			if ok != tt.wantOK {
				t.Errorf("ParseFormat(%q) ok = %v, want %v", tt.input, ok, tt.wantOK)
			}
		})
	}
}

func TestFormatString(t *testing.T) {
	tests := []struct {
		format Format
		want   string
	}{
		{FormatJSON, "json"},
		{FormatNDJSON, "ndjson"},
		{FormatTable, "table"},
		{FormatCSV, "csv"},
		{Format(99), "json"}, // unknown falls back
	}

	for _, tt := range tests {
		t.Run(tt.want, func(t *testing.T) {
			got := tt.format.String()
			if got != tt.want {
				t.Errorf("Format(%d).String() = %q, want %q", tt.format, got, tt.want)
			}
		})
	}
}
