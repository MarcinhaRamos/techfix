import os

import gradio as gr
from dotenv import load_dotenv
from supabase import create_client, Client


# Carrega as variáveis do arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# Verifica se as credenciais foram configuradas
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL e SUPABASE_KEY precisam estar configuradas no arquivo .env."
    )


# Cria a conexão com o Supabase
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

def cadastrar_ordem(
    nome,
    endereco,
    email,
    celular,
    modelo_computador,
    problema
):
    # Remove espaços desnecessários
    nome = nome.strip()
    endereco = endereco.strip()
    email = email.strip().lower()
    celular = celular.strip()
    modelo_computador = modelo_computador.strip()
    problema = problema.strip()

    # Validação dos campos obrigatórios
    if not nome:
        return "❌ Informe o nome do cliente.", ""

    if not endereco:
        return "❌ Informe o endereço.", ""

    if not email:
        return "❌ Informe o e-mail.", ""

    if not celular:
        return "❌ Informe o celular/WhatsApp.", ""

    if not modelo_computador:
        return "❌ Informe o modelo do computador.", ""

    if not problema:
        return "❌ Informe o problema relatado.", ""

    # Validação simples do e-mail
    if "@" not in email or "." not in email.split("@")[-1]:
        return "❌ Informe um e-mail válido.", ""

    # Mantém somente os números do celular
    celular = "".join(filter(str.isdigit, celular))

    if len(celular) < 10 or len(celular) > 13:
        return "❌ O celular deve ter entre 10 e 13 dígitos.", ""

    try:
        # Procura se o cliente já existe pelo e-mail
        cliente_response = (
            supabase
            .table("clientes")
            .select("id")
            .eq("email", email)
            .execute()
        )

        if cliente_response.data:
            # Cliente já existe
            cliente_id = cliente_response.data[0]["id"]

        else:
            # Cliente ainda não existe: cria um novo
            novo_cliente = (
                supabase
                .table("clientes")
                .insert({
                    "nome": nome,
                    "endereco": endereco,
                    "email": email,
                    "celular_whatsapp": celular
                })
                .execute()
            )

            if not novo_cliente.data:
                return "❌ Não foi possível cadastrar o cliente.", ""

            cliente_id = novo_cliente.data[0]["id"]

        # Cria a ordem de serviço
        nova_os = (
            supabase
            .table("ordens_servico")
            .insert({
                "cliente_id": cliente_id,
                "modelo_computador": modelo_computador,
                "problema_relatado": problema,
                "status": "Aberto"
            })
            .execute()
        )

        if not nova_os.data:
            return "❌ Não foi possível cadastrar a ordem de serviço.", ""

        numero_os = nova_os.data[0]["id"]

        mensagem = (
            f"✅ Cadastro realizado com sucesso!\n\n"
            f"Cliente: {nome}\n"
            f"Ordem de Serviço: #{numero_os}\n"
            f"Status: Aberto"
        )

        return mensagem, ""

    except Exception as erro:
        return (
            f"❌ Ocorreu um erro ao realizar o cadastro: {erro}",
            ""
        )

       # =========================================================
# INTERFACE GRADIO
# =========================================================

with gr.Blocks(title="TechFix Informática") as app:

    gr.Markdown(
        """
        # 🛠️ TechFix Informática
        ### Cadastro de Cliente e Ordem de Serviço
        """
    )

    with gr.Row():

        with gr.Column():
            nome = gr.Textbox(
                label="Nome",
                placeholder="Digite o nome do cliente"
            )

            endereco = gr.Textbox(
                label="Endereço",
                placeholder="Digite o endereço"
            )

            email = gr.Textbox(
                label="E-mail",
                placeholder="Digite o e-mail"
            )

            celular = gr.Textbox(
                label="Celular / WhatsApp",
                placeholder="Digite somente os números"
            )

        with gr.Column():
            modelo_computador = gr.Textbox(
                label="Modelo do Computador",
                placeholder="Ex.: Dell Inspiron 15"
            )

            problema = gr.Textbox(
                label="Problema",
                placeholder="Descreva o problema apresentado",
                lines=5
            )

    with gr.Row():

        cadastrar = gr.Button(
            "Cadastrar",
            variant="primary"
        )

        limpar = gr.Button(
            "Limpar"
        )

    mensagem = gr.Textbox(
        label="Resultado",
        interactive=False,
        lines=5
    )

    cadastrar.click(
        fn=cadastrar_ordem,
        inputs=[
            nome,
            endereco,
            email,
            celular,
            modelo_computador,
            problema
        ],
        outputs=[
            mensagem,
            problema
        ]
    )

    limpar.click(
        fn=lambda: ("", "", "", "", "", "", ""),
        inputs=[],
        outputs=[
            nome,
            endereco,
            email,
            celular,
            modelo_computador,
            problema,
            mensagem
        ]
    )


# =========================================================
# EXECUÇÃO DO APLICATIVO
# =========================================================

if __name__ == "__main__":
    app.launch(share=True) 