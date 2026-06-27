// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package skillscheck

import (
	"os"
	"testing"
)

// clearSkillsSkipEnv unsets the env vars shouldSkip checks so the
// host environment cannot pollute test results.
func clearSkillsSkipEnv(t *testing.T) {
	t.Helper()
	for _, key := range []string{"LARKSUITE_CLI_NO_SKILLS_NOTIFIER", "CI", "BUILD_NUMBER", "RUN_ID"} {
		t.Setenv(key, "")
		os.Unsetenv(key)
	}
}

func TestShouldSkip(t *testing.T) {
	tests := []struct {
		name    string
		setup   func(t *testing.T)
		version string
		want    bool
	}{
		{"release_no_skip", clearSkillsSkipEnv, "1.0.21", false},
		{"dev_uppercase", clearSkillsSkipEnv, "DEV", true},
		{"dev_lowercase", clearSkillsSkipEnv, "dev", true},
		{"empty_version", clearSkillsSkipEnv, "", true},
		{"git_describe", clearSkillsSkipEnv, "1.0.0-12-g9b933f1-dirty", true},
		{"opt_out", func(t *testing.T) {
			clearSkillsSkipEnv(t)
			t.Setenv("LARKSUITE_CLI_NO_SKILLS_NOTIFIER", "1")
		}, "1.0.21", true},
		{"ci_env", func(t *testing.T) {
			clearSkillsSkipEnv(t)
			t.Setenv("CI", "true")
		}, "1.0.21", true},
		{"build_number_env", func(t *testing.T) {
			clearSkillsSkipEnv(t)
			t.Setenv("BUILD_NUMBER", "42")
		}, "1.0.21", true},
		{"run_id_env", func(t *testing.T) {
			clearSkillsSkipEnv(t)
			t.Setenv("RUN_ID", "abc")
		}, "1.0.21", true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.setup(t)
			if got := shouldSkip(tt.version); got != tt.want {
				t.Errorf("shouldSkip(%q) = %v, want %v", tt.version, got, tt.want)
			}
		})
	}
}

// Independent opt-out: LARKSUITE_CLI_NO_SKILLS_NOTIFIER must NOT be
// affected by LARKSUITE_CLI_NO_UPDATE_NOTIFIER (different env vars).
func TestShouldSkip_OptOutIsIndependent(t *testing.T) {
	clearSkillsSkipEnv(t)
	t.Setenv("LARKSUITE_CLI_NO_UPDATE_NOTIFIER", "1") // update opt-out, not us
	if shouldSkip("1.0.21") {
		t.Error("shouldSkip(release) = true with only LARKSUITE_CLI_NO_UPDATE_NOTIFIER set, want false")
	}
}
