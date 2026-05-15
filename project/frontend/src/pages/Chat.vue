<template>
  <section class="page-container">
    <header class="page-header">
      <p class="eyebrow">政务服务咨询</p>
      <h1>智能政务问答</h1>
      <p class="lead">
        输入政策咨询、办事流程或民生服务相关问题，系统将结合本地政策知识库提供参考答复。
      </p>
    </header>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <div class="chat-workspace">
      <main class="chat-main">
        <form class="section-card chat-panel" @submit.prevent="handleSubmit">
          <div class="section-heading">
            <p class="eyebrow">在线咨询</p>
            <h2>智能政务咨询</h2>
          </div>
          <label for="question">请输入政务咨询问题</label>
          <textarea
            id="question"
            v-model="question"
            rows="7"
            placeholder="例如：办理社保补贴需要准备哪些材料？"
            :disabled="loading"
          />
          <p class="privacy-hint">
            请勿输入完整身份证号、银行卡号、手机号、家庭住址等个人敏感信息。
          </p>
          <button type="submit" class="primary-action" :disabled="loading">
            {{ loading ? "提交中..." : "提交问题" }}
          </button>
        </form>

        <section class="section-card answer-panel" aria-label="回答展示区域">
          <div class="section-heading">
            <p class="eyebrow">咨询答复</p>
            <h2>答复内容</h2>
          </div>
      <p v-if="currentRecord?.has_sensitive_info" class="safety-message">
        {{ currentRecord.safety_warning }}
      </p>
      <p v-if="currentRecord?.masked_question" class="masked-question">
        系统保存的脱敏问题：{{ currentRecord.masked_question }}
      </p>
      <p class="answer-text">{{ currentAnswer }}</p>
      <dl v-if="currentRecord" class="answer-meta tag-meta">
        <div>
          <dt>分类编号</dt>
          <dd>{{ currentRecord.category_id || "未识别" }}</dd>
        </div>
        <div>
          <dt>问答时间</dt>
          <dd>{{ formatTime(currentRecord.created_at) }}</dd>
        </div>
        <div>
          <dt>资料来源</dt>
          <dd>{{ retrievalModeLabel(currentRecord.retrieval_mode) }}</dd>
        </div>
        <div>
          <dt>参考资料</dt>
          <dd>{{ currentRecord.reference_count || 0 }}</dd>
        </div>
        <div>
          <dt>答复方式</dt>
          <dd>{{ answerModeLabel(currentRecord.answer_mode) }}</dd>
        </div>
        <div v-if="currentRecord.llm_provider || currentRecord.llm_model">
          <dt>辅助服务</dt>
          <dd>
            {{ currentRecord.llm_provider || "未配置服务商" }}
            <span v-if="currentRecord.llm_model"> / {{ currentRecord.llm_model }}</span>
          </dd>
        </div>
      </dl>

      <p v-if="currentRecord?.llm_error" class="llm-message">
        当前答复由本地政策知识库辅助生成。
      </p>

      <section v-if="currentRecord" class="references-panel" aria-label="参考依据">
        <h3>参考依据</h3>
        <p v-if="!currentRecord.reference_count" class="muted-text">
          当前知识库暂未检索到明确依据。
        </p>
        <article
          v-for="reference in currentRecord.references"
          :key="`${reference.document_id}-${reference.chunk_index}`"
          class="reference-item"
        >
          <h4>{{ reference.title || "未命名政策资料" }}</h4>
          <p>{{ reference.content }}</p>
          <span>
            来源：{{ reference.source || "未注明来源" }} · 文档编号：{{ reference.document_id }}
            · 切片序号：{{ reference.chunk_index }}
          </span>
        </article>
      </section>

      <form v-if="currentRecord" class="feedback-panel" @submit.prevent="handleFeedbackSubmit">
        <h3>本次回答对您有帮助吗？</h3>
        <div class="feedback-options" role="group" aria-label="反馈评价">
          <button
            v-for="option in feedbackOptions"
            :key="option.value"
            type="button"
            class="feedback-option"
            :class="{ active: feedbackRating === option.value }"
            :disabled="feedbackLoading || feedbackSubmitted"
            @click="feedbackRating = option.value"
          >
            {{ option.label }}
          </button>
        </div>
        <label for="feedback-comment">文字反馈（可选）</label>
        <textarea
          id="feedback-comment"
          v-model="feedbackComment"
          rows="3"
          placeholder="可以补充说明回答哪里有帮助，或哪里需要改进。"
          :disabled="feedbackLoading || feedbackSubmitted"
        />
        <button type="submit" :disabled="feedbackLoading || feedbackSubmitted || !currentRecord?.id">
          {{ feedbackLoading ? "提交中..." : "提交反馈" }}
        </button>
        <p v-if="feedbackMessage" class="success-message">{{ feedbackMessage }}</p>
      </form>

      <div v-if="feedbackStatistics" class="feedback-statistics" aria-label="反馈统计">
        <span>反馈总数：{{ feedbackStatistics.total }}</span>
        <span>有帮助：{{ feedbackStatistics.helpful_count }}</span>
        <span>没帮助：{{ feedbackStatistics.unhelpful_count }}</span>
        <span>一般：{{ feedbackStatistics.neutral_count }}</span>
      </div>
        </section>
      </main>

      <aside class="chat-aside">
        <section class="section-card side-note">
          <h2>咨询安全提示</h2>
          <p>系统会自动检测并脱敏常见个人敏感信息，但建议提交问题时主动避免输入完整证件号、手机号和银行卡号。</p>
        </section>

        <section class="section-card history-panel" aria-label="最近问答记录">
          <div class="section-title-row">
            <h2>最近问答记录</h2>
            <button type="button" class="secondary-action" @click="loadHistory" :disabled="historyLoading">
              {{ historyLoading ? "刷新中..." : "刷新" }}
            </button>
          </div>

          <p v-if="!history.length" class="muted-text">暂无历史记录。</p>
          <article v-for="item in history" :key="item.id" class="history-item">
            <h3>{{ item.user_question }}</h3>
            <p>{{ item.ai_answer }}</p>
            <span>分类编号：{{ item.category_id || "未识别" }} · {{ formatTime(item.created_at) }}</span>
          </article>
        </section>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import {
  getChatHistory,
  getFeedbackStatistics,
  sendChatMessage,
  submitFeedback,
} from "../api";

const question = ref("");
const currentAnswer = ref("这里将展示系统根据政策知识库生成的参考答复。");
const currentRecord = ref(null);
const history = ref([]);
const loading = ref(false);
const historyLoading = ref(false);
const errorMessage = ref("");
const feedbackRating = ref("helpful");
const feedbackComment = ref("");
const feedbackLoading = ref(false);
const feedbackMessage = ref("");
const feedbackSubmitted = ref(false);
const feedbackStatistics = ref(null);

const feedbackOptions = [
  { label: "有帮助", value: "helpful" },
  { label: "没帮助", value: "unhelpful" },
  { label: "一般", value: "neutral" },
];

function formatTime(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("zh-CN");
}

function retrievalModeLabel(value) {
  const labels = {
    vector: "已检索到本地政策资料",
    keyword: "已匹配到相关政策资料",
    none: "未检索到依据",
  };
  return labels[value] || "未检索到依据";
}

function answerModeLabel(value) {
  const labels = {
    template_rag: "基于知识库生成",
    llm_rag: "基于知识库生成",
    no_context: "知识库无明确依据",
  };
  return labels[value] || "基于知识库生成";
}

async function loadHistory() {
  historyLoading.value = true;
  try {
    history.value = await getChatHistory(20);
  } catch (error) {
    errorMessage.value = error.message || "历史记录加载失败";
  } finally {
    historyLoading.value = false;
  }
}

async function loadFeedbackStatistics() {
  try {
    feedbackStatistics.value = await getFeedbackStatistics();
  } catch (error) {
    errorMessage.value = error.message || "反馈统计加载失败";
  }
}

async function handleSubmit() {
  const text = question.value.trim();
  if (!text) {
    errorMessage.value = "请先输入一个政务咨询问题。";
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  try {
    const record = await sendChatMessage(text);
    currentRecord.value = record;
    currentAnswer.value = record.ai_answer;
    feedbackRating.value = "helpful";
    feedbackComment.value = "";
    feedbackMessage.value = "";
    feedbackSubmitted.value = false;
    question.value = "";
    await loadHistory();
  } catch (error) {
    errorMessage.value = error.message || "提交失败，请稍后重试。";
  } finally {
    loading.value = false;
  }
}

async function handleFeedbackSubmit() {
  if (!currentRecord.value?.id) {
    errorMessage.value = "请先完成一次问答后再提交反馈。";
    return;
  }

  feedbackLoading.value = true;
  errorMessage.value = "";
  feedbackMessage.value = "";
  try {
    await submitFeedback(
      currentRecord.value.id,
      feedbackRating.value,
      feedbackComment.value,
    );
    feedbackSubmitted.value = true;
    feedbackMessage.value = "反馈已提交，感谢您的评价。";
    await loadFeedbackStatistics();
  } catch (error) {
    errorMessage.value = error.message || "反馈提交失败，请稍后重试。";
  } finally {
    feedbackLoading.value = false;
  }
}

onMounted(async () => {
  await loadHistory();
  await loadFeedbackStatistics();
});
</script>
