// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package output

import (
	"bytes"
	"strings"
	"testing"
)

func TestFormatAsTable_ObjectArray(t *testing.T) {
	data := []interface{}{
		map[string]interface{}{"name": "Alice", "age": float64(30)},
		map[string]interface{}{"name": "Bob", "age": float64(25)},
	}

	var buf bytes.Buffer
	FormatAsTable(&buf, data)
	out := buf.String()

	if !strings.Contains(out, "name") {
		t.Errorf("output should contain 'name' header, got:\n%s", out)
	}
	if !strings.Contains(out, "age") {
		t.Errorf("output should contain 'age' header, got:\n%s", out)
	}
	if !strings.Contains(out, "Alice") {
		t.Errorf("output should contain 'Alice', got:\n%s", out)
	}
	if !strings.Contains(out, "Bob") {
		t.Errorf("output should contain 'Bob', got:\n%s", out)
	}
	// Should contain separator with ─
	if !strings.Contains(out, "─") {
		t.Errorf("output should contain ─ separator, got:\n%s", out)
	}
}

func TestFormatAsTable_SingleObject(t *testing.T) {
	data := map[string]interface{}{
		"name": "Alice",
		"age":  float64(30),
	}

	var buf bytes.Buffer
	FormatAsTable(&buf, data)
	out := buf.String()

	if !strings.Contains(out, "name") {
		t.Errorf("output should contain 'name', got:\n%s", out)
	}
	if !strings.Contains(out, "Alice") {
		t.Errorf("output should contain 'Alice', got:\n%s", out)
	}
}

func TestFormatAsTable_EmptyArray(t *testing.T) {
	data := []interface{}{}

	var buf bytes.Buffer
	FormatAsTable(&buf, data)
	out := strings.TrimSpace(buf.String())

	if out != "(empty)" {
		t.Errorf("empty array should output '(empty)', got:\n%s", out)
	}
}

func TestFormatAsTable_NestedFlattening(t *testing.T) {
	data := []interface{}{
		map[string]interface{}{
			"user": map[string]interface{}{
				"name": "Alice",
			},
			"id": float64(1),
		},
	}

	var buf bytes.Buffer
	FormatAsTable(&buf, data)
	out := buf.String()

	if !strings.Contains(out, "user.name") {
		t.Errorf("output should contain flattened 'user.name' column, got:\n%s", out)
	}
	if !strings.Contains(out, "Alice") {
		t.Errorf("output should contain 'Alice', got:\n%s", out)
	}
}

func TestFormatAsTable_ColumnUnionFromAllRows(t *testing.T) {
	data := []interface{}{
		map[string]interface{}{"a": "1"},
		map[string]interface{}{"a": "2", "b": "3"},
	}

	var buf bytes.Buffer
	FormatAsTable(&buf, data)
	out := buf.String()

	if !strings.Contains(out, "b") {
		t.Errorf("output should contain column 'b' from second row, got:\n%s", out)
	}
}

func TestFormatAsTablePaginated_FirstPage(t *testing.T) {
	data := []interface{}{
		map[string]interface{}{"name": "Alice"},
	}

	var buf bytes.Buffer
	FormatAsTablePaginated(&buf, data, true)
	out := buf.String()

	// First page should have header
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) < 3 {
		t.Errorf("first page should have header + separator + data, got %d lines:\n%s", len(lines), out)
	}
}

func TestFormatAsTablePaginated_ContinuationPage(t *testing.T) {
	data := []interface{}{
		map[string]interface{}{"name": "Bob"},
	}

	var buf bytes.Buffer
	FormatAsTablePaginated(&buf, data, false)
	out := buf.String()

	// Continuation page should not have header/separator
	if strings.Contains(out, "─") {
		t.Errorf("continuation page should not contain separator, got:\n%s", out)
	}
	if !strings.Contains(out, "Bob") {
		t.Errorf("continuation page should contain data, got:\n%s", out)
	}
	lines := strings.Split(strings.TrimRight(out, "\n"), "\n")
	if len(lines) != 1 {
		t.Errorf("continuation page should have 1 data line, got %d lines:\n%s", len(lines), out)
	}
}

func TestFormatAsTable_ColumnWidthClamp(t *testing.T) {
	// Create a value longer than maxColWidth
	longVal := strings.Repeat("x", 101)
	data := []interface{}{
		map[string]interface{}{"col": longVal},
	}

	var buf bytes.Buffer
	FormatAsTable(&buf, data)
	out := buf.String()

	if strings.Contains(out, longVal) {
		t.Errorf("output should not contain the full long value (should be truncated)")
	}
	if !strings.Contains(out, "…") {
		t.Errorf("output should contain truncation marker …, got:\n%s", out)
	}
}
