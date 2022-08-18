<script>
export default {
  name: "event-listener",
  emits: ["slot-click", "slot-contextmenu"],
  render() {
    return this.$slots.default ? this.$slots.default() : "";
  },
};
</script>
