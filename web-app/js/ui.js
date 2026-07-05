// 渲染对话气泡、合同卡片、上传缩略图、风险报告等 DOM 操作。

const Ui = (() => {
  function scrollChatToBottom() {
    const scroll = document.getElementById('chat-scroll');
    if (scroll) scroll.scrollTop = scroll.scrollHeight;
  }

  // ---------- 对话气泡 ----------

  function appendUserBubble(text) {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    const row = document.createElement('div');
    row.className = 'msg-row msg-row-user';
    const bubble = document.createElement('div');
    bubble.className = 'bubble bubble-user';
    bubble.textContent = text;
    row.appendChild(bubble);
    container.appendChild(row);
    scrollChatToBottom();
  }

  function appendAiBubble(text) {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    const row = document.createElement('div');
    row.className = 'msg-row msg-row-ai';
    const bubble = document.createElement('div');
    bubble.className = 'bubble bubble-ai';
    bubble.textContent = text;
    row.appendChild(bubble);
    container.appendChild(row);
    scrollChatToBottom();
  }

  // ---------- 合同卡片（生成完成时） ----------

  function appendContractCard(data) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const contractBody = data.contract_body || '';
    const contractTitle = data.contract_title || '房屋租赁合同';
    const disclaimer = data.disclaimer || '';
    const contractInfo = data.contract_info || {};

    const row = document.createElement('div');
    row.className = 'msg-row msg-row-ai';

    const card = document.createElement('div');
    card.className = 'contract-card';

    // 头部：图标 + 标题
    const header = document.createElement('div');
    header.className = 'contract-card-header';

    const iconWrap = document.createElement('div');
    iconWrap.className = 'contract-card-icon';
    iconWrap.innerHTML =
      '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#3B5CB7" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M7 3h7l4 4v14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>' +
      '<path d="M14 3v4h4"/><path d="M8.5 12h7"/><path d="M8.5 15.5h7"/></svg>';

    const info = document.createElement('div');
    const name = document.createElement('div');
    name.className = 'contract-card-name';
    name.textContent = contractTitle + '.docx';
    const summary = document.createElement('div');
    summary.className = 'contract-card-summary';
    summary.textContent = '合同信息已收集完整，可下载查看完整内容';
    info.appendChild(name);
    info.appendChild(summary);

    header.appendChild(iconWrap);
    header.appendChild(info);

    // 信息确认摘要
    if (Object.keys(contractInfo).length > 0) {
      const infoSummary = document.createElement('div');
      infoSummary.className = 'contract-info-summary';
      const entries = Object.entries(contractInfo);
      entries.forEach(([key, value]) => {
        if (value) {
          const item = document.createElement('span');
          item.className = 'info-tag';
          item.textContent = value;
          infoSummary.appendChild(item);
        }
      });
      card.appendChild(infoSummary);
    }

    // 合同正文预览
    const preview = document.createElement('pre');
    preview.className = 'contract-card-preview';
    preview.textContent = contractBody;
    card.appendChild(preview);

    // 免责声明
    if (disclaimer) {
      const disc = document.createElement('p');
      disc.className = 'contract-disclaimer';
      disc.textContent = disclaimer;
      card.appendChild(disc);
    }

    // 下载按钮
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'primary-btn full-width';
    downloadBtn.textContent = '下载合同';
    downloadBtn.addEventListener('click', async () => {
      downloadBtn.disabled = true;
      downloadBtn.textContent = '正在生成…';
      try {
        const blob = await Api.exportContractDocx(contractBody, disclaimer);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = (contractTitle || '房屋租赁合同') + '.docx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      } catch (e) {
        showError('下载失败，请稍后再试');
      } finally {
        downloadBtn.disabled = false;
        downloadBtn.textContent = '下载合同';
      }
    });

    card.appendChild(header);
    card.appendChild(preview);
    card.appendChild(downloadBtn);
    row.appendChild(card);
    container.appendChild(row);
    scrollChatToBottom();
  }

  // ---------- 错误提示 ----------

  function showError(message) {
    const banner = document.getElementById('error-banner');
    if (!banner) return;
    banner.textContent = message;
    banner.hidden = false;
  }

  function hideError() {
    const banner = document.getElementById('error-banner');
    if (banner) banner.hidden = true;
  }

  // ---------- 文件上传缩略图 ----------

  function renderUploadGrid(files) {
    const grid = document.getElementById('upload-grid');
    const addBtn = document.getElementById('upload-add-btn');
    if (!grid || !addBtn) return;

    // 清除旧的缩略图（保留添加按钮）
    grid.querySelectorAll('.upload-tile').forEach((el) => el.remove());

    files.forEach((file, idx) => {
      const tile = document.createElement('div');
      tile.className = 'upload-tile';

      if (file.type && file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        tile.appendChild(img);
      } else {
        const docWrap = document.createElement('div');
        docWrap.className = 'upload-tile-doc';
        docWrap.innerHTML =
          '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#3B5CB7" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' +
          '<path d="M7 3h7l4 4v14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14 3v4h4"/></svg>' +
          `<span>${file.name}</span>`;
        tile.appendChild(docWrap);
      }

      const removeBtn = document.createElement('button');
      removeBtn.className = 'upload-tile-remove';
      removeBtn.type = 'button';
      removeBtn.setAttribute('aria-label', '删除');
      removeBtn.textContent = '×';
      removeBtn.addEventListener('click', () => {
        AppState.removeReviewFile(idx);
        renderUploadGrid(AppState.getReviewFiles());
        updateUploadHint();
      });
      tile.appendChild(removeBtn);

      grid.insertBefore(tile, addBtn);
    });

    // 已满10张则隐藏添加按钮
    addBtn.hidden = files.length >= AppState.getMaxImages();
  }

  function updateUploadHint() {
    const hint = document.getElementById('upload-hint');
    if (!hint) return;
    const files = AppState.getReviewFiles();
    const max = AppState.getMaxImages();
    if (files.length > 0) {
      const names = files.map((f) => f.name).join('、');
      hint.textContent = `已选 ${files.length}/${max} 个文件：${names}`;
    } else {
      hint.textContent = `支持上传合同图片（最多${max}张）、Word 或 PDF 文件`;
    }
  }

  // ---------- 审查结果 ----------

  function riskLevelClass(level) {
    if (level === 'RED') return 'risk-red';
    if (level === 'YELLOW') return 'risk-yellow';
    if (level === 'GREEN') return 'risk-green';
    return '';
  }

  function riskLevelLabel(level) {
    if (level === 'RED') return '高风险';
    if (level === 'YELLOW') return '中风险';
    if (level === 'GREEN') return '低风险';
    return level;
  }

  function renderRiskResult(data) {
    const container = document.getElementById('review-result');
    if (!container) return;
    container.hidden = false;
    container.innerHTML = '';

    const overallLevel = data.overall_risk_level || 'GREEN';
    const risks = data.risks || [];

    // 整体风险等级横幅
    const banner = document.createElement('div');
    banner.className = `risk-banner ${riskLevelClass(overallLevel)}`;
    banner.textContent = `整体风险等级：${riskLevelLabel(overallLevel)}（红色 ${data.red_count || 0} · 黄色 ${data.yellow_count || 0} · 绿色 ${data.green_count || 0}）`;
    container.appendChild(banner);

    // 仅展示 RED 和 YELLOW 条目
    const visibleRisks = risks.filter(
      (r) => r.risk_level === 'RED' || r.risk_level === 'YELLOW'
    );

    if (visibleRisks.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'card empty-issues';
      empty.textContent = '未发现需要关注的风险条款';
      container.appendChild(empty);
      container.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    visibleRisks.forEach((risk) => {
      const card = document.createElement('div');
      card.className = `card issue-card ${riskLevelClass(risk.risk_level)}`;

      // 风险等级标签 + 编号
      const headerRow = document.createElement('div');
      headerRow.className = 'issue-header';

      const levelTag = document.createElement('span');
      levelTag.className = `issue-level-tag ${riskLevelClass(risk.risk_level)}`;
      levelTag.textContent = riskLevelLabel(risk.risk_level);
      headerRow.appendChild(levelTag);

      if (risk.risk_code) {
        const codeTag = document.createElement('span');
        codeTag.className = 'issue-code-tag';
        codeTag.textContent = risk.risk_code;
        headerRow.appendChild(codeTag);
      }

      if (risk.risk_target) {
        const targetTag = document.createElement('span');
        targetTag.className = 'issue-target-tag';
        targetTag.textContent = '涉及：' + risk.risk_target;
        headerRow.appendChild(targetTag);
      }

      card.appendChild(headerRow);

      // 原文片段
      if (risk.clause_text) {
        const original = document.createElement('div');
        original.className = 'issue-original';
        original.textContent = risk.clause_text;
        card.appendChild(original);
      }

      // 问题说明
      if (risk.risk_description) {
        const desc = document.createElement('p');
        desc.className = 'issue-problem';
        desc.innerHTML = '<strong>问题说明：</strong>' + risk.risk_description;
        card.appendChild(desc);
      }

      // 适用法条
      if (risk.applicable_law) {
        const law = document.createElement('p');
        law.className = 'issue-law';
        law.innerHTML = '<strong>适用法条：</strong>' + risk.applicable_law;
        card.appendChild(law);
      }

      // 修改建议
      if (risk.suggestion) {
        const suggestionBlock = document.createElement('div');
        suggestionBlock.className = 'issue-suggestion';

        const label = document.createElement('div');
        label.className = 'issue-suggestion-label';
        label.textContent = '修改建议';
        suggestionBlock.appendChild(label);

        const suggestionText = document.createElement('p');
        suggestionText.textContent = risk.suggestion;
        suggestionBlock.appendChild(suggestionText);

        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.type = 'button';
        copyBtn.textContent = '复制';
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(risk.suggestion).then(() => {
            copyBtn.textContent = '已复制';
            setTimeout(() => { copyBtn.textContent = '复制'; }, 1500);
          });
        });
        suggestionBlock.appendChild(copyBtn);

        card.appendChild(suggestionBlock);
      }

      container.appendChild(card);
    });

    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  return {
    appendUserBubble,
    appendAiBubble,
    appendContractCard,
    showError,
    hideError,
    renderUploadGrid,
    updateUploadHint,
    renderRiskResult,
  };
})();
