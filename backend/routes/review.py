"""合同审查相关接口。只负责接收文件上传、转发给 Dify Workflow、把结果返回，
不做任何"判断风险等级"之类的业务判断——统计计算在 dify_client 中完成。"""

import traceback

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import dify_client

router = APIRouter()


@router.post("/api/v1/review/upload")
async def review_upload(request: Request):
    """接收合同文件上传，转发给 Dify Workflow 审查，返回结构化风险报告。"""
    try:
        form = await request.form()
    except Exception:
        return JSONResponse(status_code=400, content={"error": True, "message": "请求格式有误"})

    upload_files = form.getlist("files")

    if not upload_files:
        return JSONResponse(status_code=400, content={"error": True, "message": "请至少上传一个文件"})

    # 读取所有上传文件
    file_payloads = []
    for f in upload_files:
        if not hasattr(f, "read"):
            continue
        file_bytes = await f.read()
        file_payloads.append({
            "bytes": file_bytes,
            "filename": f.filename or "contract.pdf",
            "content_type": f.content_type,
        })

    if not file_payloads:
        return JSONResponse(status_code=400, content={"error": True, "message": "文件无效"})

    try:
        result = await dify_client.review_contract(file_payloads)
        return result
    except Exception:
        print("[routes/review] review_contract 异常:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": True, "message": "出问题了，请稍后再试"})
