# newsletter

Script para generar un guion de podcast a partir de noticias en Markdown y
convertirlo a audio utilizando Azure OpenAI y Azure AI Speech.

## Uso
1. Coloca archivos `.md` con noticias en la carpeta `entrada`.
2. Define las variables de entorno necesarias:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT`
   - `AZURE_SPEECH_KEY`
   - `AZURE_SPEECH_REGION`
3. Ejecuta `python podcast_generator.py`.
4. El audio generado se almacenará en `salida` y los archivos procesados se moverán a `procesado`.
