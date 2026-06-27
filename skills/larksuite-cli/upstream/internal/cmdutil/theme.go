// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package cmdutil

import (
	"github.com/charmbracelet/huh"
	"github.com/charmbracelet/lipgloss"
)

// ThemeFeishu returns a huh theme with Feishu brand colors.
func ThemeFeishu() *huh.Theme {
	t := huh.ThemeBase()

	var (
		blue    = lipgloss.Color("#1456F0") // 标题、边框
		teal    = lipgloss.Color("#33D6C0") // 选择器、光标、输入提示
		cyan    = lipgloss.Color("#3EC3C0") // 选中项
		orange  = lipgloss.Color("#FF811A") // 按钮高亮
		magenta = lipgloss.Color("#CC398C") // 错误
		text    = lipgloss.AdaptiveColor{Light: "#1F2329", Dark: "#E8E8E8"}
		subtext = lipgloss.AdaptiveColor{Light: "#8F959E", Dark: "#8F959E"}
		btnBg   = lipgloss.AdaptiveColor{Light: "#EEF3FF", Dark: "#2B3A5C"}
	)

	t.Focused.Base = t.Focused.Base.BorderForeground(blue)
	t.Focused.Card = t.Focused.Base
	t.Focused.Title = t.Focused.Title.Foreground(blue).Bold(true)
	t.Focused.NoteTitle = t.Focused.NoteTitle.Foreground(blue).Bold(true)
	t.Focused.Description = t.Focused.Description.Foreground(subtext)
	t.Focused.ErrorIndicator = t.Focused.ErrorIndicator.Foreground(magenta)
	t.Focused.ErrorMessage = t.Focused.ErrorMessage.Foreground(magenta)
	t.Focused.SelectSelector = t.Focused.SelectSelector.Foreground(teal)
	t.Focused.NextIndicator = t.Focused.NextIndicator.Foreground(teal)
	t.Focused.PrevIndicator = t.Focused.PrevIndicator.Foreground(teal)
	t.Focused.Option = t.Focused.Option.Foreground(text)
	t.Focused.MultiSelectSelector = t.Focused.MultiSelectSelector.Foreground(teal)
	t.Focused.SelectedOption = t.Focused.SelectedOption.Foreground(cyan)
	t.Focused.SelectedPrefix = t.Focused.SelectedPrefix.Foreground(cyan).SetString("✓ ")
	t.Focused.UnselectedOption = t.Focused.UnselectedOption.Foreground(text)
	t.Focused.UnselectedPrefix = t.Focused.UnselectedPrefix.Foreground(subtext).SetString("• ")
	t.Focused.FocusedButton = t.Focused.FocusedButton.Foreground(lipgloss.Color("#FFFFFF")).Background(orange).Bold(true)
	t.Focused.BlurredButton = t.Focused.BlurredButton.Foreground(text).Background(btnBg)

	t.Focused.TextInput.Cursor = t.Focused.TextInput.Cursor.Foreground(teal)
	t.Focused.TextInput.Placeholder = t.Focused.TextInput.Placeholder.Foreground(subtext)
	t.Focused.TextInput.Prompt = t.Focused.TextInput.Prompt.Foreground(teal)

	t.Blurred = t.Focused
	t.Blurred.Base = t.Blurred.Base.BorderStyle(lipgloss.HiddenBorder())
	t.Blurred.Card = t.Blurred.Base
	t.Blurred.NextIndicator = lipgloss.NewStyle()
	t.Blurred.PrevIndicator = lipgloss.NewStyle()

	t.Group.Title = t.Focused.Title
	t.Group.Description = t.Focused.Description
	return t
}
