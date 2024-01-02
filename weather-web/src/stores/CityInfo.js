import { defineStore } from "pinia";
import userApi from '@/api/user';
import auth from "@/utils/authorization";
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
    


}, {
    persistent: true
});
