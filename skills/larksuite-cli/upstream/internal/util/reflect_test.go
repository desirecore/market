// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package util

import "testing"

func TestIsNil(t *testing.T) {
	var nilPtr *int
	var nilSlice []int
	var nilMap map[string]int
	var nilChan chan int
	var nilFunc func()
	nonNilPtr := new(int)

	tests := []struct {
		name string
		v    interface{}
		want bool
	}{
		{"nil", nil, true},
		{"empty string", "", false},
		{"zero int", 0, false},
		{"false", false, false},
		{"non-nil map", map[string]interface{}{}, false},
		{"non-nil slice", []interface{}{}, false},
		{"string value", "hello", false},
		{"typed-nil pointer", nilPtr, true},
		{"typed-nil slice", nilSlice, true},
		{"typed-nil map", nilMap, true},
		{"typed-nil chan", nilChan, true},
		{"typed-nil func", nilFunc, true},
		{"non-nil pointer", nonNilPtr, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsNil(tt.v); got != tt.want {
				t.Errorf("IsNil(%v) = %v, want %v", tt.v, got, tt.want)
			}
		})
	}
}

func TestIsEmptyValue(t *testing.T) {
	tests := []struct {
		name string
		v    interface{}
		want bool
	}{
		{"nil", nil, true},
		{"empty string", "", true},
		{"non-empty string", "hello", false},
		{"zero int", 0, true},
		{"non-zero int", 42, false},
		{"zero float64", float64(0), true},
		{"non-zero float64", float64(3.14), false},
		{"false", false, true},
		{"true", true, false},
		{"nil slice", []interface{}(nil), true},
		{"empty slice", []interface{}{}, false},
		{"non-empty slice", []interface{}{1}, false},
		{"nil map", map[string]interface{}(nil), true},
		{"empty map", map[string]interface{}{}, false},
		{"non-empty map", map[string]interface{}{"a": 1}, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsEmptyValue(tt.v); got != tt.want {
				t.Errorf("IsEmptyValue(%v) = %v, want %v", tt.v, got, tt.want)
			}
		})
	}
}
