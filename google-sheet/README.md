# Save guesses to a Google Sheet

1. Create a new Google Sheet (e.g. "TC Guesses").
2. In the sheet: **Extensions → Apps Script**. Delete the sample code and paste in `Code.gs` from this folder. Save.
3. **Deploy → New deployment** → gear icon → **Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click **Deploy**, allow the permissions it asks for, and copy the **Web app URL** (ends in `/exec`).
4. Open that URL in a browser. You should see `{"ok":true,"message":"Guess endpoint is live."}`.
5. In `index.html`, set `const SHEET_URL = 'https://script.google.com/macros/s/…/exec';`, then commit and push / redeploy the site.

Guesses appear in the **Guesses** tab with the time Google received them (IST, to the millisecond), so sort by column A to see who was fastest.

If you edit `Code.gs` later, use **Deploy → Manage deployments → Edit → Version: New version**. This keeps the same URL.
