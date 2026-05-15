<template>
  <section class="page-container home-page">
    <div class="home-hero">
      <div class="hero-copy">
        <p class="eyebrow">政务服务 · 智能咨询</p>
        <h1>政务服务智能问答平台</h1>
        <p class="lead">
          围绕政务服务高频咨询需求，系统提供政策问答、办事流程查询、信息安全提示和服务数据统计，
          帮助提升政务咨询响应效率。
        </p>

        <div class="actions">
          <RouterLink class="primary-action" to="/chat">开始咨询</RouterLink>
          <RouterLink class="secondary-action" to="/knowledge">进入知识库</RouterLink>
        </div>
      </div>

      <aside class="capability-panel" aria-label="服务概览">
        <h2>服务概览</h2>
        <ul>
          <li><span>咨</span>政策咨询</li>
          <li><span>办</span>办事指南</li>
          <li><span>护</span>信息保护</li>
          <li><span>统</span>数据统计</li>
        </ul>
      </aside>
    </div>

    <section class="section-card">
      <div class="section-heading">
        <p class="eyebrow">便民服务</p>
        <h2>政务服务功能</h2>
      </div>

      <div class="feature-grid" aria-label="政务服务功能">
      <article>
        <span class="feature-index">问</span>
        <h2>政策咨询问答</h2>
        <p>为用户提供政策文件、办事指南和常见问题查询服务。</p>
      </article>
      <article>
        <span class="feature-index">办</span>
        <h2>办事指南查询</h2>
        <p>围绕办理条件、申请材料、办理流程等内容提供指引。</p>
      </article>
      <article>
        <span class="feature-index">库</span>
        <h2>知识库维护</h2>
        <p>支持政策资料新增、编辑、停用和分类管理。</p>
      </article>
      <article>
        <span class="feature-index">安</span>
        <h2>信息安全提示</h2>
        <p>对手机号、身份证号、银行卡号等敏感信息进行提醒和脱敏处理。</p>
      </article>
      <article>
        <span class="feature-index">数</span>
        <h2>服务数据统计</h2>
        <p>展示咨询记录、知识库数量、反馈评价和分类统计。</p>
      </article>
      <article>
        <span class="feature-index">据</span>
        <h2>问答依据展示</h2>
        <p>回答结果展示参考资料，便于用户核对政策来源。</p>
      </article>
      </div>
    </section>

    <section class="section-card">
      <div class="section-heading">
        <p class="eyebrow">办理辅助</p>
        <h2>服务流程</h2>
      </div>
      <div class="process-grid">
        <article><span>1</span><strong>提交咨询</strong><p>用户输入政策、办事或民生服务相关问题。</p></article>
        <article><span>2</span><strong>检索资料</strong><p>系统从本地政策知识库中查找相关依据。</p></article>
        <article><span>3</span><strong>生成答复</strong><p>结合检索结果形成结构化答复。</p></article>
        <article><span>4</span><strong>记录反馈</strong><p>保存咨询记录和用户评价，用于后续服务优化。</p></article>
      </div>
    </section>

    <section class="section-card service-note">
      <p class="eyebrow">温馨提示</p>
      <h2>服务说明</h2>
      <p>
        本系统为政务服务咨询辅助平台，答复内容仅供办事参考，具体办理要求请以当地政务服务窗口和官方最新政策为准。
      </p>
    </section>
  </section>
</template>
