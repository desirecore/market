// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package draft

import (
	"testing"
)

func TestCheckLimit_LargeBodyDoesNotCountAsAttachment(t *testing.T) {
	// A draft whose text/plain body is 20 MB should still allow adding a
	// small attachment — the body is not an attachment.
	snapshot := &DraftSnapshot{
		Body: &Part{
			MediaType: "multipart/mixed",
			Children: []*Part{
				{
					MediaType: "text/plain",
					Body:      make([]byte, 20*1024*1024), // 20 MB body
				},
			},
		},
	}

	if err := checkSnapshotAttachmentLimit(snapshot, 1024, nil); err != nil {
		t.Fatalf("should allow adding a small attachment when only the body is large: %v", err)
	}
}

func TestCheckLimit_ReplaceInlineDoesNotDoubleCount(t *testing.T) {
	// An existing inline image is 10 MB. Replacing it with a 10 MB file
	// should succeed because the old part's size is deducted.
	oldInline := &Part{
		MediaType:          "image/png",
		ContentDisposition: "inline",
		ContentID:          "img1",
		Body:               make([]byte, 10*1024*1024), // 10 MB
	}
	snapshot := &DraftSnapshot{
		Body: &Part{
			MediaType: "multipart/related",
			Children: []*Part{
				{MediaType: "text/html", Body: []byte("<img src='cid:img1'>")},
				oldInline,
			},
		},
	}

	if err := checkSnapshotAttachmentLimit(snapshot, 10*1024*1024, oldInline); err != nil {
		t.Fatalf("replace inline should not double-count: %v", err)
	}
}

func TestCheckLimit_ExceedsSizeWithAttachments(t *testing.T) {
	// Existing attachment is 20 MB. Adding a 6 MB file should exceed the 25 MB limit.
	snapshot := &DraftSnapshot{
		Body: &Part{
			MediaType: "multipart/mixed",
			Children: []*Part{
				{MediaType: "text/plain", Body: []byte("hello")},
				{
					MediaType:          "application/octet-stream",
					ContentDisposition: "attachment",
					Body:               make([]byte, 20*1024*1024), // 20 MB
				},
			},
		},
	}

	if err := checkSnapshotAttachmentLimit(snapshot, 6*1024*1024, nil); err == nil {
		t.Fatal("should reject when total attachment size exceeds 25 MB")
	}
}
