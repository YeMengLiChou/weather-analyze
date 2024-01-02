<template>
    <el-container>
        <el-header>
            <h1>{{ data.city_name }}</h1>
        </el-header>
        <el-main>
            <el-descriptions class="margin-top" title="当前天气数据" :column="2" border>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item">
                            <span style="font-size: 600;">城市</span>
                        </div>
                    </template>
                    {{ data.city_name }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item">
                            <span style="font-size: 600;">所属省/市</span>
                        </div>
                    </template>
                    {{ data.city_province }}
                </el-descriptions-item>
                <el-descriptions-item :span="2">
                    <template #label>
                        <div class="cell-item">
                            <span style="font-size: 600;">当前温度</span>
                        </div>
                    </template>
                    {{ data.temp }} ℃
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item">
                            <span style="font-size: 600;">日间温度</span>
                        </div>
                    </template>
                    {{ data.d_temp }} ℃
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item">
                            <span style="font-size: 600;">夜间温度</span>
                        </div>
                    </template>
                    {{ data.n_temp }} ℃
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item">
                            <span style="font-size: 600;">湿度</span>
                        </div>
                    </template>
                    {{ data.humidity }}%
                </el-descriptions-item>
                <el-descriptions-item :span="2">
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">风向</span>
                        </div>
                    </template>
                    {{ info.w_direction }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">风级</span>
                        </div>
                    </template>
                    {{ info.w_level }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">风速</span>
                        </div>
                    </template>
                    {{ data.w_speed }} km/h
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">天气</span>
                        </div>
                    </template>
                    {{ data.description }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">降雨量</span>
                        </div>
                    </template>
                    {{ info.rain}}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">24h降水量</span>
                        </div>
                    </template>
                    {{ info.rain24h }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">日出时间</span>
                        </div>
                    </template>
                    {{ info.sunrise }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">日落时间</span>
                        </div>
                    </template>
                    {{ info.sunset }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <div class="cell-item" >
                            <span style="font-size: 600;">数据更新时间</span>
                        </div>
                    </template>
                    {{ info.update }}
                </el-descriptions-item>
            </el-descriptions>
        </el-main>
    </el-container>
</template>


<script setup>

import api from '@/api/api';
import { ref, onMounted, computed, defineProps, watch } from 'vue';
import { useRoute } from 'vue-router';
import { _} from 'lodash'
import { useCityInfoStore } from '@/stores/CityInfo';

const route = useRoute()
const data = ref({})
const store = useCityInfoStore()

const info = computed(() => {
    if (data.value) {
        const cal = (x) => {
            if (x - 0.0 <= 1e-5) {
                return '无降水'
            } else {
                x
            }
        }
        const calWD = (y) => {
            if (!y) return 
            let res = ""
            for (let i = 0; i < y.length; i ++ ) {
                if (y[i] == 'E') res += '东';
                if (y[i] == 'W') res += '西';
                if (y[i] == 'N') res += '北';
                if (y[i] == 'S') res += '南';
            }
            return res + '风'    
        }
        const calWL = (y) => {
            if (!y) return 
            if (y === 0) {
                return '微风'
            } else {
                return y + '级'
            }
        }
        return {
            w_direction: calWD(data.value.w_direction),
            w_level: calWL( data.value.w_level),
            update: data.value.timestamp,
            sunset: data.value.sunrise,
            sunrise: data.value.sunrise,
            rain: cal(data.value.rain),
            rain24h: cal(data.value.rain24h),            
        }
    } else {
        return {}
    }
})

onMounted(() => {
    api.getRealDataByCityId(route.query.id)
    .then(res => {
        data.value = res
    })
})


</script>


<style></style>