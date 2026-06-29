# Recon Reports — password-protected publishing

This repository publishes Recon analysis briefs as **password-encrypted** HTML pages
on GitHub Pages. Anyone with the link sees a password prompt; the report decrypts in
their browser only with the correct password. No accounts, no server.

## What is (and isn't) in here

- ✅ **Encrypted** report files (e.g. `expense-report.html`) and a landing page (`index.html`).
- ✅ `publish_report.py` (the helper) and `reports.json` (the report list).
- ❌ **Never** the unencrypted source reports, and never any Recon pipeline files,
  prompts, or cache. Those stay in `C:\Claude\Recon` and are not published.

> Content classification: use this only for **Internal, non-regulated** material.
> Do not publish PHI, PII, or anything Yale classifies as Confidential — even encrypted.

---

## One-time setup (GitHub Desktop)

This folder is already a Git repository, so:

1. In **GitHub Desktop** → **File ▸ Add local repository…** (or the
   "Add an Existing Repository from your local drive" button) → choose
   `C:\Claude\recon-reports` → **Add repository**.
2. Click **Publish repository** (top bar).
   - Name: `recon-reports`
   - **Uncheck "Keep this code private"** — the encryption is what protects the
     content; GitHub Pages only serves *public* repos on the free plan.
   - Publish.
3. On github.com open the repo → **Settings ▸ Pages** →
   **Source: Deploy from a branch** → Branch: **main** / **/(root)** → **Save**.
4. Wait ~1 minute. Your site goes live at:

   ```
   https://OPMOYale.github.io/recon-reports/
   ```

   The expense report is at:

   ```
   https://OPMOYale.github.io/recon-reports/expense-report.html
   ```

Share the **link** and the **password** through *separate* channels (e.g. link by
email, password by text/Teams). Don't put both in the same message.

---

## Publishing a new report (or updating one)

From this folder, run:

```powershell
python publish_report.py add "C:\Claude\Recon\reports\<the-report>.html" "ChooseAStrongPassword!" --title "Report title shown on the landing page" --out short-name.html
```

This encrypts the report, drops the encrypted file here, and rebuilds `index.html`.
Then in **GitHub Desktop**: review the change → **Commit to main** → **Push origin**.
The live site updates within a minute.

### Rotating / changing a password

Re-run the same `add` command with a new password and the same `--out` name, then
commit + push. The old password stops working immediately for the new file.

### Removing a report

Delete its file and its entry from `reports.json`, run
`python publish_report.py reindex`, then commit + push.

---

## Notes & limits

- **Public repo = encrypted blobs are downloadable**, but unreadable without the
  password (AES-256). Filenames and titles in `index.html` *are* visible — keep them
  non-sensitive.
- A viewer who knows the password can save the decrypted page. Treat the password as
  the access control, and rotate it if a report should no longer be reachable.
- Requires **Node.js / npx** (StatiCrypt runs via `npx staticrypt`).
