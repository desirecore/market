// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package cmdutil

import (
	"encoding/json"

	"github.com/spf13/cobra"
)

const tipsAnnotationKey = "tips"

// SetTips sets the tips for a command (stored as JSON in Annotations).
func SetTips(cmd *cobra.Command, tips []string) {
	if len(tips) == 0 {
		return
	}
	if cmd.Annotations == nil {
		cmd.Annotations = map[string]string{}
	}
	data, _ := json.Marshal(tips)
	cmd.Annotations[tipsAnnotationKey] = string(data)
}

// AddTips appends tips to a command (merges with existing).
func AddTips(cmd *cobra.Command, tips ...string) {
	existing := GetTips(cmd)
	SetTips(cmd, append(existing, tips...))
}

// GetTips retrieves the tips from a command's annotations.
func GetTips(cmd *cobra.Command) []string {
	if cmd.Annotations == nil {
		return nil
	}
	raw, ok := cmd.Annotations[tipsAnnotationKey]
	if !ok {
		return nil
	}
	var tips []string
	err := json.Unmarshal([]byte(raw), &tips)
	if err != nil {
		return nil
	}
	return tips
}
