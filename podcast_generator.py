"""Genera un guion de podcast a partir de noticias en un archivo Markdown y
convierte ese guion a audio usando Azure OpenAI y Azure AI Speech.

Requisitos de entorno:
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_DEPLOYMENT  (nombre del deployment para chat completions)
- AZURE_SPEECH_KEY
- AZURE_SPEECH_REGION
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import openai
import azure.cognitiveservices.speech as speechsdk


ENTRADA_DIR = Path("entrada")
SALIDA_DIR = Path("salida")
PROCESADO_DIR = Path("procesado")


for d in (ENTRADA_DIR, SALIDA_DIR, PROCESADO_DIR):
    d.mkdir(parents=True, exist_ok=True)


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


def procesar_archivo(md_path: Path) -> None:
    """Procesa un archivo Markdown: genera guion, audio y mueve el archivo."""
    contenido = md_path.read_text(encoding="utf-8")
    guion = generar_guion(contenido)
    archivo_audio = SALIDA_DIR / f"{md_path.stem}.mp3"
    generar_audio(guion, archivo_audio)
    shutil.move(str(md_path), PROCESADO_DIR / md_path.name)


def main() -> None:
    for md_file in ENTRADA_DIR.glob("*.md"):
        procesar_archivo(md_file)


if __name__ == "__main__":
    main()
