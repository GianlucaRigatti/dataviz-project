# Dashboard

This dashboard can be run either using Docker or a standard Python virtual environment. The complete dashboard is contained in the current `dashboard/` folder, with `requirements.txt` and the `Dockerfile` in the repository root.

## Running with Docker

From the repository root, build the Docker image:

```bash
docker build -t my-dashboard .
```

Run the dashboard:

```bash
docker run -p 8050:8050 my-dashboard
```

The dashboard will be available at:

```text
http://localhost:8050
```

To run it in the background:

```bash
docker run -d -p 8050:8050 --name my-dashboard my-dashboard
```

Stop the dashboard with:

```bash
docker stop my-dashboard
```

## Running with a Python Virtual Environment

From the repository root, create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

**Linux / macOS:**

```bash
source .venv/bin/activate
```

**Windows:**

```powershell
.venv\Scripts\activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Then start the dashboard:

```bash
cd dashboard
python app.py
```

The dashboard will be available at:

```text
http://localhost:8050
```

When finished, you can deactivate the virtual environment with:

```bash
deactivate
```
