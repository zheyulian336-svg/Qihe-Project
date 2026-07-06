// 封装 fetch 调用 backend 接口，不做任何判断逻辑。

const API_BASE = (typeof window.__QIHE_API_BASE__ !== 'undefined')
  ? window.__QIHE_API_BASE__
  : `http://${window.location.hostname}:8000`;

const Api = (() => {
  async function sendTextMessage(sessionId, content) {
    const res = await fetch(`${API_BASE}/api/v1/generate/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, content }),
    });
    return res.json();
  }

  async function exportContractDocx(content, disclaimer) {
    const res = await fetch(`${API_BASE}/api/v1/generate/export-docx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, disclaimer }),
    });
    if (!res.ok) throw new Error('导出失败');
    return res.blob();
  }

  async function uploadReview(files) {
    const formData = new FormData();
    for (const f of files) formData.append('files', f);
    const res = await fetch(`${API_BASE}/api/v1/review/upload`, {
      method: 'POST',
      body: formData,
    });
    return res.json();
  }

  return { sendTextMessage, exportContractDocx, uploadReview };
})();
