from flask import Blueprint, request, jsonify
from sistema.reserva import Reserva
from sistema.reserva_service import ReservaService
from sistema.main import proximo_id

reservas_bp = Blueprint("reservas", __name__)

@reservas_bp.route("/", methods=["POST"])
def adicionar_reserva():
    dados = request.get_json()

    for usuario, info in dados.items():
        data = info["data"]
        horario = info["horario"]
        pessoas = info["pessoas"]
        id = proximo_id()

        reserva = Reserva(usuario, id, data, horario, pessoas)
        ReservaService.adicionar(reserva)
        
    ReservaService.salvar()  
    return jsonify({"mensagem": "Reserva criada"}), 201

@reservas_bp.route("/", methods=["GET"])
def listar_reservas():
    return jsonify([r.to_dict() for r in ReservaService.lista_reservas])