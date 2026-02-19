const pageOptions = (lookups) => ({
  entityName: "User",
  csvName: "users",
  showRequiredAndoptionalSideBySideInCrud: false,
  properties: [
    { type: "gridOnly", label: "Id", prop: "id", showInGrid: true, val_func: (row) => row.id, width: 80 },
    { type: "text", label: "Name", prop: "name", required: true, default: "", showInGrid: true, flex: 1 },
    { type: "text", label: "Username", prop: "username", required: true, default: "", showInGrid: true, flex: 1 },
    { type: "gridOnly", label: "Created by", prop: "createdby", showInGrid: true, val_func: (row) => row.createdby, width: 150 },
    { type: "gridOnly", label: "Created", prop: "created", showInGrid: true, val_func: (row) => row.created, width: 180 },
    { type: "gridOnly", label: "Groups", prop: "group_labels", showInGrid: true, val_func: (row) => row.group_labels, flex: 1 }
  ],
  lookups: lookups
});

export default pageOptions;
