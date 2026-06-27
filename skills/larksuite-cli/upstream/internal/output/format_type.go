// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package output

import "strings"

// Format represents an output format type.
type Format int

const (
	FormatJSON Format = iota
	FormatNDJSON
	FormatTable
	FormatCSV
)

// ParseFormat parses a format string into a Format value.
// The second return value is false if the format string was not recognized,
// in which case FormatJSON is returned as default.
func ParseFormat(s string) (Format, bool) {
	switch strings.ToLower(s) {
	case "json", "":
		return FormatJSON, true
	case "ndjson":
		return FormatNDJSON, true
	case "table":
		return FormatTable, true
	case "csv":
		return FormatCSV, true
	default:
		return FormatJSON, false
	}
}

// String returns the string representation of a Format.
func (f Format) String() string {
	switch f {
	case FormatNDJSON:
		return "ndjson"
	case FormatTable:
		return "table"
	case FormatCSV:
		return "csv"
	default:
		return "json"
	}
}
