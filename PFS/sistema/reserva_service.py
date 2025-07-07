import json
import os
from sistema.reserva import Reserva

class ReservaService:
    lista_reservas = []

    @classmethod
    def adicionar(cls, reserva):
        cls.lista_reservas.append(reserva)
        cls.salvar()

    @classmethod
    def salvar(cls):
        with open("Dados/reservas.json", "w") as arquivo:
            json.dump([reserva.to_dict() for reserva in cls.lista_reservas], arquivo, indent = 4, ensure_ascii = False)

    @classmethod
    def carregar(cls):
        caminho = "Dados/reservas.json"
        if not os.path.exists(caminho):
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            cls.lista_reservas = []
            return
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                conteudo = arquivo.read().strip()
                if not conteudo:
                    cls.lista_reservas = []
                    return
                dados = json.loads(conteudo)
                cls.lista_reservas = [Reserva.from_dict(dado) for dado in dados]
        except FileNotFoundError:
            cls.lista_reservas = []
        except json.JSONDecodeError as e:
            print(f"Erro ao carregar JSON: {e}")
            cls.lista_reservas = []

    @classmethod
    def excluir(cls, reserva):
        try:
            cls.lista_reservas.remove(reserva)
            cls.salvar()
        except ValueError:
            print("Não foi possível excluir")

    @classmethod
    def remover(cls, id):
        for reserva in cls.lista_reservas:
            if reserva.id == id:
                cls.lista_reservas.remove(reserva)
                cls.salvar()
                return True
        return False
    
    @classmethod
    def listar_reservas(cls):
        return [reserva.to_dict() for reserva in cls.lista_reservas]

    @classmethod
    def atualizar_status(cls, id, novo_status):
        for reserva in cls.lista_reservas:
            if reserva.id == id:
                reserva.status = novo_status
                cls.salvar()
                return f"Status da reserva {id} atualizado para {novo_status}."
        return "Reserva não encontrada."