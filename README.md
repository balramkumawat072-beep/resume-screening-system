# ResumeRank AI Screening System

A Streamlit app for screening resumes against a job profile. It lets you define required and preferred skills, paste candidate resumes, generate match scores, shortlist candidates, review missing skills, and export results as CSV.

## Run

Double-click `Run ResumeRank.bat`, or run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

The scoring engine is a transparent local heuristic designed for demos and prototypes. In a production hiring workflow, it should be paired with human review, audit logging, consent controls, and bias testing.
