from dataclasses import dataclass


@dataclass
class StorageSiteInput:
    site_id: str
    site_name: str
    capacity_tons: float
    is_active: bool
