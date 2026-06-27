// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package util

import "reflect"

// IsNil reports whether v is nil, covering both untyped nil (interface itself)
// and typed nil (e.g. (*T)(nil) wrapped in interface{}).
// Avoids direct interface{} == nil comparison .
func IsNil(v interface{}) bool {
	rv := reflect.ValueOf(v)
	if !rv.IsValid() {
		return true
	}
	switch rv.Kind() {
	case reflect.Ptr, reflect.Map, reflect.Slice, reflect.Func, reflect.Interface, reflect.Chan:
		return rv.IsNil()
	default:
		return false
	}
}

// IsEmptyValue checks whether v is considered empty using reflect.
// Returns true for nil interface, and zero values of the underlying type
// (e.g. "", 0, false, empty slice/map).
func IsEmptyValue(v interface{}) bool {
	rv := reflect.ValueOf(v)
	if !rv.IsValid() {
		return true
	}
	return rv.IsZero()
}
