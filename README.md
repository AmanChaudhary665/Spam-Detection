# 🛡️ CyberGuard: Email Threat Defense & AI Spam Detection System

A modern, multi-vector cybersecurity application combining **Machine Learning (Multinomial Naive Bayes)** with **Rule-Based Heuristic Defense** to inspect emails for spam, phishing signatures, malicious URLs, and hazardous attachments.

---

## 🚀 Key Features & Capabilities

- **🤖 Dual-Layer Threat Architecture:**
  - **Machine Learning Layer:** Multinomial Naive Bayes trained on 5,572 emails (`spam.csv`) with TF-IDF vectorization (7,118 token dimensions) and NLTK Porter Stemming.
  - **Heuristic Threat Layer:** Real-time inspection for 15+ credential-harvesting phishing phrases, suspicious URLs (malicious keywords, risky TLDs, raw IP links), and dangerous double-extension attachments (e.g., `.pdf.exe`).
- **🎯 Dynamic SVG Threat Radar:** Visual circular gauge calculating a unified risk score (0–100) across `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL` severity bands with safety floor heuristics.
- **🖍️ Inline Threat Visualizer:** Color-coded markup rendering detected attack vectors, credential prompts, and suspicious links directly inside the email body.
- **⚡ 5 One-Click Attack & Safe Scenarios:** Instantly test legitimate corporate memos, urgent banking phishing, fake invoices with executable attachments, CEO fraud wire transfers, and lottery prize scams.
- **📁 Bulk Threat Triage & Batch Analyzer:** Upload custom CSV files or run a standardized 8-email benchmark test suite with instant statistics and CSV export.
- **📈 SOC Session Audit Log:** Tracks and analyzes historical scan events, clean vs threat ratios, and allows exporting logs as CSV.
- **🧪 Interactive Model & NLP Lab:** Features an interactive live text preprocessor sandbox demonstrating text cleaning, stopword removal, and stemming in real-time.
- **📋 Multi-Format Export:** Export comprehensive forensic audit reports in formatted plaintext (`.txt`) and structured incident JSON logs (`.json`).

---

## 🛠️ Project Structure

```text
├── .streamlit/
│   └── config.toml         # Custom dark theme configuration
├── venv/                   # Python virtual environment
├── app.py                  # Main CyberGuard Streamlit application
├── train_model.py          # Model training pipeline & evaluation script
├── spam.csv                # SMS/Email spam training dataset (5,572 rows)
├── model.pkl               # Serialized MultinomialNB model
├── vectorizer.pkl          # Serialized TF-IDF vectorizer (7,118 features)
├── requirements.txt        # Project dependencies
└── README.md               # Documentation
```

---

## 💻 How to Run the Application

### 1. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. (Optional) Re-train the Machine Learning Model
```powershell
python train_model.py
```

### 3. Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Dataset & Model Benchmark

- **Dataset:** SMS & Email Spam Collection
- **Total Samples:** 5,572 (4,825 Ham / 747 Spam)
- **Train/Test Split:** 80% / 20% Stratified
- **Test Set Accuracy:** **~98.03%**
- **Inference Latency:** < 50ms

