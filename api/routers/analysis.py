"""
分析任务路由
============

提供分析任务的提交、查询、取消接口。
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import AnalysisTaskORM, ReportORM, get_session
from api.schemas import AnalysisSubmitRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# 运行中的任务追踪
_running_tasks: dict[str, asyncio.Task] = {}


def _orm_to_response(orm: AnalysisTaskORM) -> dict:
    """ORM 对象转响应字典"""
    return {
        "id": orm.id,
        "competitors": orm.competitors or [],
        "analysis_type": orm.analysis_type,
        "dimensions": orm.dimensions or [],
        "my_product": orm.my_product,
        "status": orm.status,
        "result": orm.result,
        "error_message": orm.error_message,
        "created_at": orm.created_at.isoformat() if orm.created_at else None,
        "completed_at": orm.completed_at.isoformat() if orm.completed_at else None,
    }


async def _run_analysis(task_id: str):
    """后台执行分析任务"""
    from api.database import async_session
    from agent.graph import create_analysis_graph

    async with async_session() as session:
        try:
            result = await session.execute(
                select(AnalysisTaskORM).where(AnalysisTaskORM.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                return

            task.status = "planning"
            await session.commit()

            graph = create_analysis_graph()
            task.status = "collecting"
            await session.commit()

            graph_result = await graph.ainvoke({
                "competitors": task.competitors,
                "analysis_type": task.analysis_type,
                "dimensions": task.dimensions or ["features", "pricing", "swot"],
                "my_product": task.my_product,
                "collection_plan": {},
                "raw_data": [],
                "extracted_info": [],
                "analysis_results": {},
                "report": "",
                "status": "collecting",
                "errors": [],
            })

            task.status = "completed"
            task.result = {
                "report": graph_result.get("report", ""),
                "analysis_results": graph_result.get("analysis_results", {}),
                "errors": graph_result.get("errors", []),
            }
            task.completed_at = datetime.now()
            await session.commit()

            if graph_result.get("report"):
                report_orm = ReportORM(
                    analysis_id=task_id,
                    title=f"竞品分析报告 - {', '.join(task.competitors)}",
                    report_type=task.analysis_type,
                    format="markdown",
                    content=graph_result["report"],
                )
                session.add(report_orm)
                await session.commit()

            logger.info(f"分析任务完成: {task_id}")

        except Exception as e:
            logger.error(f"分析任务失败: {task_id}, 错误: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            await session.commit()

        finally:
            _running_tasks.pop(task_id, None)


@router.post("")
async def submit_analysis(
    req: AnalysisSubmitRequest,
    session: AsyncSession = Depends(get_session),
):
    """提交分析任务"""
    orm = AnalysisTaskORM(
        competitors=req.competitors,
        analysis_type=req.analysis_type,
        dimensions=req.dimensions,
        my_product=req.my_product,
        status="pending",
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)

    # 启动后台任务
    task = asyncio.create_task(_run_analysis(orm.id))
    _running_tasks[orm.id] = task

    logger.info(f"提交分析任务: {orm.id}, 竞品: {req.competitors}")
    return {
        "code": 200,
        "data": {"task_id": orm.id, "status": "pending", "message": "分析任务已提交"},
        "message": "success",
    }


@router.get("")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取任务列表"""
    query = select(AnalysisTaskORM)

    if status:
        query = query.where(AnalysisTaskORM.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(AnalysisTaskORM.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    tasks = result.scalars().all()

    return {
        "code": 200,
        "data": [_orm_to_response(t) for t in tasks],
        "total": total,
        "page": page,
        "page_size": page_size,
        "message": "success",
    }


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取任务详情"""
    result = await session.execute(
        select(AnalysisTaskORM).where(AnalysisTaskORM.id == task_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {"code": 200, "data": _orm_to_response(orm), "message": "success"}


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    """取消/删除任务"""
    result = await session.execute(
        select(AnalysisTaskORM).where(AnalysisTaskORM.id == task_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task_id in _running_tasks:
        _running_tasks[task_id].cancel()
        _running_tasks.pop(task_id, None)

    await session.delete(orm)
    await session.commit()

    logger.info(f"删除任务: {task_id}")
    return {"code": 200, "data": None, "message": "删除成功"}
