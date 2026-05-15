const API_BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export function checkHealth() {
  return request("/health");
}

export function sendChatMessage(question) {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function getChatHistory(limit = 20) {
  return request(`/chat/history?limit=${limit}`);
}

export function checkSafety(text) {
  return request("/safety/check", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function submitFeedback(chatId, rating, comment) {
  return request("/feedback", {
    method: "POST",
    body: JSON.stringify({
      chat_id: chatId,
      rating,
      comment: comment?.trim() || null,
    }),
  });
}

export function getFeedbackStatistics() {
  return request("/feedback/statistics");
}

export function getDashboardData() {
  return request("/dashboard");
}

export function getLLMStatus() {
  return request("/llm/status");
}

export function getCategories() {
  return request("/categories");
}

function buildQuery(params = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, value);
    }
  });
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

export function getKnowledgeList(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.keyword) {
    searchParams.append("keyword", params.keyword);
  }
  if (params.category_id) {
    searchParams.append("category_id", params.category_id);
  }
  if (params.status !== undefined && params.status !== null) {
    searchParams.append("status", params.status);
  }
  const queryString = searchParams.toString();
  return request(`/knowledge${queryString ? `?${queryString}` : ""}`);
}

export function getKnowledgeDetail(id) {
  return request(`/knowledge/${id}`);
}

export function createKnowledge(data) {
  return request("/knowledge", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateKnowledge(id, data) {
  return request(`/knowledge/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteKnowledge(id) {
  return request(`/knowledge/${id}`, {
    method: "DELETE",
  });
}
