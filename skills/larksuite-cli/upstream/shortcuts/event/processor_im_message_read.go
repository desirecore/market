// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package event

import (
	"context"
	"encoding/json"
)

// ── im.message.message_read_v1 ──────────────────────────────────────────────

// ImMessageReadProcessor handles im.message.message_read_v1 events.
//
// Compact output fields:
//   - type, event_id, timestamp (from compactBase)
//   - reader_id: the open_id of the user who read the message
//   - read_time: Unix timestamp of the read action
//   - message_ids: list of message IDs that were read
type ImMessageReadProcessor struct{}

func (p *ImMessageReadProcessor) EventType() string { return "im.message.message_read_v1" }

func (p *ImMessageReadProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
	if mode == TransformRaw {
		return raw
	}
	var ev struct {
		Reader struct {
			ReaderID struct {
				OpenID string `json:"open_id"`
			} `json:"reader_id"`
			ReadTime string `json:"read_time"`
		} `json:"reader"`
		MessageIDList []string `json:"message_id_list"`
	}
	if err := json.Unmarshal(raw.Event, &ev); err != nil {
		return raw
	}
	out := compactBase(raw)
	if ev.Reader.ReaderID.OpenID != "" {
		out["reader_id"] = ev.Reader.ReaderID.OpenID
	}
	if ev.Reader.ReadTime != "" {
		out["read_time"] = ev.Reader.ReadTime
	}
	if len(ev.MessageIDList) > 0 {
		out["message_ids"] = ev.MessageIDList
	}
	return out
}

func (p *ImMessageReadProcessor) DeduplicateKey(raw *RawEvent) string {
	return raw.Header.EventID
}
func (p *ImMessageReadProcessor) WindowStrategy() WindowConfig { return WindowConfig{} }
