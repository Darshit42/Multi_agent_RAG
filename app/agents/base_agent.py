from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAgent(ABC):    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> None:
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass
    
    @abstractmethod
    async def validate(self, input_data: Any) -> bool:
        pass
    
    def run(self, input_data: Any) -> Any:
        if not self.validate(input_data):
            raise ValueError(f"Invalid input data for agent {self.name}")
        return self.process(input_data)
    
    async def run_async(self, input_data: Any) -> Any:
        if not await self.validate(input_data):
            raise ValueError(f"Invalid input data for agent {self.name}")
        return await self.process(input_data)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": "operational",
            "config": self.config
        } 