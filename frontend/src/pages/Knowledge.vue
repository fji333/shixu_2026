<template>
  <section class="page-container">
    <header class="page-header split-header">
      <div>
        <p class="eyebrow">知识库维护</p>
        <h1>政策知识库管理</h1>
        <p class="lead">
          维护政策文件、办事指南和常见问题资料，为咨询答复提供依据。
        </p>
      </div>
      <button type="button" class="primary-action" @click="startCreate">新增政策文档</button>
    </header>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success-banner">{{ successMessage }}</p>

    <section class="section-card toolbar-panel" aria-label="知识库筛选">
      <label>
        关键词
        <input v-model="filters.keyword" type="search" placeholder="输入标题或正文关键词" />
      </label>
      <label>
        分类
        <select v-model="filters.category_id">
          <option value="">全部分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </label>
      <label>
        状态
        <select v-model="filters.status">
          <option value="">全部</option>
          <option value="active">有效</option>
          <option value="inactive">已停用</option>
        </select>
      </label>
      <div class="toolbar-actions">
        <button type="button" @click="loadKnowledge" :disabled="loading">
          {{ loading ? "查询中..." : "查询" }}
        </button>
        <button type="button" class="secondary-action" @click="resetFilters" :disabled="loading">
          重置
        </button>
      </div>
    </section>

    <section class="knowledge-layout">
      <section class="section-card knowledge-list-panel" aria-label="知识文档列表">
        <div class="section-title-row">
          <h2>文档列表</h2>
          <span class="muted-text">共 {{ knowledgeList.length }} 条</span>
        </div>

        <p v-if="loading" class="muted-text">知识文档加载中...</p>
        <p v-else-if="!knowledgeList.length" class="muted-text">暂无知识文档。</p>

        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>标题</th>
                <th>分类</th>
                <th>来源</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>更新时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in knowledgeList" :key="item.id">
                <td>{{ item.id }}</td>
                <td>{{ item.title }}</td>
                <td>{{ categoryName(item.category_id) }}</td>
                <td>{{ item.source || "未注明" }}</td>
                <td>
                  <span class="badge" :class="item.status">{{ statusLabel(item.status) }}</span>
                </td>
                <td>{{ formatTime(item.created_at) }}</td>
                <td>{{ formatTime(item.updated_at) }}</td>
                <td>
                  <div class="table-actions">
                    <button type="button" class="text-action" @click="viewDetail(item.id)">查看</button>
                    <button type="button" class="text-action" @click="startEdit(item.id)">编辑</button>
                    <button type="button" class="text-danger" @click="softDelete(item)">删除</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="section-card knowledge-editor-panel" aria-label="知识文档编辑">
        <h2>{{ editingId ? "编辑政策文档" : "新增政策文档" }}</h2>
        <form class="knowledge-form" @submit.prevent="submitForm">
          <label>
            标题
            <input v-model="form.title" type="text" placeholder="请输入政策文档标题" />
          </label>
          <label>
            分类
            <select v-model="form.category_id">
              <option value="">未分类</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </label>
          <label>
            来源
            <input v-model="form.source" type="text" placeholder="例如：本地示例政策文档" />
          </label>
          <label>
            状态
            <select v-model="form.status">
              <option value="active">有效</option>
              <option value="inactive">已停用</option>
            </select>
          </label>
          <label>
            正文内容
            <textarea v-model="form.content" rows="10" placeholder="请输入政策正文或办事说明" />
          </label>
          <div class="form-actions">
            <button type="submit" class="primary-action" :disabled="saving">{{ saving ? "保存中..." : "保存" }}</button>
            <button type="button" class="secondary-action" @click="resetForm" :disabled="saving">
              取消
            </button>
          </div>
        </form>
      </aside>
    </section>

    <section v-if="detail" class="section-card detail-panel" aria-label="知识文档详情">
      <div class="section-title-row">
        <h2>文档详情</h2>
        <button type="button" class="secondary-action" @click="detail = null">关闭</button>
      </div>
      <dl class="detail-meta">
        <div>
          <dt>ID</dt>
          <dd>{{ detail.id }}</dd>
        </div>
        <div>
          <dt>分类</dt>
          <dd>{{ categoryName(detail.category_id) }}</dd>
        </div>
        <div>
          <dt>来源</dt>
          <dd>{{ detail.source || "未注明" }}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd>{{ statusLabel(detail.status) }}</dd>
        </div>
      </dl>
      <h3>{{ detail.title }}</h3>
      <p class="detail-content">{{ detail.content }}</p>
    </section>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import {
  createKnowledge,
  deleteKnowledge,
  getCategories,
  getKnowledgeDetail,
  getKnowledgeList,
  updateKnowledge,
} from "../api";

const categories = ref([]);
const knowledgeList = ref([]);
const detail = ref(null);
const loading = ref(false);
const saving = ref(false);
const editingId = ref(null);
const errorMessage = ref("");
const successMessage = ref("");

const filters = reactive({
  keyword: "",
  category_id: "",
  status: "active",
});

const form = reactive({
  title: "",
  category_id: "",
  source: "",
  status: "active",
  content: "",
});

function formatTime(value) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString("zh-CN");
}

function categoryName(categoryId) {
  const category = categories.value.find((item) => item.id === Number(categoryId));
  return category?.name || "未分类";
}

function statusLabel(status) {
  const labels = {
    active: "有效",
    inactive: "已停用",
  };
  return labels[status] || status;
}

function showSuccess(message) {
  successMessage.value = message;
  window.setTimeout(() => {
    if (successMessage.value === message) {
      successMessage.value = "";
    }
  }, 3000);
}

function resetForm() {
  editingId.value = null;
  form.title = "";
  form.category_id = "";
  form.source = "";
  form.status = "active";
  form.content = "";
}

function buildListParams() {
  return {
    keyword: filters.keyword.trim(),
    category_id: filters.category_id,
    status: filters.status,
  };
}

async function loadCategories() {
  categories.value = await getCategories();
}

async function loadKnowledge() {
  loading.value = true;
  errorMessage.value = "";
  try {
    knowledgeList.value = await getKnowledgeList(buildListParams());
  } catch (error) {
    errorMessage.value = error.message || "知识文档加载失败";
  } finally {
    loading.value = false;
  }
}

async function resetFilters() {
  filters.keyword = "";
  filters.category_id = "";
  filters.status = "active";
  await loadKnowledge();
}

function startCreate() {
  resetForm();
  detail.value = null;
}

async function startEdit(id) {
  errorMessage.value = "";
  try {
    const doc = await getKnowledgeDetail(id);
    editingId.value = doc.id;
    form.title = doc.title;
    form.category_id = doc.category_id || "";
    form.source = doc.source || "";
    form.status = doc.status || "active";
    form.content = doc.content || "";
    detail.value = doc;
  } catch (error) {
    errorMessage.value = error.message || "文档详情加载失败";
  }
}

async function viewDetail(id) {
  errorMessage.value = "";
  try {
    detail.value = await getKnowledgeDetail(id);
  } catch (error) {
    errorMessage.value = error.message || "文档详情加载失败";
  }
}

function validateForm() {
  if (!form.title.trim()) {
    errorMessage.value = "请填写文档标题。";
    return false;
  }
  if (!form.content.trim()) {
    errorMessage.value = "请填写文档正文。";
    return false;
  }
  return true;
}

function formPayload() {
  return {
    title: form.title.trim(),
    category_id: form.category_id ? Number(form.category_id) : null,
    source: form.source.trim() || null,
    status: form.status || "active",
    content: form.content.trim(),
  };
}

async function submitForm() {
  if (!validateForm()) {
    return;
  }

  saving.value = true;
  errorMessage.value = "";
  try {
    if (editingId.value) {
      await updateKnowledge(editingId.value, formPayload());
      showSuccess("知识文档已更新。");
    } else {
      await createKnowledge(formPayload());
      showSuccess("知识文档已新增。");
    }
    resetForm();
    await loadKnowledge();
  } catch (error) {
    errorMessage.value = error.message || "知识文档保存失败";
  } finally {
    saving.value = false;
  }
}

async function softDelete(item) {
  const confirmed = window.confirm(`确认停用“${item.title}”？删除操作为停用文档，不会删除原始记录。`);
  if (!confirmed) {
    return;
  }

  errorMessage.value = "";
  try {
    await deleteKnowledge(item.id);
    showSuccess("知识文档已停用。");
    if (detail.value?.id === item.id) {
      detail.value = null;
    }
    await loadKnowledge();
  } catch (error) {
    errorMessage.value = error.message || "知识文档删除失败";
  }
}

onMounted(async () => {
  try {
    await loadCategories();
    await loadKnowledge();
  } catch (error) {
    errorMessage.value = error.message || "知识库页面初始化失败";
  }
});
</script>
