import { ref, computed } from 'vue';
import sortOn from 'sort-on';

export default function useSortable(list, prop, asc = true) {
  const sortProp = ref(prop);
  const ascending = ref(asc);

  const onSort = (prop) => {
    if (sortProp.value == prop) ascending.value = !ascending.value;
    else ascending.value = true;
    sortProp.value = prop;
  };

  const sortedList = computed(() => {
    if (!list.value) return [];
    if (!sortProp.value) return list.value;
    //return list.value.sort(sortByProperty(sortProp.value, ascending.value ? "desc" : "asc"));
    return sortOn(list.value, ascending.value ? sortProp.value : '-'.concat(sortProp.value));
  });

  return {
    onSort,
    ascending,
    sortProp,
    sortedList
  };
}
