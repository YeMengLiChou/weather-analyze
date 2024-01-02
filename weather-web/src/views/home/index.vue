<template>
    <el-container>
        <el-row>
            <el-col>
                <el-tag>
                    {{  }}
                </el-tag>
            </el-col>
        </el-row>
    </el-container>
</template>


<script setup>
import {ref, onMounted, computed} from 'vue';
import api from '@/api/api'
data = ref(null)

onMounted(() => {
    api.fetchAllCities()
    .then(res=> {

        data.value = res.items()
        console.log(res);
    })
})

</script>


<style>


</style>