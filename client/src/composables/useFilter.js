import { ref, computed } from "vue";
import { filterList } from "../helpers/utils/";

export default function useFilter(list) {
  const q = ref("");
  const filteredList = computed(() => {
    return filterList(q.value, list.value);
  });

  return {
    q,
    filteredList
  };
}
