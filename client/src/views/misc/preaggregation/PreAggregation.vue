<script setup>
import Service from "./service";
import Eventy from "../../../helpers/eventy";

const data = ref([]);

onMounted(async () => {
  await loadData();
});

const loadData = async () => {
  data.value = await Service.get();
};

const update = async () => {
  Eventy.showMessage("Aggregating data. Please wait", "loading");
  await Service.update();
  await loadData();
  Eventy.hideMessage();
};
</script>

<template>
  <common-layout>
    <tool-bar title="Pre aggregation" :show-column-picker="false" :show-add="false" :show-download="false" :show-filter="false" />

    <container>
      <div class="font-bold">Pre aggregating the data may take a while, depending on the amount of data stored in the database</div>
      <div><button class="n-button" @click="update">Manually aggregate data</button></div>
    </container>
    <div class="mt-4">
      <table id="preaggId" class="n-table">
        <tr>
          <th>Aggregation type</th>
          <th>Values count</th>
          <th>Samplingpoints count</th>
          <th>Average coverage</th>
          <!-- <th>First date</th> -->
          <th>Last date</th>
          <th>Last updated</th>
        </tr>
        <tr v-for="row in data">
          <td>{{ row.type }}</td>
          <td>{{ row.count_val }}</td>
          <td>{{ row.count_sp }}</td>
          <td>{{ row.avg_cov ? row.avg_cov + "%" : "-" }}</td>
          <!-- <td>{{ row.first_time }}</td> -->
          <td>{{ row.last_time ? row.last_time : "-" }}</td>
          <td class="font-bold">{{ row.created ? row.created : "-" }}</td>
        </tr>
      </table>
    </div>
  </common-layout>
</template>
