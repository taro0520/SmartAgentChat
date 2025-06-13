<template>
  <div class="fixed inset-0 bg-gradient-to-br from-indigo-300 p-4">
    <!-- Header bar -->
    <header class="flex items-center justify-between">
      <!-- Sidebar toggle button -->
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

      <!-- User dropdown -->
      <div class="relative" ref="dropdownRef">
        <button @click="toggleDropdown" class="flex items-center space-x-2 focus:outline-none">
          <img src="../assets/user.png" class="w-12 h-12 rounded-full border-1 border-white shadow" alt="Avatar" />
          <span class="text-blue text-[24px] font-bold">User</span>
        </button>

        <!-- Dropdown menu -->
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-full bg-white rounded-lg shadow-lg py-2 z-50">
          <button class="block w-full text-left px-4 py-2 text-lg hover:bg-gray-100" @click="handleLogout">
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Chat main content -->
    <main class="flex-1 flex flex-col justify-between items-center px-4 pt-10 pb-4">
      <div ref="messageContainer" class="w-full max-w-4xl flex flex-col space-y-4 overflow-y-auto flex-1 mb-28"
        style="max-height: calc(100vh - 250px);">
        <div v-for="(msg, index) in messages" :key="index" :class="[
          'max-w-4xl w-full whitespace-pre-wrap flex items-start space-x-2',
          msg.role === 'user' ? 'justify-end' : 'justify-start'
        ]">
          <!-- Bot avatar -->
          <img v-if="msg.role !== 'user'" src="../assets/bot.png" alt="Agent Avatar"
            class="w-12 h-12 rounded-full border-1 border-white shadow mr-1" />

          <!-- Message bubble -->
          <div :class="[
            'rounded-lg p-4 max-w-lg whitespace-pre-wrap',
            msg.role === 'user'
              ? 'bg-indigo-400 text-white text-left'
              : 'bg-gray-200 text-gray-800 text-left'
          ]">{{ msg.content }}</div>

          <!-- User avatar -->
          <img v-if="msg.role === 'user'" src="../assets/user.png" alt="User Avatar"
            class="w-12 h-12 rounded-full border-1 border-white shadow ml-2" />
        </div>
      </div>

      <!-- Message input area -->
      <div class="w-full max-w-4xl mt-6 fixed bottom-10">
        <div class="flex items-center bg-white rounded-full shadow px-4 py-2 space-x-2">
          <!-- PDF upload button -->
          <button class="text-gray-500 hover:text-indigo-600 focus:outline-none" @click="triggerFileSelect">
            <img src="../assets/pdf.png" class="h-6 w-6" alt="icon" />
          </button>

          <!-- Hidden file input -->
          <input type="file" ref="fileInput" class="hidden" accept="application/pdf" @change="uploadPDF" />

          <!-- Text input -->
          <input v-model="messageInput" @keyup.enter="sendMessage" placeholder="Input message..."
            class="flex-1 bg-transparent focus:outline-none text-lg" />

          <!-- Send button -->
          <button @click="sendMessage"
            class="text-white bg-indigo-500 hover:bg-indigo-600 px-4 py-2 rounded-full text-sm font-semibold disabled:opacity-50">
            {{ canSend ? 'Send' : `${cooldown} sec...` }}
          </button>
        </div>
      </div>
    </main>

    <!-- Sidebar with transition -->
    <transition name="slide">
      <aside v-if="sidebarOpen" class="fixed top-0 left-0 h-full w-64 bg-white shadow-lg p-6 z-40">
        <div class="h-16"></div>
        <nav>
          <ul>
            <li class="mb-3"><a href="#" class="text-gray-800 hover:text-indigo-600">Label1</a></li>
            <li class="mb-3"><a href="#" class="text-gray-800 hover:text-indigo-600">Label2</a></li>
            <li class="mb-3"><a href="#" class="text-gray-800 hover:text-indigo-600">Label3</a></li>
          </ul>
        </nav>
      </aside>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRouter } from "vue-router";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const router = useRouter();

const dropdownOpen = ref(false);
const sidebarOpen = ref(false);
const dropdownRef = ref(null);

const messages = ref([]);
const messageInput = ref('');
const canSend = ref(true);
const cooldown = ref(0);
let cooldownTimer = null;
const messageContainer = ref('');
const chatToken = ref("");

const fileInput = ref(null);

function triggerFileSelect() {
  if (fileInput.value) {
    fileInput.value.value = null;
    fileInput.value.click();
  }
}

// File upload logic
const uploadPDF = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("token", chatToken.value);

  try {
    const res = await fetch(`${API_BASE_URL}/chat/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    messages.value.push({ role: 'assistant', content: `Uploaded file success.` });
  } catch (err) {
    console.error("Upload failed", err);
    messages.value.push({ role: 'assistant', content: `❌ Upload failed.` });
  }
};

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

// Logout
async function handleLogout() {
  const savedToken = localStorage.getItem("chat_token");
  try {
    await fetch(`${API_BASE_URL}/chat/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: savedToken, query: "" }),
    });
  } catch (err) {
    console.error("Logout error", err);
  }

  localStorage.removeItem("chat_token");
  localStorage.removeItem("auth");
  router.push({ name: "login" });
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

// Token Generator
function generateRandomToken(length = 16) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Initialization
onMounted(() => {
  const savedToken = localStorage.getItem("chat_token");
  if (savedToken) {
    chatToken.value = savedToken;
  } else {
    const newToken = generateRandomToken();
    localStorage.setItem("chat_token", newToken);
    chatToken.value = newToken;
  }
  console.log(chatToken.value);
});

// Listen for clicks to close dropdown
onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
  if (cooldownTimer) clearInterval(cooldownTimer);
});

// Send Message to Backend
async function sendMessage() {
  const message = messageInput.value.trim();
  const token = localStorage.getItem("chat_token");

  if (!message || !canSend.value) return;

  canSend.value = false;
  cooldown.value = 10;

  cooldownTimer = setInterval(() => {
    cooldown.value--;
    if (cooldown.value <= 0) {
      clearInterval(cooldownTimer);
      canSend.value = true;
    }
  }, 1000);

  // Show user message
  messages.value.push({ role: 'user', content: message });
  messageInput.value = '';

  await nextTick();
  scrollToBottom();

  // Send to API
  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: token,
        query: message,
        history: messages.value
      })
    });

    const data = await res.json();

    if (data) {
      // messages.value.push({ role: 'assistant', content: data.user_summary });
      // messages.value.push({ role: 'assistant', content: data.ai_summary });
      // console.log({ content: data.ai_summary, content: data.user_summary,content: data.token });
      messages.value.push({ role: 'assistant', content: data.response });
    } else {
      messages.value.push({ role: 'assistant', content: '⚠️ No valid response received.' });
    }
  } catch (error) {
    console.error('Error:', error);
    messages.value.push({ role: 'assistant', content: '❌ Error occurred while sending the message.' });
  }

  await nextTick();
  scrollToBottom();
}

// Scroll to bottom after message
function scrollToBottom() {
  const el = messageContainer.value;
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
