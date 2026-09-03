[app]

# Nome do aplicativo
title = Kwai Automatico

# Nome do pacote
package.name = kwaiautomatico
package.domain = org.kwai

# Arquivo principal
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

# Pasta do projeto
source.dir = .

# Versão
version = 1.0

# Orientação da tela
orientation = portrait

# Dependências
requirements = python3,kivy

# Tela cheia
fullscreen = 0

# Android
android.api = 35
android.minapi = 21
android.archs = arm64-v8a

# Permissões
android.permissions = INTERNET,READ_MEDIA_VIDEO,READ_MEDIA_IMAGES

# Nome do aplicativo no Android
android.entrypoint = org.kivy.android.PythonActivity


[buildozer]

# Avisos
log_level = 2

# Pasta onde o APK será criado
bin_dir = bin

# Pasta de arquivos temporários
build_dir = .buildozer
