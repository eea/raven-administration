import { ref, computed } from 'vue';

export default function useCrud(service, onCompleted, clearContextMenu) {
  const showCrud = ref(false);

  const toggleCrud = () => {
    showCrud.value = !showCrud.value;
    clearContextMenu();
  };
  const onInsert = (data) => {};
  const onUpdate = async (data) => {
    console.log('onUpdate', data);
    onCompleted();
  };
  const onDelete = (data) => {};

  return {
    showCrud,
    toggleCrud,
    onInsert,
    onUpdate,
    onDelete
  };
}
