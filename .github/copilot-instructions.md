---
description: "Instructions for implementing the M1 assignment."
applyTo: "**"
---
# AEPIL1 | Assignment

HENRY ㅤ

## Context & Objectives

You are an engineer on a small product team building a helper for
customer-support agents. The helper must return a concise JSON response
for any incoming question so downstream systems can display an answer, a
confidence estimate, and recommended actions. The team also needs
per-query metrics (tokens, latency, estimated USD cost) to monitor
usage.

**Objectives (what you will deliver and why it matters):**

- Implement a runnable script or minimal endpoint that accepts a user
  question and returns valid JSON with named fields (*answer*,
  *confidence*, *actions*, *etc.*). This produces a stable contract for
  downstream systems.

- Log per-run metrics: *tokens* (prompt / completion / total),
  *latency\_ms*, and *estimated\_cost\_usd*. This enables cost and
  performance monitoring.

- Apply **at least** one explicit prompt engineering technique
  (instruction-based template, few-shot, chain-of-thought trimming, or
  self-consistency) and document why it was chosen.

- Provide a short English report (1–2 pages) describing architecture,
  prompt technique, sample metrics, and trade-offs.

- Provide at least one automated test (e.g., JSON validation or token
  counting). **Optional:** implement a safety/moderation fallback for
  adversarial inputs.

**Why this matters:** structured outputs + metrics + documented prompt
choices are core skills for reliable ML/AI engineering and prepare you
for retrieval-augmented systems.

## Assignment

Develop a *"****Multi-Task Text Utility****"* application that takes a
user question and returns a JSON output. Apply the OpenAI API using at
least one prompt engineering technique learned in class. Track and
report **at least three metrics**, such as *cost*, *tokens used*, and
*latency*.  
  
**Bonus:** support handling of adversarial prompts to test safety.

## Project Deliverables and Submission Requirements

Submit via a public Git repository link of the repository. Ensure the
repository is self-contained and runnable.

## Expected repository structure

|  Deliverable              |  Filename / Format                                         |  Minimum Content                                                                                                          | 
|---------------------------|------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
|  Runnable app or script   |  src/run_query.py or app/endpoint.py (or notebook .ipynb)  |  Accept a user question; call OpenAI API; return valid JSON; print/save output.                                           | 
|  Prompt template(s)       |  prompts/main_prompt.txt (or .md)                          |  Instruction-based prompt; any few-shot examples; JSON schema instructions.                                               | 
|  Metrics log              |  metrics/metrics.csv or metrics/metrics.json               |  Per run: timestamp, tokens_prompt, tokens_completion, total_tokens, latency_ms, estimated_cost_usd.                      | 
|  Short report             |  reports/PI_report_en.md (1–2 pages)                       |  Architecture overview, prompt technique(s) used and why, metrics summary with sample results, challenges, improvements.  | 
|  README                   |  README.md                                                 |  Setup, environment variables, run commands, how to reproduce metrics, known limitations.                                 | 
|  Tests                    |  tests/test_core.py                                        |  At least one test (e.g., token counting or JSON schema validation) with run instructions.                                | 
|  Safety handling (bonus)  |  src/safety.py + docs in report                            |  Moderation step or fallback; sample adversarial prompt and outcome; logging of decisions                                 | 

## Submission checklist

- API key usage documented via environment variable (OPENAI\_API\_KEY).
  Provide *.env.example*.

- At least one recorded run producing JSON and metrics.

- Report and README complete and consistent.

