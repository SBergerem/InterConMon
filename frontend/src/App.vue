<script setup lang="ts">
import { ref, onMounted } from "vue";

type ApiStatusResponse = {
  status: string;
  app: string;
};

const data = ref<ApiStatusResponse | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);

async function getData(url: string) {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      errorMessage.value = `Request failed with status ${response.status}`;
      return;
    }

    const json: ApiStatusResponse = await response.json();
    data.value = json;
  } catch (error) {
    errorMessage.value = String(error);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  getData("http://127.0.0.1:8000/api/health");
});
</script>

<template>
  <p>TEST</p>

  <p v-if="isLoading">Loading...</p>

  <p v-else-if="errorMessage">Error {{ errorMessage }}</p>

  <div v-else-if="data">
    <p>Status: {{ data.status }}</p>
    <p>App: {{ data.app }}</p>
  </div>

  <p v-else>No data loaded</p>
</template>
<style scoped></style>
