import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../views/loginPage.vue";
import ChatPage from "../views/chatPage.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginPage,
  },
  {
    path: "/chat",
    name: "chat",
    component: ChatPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem("auth") === "true";
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: "login" });
  } else if (to.name === "login" && isLoggedIn) {
    next({ name: "chat" });
  } else {
    next();
  }
});

export default router;
