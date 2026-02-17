# How to Use ReelSmith

ReelSmith is an automated pipeline that transforms a financial topic into a high-quality, domain-specific video script in Rioplatense Spanish.

## Prerequisites

1.  **Python 3.10+**: Ensure you have Python 3.10 or higher installed.
2.  **Poetry**: This project uses Poetry for dependency management.
3.  **API Keys**: You will need:
    *   [OpenRouter](https://openrouter.ai/) API key for LLM inference.
    *   [Tavily](https://tavily.com/) API key for web search.

## Setup

1.  Clone the repository and navigate to the project directory.
2.  Install dependencies:
    ```bash
    poetry install
    ```
3.  Set up your environment variables:
    ```bash
    cp .env_example .env
    ```
    Edit the `.env` file and insert your API keys.

## Running the Entrypoint

Use `src/main.py` to run the full pipeline.

### Basic Command

```bash
poetry run python src/main.py --topic "Bitcoin Halving 2024"
```

### Options

*   `--topic`: (Required) The subject of your video.
*   `--angle`: (Optional) A specific perspective (e.g., "Impact on small investors").
*   `--framework`: (Optional) Choose between:
    *   `direct_response` (Default): Standard Hook -> Problem -> Solution.
    *   `storytelling`: Hero's Journey narrative.
    *   `metaphor`: Explaining concepts through analogies.
*   `--datasource`: (Optional) Choose between `tavily` (default) or `yfinance`.
*   `--output`: (Optional) Filename for the JSON output. Defaults to `{topic}_{angle}_{timestamp}.json`.

### Example: Storytelling Framework

```bash
poetry run python -m src.main --topic "The Compound Interest Effect" --angle "Start investing at 20 vs 40" --framework storytelling
```

## Generated Output

The script will be printed to your console and saved as a JSON file. Each scene includes:
*   **Visual Cue**: Direction for the video editor.
*   **Spoken Text**: The dialogue in Rioplatense Spanish (using *voseo*).
*   **Text on Screen**: Key highlights for overlays.
*   **Estimated Duration**: Timing in seconds.

### Sample Scene JSON

```json
{
  "scene_number": 1,
  "visual_cue": "Alfred mirándote a cámara con un café en la mano.",
  "spoken_text": "¿sabías que si arrancás hoy, tu futuro cambia por completo?.",
  "text_on_screen": "¡Arrancá HOY!",
  "estimated_duration": 5
}
```
