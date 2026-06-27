// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package event

import (
	"context"
	"encoding/json"
)

// ── im.chat.updated_v1 ──────────────────────────────────────────────────────

// ImChatUpdatedProcessor handles im.chat.updated_v1 events.
//
// Compact output fields:
//   - type, event_id, timestamp (from compactBase)
//   - chat_id: the group chat that was updated
//   - operator_id: open_id of the user who made the change
//   - external: whether this is an external (cross-tenant) chat
//   - before_change: chat properties before the update (e.g. name, description)
//   - after_change: chat properties after the update
type ImChatUpdatedProcessor struct{}

func (p *ImChatUpdatedProcessor) EventType() string { return "im.chat.updated_v1" }

func (p *ImChatUpdatedProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
	if mode == TransformRaw {
		return raw
	}
	var ev struct {
		ChatID       string      `json:"chat_id"`
		OperatorID   interface{} `json:"operator_id"`
		External     bool        `json:"external"`
		AfterChange  interface{} `json:"after_change"`
		BeforeChange interface{} `json:"before_change"`
	}
	if err := json.Unmarshal(raw.Event, &ev); err != nil {
		return raw
	}
	out := compactBase(raw)
	if ev.ChatID != "" {
		out["chat_id"] = ev.ChatID
	}
	if id := openID(ev.OperatorID); id != "" {
		out["operator_id"] = id
	}
	out["external"] = ev.External
	if ev.AfterChange != nil {
		out["after_change"] = ev.AfterChange
	}
	if ev.BeforeChange != nil {
		out["before_change"] = ev.BeforeChange
	}
	return out
}

func (p *ImChatUpdatedProcessor) DeduplicateKey(raw *RawEvent) string {
	return raw.Header.EventID
}
func (p *ImChatUpdatedProcessor) WindowStrategy() WindowConfig { return WindowConfig{} }

// ── im.chat.disbanded_v1 ────────────────────────────────────────────────────

// ImChatDisbandedProcessor handles im.chat.disbanded_v1 events.
//
// Compact output fields:
//   - type, event_id, timestamp (from compactBase)
//   - chat_id: the group chat that was disbanded
//   - operator_id: open_id of the user who disbanded the chat
//   - external: whether this is an external (cross-tenant) chat
type ImChatDisbandedProcessor struct{}

func (p *ImChatDisbandedProcessor) EventType() string { return "im.chat.disbanded_v1" }

func (p *ImChatDisbandedProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
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
	if ev.ChatID != "" {
		out["chat_id"] = ev.ChatID
	}
	if id := openID(ev.OperatorID); id != "" {
		out["operator_id"] = id
	}
	out["external"] = ev.External
	return out
}

func (p *ImChatDisbandedProcessor) DeduplicateKey(raw *RawEvent) string {
	return raw.Header.EventID
}
func (p *ImChatDisbandedProcessor) WindowStrategy() WindowConfig { return WindowConfig{} }
