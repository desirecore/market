// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package build

import "runtime/debug"

// Version is dynamically set by -ldflags or falls back to module info.
var Version = "DEV"

// Date is the build date in YYYY-MM-DD format, set by -ldflags.
var Date = ""

func init() {
	if Version == "DEV" {
		if info, ok := debug.ReadBuildInfo(); ok && info.Main.Version != "(devel)" {
			Version = info.Main.Version
		}
	}
	if Version == "" {
		Version = "DEV"
	}
}
