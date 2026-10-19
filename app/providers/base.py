from abc import ABC, abstractmethod


class HumanizerProvider(ABC):
    name: str

    @abstractmethod
    async def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 1500,
        temperature: float = 0.7,
    ) -> str:
        ...