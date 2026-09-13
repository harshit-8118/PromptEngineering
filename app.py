import os
import time
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageOps

from prompts import IMAGE_DEMOS, TEXT_DEMOS

load_dotenv()

st.set_page_config(
    page_title="PromptLab — Live Prompt Engineering",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass(frozen=True)
class ApiSettings:
    api_key: str
    model: str


def secret_or_env(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except (FileNotFoundError, AttributeError):
        return os.getenv(name, default)


def get_settings() -> ApiSettings:
    return ApiSettings(
        api_key=secret_or_env("GEMINI_API_KEY"),
        model=secret_or_env("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    )


@st.cache_resource(show_spinner=False)
def get_client(api_key: str):
    return genai.Client(api_key=api_key)


def call_gemini(prompt: str, system_instruction: str, images: list[Image.Image] | None = None) -> str:
    settings = get_settings()
    if not settings.api_key or settings.api_key == "your_google_ai_studio_api_key_here":
        raise RuntimeError("Add GEMINI_API_KEY in .env locally or Streamlit Secrets when deployed.")

    contents = []
    if images:
        for index, image in enumerate(images, start=1):
            contents.extend([f"IMAGE {index}:", image])
    contents.append(prompt)
    candidates = list(
        dict.fromkeys(
            [
                settings.model,
                "gemini-flash-latest",
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash-lite",
            ]
        )
    )
    unavailable = []
    capacity_errors = []
    for model in candidates:
        for attempt in range(2):
            try:
                response = get_client(settings.api_key).models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction or None,
                        temperature=0.3,
                        max_output_tokens=700,
                    ),
                )
                if not response.text:
                    raise RuntimeError(
                        "The model returned no text. The request may have been blocked by a safety filter."
                    )
                st.session_state["active_model"] = model
                return response.text
            except Exception as exc:
                message = str(exc)
                lowered = message.lower()
                if "not_found" in lowered or "not found" in lowered or "no longer available" in lowered:
                    unavailable.append(model)
                    break
                if (
                    "503" in message
                    or "429" in message
                    or "unavailable" in lowered
                    or "resource_exhausted" in lowered
                    or "high demand" in lowered
                ):
                    if attempt == 0:
                        time.sleep(1.25)
                        continue
                    capacity_errors.append(model)
                    break
                raise

    raise RuntimeError(
        "Gemini could not serve this request after retrying available models. "
        f"Unavailable: {', '.join(unavailable) or 'none'}. "
        f"At capacity or rate-limited: {', '.join(capacity_errors) or 'none'}. "
        "Wait briefly and run the prompt again."
    )


def run_button(
    key: str,
    prompt: str,
    system_instruction: str,
    images: list[Image.Image] | None = None,
    label: str = "Run live prompt",
):
    if st.button(label, key=key, type="primary", width="stretch"):
        with st.spinner("Gemini is responding…"):
            try:
                st.session_state[f"result_{key}"] = call_gemini(prompt, system_instruction, images)
            except Exception as exc:
                st.session_state[f"result_{key}"] = None
                message = str(exc)
                st.error(f"Could not complete the request: {message}")
    result = st.session_state.get(f"result_{key}")
    if result:
        st.markdown(result)


def prompt_breakdown(demo: dict):
    labels = []
    if demo.get("system"):
        labels.append("System instruction")
    labels.extend(demo.get("components", []))
    st.caption(" · ".join(dict.fromkeys(labels)))


def comparison_lens(items: list[str]):
    st.markdown("**What to compare after both runs**")
    st.markdown("\n".join(f"- {item}" for item in items))


st.markdown(
    """
    <style>
      :root { --teal:#2f6f68; --teal-dark:#1e4b46; --paper:#f7f7f4; }
      html { color-scheme: light; }
      .stApp { background: var(--paper); color:#1c201f; }
      .block-container { max-width: 1120px; padding-top: 2.2rem; }
      .stApp h1, .stApp h2, .stApp h3,
      .stApp p, .stApp li, .stApp label,
      .stApp [data-testid="stMarkdownContainer"] { color:#1c201f; }
      h1, h2 { letter-spacing: -.025em; }
      .hero { padding: 1.5rem 0 1rem; border-bottom: 1px solid #deddd5; margin-bottom: 1.2rem; }
      .eyebrow { color:#2f6f68 !important; font-weight:700; font-size:.78rem; letter-spacing:.1em; text-transform:uppercase; }
      .hero h1 { color:#1c201f !important; font-family: Georgia, serif; font-weight:400; font-size:2.65rem; margin:.25rem 0; }
      .hero p { color:#4f5753 !important; max-width:760px; font-size:1.04rem; }
      [data-testid="stMetric"] { background:white; border:1px solid #deddd5; border-radius:12px; padding:14px; }
      [data-testid="stMetricLabel"] p { color:#4f5753 !important; }
      [data-testid="stMetricValue"] { color:#1c201f !important; }
      [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] { background:white; border-color:#deddd5; }
      [data-testid="stExpander"] summary,
      [data-testid="stExpander"] summary p,
      [data-testid="stExpanderDetails"] p,
      [data-testid="stExpanderDetails"] li { color:#1c201f !important; }
      button[data-baseweb="tab"] p { color:#4f5753 !important; }
      button[data-baseweb="tab"][aria-selected="true"] p { color:#2f6f68 !important; font-weight:700; }
      [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:#59615d !important; }
      [data-testid="stCodeBlock"] code { color:#1c201f !important; }
      [data-baseweb="select"] * { color:#1c201f !important; }
      .stButton>button[kind="primary"] { background:#2f6f68; border-color:#2f6f68; }
      .stButton>button[kind="primary"]:hover { background:#1e4b46; border-color:#1e4b46; }
      code { white-space:pre-wrap !important; }
    </style>
    <div class="hero">
      <div class="eyebrow">AI for Clinicians · Interactive learning lab · Live Gemini API</div>
      <h1>Prompt engineering changes the answer.</h1>
      <p>Choose a prepared technique, inspect the prompt, and run it against a real model. Compare what changes when the model receives clearer instructions, context, examples, and visual evidence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

settings = get_settings()
with st.sidebar:
    st.header("Demo controls")
    api_ready = bool(settings.api_key and settings.api_key != "your_google_ai_studio_api_key_here")
    if api_ready:
        st.success("API connected", icon="✅")
    else:
        st.warning("API key required", icon="🔑")
    st.caption(f"Model: `{settings.model}`")
    if st.session_state.get("active_model"):
        st.caption(f"Last successful model: `{st.session_state['active_model']}`")
    st.markdown("The model can make mistakes. Do not use demo output as medical advice or include real patient-identifying information.")
    st.divider()
    st.markdown("**Prompt recipe**")
    st.markdown("1. Objective\n2. Context\n3. Constraints\n4. Output format\n5. Examples (when useful)")

intro, text_tab, image_tab = st.tabs(["Foundations", "Text prompt lab", "Image prompt lab"])

with intro:
    st.subheader("A prompt is more than a question")
    cols = st.columns(4)
    for col, value, label in zip(cols, ["Required", "Optional", "Optional", "Optional"], ["Task", "System instruction", "Context", "Few-shot examples"]):
        col.metric(label, value)
    st.markdown(
        "Prompt design shapes a model's response by supplying the information and structure it needs. "
        "Prompt engineering is the iterative cycle of changing that design and evaluating the results."
    )
    with st.expander("What each technique does", expanded=True):
        st.markdown(
            """
            - **Zero-shot:** asks for a task without worked examples.
            - **Few-shot:** demonstrates the desired input/output pattern before the new task.
            - **System instruction:** sets durable role, behavior, boundaries, or tone.
            - **Context:** supplies facts the model should use instead of forcing it to guess.
            - **Constraints and format:** make success observable: length, audience, sections, or schema.
            - **Multimodal prompting:** combines text instructions with an image or other media.
            """
        )

with text_tab:
    st.markdown("**Choose a prompt-engineering comparison**")
    demo_name = st.segmented_control(
        "Choose a prompt-engineering comparison",
        options=list(TEXT_DEMOS),
        default=list(TEXT_DEMOS)[0],
        key="text_demo",
        label_visibility="collapsed",
        width="stretch",
    )
    demo = TEXT_DEMOS[demo_name]
    st.info(demo["teaching_point"], icon="💡")
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("A · Baseline")
        prompt_breakdown(demo["baseline"])
        st.code(demo["baseline"]["prompt"], language="text")
        with st.expander("System instruction"):
            st.code(demo["baseline"].get("system") or "None", language="text")
        run_button(
            f"text_base_{demo_name}",
            demo["baseline"]["prompt"],
            demo["baseline"].get("system", ""),
            label="Run baseline prompt",
        )
    with right:
        st.subheader("B · Engineered")
        prompt_breakdown(demo["engineered"])
        st.code(demo["engineered"]["prompt"], language="text")
        with st.expander("System instruction"):
            st.code(demo["engineered"].get("system") or "None", language="text")
        run_button(
            f"text_eng_{demo_name}",
            demo["engineered"]["prompt"],
            demo["engineered"].get("system", ""),
            label="Run engineered prompt",
        )
    st.divider()
    comparison_lens(demo.get("compare", ["Compare specificity, completeness, consistency, and usability."]))

with image_tab:
    image_demo = IMAGE_DEMOS["Pneumonia X-ray comparison"]
    st.info(image_demo["teaching_point"], icon="💡")
    app_directory = Path(__file__).resolve().parent
    image_paths = [app_directory / "pneumonia1.png", app_directory / "pneumonia2.png"]
    missing = [str(path) for path in image_paths if not path.exists()]
    if missing:
        st.error("Missing required static image files: " + ", ".join(missing))
    else:
        images = [Image.open(path).convert("RGB") for path in image_paths]
        display_images = [
            ImageOps.pad(image, (1000, 680), method=Image.Resampling.LANCZOS, color="black")
            for image in images
        ]
        image_columns = st.columns(2, gap="medium")
        image_columns[0].image(display_images[0], caption="IMAGE 1 · pneumonia1.png", width="stretch")
        image_columns[1].image(display_images[1], caption="IMAGE 2 · pneumonia2.png", width="stretch")
        st.caption("Fixed educational images sent to Gemini. This demonstration is not a diagnostic tool.")

        left, right = st.columns(2, gap="large")
        with left:
            st.subheader("A · Baseline")
            prompt_breakdown(image_demo["baseline"])
            st.code(image_demo["baseline"]["prompt"], language="text")
            with st.expander("System instruction"):
                st.code(image_demo["baseline"].get("system") or "None", language="text")
            run_button(
                "xray_baseline",
                image_demo["baseline"]["prompt"],
                image_demo["baseline"].get("system", ""),
                images,
                label="Run baseline prompt",
            )
        with right:
            st.subheader("B · Engineered")
            prompt_breakdown(image_demo["engineered"])
            st.code(image_demo["engineered"]["prompt"], language="text")
            with st.expander("System instruction"):
                st.code(image_demo["engineered"].get("system") or "None", language="text")
            run_button(
                "xray_engineered",
                image_demo["engineered"]["prompt"],
                image_demo["engineered"].get("system", ""),
                images,
                label="Run engineered prompt",
            )
        st.divider()
        comparison_lens(image_demo.get("compare", ["Compare structure, evidence boundaries, uncertainty, and safety."]))

st.divider()
st.caption("Built for teaching. Powered by the Gemini Developer API. Free-tier availability and limits depend on Google's current terms and your project.")
