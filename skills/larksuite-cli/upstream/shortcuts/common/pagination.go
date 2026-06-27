// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package common

import "fmt"

// PaginationMeta extracts pagination metadata from an API response data map.
func PaginationMeta(data map[string]interface{}) (hasMore bool, pageToken string) {
	hasMore, _ = data["has_more"].(bool)
	pageToken, _ = data["page_token"].(string)
	if pageToken == "" {
		pageToken, _ = data["next_page_token"].(string)
	}
	return
}

// PaginationHint returns a human-readable pagination hint for pretty output.
func PaginationHint(data map[string]interface{}, count int) string {
	hasMore, token := PaginationMeta(data)
	if !hasMore {
		return fmt.Sprintf("\n%d total\n", count)
	}
	return fmt.Sprintf("\n%d total (more available, page_token: %s)\n", count, token)
}
