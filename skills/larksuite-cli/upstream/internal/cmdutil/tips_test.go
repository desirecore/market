// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package cmdutil

import (
	"testing"

	"github.com/spf13/cobra"
)

func TestSetTipsAndGetTips(t *testing.T) {
	cmd := &cobra.Command{Use: "test"}
	tips := []string{"tip one", "tip two"}
	SetTips(cmd, tips)

	got := GetTips(cmd)
	if len(got) != 2 || got[0] != "tip one" || got[1] != "tip two" {
		t.Fatalf("expected %v, got %v", tips, got)
	}
}

func TestSetTipsEmpty(t *testing.T) {
	cmd := &cobra.Command{Use: "test"}
	SetTips(cmd, nil)

	if cmd.Annotations != nil {
		t.Fatal("expected nil annotations for empty tips")
	}
}

func TestGetTipsNoAnnotations(t *testing.T) {
	cmd := &cobra.Command{Use: "test"}
	got := GetTips(cmd)
	if got != nil {
		t.Fatalf("expected nil, got %v", got)
	}
}

func TestAddTips(t *testing.T) {
	cmd := &cobra.Command{Use: "test"}
	SetTips(cmd, []string{"first"})
	AddTips(cmd, "second", "third")

	got := GetTips(cmd)
	if len(got) != 3 || got[0] != "first" || got[1] != "second" || got[2] != "third" {
		t.Fatalf("expected [first second third], got %v", got)
	}
}

func TestAddTipsToEmpty(t *testing.T) {
	cmd := &cobra.Command{Use: "test"}
	AddTips(cmd, "only")

	got := GetTips(cmd)
	if len(got) != 1 || got[0] != "only" {
		t.Fatalf("expected [only], got %v", got)
	}
}
