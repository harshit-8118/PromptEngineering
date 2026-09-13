NOTE = """Mr. Iyer, 68M. Admitted for community-acquired pneumonia. IV Augmentin for 3 days, afebrile for 48 hours, chest X-ray improving. Discharged on oral Augmentin for 5 days. OPD follow-up in 1 week."""

TEXT_DEMOS = {
    "Zero-shot vs few-shot": {
        "teaching_point": "Examples reduce ambiguity when a team needs a precise house style.",
        "compare": [
            "Does the answer follow the department shorthand rather than inventing its own format?",
            "Is it exactly one line with no preamble?",
            "Are all supplied facts preserved without additions?",
        ],
        "baseline": {
            "components": ["Task", "Context", "Zero-shot"],
            "system": "",
            "prompt": f"Convert this discharge note into a one-line handover.\n\nNOTE:\n{NOTE}",
        },
        "engineered": {
            "components": ["Task", "Context", "Few-shot examples", "Output format"],
            "system": "You format fictional clinical training notes. Preserve supplied facts; do not invent details.",
            "prompt": f"""TASK:
Convert the final note into the same one-line handover style as the examples.

EXAMPLES:
Input: Mrs. Rao, 72F. UTI. IV then oral antibiotics, day 3. Afebrile 48h. Discharged home. OPD in 1 week.
Output: Mrs. Rao, 72F — UTI → IV/oral abx d3, afebrile 48h, D/C home, OPD f/u 1wk.

Input: Mr. Sundar, 45M. Appendicitis. Laparoscopic appendectomy. Uncomplicated. Discharged postoperative day 2. Wound check in 1 week.
Output: Mr. Sundar, 45M — appendicitis → lap appy, uncomplicated, D/C POD2, wound check 1wk.

NEW INPUT:
{NOTE}

OUTPUT:
Return exactly one line and no preamble.""",
        },
    },
    "Vague vs specific instructions": {
        "teaching_point": "Audience, scope, length, and exclusions turn a broad request into a usable deliverable.",
        "compare": [
            "Which response is calibrated to a defined audience and reading level?",
            "Which one reliably covers all three requested topics?",
            "Which answer has a measurable length and structure?",
        ],
        "baseline": {
            "components": ["Task"],
            "system": "",
            "prompt": "Explain type 2 diabetes to my patient.",
        },
        "engineered": {
            "components": ["Task", "Audience context", "Constraints", "Output format"],
            "system": "You are a careful health educator. Use supportive language and never diagnose or change treatment.",
            "prompt": """AUDIENCE:
A fictional 54-year-old auto-rickshaw driver, newly diagnosed with type 2 diabetes, anxious about whether the condition affects driving.

TASK:
Explain what type 2 diabetes means and why clinicians often begin with lifestyle changes and tablets.

CONSTRAINTS:
- Grade-6 English; no unexplained jargon
- 120–150 words
- Reassure without promising an outcome
- Do not give individualized treatment advice

FORMAT:
Use three short sections: What it means; What happens next; Driving and safety.""",
        },
    },
    "Persona and system instruction": {
        "teaching_point": "A system instruction can consistently calibrate voice, expertise, and boundaries across user tasks.",
        "compare": [
            "Which response sounds appropriate for a worried patient rather than a textbook?",
            "Does the engineered answer include the requested analogy and safety advice?",
            "Does it stay within 100 words and avoid biochemical jargon?",
        ],
        "baseline": {
            "components": ["Task"],
            "system": "",
            "prompt": "Explain how ACE inhibitors work.",
        },
        "engineered": {
            "components": ["System instruction", "Task", "Audience", "Constraints"],
            "system": "You are a friendly nurse educator speaking to a worried adult patient. Be accurate, calm, and plain-spoken. Do not provide personal medical advice.",
            "prompt": """Explain, in 100 words or fewer, how ACE inhibitors lower blood pressure.
Use one everyday analogy. Mention one common side effect and advise the reader to contact their clinician rather than stopping medicine on their own.
Avoid biochemical pathway terminology and drug dosing.""",
        },
    },
    "Context and structured output": {
        "teaching_point": "Relevant context grounds the response; an explicit format makes the result immediately reusable.",
        "compare": [
            "Does the baseline invent placeholders or details because context is missing?",
            "Does the engineered response use every supplied fact and no unsupported fact?",
            "Is the engineered answer immediately usable as an SMS and within 280 characters?",
        ],
        "baseline": {
            "components": ["Task"],
            "system": "",
            "prompt": "Write a reminder about our clinic event.",
        },
        "engineered": {
            "components": ["System instruction", "Task", "Context", "Constraints", "Output format"],
            "system": "You write concise, accessible community-health communications. Use only facts supplied by the user.",
            "prompt": """CONTEXT:
Event: Community Health Day
Offer: Free screening
Time: Saturday, 9 AM–1 PM
Place: District Hospital, Hall B
Attendees should bring: an ID and medicine list

TASK:
Write an SMS reminder for registered attendees.

CONSTRAINTS:
Maximum 280 characters. Friendly tone. Do not add a phone number or services not listed.

OUTPUT:
Return only the SMS text.""",
        },
    },
}


IMAGE_DEMOS = {
    "Pneumonia X-ray comparison": {
        "teaching_point": "Images alone do not define the task. A structured multimodal prompt specifies scope, comparison criteria, uncertainty, and a usable output format.",
        "compare": [
            "Does the baseline decide its own audience, scope, and terminology?",
            "Does the engineered response compare the same named features for both images?",
            "Does it separate visible observations from interpretation and acknowledge uncertainty?",
            "Does it avoid diagnosis, invented history, treatment advice, and false certainty?",
        ],
        "baseline": {
            "components": ["Two images", "Vague task", "Zero-shot"],
            "system": "",
            "prompt": "Compare these two chest X-rays.",
        },
        "engineered": {
            "components": ["System instruction", "Two labeled images", "Objective", "Comparison criteria", "Evidence boundary", "Output format"],
            "system": """You are a medical-image education assistant helping clinicians discuss prompt design. Describe only visible radiographic features. Do not diagnose, estimate probability, recommend treatment, or invent patient history. State that image interpretation requires a qualified clinician with clinical context.""",
            "prompt": """OBJECTIVE:
Compare IMAGE 1 (pneumonia1.png) and IMAGE 2 (pneumonia2.png) as an educational exercise in visual description.

INSPECT THE SAME FEATURES IN EACH IMAGE:
1. Projection/positioning and image-quality limitations that are visibly assessable
2. Distribution of lung opacity: side, zone, focal versus diffuse
3. Relative symmetry of the lungs
4. Visible pleural-space or support-device findings, only if clearly present

EVIDENCE RULES:
- Separate direct observations from possible interpretations.
- If a feature cannot be assessed, write “Cannot assess from this image.”
- Do not claim that either image proves pneumonia or any other diagnosis.
- Do not infer symptoms, age, cause, severity, prognosis, or treatment.

OUTPUT FORMAT:
Return a compact Markdown table with rows for the four features and columns “IMAGE 1” and “IMAGE 2”. After the table, add exactly two bullets:
- Most visible contrast: one sentence
- Limitation: one sentence explaining that a qualified clinician must interpret imaging with clinical context""",
        },
    },
}
