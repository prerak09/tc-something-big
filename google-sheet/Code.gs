/**
 * Receives guesses from the teaser page and appends them to this spreadsheet.
 * Paste into Extensions → Apps Script of the Google Sheet, then deploy as a web app
 * (see README.md in this folder).
 */
const SHEET_NAME = 'Guesses';
const TIMEZONE = 'Asia/Kolkata';

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    const data = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const name = String(data.name || '').replace(/\s+/g, ' ').trim().slice(0, 40);
    const guess = String(data.guess || '').replace(/\s+/g, ' ').trim().slice(0, 120);
    if (!name || !guess) return json({ ok: false, error: 'Please fill in both fields.' });

    const sheet = getSheet();
    const now = new Date();
    // Received time is stamped here, on Google's side, so "fastest" is fair.
    sheet.appendRow([
      Utilities.formatDate(now, TIMEZONE, 'yyyy-MM-dd HH:mm:ss.SSS'),
      name,
      guess,
    ]);
    return json({ ok: true, at: now.toISOString() });
  } catch (err) {
    return json({ ok: false, error: 'Could not save your guess. Try again.' });
  } finally {
    lock.releaseLock();
  }
}

// Visiting the web-app URL in a browser shows this — handy to check the deployment works.
function doGet() {
  return json({ ok: true, message: 'Guess endpoint is live.' });
}

function getSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(['Received (IST)', 'Name', 'Guess']);
    sheet.setFrozenRows(1);
    sheet.getRange('A1:C1').setFontWeight('bold');
  }
  return sheet;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
