# CampusAssist — Specialization Registration Assistant

## Features
- Form fields: first name, last name, roll number, division, email ID, phone number, semester, CGPA, completed credits and specialization choice.
- Semester choices start at 5th semester and go through 10th.
- CGPA validation: 1.00–10.00. Credits validation: 1–100.
- Specializations: AIML, Cybersecurity, Data Science, IoT, IT, Cloud Computing, Software Engineering, Full Stack Development, Computer Networks, and Robotics & Automation.
- Eligibility checker and NLP FAQ chatbot with course-aware answers.

## Sample requirements — not official college policy
AIML: CGPA 8.50 and 60 credits; Cybersecurity: 8.00 and 50; Data Science: 7.50 and 45; IoT: 7.00 and 40; IT: 6.50 and 30; Cloud Computing: 7.00 and 40; Software Engineering: 6.50 and 30; Full Stack: 6.50 and 30; Computer Networks: 6.50 and 30; Robotics & Automation: 7.50 and 45.
Update the `COURSES` rules in `app.py` and `rules` in `static/script.js` to match your college's approved requirements.

## Deploy online on Render (GitHub required)
1. Extract this ZIP on your computer.
2. Create a new GitHub repository and upload the contents of the `ai_registration_flask` folder (including `app.py`, `requirements.txt`, `templates/`, and `static/`) to the repository root.
3. On Render, choose New > Web Service and connect that repository.
4. Set Build Command to `pip install -r requirements.txt`.
5. Set Start Command to `gunicorn app:app`.
6. Choose a plan and deploy. Render will provide a public `onrender.com` URL.

Free Render services may sleep after 15 minutes of inactivity. The first request after sleeping can take longer to load.

## Chatbot scope
The chatbot uses TF-IDF/cosine-similarity NLP with course-aware rules and a broad FAQ set. It answers common questions about registration, requirements, credits, semesters, and specialization choices. It is not an unrestricted large language model; unknown questions receive a helpful redirect. An LLM API would be needed for general open-domain answers.

## Important limitations
This is a demonstration, not an official college system. The registration endpoint validates and returns a result but does not save records, reserve a seat, or submit an official registration. Use fake student details during public demos.
