// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package event

import (
	"context"
	"encoding/json"
	"strings"
)

// ImMessageReactionProcessor handles im.message.reaction.created_v1 and deleted_v1.
// A single struct serves both event types; the concrete type is set via constructor.
//
// Compact output fields:
//   - type, event_id, timestamp (from compactBase)
//   - action: "added" (created) or "removed" (deleted)
//   - message_id: the message that was reacted to
//   - emoji_type: the emoji used (e.g. "THUMBSUP")
//   - operator_id: open_id of the user who added/removed the reaction
//   - action_time: Unix timestamp of the action
type ImMessageReactionProcessor struct {
	eventType string
}

// NewImReactionCreatedProcessor creates a processor for im.message.reaction.created_v1.
func NewImReactionCreatedProcessor() *ImMessageReactionProcessor {
	return &ImMessageReactionProcessor{eventType: "im.message.reaction.created_v1"}
}

// NewImReactionDeletedProcessor creates a processor for im.message.reaction.deleted_v1.
func NewImReactionDeletedProcessor() *ImMessageReactionProcessor {
	return &ImMessageReactionProcessor{eventType: "im.message.reaction.deleted_v1"}
}

func (p *ImMessageReactionProcessor) EventType() string { return p.eventType }

func (p *ImMessageReactionProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
	if mode == TransformRaw {
		return raw
	}
	var ev struct {
		MessageID    string `json:"message_id"`
		ReactionType struct {
			EmojiType string `json:"emoji_type"`
		} `json:"reaction_type"`
		OperatorType string `json:"operator_type"`
		UserID       struct {
			OpenID string `json:"open_id"`
		} `json:"user_id"`
		ActionTime string `json:"action_time"`
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
	if ev.MessageID != "" {
		out["message_id"] = ev.MessageID
	}
	if ev.ReactionType.EmojiType != "" {
		out["emoji_type"] = ev.ReactionType.EmojiType
	}
	if ev.UserID.OpenID != "" {
		out["operator_id"] = ev.UserID.OpenID
	}
	if ev.ActionTime != "" {
		out["action_time"] = ev.ActionTime
	}
	return out
}

func (p *ImMessageReactionProcessor) DeduplicateKey(raw *RawEvent) string {
	return raw.Header.EventID
}
func (p *ImMessageReactionProcessor) WindowStrategy() WindowConfig {
	return WindowConfig{}
}
