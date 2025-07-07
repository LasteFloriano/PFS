class Evento:
    def __init__(self, id, nome, data, horario, descricao, status="pendente"):
        self.id = id
        self.nome = nome
        self.data = data
        self.horario = horario
        self.descricao = descricao
        self.status = status  # novo atributo

    def atualizar_informacoes(self, nome, data, horario, descricao, status=None):
        self.nome = nome
        self.data = data
        self.horario = horario
        self.descricao = descricao
        if status is not None:
            self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "data": self.data,
            "horario": self.horario,
            "descricao": self.descricao,
            "status": self.status   # inclui no dict
        }

    @staticmethod
    def from_dict(d):
        return Evento(
            d["id"], d["nome"], d["data"], d["horario"], d["descricao"], d.get("status", "pendente")
        )