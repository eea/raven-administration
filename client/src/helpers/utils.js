export const groupBy = (arr, keyGetter) => {
  const map = new Map();
  arr.forEach((item) => {
    const key = keyGetter(item);
    const collection = map.get(key);
    if (!collection) {
      map.set(key, [item]);
    } else {
      collection.push(item);
    }
  });
  return Array.from(map);
};

export const sortBy = (arr, props) => {
  const fieldSorter = (fields) => (a, b) =>
    fields
      .map((o) => {
        let dir = 1;
        if (o[0] === "-") {
          dir = -1;
          o = o.substring(1);
        }
        return a[o] > b[o] ? dir : a[o] < b[o] ? -dir : 0;
      })
      .reduce((p, n) => (p ? p : n), 0);
  return arr.sort(fieldSorter(props));
};

export const tblToCsv = (id, name, separator = ",") => {
  // Select rows from id
  var rows = document.querySelectorAll("table#" + id + " tr");
  // Construct csv
  var csv = [];
  for (var i = 0; i < rows.length; i++) {
    var row = [],
      cols = rows[i].querySelectorAll("td, th");
    for (var j = 0; j < cols.length; j++) {
      // Clean innertext to remove multiple spaces and jumpline (break csv)
      var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, "").replace(/(\s\s)/gm, " ");
      data = data.replace(/"/g, '""');

      if (cols[j].childElementCount > 0 && cols[j].firstChild?.classList.contains("n-checkbox")) {
        data = "'" + cols[j].firstChild?.classList.contains("n-checkbox-checked") + "'";
      }

      // Push escaped string
      row.push('"' + data + '"');
    }
    csv.push(row.join(separator));
  }
  var csv_string = csv.join("\n");
  // Download it
  var filename = name + ".csv";
  var link = document.createElement("a");
  link.style.display = "none";
  link.setAttribute("target", "_blank");
  link.setAttribute("href", "data:text/csv;charset=utf-8," + encodeURIComponent(csv_string));
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const compare = (object1, object2) => {
  if (!object1 || !object2) return false;
  const keys1 = Object.keys(object1);
  const keys2 = Object.keys(object2);
  if (keys1.length !== keys2.length) {
    return false;
  }
  for (let key of keys1) {
    if (object1[key] !== object2[key]) {
      return false;
    }
  }
  return true;
};

export const month = (monthAsInt) => {
  if (monthAsInt == 1) return "January";
  if (monthAsInt == 2) return "February";
  if (monthAsInt == 3) return "March";
  if (monthAsInt == 4) return "April";
  if (monthAsInt == 5) return "May";
  if (monthAsInt == 6) return "June";
  if (monthAsInt == 7) return "July";
  if (monthAsInt == 8) return "August";
  if (monthAsInt == 9) return "September";
  if (monthAsInt == 10) return "October";
  if (monthAsInt == 11) return "November";
  if (monthAsInt == 12) return "December";
  return "Unknown";
};

export const filterList = (q, list, exclude_list) => {
  if (!q) return list;
  return list.filter((row) => {
    // dont search on excluded properties
    var props = Object.entries(row);
    if (exclude_list) props = props.filter((p) => !exclude_list.includes(p[0]));

    const showValues = Object.values(Object.fromEntries(props)).some((p) => String(p).toLowerCase().includes(q.toLowerCase()));

    return showValues;
  });
};

export const version = "3.0.4";
