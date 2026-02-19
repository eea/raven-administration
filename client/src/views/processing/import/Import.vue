<script setup>
import { ref } from "vue";
import CommonLayout from "../../../components/CommonLayout.vue";
import ToolBar from "../../../components/ToolBar.vue";
import Container from "../../../components/Container.vue";
import Service from "./service";
import Eventy from "../../../helpers/eventy";

const file = ref(null);

const onUpload = async () => {
  Eventy.showMessage("Uploading file, Please wait!", "loading");
  let formData = new FormData();
  formData.append("file", file.value.files[0]);
  await Service.upload(formData);
  file.value.value = null;
  Eventy.showHideMessage("Upload successful");
};
</script>

<template>
  <common-layout>
    <tool-bar title="Manual limport" :show-add="false" :show-download="false" :show-filter="false" />
    <container class="flex gap-4">
      <container class="bg-nord7/20! mt-2 flex gap-1">
        <div class="font-bold text-base">The csv file must contain the following headers:</div>
        <div class="text-sm">
          <table class="">
            <tr>
              <td class="font-bold align-top">sampling_point_id</td>
              <td class="pl-4">
                A valid reference to a
                <a href="/management/samplingpoints">sampling_point_id</a>
              </td>
            </tr>
            <tr>
              <td class="font-bold align-top">begin_position</td>
              <td class="pl-4">ISO 8601 date standard with format: 2001-01-01T00:00:00+01:00</td>
            </tr>
            <tr>
              <td class="font-bold align-top">end_position</td>
              <td class="pl-4">ISO 8601 date standard with format: 2001-01-01T00:00:00+01:00</td>
            </tr>
            <tr>
              <td class="font-bold align-top">value</td>
              <td class="pl-4">The measured value</td>
            </tr>
            <tr>
              <td class="font-bold align-top">validation_flag</td>
              <td class="pl-4">
                An integer verification flag.
                <a href="http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity">Read more about validation levels here</a>
              </td>
            </tr>
            <tr>
              <td class="font-bold align-top">verification_flag</td>
              <td class="pl-4">
                An integer validation flag.
                <a href="http://dd.eionet.europa.eu/vocabulary/aq/observationverification">Read more about verification levels here</a>
              </td>
            </tr>
          </table>
        </div>
      </container>
      <div class="flex gap-2">
        <input type="file" ref="file" class="input" />
        <button class="button" @click="onUpload()">Upload</button>
      </div>
    </container>
  </common-layout>
</template>
