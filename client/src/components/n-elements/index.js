import NInput from './NInput.vue'
import NSelect from './NSelect.vue'
import NOption from './NOption.vue'
import NDatetime from './NDatetime.vue'
import NMultiselect from './NMultiselect.vue'
import NTable from './NTable.vue'
import NRow from './NRow.vue'
import NButton from "./NButton.vue"
import NCheckbox from "./NCheckbox.vue"
import "./n-elements.css";
export { NInput, NSelect, NOption, NDatetime, NMultiselect, NTable, NRow, NButton, NCheckbox };

export const registerElements = (app) => {
  app.component("NInput", NInput);
  app.component("NSelect", NSelect);
  app.component("NOption", NOption);
  app.component("NDatetime", NDatetime);
  app.component("NMultiselect", NMultiselect);
  app.component("NTable", NTable);
  app.component("NRow", NRow);
  app.component("NButton", NButton);
  app.component("NCheckbox", NCheckbox);
};