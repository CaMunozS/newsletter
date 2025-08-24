"""Genera un guion de podcast a partir de noticias en un archivo Markdown y
convierte ese guion a audio usando Azure OpenAI y Azure AI Speech.

Requisitos de entorno:
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT  (nombre del deployment para chat completions)
- AZURE_SPEECH_KEY
- AZURE_SPEECH_REGION

Los directorios de entrada, salida y procesado pueden configurarse mediante
argumentos de línea de comandos (``--entrada``, ``--salida`` y ``--procesado``).
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

import openai
import azure.cognitiveservices.speech as speechsdk


def generar_guion(contenido: str) -> str:
    """Genera un guion de podcast a partir del texto proporcionado."""
    client = openai.AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-05-01-preview",
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
    )

    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres un asistente que redacta guiones de podcasts sobre"
                " noticias relacionadas con banca."
            ),
        },
        {"role": "user", "content": contenido},
    ]

    respuesta = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"], messages=mensajes
    )
    return respuesta.choices[0].message.content.strip()


def generar_audio(texto: str, archivo_salida: Path) -> None:
    """Convierte el texto en audio y lo guarda en archivo_salida."""
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["AZURE_SPEECH_KEY"],
        region=os.environ["AZURE_SPEECH_REGION"],
    )
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(archivo_salida))
    sintetizador = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    sintetizador.speak_text_async(texto).get()


def procesar_archivo(md_path: Path, salida_dir: Path, procesado_dir: Path) -> None:
    """Procesa un archivo Markdown: genera guion, audio y mueve el archivo."""
    contenido = md_path.read_text(encoding="utf-8")
    guion = generar_guion(contenido)
    archivo_audio = salida_dir / f"{md_path.stem}.mp3"
    generar_audio(guion, archivo_audio)
    shutil.move(str(md_path), procesado_dir / md_path.name)


def parse_args() -> argparse.Namespace:
    """Devuelve los argumentos de línea de comandos para configurar rutas."""
    parser = argparse.ArgumentParser(description="Generador de podcast")
    parser.add_argument(
        "--entrada", default="entrada", help="Directorio de archivos Markdown"
    )
    parser.add_argument(
        "--salida", default="salida", help="Directorio donde guardar los MP3"
    )
    parser.add_argument(
        "--procesado", default="procesado", help="Directorio de archivos procesados"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entrada_dir = Path(args.entrada)
    salida_dir = Path(args.salida)
    procesado_dir = Path(args.procesado)

    for d in (entrada_dir, salida_dir, procesado_dir):
        d.mkdir(parents=True, exist_ok=True)

    for md_file in entrada_dir.glob("*.md"):
        procesar_archivo(md_file, salida_dir, procesado_dir)


if __name__ == "__main__":
    main()
