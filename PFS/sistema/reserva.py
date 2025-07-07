class Reserva:
    def __init__(self, usuario, id, data, horario, pessoas, email_cliente, telefone_cliente, status="pendente"):
        self.usuario = usuario
        self.id = id
        self.data = data
        self.horario = horario 
        self.pessoas = int(pessoas)
        self.email_cliente = email_cliente
        self.telefone_cliente = telefone_cliente
        self.status = status

    def confirmar(self):
        self.status = "confirmado"
    
    def cancelar(self):
        self.status = "cancelado"

    def to_dict(self):
        return {
            "id": self.id,
            "usuario": self.usuario,
            "email_cliente": self.email_cliente,
            "telefone_cliente": self.telefone_cliente,
            "data": self.data,
            "horario": self.horario,
            "pessoas": self.pessoas,
            "status": self.status
        }
    
    @staticmethod
    def from_dict(d):
        return Reserva(
            d["usuario"], d["id"], d["data"], d["horario"], d["pessoas"],
            d.get("email_cliente", ""), d.get("telefone_cliente", ""), d.get("status", "pendente")
        )