"""
Conflict Manager and Multi-Tier Trust Reconciliation Module.
Maintains version-scoped facts, authority tiers, and gap/uncertainty classifications.
"""

from typing import Dict, Any, List

class ConflictManager:
    def __init__(self):
        self.trust_tiers = {
            "Tier 1": {
                "name": "Absolute Authority (Engineering Change Notices)",
                "sources": ["ECN-1042.pdf", "ECN-1058.pdf"],
                "rule": "Overrides all prior manuals from effective date/revision."
            },
            "Tier 2": {
                "name": "Baseline Authority (Official Manuals & Registers)",
                "sources": [
                    "operator_manual.pdf", "maintenance_manual.pdf",
                    "alarm_reference.pdf", "component_register.xlsx",
                    "revision_history.xlsx", "system_diagram_hydraulic.pdf",
                    "system_diagram_electrical.png", "wiring_diagram.pdf"
                ],
                "rule": "Authoritative standard specifications, valid unless superseded by Tier 1."
            },
            "Tier 3": {
                "name": "Historical / Superseded Documentation",
                "sources": ["legacy_manual_v1.html"],
                "rule": "Represents pre-revision historical specifications; not valid for current post-3.2 units."
            },
            "Tier 4": {
                "name": "Informal / Low Trust Field Observations",
                "sources": ["site_survey_notes.docx"],
                "rule": "Anecdotal field notes with uncalibrated tools; never treated as official specification."
            }
        }

        # Explicit parameter version matrix
        self.versioned_parameters = {
            "hpu_normal_operating_pressure": {
                "parameter": "Normal HPU Discharge Operating Pressure",
                "active_value": 200,
                "unit": "bar",
                "conditions": "Software Revision >= 3.2, Series-7 units manufactured after 2024",
                "active_provenance": {
                    "document": "ECN-1042.pdf",
                    "page": 1,
                    "section": "1. Description of Change",
                    "trust_tier": "Tier 1"
                },
                "historical_value": 180,
                "historical_conditions": "Software Revision < 3.2, units prior to revision 3.2",
                "historical_provenance": {
                    "document": "legacy_manual_v1.html / operator_manual.pdf",
                    "page": 1,
                    "section": "Operating Procedures",
                    "trust_tier": "Tier 2 / Tier 3"
                },
                "informal_observation": {
                    "value": 175,
                    "note": "Field technician noted 175 bar on Line 4 local panel, but noted it was measured with an uncalibrated gauge and is unverified.",
                    "document": "site_survey_notes.docx",
                    "trust_tier": "Tier 4"
                },
                "scope_applicability": "Only applies to units manufactured after 2024 on rev >= 3.2; units running pre-3.2 firmware remain at 180 bar."
            },
            "active_hpu_pressure_sensor": {
                "parameter": "HPU Discharge Line Pressure Sensor",
                "current_component": "PS-04A",
                "current_effective": "Software Revision 3.2 (released 2025-09-30)",
                "current_provenance": {
                    "document": "ECN-1042.pdf",
                    "page": 1,
                    "trust_tier": "Tier 1"
                },
                "prior_component": "PS-04",
                "prior_effective": "Software Revisions prior to 3.2",
                "compatibility_note": "PS-04A is NOT a form-fit-function replacement for PS-04; requires firmware >= 3.2."
            }
        }

        # Alarms Specification
        self.alarms = {
            "A17": {
                "code": "A17",
                "title": "Hydraulic Pressure Low",
                "condition": "Hydraulic pressure below 150 bar",
                "panel_indication": "RED",
                "possible_causes": [
                    "IV-21 closed or partially closed",
                    "Low hydraulic fluid",
                    "Pressure sensor signal invalid"
                ],
                "active_sensor": "PS-04 prior to revision 3.2, PS-04A on revision 3.2 and later (updated per ECN-1058)",
                "action_standard": "See Section 4 of Maintenance Manual AEG-MM-700",
                "action_if_persists_gt_10s": "Run Shutdown Procedure 4.7 (close IV-21, confirm pressure decay, power OFF, tag out)",
                "provenance": {
                    "document": "alarm_reference.pdf",
                    "page": 1,
                    "trust_tier": "Tier 2 (incorporates ECN-1058)"
                }
            },
            "A18": {
                "code": "A18",
                "title": "Hydraulic Pressure High",
                "condition": "Hydraulic pressure above 220 bar",
                "panel_indication": "AMBER",
                "possible_causes": ["Relief valve fault", "Setpoint misconfiguration"],
                "required_action": "Stop the HPU. Do not restart until pressure relief is verified.",
                "provenance": {"document": "alarm_reference.pdf", "page": 1, "trust_tier": "Tier 2"}
            },
            "A19": {
                "code": "A19",
                "title": "Pressure Sensor Signal Invalid",
                "panel_indication": "RED",
                "possible_causes": ["Sensor wiring fault", "Sensor drift beyond tolerance (see ECN-1042)"],
                "required_action": "Replace sensor per Maintenance Manual Section 6.",
                "provenance": {"document": "alarm_reference.pdf", "page": 1, "trust_tier": "Tier 2"}
            }
        }

        # Interlocks Specification
        self.interlocks = {
            "hpu_prestart_prerequisites": [
                "Isolation valve IV-21 is fully OPEN",
                "Emergency stop circuit is RESET (not latched)",
                "Maintenance access panel is INSTALLED, CLOSED, and secured",
                "Hydraulic fluid level is NORMAL (within sight glass band)"
            ],
            "provenance": "operator_manual.pdf (Section 4.3), configuration_export.json, training_slide_excerpt.pptx (Slide 3)"
        }

        # Known Gaps / Deliberately Undetermined Specifications (Anti-Hallucination Guardrails)
        self.known_gaps = {
            "ecn1058_approver": {
                "question": "Who approved engineering bulletin ECN-1058?",
                "status": "UNDETERMINED",
                "reason": "ECN-1058 lists ECN Number, Title, Effective, References, and Status ('Released'), but completely omits an approver or author field.",
                "provenance": "ECN-1058.pdf (Page 1)"
            },
            "iv21_mtbf": {
                "question": "What is the mean time between failures for the isolation valve IV-21?",
                "status": "UNDETERMINED",
                "reason": "The documentation corpus does not specify reliability or MTBF metrics for valve IV-21.",
                "provenance": "None (Absence in manuals and registers)"
            },
            "ps04a_max_temp": {
                "question": "What is the maximum continuous operating temperature of PS-04A?",
                "status": "UNDETERMINED",
                "reason": "Neither ECN-1042, the manuals, nor Appendix C specify a maximum continuous operating temperature rating for PS-04A.",
                "provenance": "None (Absence in manuals and datasheets)"
            },
            "voltage_sensor_calibration": {
                "question": "What is the calibration interval for the electrical system diagram's voltage sensor?",
                "status": "UNDETERMINED",
                "reason": "The electrical system diagram (AEG-DWG-E02) does not contain a voltage sensor; no calibration interval exists for this non-existent device.",
                "provenance": "system_diagram_electrical.png (AEG-DWG-E02)"
            },
            "supply_400v_3phase": {
                "question": "Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply?",
                "status": "INCOMPATIBLE / NOT SPECIFIED",
                "reason": "The system electrical schematic and component register specify a 480V incoming disconnect (Q1) and 480:120V control transformer (T1). A 400V supply is not supported by standard documentation.",
                "provenance": "component_register.xlsx, system_diagram_electrical.png"
            }
        }
