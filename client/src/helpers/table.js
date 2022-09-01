import { compare } from "./utils";

export const multiRowClick = (model, row, rows, shiftKey, ctrlKey, rightClick, isSelected) => {
  var arr = model.map((o) => Object.assign({}, o));

  if (rightClick && isSelected) return arr;
  else if (!shiftKey && !ctrlKey && isSelected) return [];
  else if (!shiftKey && !ctrlKey) return [row];
  else {
    if (shiftKey) {
      var selectedRows = [];
      var last = rows.findIndex((o) => compare(model[model.length - 1], o));
      var current = rows.findIndex((o) => compare(row, o));

      var selectedRows = rows.slice(Math.min(last, current), Math.max(last, current) + 1);
      var all = arr.concat(selectedRows);
      // Show only one if duplicate
      all = all.filter((value, index, self) => index == self.findIndex((o) => compare(o, value)));
      return all;
    } else if (ctrlKey) {
      var arr2 = [];
      var found = false;
      arr.forEach((o) => {
        var isSame = compare(row, o);
        if (!isSame) arr2.push(o);
        if (!found && isSame) found = true;
      });

      if (!found) arr2.push(row);
      return arr2;
    }
  }
};
