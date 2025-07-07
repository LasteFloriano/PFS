import json
import os
from sistema.item_cardapio import ItemCardapio

class ItemCardapioService:
    lista_cardapio = []

    @classmethod
    def adicionar(cls, item):
        cls.lista_cardapio.append(item)
        cls.salvar()
    
    @classmethod
    def salvar(cls):
        caminho = os.path.join(os.path.dirname(__file__), "..", "Dados", "item_cardapio.json")
        caminho = os.path.abspath(caminho)
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump([item.to_dict() for item in cls.lista_cardapio], arquivo, ensure_ascii=False, indent=4)
            
    @classmethod
    def carregar(cls):
        caminho = os.path.join(os.path.dirname(__file__), "..", "Dados", "item_cardapio.json")
        caminho = os.path.abspath(caminho)
        if not os.path.exists(caminho):
            # Cria o arquivo se não existir
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
            cls.lista_cardapio = []
            return
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                conteudo = arquivo.read().strip()
                if not conteudo:
                    cls.lista_cardapio = []
                    return
                dados = json.loads(conteudo)
                cls.lista_cardapio = [ItemCardapio.from_dict(dado) for dado in dados]
        except FileNotFoundError:
            cls.lista_cardapio = []
        except json.JSONDecodeError as e:
            print(f"Erro ao carregar itens do cardápio: {e}")
            cls.lista_cardapio = []

    @classmethod
    def excluir(cls, item):
        try:
            cls.lista_cardapio.remove(item)
            cls.salvar()
        except ValueError:
            print("Não foi possível excluir")

    @classmethod
    def remover(cls, id):
        for item in cls.lista_cardapio:
            if item.id == id:
                cls.lista_cardapio.remove(item)
                cls.salvar()
                return True
        return False
    
    @classmethod
    def listar_cardapio(cls):
        return [item.to_dict() for item in cls.lista_cardapio]

    @classmethod
    def atualizar_disponibilidade(cls, id, disponivel):
        for item in cls.lista_cardapio:
            if item.id == id:
                item.disponivel = disponivel
                cls.salvar()
                return f"Disponibilidade do item {id} atualizada."
        return "Item não encontrado."