# Support Agent Assistant

## Setup
### Installation and Uninstallation
You can then install your package in “editable” mode by running from the same directory:

```bash
pip install -e .
```

Uninstallation can be done via pip:

```bash
pip uninstall support-agent
```

### Environment Variables
Create a `.env` file in the root directory of the project and add your OpenAI API key as follows:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxx...xxxxxxxxxxxxx
```
## Usage
After installing the package, you can use it from the command line. Here’s an example command to get an answer from the support agent assistant, the `--metrics` flag is used to optionally print the performance metrics to the terminal:

```bash
support-agent --metrics "How can I reset my password if I've forgotten it?"
```

You can find a sample notebook with the output in [`notebooks/notebook.ipynb`](notebooks/notebook.ipynb).

**You should get an answer similar to this:**  

```markdown
Answer:
-------
```
```json
{
    "answer": "To reset a forgotten password, use the \u201cForgot password\u201d link on the sign-in page. Enter the email address (or username) associated with your account when prompted. You will receive an email with a secure reset link or one-time code\u2014follow the instructions in that message to create a new password. If you don\u2019t receive the email, check your spam/junk folder and any other email addresses you may have used.",
    "actions": [
        "Go to the sign-in page and click \u201cForgot password\u201d",
        "Enter the email address or username tied to the account",
        "Open the reset email and follow the link or enter the one-time code",
        "Choose a strong new password and confirm it",
        "If no email arrives, check spam/junk and alternate email addresses",
        "If you can\u2019t access that email or don\u2019t receive the reset email after 15 minutes, contact support with your account details (email, username, last successful login)"
    ],
    "confidence": 0.92
}
```
```markdown
Metrics:
-------
```
```json
{
    "timestamp": 1762111045,
    "tokens_prompt": 182,
    "tokens_completion": 208,
    "total_tokens": 390,
    "latency_ms": 3887.35032081604,
    "estimated_cost_usd": 0.0004615
}
```

The metrics are logged in the [`metrics/metrics.csv`](metrics/metrics.csv) file, and will look like this:

| timestamp           | tokens_prompt | tokens_completion | total_tokens | latency_ms       | estimated_cost_usd |
|---------------------|---------------|-------------------|--------------|------------------|--------------------|
| 2025-11-02T21:17:25 | 182           | 208               | 390          | 3887.35032081604 | 0.0004615          |

## Testing

To run the tests for the package, use the following command:

```bash
pytest -vv tests/
```
## Limitations
- The assistant serves as a demo. It doesn't have access to a real knowledge base or customer data.

## Project Report
See [Project Report](reports/PI_report_en.md) for detailed information about the project architecture and development.
