import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "home",
            redirect: 'index',
            component: () => import("@/views/home/Home.vue"),
            children: [
                {
                    path: 'index',
                    name: 'index',
                    components: () => import('@/views/home/index.vue')
                },
            ]
        },
        {
            path: '/details',
            name: 'details',
            component: () => import('@/views/detail/index.vue'),
            children: [
                {
                    path: 'real',
                    name: 'd-real',
                    component: () => import('@/views/detail/real.vue')
                },
                {
                    path: 'history',
                    name:'d-history',
                    component: () => import('@/views/detail/history.vue')
                }
            ]
        }
    ],
});

export default router;
