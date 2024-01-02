import { defineStore } from "pinia";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ref } from "vue";
import msg from '@/utils/message'


/**
 * 存储用户信息
 */
export const useCityInfoStore = defineStore("city-info", () => {
    // 路由
    const router = useRouter();
    
    const id = ref(0)

    const updateId = (_id) => {
        id.value = _id
    }
    return {
        id, updateId
    }
}, {
    persistent: true
});
