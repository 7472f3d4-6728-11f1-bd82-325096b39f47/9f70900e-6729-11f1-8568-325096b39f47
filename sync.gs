/**
 * 進捗同期 Web App —— チャンク保存版（50,000字セル上限を撤廃）
 * ------------------------------------------------------------------
 * 旧コードは progress(JSON) を 1 セルに保存していたため、
 * Google スプレッドシートの「1セル=50,000字」上限に達すると（≈650〜720問）
 * 書き込みが静かに失敗し、それ以降の学習が同期されなくなっていた。
 *
 * 本コードは JSON を複数セルに分割（チャンク）して保存するため、
 * 事実上サイズ無制限（既定で最大約2MB）になる。
 *
 * API（クライアント muki/yuki/kobunshi と互換）:
 *   GET  ?userId=KEY              -> {"ok":true,"data":{...}}
 *   POST body={"userId","data"}   -> {"ok":true,"chunks":N}
 *
 * ★ 既存データとの互換は不要（最初から解き直す）方針のため、
 *   新しいシート "store_v4" に保存する。旧シート(a-mikan2 等)はそのまま残してOK（不要なら削除可）。
 */

var SHEET_NAME = 'store_v4';   // 進捗を保存する専用シート（自動作成）
var CHUNK      = 40000;        // 1セルあたり最大文字数（50000より安全側）
var MAX_COLS   = 50;           // 1ユーザーの最大チャンク数（≈ 2MB まで）

/** 保存用シートを取得（無ければ作成）。 */
function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  // ▼ もしこのスクリプトがスプレッドシートに紐づいていない（スタンドアロン）場合は
  //    下行のコメントを外し、スプレッドシートIDを入れてください。
  // if (!ss) ss = SpreadsheetApp.openById('★スプレッドシートIDをここに★');
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) { sh = ss.insertSheet(SHEET_NAME); sh.getRange(1, 1).setValue('userId'); }
  return sh;
}

/** userId の行番号を返す（無ければ -1）。 */
function findRow_(sh, userId) {
  var last = sh.getLastRow();
  if (last < 1) return -1;
  var ids = sh.getRange(1, 1, last, 1).getValues();
  for (var i = 0; i < ids.length; i++) { if (ids[i][0] === userId) return i + 1; }
  return -1;
}

/** userId の保存データ（分割セルを連結して JSON.parse）。 */
function readData_(userId) {
  var sh = getSheet_();
  var row = findRow_(sh, userId);
  if (row < 0) return {};
  var lastCol = sh.getLastColumn();
  if (lastCol < 2) return {};
  var cells = sh.getRange(row, 2, 1, lastCol - 1).getValues()[0];
  var s = cells.join('');
  if (!s) return {};
  try { return JSON.parse(s); } catch (e) { return {}; }
}

/** userId に保存データを分割して書き込む。 */
function writeData_(userId, dataObj) {
  var sh = getSheet_();
  var str = JSON.stringify(dataObj || {});
  var chunks = [];
  for (var i = 0; i < str.length; i += CHUNK) chunks.push(str.substring(i, i + CHUNK));
  if (chunks.length > MAX_COLS) throw new Error('data too large: ' + str.length + ' chars');

  var row = findRow_(sh, userId);
  if (row < 0) { row = Math.max(sh.getLastRow(), 1) + 1; sh.getRange(row, 1).setValue(userId); }

  // 旧チャンクを消してから新チャンクを書く（縮小時の取り残し防止）
  var lastCol = sh.getLastColumn();
  if (lastCol >= 2) sh.getRange(row, 2, 1, lastCol - 1).clearContent();
  if (chunks.length) sh.getRange(row, 2, 1, chunks.length).setValues([chunks]);
  return chunks.length;
}

/** JSON レスポンス（正しい MIME で返す＝クライアントが成否を判定できる）。 */
function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
                       .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  var lock = LockService.getScriptLock();
  try {
    var userId = (e && e.parameter && e.parameter.userId) || '';
    if (!userId) return json_({ ok: true, data: {} });
    lock.tryLock(20000);
    var data = readData_(userId);
    return json_({ ok: true, data: data });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (_) {}
  }
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    var body = JSON.parse(e.postData.contents);
    var userId = body.userId || '';
    if (!userId) return json_({ ok: false, error: 'no userId' });
    lock.tryLock(20000);
    var n = writeData_(userId, body.data);
    return json_({ ok: true, chunks: n });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (_) {}
  }
}
