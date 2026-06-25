"""Compliance rule CRUD endpoints."""

from fastapi import APIRouter, HTTPException

import database
from schemas import RuleSchema

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("")
def get_rules():
    return database.get_all_rules()


@router.post("")
def create_rule(rule: RuleSchema):
    rule_id = database.create_rule(**rule.model_dump())
    return {"id": rule_id, "message": "Rule created successfully"}


@router.put("/{rule_id}")
def update_rule(rule_id: int, rule: RuleSchema):
    if not database.update_rule(rule_id=rule_id, **rule.model_dump()):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule updated successfully"}


@router.delete("/{rule_id}")
def delete_rule(rule_id: int):
    if not database.delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}
