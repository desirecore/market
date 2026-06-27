// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package common

// IsDangerousUnicode reports whether r is a Unicode character that can cause
// terminal injection: BiDi overrides, zero-width characters, and Unicode line
// terminators.
func IsDangerousUnicode(r rune) bool {
	switch {
	case r >= 0x200B && r <= 0x200D: // ZWSP / ZWJ / ZWNJ
		return true
	case r == 0xFEFF: // BOM / ZWNBSP
		return true
	case r >= 0x202A && r <= 0x202E: // BiDi: LRE, RLE, PDF, LRO, RLO
		return true
	case r >= 0x2028 && r <= 0x2029: // LS, PS
		return true
	case r >= 0x2066 && r <= 0x2069: // LRI, RLI, FSI, PDI
		return true
	}
	return false
}
