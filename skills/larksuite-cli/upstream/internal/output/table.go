// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package output

import (
	"fmt"
	"io"
	"strings"
)

const maxColWidth = 100

// FormatAsTable formats data as a table and writes it to w.
//   - []interface{} (array of objects) → header + separator + rows
//   - map[string]interface{} (single object) → key-value two-column table
//   - empty array → "(empty)"
func FormatAsTable(w io.Writer, data interface{}) {
	FormatAsTablePaginated(w, data, true)
}

// FormatAsTablePaginated formats data as a table with pagination awareness.
// When isFirstPage is true, outputs the header; otherwise only data rows.
func FormatAsTablePaginated(w io.Writer, data interface{}, isFirstPage bool) {
	rows, cols, isList := prepareRows(data)
	if cols == nil {
		if isList {
			fmt.Fprintln(w, "(empty)")
		} else {
			// Not a list and not an object — print as JSON fallback
			PrintJson(w, data)
		}
		return
	}

	if len(rows) == 0 {
		if isFirstPage {
			fmt.Fprintln(w, "(empty)")
		}
		return
	}

	if !isList {
		// Single object: key-value two-column format
		formatKeyValueTable(w, rows[0], cols)
		return
	}

	// Calculate column widths (clamped to maxColWidth)
	widths := computeColumnWidths(rows, cols)

	if isFirstPage {
		writeHeader(w, cols, widths)
	}

	for _, row := range rows {
		writeRow(w, row, cols, widths)
	}
}

// formatKeyValueTable renders a single object as a two-column key-value table.
func formatKeyValueTable(w io.Writer, row map[string]string, cols []string) {
	maxKeyWidth := 0
	for _, col := range cols {
		kw := stringWidth(col)
		if kw > maxKeyWidth {
			maxKeyWidth = kw
		}
	}

	for _, col := range cols {
		val := row[col]
		val = truncateToWidth(val, maxColWidth)
		fmt.Fprintf(w, "%s  %s\n", padToWidth(col, maxKeyWidth), val)
	}
}

// computeColumnWidths returns display widths for each column, clamped to maxColWidth.
func computeColumnWidths(rows []map[string]string, cols []string) []int {
	widths := make([]int, len(cols))
	for i, col := range cols {
		widths[i] = stringWidth(col)
	}
	for _, row := range rows {
		for i, col := range cols {
			cw := stringWidth(row[col])
			if cw > widths[i] {
				widths[i] = cw
			}
		}
	}
	// Clamp to max
	for i := range widths {
		if widths[i] > maxColWidth {
			widths[i] = maxColWidth
		}
	}
	return widths
}

// writeHeader writes the header row and separator line.
func writeHeader(w io.Writer, cols []string, widths []int) {
	var header []string
	var sep []string
	for i, col := range cols {
		header = append(header, padToWidth(col, widths[i]))
		sep = append(sep, strings.Repeat("─", widths[i]))
	}
	fmt.Fprintln(w, strings.Join(header, "  "))
	fmt.Fprintln(w, strings.Join(sep, "  "))
}

// writeRow writes a single data row.
func writeRow(w io.Writer, row map[string]string, cols []string, widths []int) {
	var cells []string
	for i, col := range cols {
		val := truncateToWidth(row[col], widths[i])
		cells = append(cells, padToWidth(val, widths[i]))
	}
	fmt.Fprintln(w, strings.Join(cells, "  "))
}

// padToWidth pads a string with spaces to reach the target display width.
func padToWidth(s string, targetWidth int) string {
	sw := stringWidth(s)
	if sw >= targetWidth {
		return s
	}
	return s + strings.Repeat(" ", targetWidth-sw)
}
