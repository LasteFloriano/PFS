import json
import os
from sistema.evento import Evento

class EventoService:
    lista_eventos = []

    @classmethod 
    def adicionar(cls, evento):
        cls.lista_eventos.append(evento)
        cls.salvar()

    @classmethod
    def salvar(cls):
        caminho = os.path.join(os.path.dirname(__file__), "..", "Dados", "evento.json")
        caminho = os.path.abspath(caminho)
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump([evento.to_dict() for evento in cls.lista_eventos], arquivo, indent=4, ensure_ascii=False)

    @classmethod
    def carregar(cls):
        caminho = os.path.join(os.path.dirname(__file__), "..", "Dados", "evento.json")
        caminho = os.path.abspath(caminho)
        if not os.path.exists(caminho):
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            cls.lista_eventos = []
            return
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                conteudo = arquivo.read().strip()
                if not conteudo:
                    cls.lista_eventos = []
                    return
                dados = json.loads(conteudo)
                cls.lista_eventos = [Evento.from_dict(dado) for dado in dados]
        except Exception as e:
            print(f"Erro ao carregar eventos: {e}")
            cls.lista_eventos = []

    @classmethod
    def excluir(cls, evento):
        try:
            cls.lista_eventos.remove(evento)
            cls.salvar()
        except ValueError:
            print("Não foi possível excluir")
    
    @classmethod
    def remover(cls, id):
        for evento in cls.lista_eventos:
            if evento.id == id:
                cls.lista_eventos.remove(evento)
                cls.salvar()
                return True
        return False
    
    @classmethod
    def listar_eventos(cls):
        return [evento.to_dict() for evento in cls.lista_eventos]