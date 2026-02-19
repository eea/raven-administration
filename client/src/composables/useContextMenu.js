import { ref } from 'vue';
import { compare } from '../helpers/utils';

export default function useContextMenu() {
  const selected = ref({});
  const ev = ref({});
  const showContextMenu = ref(false);

  const onContextMenu = (row, e) => {
    selected.value = row;
    ev.value = e;
    showContextMenu.value = true;
  };

  const clearContextMenu = () => {
    showContextMenu.value = false;
    // selected.value = {};
    ev.value = {};
  };

  const selectedClass = (row) => {
    var classes = '';
    if (compare(selected.value, row)) classes = classes + ' selected';
    return classes;
  };

  return {
    selectedClass,
    selected,
    ev,
    showContextMenu,
    onContextMenu,
    clearContextMenu
  };
}
