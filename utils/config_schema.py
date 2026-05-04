from pydantic import BaseModel, Field
from typing import Dict, List


class AppConfig(BaseModel):
    watch_directory: str
    admin_password: str = Field(default="admin")
    # NEW: Mode and Schedule settings
    real_time_mode: bool = Field(default=True)
    scheduled_hour: int = Field(default=18, ge=0, le=23)  # 0-23 hour format

    retry_attempts: int = Field(default=3)
    base_delay: int = Field(default=2)
    file_mappings: Dict[str, List[str]] = Field(default_factory=dict)
