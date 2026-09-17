from abc import ABC, abstractmethod


class ISalonRepository(ABC):
    """ISP: contrato mínimo de persistencia de salones. DIP: el servicio depende de esta abstracción."""

    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def crear(self, nombre, capacidad, ubicacion):
        pass

    @abstractmethod
    def actualizar(self, id_salon, nombre, capacidad, ubicacion):
        pass
