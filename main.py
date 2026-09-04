from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock

import json
import os
from datetime import datetime


ARQUIVO_AGENDAMENTOS = "agendamentos.json"


# ============================================================
# CORES
# ============================================================

FUNDO = (0.055, 0.055, 0.08, 1)
CARTAO = (0.09, 0.09, 0.14, 1)
CARTAO_2 = (0.12, 0.12, 0.18, 1)

BRANCO = (0.95, 0.95, 0.98, 1)
CINZA = (0.62, 0.63, 0.70, 1)

ROXO = (0.45, 0.25, 0.90, 1)
ROXO_CLARO = (0.58, 0.38, 1, 1)

VERDE = (0.18, 0.75, 0.42, 1)
VERMELHO = (0.88, 0.22, 0.25, 1)
AZUL = (0.20, 0.50, 0.95, 1)


# ============================================================
# BOTÃO PERSONALIZADO
# ============================================================

class BotaoModerno(Button):

    def __init__(
        self,
        cor=ROXO,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.cor = cor

        self.color = BRANCO
        self.font_size = 17
        self.bold = True

        with self.canvas.before:

            Color(*self.cor)

            self.retangulo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[14]
            )

        self.bind(
            pos=self.atualizar_retangulo,
            size=self.atualizar_retangulo
        )

    def atualizar_retangulo(self, *args):

        self.retangulo.pos = self.pos
        self.retangulo.size = self.size


# ============================================================
# CARTÃO
# ============================================================

class Cartao(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.padding = 18
        self.spacing = 8

        with self.canvas.before:

            Color(*CARTAO)

            self.retangulo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18]
            )

        self.bind(
            pos=self.atualizar_retangulo,
            size=self.atualizar_retangulo
        )

    def atualizar_retangulo(self, *args):

        self.retangulo.pos = self.pos
        self.retangulo.size = self.size


# ============================================================
# APLICATIVO
# ============================================================

class KwaiAutomatico(App):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.programa_rodando = False

        self.videos_selecionados = []

    # ========================================================
    # ARQUIVO
    # ========================================================

    def carregar_agendamentos(self):

        if not os.path.exists(
            ARQUIVO_AGENDAMENTOS
        ):

            return []

        try:

            with open(
                ARQUIVO_AGENDAMENTOS,
                "r",
                encoding="utf-8"
            ) as arquivo:

                return json.load(arquivo)

        except Exception:

            return []

    def salvar_arquivo(
        self,
        agendamentos
    ):

        with open(
            ARQUIVO_AGENDAMENTOS,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                agendamentos,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    # ========================================================
    # INICIALIZAÇÃO
    # ========================================================

    def build(self):

        self.root = BoxLayout(
            orientation="vertical"
        )

        with self.root.canvas.before:

            Color(*FUNDO)

            self.fundo = RoundedRectangle(
                pos=self.root.pos,
                size=self.root.size
            )

        self.root.bind(
            pos=self.atualizar_fundo,
            size=self.atualizar_fundo
        )

        return self.root

    def atualizar_fundo(self, *args):

        self.fundo.pos = self.root.pos
        self.fundo.size = self.root.size

    def on_start(self):

        self.mostrar_principal()

    # ========================================================
    # TÍTULO
    # ========================================================

    def criar_titulo(
        self,
        texto,
        tamanho=24
    ):

        return Label(
            text=texto,
            color=BRANCO,
            font_size=tamanho,
            bold=True,
            size_hint_y=None,
            height=45
        )

    # ========================================================
    # PRINCIPAL
    # ========================================================

    def mostrar_principal(
        self,
        *args
    ):

        self.root.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        # ----------------------------------------------------
        # CABEÇALHO
        # ----------------------------------------------------

        cabecalho = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=95,
            spacing=3
        )

        titulo = Label(
            text="Kwai Automático",
            color=BRANCO,
            font_size=30,
            bold=True
        )

        subtitulo = Label(
            text="Gerenciador de vídeos e agendamentos",
            color=CINZA,
            font_size=14
        )

        cabecalho.add_widget(titulo)
        cabecalho.add_widget(subtitulo)

        principal.add_widget(cabecalho)

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status_cartao = Cartao(
            size_hint_y=None,
            height=105
        )

        status_titulo = Label(
            text="STATUS DO PROGRAMA",
            color=CINZA,
            font_size=13,
            bold=True,
            size_hint_y=None,
            height=25,
            halign="left"
        )

        status = Label(
            text=self.obter_status(),
            color=(
                VERDE
                if self.programa_rodando
                else CINZA
            ),
            font_size=23,
            bold=True
        )

        status_cartao.add_widget(
            status_titulo
        )

        status_cartao.add_widget(
            status
        )

        principal.add_widget(
            status_cartao
        )

        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        agendamentos = self.carregar_agendamentos()

        resumo = GridLayout(
            cols=2,
            spacing=12,
            size_hint_y=None,
            height=95
        )

        videos_cartao = Cartao()

        videos_numero = Label(
            text=str(
                len(
                    self.videos_selecionados
                )
            ),
            color=ROXO_CLARO,
            font_size=27,
            bold=True
        )

        videos_texto = Label(
            text="Vídeos selecionados",
            color=CINZA,
            font_size=13
        )

        videos_cartao.add_widget(
            videos_numero
        )

        videos_cartao.add_widget(
            videos_texto
        )

        agenda_cartao = Cartao()

        agenda_numero = Label(
            text=str(
                len(agendamentos)
            ),
            color=AZUL,
            font_size=27,
            bold=True
        )

        agenda_texto = Label(
            text="Agendamentos",
            color=CINZA,
            font_size=13
        )

        agenda_cartao.add_widget(
            agenda_numero
        )

        agenda_cartao.add_widget(
            agenda_texto
        )

        resumo.add_widget(
            videos_cartao
        )

        resumo.add_widget(
            agenda_cartao
        )

        principal.add_widget(
            resumo
        )

        # ----------------------------------------------------
        # CONTROLE
        # ----------------------------------------------------

        controle = Label(
            text="CONTROLE",
            color=CINZA,
            font_size=13,
            bold=True,
            size_hint_y=None,
            height=30
        )

        principal.add_widget(
            controle
        )

        botoes = GridLayout(
            cols=2,
            spacing=12,
            size_hint_y=None,
            height=65
        )

        iniciar = BotaoModerno(
            text="▶  INICIAR",
            cor=VERDE
        )

        iniciar.bind(
            on_press=self.iniciar_programa
        )

        parar = BotaoModerno(
            text="■  PARAR",
            cor=VERMELHO
        )

        parar.bind(
            on_press=self.parar_programa
        )

        botoes.add_widget(
            iniciar
        )

        botoes.add_widget(
            parar
        )

        principal.add_widget(
            botoes
        )

        # ----------------------------------------------------
        # VÍDEOS
        # ----------------------------------------------------

        videos_label = Label(
            text="VÍDEOS",
            color=CINZA,
            font_size=13,
            bold=True,
            size_hint_y=None,
            height=30
        )

        principal.add_widget(
            videos_label
        )

        selecionar = BotaoModerno(
            text="🎬  SELECIONAR VÍDEOS",
            cor=ROXO,
            size_hint_y=None,
            height=60
        )

        selecionar.bind(
            on_press=self.selecionar_videos
        )

        principal.add_widget(
            selecionar
        )

        pasta = BotaoModerno(
            text="📁  SELECIONAR PASTA",
            cor=CARTAO_2,
            size_hint_y=None,
            height=60
        )

        principal.add_widget(
            pasta
        )

        pasta.bind(
            on_press=self.selecionar_pasta
        )

        # ----------------------------------------------------
        # AGENDAMENTOS
        # ----------------------------------------------------

        agenda = BotaoModerno(
            text="🕐  VER AGENDAMENTOS",
            cor=AZUL,
            size_hint_y=None,
            height=60
        )

        agenda.bind(
            on_press=self.mostrar_agendamentos
        )

        principal.add_widget(
            agenda
        )

        self.root.add_widget(
            principal
        )

    # ========================================================
    # STATUS
    # ========================================================

    def obter_status(self):

        if self.programa_rodando:

            return "●  Programa em execução"

        return "○  Programa parado"

    # ========================================================
    # INICIAR
    # ========================================================

    def iniciar_programa(
        self,
        *args
    ):

        if self.programa_rodando:

            self.mostrar_mensagem(
                "O programa já está em execução."
            )

            return

        self.programa_rodando = True

        Clock.schedule_interval(
            self.verificar_agendamentos,
            30
        )

        self.mostrar_mensagem(
            "PROGRAMA INICIADO\n\n"
            "O sistema está monitorando "
            "seus agendamentos.\n\n"
            "Nesta versão, o monitoramento "
            "funciona enquanto o aplicativo "
            "estiver aberto."
        )

    # ========================================================
    # PARAR
    # ========================================================

    def parar_programa(
        self,
        *args
    ):

        self.programa_rodando = False

        Clock.unschedule(
            self.verificar_agendamentos
        )

        self.mostrar_mensagem(
            "PROGRAMA PARADO\n\n"
            "O monitoramento dos agendamentos "
            "foi interrompido."
        )

    # ========================================================
    # VERIFICAR
    # ========================================================

    def verificar_agendamentos(
        self,
        dt
    ):

        if not self.programa_rodando:

            return

        agora = datetime.now()

        horario_atual = agora.strftime(
            "%H:%M"
        )

        agendamentos = (
            self.carregar_agendamentos()
        )

        alterado = False

        for agendamento in agendamentos:

            if agendamento.get(
                "status"
            ) != "agendado":

                continue

            if agendamento.get(
                "horario"
            ) == horario_atual:

                agendamento[
                    "status"
                ] = "processando"

                alterado = True

        if alterado:

            self.salvar_arquivo(
                agendamentos
            )

    # ========================================================
    # SELECIONAR VÍDEOS
    # ========================================================

    def selecionar_videos(
        self,
        *args
    ):

        layout = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=12
        )

        layout.add_widget(
            self.criar_titulo(
                "Selecionar vídeos"
            )
        )

        arquivos = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=[
                "*.mp4",
                "*.mov",
                "*.avi",
                "*.mkv",
                "*.webm"
            ],
            multiselect=True
        )

        layout.add_widget(
            arquivos
        )

        confirmar = BotaoModerno(
            text="✓  ADICIONAR VÍDEOS",
            cor=VERDE,
            size_hint_y=None,
            height=60
        )

        confirmar.bind(
            on_press=lambda x:
            self.mostrar_videos(
                arquivos.selection
            )
        )

        layout.add_widget(
            confirmar
        )

        voltar = Button(
            text="Voltar",
            color=CINZA,
            background_color=(
                0,
                0,
                0,
                0
            ),
            size_hint_y=None,
            height=45
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(
            voltar
        )

        self.root.clear_widgets()

        self.root.add_widget(
            layout
        )

    # ========================================================
    # SELECIONAR PASTA
    # ========================================================

    def selecionar_pasta(
        self,
        *args
    ):

        layout = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=12
        )

        layout.add_widget(
            self.criar_titulo(
                "Selecionar pasta"
            )
        )

        arquivos = FileChooserListView(
            path=os.path.expanduser("~"),
            dirselect=True
        )

        layout.add_widget(
            arquivos
        )

        confirmar = BotaoModerno(
            text="✓  USAR ESTA PASTA",
            cor=VERDE,
            size_hint_y=None,
            height=60
        )

        confirmar.bind(
            on_press=lambda x:
            self.confirmar_pasta(
                arquivos.selection
            )
        )

        layout.add_widget(
            confirmar
        )

        voltar = Button(
            text="Voltar",
            color=CINZA,
            background_color=(
                0,
                0,
                0,
                0
            ),
            size_hint_y=None,
            height=45
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(
            voltar
        )

        self.root.clear_widgets()

        self.root.add_widget(
            layout
        )

    # ========================================================
    # CONFIRMAR PASTA
    # ========================================================

    def confirmar_pasta(
        self,
        selecao
    ):

        if not selecao:

            self.mostrar_mensagem(
                "Nenhuma pasta foi selecionada."
            )

            return

        pasta = selecao[0]

        if not os.path.isdir(
            pasta
        ):

            self.mostrar_mensagem(
                "Selecione uma pasta."
            )

            return

        extensoes = (
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".webm"
        )

        videos = []

        try:

            for nome in os.listdir(
                pasta
            ):

                caminho = os.path.join(
                    pasta,
                    nome
                )

                if os.path.isfile(
                    caminho
                ):

                    if nome.lower().endswith(
                        extensoes
                    ):

                        videos.append(
                            caminho
                        )

        except Exception as erro:

            self.mostrar_mensagem(
                "Erro ao acessar a pasta.\n\n"
                f"{erro}"
            )

            return

        self.videos_selecionados = videos

        if not videos:

            self.mostrar_mensagem(
                "Nenhum vídeo foi encontrado "
                "nesta pasta."
            )

            return

        self.mostrar_videos(
            videos
        )

    # ========================================================
    # MOSTRAR VÍDEOS
    # ========================================================

    def mostrar_videos(
        self,
        videos
    ):

        if not videos:

            self.mostrar_mensagem(
                "Nenhum vídeo foi selecionado."
            )

            return

        self.videos_selecionados = list(
            videos
        )

        layout = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=12
        )

        layout.add_widget(
            self.criar_titulo(
                "Agendar publicação"
            )
        )

        lista_scroll = ScrollView()

        nomes = "\n\n".join(
            "• " + os.path.basename(video)
            for video in videos
        )

        lista = Label(
            text=nomes,
            color=BRANCO,
            font_size=16,
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        lista.bind(
            texture_size=lambda instance,
            value:
            setattr(
                instance,
                "height",
                value[1]
            )
        )

        lista_scroll.add_widget(
            lista
        )

        layout.add_widget(
            lista_scroll
        )

        horario_label = Label(
            text="HORÁRIO DA POSTAGEM",
            color=CINZA,
            font_size=13,
            bold=True,
            size_hint_y=None,
            height=35
        )

        layout.add_widget(
            horario_label
        )

        horarios = BoxLayout(
            spacing=10,
            size_hint_y=None,
            height=60
        )

        horas = [
            f"{i:02d}"
            for i in range(24)
        ]

        self.seletor_hora = Spinner(
            text="12",
            values=horas,
            background_color=ROXO,
            color=BRANCO,
            font_size=18
        )

        minutos = [
            f"{i:02d}"
            for i in range(
                0,
                60,
                5
            )
        ]

        self.seletor_minuto = Spinner(
            text="00",
            values=minutos,
            background_color=ROXO,
            color=BRANCO,
            font_size=18
        )

        horarios.add_widget(
            self.seletor_hora
        )

        horarios.add_widget(
            self.seletor_minuto
        )

        layout.add_widget(
            horarios
        )

        salvar = BotaoModerno(
            text="✓  SALVAR AGENDAMENTO",
            cor=VERDE,
            size_hint_y=None,
            height=65
        )

        salvar.bind(
            on_press=self.salvar_agendamento
        )

        layout.add_widget(
            salvar
        )

        voltar = Button(
            text="Voltar",
            color=CINZA,
            background_color=(
                0,
                0,
                0,
                0
            ),
            size_hint_y=None,
            height=45
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(
            voltar
        )

        self.root.clear_widgets()

        self.root.add_widget(
            layout
        )

    # ========================================================
    # SALVAR AGENDAMENTO
    # ========================================================

    def salvar_agendamento(
        self,
        *args
    ):

        hora = self.seletor_hora.text

        minuto = self.seletor_minuto.text

        agendamentos = (
            self.carregar_agendamentos()
        )

        novo_agendamento = {

            "id":
                len(agendamentos) + 1,

            "videos":
                self.videos_selecionados,

            "horario":
                f"{hora}:{minuto}",

            "criado_em":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "status":
                "agendado"
        }

        agendamentos.append(
            novo_agendamento
        )

        self.salvar_arquivo(
            agendamentos
        )

        self.mostrar_mensagem(
            "AGENDAMENTO SALVO!\n\n"
            f"Vídeos: "
            f"{len(self.videos_selecionados)}\n\n"
            f"Horário: {hora}:{minuto}"
        )

    # ========================================================
    # AGENDAMENTOS
    # ========================================================

    def mostrar_agendamentos(
        self,
        *args
    ):

        agendamentos = (
            self.carregar_agendamentos()
        )

        layout = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=12
        )

        layout.add_widget(
            self.criar_titulo(
                "Meus agendamentos"
            )
        )

        scroll = ScrollView()

        conteudo = BoxLayout(
            orientation="vertical",
            spacing=12,
            size_hint_y=None
        )

        conteudo.bind(
            minimum_height=
            conteudo.setter(
                "height"
            )
        )

        if not agendamentos:

            vazio = Label(
                text="Nenhum agendamento salvo.",
                color=CINZA,
                font_size=18
            )

            conteudo.add_widget(
                vazio
            )

        else:

            for agendamento in agendamentos:

                cartao = Cartao(
                    size_hint_y=None,
                    height=135
                )

                numero = Label(
                    text=
                    f"AGENDAMENTO #{agendamento['id']}",
                    color=ROXO_CLARO,
                    font_size=16,
                    bold=True,
                    size_hint_y=None,
                    height=30
                )

                horario = Label(
                    text=
                    f"Horário: "
                    f"{agendamento['horario']}",
                    color=BRANCO,
                    font_size=17,
                    size_hint_y=None,
                    height=30
                )

                quantidade = Label(
                    text=
                    f"Vídeos: "
                    f"{len(agendamento['videos'])}   "
                    f"|   Status: "
                    f"{agendamento['status']}",
                    color=CINZA,
                    font_size=14
                )

                cartao.add_widget(
                    numero
                )

                cartao.add_widget(
                    horario
                )

                cartao.add_widget(
                    quantidade
                )

                conteudo.add_widget(
                    cartao
                )

        scroll.add_widget(
            conteudo
        )

        layout.add_widget(
            scroll
        )

        voltar = BotaoModerno(
            text="VOLTAR",
            cor=ROXO,
            size_hint_y=None,
            height=60
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(
            voltar
        )

        self.root.clear_widgets()

        self.root.add_widget(
            layout
        )

    # ========================================================
    # MENSAGEM
    # ========================================================

    def mostrar_mensagem(
        self,
        mensagem
    ):

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=25
        )

        topo = Label(
            text="Kwai Automático",
            color=ROXO_CLARO,
            font_size=25,
            bold=True,
            size_hint_y=None,
            height=60
        )

        texto = Label(
            text=mensagem,
            color=BRANCO,
            font_size=20,
            halign="center",
            valign="middle"
        )

        voltar = BotaoModerno(
            text="CONTINUAR",
            cor=ROXO,
            size_hint_y=None,
            height=65
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(
            topo
        )

        layout.add_widget(
            texto
        )

        layout.add_widget(
            voltar
        )

        self.root.clear_widgets()

        self.root.add_widget(
            layout
        )


# ============================================================
# EXECUTAR
# ============================================================

if __name__ == "__main__":

    KwaiAutomatico().run()