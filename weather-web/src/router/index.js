import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "home",
            component: () => import("@/views/home/Home.vue"),
        },
        {
            path: "/details/",
            name: "about",
            component: () => import("@/views/detail/Details.vue"),
            children: [],
        },
    ],
});

export default router;
