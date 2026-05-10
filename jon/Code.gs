const SOURCE_SHEET_NAME = 'PivotGrid';
const TARGET_SHEET_NAME = 'PivotGrid_Cleaned';
const HEADER_ROWS = 4; // Endre hvis arket ditt har et annet antall header-rader.

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('PivotGrid')
    .addItem('Rens data', 'cleanPivotGrid')
    .addToUi();
}

function cleanPivotGrid() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheet = spreadsheet.getSheetByName(SOURCE_SHEET_NAME);

  if (!sourceSheet) {
    throw new Error(`Fant ikke arket "${SOURCE_SHEET_NAME}".`);
  }

  const data = sourceSheet.getDataRange().getValues();
  if (data.length === 0) {
    throw new Error(`Arket "${SOURCE_SHEET_NAME}" er tomt.`);
  }

  const cleaned = forwardFillPivotGrid(data, HEADER_ROWS, [0, 1, 2]);
  const targetSheet =
    spreadsheet.getSheetByName(TARGET_SHEET_NAME) || spreadsheet.insertSheet(TARGET_SHEET_NAME);

  targetSheet.clearContents();
  targetSheet
    .getRange(1, 1, cleaned.length, cleaned[0].length)
    .setValues(cleaned);

  SpreadsheetApp.getUi().alert(
    `Renset data skrevet til arket "${TARGET_SHEET_NAME}".`
  );
}

function forwardFillPivotGrid(data, headerRows, fillColumnIndexes) {
  const result = data.map((row) => row.slice());
  const lastSeen = {};

  for (let rowIndex = headerRows; rowIndex < result.length; rowIndex += 1) {
    for (let i = 0; i < fillColumnIndexes.length; i += 1) {
      const columnIndex = fillColumnIndexes[i];
      const value = result[rowIndex][columnIndex];

      if (isBlank(value)) {
        if (lastSeen[columnIndex] !== undefined) {
          result[rowIndex][columnIndex] = lastSeen[columnIndex];
        }
      } else {
        lastSeen[columnIndex] = value;
      }
    }
  }

  return result;
}

function isBlank(value) {
  return value === '' || value === null;
}
