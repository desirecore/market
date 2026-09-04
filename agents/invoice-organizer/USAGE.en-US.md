# Invoice Organizer · Usage

## Check three things before installing

**1. A mailbox is connected.** This is the only step that requires you: authorize an account (Gmail, Outlook or IMAP) in the DesireCore mail interface. Without one, the Agent can still parse files you drop into its work directory yourself, but the collection step is unavailable.

**2. There is a work directory you can actually find.** After installation the Agent automatically receives a default workspace, but that path is hard to locate in a file manager. On the first conversation it will suggest registering a visible directory (for example `~/Documents/invoices`) and making it primary — just agree. Deliverables land there and appear in DesireCore's file workbench.

**3. It does not verify invoice authenticity.** No official verification channel is available to it. It performs format and arithmetic checks only (required fields present, amounts reconcile, the document is internally consistent) and hands you the State Taxation Administration's national VAT invoice verification platform so you can check the number yourself. If verification is what you need, this Agent is not the answer.

## How to use it

Once installed, just say what you want in plain language:

- "Sort out August's invoices" — the full pipeline: intake, extraction, dedupe, archive, ledger, report
- "How much is this month's spend?" — summary only, no mailbox re-scan
- "Have I already recorded this invoice?" — an index lookup, answered immediately
- "Export August's invoices to Excel" — rebuilds the ledger from the index without re-parsing anything
- "From now on, post new invoices automatically" — sets up the mail rule and the scheduled job, after explaining exactly what will happen

Relative dates like "last month" are converted to explicit start and end dates and read back to you before any work starts — that one step avoids most year-boundary mistakes.

## What you get

One new directory under your work directory:

```
发票/                  (invoices)
├── 台账.xlsx           (ledger; 台账.csv when the xlsx dependencies are unavailable)
├── 报告/2024-08.md     (reports; invoices spanning months write 报告/2020-08_2024-09.md)
├── 归档/2024/08/20240815_<seller>_1959.98_24312000000000020002.pdf   (archive, by year/month)
├── _inbox/            downloaded, not yet processed
├── _quarantine/       parse failures and non-invoices, each with a .reason.txt
└── .index/            dedupe index — do not edit by hand
```

The directory and file names are Chinese, matching the invoices themselves; the English glosses above
are only for reading this page. Look for `发票/` under your work directory.

The ledger has four sheets: line items, monthly summary, per-seller summary, and exceptions. Amounts follow RMB conventions (two decimal places always; a zero-amount invoice shows as `¥0.00` rather than being hidden), and invoice numbers and tax IDs are stored as text so Excel cannot turn them into `2.4312E+19`.

Every monthly report opens with a one-line conclusion before any detail, and each entry under "needs your attention" carries a concrete action rather than just a description.

## Documents it handles

- **PDF**: fully digital VAT e-invoices (the nationwide platform format used since 2023, both ordinary and special), legacy VAT electronic ordinary invoices, railway e-ticket reimbursement vouchers (both the old and new layouts), air transport e-ticket itineraries, taxi and ride-hailing receipts
- **OFD**: reads the structured invoice data carried inside the package. A 2020-style invoice ships a complete national-standard invoice XML in the package — those values are written by the issuing system rather than guessed from the layout, so that path gets full confidence. A 2024 fully-digital invoice carries only invoice tags, which cannot supply the invoice code or the per-line item breakdown; those are recovered from the layout text and confidence is lowered to match. When neither is present it falls back to layout text
- **Scans and images**: JPG, PNG, WebP, and scanned PDFs with no text layer, handed to the vision model with confidence lowered accordingly

None of this requires you to install anything. Only the `.xlsx` ledger may need Python with `openpyxl` and `pandas`; when they are missing it writes a UTF-8 BOM CSV instead (so non-Latin text opens correctly in Excel) and tells you it degraded.

## About approvals (read this before expecting unattended runs)

Organizing invoices calls confirmation-gated tools constantly — reading the mailbox, downloading attachments, writing files — and under the default approval mode each call raises an approval card. Processing a few dozen invoices raises a lot of them in a row. That is by design, not a fault.

If you want genuinely unattended operation (a ledger built overnight on a schedule, new mail posted automatically), **you** need to switch this Agent's execution-approval mode to allow-all in its settings. The cost is that its file writes and mail calls stop asking each time. Note that the "always allow" button does not currently take effect for these tools — pressing it will not stop the cards.

## What it will not do

- Never deletes, moves or forwards your mail. Mailbox cleanup stays with you
- No accounting entries, no tax filing, no input-tax-credit judgements
- No currency conversion. A foreign-currency settlement is still priced in RMB on the face of the invoice; the original amount and the rate used are copied verbatim into the notes, never converted and never totalled separately
- Never merges suspected duplicates on its own (numbers differing by one digit with every other field identical); they are listed for you to decide
- Never invents invoice fields. Whatever cannot be extracted is left empty, the original is quarantined, and the reason is stated
- Never claims to have found everything, only that within the stated range it found N candidate messages and successfully parsed M invoices

## Known limits

- **On IMAP accounts, mail rules only cover the inbox.** If you are on IMAP and your invoice mail is auto-filed into another folder, the rule will not fire; in that case ask the Agent in conversation to scan that folder. Gmail and Outlook poll the whole mailbox and are not affected
- **The local cached search matches keywords against the subject only.** Mail whose subject never says "invoice" and only mentions it in the body ("You have a new electronic voucher") will not surface that way. On Gmail the Agent switches to Gmail's own server-side search, which does cover bodies; on Outlook and IMAP it has to pull the messages locally and scan them one by one, which is slower over a wide range. It states in its summary which of the two it used
- **Outlook and IMAP have no server-side search**, so messages must be pulled locally before filtering. Over a wide range that is noticeably slower than Gmail, where the native search syntax narrows the set in one call
- **Password-protected PDFs cannot be opened.** Some invoicing platforms send them with the password in the message body. For now you need to decrypt the file yourself and drop it into `_inbox/`, and the next run will pick it up
- **Void detection relies on the text layer.** A void stamp that exists only as an image may go undetected. Void invoices get their own column in the ledger — worth a glance

## Privacy

Invoices carry company names, taxpayer IDs, bank accounts and travel details. All of it stays in your local work directory and ledger. This Agent has no outbound channel and never replies to or forwards mail on your behalf; when you want to send the ledger to someone, it hands the file back to you and you decide where it goes.
