<template>
  <div class="dashboard">

    <div class="welcome-card">
      <h1>
        Welcome {{ userInfo?.name }} {{ userInfo?.surname }}
      </h1>
      <p>Manage your indexes, embeddings and evaluations from one place.</p>
    </div>

    <div class="status-card">
      <h2>System Status</h2>

      <div class="status-item">
        <span
          class="status-dot"
          :class="userStore.hasEmbedKey ? 'green' : 'red'"
        ></span>

        <div>
          <strong>Embedding API Keys</strong>
          <p v-if="userStore.hasEmbedKey">
            Ready
          </p>
          <p v-else>
            Please insert one of the following keys:
            <b>Gemini, Jina or Cohere</b>.
          </p>
        </div>
      </div>

      <div class="status-item">
        <span
          class="status-dot"
          :class="userStore.hasLLmKey ? 'green' : 'red'"
        ></span>

        <div>
          <strong>LLM API Keys</strong>
          <p v-if="userStore.hasLLmKey">
            Ready
          </p>
          <p v-else>
            Please insert one of the following keys:
            <b>Gemini, Groq or Mistral</b>.
          </p>
        </div>
      </div>

      <div class="status-item">
        <span
          class="status-dot"
          :class="userStore.hasPineconeKey ? 'green' : 'red'"
        ></span>

        <div>
          <strong>Pinecone API Key</strong>
          <p v-if="userStore.hasPineconeKey">
            Ready
          </p>
          <p v-else>
            Please insert your <b>Pinecone</b> API key.
          </p>
        </div>
      </div>
    </div>

    <div class="actions">

      <div class="action-card" @click="handleRoute('PineconeIndexes')">
        <span>Go to Pinecone Indexes →</span>
      </div>

      <div class="action-card" @click="handleRoute('SupabaseNameSpaces')">
        <span>Go to Supabase Namespaces →</span>
      </div>

      <div class="action-card" @click="handleRoute('')">
        <span>Go to Embed your Data to Pinecone →</span>
      </div>

      <div class="action-card" @click="handleRoute('')">
        <span>Go to Embed your Data to Supabase →</span>
      </div>

      <div class="action-card" @click="handleRoute('')">
        <span>Go to Evaluate with Pinecone →</span>
      </div>

      <div class="action-card" @click="handleRoute('')">
        <span>Go to Evaluate with Supabase →</span>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user_store";
import { storeToRefs } from "pinia";

const router = useRouter()
const userStore = useUserStore();

const { userInfo } = storeToRefs(userStore);
function handleRoute( route: string ){
    router.push(
        {
            name: route
        }
    )

}


</script>

<style scoped>
.dashboard {
    max-width: 1100px;
    padding: 40px;
    display: flex;
    flex-direction: column;
    gap: 30px;
}

.welcome-card {
    background: white;
    border-radius: 14px;
    padding: 25px;
    box-shadow: 0 2px 10px 4px rgba(0,0,0,.2);
}

.welcome-card h1 {
    margin: 0;
    font-size: 2rem;
}

.welcome-card p {
    color: #666;
}
.status-card {
    background: white;
    border-radius: 14px;
    padding: 25px;
    box-shadow: 0 2px 10px 4px rgba(0,0,0,.2);
}

.status-card h2 {
    padding-bottom: 20px;
}

.status-item {
    display: flex;
    align-items: flex-start;
    gap: 18px;
    padding: 15px 0;
    border-bottom: 1px solid #ececec;
}

.status-item:last-child {
    border-bottom: none;
}

.status-dot {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}

.green {
    background: #2ecc71;
}

.red {
    background: #e74c3c;
}


.actions {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.action-card {
    width: 90%;
    background: white;
    border-radius: 12px;
    padding: 22px 30px;
    cursor: pointer;
    font-size: 18px;
    font-weight: 600;
    transition: .2s;
    border: 1px solid #ddd;
    box-shadow: 0 2px 10px 4px rgba(0,0,0,.2);

    display: flex;
    justify-content: space-between;
    align-items: center;
}

.action-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 24px 6px rgba(0,0,0,.2);
    border-color: #409eff;
    color: #409eff;
}
</style>