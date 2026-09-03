from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.spinner import Spinner
import json
import os
from datetime import datetime


ARQUIVO_AGENDAMENTOS = "agendamentos.json"


class KwaiAutomatico(App):

    def carregar_agendamentos(self):
        if not os.path.exists(ARQUIVO_AGENDAMENTOS):
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

    def salvar_arquivo(self, agendamentos):
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

    def build(self):

        return BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

    def on_start(self):
        self.mostrar_principal()

    def mostrar_principal(self, *args):

        self.root.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        titulo = Label(
            text="Kwai Automatico",
            font_size=28,
            size_hint_y=None,
            height=60
        )

        selecionar = Button(
            text="Selecionar videos",
            font_size=20
        )

        selecionar.bind(
            on_press=self.selecionar_videos
        )

        ver_agendamentos = Button(
            text="Ver agendamentos",
            font_size=20
        )

        ver_agendamentos.bind(
            on_press=self.mostrar_agendamentos
        )

        layout.add_widget(titulo)
        layout.add_widget(selecionar)
        layout.add_widget(ver_agendamentos)

        self.root.add_widget(layout)

    def selecionar_videos(self, *args):

        layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        titulo = Label(
            text="Selecione seus videos",
            font_size=22,
            size_hint_y=None,
            height=50
        )

        arquivos = FileChooserListView(
            filters=[
                "*.mp4",
                "*.mov",
                "*.avi",
                "*.mkv"
            ],
            multiselect=True
        )

        confirmar = Button(
            text="Adicionar videos selecionados",
            size_hint_y=None,
            height=60
        )

        voltar = Button(
            text="Voltar",
            size_hint_y=None,
            height=50
        )

        confirmar.bind(
            on_press=lambda x:
            self.mostrar_videos(arquivos.selection)
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

    def mostrar_videos(self, videos):

        if not videos:
            self.mostrar_mensagem(
                "Nenhum video foi selecionado."
            )
            return

        self.videos_selecionados = list(videos)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        titulo = Label(
            text="Videos selecionados",
            font_size=24,
            size_hint_y=None,
            height=60
        )

        nomes = "\n".join(
            os.path.basename(video)
            for video in videos
        )

        lista = Label(
            text=nomes,
            font_size=16
        )

        horario_titulo = Label(
            text="Escolha o horario da postagem:",
            font_size=20,
            size_hint_y=None,
            height=45
        )

        horas = [
            f"{i:02d}"
            for i in range(24)
        ]

        self.seletor_hora = Spinner(
            text="12",
            values=horas,
            size_hint_y=None,
            height=55
        )

        minutos = [
            f"{i:02d}"
            for i in range(0, 60, 5)
        ]

        self.seletor_minuto = Spinner(
            text="00",
            values=minutos,
            size_hint_y=None,
            height=55
        )

        horario_atual = Label(
            text="Horario escolhido: 12:00",
            font_size=20,
            size_hint_y=None,
            height=50
        )

        def atualizar_horario(instance, valor):

            horario_atual.text = (
                "Horario escolhido: "
                f"{self.seletor_hora.text}:"
                f"{self.seletor_minuto.text}"
            )

        self.seletor_hora.bind(
            text=atualizar_horario
        )

        self.seletor_minuto.bind(
            text=atualizar_horario
        )

        salvar = Button(
            text="Salvar agendamento",
            font_size=20,
            size_hint_y=None,
            height=60
        )

        salvar.bind(
            on_press=self.salvar_agendamento
        )

        voltar = Button(
            text="Voltar",
            size_hint_y=None,
            height=50
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

    def salvar_agendamento(self, *args):

        hora = self.seletor_hora.text
        minuto = self.seletor_minuto.text

        agendamentos = self.carregar_agendamentos()

        novo_agendamento = {
            "id": len(agendamentos) + 1,
            "videos": self.videos_selecionados,
            "horario": f"{hora}:{minuto}",
            "criado_em": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "status": "agendado"
        }

        agendamentos.append(novo_agendamento)

        self.salvar_arquivo(agendamentos)

        self.mostrar_mensagem(
            "Agendamento salvo!\n\n"
            f"Videos: {len(self.videos_selecionados)}\n"
            f"Horario: {hora}:{minuto}\n\n"
            "Arquivo salvo:\n"
            "agendamentos.json"
        )

    def mostrar_agendamentos(self, *args):

        agendamentos = self.carregar_agendamentos()

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        titulo = Label(
            text="Agendamentos salvos",
            font_size=24,
            size_hint_y=None,
            height=60
        )

        if not agendamentos:

            lista = Label(
                text="Nenhum agendamento salvo.",
                font_size=20
            )

        else:

            textos = []

            for agendamento in agendamentos:

                texto = (
                    f"Agendamento #{agendamento['id']}\n"
                    f"Horario: {agendamento['horario']}\n"
                    f"Videos: "
                    f"{len(agendamento['videos'])}\n"
                    f"Status: {agendamento['status']}\n"
                )

                textos.append(texto)

            lista = Label(
                text="\n".join(textos),
                font_size=17
            )

        voltar = Button(
            text="Voltar",
            size_hint_y=None,
            height=60
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(titulo)
        layout.add_widget(lista)
        layout.add_widget(voltar)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    def mostrar_mensagem(self, mensagem):

        self.root.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=20
        )

        texto = Label(
            text=mensagem,
            font_size=21
        )

        voltar = Button(
            text="Voltar",
            size_hint_y=None,
            height=60
        )

        voltar.bind(
            on_press=self.mostrar_principal
        )

        layout.add_widget(texto)
        layout.add_widget(voltar)

        self.root.add_widget(layout)


if __name__ == "__main__":
    KwaiAutomatico().run()