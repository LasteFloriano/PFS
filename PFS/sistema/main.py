from sistema.evento_service import EventoService
from sistema.reserva_service import ReservaService
from sistema.item_cardapio_service import ItemCardapioService
import json
import os

def carregar_dados():
        ReservaService.carregar()
        EventoService.carregar()
        ItemCardapioService.carregar()

ARQUIVO_CONTADOR = "Dados/id_contador.json"

def proximo_id():
    if not os.path.exists(ARQUIVO_CONTADOR):
        dados = {"ultimo_id": 0}
    else:
        try:
            with open(ARQUIVO_CONTADOR) as f:
                dados = json.load(f)
            if "ultimo_id" not in dados:
                dados["ultimo_id"] = 0
        except (json.JSONDecodeError, ValueError):
            dados = {"ultimo_id": 0}

    dados["ultimo_id"] += 1
    with open(ARQUIVO_CONTADOR, "w") as f:
        json.dump(dados, f)

    return dados["ultimo_id"]