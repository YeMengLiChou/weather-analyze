<template>
    <el-container>
        <el-aside>
            <el-menu active-text-color="#ffd04b"
                     background-color="#545c64"
                     class="el-menu-vertical-demo"
                     default-active="real"
                     text-color="#fff"
                     @select="handle">
                <el-menu-item index="real" >
                    <el-icon><Location /></el-icon>
                    <span>实时</span>
                </el-menu-item>
                <el-menu-item index="history">
                    <el-icon>
                        <document />
                    </el-icon>
                    <span>历史</span>
                </el-menu-item>
                <el-menu-item index="analyze">
                    <el-icon>
                        <setting />
                    </el-icon>
                    <span>数据分析</span>
                </el-menu-item>
            </el-menu>
        </el-aside>
        <el-main>
            <RouterView/>
        </el-main>
    </el-container>
</template>

<script setup>
import {ref, computed, onMounted} from 'vue';
import { useCityInfoStore } from '@/stores/CityInfo';
import { useRouter, useRoute } from 'vue-router';

const store = useCityInfoStore()
const router = useRouter()
const route = useRoute()

const id = ref(0)
const actived = computed(() => {
    // 通过路由计算当前的菜单项
    const paths = route.path.split('/');
    return paths[paths.length - 1]
})

onMounted(() => {
    console.log(route.query.id)
    id.value = route.query.id
    store.updateId(id.value)
    console.log(store.$state.id)
})

const handle = (value) => {
    if (value != actived.value) {
        router.push({
            name: 'd-' + value,
            query: {
                id: id.value
            }
        })
    }
}

</script>


<style>
.el-menu {
    height: 100%;
    justify-content: center;
}
.el-main {
    background-color: white;
}
</style>