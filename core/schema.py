from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class TimeRecord:
    chronometric: Dict[str, Any] = field(default_factory=dict)
    relative: Dict[str, Any] = field(default_factory=dict)
    state_based: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LocationRecord:
    text: Optional[str] = None
    normalized: Optional[str] = None
    geometry: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvidenceRecord:
    modality: str
    source_id: str
    content: str
    span: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventRecord:
    record_id: str
    objects: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)
    information: Dict[str, Any] = field(default_factory=dict)
    time: TimeRecord = field(default_factory=TimeRecord)
    location: LocationRecord = field(default_factory=LocationRecord)
    evidence: List[EvidenceRecord] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    notes: Dict[str, Any] = field(default_factory=dict)

def to_dict(record: EventRecord) -> Dict[str, Any]:
    return asdict(record)
