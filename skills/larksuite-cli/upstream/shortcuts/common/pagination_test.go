// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package common

import (
	"strings"
	"testing"
)

func TestPaginationMeta(t *testing.T) {
	tests := []struct {
		name      string
		data      map[string]interface{}
		wantMore  bool
		wantToken string
	}{
		{
			name:      "has more with page_token",
			data:      map[string]interface{}{"has_more": true, "page_token": "abc"},
			wantMore:  true,
			wantToken: "abc",
		},
		{
			name:      "has more with next_page_token",
			data:      map[string]interface{}{"has_more": true, "next_page_token": "def"},
			wantMore:  true,
			wantToken: "def",
		},
		{
			name:      "page_token preferred over next_page_token",
			data:      map[string]interface{}{"has_more": true, "page_token": "abc", "next_page_token": "def"},
			wantMore:  true,
			wantToken: "abc",
		},
		{
			name:      "no more",
			data:      map[string]interface{}{"has_more": false},
			wantMore:  false,
			wantToken: "",
		},
		{
			name:      "empty data",
			data:      map[string]interface{}{},
			wantMore:  false,
			wantToken: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			hasMore, token := PaginationMeta(tt.data)
			if hasMore != tt.wantMore {
				t.Errorf("hasMore = %v, want %v", hasMore, tt.wantMore)
			}
			if token != tt.wantToken {
				t.Errorf("token = %q, want %q", token, tt.wantToken)
			}
		})
	}
}

func TestPaginationHint(t *testing.T) {
	t.Run("no more", func(t *testing.T) {
		data := map[string]interface{}{"has_more": false}
		hint := PaginationHint(data, 5)
		if !strings.Contains(hint, "5 total") {
			t.Errorf("hint = %q, want to contain '5 total'", hint)
		}
		if strings.Contains(hint, "more available") {
			t.Errorf("hint should not contain 'more available'")
		}
	})

	t.Run("has more", func(t *testing.T) {
		data := map[string]interface{}{"has_more": true, "page_token": "tok123"}
		hint := PaginationHint(data, 10)
		if !strings.Contains(hint, "10 total") {
			t.Errorf("hint = %q, want to contain '10 total'", hint)
		}
		if !strings.Contains(hint, "more available") {
			t.Errorf("hint = %q, want to contain 'more available'", hint)
		}
		if !strings.Contains(hint, "tok123") {
			t.Errorf("hint = %q, want to contain page token", hint)
		}
	})
}
