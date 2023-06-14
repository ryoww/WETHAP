import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import API from '../views/API.vue'

const router = createRouter({
    history: createWebHistory("/WETHAP"),
    routes: [
        {
            path: '/',
            component: Home
        },
        {
            path: '/about',
            component: About
        },
        {
            path: '/api',
            component: API
        }
    ]
})

export default router