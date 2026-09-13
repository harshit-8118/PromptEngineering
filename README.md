# PromptLab — live prompt-engineering demo

## WEBSITE: [https://prompt-eng.streamlit.app/](https://prompt-eng.streamlit.app/)

A small Streamlit teaching app that compares baseline and engineered prompts using real Gemini responses. It includes zero-shot, few-shot, system-instruction, context, structured-output, and image-prompt demonstrations using two fixed educational chest X-rays.

## 1. Get a Gemini API key

Create a key in [Google AI Studio](https://aistudio.google.com/app/apikey). New projects can use eligible Gemini models within Google's free-tier limits; availability, quotas, and data-use terms can change, so review the [current Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) before the event.

Never commit an actual API key. The included `.env` contains only a placeholder and is ignored by Git.

## 2. Run locally

Python 3.10 or later is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Edit `.env`:

```dotenv
GEMINI_API_KEY=replace_with_your_real_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Then start the app:

```powershell
streamlit run app.py
```

## 3. Deploy on Streamlit Community Cloud

1. Push `app.py`, `prompts.py`, `requirements.txt`, `.env.example`, `.gitignore`, and this README to a GitHub repository. Do **not** push `.env`.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app and select `app.py` as the entry point.
3. Open the app's **Settings → Secrets** and add:

```toml
GEMINI_API_KEY = "replace_with_your_real_key"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

4. Save, reboot the app, and verify that the sidebar says **API connected**.

Streamlit Secrets take precedence over `.env`, so the same code works locally and after deployment. The API call runs on the server; the secret is not embedded in the page.

## Configuration

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `GEMINI_API_KEY` | Yes | — | Authenticates Gemini Developer API calls |
| `GEMINI_MODEL` | No | `gemini-3.5-flash-lite` | Model used for text and image understanding |

If your project does not have access to the default model, set `GEMINI_MODEL` to another text-and-image input model available to that project.
The app also retries unavailable-model errors with `gemini-flash-latest`, `gemini-3.1-flash-lite`, and `gemini-3.5-flash-lite`. The sidebar shows which model completed the latest request.
Temporary `429` and `503` capacity errors are retried once per model with a short delay before the app moves to the next fallback.

## Demo notes and safety

- Model output is nondeterministic; two runs may differ. That variation is useful when explaining why prompt evaluation matters.
- The clinical scenarios are fictional training examples. Do not enter real patient-identifying or confidential information.
- `pneumonia1.png` and `pneumonia2.png` are fixed demonstration inputs and are sent to the Gemini API project configured by the deployment owner.
- Keep both image files beside `app.py` when deploying.
- The app generates text only; “image prompt” means image-plus-text input for visual understanding.
- Test quota and network access before presenting. Keep screenshots as a fallback.

## Prompt sources

The lesson structure follows Google's guidance on [prompt components](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/introduction-prompt-design), [prompt-design strategies](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/prompt-design-strategies), and [multimodal prompt design](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/design-multimodal-prompts).
