from abc import ABC, abstractmethod


class CustomFunctionInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        "Custom function name"
        raise NotImplementedError
