# Ethiopian Mobile Banking App Analytics: AI-Powered Review Analysis

*Leveraging NLP to transform user feedback into actionable banking insights*

## 📌 Table of Contents
- [Project Overview](#-project-overview)
- [Technology Stack](#-technology-stack)
- [System Requirements](#-system-requirements)
- [Setup Guide](#-setup-guide)
- [Workflow Pipeline](#-workflow-pipeline)
- [Key Deliverables](#-key-deliverables)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## 🌐 Project Overview
This enterprise-grade analytics solution extracts, processes, and visualizes customer sentiment from Google Play Store reviews for three major Ethiopian banks:
- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA) 
- Dashen Bank

**Business Value**: Identifies UX pain points, feature demands, and competitive positioning to drive digital banking strategy.

## 🛠 Technology Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Core Language | Python | 3.11.9 |
| IDE | VS Code | Latest |
| Shell | PowerShell | 5.1+ |
| NLP | Transformers, spaCy | 4.30.2, 3.6.1 |
| Database | Oracle XE | 21c |
| Visualization | Matplotlib, Seaborn | 3.7.2, 0.12.2 |

## 💻 System Requirements
### Minimum Hardware
- Windows 10/11 (64-bit)
- 8GB RAM (16GB recommended for Oracle)
- 10GB free storage (25GB with Oracle XE)

### Software Prerequisites
1. **Python 3.11.9** (must be exact version):
   ```powershell
   winget install Python.Python.3.11.9
# 🚀 Setup Guide
## 1. Environment Configuration
```
# Create project directory
mkdir ethio-bank-analysis
cd ethio-bank-analysis

# Set up virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Verify Python version
python --version  # Must show 3.11.9
```
## 2. Clone Repository
```
git clone https://github.com/yourusername/banking-app-reviews-analysis.git
cd banking-app-reviews-analysis
```
## 3. Install Dependencies
```
pip install -r requirements.txt

# Additional NLP models
python -m spacy download en_core_web_sm
```
## 4. Database Setup (Oracle XE)
1.Install Oracle XE using default settings

2.Configure environment variables:
```
[System.Environment]::SetEnvironmentVariable('ORACLE_HOME','C:\app\username\product\21c\dbhomeXE', [System.EnvironmentVariableTarget]::User)
```
3. Initialize database:
```
python scripts/database_setup.py
```
# 🔄 Workflow Pipeline
## Phase 1: Data Collection
![alt text](<data collection.png>)
### Execution:
```
python scripts/scrape_reviews.py
python scripts/preprocess_reviews.py
```
## Phase 2: Analysis
```
# Sentiment Analysis
python scripts/sentiment_analysis.py

# Thematic Analysis
python scripts/thematic_analysis.py

# Jupyter Notebook Exploration
jupyter notebook notebooks/analysis.ipynb
```
## Phase 3: Visualization & Reporting