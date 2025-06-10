<template>
  <div class="fixed inset-0 bg-gradient-to-br from-indigo-300 p-4">
    <header class="flex items-center justify-between">
      <button @click="toggleSidebar" class="z-50 p-2 bg-white rounded-md shadow-md focus:outline-none"
        aria-label="Toggle sidebar">
        <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
          stroke-linejoin="round" viewBox="0 0 24 24">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <div class="text-[40px] font-bold text-gray-800 select-none">
        ChatBot
      </div>

      <div class="relative" ref="dropdownRef">
        <button @click="toggleDropdown" class="flex items-center space-x-2 focus:outline-none">
          <img src="https://i.pravatar.cc/40" class="w-12 h-12 rounded-full border-2 border-white shadow" alt="Avatar" />
          <span class="text-blue text-[24px] font-bold">User</span>
        </button>

        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-full bg-white rounded-lg shadow-lg py-2 z-50">
          <button class="block w-full text-left px-4 py-2 text-lg hover:bg-gray-100" @click="goToSettings">
            Settings
          </button>
          <button class="block w-full text-left px-4 py-2 text-lg hover:bg-gray-100" @click="handleLogout">
            Logout
          </button>
        </div>
      </div>
    </header>

    <main class="flex-1 flex flex-col justify-between items-center px-4 pt-10 pb-4">
      <div class="w-full max-w-4xl flex flex-col space-y-4">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="[
            'rounded-lg p-4 max-w-lg w-full whitespace-pre-wrap',
            msg.role === 'user'
              ? 'self-end bg-indigo-400 text-white text-left'
              : 'self-start bg-gray-200 text-gray-800 text-left'
          ]"
        >
          <strong>{{ msg.role === 'user' ? '你' : 'Agent' }}：</strong>
          {{ msg.content }}
        </div>
      </div>

      <div class="w-full max-w-4xl mt-6 fixed bottom-10">
        <div class="flex items-center bg-white rounded-full shadow px-4 py-2 space-x-2">
          <button class="text-gray-500 hover:text-indigo-600 focus:outline-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.75 3v3.75M9.75 3a6.75 6.75 0 100 13.5H21M21 3v3.75M21 3a6.75 6.75 0 01-13.5 0H3" />
            </svg>
          </button>

          <input
          v-model="messageInput"
          @keyup.enter="sendMessage"
          placeholder="輸入訊息..."
          class="flex-1 bg-transparent focus:outline-none text-lg"
        />
          <button @click="sendMessage"
            class="text-white bg-indigo-500 hover:bg-indigo-600 px-4 py-2 rounded-full text-sm font-semibold disabled:opacity-50">
            {{ canSend ? '送出' : `${cooldown} 秒...` }}
          </button>
        </div>
      </div>
    </main>

    <transition name="slide">
      <aside v-if="sidebarOpen" class="fixed top-0 left-0 h-full w-64 bg-white shadow-lg p-6 z-40">
        <div class="h-16"></div>
        <nav>
          <ul>
            <li class="mb-3"><a href="#" class="text-gray-800 hover:text-indigo-600">Dashboard</a></li>
            <li class="mb-3"><a href="#" class="text-gray-800 hover:text-indigo-600">Profile</a></li>
            <li class="mb-3"><a href="#" class="text-gray-800 hover:text-indigo-600">Settings</a></li>
          </ul>
        </nav>
      </aside>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const dropdownOpen = ref(false);
const sidebarOpen = ref(false);
const dropdownRef = ref(null);

const messages = ref([]);
const messageInput = ref('');
const canSend = ref(true);
const cooldown = ref(0);
let cooldownTimer = null;
const chatContainer = ref(null);

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}
function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}
function handleLogout() {
  localStorage.removeItem("auth");
  router.push({ name: "login" });
}
function goToSettings() {
  alert("Go to settings");
  dropdownOpen.value = false;
}
function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
  if (cooldownTimer) clearInterval(cooldownTimer);
});

// ✅ 傳送訊息
async function sendMessage() {
  const message = messageInput.value.trim();
  if (!message || !canSend.value) return;

  canSend.value = false;
  cooldown.value = 30;

  cooldownTimer = setInterval(() => {
    cooldown.value--;
    if (cooldown.value <= 0) {
      clearInterval(cooldownTimer);
      canSend.value = true;
    }
  }, 1000);

  messages.value.push({ role: 'user', content: message });
  messageInput.value = '';

  await nextTick();
  scrollToBottom();

  try {
    const res = await fetch('http://127.0.0.1:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: message,
        history: messages.value
      })
    });

    const data = await res.json();

    if (data) {
      // messages.value.push({ role: 'assistant', content: data.user_summary });
      // messages.value.push({ role: 'assistant', content: data.ai_summary });
      messages.value.push({ role: 'assistant', content: data.response });
    } else {
      messages.value.push({ role: 'assistant', content: '⚠️ 沒有收到有效的回應。' });
    }
  } catch (error) {
    console.error('Error:', error);
    messages.value.push({ role: 'assistant', content: '❌ 發送訊息時發生錯誤。' });
  }

  await nextTick();
  scrollToBottom();
}

function scrollToBottom() {
  const el = chatContainer.value;
  if (el) {
    el.scrollTop = el.scrollHeight;
  }
}
</script>


<style>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
