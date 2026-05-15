<template>
  <section class="page-container dashboard-page">
    <header class="page-header">
      <p class="eyebrow">运行数据概览</p>
      <h1>数据看板</h1>
      <p class="lead">
        展示咨询记录、知识库文档、用户反馈和分类统计情况。
      </p>
    </header>

    <p v-if="loading" class="muted-text">数据加载中...</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <template v-if="dashboard">
      <section class="stats-grid" aria-label="顶部统计">
        <article class="stat-card">
          <span>知识库文档总数</span>
          <strong>{{ dashboard.overview.total_knowledge_docs }}</strong>
        </article>
        <article class="stat-card">
          <span>有效政策文档</span>
          <strong>{{ dashboard.overview.active_knowledge_docs }}</strong>
        </article>
        <article class="stat-card">
          <span>问答总次数</span>
          <strong>{{ dashboard.overview.total_chat_records }}</strong>
        </article>
        <article class="stat-card">
          <span>用户反馈总数</span>
          <strong>{{ dashboard.overview.total_feedback }}</strong>
        </article>
      </section>

      <section class="section-card dashboard-panel" aria-label="反馈统计">
        <h2>反馈统计</h2>
        <div class="feedback-summary-grid">
          <article>
            <span>有帮助</span>
            <strong>{{ dashboard.overview.helpful_feedback }}</strong>
          </article>
          <article>
            <span>没帮助</span>
            <strong>{{ dashboard.overview.unhelpful_feedback }}</strong>
          </article>
          <article>
            <span>一般</span>
            <strong>{{ dashboard.overview.neutral_feedback }}</strong>
          </article>
        </div>
      </section>

      <section class="section-card dashboard-panel" aria-label="分类统计">
        <h2>分类统计</h2>
        <p v-if="!dashboard.category_statistics.length" class="muted-text">暂无分类统计数据。</p>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>分类名称</th>
                <th>问答数量</th>
                <th>知识文档数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in dashboard.category_statistics" :key="item.category_id">
                <td>{{ item.category_name || "未分类" }}</td>
                <td>{{ item.chat_count }}</td>
                <td>{{ item.knowledge_count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="dashboard-two-column">
        <section class="section-card dashboard-panel" aria-label="最近问答">
          <h2>最近问答</h2>
          <p v-if="!dashboard.recent_chats.length" class="muted-text">暂无问答记录。</p>
          <article v-for="item in dashboard.recent_chats" :key="item.id" class="dashboard-list-item">
            <h3>{{ item.user_question }}</h3>
            <p>{{ item.ai_answer || "暂无回答内容" }}</p>
            <span>分类编号：{{ item.category_id || "未识别" }} · {{ formatTime(item.created_at) }}</span>
          </article>
        </section>

        <section class="section-card dashboard-panel" aria-label="最近反馈">
          <h2>最近反馈</h2>
          <p v-if="!dashboard.recent_feedback.length" class="muted-text">暂无反馈记录。</p>
          <article v-for="item in dashboard.recent_feedback" :key="item.id" class="dashboard-list-item">
            <h3>问答记录 #{{ item.chat_id }} · {{ ratingLabel(item.rating) }}</h3>
            <p>{{ item.comment || "用户未填写文字反馈。" }}</p>
            <span>{{ formatTime(item.created_at) }}</span>
          </article>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getDashboardData } from "../api";

const dashboard = ref(null);
const loading = ref(false);
const errorMessage = ref("");

function formatTime(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("zh-CN");
}

function ratingLabel(value) {
  const labels = {
    helpful: "有帮助",
    unhelpful: "没帮助",
    neutral: "一般",
  };
  return labels[value] || value;
}

async function loadDashboard() {
  loading.value = true;
  errorMessage.value = "";
  try {
    dashboard.value = await getDashboardData();
  } catch (error) {
    errorMessage.value = error.message || "数据看板加载失败";
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>
