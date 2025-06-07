<template>
  <div class="chat-container" ref="chatContainer">
    <div
      v-for="(msg, index) in messages"
      :key="index"
      :class="['message', msg.role]"
    >
      <p><strong>{{ msg.role === 'user' ? '你' : 'Agent' }}：</strong>{{ msg.content }}</p>
    </div>
  </div>

  <div class="input-area">
    <input
      v-model="newMessage"
      @keyup.enter="sendMessage"
      placeholder="輸入訊息..."
    />
    <button @click="sendMessage">送出</button>
  </div>
</template>

<script>
export default {
  name: 'TestChatBot',
  data() {
    return {
      messages: [],
      newMessage: ''
    };
  },
  methods: {
    async sendMessage() {
      const message = this.newMessage.trim();
      if (!message) return;

      // 加入使用者訊息
      this.messages.push({ role: 'user', content: message });
      this.newMessage = '';

      // 滾到底部
      this.$nextTick(() => {
        this.$refs.chatContainer.scrollTop = this.$refs.chatContainer.scrollHeight;
      });

      try {
        const res = await fetch('http://127.0.0.1:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: message,
            history: this.messages
          })
        });

        const data = await res.json();

        // 檢查回傳是否含有 reply
        if (data) {
          this.messages.push({ role: 'assistant', content: data.response });
        } else {
          this.messages.push({ role: 'assistant', content: '⚠️ 沒有收到有效的回應。' });
        }

        // 滾到底部
        this.$nextTick(() => {
          this.$refs.chatContainer.scrollTop = this.$refs.chatContainer.scrollHeight;
        });
      } catch (error) {
        console.error('Error:', error);
        this.messages.push({ role: 'assistant', content: '❌ 發送訊息時發生錯誤。' });
      }
    }
  }
};
</script>

<style scoped>
.chat-container {
  height: 400px;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: 8px;
  max-width: 60%;
  word-wrap: break-word;
}

.user {
  text-align: right;
  background-color: #dcf8c6;
  margin-left: auto;
}

.assistant {
  text-align: left;
  background-color: #fff;
  margin-right: auto;
}

.input-area {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

input {
  flex: 1;
  padding: 0.5rem;
  font-size: 1rem;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
