import csv
import html
import io
import re
from collections import Counter

import streamlit as st


SAMPLE_CANDIDATES = [
    {
        "name": "Aanya Mehta",
        "resume": (
            "Frontend engineer with 5 years building React and TypeScript applications. "
            "Led a design system migration, wrote unit and integration testing, improved "
            "Core Web Vitals, and partnered with product teams on accessible workflows "
            "using HTML, CSS, REST APIs, and component libraries."
        ),
    },
    {
        "name": "Rohan Iyer",
        "resume": (
            "Software developer focused on Java, Spring Boot, SQL, and backend APIs. "
            "Built microservices, dashboards, and deployment automation. Some JavaScript "
            "experience with internal admin screens, CSS fixes, and API integrations."
        ),
    },
    {
        "name": "Maya Shah",
        "resume": (
            "UI engineer with React, JavaScript, HTML, CSS, Figma collaboration, "
            "accessibility audits, performance profiling, Jest tests, Storybook, design "
            "systems, and GraphQL APIs. Mentored peers and owned candidate-facing product surfaces."
        ),
    },
    {
        "name": "Kabir Sharma",
        "resume": (
            "Frontend developer with 3 years of experience building dashboards in React, "
            "JavaScript, HTML, and CSS. Worked with REST APIs, reusable components, Git, "
            "responsive layouts, and bug fixing. Recently started using TypeScript and Jest."
        ),
    },
    {
        "name": "Sara Fernandes",
        "resume": (
            "Full-stack engineer with 6 years of experience across React, TypeScript, Node.js, "
            "PostgreSQL, API integrations, automated testing, and performance optimization. "
            "Built accessible customer portals and collaborated closely with designers."
        ),
    },
    {
        "name": "Dev Patel",
        "resume": (
            "Recent computer science graduate with internship projects in HTML, CSS, JavaScript, "
            "React, Firebase, and UI testing. Built a portfolio site, task manager, and weather "
            "app using public APIs. Strong learner with product and teamwork experience."
        ),
    },
    {
        "name": "Nisha Rao",
        "resume": (
            "QA automation engineer with Selenium, Cypress, JavaScript, regression testing, "
            "test planning, CI pipelines, and API validation. Comfortable reviewing HTML and CSS "
            "issues, but limited production React development experience."
        ),
    },
    {
        "name": "Arjun Menon",
        "resume": (
            "Backend engineer with 4 years of Python, Django, Flask, SQL, Docker, cloud deployment, "
            "and REST API development. Built internal tools and data pipelines. Basic HTML and CSS "
            "knowledge from admin panel maintenance."
        ),
    },
]


def initialize_state():
    if "candidates" not in st.session_state:
        st.session_state.candidates = []


def split_skills(value):
    return [skill.strip().lower() for skill in value.split(",") if skill.strip()]


def tokenize(value):
    return re.findall(r"[a-z0-9+#.-]+", value.lower())


def phrase_in_text(text, phrase):
    return phrase.lower() in text.lower()


def score_candidate(candidate, job_description, required_skills, preferred_skills):
    resume = candidate["resume"]
    resume_tokens = set(tokenize(resume))
    job_tokens = set(tokenize(job_description))
    required_matches = [skill for skill in required_skills if phrase_in_text(resume, skill)]
    preferred_matches = [skill for skill in preferred_skills if phrase_in_text(resume, skill)]
    keyword_matches = [
        token for token in job_tokens if len(token) > 3 and token in resume_tokens
    ]

    required_score = len(required_matches) / len(required_skills) if required_skills else 0
    preferred_score = len(preferred_matches) / len(preferred_skills) if preferred_skills else 0
    keyword_score = min(len(keyword_matches) / 18, 1) if job_tokens else 0
    experience_score = 1 if re.search(r"\b\d+\+?\s*(years|year|yrs)\b", resume, re.I) else 0.45

    score = round(
        (
            required_score * 0.48
            + preferred_score * 0.22
            + keyword_score * 0.18
            + experience_score * 0.12
        )
        * 100
    )

    return {
        "score": score,
        "matched": sorted(set(required_matches + preferred_matches)),
        "missing": [skill for skill in required_skills if skill not in required_matches],
        "keywords": keyword_matches[:6],
    }


def build_csv(scored_candidates, threshold):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["Candidate", "Score", "Status", "Matched skills", "Missing required skills"]
    )
    for candidate in scored_candidates:
        status = "Shortlisted" if candidate["analysis"]["score"] >= threshold else "Needs review"
        writer.writerow(
            [
                candidate["name"],
                f'{candidate["analysis"]["score"]}%',
                status,
                "; ".join(candidate["analysis"]["matched"]),
                "; ".join(candidate["analysis"]["missing"]),
            ]
        )
    return output.getvalue()


def render_candidate_card(candidate, threshold):
    analysis = candidate["analysis"]
    status = "Shortlisted" if analysis["score"] >= threshold else "Needs review"
    status_class = "shortlisted" if status == "Shortlisted" else "review"
    matched = html.escape(", ".join(analysis["matched"]) if analysis["matched"] else "No direct skill matches")
    missing = html.escape(", ".join(analysis["missing"]) if analysis["missing"] else "No required skills missing")
    keywords = html.escape(", ".join(analysis["keywords"]) if analysis["keywords"] else "No keyword overlap")
    name = html.escape(candidate["name"])
    preview = html.escape(
        f'{candidate["resume"][:260]}{"..." if len(candidate["resume"]) > 260 else ""}'
    )

    st.markdown(
        f"""
        <div class="candidate-card">
            <div class="candidate-top">
                <h3>{name}</h3>
                <span class="pill {status_class}">{status}</span>
            </div>
            <div class="score">{analysis["score"]}%</div>
            <div class="bar"><span style="width:{analysis["score"]}%"></span></div>
            <p><strong>Matched evidence:</strong> {matched}</p>
            <p><strong>Missing:</strong> {missing}</p>
            <p><strong>Job signals:</strong> {keywords}</p>
            <p class="resume-preview">{preview}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                linear-gradient(rgba(244, 247, 248, 0.92), rgba(244, 247, 248, 0.96)),
                url("https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1800&q=80");
            background-size: cover;
            background-attachment: fixed;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.94);
            border-right: 1px solid #dce5e8;
        }

        h1, h2, h3 {
            color: #1c2528 !important;
            letter-spacing: 0;
        }

        p, label, span, div {
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: #1c2528 !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {
            color: #1c2528 !important;
            background: #ffffff !important;
            border: 1px solid #b9c7cc !important;
            caret-color: #1c2528 !important;
        }

        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {
            color: #7b8b92 !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] [data-baseweb="slider"] span {
            color: #1c2528 !important;
        }

        .hero {
            padding: 1.1rem 0 1.4rem;
        }

        .eyebrow {
            margin: 0;
            color: #4d6269 !important;
            font-size: .78rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: .15rem 0 .35rem;
            font-size: 2.4rem;
            color: #1c2528 !important;
        }

        .hero p {
            max-width: 760px;
            color: #405157 !important;
            line-height: 1.55;
        }

        .metric-card, .candidate-card, .guardrail {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #dce5e8;
            border-radius: 8px;
            box-shadow: 0 16px 40px rgba(28, 37, 40, 0.08);
        }

        .metric-card {
            padding: 1rem;
            min-height: 118px;
        }

        .metric-card span {
            display: block;
            font-size: 1.85rem;
            font-weight: 900;
            color: #1c2528;
        }

        .metric-card p {
            margin: .35rem 0 0;
            color: #52656c !important;
            font-weight: 700;
        }

        [data-testid="stRadio"] label,
        [data-testid="stRadio"] p,
        [data-testid="stRadio"] span {
            color: #1c2528 !important;
        }

        [data-testid="stAlert"] p {
            color: #2563eb !important;
        }

        .candidate-card {
            min-height: 365px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .candidate-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
        }

        .candidate-top h3 {
            margin: 0;
            font-size: 1.08rem;
        }

        .pill {
            border-radius: 999px;
            padding: .28rem .55rem;
            font-size: .75rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .shortlisted {
            color: #0f7b61;
            background: #dff4ed;
        }

        .review {
            color: #a76005;
            background: #fff1d6;
        }

        .score {
            margin-top: .9rem;
            font-size: 2.35rem;
            font-weight: 950;
            color: #1c2528;
        }

        .bar {
            height: 10px;
            margin: .55rem 0 1rem;
            overflow: hidden;
            background: #e8eef0;
            border-radius: 999px;
        }

        .bar span {
            display: block;
            height: 100%;
            background: linear-gradient(90deg, #0f7b61, #2563eb);
        }

        .candidate-card p {
            color: #405157;
            line-height: 1.45;
        }

        .resume-preview {
            color: #617178 !important;
        }

        .guardrail {
            padding: 1rem;
            margin-top: 1rem;
            background: rgba(28, 37, 40, .92);
        }

        .guardrail h3 {
            margin-top: 0;
            color: white;
        }

        .guardrail p {
            color: #d4dee1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="ResumeRank AI Screening", page_icon="RR", layout="wide")
    initialize_state()
    apply_styles()

    with st.sidebar:
        st.title("ResumeRank")
        st.caption("AI resume screening system")

        st.subheader("Role Profile")
        role_title = st.text_input("Job title", value="Frontend Engineer")
        job_description = st.text_area(
            "Job description",
            value=(
                "We are hiring a frontend engineer to build accessible, high-performance React "
                "applications. The role requires JavaScript, TypeScript, React, HTML, CSS, "
                "testing, APIs, component systems, collaboration, and product thinking."
            ),
            height=180,
        )
        required_skills_text = st.text_input(
            "Required skills", value="JavaScript, TypeScript, React, CSS, HTML, testing"
        )
        preferred_skills_text = st.text_input(
            "Preferred skills", value="accessibility, performance, design systems, APIs"
        )
        threshold = st.slider("Shortlist threshold", 45, 95, 72)

        st.divider()
        st.subheader("Add Candidate")
        candidate_name = st.text_input("Candidate name", placeholder="e.g. Aanya Mehta")
        candidate_resume = st.text_area(
            "Resume text",
            placeholder="Paste resume summary, skills, projects, and experience here",
            height=170,
        )

        col_add, col_sample = st.columns(2)
        with col_add:
            if st.button("Add", use_container_width=True, type="primary"):
                if candidate_resume.strip():
                    st.session_state.candidates.insert(
                        0,
                        {
                            "name": candidate_name.strip() or "Unnamed Candidate",
                            "resume": candidate_resume.strip(),
                        },
                    )
                    st.rerun()
                st.warning("Paste resume text before adding a candidate.")

        with col_sample:
            if st.button("Samples", use_container_width=True):
                st.session_state.candidates = SAMPLE_CANDIDATES.copy()
                st.rerun()

        if st.button("Reset candidates", use_container_width=True):
            st.session_state.candidates = []
            st.rerun()

    required_skills = split_skills(required_skills_text)
    preferred_skills = split_skills(preferred_skills_text)
    scored_candidates = [
        {
            **candidate,
            "analysis": score_candidate(
                candidate, job_description, required_skills, preferred_skills
            ),
        }
        for candidate in st.session_state.candidates
    ]

    shortlisted = [
        candidate
        for candidate in scored_candidates
        if candidate["analysis"]["score"] >= threshold
    ]
    average_score = (
        round(sum(candidate["analysis"]["score"] for candidate in scored_candidates) / len(scored_candidates))
        if scored_candidates
        else 0
    )
    skill_counts = Counter(
        skill for candidate in scored_candidates for skill in candidate["analysis"]["matched"]
    )
    top_skill = skill_counts.most_common(1)[0][0] if skill_counts else "-"

    st.markdown(
        f"""
        <section class="hero">
            <p class="eyebrow">Candidate Intelligence</p>
            <h1>{html.escape(role_title)} Screening</h1>
            <p>Rank resumes against role-specific skills, inspect evidence, shortlist candidates, and export a transparent review file.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metrics = [
        ("Candidates", len(scored_candidates)),
        ("Shortlisted", len(shortlisted)),
        ("Average match", f"{average_score}%"),
        ("Top matched skill", top_skill),
    ]
    for column, (label, value) in zip(metric_cols, metrics):
        with column:
            st.markdown(
                f'<div class="metric-card"><span>{value}</span><p>{label}</p></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    filter_choice = st.radio(
        "Candidate view",
        ["All", "Shortlisted", "Needs review"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    if filter_choice == "Shortlisted":
        visible_candidates = shortlisted
    elif filter_choice == "Needs review":
        visible_candidates = [
            candidate
            for candidate in scored_candidates
            if candidate["analysis"]["score"] < threshold
        ]
    else:
        visible_candidates = scored_candidates

    if scored_candidates:
        csv_data = build_csv(scored_candidates, threshold)
        st.download_button(
            "Export CSV",
            data=csv_data,
            file_name="resume-screening-results.csv",
            mime="text/csv",
        )

    if visible_candidates:
        columns = st.columns(3)
        for index, candidate in enumerate(visible_candidates):
            with columns[index % 3]:
                render_candidate_card(candidate, threshold)
    else:
        st.info("No candidates in this view. Add a resume or load sample candidates to start screening.")

    st.markdown(
        """
        <div class="guardrail">
            <h3>Review Guardrails</h3>
            <p>Scores use role-related skill evidence, job keyword overlap, and experience signals from resume text. Names and demographic hints are not scoring inputs. Use the result as decision support, not as an automated hiring decision.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
