class ItemCardapio:
    def __init__(self, id, nome, categoria, preco, descricao, disponivel=True):
        self.id = id
        self.nome = nome
        self.categoria = categoria
        self.preco = preco
        self.descricao = descricao
        self.disponivel = disponivel

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "descricao": self.descricao,
            "disponivel": self.disponivel
        }

    @staticmethod
    def from_dict(d):
        # Se o JSON não tiver o campo disponivel, assume True
        disponivel = d.get("disponivel", True)
        return ItemCardapio(d["id"], d["nome"], d["categoria"], d["preco"], d["descricao"], disponivel)