import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client


st.set_page_config(
    page_title="TechFix Informática",
    page_icon="🛠️",
    layout="wide"
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error(
        "SUPABASE_URL e SUPABASE_KEY precisam estar configuradas "
        "no arquivo .env."
    )
    st.stop()

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

st.title("🛠️ TechFix Informática")
st.write("Painel Administrativo")


STATUS_DISPONIVEIS = [
    "Aberto",
    "Em análise",
    "Aguardando peça",
    "Concluído",
    "Entregue"
]


aba_consultar, aba_cadastrar, aba_editar, aba_indicadores = st.tabs(
    [
        "📋 CONSULTAR",
        "➕ CADASTRAR",
        "✏️ EDITAR / EXCLUIR",
        "📊 INDICADORES"
    ]
)


with aba_consultar:

    st.header("Consultar Ordens de Serviço")

    try:

        resposta_os = (
            supabase
            .table("ordens_servico")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        ordens = resposta_os.data or []

        resposta_clientes = (
            supabase
            .table("clientes")
            .select("*")
            .order("nome")
            .execute()
        )

        clientes = resposta_clientes.data or []

        clientes_por_id = {
            cliente["id"]: cliente
            for cliente in clientes
        }

        dados_tabela = []

        for ordem in ordens:

            cliente = clientes_por_id.get(
                ordem.get("cliente_id"),
                {}
            )

            dados_tabela.append(
                {
                    "OS": ordem.get("id"),
                    "Cliente": cliente.get("nome", ""),
                    "E-mail": cliente.get("email", ""),
                    "Celular": cliente.get("celular_whatsapp", ""),
                    "Modelo": ordem.get("modelo_computador", ""),
                    "Problema": ordem.get("problema_relatado", ""),
                    "Status": ordem.get("status", ""),
                    "Data de abertura": ordem.get("data_abertura", "")
                }
            )

        st.sidebar.header("🔎 Filtros")

        nomes_clientes = sorted(
            set(
                item["Cliente"]
                for item in dados_tabela
                if item["Cliente"]
            )
        )

        emails_clientes = sorted(
            set(
                item["E-mail"]
                for item in dados_tabela
                if item["E-mail"]
            )
        )

        filtro_cliente = st.sidebar.selectbox(
            "Cliente",
            ["Todos"] + nomes_clientes
        )

        filtro_email = st.sidebar.selectbox(
            "E-mail",
            ["Todos"] + emails_clientes
        )

        filtro_status = st.sidebar.selectbox(
            "Status",
            ["Todos"] + STATUS_DISPONIVEIS
        )

        dados_filtrados = dados_tabela

        if filtro_cliente != "Todos":

            dados_filtrados = [
                item
                for item in dados_filtrados
                if item["Cliente"] == filtro_cliente
            ]

        if filtro_email != "Todos":

            dados_filtrados = [
                item
                for item in dados_filtrados
                if item["E-mail"] == filtro_email
            ]

        if filtro_status != "Todos":

            dados_filtrados = [
                item
                for item in dados_filtrados
                if item["Status"] == filtro_status
            ]

        if not ordens:

            st.info(
                "Nenhuma ordem de serviço cadastrada."
            )

        else:

            st.write(
                f"Ordens encontradas: **{len(dados_filtrados)}**"
            )

            st.dataframe(
                dados_filtrados,
                use_container_width=True
            )

    except Exception as erro:

        st.error(
            f"Erro ao consultar os dados: {erro}"
        )


with aba_cadastrar:

    st.header("Cadastrar")

    try:

        st.subheader("👤 Novo Cliente")

        nome_cliente = st.text_input(
            "Nome",
            placeholder="Nome completo"
        )

        endereco_cliente = st.text_input(
            "Endereço",
            placeholder="Rua, número, bairro"
        )

        email_cliente = st.text_input(
            "E-mail",
            placeholder="cliente@email.com"
        )

        celular_cliente = st.text_input(
            "Celular / WhatsApp",
            placeholder="Ex.: 31999999999"
        )

        cadastrar_cliente = st.button(
            "Cadastrar Cliente"
        )

        if cadastrar_cliente:

            if not nome_cliente.strip():

                st.error(
                    "Informe o nome do cliente."
                )

            elif not endereco_cliente.strip():

                st.error(
                    "Informe o endereço do cliente."
                )

            elif not email_cliente.strip():

                st.error(
                    "Informe o e-mail do cliente."
                )

            elif not celular_cliente.strip():

                st.error(
                    "Informe o celular/WhatsApp do cliente."
                )

            else:

                try:

                    novo_cliente = {
                        "nome": nome_cliente.strip(),
                        "endereco": endereco_cliente.strip(),
                        "email": email_cliente.strip(),
                        "celular_whatsapp": celular_cliente.strip()
                    }

                    resposta_cliente = (
                        supabase
                        .table("clientes")
                        .insert(novo_cliente)
                        .execute()
                    )

                    if resposta_cliente.data:

                        st.success(
                            "✅ Cliente cadastrado com sucesso!"
                        )

                    else:

                        st.error(
                            "Não foi possível cadastrar o cliente."
                        )

                except Exception as erro:

                    st.error(
                        f"Erro ao cadastrar cliente: {erro}"
                    )

        st.divider()

        st.subheader("🛠️ Nova Ordem de Serviço")

        resposta_clientes = (
            supabase
            .table("clientes")
            .select("id, nome, email")
            .order("nome")
            .execute()
        )

        clientes = resposta_clientes.data or []

        if not clientes:

            st.warning(
                "Não existem clientes cadastrados."
            )

        else:

            opcoes_clientes = [
                f"{cliente['nome']} - {cliente['email']}"
                for cliente in clientes
            ]

            cliente_escolhido = st.selectbox(
                "Cliente",
                opcoes_clientes
            )

            cliente = next(
                cliente
                for cliente in clientes
                if (
                    f"{cliente['nome']} - "
                    f"{cliente['email']}"
                ) == cliente_escolhido
            )

            modelo_computador = st.text_input(
                "Modelo do Computador",
                placeholder="Ex.: Dell Inspiron 15"
            )

            problema_relatado = st.text_area(
                "Problema Relatado",
                placeholder=(
                    "Descreva o problema apresentado "
                    "pelo cliente."
                )
            )

            cadastrar_os = st.button(
                "Cadastrar Ordem de Serviço"
            )

            if cadastrar_os:

                if not modelo_computador.strip():

                    st.error(
                        "Informe o modelo do computador."
                    )

                elif not problema_relatado.strip():

                    st.error(
                        "Informe o problema relatado."
                    )

                else:

                    try:

                        nova_os = {
                            "cliente_id": cliente["id"],
                            "modelo_computador": modelo_computador.strip(),
                            "problema_relatado": problema_relatado.strip(),
                            "status": "Aberto"
                        }

                        resposta = (
                            supabase
                            .table("ordens_servico")
                            .insert(nova_os)
                            .execute()
                        )

                        if resposta.data:

                            numero_os = resposta.data[0]["id"]

                            st.success(
                                "✅ Ordem de Serviço cadastrada "
                                "com sucesso! "
                                f"Número da OS: {numero_os}"
                            )

                        else:

                            st.error(
                                "Não foi possível cadastrar "
                                "a Ordem de Serviço."
                            )

                    except Exception as erro:

                        st.error(
                            f"Erro ao cadastrar a OS: {erro}"
                        )

    except Exception as erro:

        st.error(
            f"Erro ao carregar a tela de cadastro: {erro}"
        )


with aba_editar:

    st.header("Editar / Excluir")

    try:

        resposta_os = (
            supabase
            .table("ordens_servico")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        ordens = resposta_os.data or []

        resposta_clientes = (
            supabase
            .table("clientes")
            .select("*")
            .order("nome")
            .execute()
        )

        clientes = resposta_clientes.data or []

        clientes_por_id = {
            cliente["id"]: cliente
            for cliente in clientes
        }

        if not ordens:

            st.info(
                "Não existem ordens de serviço cadastradas."
            )

        else:

            opcoes_os = []

            for ordem in ordens:

                cliente = clientes_por_id.get(
                    ordem.get("cliente_id"),
                    {}
                )

                nome_cliente = cliente.get(
                    "nome",
                    "Cliente não encontrado"
                )

                opcoes_os.append(
                    f"OS {ordem['id']} - {nome_cliente}"
                )

            os_selecionada = st.selectbox(
                "Selecione a Ordem de Serviço",
                opcoes_os
            )

            numero_os = int(
                os_selecionada
                .split(" - ")[0]
                .replace("OS ", "")
            )

            ordem_selecionada = next(
                ordem
                for ordem in ordens
                if ordem["id"] == numero_os
            )

            cliente_selecionado = clientes_por_id.get(
                ordem_selecionada.get("cliente_id"),
                {}
            )

            st.subheader(
                f"OS {numero_os}"
            )

            st.write(
                f"**Modelo:** "
                f"{ordem_selecionada.get('modelo_computador', '')}"
            )

            st.write(
                f"**Problema:** "
                f"{ordem_selecionada.get('problema_relatado', '')}"
            )

            st.divider()

            st.subheader("✏️ Editar informações")

            status_atual = ordem_selecionada.get(
                "status",
                "Aberto"
            )

            if status_atual not in STATUS_DISPONIVEIS:

                status_atual = "Aberto"

            novo_status = st.selectbox(
                "Status",
                STATUS_DISPONIVEIS,
                index=STATUS_DISPONIVEIS.index(status_atual)
            )

            novo_endereco = st.text_input(
                "Endereço",
                value=cliente_selecionado.get(
                    "endereco",
                    ""
                )
            )

            novo_email = st.text_input(
                "E-mail",
                value=cliente_selecionado.get(
                    "email",
                    ""
                )
            )

            novo_celular = st.text_input(
                "Celular / WhatsApp",
                value=cliente_selecionado.get(
                    "celular_whatsapp",
                    ""
                )
            )

            salvar_alteracoes = st.button(
                "💾 Salvar alterações"
            )

            if salvar_alteracoes:

                try:

                    (
                        supabase
                        .table("clientes")
                        .update(
                            {
                                "endereco": novo_endereco.strip(),
                                "email": novo_email.strip(),
                                "celular_whatsapp": novo_celular.strip()
                            }
                        )
                        .eq(
                            "id",
                            cliente_selecionado["id"]
                        )
                        .execute()
                    )

                    (
                        supabase
                        .table("ordens_servico")
                        .update(
                            {
                                "status": novo_status
                            }
                        )
                        .eq(
                            "id",
                            numero_os
                        )
                        .execute()
                    )

                    st.success(
                        f"✅ OS {numero_os} atualizada "
                        "com sucesso!"
                    )

                except Exception as erro:

                    st.error(
                        f"Erro ao salvar as alterações: {erro}"
                    )

            st.divider()

            st.subheader(
                "🗑️ Excluir Ordem de Serviço"
            )

            confirmar_exclusao_os = st.checkbox(
                "Confirmo que desejo excluir esta "
                "Ordem de Serviço."
            )

            if confirmar_exclusao_os:

                excluir_os = st.button(
                    "🗑️ Excluir Ordem de Serviço"
                )

                if excluir_os:

                    try:

                        (
                            supabase
                            .table("ordens_servico")
                            .delete()
                            .eq(
                                "id",
                                numero_os
                            )
                            .execute()
                        )

                        st.success(
                            f"✅ OS {numero_os} excluída "
                            "com sucesso!"
                        )

                    except Exception as erro:

                        st.error(
                            "Erro ao excluir a Ordem de "
                            f"Serviço: {erro}"
                        )

        st.divider()

        st.subheader(
            "👤🗑️ Excluir Cliente"
        )

        if not clientes:

            st.info(
                "Não existem clientes cadastrados."
            )

        else:

            opcoes_clientes_exclusao = [
                (
                    f"{cliente['nome']} - "
                    f"{cliente['email']}"
                )
                for cliente in clientes
            ]

            cliente_excluir_texto = st.selectbox(
                "Selecione o cliente",
                opcoes_clientes_exclusao,
                key="cliente_excluir"
            )

            cliente_excluir = next(
                cliente
                for cliente in clientes
                if (
                    f"{cliente['nome']} - "
                    f"{cliente['email']}"
                ) == cliente_excluir_texto
            )

            st.warning(
                "A exclusão do cliente também excluirá "
                "as Ordens de Serviço relacionadas."
            )

            confirmar_exclusao_cliente = st.checkbox(
                "Confirmo que desejo excluir este cliente.",
                key="confirmar_exclusao_cliente"
            )

            if confirmar_exclusao_cliente:

                excluir_cliente = st.button(
                    "🗑️ Excluir Cliente",
                    key="excluir_cliente"
                )

                if excluir_cliente:

                    try:

                        (
                            supabase
                            .table("clientes")
                            .delete()
                            .eq(
                                "id",
                                cliente_excluir["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Cliente excluído com sucesso!"
                        )

                    except Exception as erro:

                        st.error(
                            f"Erro ao excluir cliente: {erro}"
                        )

    except Exception as erro:

        st.error(
            f"Erro ao carregar a tela de edição: {erro}"
        )


with aba_indicadores:

    st.header("📊 Indicadores")

    try:

        resposta_os = (
            supabase
            .table("ordens_servico")
            .select("*")
            .execute()
        )

        ordens = resposta_os.data or []

        resposta_clientes = (
            supabase
            .table("clientes")
            .select("*")
            .execute()
        )

        clientes = resposta_clientes.data or []

        total_clientes = len(clientes)

        total_os = len(ordens)

        os_abertas = sum(
            1
            for ordem in ordens
            if ordem.get("status") == "Aberto"
        )

        os_concluidas = sum(
            1
            for ordem in ordens
            if ordem.get("status") == "Concluído"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "👤 Total de clientes",
                total_clientes
            )

        with col2:

            st.metric(
                "🛠️ Total de OS",
                total_os
            )

        with col3:

            st.metric(
                "🟢 OS abertas",
                os_abertas
            )

        with col4:

            st.metric(
                "✅ OS concluídas",
                os_concluidas
            )

        st.divider()

        st.subheader(
            "Ordens de Serviço por Status"
        )

        quantidade_por_status = {}

        for status in STATUS_DISPONIVEIS:

            quantidade_por_status[status] = sum(
                1
                for ordem in ordens
                if ordem.get("status") == status
            )

        st.bar_chart(
            quantidade_por_status
        )

    except Exception as erro:

        st.error(
            f"Erro ao carregar os indicadores: {erro}"
        )
        