<template>
    <div class="fixed inset-0 bg-gradient-to-br from-indigo-300 flex items-center justify-center overflow-hidden">
        <!-- Login Window -->
        <div class="bg-white bg-opacity-90 rounded-lg shadow-lg p-8 w-96 max-w-full">
            <!-- Login 標題置中 -->
            <h2 class="text-2xl font-semibold mb-6 text-center text-gray-800">
                Login
            </h2>
            <form @submit.prevent="handleLogin" class="space-y-5">
                <div>
                    <label for="account" class="block text-gray-700 mb-2 text-left font-medium">Account</label>
                    <input id="account" type="text" v-model="account" required placeholder="Enter your account"
                        class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                    <label for="password" class="block text-gray-700 mb-2 text-left font-medium">Password</label>
                    <input id="password" type="password" v-model="password" required placeholder="Enter your password"
                        class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 transition">
                    Login
                </button>
            </form>
        </div>
    </div>
</template>
  
<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const account = ref("");
const password = ref("");
const router = useRouter();

function handleLogin() {
    if (account.value === "user" && password.value === "$1234") {
        localStorage.setItem("auth", "true");
        router.push({ name: "chat" });
    } else {
        alert("Invalid credentials");
    }
}
</script>