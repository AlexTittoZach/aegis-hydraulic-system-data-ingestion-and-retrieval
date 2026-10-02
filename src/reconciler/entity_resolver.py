"""
Entity and Alias Resolver Module for Aegis Knowledge Ingestion System.
Handles canonicalization of component identifiers and disambiguation of deceptively similar names.
"""

from typing import Optional, Dict, Any, List

class EntityResolver:
    def __init__(self):
        # Canonical Entity Database with aliases and negative constraints
        self.entities: Dict[str, Dict[str, Any]] = {
            "PS-04A": {
                "canonical_id": "PS-04A",
                "common_name": "Pressure Sensor 04A",
                "aliases": [
                    "PS-04A", "P04A", "PS04A", "P.S.04-A",
                    "sensor_ps04a", "sensor_ps04a_threshold_bar",
                    "TB-7", "Connector J-14", "PRESSURE XDCR"
                ],
                "location": "HPU discharge line",
                "system": "Hydraulic Power Unit (HPU)",
                "replaces": "PS-04",
                "effective_version": ">= 3.2",
                "status": "ACTIVE",
                "disambiguation": "Not a form-fit-function replacement for PS-04; requires firmware >= 3.2. Completely distinct from PS-40 (Coolant Loop).",
                "provenance": "component_register.xlsx, ECN-1042.pdf, wiring_diagram.pdf, screen_03_diagnostics.png"
            },
            "PS-04": {
                "canonical_id": "PS-04",
                "common_name": "Pressure Sensor 04",
                "aliases": ["PS-04", "P04", "PS04", "PRESSURE SENSOR 04"],
                "location": "HPU discharge line",
                "system": "Hydraulic Power Unit (HPU)",
                "superseded_by": "PS-04A",
                "effective_version": "< 3.2",
                "status": "SUPERSEDED",
                "disambiguation": "Original pressure sensor installed prior to Revision 3.2. Suffered signal drift after ~18 months. Completely distinct from PS-40.",
                "provenance": "component_register.xlsx, ECN-1042.pdf, legacy_manual_v1.html"
            },
            "PS-40": {
                "canonical_id": "PS-40",
                "common_name": "Pressure Sensor 40",
                "aliases": ["PS-40", "P40", "PS40"],
                "location": "Coolant Loop, Skid B",
                "system": "Cooling System",
                "status": "ACTIVE",
                "disambiguation": "NOT related to HPU discharge circuit. Do not confuse with PS-04 / PS-04A.",
                "provenance": "component_register.xlsx (Row 6)"
            },
            "IV-21": {
                "canonical_id": "IV-21",
                "common_name": "Isolation Valve 21",
                "aliases": ["IV-21", "IV21", "Isolation Valve", "valve_iv21", "IV-21 SOLENOID"],
                "location": "Hydraulic Module",
                "system": "Hydraulic Power Unit (HPU)",
                "required_prestart_state": "OPEN",
                "status": "ACTIVE",
                "notes": "Must be OPEN prior to HPU startup.",
                "provenance": "component_register.xlsx, operator_manual.pdf, configuration_export.json"
            },
            "PLC-03": {
                "canonical_id": "PLC-03",
                "common_name": "HCS Controller",
                "aliases": ["PLC-03", "Controller", "Aegis Controller", "PLC-03 Controller"],
                "location": "Control Cabinet 1",
                "system": "Supervisory Control",
                "status": "ACTIVE",
                "reset_restriction": "Do NOT reset controller while hydraulic pressure is above 50 bar.",
                "provenance": "component_register.xlsx, operator_manual.pdf, maintenance_manual.pdf"
            },
            "HPU": {
                "canonical_id": "HPU",
                "common_name": "Hydraulic Power Unit",
                "aliases": ["HPU", "Hydraulic Power Unit", "Hydraulic Unit", "HP unit", "Hydraulic Power Pack"],
                "location": "Skid A, Bay 2",
                "system": "Hydraulic System",
                "status": "ACTIVE",
                "provenance": "component_register.xlsx, operator_manual.pdf, maintenance_manual.pdf"
            },
            "Auxiliary Reservoir": {
                "canonical_id": "Auxiliary Reservoir",
                "common_name": "Auxiliary Reservoir",
                "aliases": ["Auxiliary Reservoir", "Aux Reservoir"],
                "location": "Line 4 / Line 5 Skid",
                "system": "Hydraulic Fluid Supply",
                "status": "ACTIVE (Line 4/5 specific)",
                "notes": "Introduced in training slide deck for Line 4/5 peak demand top-up; NOT covered in standard Operator Manual.",
                "provenance": "training_slide_excerpt.pptx (Slide 2), system_diagram_hydraulic.pdf"
            },
            "Q1": {
                "canonical_id": "Q1",
                "common_name": "Main Disconnect",
                "aliases": ["Q1", "MAIN DISCONNECT Q1"],
                "location": "Control Cabinet 1",
                "voltage_rating": "480V incoming disconnect",
                "status": "ACTIVE",
                "provenance": "component_register.xlsx, system_diagram_electrical.png"
            },
            "T1": {
                "canonical_id": "T1",
                "common_name": "Control Transformer",
                "aliases": ["T1", "CONTROL XFMR T1"],
                "location": "Control Cabinet 1",
                "voltage_rating": "480:120V control power",
                "status": "ACTIVE",
                "provenance": "component_register.xlsx, system_diagram_electrical.png"
            }
        }

    def resolve_alias(self, query_string: str) -> Optional[Dict[str, Any]]:
        """Resolves any variant or alias string to the canonical entity."""
        normalized = query_string.strip()
        clean = normalized.replace(".", "").replace("-", "").replace("_", "").upper()

        for canonical_id, data in self.entities.items():
            if normalized.lower() == canonical_id.lower():
                return data
            for alias in data["aliases"]:
                if normalized.lower() == alias.lower():
                    return data
                alias_clean = alias.replace(".", "").replace("-", "").replace("_", "").upper()
                if clean == alias_clean:
                    return data

        return None

    def get_entity(self, canonical_id: str) -> Optional[Dict[str, Any]]:
        return self.entities.get(canonical_id)
