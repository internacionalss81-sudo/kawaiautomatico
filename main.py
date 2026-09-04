from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle

import json
import os
from datetime import datetime


ARQUIVO_AGENDAMENTOS = "agendamentos.json"


class BotaoColorido(Button):

    def __init__(self, cor=(0.15, 0.55, 0.90, 1), **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.cor = cor

        with self.canvas.before:
            Color(*self.cor)
            self.retangulo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )

        self.bind(
            pos=self.atualizar_retangulo,
            size=self.atualizar_retangulo
        )

    def atualizar_retangulo(self, *args):
        self.retangulo.pos = self.pos
        self.retangulo.size = self.size


class KwaiAutomatico(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.programa_rodando = False

        self.videos_selecionados = []

        self.pasta_selecionada = ""

        self.selecao_android = None

    def build(self):

        return BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

    def on_start(self):
        self.mostrar_principal()

    # ==========================================================
    # ARQUIVOS DE AGENDAMENTO
    # ==========================================================

    def caminho_agendamentos(self):

        if platform == "android":

            try:
                from android.storage import app_storage_path

                pasta = app_storage_path()

                return os.path.join(
                    pasta,
                    ARQUIVO_AGENDAMENTOS
                )

            except Exception:

                return ARQUIVO_AGENDAMENTOS

        return ARQUIVO_AGENDAMENTOS

    def carregar_agendamentos(self):

        arquivo_agendamentos = self.caminho_agendamentos()

        if not os.path.exists(arquivo_agendamentos):
            return []

        try:

            with open(
                arquivo_agendamentos,
                "r",
                encoding="utf-8"
            ) as arquivo:

                return json.load(arquivo)

        except Exception:

            return []

    def salvar_arquivo(self, agendamentos):

        arquivo_agendamentos = self.caminho_agendamentos()

        with open(
            arquivo_agendamentos,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                agendamentos,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    # ==========================================================
    # TELA PRINCIPAL
    # ==========================================================

    def mostrar_principal(self, *args):

        self.root.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=[25, 30, 25, 30],
            spacing=18
        )

        titulo = Label(
            text="Kwai Automático",
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=70
        )

        subtitulo = Label(
            text="Painel de automação",
            font_size=18,
            size_hint_y=None,
            height=40
        )

        status = Label(
            text=self.obter_status(),
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=45
        )

        iniciar = BotaoColorido(
            text="▶  INICIAR PROGRAMA",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=80,
            cor=(0.10, 0.65, 0.25, 1)
        )

        iniciar.bind(
            on_press=self.iniciar_programa
        )

        parar = BotaoColorido(
            text="■  PARAR PROGRAMA",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=80,
            cor=(0.85, 0.15, 0.15, 1)
        )

        parar.bind(
            on_press=self.parar_programa
        )

        selecionar = BotaoColorido(
            text="📹  SELECIONAR VÍDEOS",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=80,
            cor=(0.10, 0.40, 0.85, 1)
        )

        selecionar.bind(
            on_press=self.selecionar_videos
        )

        pasta = BotaoColorido(
            text="📂  SELECIONAR PASTA",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=80,
            cor=(0.15, 0.45, 0.75, 1)
        )

        pasta.bind(
            on_press=self.selecionar_pasta
        )

        agendamentos = BotaoColorido(
            text="🕐  MEUS AGENDAMENTOS",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=80,
            cor=(0.50, 0.25, 0.75, 1)
        )

        agendamentos.bind(
            on_press=self.mostrar_agendamentos
        )

        layout.add_widget(titulo)
        layout.add_widget(subtitulo)
        layout.add_widget(status)
        layout.add_widget(iniciar)
        layout.add_widget(parar)
        layout.add_widget(selecionar)
        layout.add_widget(pasta)
        layout.add_widget(agendamentos)

        self.root.add_widget(layout)

    def obter_status(self):

        if self.programa_rodando:
            return "●  PROGRAMA ATIVO"

        return "○  PROGRAMA PARADO"

    # ==========================================================
    # INICIAR / PARAR
    # ==========================================================

    def iniciar_programa(self, *args):

        if self.programa_rodando:

            self.mostrar_mensagem(
                "O programa já está iniciado."
            )

            return

        self.programa_rodando = True

        Clock.schedule_interval(
            self.verificar_agendamentos,
            30
        )

        self.mostrar_mensagem(
            "PROGRAMA INICIADO!\n\n"
            "O aplicativo está monitorando "
            "os seus agendamentos."
        )

    def parar_programa(self, *args):

        self.programa_rodando = False

        Clock.unschedule(
            self.verificar_agendamentos
        )

        self.mostrar_mensagem(
            "PROGRAMA PARADO."
        )

    def verificar_agendamentos(self, dt):

        if not self.programa_rodando:
            return

        horario_atual = datetime.now().strftime(
            "%H:%M"
        )

        agendamentos = self.carregar_agendamentos()

        alterado = False

        for agendamento in agendamentos:

            if agendamento.get("status") != "agendado":
                continue

            if agendamento.get("horario") == horario_atual:

                agendamento["status"] = "processando"

                alterado = True

        if alterado:

            self.salvar_arquivo(
                agendamentos
            )

    # ==========================================================
    # SELECIONAR VÍDEOS
    # ==========================================================

    def selecionar_videos(self, *args):

        if platform == "android":

            self.abrir_seletor_android_videos()

        else:

            self.selecionar_videos_pc()

    def selecionar_videos_pc(self):

        from kivy.uix.filechooser import FileChooserListView

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        titulo = Label(
            text="📹 SELECIONE SEUS VÍDEOS",
            font_size=26,
            bold=True,
            size_hint_y=None,
            height=65
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

        confirmar = BotaoColorido(
            text="✓  ADICIONAR VÍDEOS",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=75,
            cor=(0.10, 0.65, 0.25, 1)
        )

        voltar = BotaoColorido(
            text="←  VOLTAR",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=65,
            cor=(0.35, 0.35, 0.40, 1)
        )

        confirmar.bind(
            on_press=lambda x:
            self.mostrar_videos(
                arquivos.selection
            )
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(titulo)
        layout.add_widget(arquivos)
        layout.add_widget(confirmar)
        layout.add_widget(voltar)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    # ==========================================================
    # SELETOR ANDROID DE VÍDEOS
    # ==========================================================

    def abrir_seletor_android_videos(self):

        try:

            from android import activity
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity_real = PythonActivity.mActivity

            Intent = autoclass(
                "android.content.Intent"
            )

            intent = Intent(
                Intent.ACTION_OPEN_DOCUMENT
            )

            intent.addCategory(
                Intent.CATEGORY_OPENABLE
            )

            intent.setType(
                "video/*"
            )

            intent.putExtra(
                Intent.EXTRA_ALLOW_MULTIPLE,
                True
            )

            self.selecao_android = "videos"

            activity.bind(
                on_activity_result=
                self.receber_resultado_android
            )

            activity_real.startActivityForResult(
                intent,
                1001
            )

        except Exception as erro:

            self.mostrar_mensagem(
                "Não foi possível abrir o "
                "seletor de vídeos.\n\n"
                f"{erro}"
            )

    # ==========================================================
    # SELECIONAR PASTA
    # ==========================================================

    def selecionar_pasta(self, *args):

        if platform == "android":

            self.abrir_seletor_android_pasta()

        else:

            self.selecionar_pasta_pc()

    def selecionar_pasta_pc(self):

        from kivy.uix.filechooser import FileChooserListView

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        titulo = Label(
            text="📂 ESCOLHA A PASTA DOS VÍDEOS",
            font_size=25,
            bold=True,
            size_hint_y=None,
            height=65
        )

        arquivos = FileChooserListView(
            path=os.path.expanduser("~"),
            dirselect=True,
            filters=[]
        )

        confirmar = BotaoColorido(
            text="✓  USAR ESTA PASTA",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=75,
            cor=(0.10, 0.65, 0.25, 1)
        )

        voltar = BotaoColorido(
            text="←  VOLTAR",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=65,
            cor=(0.35, 0.35, 0.40, 1)
        )

        confirmar.bind(
            on_press=lambda x:
            self.confirmar_pasta_pc(
                arquivos.selection
            )
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(titulo)
        layout.add_widget(arquivos)
        layout.add_widget(confirmar)
        layout.add_widget(voltar)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    # ==========================================================
    # ABRIR PASTA ANDROID
    # ==========================================================

    def abrir_seletor_android_pasta(self):

        try:

            from android import activity
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity_real = PythonActivity.mActivity

            Intent = autoclass(
                "android.content.Intent"
            )

            intent = Intent(
                Intent.ACTION_OPEN_DOCUMENT_TREE
            )

            intent.addFlags(
                Intent.FLAG_GRANT_READ_URI_PERMISSION
                | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
                | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            )

            self.selecao_android = "pasta"

            activity.bind(
                on_activity_result=
                self.receber_resultado_android
            )

            activity_real.startActivityForResult(
                intent,
                1002
            )

        except Exception as erro:

            self.mostrar_mensagem(
                "Não foi possível abrir o "
                "seletor de pastas.\n\n"
                f"{erro}"
            )

    # ==========================================================
    # RESULTADO DO ANDROID
    # ==========================================================

    def receber_resultado_android(
        self,
        request_code,
        result_code,
        intent
    ):

        try:

            from jnius import autoclass

            Activity = autoclass(
                "android.app.Activity"
            )

            if result_code != Activity.RESULT_OK:
                return

            if intent is None:
                return

            if request_code == 1002:

                uri = intent.getData()

                if uri is None:

                    self.mostrar_mensagem(
                        "Nenhuma pasta foi selecionada."
                    )

                    return

                uri_string = uri.toString()

                self.pasta_selecionada = uri_string

                # Guarda a permissão da pasta.
                self.guardar_permissao_pasta(
                    uri
                )

                # Procura os vídeos dentro da pasta.
                videos = self.listar_videos_android(
                    uri
                )

                if not videos:

                    self.mostrar_mensagem(
                        "Pasta selecionada!\n\n"
                        "Porém, nenhum vídeo foi "
                        "encontrado nessa pasta.\n\n"
                        "Coloque vídeos MP4, MOV, AVI, "
                        "MKV ou WEBM dentro dela."
                    )

                    return

                self.videos_selecionados = videos

                self.mostrar_videos_android(
                    videos
                )

                return

            if request_code == 1001:

                videos = []

                clip_data = intent.getClipData()

                if clip_data is not None:

                    quantidade = clip_data.getItemCount()

                    for i in range(quantidade):

                        item = clip_data.getItemAt(i)

                        item_uri = item.getUri()

                        videos.append(
                            item_uri.toString()
                        )

                else:

                    uri = intent.getData()

                    if uri is not None:

                        videos.append(
                            uri.toString()
                        )

                self.videos_selecionados = videos

                self.mostrar_videos_android(
                    videos
                )

        except Exception as erro:

            self.mostrar_mensagem(
                "Erro ao acessar a seleção do Android.\n\n"
                f"{erro}"
            )

    # ==========================================================
    # PERMISSÃO DA PASTA
    # ==========================================================

    def guardar_permissao_pasta(self, uri):

        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = PythonActivity.mActivity
            resolver = activity.getContentResolver()

            Intent = autoclass(
                "android.content.Intent"
            )

            flags = (
                Intent.FLAG_GRANT_READ_URI_PERMISSION
                | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
            )

            resolver.takePersistableUriPermission(
                uri,
                flags
            )

        except Exception as erro:
            print(
                "Erro ao guardar permissão:",
                erro
            )

    # ==========================================================
    # ENCONTRAR VÍDEOS DENTRO DA PASTA ANDROID
    # ==========================================================

    def listar_videos_android(self, pasta_uri):

        videos = []

        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = PythonActivity.mActivity
            resolver = activity.getContentResolver()

            DocumentsContract = autoclass(
                "android.provider.DocumentsContract"
            )

            children_uri = (
                DocumentsContract.buildChildDocumentsUriUsingTree(
                    pasta_uri,
                    DocumentsContract.getTreeDocumentId(
                        pasta_uri
                    )
                )
            )

            cursor = resolver.query(
                children_uri,
                None,
                None,
                None,
                None
            )

            if cursor is None:
                return []

            try:
                extensoes = (
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".mkv",
                    ".webm"
                )

                nome_coluna = (
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME
                )

                documento_coluna = (
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID
                )

                while cursor.moveToNext():
                    try:
                        nome_index = cursor.getColumnIndex(
                            nome_coluna
                        )

                        if nome_index < 0:
                            continue

                        nome = cursor.getString(nome_index)

                        if not nome or not nome.lower().endswith(extensoes):
                            continue

                        documento_index = cursor.getColumnIndex(
                            documento_coluna
                        )

                        if documento_index < 0:
                            continue

                        document_id = cursor.getString(
                            documento_index
                        )

                        arquivo_uri = (
                            DocumentsContract.buildDocumentUriUsingTree(
                                pasta_uri,
                                document_id
                            )
                        )

                        videos.append(arquivo_uri.toString())

                    except Exception as erro:
                        print(
                            "Erro ao processar arquivo:",
                            erro
                        )
                        continue

            finally:
                cursor.close()

        except Exception as erro:
            print(
                "Erro ao listar vídeos:",
                erro
            )

        return videos

    # ==========================================================
    # FALLBACK CONTENT RESOLVER
    # ==========================================================

    # ==========================================================
    # MOSTRAR VÍDEOS ANDROID
    # ==========================================================

    def mostrar_videos_android(self, videos):

        if not videos:

            self.mostrar_mensagem(
                "Nenhum vídeo foi selecionado."
            )

            return

        layout = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
        )

        titulo = Label(
            text="📹 VÍDEOS ENCONTRADOS",
            font_size=27,
            bold=True,
            size_hint_y=None,
            height=65
        )

        nomes = []

        for video in videos:

            nome = self.obter_nome_uri(
                video
            )

            if not nome:
                nome = "Vídeo selecionado"

            nomes.append(
                "• " + nome
            )

        lista = Label(
            text="\n".join(nomes),
            font_size=18
        )

        quantidade = Label(
            text=f"Total de vídeos: {len(videos)}",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=50
        )

        horario_titulo = Label(
            text="🕐 ESCOLHA O HORÁRIO",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=50
        )

        horas = [
            f"{i:02d}"
            for i in range(24)
        ]

        self.seletor_hora = Spinner(
            text="12",
            values=horas,
            font_size=22,
            size_hint_y=None,
            height=65
        )

        minutos = [
            f"{i:02d}"
            for i in range(0, 60, 5)
        ]

        self.seletor_minuto = Spinner(
            text="00",
            values=minutos,
            font_size=22,
            size_hint_y=None,
            height=65
        )

        horario_atual = Label(
            text="Horário escolhido: 12:00",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=55
        )

        def atualizar_horario(
            instance,
            valor
        ):

            horario_atual.text = (
                "Horário escolhido: "
                f"{self.seletor_hora.text}:"
                f"{self.seletor_minuto.text}"
            )

        self.seletor_hora.bind(
            text=atualizar_horario
        )

        self.seletor_minuto.bind(
            text=atualizar_horario
        )

        salvar = BotaoColorido(
            text="✓  SALVAR AGENDAMENTO",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=75,
            cor=(0.10, 0.65, 0.25, 1)
        )

        salvar.bind(
            on_press=self.salvar_agendamento
        )

        voltar = BotaoColorido(
            text="←  VOLTAR",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=65,
            cor=(0.35, 0.35, 0.40, 1)
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(titulo)
        layout.add_widget(lista)
        layout.add_widget(quantidade)
        layout.add_widget(horario_titulo)
        layout.add_widget(self.seletor_hora)
        layout.add_widget(self.seletor_minuto)
        layout.add_widget(horario_atual)
        layout.add_widget(salvar)
        layout.add_widget(voltar)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    # ==========================================================
    # NOME DA URI
    # ==========================================================

    def obter_nome_uri(self, uri_string):

        try:

            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = PythonActivity.mActivity

            resolver = activity.getContentResolver()

            Uri = autoclass(
                "android.net.Uri"
            )

            uri = Uri.parse(
                uri_string
            )

            cursor = resolver.query(
                uri,
                None,
                None,
                None,
                None
            )

            if cursor is None:
                return uri_string

            try:

                if cursor.moveToFirst():

                    indice = cursor.getColumnIndex(
                        "_display_name"
                    )

                    if indice >= 0:

                        nome = cursor.getString(
                            indice
                        )

                        if nome:
                            return nome

            finally:

                cursor.close()

        except Exception:
            pass

        return uri_string

    # ==========================================================
    # PASTA WINDOWS
    # ==========================================================

    def confirmar_pasta_pc(self, selecao):

        if not selecao:

            self.mostrar_mensagem(
                "Nenhuma pasta foi selecionada."
            )

            return

        pasta = selecao[0]

        if not os.path.isdir(pasta):

            self.mostrar_mensagem(
                "Selecione uma pasta, "
                "não um arquivo."
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

            for nome in os.listdir(pasta):

                caminho = os.path.join(
                    pasta,
                    nome
                )

                if os.path.isfile(caminho):

                    if nome.lower().endswith(
                        extensoes
                    ):

                        videos.append(
                            caminho
                        )

        except Exception as erro:

            self.mostrar_mensagem(
                "Não foi possível acessar a pasta.\n\n"
                f"{erro}"
            )

            return

        self.videos_selecionados = videos

        self.pasta_selecionada = pasta

        if not videos:

            self.mostrar_mensagem(
                "A pasta foi selecionada, "
                "mas nenhum vídeo foi encontrado."
            )

            return

        self.mostrar_videos(
            videos
        )

    # ==========================================================
    # MOSTRAR VÍDEOS PC
    # ==========================================================

    def mostrar_videos(self, videos):

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
            padding=25,
            spacing=15
        )

        titulo = Label(
            text="📹 VÍDEOS SELECIONADOS",
            font_size=27,
            bold=True,
            size_hint_y=None,
            height=65
        )

        nomes = "\n".join(
            os.path.basename(video)
            for video in videos
        )

        lista = Label(
            text=nomes,
            font_size=18
        )

        horario_titulo = Label(
            text="🕐 ESCOLHA O HORÁRIO",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=50
        )

        horas = [
            f"{i:02d}"
            for i in range(24)
        ]

        self.seletor_hora = Spinner(
            text="12",
            values=horas,
            font_size=22,
            size_hint_y=None,
            height=65
        )

        minutos = [
            f"{i:02d}"
            for i in range(0, 60, 5)
        ]

        self.seletor_minuto = Spinner(
            text="00",
            values=minutos,
            font_size=22,
            size_hint_y=None,
            height=65
        )

        horario_atual = Label(
            text="Horário escolhido: 12:00",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=55
        )

        def atualizar_horario(
            instance,
            valor
        ):

            horario_atual.text = (
                "Horário escolhido: "
                f"{self.seletor_hora.text}:"
                f"{self.seletor_minuto.text}"
            )

        self.seletor_hora.bind(
            text=atualizar_horario
        )

        self.seletor_minuto.bind(
            text=atualizar_horario
        )

        salvar = BotaoColorido(
            text="✓  SALVAR AGENDAMENTO",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=75,
            cor=(0.10, 0.65, 0.25, 1)
        )

        salvar.bind(
            on_press=self.salvar_agendamento
        )

        voltar = BotaoColorido(
            text="←  VOLTAR",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=65,
            cor=(0.35, 0.35, 0.40, 1)
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(titulo)
        layout.add_widget(lista)
        layout.add_widget(horario_titulo)
        layout.add_widget(self.seletor_hora)
        layout.add_widget(self.seletor_minuto)
        layout.add_widget(horario_atual)
        layout.add_widget(salvar)
        layout.add_widget(voltar)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    # ==========================================================
    # SALVAR AGENDAMENTO
    # ==========================================================

    def salvar_agendamento(self, *args):

        hora = self.seletor_hora.text
        minuto = self.seletor_minuto.text

        agendamentos = self.carregar_agendamentos()

        novo_agendamento = {
            "id": len(agendamentos) + 1,
            "videos": self.videos_selecionados,
            "pasta": self.pasta_selecionada,
            "horario": f"{hora}:{minuto}",
            "criado_em": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "status": "agendado"
        }

        agendamentos.append(
            novo_agendamento
        )

        self.salvar_arquivo(
            agendamentos
        )

        self.mostrar_mensagem(
            "✓ AGENDAMENTO SALVO!\n\n"
            f"Vídeos: {len(self.videos_selecionados)}\n"
            f"Horário: {hora}:{minuto}"
        )

    # ==========================================================
    # AGENDAMENTOS
    # ==========================================================

    def mostrar_agendamentos(self, *args):

        agendamentos = self.carregar_agendamentos()

        layout = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
        )

        titulo = Label(
            text="🕐 MEUS AGENDAMENTOS",
            font_size=27,
            bold=True,
            size_hint_y=None,
            height=70
        )

        if not agendamentos:

            lista = Label(
                text="Nenhum agendamento salvo.",
                font_size=21
            )

        else:

            textos = []

            for agendamento in agendamentos:

                texto = (
                    f"Agendamento #{agendamento['id']}\n"
                    f"Horário: {agendamento['horario']}\n"
                    f"Vídeos: "
                    f"{len(agendamento['videos'])}\n"
                    f"Status: {agendamento['status']}\n"
                )

                textos.append(texto)

            lista = Label(
                text="\n".join(textos),
                font_size=19
            )

        voltar = BotaoColorido(
            text="←  VOLTAR",
            font_size=21,
            bold=True,
            size_hint_y=None,
            height=70,
            cor=(0.35, 0.35, 0.40, 1)
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(titulo)
        layout.add_widget(lista)
        layout.add_widget(voltar)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    # ==========================================================
    # MENSAGEM
    # ==========================================================

    def mostrar_mensagem(self, mensagem):

        self.root.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=25
        )

        texto = Label(
            text=mensagem,
            font_size=23,
            bold=True
        )

        voltar = BotaoColorido(
            text="←  VOLTAR",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=80,
            cor=(0.35, 0.35, 0.40, 1)
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(texto)
        layout.add_widget(voltar)

        self.root.add_widget(layout)


if __name__ == "__main__":
    KwaiAutomatico().run()