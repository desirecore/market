// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package filecheck

import (
	"testing"
)

func TestCheckBlockedExtension(t *testing.T) {
	tests := []struct {
		filename string
		blocked  bool
	}{
		// Blocked extensions
		{"malware.exe", true},
		{"script.bat", true},
		{"payload.cmd", true},
		{"trojan.scr", true},
		{"installer.msi", true},
		{"hack.ps1", true},
		{"code.js", true},
		{"code.py", true},
		{"code.sh", true},
		{"code.vbs", true},
		{"package.jar", true},
		{"binary.dll", true},
		{"link.lnk", true},
		{"helper.hta", true},
		{"app.ipa", true},
		{"app.apk", true},

		// Case insensitivity
		{"VIRUS.EXE", true},
		{"Script.Bat", true},
		{"CODE.JS", true},

		// Allowed extensions
		{"report.pdf", false},
		{"photo.jpg", false},
		{"image.png", false},
		{"document.docx", false},
		{"spreadsheet.xlsx", false},
		{"archive.zip", false},
		{"data.csv", false},
		{"email.eml", false},
		{"notes.txt", false},
		{"page.html", false},
		{"page.htm", false},

		// No extension / dot files
		{"Makefile", false},
		{".gitignore", false},
		{"README", false},
	}

	for _, tt := range tests {
		t.Run(tt.filename, func(t *testing.T) {
			err := CheckBlockedExtension(tt.filename)
			if tt.blocked && err == nil {
				t.Errorf("expected %q to be blocked", tt.filename)
			}
			if !tt.blocked && err != nil {
				t.Errorf("expected %q to be allowed, got: %v", tt.filename, err)
			}
		})
	}
}

// Minimal valid file headers for content sniffing.
var (
	pngHeader  = []byte{0x89, 'P', 'N', 'G', 0x0D, 0x0A, 0x1A, 0x0A}
	jpegHeader = []byte{0xFF, 0xD8, 0xFF, 0xE0}
	gifHeader  = []byte("GIF89a")
	webpHeader = append([]byte("RIFF\x00\x00\x00\x00WEBPVP8 "), make([]byte, 20)...)
	pdfHeader  = []byte("%PDF-1.4")
	exeHeader  = []byte("MZ")
)

func TestCheckInlineImageFormat(t *testing.T) {
	tests := []struct {
		name    string
		file    string
		content []byte
		wantErr bool
	}{
		// Allowed: extension + content both match
		{"png ok", "logo.png", pngHeader, false},
		{"jpg ok", "photo.jpg", jpegHeader, false},
		{"jpeg ok", "photo.jpeg", jpegHeader, false},
		{"gif ok", "anim.gif", gifHeader, false},
		{"webp ok", "image.webp", webpHeader, false},
		{"PNG uppercase", "LOGO.PNG", pngHeader, false},

		// Rejected: wrong extension, valid image content
		{"svg ext + png content", "icon.svg", pngHeader, true},
		{"bmp ext + png content", "icon.bmp", pngHeader, true},
		{"tiff ext + png content", "icon.tiff", pngHeader, true},
		{"txt ext + png content", "file.txt", pngHeader, true},

		// Rejected: valid extension, wrong content (spoofed)
		{"png ext + exe content", "evil.png", exeHeader, true},
		{"jpg ext + pdf content", "evil.jpg", pdfHeader, true},
		{"gif ext + plain text", "evil.gif", []byte("not an image"), true},

		// Rejected: both wrong
		{"exe ext + exe content", "malware.exe", exeHeader, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ct, err := CheckInlineImageFormat(tt.file, tt.content)
			if tt.wantErr && err == nil {
				t.Errorf("expected error for %q", tt.name)
			}
			if !tt.wantErr && err != nil {
				t.Errorf("expected no error for %q, got: %v", tt.name, err)
			}
			if !tt.wantErr && ct == "" {
				t.Errorf("expected non-empty content type for %q", tt.name)
			}
		})
	}
}
