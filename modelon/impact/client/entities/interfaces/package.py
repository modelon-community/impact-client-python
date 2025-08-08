from abc import ABC, abstractmethod


class PackageInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Package name."""
        raise NotImplementedError
