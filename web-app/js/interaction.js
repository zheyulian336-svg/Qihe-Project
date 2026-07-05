// 按钮点击、回车发送、文件选择等事件处理。

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('chat-messages')) {
    initGeneratePage();
  }
  if (document.getElementById('upload-grid')) {
    initReviewPage();
  }
});

// =================== 合同生成页 ===================

function initGeneratePage() {
  const sessionId = AppState.getSessionId();
  const textInput = document.getElementById('text-input');
  const sendBtn = document.getElementById('send-btn');

  // 页面加载时发送初始消息，获取 Dify Chatflow 的开场白
  (async () => {
    try {
      const result = await Api.sendTextMessage(sessionId, '你好');
      if (result.error) {
        Ui.showError(result.message || '出问题了，请稍后再试');
        return;
      }
      handleGenerateResult(result);
    } catch (e) {
      Ui.appendAiBubble('你好，我是契合合同助手，将通过对话帮你生成一份完整的房屋租赁合同。请开始告诉我相关信息。');
    }
  })();

  function handleGenerateResult(result) {
    if (result.error) {
      Ui.showError(result.message || '出问题了，请稍后再试');
      return;
    }

    const status = result.status;
    const type = result.type;

    if (status === 'success' && type === 'contract_draft') {
      // 合同信息已收集完整，展示合同卡片
      AppState.setComplete(true);
      AppState.setContractData({
        contract_body: result.contract_body || '',
        contract_info: result.contract_info || {},
        contract_title: result.contract_title || '',
        disclaimer: result.disclaimer || '',
      });
      // 先显示 AI 消息（如果有的话）
      if (result.message) {
        Ui.appendAiBubble(result.message);
      }
      // 显示合同卡片
      Ui.appendContractCard({
        contract_body: result.contract_body || '',
        contract_info: result.contract_info || {},
        contract_title: result.contract_title || '',
        disclaimer: result.disclaimer || '',
      });
    } else {
      // 其他情况（incomplete / guide 等）：显示 AI 消息，继续收集信息
      Ui.appendAiBubble(result.message || '');
    }
  }

  async function handleSendText() {
    if (AppState.isComplete()) return;
    const content = textInput.value.trim();
    if (!content) return;

    Ui.hideError();
    Ui.appendUserBubble(content);
    textInput.value = '';
    sendBtn.disabled = true;
    try {
      const result = await Api.sendTextMessage(sessionId, content);
      handleGenerateResult(result);
    } catch (e) {
      Ui.showError('出问题了，请稍后再试');
    } finally {
      sendBtn.disabled = false;
    }
  }

  sendBtn.addEventListener('click', handleSendText);
  textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSendText();
  });
}

// =================== 合同审查页 ===================

function initReviewPage() {
  const fileInput = document.getElementById('file-input');
  const addBtn = document.getElementById('upload-add-btn');
  const startBtn = document.getElementById('start-review-btn');

  Ui.renderUploadGrid(AppState.getReviewFiles());
  Ui.updateUploadHint();

  addBtn.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      // 追加到已选文件列表（最多 MAX_IMAGES 张）
      AppState.addReviewFiles(files);
      Ui.renderUploadGrid(AppState.getReviewFiles());
      Ui.updateUploadHint();
    }
    fileInput.value = '';
  });

  startBtn.addEventListener('click', async () => {
    Ui.hideError();
    const files = AppState.getReviewFiles();
    if (files.length === 0) {
      Ui.showError('请先上传合同文件');
      return;
    }

    startBtn.disabled = true;
    startBtn.textContent = '审查中…';
    try {
      const result = await Api.uploadReview(files);
      if (result.error) {
        Ui.showError(result.message || '出问题了，请稍后再试');
      } else {
        Ui.renderRiskResult(result);
      }
    } catch (e) {
      Ui.showError('出问题了，请稍后再试');
    } finally {
      startBtn.disabled = false;
      startBtn.textContent = '开始审查';
    }
  });
}
