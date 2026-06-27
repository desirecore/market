// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package util

import (
	"encoding/json"
)

// ToFloat64 extracts a float64 from a value that may be float64 or json.Number.
// Returns (0, false) if the value is neither.
func ToFloat64(v interface{}) (float64, bool) {
	switch n := v.(type) {
	case float64:
		return n, true
	case json.Number:
		f, err := n.Float64()
		return f, err == nil
	case int:
		return float64(n), true
	case int64:
		return float64(n), true
	}
	return 0, false
}
