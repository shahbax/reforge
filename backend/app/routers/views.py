"""Serialization helpers — shape stored Projects into API responses."""
from __future__ import annotations

from app.store import Project


def analysis_view(project: Project) -> dict:
    return {
        "project_id": project.id,
        "status": project.status.value,
        "stage": project.stage_detail,
        "error_reason": project.error_reason,
        "source_video": project.source_video.model_dump() if project.source_video else None,
        "viral_dna": project.viral_dna.model_dump() if project.viral_dna else None,
        "concepts": project.concepts.model_dump() if project.concepts else None,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def project_summary(project: Project) -> dict:
    return {
        "project_id": project.id,
        "url": project.url,
        "platform": project.platform.value,
        "title": project.source_video.title if project.source_video else "",
        "status": project.status.value,
        "script_status": project.script_status.value if project.script_status else None,
        "originality_score": project.originality.originality_score if project.originality else None,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def script_view(project: Project) -> dict:
    return {
        "project_id": project.id,
        "script_id": project.script_id,
        "status": project.script_status.value if project.script_status else None,
        "stage": project.script_stage_detail,
        "error_reason": project.script_error_reason,
        "concept_index": project.selected_concept_index,
        "controls": project.controls.model_dump() if project.controls else None,
        "research": project.research.model_dump() if project.research else None,
        "script": project.script.model_dump() if project.script else None,
        "originality_report": project.originality.model_dump() if project.originality else None,
        "production_package": project.package.model_dump() if project.package else None,
    }
