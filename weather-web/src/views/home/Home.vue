<template>
    <el-container>
        <RouterView ></RouterView>
    </el-container>
</template>

<script setup>
import {ref, onMounted} from 'vue';

onMounted(() => {
    console.log('Home.vue onMounted');
});

</script>


<style scoped>
el-container {
    background-color: white;
}

el-row {
    height: 100%;
}</style>