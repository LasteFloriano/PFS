import streamlit as st
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
from sistema.reserva_service import ReservaService
from sistema.item_cardapio_service import ItemCardapioService
from sistema.evento_service import EventoService
from sistema.evento import Evento  
from sistema.item_cardapio import ItemCardapio
from sistema.reserva import Reserva
from sistema.main import carregar_dados

# Carrega todos os dados iniciais do sistema (reservas, cardápio, eventos)
# antes que a interface do usuário seja montada. Isso garante que os dados estejam
# disponíveis desde o início para exibição e manipulação.
carregar_dados() 

# --- Configuração da Página Streamlit ---
st.set_page_config(page_title="Painel de Gestão - Bistrô", layout="wide")
st.title("🍽️ Painel Administrativo - Bistrô")

# --- Menu Lateral ---
# Define as opções que aparecerão no menu de navegação lateral.
menu = ["Dashboard", "Reservas", "Eventos", "Cardápio", "Feedbacks", "Relatórios", "Mapa de Mesas"]
# Cria um rádio button no sidebar para o usuário selecionar a funcionalidade desejada.
choice = st.sidebar.radio("Selecione uma funcionalidade", menu)

# --- Função carregar_feedbacks ---
def carregar_feedbacks():
    """
    Carrega os feedbacks dos clientes diretamente de uma planilha Google Sheets.
    Esta função autentica com a API do Google, abre a planilha específica
    e processa os dados para um formato utilizável.
    """
    # Define os escopos de acesso necessários para interagir com o Google Sheets e Drive.
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    # Carrega as credenciais de serviço a partir de um arquivo JSON.
    creds = ServiceAccountCredentials.from_json_keyfile_name("Dados/credenciais.json", scope)
    # Autoriza o cliente `gspread` com as credenciais carregadas.
    client = gspread.authorize(creds)

    # Abre a planilha do Google Sheets usando seu ID único.
    spreadsheet = client.open_by_key("19aRY5aoAS3hVO81fT7ZF-1UfX3AVI2CIwLEtDoCm0HI")

    # Seleciona a aba específica da planilha onde as respostas do formulário estão armazenadas.
    worksheet = spreadsheet.worksheet("Form responses 1")

    # Obtém todos os registros da planilha como uma lista de dicionários,
    # onde cada dicionário representa uma linha (um feedback).
    registros = worksheet.get_all_records()

    # Processa os registros para limpar as chaves (nomes das colunas)
    # removendo espaços em branco extras, garantindo consistência.
    registros_corrigidos = []
    for reg in registros:
        reg_limpo = {k.strip(): v for k, v in reg.items()}
        registros_corrigidos.append(reg_limpo)
            
    feedbacks = []
    # Itera sobre os registros corrigidos para extrair e formatar os dados de feedback.
    for reg in registros_corrigidos:
        feedback = {
            "nome": reg.get("Nome (opcional)", "Anônimo"), # Usa "Anônimo" se o nome não estiver presente.
            "data": reg.get("Data da sua visita", ""),
            # Converte as avaliações para inteiros. Usa 0 se o valor não for um dígito válido.
            "avaliacao_atendimento": int(reg.get("Como você avalia o atendimento da equipe?", 0)) if str(reg.get("Como você avalia o atendimento da equipe?", "")).isdigit() else 0,
            "avaliacao_limpeza_conforto": int(reg.get("Como você avalia a limpeza e o conforto do ambiente?", 0)) if str(reg.get("Como você avalia a limpeza e o conforto do ambiente?", "")).isdigit() else 0,
            "avaliacao_tempo_espera": int(reg.get("Como você avalia o tempo de espera até ser atendido?", 0)) if str(reg.get("Como você avalia o tempo de espera até ser atendido?", "")).isdigit() else 0,
            "avaliacao_valor_qualidade": int(reg.get("Como você avalia o valor cobrado em relação à qualidade?", 0)) if str(reg.get("Como você avalia o valor cobrado em relação à qualidade?", "")).isdigit() else 0,
            "pedido_atendeu_expectativas": reg.get("O seu pedido atendeu às suas expectativas?", ""),
            "comentario": reg.get("O que podemos melhorar? (opcional)", "")
        }
        feedbacks.append(feedback)

    return feedbacks

# --- Lógica de Renderização Baseada na Escolha do Menu ---

# --- Bloco do Dashboard ---
if choice == "Dashboard":
    st.title("📊 Visão Geral - Painel do Restaurante")

    # --- Indicadores Chave ---
    # Exibe métricas importantes em colunas para uma visão rápida.
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Reservas", len(ReservaService.lista_reservas))
    with col2:
        st.metric("Eventos Ativos", len(EventoService.lista_eventos))
    with col3:
        st.metric("Itens no Cardápio", len(ItemCardapioService.lista_cardapio))

    st.divider() # Adiciona um divisor visual.

    # --- Reservas por Dia da Semana ---
    st.subheader("📅 Reservas por Dia")
    dias = {"Sexta": 0, "Sábado": 0, "Domingo": 0}
    # Itera sobre as reservas para contar quantas ocorrem em cada dia específico.
    for reserva in ReservaService.lista_reservas:
        try:
            # Converte a data da reserva para o nome do dia da semana em minúsculas.
            dia_semana = datetime.strptime(reserva.data, "%Y-%m-%d").strftime("%A").lower()
            if "sexta" in dia_semana:
                dias["Sexta"] += 1
            elif "sábado" in dia_semana:
                dias["Sábado"] += 1
            elif "domingo" in dia_semana:
                dias["Domingo"] += 1
        except ValueError:
            # Captura erros de formato de data e ignora a reserva.
            pass
    st.bar_chart(dias) # Exibe um gráfico de barras das reservas por dia.

    # --- Horários Mais Procurados ---
    st.subheader("⏰ Horários Mais Procurados")
    horarios = {}
    # Conta a frequência de cada horário de reserva.
    for reserva in ReservaService.lista_reservas:
        hora = reserva.horario
        horarios[hora] = horarios.get(hora, 0) + 1
    if horarios:
        st.line_chart(horarios) # Exibe um gráfico de linha dos horários.
    else:
        st.info("Nenhuma reserva registrada com horário.")

    st.divider()

    # --- Status das Reservas e Média de Pessoas ---
    status_count = {"pendente": 0, "confirmado": 0, "cancelado": 0}
    total_pessoas = 0
    # Calcula a contagem de cada status e o total de pessoas.
    for reserva in ReservaService.lista_reservas:
        status = reserva.status.lower()
        total_pessoas += reserva.pessoas
        if status in status_count:
            status_count[status] += 1

    col4, col5 = st.columns(2)
    with col4:
        st.subheader("⚡ Status das Reservas")
        st.bar_chart(status_count) # Gráfico de barras para o status das reservas.
    with col5:
        if ReservaService.lista_reservas:
            media = total_pessoas / len(ReservaService.lista_reservas)
            st.metric("👥 Média de Pessoas por Reserva", f"{media:.1f}") # Média de pessoas por reserva.
        else:
            st.info("Nenhuma reserva para calcular média.")

    st.divider()

    # --- Itens no Cardápio por Categoria ---
    st.subheader("🍽️ Itens no Cardápio por Categoria")
    categoria_count = {}
    # Conta quantos itens existem em cada categoria do cardápio.
    for item in ItemCardapioService.lista_cardapio:
        cat = item.categoria
        categoria_count[cat] = categoria_count.get(cat, 0) + 1
    if categoria_count:
        st.bar_chart(categoria_count) # Gráfico de barras para categorias do cardápio.
    else:
        st.info("Nenhum item cadastrado ainda.")

    st.divider()

    # --- Eventos Futuros Agendados ---
    hoje = datetime.today().date()
    # Filtra eventos que ainda vão acontecer.
    eventos_futuros = [
        evento for evento in EventoService.lista_eventos
        if datetime.strptime(evento.data, "%Y-%m-%d").date() >= hoje
    ]
    st.metric("📆 Eventos Futuramente Agendados", len(eventos_futuros)) # Exibe o número de eventos futuros.

    st.divider()

    # --- Resumo dos Feedbacks dos Clientes (NOVO) ---
    st.subheader("📝 Resumo dos Feedbacks dos Clientes")
    feedbacks = carregar_feedbacks() # Carrega os feedbacks.

    if feedbacks:
        total_feedbacks = len(feedbacks)
        # Calcula a média da avaliação de atendimento, ignorando valores não numéricos.
        avaliacoes = [fb.get("avaliacao_atendimento") for fb in feedbacks if isinstance(fb.get("avaliacao_atendimento"), (int, float))]
        media_avaliacao = round(sum(avaliacoes) / len(avaliacoes), 2) if avaliacoes else 0

        # Conta quantos feedbacks não possuem comentários.
        sem_comentario = sum(1 for fb in feedbacks if not fb.get("comentario"))

        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            st.metric("Total de Feedbacks", total_feedbacks)
        with colf2:
            st.metric("⭐ Média Avaliação Atendimento", media_avaliacao)
        with colf3:
            st.metric("Sem Comentário", sem_comentario)

        # Gráfico de distribuição das notas de atendimento.
        from collections import Counter
        contagem_notas = Counter(avaliacoes)
        notas_ord = sorted(contagem_notas.items())
        notas_dict = {str(k): v for k, v in notas_ord}

        st.bar_chart(notas_dict)
    else:
        st.info("Nenhum feedback disponível no momento.")

# --- Bloco de Gestão de Reservas ---
elif choice == "Reservas":
    st.header("📅 Gestão de Reservas")

    # --- Formulário para Adicionar Nova Reserva ---
    with st.form("add_reserva"):
        st.subheader("Adicionar Nova Reserva")
        usuario = st.text_input("Usuário")
        email_cliente = st.text_input("Email do Cliente")
        telefone_cliente = st.text_input("Telefone do Cliente")
        data = st.date_input("Data da Reserva")
        horario = st.time_input("Horário da Reserva")
        pessoas = st.number_input("Número de Pessoas", min_value=1)
        if st.form_submit_button("Adicionar"):
            # Gera um novo ID para a reserva.
            novo_id = len(ReservaService.lista_reservas) + 1
            # Cria um novo objeto Reserva.
            nova_reserva = Reserva(
                usuario=usuario,
                id=novo_id,
                data=data.strftime("%d/%m/%Y"), # Formata a data para string.
                horario=horario.strftime("%H:%M"), # Formata o horário para string.
                pessoas=pessoas,
                email_cliente=email_cliente,
                telefone_cliente=telefone_cliente,
                status="pendente"
            )
            ReservaService.adicionar(nova_reserva) # Adiciona a nova reserva.
            st.success(f"Reserva do usuário '{usuario}' adicionada com sucesso!")

    # Recarrega as reservas para garantir que a lista esteja atualizada.
    ReservaService.carregar()
    reservas = ReservaService.listar_reservas()

    if reservas:
        # Itera sobre cada reserva para exibi-la.
        for r in reservas:
            status = r['status']
            titulo = f"ID {r['id']} - {r['usuario']} ({r['data']} {r['horario']})"
            
            # Adiciona um emoji ao título da reserva com base no seu status.
            if status == "confirmado":
                titulo = f"✅ {titulo}"
            elif status == "pendente":
                titulo = f"⚠️ {titulo}"
            elif status == "cancelado":
                titulo = f"❌ {titulo}"

            # Usa um `expander` para mostrar os detalhes da reserva de forma organizada.
            with st.expander(titulo):
                # Organiza as informações de contato e número de pessoas em colunas.
                col1, col2, col3 = st.columns(3)
                col1.write(f"📧 Email: {r.get('email_cliente', '')}")
                col2.write(f"📞 Telefone: {r.get('telefone_cliente', '')}")
                col3.write(f"👥 Pessoas: {r['pessoas']}")

                st.markdown(f"**⚡ Status:** {status.capitalize()}")

                # Permite ao usuário alterar o status da reserva usando um `selectbox`.
                # A `key` é importante para garantir que o Streamlit trate cada selectbox como único.
                novo_status = st.selectbox(
                    "Alterar status:",
                    ["pendente", "confirmado", "cancelado"],
                    index=["pendente", "confirmado", "cancelado"].index(status),
                    key=f"status_{r['id']}" 
                )

                col_salvar, col_excluir = st.columns(2)
                with col_salvar:
                    # Botão para salvar as alterações de status.
                    if st.button("Salvar", key=f"salvar_{r['id']}"):
                        msg = ReservaService.atualizar_status(r['id'], novo_status)
                        st.success(msg)
                with col_excluir:
                    # Botão para excluir a reserva.
                    if st.button("Excluir Reserva", key=f"excluir_{r['id']}"):
                        sucesso = ReservaService.remover(r['id'])
                        if sucesso:
                            st.success(f"Reserva ID {r['id']} excluída com sucesso.")
                        else:
                            st.error("Erro ao tentar excluir a reserva.")

                st.divider()
    else:
        st.info("Nenhuma reserva registrada ainda.")

# --- Bloco de Gestão de Cardápio ---
elif choice == "Cardápio":
    st.header("🍽️ Gestão de Cardápio")
    # --- Formulário para Adicionar Novo Item ao Cardápio ---
    with st.form("add_item"):
        nome = st.text_input("Nome do item")
        categorias = ["Entradas", "Prato Principal", "Sobremesas", "Bebidas"]
        categoria = st.selectbox("Categoria", categorias)         
        descricao = st.text_area("Descrição")
        preco = st.number_input("Preço", min_value=0.0, step=0.5)
        if st.form_submit_button("Adicionar"):
            if nome.strip() != "": # Validação simples para nome não vazio.
                novo_id = len(ItemCardapioService.lista_cardapio) + 1
                novo_item = ItemCardapio(novo_id, nome, categoria, preco, descricao, True)
                ItemCardapioService.adicionar(novo_item)
                st.success(f"Item '{nome}' adicionado com sucesso!")

    # Carrega e exibe os itens do cardápio existentes.
    ItemCardapioService.carregar()
    cardapio = ItemCardapioService.listar_cardapio()
    if cardapio:
        # Exibe cada item do cardápio em um `expander`.
        for item in cardapio:
            with st.expander(f"{item['nome']} - R$ {item['preco']:.2f}"):
                st.write(f"📂 Categoria: {item['categoria']}")
                st.write(f"📝 Descrição: {item['descricao']}")
                # Checkbox para controlar a disponibilidade do item.
                disponivel = st.checkbox("Disponível", value=item.get("disponivel"), key=f"disp_{item['id']}")
                if st.button("Salvar", key=f"save_{item['id']}"):
                    msg = ItemCardapioService.atualizar_disponibilidade(item["id"], disponivel)
                    st.success(msg)
    else:
        st.info("Nenhum item cadastrado ainda.")

# --- Bloco de Feedbacks ---
elif choice == "Feedbacks":
    st.header("📝 Feedbacks dos Clientes")

    feedbacks = carregar_feedbacks() # Carrega os feedbacks da planilha.

    if feedbacks:
        # --- Gráfico de Distribuição das Avaliações de Atendimento ---
        from collections import Counter
        # Filtra avaliações válidas para o gráfico.
        avaliacoes = [fb["avaliacao_atendimento"] for fb in feedbacks if isinstance(fb["avaliacao_atendimento"], int) and fb["avaliacao_atendimento"] > 0]
        contagem = Counter(avaliacoes)
        st.subheader("📊 Distribuição das Avaliações de Atendimento")
        if contagem:
            # Exibe um gráfico de barras com a contagem de cada nota.
            st.bar_chart(dict(sorted(contagem.items()))) 
        else:
            st.info("Nenhuma avaliação de atendimento registrada.")

        # --- Detalhes dos Feedbacks ---
        st.subheader("📋 Detalhes dos Feedbacks")
        # Itera sobre cada feedback para exibir seus detalhes.
        for fb in feedbacks:
            with st.expander(f"{fb['nome']} - {fb['data']}"):
                st.write(f"⭐ **Atendimento:** {fb['avaliacao_atendimento']}")
                st.write(f"🪑 **Limpeza e Conforto:** {fb['avaliacao_limpeza_conforto']}")
                st.write(f"⏱️ **Tempo de Espera:** {fb['avaliacao_tempo_espera']}")
                st.write(f"💰 **Valor x Qualidade:** {fb['avaliacao_valor_qualidade']}")
                st.write(f"🍽️ **Pedido atendeu expectativas?** {fb['pedido_atendeu_expectativas']}")
                comentario = fb.get("comentario", "")
                if comentario:
                    st.write(f"💬 **Comentário:** {comentario}")
    else:
        st.info("Nenhum feedback disponível no momento.")

# --- Bloco do Mapa de Mesas ---
elif choice == "Mapa de Mesas":
    st.header("🪑 Mapa de Mesas")
    # Cria uma lista de mesas com status aleatórios para simulação.
    mesas = [{"numero": i, "status": random.choice(["livre", "ocupada", "reservada"])} for i in range(1, 13)]
    cols = st.columns(3) # Cria 3 colunas para exibir as mesas.
    # Itera sobre as mesas e as exibe em um layout de grid.
    for i, mesa in enumerate(mesas):
        with cols[i % 3]: # Usa o operador módulo para distribuir as mesas entre as colunas.
            # Define a cor de fundo do cartão da mesa com base no seu status.
            cor = "#4CAF50" if mesa["status"] == "livre" else "#F44336" if mesa["status"] == "ocupada" else "#FFC107"
            # Usa `st.markdown` com `unsafe_allow_html=True` para renderizar HTML customizado.
            st.markdown(
                f"""
                <div style='background-color: {cor}; padding: 10px; margin: 5px; border-radius: 5px; text-align: center;'>
                    Mesa {mesa['numero']}<br>
                    {mesa['status'].capitalize()}
                </div>
                """,
                unsafe_allow_html=True
            )

# --- Bloco de Eventos ---
elif choice == "Eventos":
    st.header("🎉 Eventos")
    EventoService.carregar()  # Carrega a lista de eventos.
    eventos = EventoService.lista_eventos  # obtém lista de objetos Evento

    # Formulário para adicionar novo evento
    with st.expander("➕ Adicionar Novo Evento"):
        with st.form("form_add_evento"):
            nome = st.text_input("Nome do Evento")
            data = st.date_input("Data do Evento")
            horario = st.time_input("Horário do Evento")
            descricao = st.text_area("Descrição")
            status = st.selectbox("Status", ["pendente", "confirmado", "cancelado"])
            submitted = st.form_submit_button("Adicionar Evento")

            if submitted:
                if nome.strip() == "":
                    st.error("O nome do evento é obrigatório.")
                else:
                    novo_id = max([ev.id for ev in eventos], default=0) + 1
                    novo_evento = Evento(
                        id=novo_id,
                        nome=nome.strip(),
                        data=data.strftime("%Y-%m-%d"),
                        horario=horario.strftime("%H:%M"),
                        descricao=descricao.strip(),
                        status=status
                    )
                    EventoService.adicionar(novo_evento)
                    st.success(f"Evento '{nome}' adicionado com sucesso!")
                    EventoService.carregar()  # recarrega lista atualizada
                    eventos = EventoService.lista_eventos

    st.markdown("---")

    # Listar eventos existentes com opção de editar
    if eventos:
        for ev in eventos:
            with st.expander(f"{ev.nome} - {ev.data} {ev.horario}"):
                with st.form(f"form_edit_evento_{ev.id}"):
                    nome_edit = st.text_input("Nome do Evento", value=ev.nome)
                    data_edit = st.date_input("Data do Evento", value=datetime.strptime(ev.data, "%Y-%m-%d"))
                    horario_edit = st.time_input("Horário do Evento", value=datetime.strptime(ev.horario, "%H:%M"))
                    descricao_edit = st.text_area("Descrição", value=ev.descricao)
                    status_edit = st.selectbox("Status", ["pendente", "confirmado", "cancelado"], index=["pendente", "confirmado", "cancelado"].index(ev.status))

                    submitted_edit = st.form_submit_button("Salvar Alterações")
                    excluir = st.form_submit_button("Excluir Evento")

                    if submitted_edit:
                        ev.atualizar_informacoes(
                            nome=nome_edit.strip(),
                            data=data_edit.strftime("%Y-%m-%d"),
                            horario=horario_edit.strftime("%H:%M"),
                            descricao=descricao_edit.strip(),
                            status=status_edit
                        )
                        EventoService.salvar()
                        st.success("Evento atualizado com sucesso!")

                    if excluir:
                        EventoService.remover(ev.id)
                        st.success("Evento excluído com sucesso!")
                        EventoService.carregar()
    else:
        st.info("Nenhum evento cadastrado ainda.")

# --- Bloco de Relatórios ---
elif choice == "Relatórios":
    st.header("📈 Relatórios")
    if st.button("Gerar Relatório CSV"):
        # Exemplo de dados para o relatório CSV.
        data = [["Data", "Reservas"], ["10/05", 15], ["11/05", 12]] 
        # Botão de download para o arquivo CSV.
        st.download_button(
            "Baixar CSV",
            # Converte a lista de listas para uma string formatada em CSV.
            "\n".join([",".join(map(str, row)) for row in data]), 
            "relatorio.csv" # Nome do arquivo para download.
        )