// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package auth

import "strings"

// MissingScopes returns the elements of required that are absent from storedScope.
// storedScope is a space-separated list of granted scope strings (as stored in the token).
func MissingScopes(storedScope string, required []string) []string {
	granted := make(map[string]bool)
	for _, s := range strings.Fields(storedScope) {
		granted[s] = true
	}
	var missing []string
	for _, s := range required {
		if !granted[s] {
			missing = append(missing, s)
		}
	}
	return missing
}
