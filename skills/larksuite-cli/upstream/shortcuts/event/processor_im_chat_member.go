// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package event

import (
	"context"
	"encoding/json"
	"strings"
)

// ── im.chat.member.bot.added_v1 / deleted_v1 ────────────────────────────────

// ImChatBotProcessor handles im.chat.member.bot.added_v1 and deleted_v1.
// A single struct serves both event types; the concrete type is set via constructor.
//
// Compact output fields:
//   - type, event_id, timestamp (from compactBase)
//   - action: "added" or "removed"
//   - chat_id: the group chat where the bot was added/removed
//   - operator_id: open_id of the user who performed the action
//   - external: whether this is an external (cross-tenant) chat
type ImChatBotProcessor struct {
	eventType string
}

// NewImChatBotAddedProcessor creates a processor for im.chat.member.bot.added_v1.
func NewImChatBotAddedProcessor() *ImChatBotProcessor {
	return &ImChatBotProcessor{eventType: "im.chat.member.bot.added_v1"}
}

// NewImChatBotDeletedProcessor creates a processor for im.chat.member.bot.deleted_v1.
func NewImChatBotDeletedProcessor() *ImChatBotProcessor {
	return &ImChatBotProcessor{eventType: "im.chat.member.bot.deleted_v1"}
}

func (p *ImChatBotProcessor) EventType() string { return p.eventType }

func (p *ImChatBotProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
	if mode == TransformRaw {
		return raw
	}
	var ev struct {
		ChatID     string      `json:"chat_id"`
		OperatorID interface{} `json:"operator_id"`
		External   bool        `json:"external"`
	}
	if err := json.Unmarshal(raw.Event, &ev); err != nil {
		return raw
	}
	out := compactBase(raw)
	action := "added"
	if strings.Contains(p.eventType, "deleted") {
		action = "removed"
	}
	out["action"] = action
	if ev.ChatID != "" {
		out["chat_id"] = ev.ChatID
	}
	if id := openID(ev.OperatorID); id != "" {
		out["operator_id"] = id
	}
	out["external"] = ev.External
	return out
}

func (p *ImChatBotProcessor) DeduplicateKey(raw *RawEvent) string { return raw.Header.EventID }
func (p *ImChatBotProcessor) WindowStrategy() WindowConfig        { return WindowConfig{} }

// ── im.chat.member.user.added_v1 / withdrawn_v1 / deleted_v1 ────────────────

// ImChatMemberUserProcessor handles im.chat.member.user.{added,withdrawn,deleted}_v1.
// A single struct serves all three event types; the concrete type is set via constructor.
//
// Compact output fields:
//   - type, event_id, timestamp (from compactBase)
//   - action: "added", "withdrawn" (user left), or "removed" (kicked by admin)
//   - chat_id: the group chat affected
//   - operator_id: open_id of the user who performed the action
//   - user_ids: list of open_ids of the affected users
//   - external: whether this is an external (cross-tenant) chat
type ImChatMemberUserProcessor struct {
	eventType string
}

// NewImChatMemberUserAddedProcessor creates a processor for im.chat.member.user.added_v1.
func NewImChatMemberUserAddedProcessor() *ImChatMemberUserProcessor {
	return &ImChatMemberUserProcessor{eventType: "im.chat.member.user.added_v1"}
}

// NewImChatMemberUserWithdrawnProcessor creates a processor for im.chat.member.user.withdrawn_v1.
func NewImChatMemberUserWithdrawnProcessor() *ImChatMemberUserProcessor {
	return &ImChatMemberUserProcessor{eventType: "im.chat.member.user.withdrawn_v1"}
}

// NewImChatMemberUserDeletedProcessor creates a processor for im.chat.member.user.deleted_v1.
func NewImChatMemberUserDeletedProcessor() *ImChatMemberUserProcessor {
	return &ImChatMemberUserProcessor{eventType: "im.chat.member.user.deleted_v1"}
}

func (p *ImChatMemberUserProcessor) EventType() string { return p.eventType }

func (p *ImChatMemberUserProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
	if mode == TransformRaw {
		return raw
	}
	var ev struct {
		ChatID     string        `json:"chat_id"`
		OperatorID interface{}   `json:"operator_id"`
		External   bool          `json:"external"`
		Users      []interface{} `json:"users"`
	}
	if err := json.Unmarshal(raw.Event, &ev); err != nil {
		return raw
	}
	out := compactBase(raw)
	// Derive action from event type suffix
	switch {
	case strings.Contains(p.eventType, "added"):
		out["action"] = "added"
	case strings.Contains(p.eventType, "withdrawn"):
		out["action"] = "withdrawn"
	case strings.Contains(p.eventType, "deleted"):
		out["action"] = "removed"
	}
	if ev.ChatID != "" {
		out["chat_id"] = ev.ChatID
	}
	if id := openID(ev.OperatorID); id != "" {
		out["operator_id"] = id
	}
	if userIDs := extractUserIDs(ev.Users); len(userIDs) > 0 {
		out["user_ids"] = userIDs
	}
	out["external"] = ev.External
	return out
}

func (p *ImChatMemberUserProcessor) DeduplicateKey(raw *RawEvent) string {
	return raw.Header.EventID
}
func (p *ImChatMemberUserProcessor) WindowStrategy() WindowConfig {
	return WindowConfig{}
}
