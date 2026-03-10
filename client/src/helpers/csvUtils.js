/**
 * CSV utility functions for clipboard operations
 */

/**
 * Escape a value for CSV format
 * @param {*} value - The value to escape
 * @returns {string} CSV-safe string
 */
function escapeCsvValue(value) {
  if (value === null || value === undefined) return '';

  const str = String(value);

  // If contains comma, newline, or quote, wrap in quotes and escape existing quotes
  if (str.includes(',') || str.includes('\n') || str.includes('\r') || str.includes('"')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }

  return str;
}

/**
 * Convert array of row objects to CSV string
 * @param {Array} rows - Array of row data objects
 * @param {Array} columns - Array of column definitions with 'field' or 'colId' property
 * @returns {string} CSV formatted string (data rows only, no header)
 */
export function rowsToCsv(rows, columns) {
  if (!rows || rows.length === 0) return '';
  if (!columns || columns.length === 0) return '';

  // Extract field names from column definitions
  const fields = columns
    .filter(col => col.field || col.colId)
    .map(col => col.field || col.colId);

  if (fields.length === 0) return '';

  return rows.map(row => {
    return fields.map(field => {
      const value = row[field];
      return escapeCsvValue(value);
    }).join(',');
  }).join('\n');
}

/**
 * Convert column headers to CSV string
 * @param {Array} columns - Array of column definitions with 'headerName' and 'field' properties
 * @returns {string} CSV formatted header row
 */
export function columnHeadersToCsv(columns) {
  if (!columns || columns.length === 0) return '';

  const headers = columns
    .filter(col => col.field || col.colId)
    .map(col => col.headerName || col.field || col.colId);

  return headers.map(header => escapeCsvValue(header)).join(',');
}

/**
 * Copy text to clipboard with fallback for older browsers
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if successful
 */
export async function copyToClipboard(text) {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }

    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return true;
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
    return false;
  }
}
