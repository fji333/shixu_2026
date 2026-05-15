import { createRouter, createWebHistory } from "vue-router";

import Chat from "../pages/Chat.vue";
import Dashboard from "../pages/Dashboard.vue";
import Home from "../pages/Home.vue";
import Knowledge from "../pages/Knowledge.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: Home,
  },
  {
    path: "/chat",
    name: "chat",
    component: Chat,
  },
  {
    path: "/knowledge",
    name: "knowledge",
    component: Knowledge,
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: Dashboard,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
