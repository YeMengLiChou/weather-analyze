<template>
  <el-container>
    <el-header>
      <h2>省会数据</h2>
    </el-header>
    <el-main>
      <el-table :data="data" style="width: 80%" stripe border @row-click="navigate">
        <el-table-column prop="province" label="省份" />
        <el-table-column prop="city" label="省会" />
        <el-table-column prop="id" label="城市id" />
      </el-table>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/api/api";
import { useRouter } from "vue-router";
import { useCityInfoStore } from "@/stores/CityInfo";
let data = ref([]);
let router = useRouter()
const store = useCityInfoStore()
onMounted(() => {
  api.fetchAllCities().then((res) => {
    res.data.sort((a, b) => { return a.id - b.id; })
    data.value = res.data;
    console.log(res);
  });
});

function navigate(row) {
  router.push({
    name: 'd-real',
    query: {
      id: row.id
    }
  })
}

</script>

<style>
.el-container {
  background-color: white;
}

.el-header {
  display: flex;
  justify-content: center;
  padding: 16px 0 0 0;
}

.el-main {
  display: flex;
  justify-content: center;

}

.el-row {
  width: 100%;
  background-color: white;
  padding: 10px 0;
  justify-content: center;
}
</style>
