# MedGuide AI – AI-Powered Hospital Guidance System

## About the Project
MedGuide AI is an AI-powered hospital guidance system that helps patients identify the appropriate hospital department based on their medical reports or symptoms.

The system analyzes the provided information and recommends a suitable department along with its floor and location details. It aims to reduce confusion and make hospital navigation easier for patients.

## Problem Statement
Patients visiting hospitals may find it difficult to identify the correct department or specialist. This is especially challenging for first-time visitors and patients who are unsure about their symptoms or medical reports. MedGuide AI helps simplify this process through AI-based recommendations.

## Key Features
- **Medical Report Analysis:** Upload medical reports in PDF format for analysis.
- **Symptom Analysis:** Enter symptoms manually to get department recommendations.
- **Department Recommendation:** Suggests a suitable hospital department based on the provided information.
- **Floor Guidance:** Displays the department's floor and location details.
- **AI Assistance:** Uses AI to support the recommendation process.

## How It Works

**Report-Based Flow**
1. Upload a medical report.
2. Extract and analyze the report information.
3. Recommend a suitable department.
4. Display the department floor and location.

**Symptom-Based Flow**
1. Enter symptoms.
2. Analyze the entered symptoms.
3. Recommend a suitable department.
4. Display floor and location details.

## Technologies Used

| Technology | Purpose |
|---|---|
| HTML, CSS, JavaScript | Frontend development |
| Python, Flask | Backend development |
| Google Gemini API | AI-based analysis |
| LangGraph | Agent workflow |
| PyMuPDF | PDF text extraction |
| EasyOCR | Text recognition from images |
| SQLite | Database management |

## Project Structure

```text
ai_hospital/
├── backend/
│   ├── agents/
│   ├── database/
│   ├── utils/
│   ├── app.py
│   ├── departments.csv
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── main.html
│   ├── report.html
│   ├── map.html
│   ├── script.js
│   └── style.css
├── .gitignore
└── run.bat
```

## Installation and Execution

1. Clone the repository:

```bash
git clone https://github.com/bhav1219/ai-powered-hospital-guidance-system.git
```

2. Navigate to the project folder:

```bash
cd ai-powered-hospital-guidance-system
```

3. Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

4. Install the required packages:

```bash
pip install -r backend/requirements.txt
```

5. Add your Gemini API key to the `.env` file:

```env
GEMINI_API_KEY=your_api_key
```

6. Run the application using the project's `run.bat` file.

## Social Impact
- Reduces confusion among hospital visitors.
- Helps patients reach the appropriate department.
- Saves time during hospital visits.
- Improves hospital navigation and accessibility.

## Future Enhancements
- Support for multiple hospitals.
- Multilingual symptom input.
- Enhanced hospital navigation.
- Additional department information.

## Disclaimer
AI provides recommendations only; doctors make the final diagnosis. This system does not replace professional medical advice.

## Developer
**Bhavana K**  
Department of Artificial Intelligence and Machine Learning  
Sri Shakthi Institute of Engineering and Technology

## Repository
[GitHub – MedGuide AI](https://github.com/bhav1219/ai-powered-hospital-guidance-system)
