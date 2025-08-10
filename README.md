## 📄 Method and Reasoning PDF

You can access the **Method and Reasoning PDF** in this directory.

[Download Method and Reasoning PDF](./Methods_and_Reasoning.pdf)
## 📦 Prerequisites


Before starting, make sure you have:

* **Docker** installed
* **Git** installed
* **Python 3.12+** environment
* **[uv](https://github.com/astral-sh/uv)** (Python package manager) installed

---

## 1️⃣ Run Qdrant Vector Store

Pull the latest **Qdrant** Docker image and start the container:

```bash
docker pull qdrant/qdrant
docker run -p 4580:4580 qdrant/qdrant
```

Qdrant will now be available at **[http://localhost:4580](http://localhost:4580)**.

---

## 2️⃣ Clone the Repository

```bash
git clone https://github.com/Puzan789/RAG_Tables.git
```

---

## 3️⃣ Install Dependencies

Using **uv**:

```bash
uv sync
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the **project root** and add:

```env
GROQ_MODEL=<your_groq_model>
GROQ_API_KEY=<your_groq_api_key>
GOOGLE_API_KEY=<your_google_api_key>
GOOGLE_EMBEDDINGS_MODEL=<your_google_embeddings_model>
QDRANT_URL="http://localhost:4580"
```

> 💡 Replace the placeholders with your actual credentials.

---

## 5️⃣ Start the Backend API

Run the **FastAPI** server:

```bash
uv run main.py
```

Your backend will be running locally.

---

## 6️⃣ Launch the Frontend

Run the **Streamlit** UI:

```bash
streamlit run st_app.py
```

---

## 🎯 Usage

* Use the **FastAPI endpoints** for programmatic access.
* Use the **Streamlit interface** to submit queries and view results in real time.

