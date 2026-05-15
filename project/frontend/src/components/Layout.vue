<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/" aria-label="返回首页">
        <span class="brand-mark">政</span>
        <span>
          <strong>政务服务智能问答平台</strong>
          <small>政务服务咨询平台</small>
        </span>
      </RouterLink>
      <nav aria-label="主导航">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/chat">智能问答</RouterLink>
        <RouterLink to="/knowledge">知识库管理</RouterLink>
        <RouterLink to="/dashboard">数据看板</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>
