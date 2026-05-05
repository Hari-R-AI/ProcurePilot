"""Unit tests for the Approval Service Matrix."""

import pytest
from app.services.approval_service import ApprovalService

def test_approval_service_l1_routing():
    """Test standard L1 routing for low budget."""
    result = ApprovalService.compute_approval_route(
        budget=50000.0,
        risk_flags=[],
        category="OFFICE_SUPPLIES",
        urgency="NORMAL"
    )
    assert result["level"] == "L1"
    assert "Department Head" in result["role"]

def test_approval_service_l2_routing():
    """Test L2 routing for mid budget."""
    result = ApprovalService.compute_approval_route(
        budget=200000.0,  # > L1 threshold (100k)
        risk_flags=[],
        category="SERVICES",
        urgency="NORMAL"
    )
    assert result["level"] == "L2"
    assert "Procurement Committee" in result["role"]

def test_approval_service_l3_routing():
    """Test L3 routing for high budget."""
    result = ApprovalService.compute_approval_route(
        budget=5000000.0,  # > L2 threshold (1,000,000)
        risk_flags=[],
        category="CAPITAL_EXPENDITURE",
        urgency="NORMAL"
    )
    assert result["level"] == "L3"
    assert "Management / Board" in result["role"]

def test_approval_service_risk_escalation():
    """Test escalation due to critical risk."""
    result = ApprovalService.compute_approval_route(
        budget=50000.0,
        risk_flags=[{"severity": "CRITICAL"}],
        category="SOFTWARE",
        urgency="NORMAL"
    )
    # L1 base gets escalated to L2 due to critical risk
    assert result["level"] == "L2"
    assert "Procurement Committee" in result["role"]
    assert "CRITICAL" in result["reason"]

def test_approval_service_urgency_escalation():
    """Test escalation for high urgency IT hardware."""
    result = ApprovalService.compute_approval_route(
        budget=50000.0,
        risk_flags=[],
        category="IT_HARDWARE",
        urgency="HIGH"
    )
    # Fast tracked but requires Committee min
    assert result["level"] == "L2"
    assert "Procurement Committee" in result["role"]
    assert "High-urgency IT_HARDWARE" in result["reason"]
