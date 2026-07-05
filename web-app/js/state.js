// 管理 session_id 等临时状态，内存变量即可，不需要 localStorage 持久化。

const AppState = (() => {
  let sessionId = null;
  let conversationComplete = false;
  let contractData = null;   // { contract_body, contract_info, contract_title, disclaimer }
  let selectedReviewFiles = [];

  const MAX_IMAGES = 10;

  function genId() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'sess-' + Date.now() + '-' + Math.random().toString(16).slice(2);
  }

  function getSessionId() {
    if (!sessionId) sessionId = genId();
    return sessionId;
  }

  function resetSession() {
    sessionId = genId();
    conversationComplete = false;
    contractData = null;
  }

  function setComplete(v) {
    conversationComplete = v;
  }

  function isComplete() {
    return conversationComplete;
  }

  function setContractData(data) {
    contractData = data;
  }

  function getContractData() {
    return contractData;
  }

  function getReviewFiles() {
    return selectedReviewFiles;
  }

  function addReviewFiles(newFiles) {
    for (const f of newFiles) {
      if (selectedReviewFiles.length >= MAX_IMAGES) break;
      selectedReviewFiles.push(f);
    }
  }

  function removeReviewFile(index) {
    selectedReviewFiles.splice(index, 1);
  }

  function clearReviewFiles() {
    selectedReviewFiles = [];
  }

  function getMaxImages() {
    return MAX_IMAGES;
  }

  return {
    getSessionId,
    resetSession,
    setComplete,
    isComplete,
    setContractData,
    getContractData,
    getReviewFiles,
    addReviewFiles,
    removeReviewFile,
    clearReviewFiles,
    getMaxImages,
  };
})();
