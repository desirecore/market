// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package draft

import (
	"strings"
	"testing"
)

// ---------------------------------------------------------------------------
// Part.Clone — deep copy preserves values, mutations don't leak
// ---------------------------------------------------------------------------

func TestPartCloneDeepCopy(t *testing.T) {
	original := &Part{
		PartID:    "1",
		MediaType: "multipart/mixed",
		MediaParams: map[string]string{
			"boundary": "test-boundary",
		},
		Headers: []Header{
			{Name: "Content-Type", Value: "multipart/mixed; boundary=test-boundary"},
		},
		Preamble: []byte("preamble text"),
		Epilogue: []byte("epilogue text"),
		Children: []*Part{
			{
				PartID:    "1.1",
				MediaType: "text/plain",
				MediaParams: map[string]string{
					"charset": "UTF-8",
				},
				Body: []byte("hello world"),
				Headers: []Header{
					{Name: "Content-Type", Value: "text/plain; charset=UTF-8"},
				},
			},
			{
				PartID:                "1.2",
				MediaType:             "application/pdf",
				ContentDisposition:    "attachment",
				ContentDispositionArg: map[string]string{"filename": "test.pdf"},
				Body:                  []byte("pdf-content"),
			},
		},
	}

	clone := original.Clone()

	// Verify values match
	if clone.PartID != original.PartID {
		t.Fatalf("PartID = %q, want %q", clone.PartID, original.PartID)
	}
	if clone.MediaParams["boundary"] != "test-boundary" {
		t.Fatalf("MediaParams boundary = %q", clone.MediaParams["boundary"])
	}
	if len(clone.Children) != 2 {
		t.Fatalf("Children len = %d, want 2", len(clone.Children))
	}
	if string(clone.Children[0].Body) != "hello world" {
		t.Fatalf("child body = %q", string(clone.Children[0].Body))
	}

	// Mutate clone — should not affect original
	clone.Children[0].Body = []byte("mutated")
	clone.MediaParams["boundary"] = "changed"
	clone.Preamble = []byte("changed preamble")

	if string(original.Children[0].Body) != "hello world" {
		t.Fatalf("original child body leaked: %q", string(original.Children[0].Body))
	}
	if original.MediaParams["boundary"] != "test-boundary" {
		t.Fatalf("original MediaParams leaked: %q", original.MediaParams["boundary"])
	}
	if string(original.Preamble) != "preamble text" {
		t.Fatalf("original Preamble leaked: %q", string(original.Preamble))
	}
}

func TestPartCloneNilReturnsNil(t *testing.T) {
	var p *Part
	if got := p.Clone(); got != nil {
		t.Fatalf("Clone(nil) = %#v, want nil", got)
	}
}

// ---------------------------------------------------------------------------
// PatchOp.Validate — covering branches not tested elsewhere
// ---------------------------------------------------------------------------

func TestPatchOpValidateAddRecipient(t *testing.T) {
	tests := []struct {
		name    string
		op      PatchOp
		wantErr string
	}{
		{
			name:    "add_recipient missing field",
			op:      PatchOp{Op: "add_recipient", Field: "x-invalid", Address: "a@b.com"},
			wantErr: "recipient field must be one of to/cc/bcc",
		},
		{
			name:    "add_recipient missing address",
			op:      PatchOp{Op: "add_recipient", Field: "to", Address: "  "},
			wantErr: "requires address",
		},
		{
			name:    "remove_recipient missing field",
			op:      PatchOp{Op: "remove_recipient", Field: "invalid", Address: "a@b.com"},
			wantErr: "recipient field must be one of to/cc/bcc",
		},
		{
			name:    "remove_recipient missing address",
			op:      PatchOp{Op: "remove_recipient", Field: "cc", Address: "  "},
			wantErr: "requires address",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.op.Validate()
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("Validate() = %v, want error containing %q", err, tt.wantErr)
			}
		})
	}
}

func TestPatchOpValidateSetReplyToRequiresAddresses(t *testing.T) {
	err := PatchOp{Op: "set_reply_to", Addresses: nil}.Validate()
	if err == nil || !strings.Contains(err.Error(), "requires addresses") {
		t.Fatalf("Validate() = %v, want error about addresses", err)
	}
}

func TestPatchOpValidateBodyKind(t *testing.T) {
	tests := []struct {
		name    string
		op      PatchOp
		wantErr string
	}{
		{
			name:    "replace_body invalid body_kind",
			op:      PatchOp{Op: "replace_body", BodyKind: "text/csv"},
			wantErr: "body_kind must be text/plain or text/html",
		},
		{
			name:    "append_body invalid body_kind",
			op:      PatchOp{Op: "append_body", BodyKind: "application/json"},
			wantErr: "body_kind must be text/plain or text/html",
		},
		{
			name:    "replace_body invalid selector",
			op:      PatchOp{Op: "replace_body", BodyKind: "text/html", Selector: "secondary"},
			wantErr: "selector must be primary",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.op.Validate()
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("Validate() = %v, want error containing %q", err, tt.wantErr)
			}
		})
	}
}

func TestPatchOpValidateSetHeader(t *testing.T) {
	tests := []struct {
		name    string
		op      PatchOp
		wantErr string
	}{
		{
			name:    "empty name",
			op:      PatchOp{Op: "set_header", Name: "  ", Value: "val"},
			wantErr: "requires name",
		},
		{
			name:    "name with colon",
			op:      PatchOp{Op: "set_header", Name: "Bad:Name", Value: "val"},
			wantErr: "must not contain",
		},
		{
			name:    "name with newline",
			op:      PatchOp{Op: "set_header", Name: "Bad\nName", Value: "val"},
			wantErr: "must not contain",
		},
		{
			name:    "value with CR",
			op:      PatchOp{Op: "set_header", Name: "X-Custom", Value: "val\rinjected"},
			wantErr: "must not contain",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.op.Validate()
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("Validate() = %v, want error containing %q", err, tt.wantErr)
			}
		})
	}
}

func TestPatchOpValidateRemoveHeaderRequiresName(t *testing.T) {
	err := PatchOp{Op: "remove_header", Name: "  "}.Validate()
	if err == nil || !strings.Contains(err.Error(), "requires name") {
		t.Fatalf("Validate() = %v, want error about name", err)
	}
}

func TestPatchOpValidateAttachmentOps(t *testing.T) {
	tests := []struct {
		name    string
		op      PatchOp
		wantErr string
	}{
		{
			name:    "add_attachment missing path",
			op:      PatchOp{Op: "add_attachment", Path: "  "},
			wantErr: "requires path",
		},
		{
			name:    "remove_attachment missing target",
			op:      PatchOp{Op: "remove_attachment"},
			wantErr: "requires target",
		},
		{
			name:    "add_inline missing path",
			op:      PatchOp{Op: "add_inline", Path: "  ", CID: "cid1"},
			wantErr: "requires path",
		},
		{
			name:    "add_inline missing cid",
			op:      PatchOp{Op: "add_inline", Path: "/tmp/f", CID: "  "},
			wantErr: "requires cid",
		},
		{
			name:    "replace_inline missing target",
			op:      PatchOp{Op: "replace_inline", Path: "/tmp/f"},
			wantErr: "requires target",
		},
		{
			name:    "replace_inline missing path",
			op:      PatchOp{Op: "replace_inline", Target: AttachmentTarget{PartID: "1.2"}, Path: "  "},
			wantErr: "requires path",
		},
		{
			name:    "remove_inline missing target",
			op:      PatchOp{Op: "remove_inline"},
			wantErr: "requires target",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.op.Validate()
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("Validate() = %v, want error containing %q", err, tt.wantErr)
			}
		})
	}
}

func TestPatchOpValidateUnsupportedOp(t *testing.T) {
	err := PatchOp{Op: "fly_to_moon"}.Validate()
	if err == nil || !strings.Contains(err.Error(), "unsupported") {
		t.Fatalf("Validate() = %v, want unsupported error", err)
	}
}

func TestPatchValidateEmptyOps(t *testing.T) {
	err := Patch{}.Validate()
	if err == nil || !strings.Contains(err.Error(), "ops is required") {
		t.Fatalf("Validate() = %v, want ops required error", err)
	}
}

func TestPatchValidatePropagatesOpError(t *testing.T) {
	err := Patch{
		Ops: []PatchOp{
			{Op: "set_subject", Value: "ok"},
			{Op: "set_header", Name: "", Value: "val"},
		},
	}.Validate()
	if err == nil || !strings.Contains(err.Error(), "#2") {
		t.Fatalf("Validate() = %v, want error mentioning op #2", err)
	}
}

// ---------------------------------------------------------------------------
// Patch.Summary
// ---------------------------------------------------------------------------

func TestPatchSummaryContainsOpsAndWarning(t *testing.T) {
	patch := Patch{
		Ops: []PatchOp{{Op: "set_subject", Value: "test"}},
	}
	summary := patch.Summary()
	if _, ok := summary["ops"]; !ok {
		t.Fatalf("Summary() missing 'ops' key")
	}
	warnings, ok := summary["warnings"].([]string)
	if !ok || len(warnings) == 0 {
		t.Fatalf("Summary() missing warnings")
	}
}

func TestPatchSummaryIncludesOptionsWhenSet(t *testing.T) {
	patch := Patch{
		Ops:     []PatchOp{{Op: "set_subject", Value: "test"}},
		Options: PatchOptions{RewriteEntireDraft: true},
	}
	summary := patch.Summary()
	if _, ok := summary["options"]; !ok {
		t.Fatalf("Summary() should include options when non-default")
	}
}

// ---------------------------------------------------------------------------
// Address.String
// ---------------------------------------------------------------------------

func TestAddressStringWithoutName(t *testing.T) {
	addr := Address{Address: "alice@example.com"}
	if got := addr.String(); got != "alice@example.com" {
		t.Fatalf("String() = %q", got)
	}
}

func TestAddressStringWithName(t *testing.T) {
	addr := Address{Name: "Alice", Address: "alice@example.com"}
	got := addr.String()
	if !strings.Contains(got, "Alice") || !strings.Contains(got, "alice@example.com") {
		t.Fatalf("String() = %q", got)
	}
}

// ---------------------------------------------------------------------------
// Part.FileName fallback
// ---------------------------------------------------------------------------

func TestPartFileNameFallbackToMediaParams(t *testing.T) {
	part := &Part{
		MediaParams: map[string]string{"name": "photo.jpg"},
	}
	if got := part.FileName(); got != "photo.jpg" {
		t.Fatalf("FileName() = %q, want photo.jpg", got)
	}
}

func TestPartFileNameNilPart(t *testing.T) {
	var p *Part
	if got := p.FileName(); got != "" {
		t.Fatalf("FileName(nil) = %q", got)
	}
}
