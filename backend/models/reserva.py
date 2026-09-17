class Reserva:
    def __init__(self, id_reserva=None, fecha=None, hora_inicio=None, hora_fin=None, estado=None, id_docente=None, id_salon=None):
        self.id_reserva = id_reserva
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.estado = estado
        self.id_docente = id_docente
        self.id_salon = id_salon