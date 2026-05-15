function jsonResponse(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function getSheetByName_(name) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(name);
  if (!sheet) {
    throw new Error("Worksheet not found: " + name);
  }
  return sheet;
}

function readSheet_(worksheet) {
  var sheet = getSheetByName_(worksheet);
  var values = sheet.getDataRange().getValues();
  if (values.length === 0) {
    return [];
  }

  var headers = values[0];
  var rows = [];
  for (var i = 1; i < values.length; i++) {
    var row = {};
    for (var j = 0; j < headers.length; j++) {
      row[headers[j]] = values[i][j];
    }
    rows.push(row);
  }
  return rows;
}

function writeSheet_(worksheet, rows) {
  var sheet = getSheetByName_(worksheet);
  sheet.clearContents();

  if (!rows || rows.length === 0) {
    return;
  }

  var headers = Object.keys(rows[0]);
  var values = [headers];

  for (var i = 0; i < rows.length; i++) {
    var rowValues = [];
    for (var j = 0; j < headers.length; j++) {
      rowValues.push(rows[i][headers[j]] || "");
    }
    values.push(rowValues);
  }

  sheet.getRange(1, 1, values.length, headers.length).setValues(values);
}

function doGet(e) {
  try {
    var action = e.parameter.action || "read";
    var worksheet = e.parameter.worksheet;

    if (action !== "read") {
      return jsonResponse({ status: "error", message: "Unsupported GET action" });
    }

    return jsonResponse({ status: "ok", rows: readSheet_(worksheet) });
  } catch (error) {
    return jsonResponse({ status: "error", message: String(error) });
  }
}

function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents || "{}");
    if (payload.action !== "write") {
      return jsonResponse({ status: "error", message: "Unsupported POST action" });
    }

    writeSheet_(payload.worksheet, payload.rows || []);
    return jsonResponse({ status: "ok" });
  } catch (error) {
    return jsonResponse({ status: "error", message: String(error) });
  }
}
