// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package event

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	"github.com/larksuite/cli/internal/output"
	convertlib "github.com/larksuite/cli/shortcuts/im/convert_lib"
)

// ImMessageProcessor handles im.message.receive_v1 events.
//
// Compact output fields:
//   - type, id, message_id, create_time, timestamp
//   - chat_id, chat_type, message_type, sender_id
//   - content: human-readable text converted via convertlib (supports text, post, image, file, card, etc.)
type ImMessageProcessor struct{}

func (p *ImMessageProcessor) EventType() string { return "im.message.receive_v1" }

func (p *ImMessageProcessor) Transform(_ context.Context, raw *RawEvent, mode TransformMode) interface{} {
	if mode == TransformRaw {
		return raw
	}

	// Compact: unmarshal event portion into IM message structure
	var ev struct {
		Message struct {
			MessageID   string        `json:"message_id"`
			ChatID      string        `json:"chat_id"`
			ChatType    string        `json:"chat_type"`
			MessageType string        `json:"message_type"`
			Content     string        `json:"content"`
			CreateTime  string        `json:"create_time"`
			Mentions    []interface{} `json:"mentions"`
		} `json:"message"`
		Sender struct {
			SenderID struct {
				OpenID string `json:"open_id"`
			} `json:"sender_id"`
		} `json:"sender"`
	}
	if err := json.Unmarshal(raw.Event, &ev); err != nil {
		return raw
	}

	// Card messages (interactive) are not yet supported for compact conversion;
	// return raw event data directly.
	if ev.Message.MessageType == "interactive" {
		fmt.Fprintf(os.Stderr, "%s[hint]%s card message (interactive) compact conversion is not yet supported, returning raw event data\n", output.Dim, output.Reset)
		return raw
	}

	// Use convertlib to convert raw content JSON into human-readable text.
	// Resolves @mention keys (e.g. @_user_1) to display names.
	content := convertlib.ConvertBodyContent(ev.Message.MessageType, &convertlib.ConvertContext{
		RawContent: ev.Message.Content,
		MentionMap: convertlib.BuildMentionKeyMap(ev.Message.Mentions),
	})

	// Build compact output with core message metadata
	out := map[string]interface{}{
		"type": raw.Header.EventType,
	}
	if ev.Message.MessageID != "" {
		out["id"] = ev.Message.MessageID
		out["message_id"] = ev.Message.MessageID
	}
	if ev.Message.CreateTime != "" {
		out["create_time"] = ev.Message.CreateTime
	}
	// Prefer header-level timestamp; fall back to message create_time
	if raw.Header.CreateTime != "" {
		out["timestamp"] = raw.Header.CreateTime
	} else if ev.Message.CreateTime != "" {
		out["timestamp"] = ev.Message.CreateTime
	}
	if ev.Message.ChatID != "" {
		out["chat_id"] = ev.Message.ChatID
	}
	if ev.Message.ChatType != "" {
		out["chat_type"] = ev.Message.ChatType
	}
	if ev.Message.MessageType != "" {
		out["message_type"] = ev.Message.MessageType
	}
	if ev.Sender.SenderID.OpenID != "" {
		out["sender_id"] = ev.Sender.SenderID.OpenID
	}
	if content != "" {
		out["content"] = content
	}
	return out
}

func (p *ImMessageProcessor) DeduplicateKey(raw *RawEvent) string { return raw.Header.EventID }
func (p *ImMessageProcessor) WindowStrategy() WindowConfig        { return WindowConfig{} }
