import unittest
from salon_service import SalonService
from repositories.memory_salon_repository import MemorySalonRepository


class TestSalonService(unittest.TestCase):
    def setUp(self):
        self.service = SalonService(MemorySalonRepository())

    def test_crear_y_listar(self):
        res = self.service.crear({"nombre": "Lab Redes", "capacidad": 30, "ubicacion": "Piso 3"})
        self.assertEqual(res["status"], "ok")
        data = self.service.listar()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["nombre"], "Lab Redes")

    def test_capacidad_invalida(self):
        res = self.service.crear({"nombre": "Lab", "capacidad": 0, "ubicacion": "Piso 1"})
        self.assertEqual(res["status"], "error")

    def test_actualizar_inexistente(self):
        res = self.service.actualizar(99, {"nombre": "Lab", "capacidad": 10, "ubicacion": "Piso 1"})
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
