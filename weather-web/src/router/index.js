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
    ],
});

export default router;
