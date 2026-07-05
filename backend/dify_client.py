"""
Dify 接入层。
只负责调用真实 Dify API、维护 session↔conversation 映射、对 Workflow
返回结果做纯统计计算。不做任何业务判断——那些逻辑属于 Dify Chatflow/Workflow。
"""

import json
import os
import re
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1").rstrip("/")
DIFY_CHATFLOW_API_KEY = os.getenv("DIFY_CHATFLOW_API_KEY", "")
DIFY_WORKFLOW_API_KEY = os.getenv("DIFY_WORKFLOW_API_KEY", "")

# ---------------------------------------------------------------------------
# 会话状态管理：session_id（前端生成）↔ conversation_id（Dify 对话 ID）
# 内存字典即可，不需要数据库。
# ---------------------------------------------------------------------------
SESSION_CONVERSATION_MAP: Dict[str, str] = {}


def _dify_user_id(session_id: str) -> str:
    return f"qihe-{session_id}"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _clean_dify_answer(answer: str) -> str:
    """
    清理 Dify answer 字段前后可能夹带的非 JSON 内容：
    1. DeepSeek/Qwen 思考模式的 <think>...</think> 标签
    2. markdown 代码块标记 ```json ... ```
    3. 前后的空白/换行
    """
    if not answer:
        return answer
    cleaned = answer.strip()
    # 去掉 <think>...</think> 思考标签（DeepSeek/Qwen 思考模式，大小写不敏感）
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", cleaned, flags=re.IGNORECASE)
    # 重新 strip 后再去掉 markdown 代码块包裹
    cleaned = cleaned.strip()
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?\s*```\s*$", "", cleaned)
    return cleaned.strip()


# ---------------------------------------------------------------------------
# 合同生成 —— Chatflow 调用
# ---------------------------------------------------------------------------

async def chatflow_send_message(
    session_id: str,
    content: str,
) -> Dict[str, Any]:
    """
    接收前端一轮文字消息，转发给 Dify Chatflow，并维护 session↔conversation 映射。
    返回 Dify 响应的结构化数据（可能包含 incomplete/success 两种状态）。
    """
    conversation_id = SESSION_CONVERSATION_MAP.get(session_id, "")
    user = _dify_user_id(session_id)

    payload: Dict[str, Any] = {
        "inputs": {},
        "query": content or "",
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": user,
    }

    url = f"{DIFY_BASE_URL}/chat-messages"
    headers = {"Authorization": f"Bearer {DIFY_CHATFLOW_API_KEY}"}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code >= 400:
            print(f"[dify_client] Dify Chatflow API 返回错误: status={resp.status_code}, body={resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()

    # 维护 session ↔ conversation 映射
    new_conversation_id = data.get("conversation_id", "")
    if new_conversation_id:
        SESSION_CONVERSATION_MAP[session_id] = new_conversation_id

    # Dify Chatflow 的 structured output 在 answer 字段中，是一段 JSON 字符串
    answer = data.get("answer", "{}")
    print(f"[dify_client] Dify answer (前200字符): {answer[:200]}")

    # 清理可能的 markdown 包裹，然后解析 JSON
    cleaned = _clean_dify_answer(answer)
    try:
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        print(f"[dify_client] answer 无法解析为 JSON，当作纯文本兜底处理")
        traceback.print_exc()
        parsed = {
            "status": "incomplete",
            "type": "info_collection",
            "message": answer,
        }

    return parsed


# ---------------------------------------------------------------------------
# 合同审查 —— Workflow 调用
# ---------------------------------------------------------------------------

def _guess_file_type(filename: str) -> str:
    """根据文件扩展名判断 Dify 所需的 type 字段值。"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in {"jpg", "jpeg", "png", "gif", "webp", "bmp"}:
        return "image"
    return "document"


async def _upload_file_to_dify(
    file_bytes: bytes, filename: str, content_type: Optional[str], user: str
) -> str:
    """Dify 两步法第一步：上传文件，返回 file_id。"""
    url = f"{DIFY_BASE_URL}/files/upload"
    headers = {"Authorization": f"Bearer {DIFY_WORKFLOW_API_KEY}"}
    files = {"file": (filename, file_bytes, content_type or "application/octet-stream")}
    data = {"user": user}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, files=files, data=data)
        if resp.status_code >= 400:
            print(f"[dify_client] Dify 文件上传返回错误: status={resp.status_code}, body={resp.text[:500]}")
        resp.raise_for_status()
        result = resp.json()

    file_id = result.get("id", "")
    if not file_id:
        raise ValueError("Dify 文件上传未返回 file_id")
    return file_id


def _count_risks(risks: list) -> Dict[str, Any]:
    """
    纯统计计算：遍历 risks 数组，重新计算各级别数量和整体风险等级。
    这是对 Dify 返回结果的统计，不是业务判断。
    """
    red_count = 0
    yellow_count = 0
    green_count = 0

    for r in risks:
        level = (r.get("risk_level") or "").upper()
        if level == "RED":
            red_count += 1
        elif level == "YELLOW":
            yellow_count += 1
        elif level == "GREEN":
            green_count += 1

    # 固定规则：由数量推导整体等级
    if red_count > 0:
        overall_risk_level = "RED"
    elif yellow_count > 0:
        overall_risk_level = "YELLOW"
    else:
        overall_risk_level = "GREEN"

    return {
        "overall_risk_level": overall_risk_level,
        "red_count": red_count,
        "yellow_count": yellow_count,
        "green_count": green_count,
    }


async def review_contract(
    file_payloads: list,
) -> Dict[str, Any]:
    """
    接收多个文件，逐一上传到 Dify → 调用 Workflow 审查 → 重新统计风险数据 → 返回。
    """
    user = _dify_user_id("review")

    # 两步法第一步：逐个上传文件拿 file_id
    file_refs = []
    for fp in file_payloads:
        file_id = await _upload_file_to_dify(
            fp["bytes"], fp["filename"], fp.get("content_type"), user
        )
        file_refs.append({
            "transfer_method": "local_file",
            "upload_file_id": file_id,
            "type": _guess_file_type(fp["filename"]),
        })

    # 两步法第二步：调用 Workflow
    payload = {
        "inputs": {
            "file": file_refs,
        },
        "response_mode": "blocking",
        "user": user,
    }

    url = f"{DIFY_BASE_URL}/workflows/run"
    headers = {"Authorization": f"Bearer {DIFY_WORKFLOW_API_KEY}"}

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code >= 400:
            print(f"[dify_client] Dify Workflow API 返回错误: status={resp.status_code}, body={resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()

    # 提取 Workflow 输出
    outputs = (data.get("data") or {}).get("outputs") or {}

    # 只读取 result_json 字段，解析出 risks 数组
    result_json_str = outputs.get("result_json", "{}")
    try:
        result_data = json.loads(result_json_str)
    except (json.JSONDecodeError, TypeError):
        result_data = {}

    risks = result_data.get("risks", [])

    # backend 自己重新统计（忽略 Dify 给的 overall_risk_level / *_count）
    counts = _count_risks(risks)

    return {
        "overall_risk_level": counts["overall_risk_level"],
        "red_count": counts["red_count"],
        "yellow_count": counts["yellow_count"],
        "green_count": counts["green_count"],
        "risks": risks,
    }
