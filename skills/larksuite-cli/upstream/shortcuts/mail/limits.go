// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package mail

// Mail composition limits enforced before sending.
const (
	// MaxAttachmentCount is the maximum number of attachments (including original
	// attachments carried over in +forward) allowed per message.
	MaxAttachmentCount = 250

	// MaxAttachmentBytes is the maximum combined size of all attachments in bytes.
	// Note: the overall EML size limit (emlbuilder.MaxEMLSize) is enforced separately.
	MaxAttachmentBytes = 25 * 1024 * 1024 // 25 MB

	// MaxAttachmentDownloadBytes is the safety limit for downloading a single
	// attachment. This is larger than MaxAttachmentBytes (which governs outgoing
	// composition) to allow for received attachments that exceed the send-side
	// limit. The purpose is to prevent unbounded memory allocation.
	MaxAttachmentDownloadBytes = 35 * 1024 * 1024 // 35 MB

	// MaxRecipientCount is the maximum total number of recipients (To + CC + BCC
	// combined) allowed per message. This is a defence-in-depth measure to prevent
	// abuse such as mass spam or mail bombing via the CLI.
	MaxRecipientCount = 500
)
