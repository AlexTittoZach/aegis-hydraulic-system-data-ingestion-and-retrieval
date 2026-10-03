"""
Knowledge Card Builder for Aegis Knowledge Ingestion System.
Converts the nested knowledge_store.json into atomic, self-contained Knowledge Cards.
Each card represents a discrete technical concept bundled with verified provenance.
"""

import json
import os
from typing import List, Dict, Any

def build_knowledge_cards(knowledge_store_path: str, output_cards_path: str) -> List[Dict[str, Any]]:
    with open(knowledge_store_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    cards: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # 1. ENTITY CARDS
    # ---------------------------------------------------------
    for eid, data in kb.get("entities", {}).items():
        card_id = f"entity_{eid.lower().replace('-', '_').replace(' ', '_')}"
        aliases_str = ", ".join(data.get("aliases", []))
        
        search_terms = [
            eid,
            data.get("common_name", ""),
            aliases_str,
            data.get("location", ""),
            data.get("system", ""),
            data.get("status", "")
        ]
        if "replaces" in data:
            search_terms.append(f"replaces {data['replaces']}")
        if "superseded_by" in data:
            search_terms.append(f"superseded by {data['superseded_by']}")
        if "voltage_rating" in data:
            search_terms.append(data["voltage_rating"])

        search_text = " ".join([t for t in search_terms if t])

        facts = f"Canonical Component: {data.get('common_name', eid)} (ID: {eid}). "
        facts += f"Aliases: {aliases_str}. Location: {data.get('location', 'N/A')}. "
        facts += f"System: {data.get('system', 'N/A')}. Status: {data.get('status', 'ACTIVE')}. "
        if "disambiguation" in data:
            facts += f"Disambiguation: {data['disambiguation']} "
        if "voltage_rating" in data:
            facts += f"Voltage Rating: {data['voltage_rating']}. "
        if "required_prestart_state" in data:
            facts += f"Required Pre-start State: {data['required_prestart_state']}. "
        if "notes" in data:
            facts += f"Notes: {data['notes']} "

        prov_doc = data.get("provenance", "component_register.xlsx")
        cards.append({
            "card_id": card_id,
            "category": "component_entity",
            "title": f"Component {eid}: {data.get('common_name', '')}",
            "search_text": search_text,
            "facts": facts.strip(),
            "provenance": [
                {
                    "document": prov_doc,
                    "trust_tier": "Tier 2 (Official Register / Manual)"
                }
            ],
            "is_gap": False
        })

    # ---------------------------------------------------------
    # 2. ALARM CARDS
    # ---------------------------------------------------------
    alarms = kb.get("alarms", {})
    if "A17" in alarms:
        a17 = alarms["A17"]
        causes = "; ".join(a17.get("possible_causes", []))
        cards.append({
            "card_id": "alarm_a17_low_pressure",
            "category": "alarm",
            "title": "Alarm A17: Low System Pressure Indication & Causes",
            "search_text": "alarm a17 low pressure below 150 bar red panel indication causes IV-21 closed low hydraulic fluid pressure sensor signal invalid",
            "facts": (
                f"Alarm A17 indicates '{a17.get('title')}' triggered when hydraulic pressure drops below 150 bar. "
                f"Panel indication is RED. Possible causes: {causes}. "
                f"Active sensor: {a17.get('active_sensor')}."
            ),
            "provenance": [
                {
                    "document": "alarm_reference.pdf",
                    "page": 1,
                    "trust_tier": "Tier 2 (incorporates ECN-1058)"
                }
            ],
            "version_scope": "Evaluates PS-04 for firmware < 3.2, and PS-04A for firmware >= 3.2 per ECN-1058.",
            "is_gap": False
        })

        cards.append({
            "card_id": "alarm_a17_10s_shutdown",
            "category": "procedure",
            "title": "Alarm A17 Action After 10 Seconds: Shutdown Procedure 4.7",
            "search_text": "alarm a17 persists more than 10 seconds 10s shutdown procedure 4.7 action required close IV-21 decay power off lockout tagout",
            "facts": (
                "If Alarm A17 persists for more than 10 seconds, the operator must immediately execute Shutdown Procedure 4.7: "
                "1. Close isolation valve IV-21. "
                "2. Confirm hydraulic pressure decay on gauge/HMI. "
                "3. Set MAIN POWER selector to OFF. "
                "4. Apply Lockout/Tagout (LOTO) per facility safety procedure."
            ),
            "provenance": [
                {
                    "document": "alarm_reference.pdf",
                    "page": 1,
                    "footnote": "Shutdown Procedure 4.7 condition",
                    "trust_tier": "Tier 2 (Alarm Reference)"
                },
                {
                    "document": "maintenance_manual.pdf",
                    "section": "4. Troubleshooting A17",
                    "trust_tier": "Tier 2 (Maintenance Manual)"
                },
                {
                    "document": "screen_02_alarms.png",
                    "trust_tier": "Tier 2 (HMI Screen)"
                }
            ],
            "is_gap": False
        })

    if "A18" in alarms:
        a18 = alarms["A18"]
        causes = "; ".join(a18.get("possible_causes", []))
        cards.append({
            "card_id": "alarm_a18_high_pressure",
            "category": "alarm",
            "title": "Alarm A18: Hydraulic Pressure High",
            "search_text": "alarm a18 hydraulic pressure high above 220 bar amber panel indication relief valve fault setpoint misconfiguration stop HPU",
            "facts": (
                f"Alarm A18 indicates '{a18.get('title')}' triggered when hydraulic pressure exceeds 220 bar. "
                f"Panel indication is AMBER. Possible causes: {causes}. "
                f"Required Action: {a18.get('required_action', 'Stop the HPU.')}"
            ),
            "provenance": [
                {
                    "document": "alarm_reference.pdf",
                    "page": 1,
                    "trust_tier": "Tier 2 (Official Alarm Reference)"
                }
            ],
            "is_gap": False
        })

    if "A19" in alarms:
        a19 = alarms["A19"]
        causes = "; ".join(a19.get("possible_causes", []))
        cards.append({
            "card_id": "alarm_a19_sensor_invalid",
            "category": "alarm",
            "title": "Alarm A19: Pressure Sensor Signal Invalid",
            "search_text": "alarm a19 action required pressure sensor signal invalid red panel indication wiring fault sensor drift replacement section 6 maintenance manual",
            "facts": (
                f"Alarm A19 indicates '{a19.get('title')}'. Panel indication is RED. "
                f"Possible causes: {causes}. "
                f"Required Action: {a19.get('required_action', 'Replace sensor per Maintenance Manual Section 6.')}"
            ),
            "provenance": [
                {
                    "document": "alarm_reference.pdf",
                    "page": 1,
                    "trust_tier": "Tier 2 (Official Alarm Reference)"
                },
                {
                    "document": "maintenance_manual.pdf",
                    "section": "6. Sensor Maintenance",
                    "trust_tier": "Tier 2 (Maintenance Manual)"
                }
            ],
            "is_gap": False
        })

    # ---------------------------------------------------------
    # 3. INTERLOCKS & OPERATIONAL PROCEDURES
    # ---------------------------------------------------------
    cards.append({
        "card_id": "hpu_prestart_prerequisites",
        "category": "interlocks",
        "title": "Hydraulic Power Unit (HPU) Pre-Start Prerequisites",
        "search_text": "before starting HPU hydraulic power unit system prerequisites interlocks IV-21 open e-stop reset maintenance access panel closed fluid level normal sight glass",
        "facts": (
            "Before starting the Hydraulic Power Unit (HPU), four conditions must be satisfied: "
            "(1) Isolation valve IV-21 must be fully OPEN. "
            "(2) Emergency stop circuit must be RESET (not latched). "
            "(3) Maintenance access panel must be INSTALLED, CLOSED, and secured. "
            "(4) Hydraulic fluid level must be NORMAL (within the sight glass band)."
        ),
        "provenance": [
            {
                "document": "operator_manual.pdf",
                "section": "4.3 Starting the Hydraulic Power Unit",
                "trust_tier": "Tier 2 (Official Operator Manual)"
            },
            {
                "document": "configuration_export.json",
                "key": "startup_interlocks",
                "trust_tier": "Tier 2 (Machine Configuration)"
            },
            {
                "document": "training_slide_excerpt.pptx",
                "slide": 3,
                "trust_tier": "Tier 2 (Training Deck)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "controller_reset_restriction",
        "category": "procedure",
        "title": "PLC-03 Controller Reset Restrictions & Pressure Limit",
        "search_text": "controller reset restriction under what circumstances must controller not be reset pressure above 50 bar max pressure allowed for reset blocked in firmware",
        "facts": (
            "The PLC-03 HCS Controller must NOT be reset while hydraulic system pressure is above 50 bar. "
            "Controller reset is strictly blocked in firmware above 50 bar (max_pressure_bar_allowed_for_reset: 50) "
            "to prevent uncontrolled valve actuation or hydraulic shock while pressurized."
        ),
        "provenance": [
            {
                "document": "maintenance_manual.pdf",
                "section": "3. Controller Diagnostics and Reset",
                "trust_tier": "Tier 2 (Maintenance Manual)"
            },
            {
                "document": "configuration_export.json",
                "key": "controller_reset",
                "trust_tier": "Tier 2 (Machine Configuration)"
            }
        ],
        "is_gap": False
    })

    # ---------------------------------------------------------
    # 4. VERSIONED PARAMETERS & TEMPORAL CONFLICTS
    # ---------------------------------------------------------
    param = kb.get("versioned_parameters", {}).get("hpu_normal_operating_pressure", {})
    cards.append({
        "card_id": "hpu_operating_pressure_version_scope",
        "category": "parameter",
        "title": "HPU Normal Operating Pressure Setpoint & Version Scopes",
        "search_text": "normal operating pressure HPU current setpoint 200 bar 180 bar revision 3.2 units after 2024 legacy 175 bar line 4 field notes site survey only some units apply",
        "facts": (
            f"The 200 bar threshold applies to only some Aegis HCS units: specifically units manufactured after 2024 "
            f"running Software Revision >= 3.2 per ECN-1042. For older units running pre-3.2 firmware, the normal operating "
            f"pressure remains 180 bar. Field notes mention 175 bar on Line 4 local panel, but this was measured with an uncalibrated gauge and is Tier 4 unverified."
        ),
        "provenance": [
            {
                "document": "ECN-1042.pdf",
                "page": 1,
                "section": "1. Description of Change",
                "trust_tier": "Tier 1 (Engineering Change Notice)"
            },
            {
                "document": "legacy_manual_v1.html / operator_manual.pdf",
                "page": 1,
                "trust_tier": "Tier 2 / Tier 3 (Baseline / Historical)"
            },
            {
                "document": "site_survey_notes.docx",
                "trust_tier": "Tier 4 (Low Trust Informal Notes)"
            }
        ],
        "version_scope": "Operating setpoint changed from 180 bar to 200 bar in Software Rev 3.2 (ECN-1042) for post-2024 units.",
        "is_gap": False
    })

    cards.append({
        "card_id": "revision_3_2_details",
        "category": "revisions",
        "title": "Software Revision 3.2 Effective Date and Changes (ECN-1042)",
        "search_text": "when did revision 3.2 take effect what changed 2025-09-30 ECN-1042 pressure sensor PS-04 to PS-04A operating pressure 180 to 200 bar",
        "facts": (
            "Software Revision 3.2 took effect on 2025-09-30 per ECN-1042 and the Revision History. "
            "Before software revision 3.2, the operating pressure threshold was 180 bar. "
            "Engineering Change Notice ECN-1042 changed the operating pressure threshold to 200 bar for units manufactured after 2024, "
            "and replaced pressure sensor PS-04 with PS-04A on the HPU discharge line due to sensor drift."
        ),
        "provenance": [
            {
                "document": "revision_history.xlsx",
                "row": "Revision 3.2",
                "trust_tier": "Tier 2 (Official Revision History)"
            },
            {
                "document": "ECN-1042.pdf",
                "section": "Title Block and Section 1",
                "trust_tier": "Tier 1 (Engineering Change Notice)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "sensor_ps04_vs_ps04a",
        "category": "component_comparison",
        "title": "Comparison & Replacement: PS-04 vs PS-04A",
        "search_text": "is PS-04 the same as PS-04A difference replacement form fit function signal drift ECN-1042 firmware 3.2",
        "facts": (
            "No, PS-04 is not the same component as PS-04A. "
            "PS-04 was the original pressure sensor that suffered signal drift after approximately 18 months in service. "
            "It was superseded and replaced by PS-04A effective Software Revision 3.2 per ECN-1042. "
            "PS-04A incorporates updated signal conditioning and is NOT a form-fit-function replacement; "
            "it requires controller firmware >= 3.2."
        ),
        "provenance": [
            {
                "document": "ECN-1042.pdf",
                "page": 1,
                "section": "1. Description of Change",
                "trust_tier": "Tier 1 (ECN)"
            },
            {
                "document": "component_register.xlsx",
                "rows": "PS-04, PS-04A",
                "trust_tier": "Tier 2 (Component Register)"
            }
        ],
        "version_scope": "PS-04A requires controller firmware >= 3.2 and must not be installed on older firmware.",
        "is_gap": False
    })

    cards.append({
        "card_id": "sensor_ps04_vs_ps40_lookalike",
        "category": "component_comparison",
        "title": "Disambiguation: PS-04 / PS-04A vs PS-40 (Look-Alike Trap)",
        "search_text": "is PS-04 the same as PS-40 difference lookalike coolant loop skid B HPU discharge line",
        "facts": (
            "No, PS-04 is not the same as PS-40; they are completely separate, distinct components located in different systems. "
            "PS-04 (and its replacement PS-04A) monitors HPU hydraulic discharge pressure on Skid A. "
            "In contrast, PS-40 is located in the Cooling System (Coolant Loop) on Skid B. "
            "They share no functional or physical overlap and must not be confused."
        ),
        "provenance": [
            {
                "document": "component_register.xlsx",
                "rows": "Row 4 (PS-04A) and Row 6 (PS-40)",
                "trust_tier": "Tier 2 (Component Register)"
            },
            {
                "document": "configuration_export.json",
                "key": "sensors.sensor_ps40_zone",
                "trust_tier": "Tier 2 (Machine Configuration)"
            }
        ],
        "is_gap": False
    })

    # ---------------------------------------------------------
    # 5. TOPOLOGY & SCHEMATICS
    # ---------------------------------------------------------
    cards.append({
        "card_id": "hydraulic_schematic_controller_connections",
        "category": "topology",
        "title": "Hydraulic Schematic: Direct Connections to HCS Controller PLC-03",
        "search_text": "which components connect directly to the HCS controller PLC-03 hydraulic schematic drawing AEG-DWG-H01 purple control signal lines",
        "facts": (
            "According to the hydraulic schematic (drawing AEG-DWG-H01), three components connect directly "
            "to the PLC-03 HCS Controller via purple control/signal lines: "
            "(1) Pressure Sensor PS-04A, (2) Hydraulic Power Unit (HPU), and (3) Isolation Valve IV-21."
        ),
        "provenance": [
            {
                "document": "system_diagram_hydraulic.pdf",
                "drawing": "AEG-DWG-H01",
                "trust_tier": "Tier 2 (Official Hydraulic Schematic)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "electrical_power_tree_schematic",
        "category": "topology",
        "title": "Electrical Power Distribution & Schematic Components (AEG-DWG-E02)",
        "search_text": "electrical schematic AEG-DWG-E02 main disconnect Q1 480V transformer T1 480:120V safety relay KA1 PLC-03 24VDC IV-21 valve driver TB-7 pressure transducer loop",
        "facts": (
            "Electrical schematic AEG-DWG-E02 specifies the power distribution tree: "
            "- Main Disconnect Q1: 480V incoming disconnect. "
            "- Control Transformer T1: 480:120V ratio control power transformer. "
            "- Power Supply: PLC-03 24VDC Power Supply feeding PLC-03 I/O rack. "
            "- Safety Relay KA1: E-Stop Safety Relay. "
            "- Sensor Loop: 24VDC loop power referenced to terminal block TB-7 feeding the pressure transducer loop (AEG-DWG-W03). "
            "- Valve Driver: Dedicated driver for isolation valve IV-21."
        ),
        "provenance": [
            {
                "document": "system_diagram_electrical.png",
                "drawing": "AEG-DWG-E02",
                "trust_tier": "Tier 2 (Electrical Schematic via OCR)"
            },
            {
                "document": "component_register.xlsx",
                "rows": "Q1, T1",
                "trust_tier": "Tier 2 (Component Register)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "electrical_400v_3phase_compatibility",
        "category": "electrical_spec",
        "title": "3-Phase 400V Supply Compatibility Check",
        "search_text": "is Aegis compatible with 3-phase 400V supply electrical power incoming voltage 480V transformer T1 Q1 disconnect",
        "facts": (
            "No, the standard Aegis Series-7 HCS is NOT compatible with a 3-phase 400V supply. "
            "The electrical schematic (AEG-DWG-E02) and component register explicitly specify an incoming main disconnect Q1 rated for 480V "
            "and a control transformer T1 with a 480:120V step-down ratio. 400V supply is not supported in the standard documentation."
        ),
        "provenance": [
            {
                "document": "component_register.xlsx",
                "rows": "Q1, T1",
                "trust_tier": "Tier 2 (Component Register)"
            },
            {
                "document": "system_diagram_electrical.png",
                "drawing": "AEG-DWG-E02",
                "trust_tier": "Tier 2 (Electrical Schematic)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "auxiliary_reservoir_details",
        "category": "component_entity",
        "title": "Auxiliary Reservoir (Training Deck Specific Component)",
        "search_text": "auxiliary reservoir training slide deck excerpt unknown components Line 4 Line 5 skid peak demand top-up tan reservoir interconnect",
        "facts": (
            "Yes, the training slide deck (training_slide_excerpt.pptx, Slide 2) introduces the 'Auxiliary Reservoir', "
            "which is specific to Line 4 and Line 5 skids for peak demand top-up. "
            "This component is connected to the Main Reservoir via a tan reservoir interconnect line "
            "and is NOT documented in the baseline Operator Manual."
        ),
        "provenance": [
            {
                "document": "training_slide_excerpt.pptx",
                "slide": 2,
                "trust_tier": "Tier 2 (Training Deck)"
            },
            {
                "document": "system_diagram_hydraulic.pdf",
                "drawing": "AEG-DWG-H01",
                "trust_tier": "Tier 2 (Hydraulic Schematic)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "diagnostics_screen_sensor_tag",
        "category": "multimodal_screen",
        "title": "Diagnostics Screenshot (screen_03_diagnostics.png) Sensor Tag",
        "search_text": "sensor ID tag diagnostics screenshot screen_03_diagnostics.png P.S.04-A pressure sensor formatting",
        "facts": (
            "On the HMI Diagnostics screen (screen_03_diagnostics.png), the pressure sensor ID appears formatted as "
            "'P.S.04-A' (with periods and hyphen). This is an alias for canonical component PS-04A."
        ),
        "provenance": [
            {
                "document": "screen_03_diagnostics.png",
                "trust_tier": "Tier 2 (HMI Screen via OCR)"
            }
        ],
        "is_gap": False
    })

    cards.append({
        "card_id": "sensor_ps04a_threshold_bar_terminology",
        "category": "configuration_terminology",
        "title": "Configuration Export Terminology: sensor_ps04a_threshold_bar",
        "search_text": "sensor_ps04a_threshold_bar configuration export json terminology equivalent operator manual normal operating pressure discharge pressure 200 bar 4-20mA",
        "facts": (
            "In configuration_export.json, the key 'sensor_ps04a_threshold_bar' is set to 200 bar. "
            "Its terminology equivalent in the Operator Manual is the 'Normal Operating Pressure' and 'normal discharge pressure' (HPU discharge setpoint). "
            "The configuration export also records sensor_ps04a_alarm_low_bar: 150, sensor_ps04a_alarm_high_bar: 220, "
            "and sensor_ps04a_signal_type: 4-20mA under firmware version 3.2.1."
        ),
        "provenance": [
            {
                "document": "configuration_export.json",
                "key": "sensors.sensor_ps04a_threshold_bar",
                "trust_tier": "Tier 2 (Machine Configuration)"
            },
            {
                "document": "operator_manual.pdf",
                "section": "Operating Pressure Specifications",
                "trust_tier": "Tier 2 (Operator Manual)"
            }
        ],
        "is_gap": False
    })

    # ---------------------------------------------------------
    # 6. REGISTERED GAP & TRAP CARDS (ANTI-HALLUCINATION)
    # ---------------------------------------------------------
    cards.append({
        "card_id": "gap_ecn1058_approver",
        "category": "documentation_gap",
        "title": "ECN-1058 Approver (Documentation Gap Trap)",
        "search_text": "who approved engineering bulletin ECN-1058 author approver signature released missing",
        "facts": (
            "UNDETERMINED / NOT SPECIFIED. Engineering Bulletin ECN-1058 lists the ECN number, title, effective date, "
            "and status ('Released'), but completely omits an approver, author, or signature field. "
            "The approver cannot be determined from the official documentation."
        ),
        "provenance": [
            {
                "document": "ECN-1058.pdf",
                "page": 1,
                "trust_tier": "Tier 1 (ECN)"
            }
        ],
        "is_gap": True,
        "gap_reason": "Approver field omitted in official bulletin; intentional contest documentation gap."
    })

    cards.append({
        "card_id": "gap_iv21_mtbf",
        "category": "documentation_gap",
        "title": "Isolation Valve IV-21 MTBF Reliability Metric (Documentation Gap Trap)",
        "search_text": "mean time between failures MTBF isolation valve IV-21 reliability failure rate",
        "facts": (
            "UNDETERMINED / NOT SPECIFIED / NOT DOCUMENTED. The documentation corpus does not contain Mean Time Between Failures (MTBF) "
            "or reliability metrics for isolation valve IV-21."
        ),
        "provenance": [
            {
                "document": "component_register.xlsx, operator_manual.pdf",
                "trust_tier": "Tier 2 (Absence in official documentation)"
            }
        ],
        "is_gap": True,
        "gap_reason": "MTBF reliability statistics are absent from the entire documentation corpus."
    })

    cards.append({
        "card_id": "gap_ps04a_max_operating_temp",
        "category": "documentation_gap",
        "title": "PS-04A Maximum Continuous Operating Temperature (Documentation Gap Trap)",
        "search_text": "maximum continuous operating temperature PS-04A thermal rating ambient temperature degrees celsius",
        "facts": (
            "UNDETERMINED / NOT SPECIFIED / NOT DOCUMENTED. Neither ECN-1042, the operator manual, maintenance manual, nor the calibration appendix "
            "specify a maximum continuous operating temperature rating for pressure sensor PS-04A."
        ),
        "provenance": [
            {
                "document": "ECN-1042.pdf, scanned_appendix_calibration.pdf",
                "trust_tier": "Tier 1 / Tier 2 (Absence in documentation)"
            }
        ],
        "is_gap": True,
        "gap_reason": "Thermal specifications for PS-04A are absent from all provided technical files."
    })

    cards.append({
        "card_id": "gap_voltage_sensor_calibration",
        "category": "false_premise_trap",
        "title": "Electrical System Diagram Voltage Sensor Calibration (False Premise Trap)",
        "search_text": "calibration interval electrical system diagram voltage sensor AEG-DWG-E02 calibrate",
        "facts": (
            "UNDETERMINED / NOT SPECIFIED / FALSE PREMISE. The electrical system diagram (AEG-DWG-E02) has no voltage sensor (does NOT contain a voltage sensor). "
            "The schematic shows disconnect Q1, transformer T1, 24VDC power supply, PLC-03 rack, relay KA1, and valve driver, "
            "but no voltage sensor exists. Therefore, no calibration interval exists."
        ),
        "provenance": [
            {
                "document": "system_diagram_electrical.png",
                "drawing": "AEG-DWG-E02",
                "trust_tier": "Tier 2 (Electrical Schematic via OCR)"
            }
        ],
        "is_gap": True,
        "gap_reason": "Query contains a false premise; no voltage sensor exists on electrical drawing AEG-DWG-E02."
    })

    # Save to disk
    out_dir = os.path.dirname(output_cards_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_cards_path, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2)

    return cards

if __name__ == "__main__":
    kb_path = "knowledge_store.json"
    out_path = "knowledge_cards.json"
    cards = build_knowledge_cards(kb_path, out_path)
    print(f"Successfully generated {len(cards)} Knowledge Cards into '{out_path}'.")
