import psutil
from typing import Dict, Any

from friday.tools.base import BaseTool


class SystemStatsTool(BaseTool):
    @property
    def name(self) -> str:
        return "system_stats"

    @property
    def description(self) -> str:
        return "Returns current system statistics including CPU usage, RAM usage, and Disk space."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def execute(self, **kwargs) -> Any:
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": cpu,
            "ram_percent": memory.percent,
            "ram_used_gb": round(memory.used / (1024**3), 2),
            "ram_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
        }
