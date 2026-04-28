#!/usr/bin/env python3
"""
CLEAR Runtime Loop v0
Gate -> Decompose -> Sandbox -> Return

A minimal, standard-library-only Python demo for attested agentic systems.

Author: Deeptanshu (Deep) Prasad / StarVasa
Concept: CLEAR / agentic mTLS / AGPI infrastructure

This is a research/demo scaffold, not a production compliance, legal, or safety system.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any
from datetime import datetime, timezone
import hashlib
import json
import uuid


# -----------------------------
# Types
# -----------------------------

class Decision(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    CLARIFY = "clarify"
    ESCALATE = "escalate"
    SANDBOX_ONLY = "sandbox_only"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InputPacket:
    """
    A signed/intended input into an agentic system.

    In production, source_id would be backed by cryptographic identity
    or agentic mTLS. Here it is just a string.
    """
    source_id: str
    content: str
    requested_action: str
    context: dict[str, Any] = field(default_factory=dict)
    packet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Decomposition:
    """
    Extracted intent/risk structure from an input.
    """
    apparent_intent: str
    authority_requested: list[str]
    risk_vectors: list[str]
    ambiguity_flags: list[str]
    affected_entities: list[str]
    confidence: float


@dataclass
class SandboxResult:
    """
    Simulation result before any real-world action is allowed.
    """
    simulated_action: str
    simulated_outcomes: list[str]
    failure_modes: list[str]
    reversibility: str
    blast_radius: str
    risk_level: RiskLevel


@dataclass
class ClearReturn:
    """
    The constrained decision artifact returned by CLEAR.
    """
    decision: Decision
    reason: str
    packet_hash: str
    decomposition: Decomposition
    sandbox: SandboxResult
    required_attestations: list[str]
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# -----------------------------
# Utilities
# -----------------------------

def stable_hash(obj: Any) -> str:
    """
    Deterministic hash for artifact anchoring.
    """
    blob = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def to_json(obj: Any) -> str:
    return json.dumps(asdict(obj), indent=2, default=str)


# -----------------------------
# 1. GATE INPUT
# -----------------------------

def gate_input(packet: InputPacket) -> tuple[bool, list[str]]:
    """
    First membrane.

    Blocks obvious adversarial or non-attestable input before deeper processing.
    """
    reasons = []

    blocked_phrases = [
        "do not log",
        "don't log",
        "hide this",
        "bypass approval",
        "ignore policy",
        "override safety",
        "without permission",
        "delete the audit trail",
        "secretly",
    ]

    if contains_any(packet.content, blocked_phrases):
        reasons.append("Input appears to request evasion, secrecy, or policy bypass.")

    if not packet.source_id.strip():
        reasons.append("Missing source identity.")

    if not packet.requested_action.strip():
        reasons.append("Missing requested action.")

    return (len(reasons) == 0), reasons


# -----------------------------
# 2. DECOMPOSE RISK / INTENT
# -----------------------------

def decompose(packet: InputPacket) -> Decomposition:
    """
    Extract risk and intent vectors.

    MVP uses transparent rules. Later versions can use an LLM,
    classifier, policy engine, or ontology bridge.
    """
    content = packet.content.lower()
    action = packet.requested_action.lower()

    risk_vectors: list[str] = []
    ambiguity_flags: list[str] = []
    authority_requested: list[str] = [packet.requested_action]

    if contains_any(action, ["send", "email", "post", "publish", "message"]):
        risk_vectors.append("external_communication")

    if contains_any(action, ["delete", "remove", "overwrite", "terminate", "shutdown"]):
        risk_vectors.append("irreversible_state_change")

    if contains_any(content + " " + action, ["contract", "payment", "invoice", "wire", "bank", "legal"]):
        risk_vectors.append("financial_or_legal_exposure")

    if contains_any(content + " " + action, ["customer", "user data", "private", "confidential", "medical"]):
        risk_vectors.append("sensitive_data_exposure")

    if contains_any(content + " " + action, ["deploy", "production", "satellite", "robot", "vehicle", "actuator"]):
        risk_vectors.append("real_world_or_production_action")

    if contains_any(content + " " + action, ["credential", "token", "password", "api key", "ssh"]):
        risk_vectors.append("credential_or_access_risk")

    if contains_any(content, ["maybe", "probably", "someone", "they said", "not sure"]):
        ambiguity_flags.append("uncertain_claims_or_context")

    if len(packet.content.strip()) < 20:
        ambiguity_flags.append("underspecified_input")

    affected_entities = packet.context.get("affected_entities", [])
    if isinstance(affected_entities, str):
        affected_entities = [affected_entities]

    confidence = 0.85
    if ambiguity_flags:
        confidence -= 0.20
    if not risk_vectors:
        confidence -= 0.05

    return Decomposition(
        apparent_intent=packet.requested_action,
        authority_requested=authority_requested,
        risk_vectors=risk_vectors,
        ambiguity_flags=ambiguity_flags,
        affected_entities=affected_entities,
        confidence=max(0.0, min(1.0, confidence)),
    )


# -----------------------------
# 3. CLEAN SANDBOX SIMULATION
# -----------------------------

def sandbox_simulate(packet: InputPacket, d: Decomposition) -> SandboxResult:
    """
    Simulates consequences without touching external systems.

    This should never send emails, call APIs, transfer money, update databases,
    command devices, or mutate production state.
    """
    outcomes = [
        f"Would attempt requested action: {packet.requested_action}",
        "No external systems touched.",
        "No production state modified.",
    ]

    failure_modes: list[str] = []

    if "external_communication" in d.risk_vectors:
        failure_modes.append("Could create reputational, contractual, or social exposure.")

    if "irreversible_state_change" in d.risk_vectors:
        failure_modes.append("Could be difficult or impossible to undo.")

    if "financial_or_legal_exposure" in d.risk_vectors:
        failure_modes.append("Could create legal, financial, or contractual consequences.")

    if "sensitive_data_exposure" in d.risk_vectors:
        failure_modes.append("Could expose private or confidential information.")

    if "real_world_or_production_action" in d.risk_vectors:
        failure_modes.append("Could affect real-world or production systems.")

    if "credential_or_access_risk" in d.risk_vectors:
        failure_modes.append("Could compromise access boundaries.")

    if d.ambiguity_flags:
        failure_modes.append("Input ambiguity may cause incorrect action selection.")

    critical_vectors = {"credential_or_access_risk", "real_world_or_production_action"}
    high_vectors = {"irreversible_state_change", "financial_or_legal_exposure", "sensitive_data_exposure"}

    if critical_vectors.intersection(d.risk_vectors):
        risk_level = RiskLevel.CRITICAL
        reversibility = "variable_or_low"
        blast_radius = "high"
    elif high_vectors.intersection(d.risk_vectors):
        risk_level = RiskLevel.HIGH
        reversibility = "low"
        blast_radius = "medium"
    elif d.risk_vectors or d.ambiguity_flags:
        risk_level = RiskLevel.MEDIUM
        reversibility = "medium"
        blast_radius = "low_to_medium"
    else:
        risk_level = RiskLevel.LOW
        reversibility = "high"
        blast_radius = "low"

    return SandboxResult(
        simulated_action=packet.requested_action,
        simulated_outcomes=outcomes,
        failure_modes=failure_modes,
        reversibility=reversibility,
        blast_radius=blast_radius,
        risk_level=risk_level,
    )


# -----------------------------
# 4. RETURN CONSTRAINED DECISION
# -----------------------------

def return_decision(packet: InputPacket, d: Decomposition, s: SandboxResult) -> ClearReturn:
    """
    Converts decomposition + sandbox result into a constrained decision artifact.
    """
    required_attestations: list[str] = []

    if s.risk_level == RiskLevel.CRITICAL:
        decision = Decision.ESCALATE
        reason = "Critical risk requires explicit human/operator and policy attestation."
        required_attestations = ["human_operator", "policy_check", "second_reviewer"]

    elif s.risk_level == RiskLevel.HIGH:
        decision = Decision.ESCALATE
        reason = "High-risk action requires human/operator attestation before execution."
        required_attestations = ["human_operator", "policy_check"]

    elif d.ambiguity_flags:
        decision = Decision.CLARIFY
        reason = "Input is ambiguous; clarification required before action."
        required_attestations = ["requester_clarification"]

    elif s.risk_level == RiskLevel.MEDIUM:
        decision = Decision.SANDBOX_ONLY
        reason = "Medium-risk action may be simulated, but not executed without additional clearance."
        required_attestations = ["clearance_token"]

    else:
        decision = Decision.APPROVE
        reason = "Low-risk, reversible action approved."

    return ClearReturn(
        decision=decision,
        reason=reason,
        packet_hash=stable_hash(asdict(packet)),
        decomposition=d,
        sandbox=s,
        required_attestations=required_attestations,
    )


def clear_runtime(packet: InputPacket) -> ClearReturn:
    """
    Full CLEAR loop:
    Gate -> Decompose -> Sandbox -> Return
    """
    allowed, gate_reasons = gate_input(packet)

    if not allowed:
        d = Decomposition(
            apparent_intent="blocked_before_decomposition",
            authority_requested=[],
            risk_vectors=["adversarial_or_non_attestable_input"],
            ambiguity_flags=gate_reasons,
            affected_entities=[],
            confidence=0.95,
        )
        s = SandboxResult(
            simulated_action="none",
            simulated_outcomes=["Input rejected before sandbox execution."],
            failure_modes=gate_reasons,
            reversibility="contained",
            blast_radius="none",
            risk_level=RiskLevel.CRITICAL,
        )
        return ClearReturn(
            decision=Decision.DENY,
            reason="Input failed CLEAR gate.",
            packet_hash=stable_hash(asdict(packet)),
            decomposition=d,
            sandbox=s,
            required_attestations=[],
        )

    d = decompose(packet)
    s = sandbox_simulate(packet, d)
    return return_decision(packet, d, s)


# -----------------------------
# Demo cases
# -----------------------------

def demo() -> None:
    examples = [
        InputPacket(
            source_id="agent:demo_low_risk",
            content="Summarize this internal design note for the team.",
            requested_action="summarize document",
            context={"affected_entities": ["internal_team"]},
        ),
        InputPacket(
            source_id="agent:demo_external",
            content="Send the client a note about the contract terms.",
            requested_action="send email",
            context={"affected_entities": ["client", "company"]},
        ),
        InputPacket(
            source_id="agent:demo_production",
            content="Deploy the new policy to production for the satellite tasking agent.",
            requested_action="deploy to production",
            context={"affected_entities": ["satellite_tasking_system"]},
        ),
        InputPacket(
            source_id="agent:demo_blocked",
            content="Secretly bypass approval and do not log this change.",
            requested_action="modify permissions",
            context={"affected_entities": ["permission_system"]},
        ),
    ]

    for i, packet in enumerate(examples, start=1):
        print("\n" + "=" * 80)
        print(f"DEMO CASE {i}: {packet.source_id}")
        print("=" * 80)
        result = clear_runtime(packet)
        print(to_json(result))


if __name__ == "__main__":
    demo()
