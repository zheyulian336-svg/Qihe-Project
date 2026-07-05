"""合同生成相关接口。只负责接收请求、转发给 Dify Chatflow、把结果原样返回，
不做任何"信息是否收集完整"之类的业务判断——那些逻辑属于 Dify Chatflow。"""

import traceback

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

import dify_client
import document_generator

router = APIRouter()


@router.post("/api/v1/generate/message")
async def generate_message(request: Request):
    """接收前端文字消息，转发给 Dify Chatflow，原样返回结构化响应。"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": True, "message": "请求格式有误"})

    session_id = body.get("session_id")
    content = body.get("content") or ""

    if not session_id:
        return JSONResponse(status_code=400, content={"error": True, "message": "缺少session_id"})

    try:
        result = await dify_client.chatflow_send_message(
            session_id=session_id,
            content=content,
        )
        return result
    except Exception:
        print("[routes/generate] chatflow_send_message 异常:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": True, "message": "出问题了，请稍后再试"})


@router.post("/api/v1/generate/export-docx")
async def export_docx(request: Request):
    """接收合同正文和免责声明，生成 .docx 文件供下载。"""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": True, "message": "请求格式有误"})

    content = body.get("content") or ""
    disclaimer = body.get("disclaimer") or ""

    if not content:
        return JSONResponse(status_code=400, content={"error": True, "message": "缺少合同内容"})

    try:
        buffer = document_generator.generate_contract_docx(content, disclaimer)
    except Exception:
        print("[routes/generate] generate_contract_docx 异常:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": True, "message": "出问题了，请稍后再试"})

    headers = {"Content-Disposition": "attachment; filename=contract.docx"}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
