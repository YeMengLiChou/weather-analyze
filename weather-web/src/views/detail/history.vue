<template>
    <el-container>
        <el-header>
            <el-tag size="large">
                {{ city_name }}
            </el-tag>
                <el-select v-model="year" placeholder="年">
                    <el-option v-for="item in yearOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>

                <el-select v-model="month" placeholder="月">
                    <el-option v-for="item in monthOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
                <el-button @click="handleClick">
                    确定
                </el-button>
        </el-header>
        <el-main>

            <Chart :chartData="data" />
        </el-main>
    </el-container>
</template>

<script setup>
import api from '@/api/api';
import { ref, onMounted, computed, defineProps, watch } from 'vue';
import Chart from '@/views/detail/Chart.vue';
import { useRoute } from 'vue-router';
import { _ } from 'lodash'

const year = ref('2023')
const month = ref('12')
const yearOptions = []
const monthOptions = []
const route = useRoute()
const data = ref([])
const city_name = ref('')
onMounted(() => {
    for (let i = 2019; i < 2024; i++) {
        yearOptions.push({
            value: i,
            label: i,
        })
    }
    for (let i = 1; i < 13; i++) {
        monthOptions.push({
            value: i,
            label: i,
        })
    }
    api.getHistoryDataByCityId(route.query.id, year.value, month.value)
            .then(res => {
                data.value = res
            })
})

const handleClick = () => {
    if (year.value && month.value) {
        api.getHistoryDataByCityId(route.query.id, year.value, month.value)
            .then(res => {
                data.value = res
            })

    }
}


onMounted(() => {
    api.getCityNameById(route.query.id)
    .then(res => {
        city_name.value = res
    })
})


</script>

<style scoped>
.el-header {
    display: flex;
    justify-content: center;
}

.el-select {
    margin: 0 16px
}

</style>