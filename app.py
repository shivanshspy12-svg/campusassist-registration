from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)

# SAMPLE RULES FOR A STUDENT PROJECT ONLY. Replace with your college's official rules.
COURSES = {
    "Artificial Intelligence & Machine Learning (AIML)": {"short":"AIML", "cgpa":8.5, "credits":60, "about":"AI, machine learning, neural networks, and intelligent applications."},
    "Cybersecurity": {"short":"Cybersecurity", "cgpa":8.0, "credits":50, "about":"Network security, ethical hacking, digital forensics, and secure systems."},
    "Data Science": {"short":"Data Science", "cgpa":7.5, "credits":45, "about":"Statistics, data analysis, visualization, and predictive modelling."},
    "Internet of Things (IoT)": {"short":"IoT", "cgpa":7.0, "credits":40, "about":"Connected devices, sensors, embedded systems, and edge computing."},
    "Information Technology (IT)": {"short":"IT", "cgpa":6.5, "credits":30, "about":"Software systems, databases, networking, and IT infrastructure."},
    "Cloud Computing": {"short":"Cloud Computing", "cgpa":7.0, "credits":40, "about":"Cloud platforms, deployment, distributed systems, and DevOps."},
    "Software Engineering": {"short":"Software Engineering", "cgpa":6.5, "credits":30, "about":"Software design, testing, requirements, and project development."},
    "Full Stack Development": {"short":"Full Stack", "cgpa":6.5, "credits":30, "about":"Frontend, backend, APIs, databases, and web applications."},
    "Computer Networks": {"short":"Computer Networks", "cgpa":6.5, "credits":30, "about":"Network architecture, protocols, routing, and communications."},
    "Robotics & Automation": {"short":"Robotics", "cgpa":7.5, "credits":45, "about":"Robotics, control systems, automation, and intelligent machines."}
}

FAQS = [
("how do i register registration process steps", "To register: 1) Enter your first name, last name, roll number, division, email and phone. 2) Select your current semester (5th or above). 3) Enter CGPA from 1.00 to 10.00 and completed credits from 1 to 100. 4) Choose a specialization. 5) Click Check Eligibility, review the result, then click Submit Registration. This demo does not save data to your college system."),
("what cgpa is required for aiml artificial intelligence machine learning", "For this demo, AIML requires a minimum CGPA of 8.50/10.00 and at least 60 completed credits. These are example values, not official college policy."),
("how many credits are required for aiml", "For this demo, AIML requires at least 60 completed credits and CGPA of 8.50/10.00. Please confirm the actual criteria with your college."),
("what cgpa and credits for cybersecurity cyber security", "For this demo, Cybersecurity requires CGPA of at least 8.00/10.00 and 50 completed credits."),
("what cgpa and credits for data science", "For this demo, Data Science requires CGPA of at least 7.50/10.00 and 45 completed credits."),
("what cgpa and credits for iot internet of things", "For this demo, IoT requires CGPA of at least 7.00/10.00 and 40 completed credits."),
("what cgpa and credits for it information technology", "For this demo, Information Technology requires CGPA of at least 6.50/10.00 and 30 completed credits."),
("what cgpa and credits for cloud computing", "For this demo, Cloud Computing requires CGPA of at least 7.00/10.00 and 40 completed credits."),
("what cgpa and credits for software engineering", "For this demo, Software Engineering requires CGPA of at least 6.50/10.00 and 30 completed credits."),
("what cgpa and credits for full stack development", "For this demo, Full Stack Development requires CGPA of at least 6.50/10.00 and 30 completed credits."),
("what cgpa and credits for computer networks", "For this demo, Computer Networks requires CGPA of at least 6.50/10.00 and 30 completed credits."),
("what cgpa and credits for robotics automation", "For this demo, Robotics & Automation requires CGPA of at least 7.50/10.00 and 45 completed credits."),
("what is cgpa", "CGPA means Cumulative Grade Point Average. Enter the CGPA shown on your latest official grade report, on a 10-point scale from 1.00 to 10.00."),
("what are completed credits course credits", "Completed credits are the academic credits you have earned so far according to your transcript. Enter a whole number from 1 to 100. Each specialization's minimum shown here is a demo requirement."),
("which semester can apply fifth semester and above", "This form accepts semester 5 and above. Choose 5th, 6th, 7th, 8th, 9th or 10th semester. Your actual programme may not offer all these semesters."),
("what courses are available list specialization options", "The demo offers AIML, Cybersecurity, Data Science, IoT, Information Technology, Cloud Computing, Software Engineering, Full Stack Development, Computer Networks, and Robotics & Automation."),
("which specialization should i choose best course", "Choose based on your interests: AIML for AI and predictive systems; Cybersecurity for digital defence; Data Science for analytics; IoT for sensors and connected devices; IT for broad technology systems; Cloud Computing for cloud platforms; Software Engineering or Full Stack for software and web apps. Compare eligibility and your college syllabus too."),
("what is aiml", "AIML combines artificial intelligence and machine learning to build systems that learn from data. Topics often include Python, statistics, machine learning, neural networks, and responsible AI."),
("what is cybersecurity", "Cybersecurity protects devices, networks, applications and data. Topics may include network security, secure coding, ethical hacking, incident response and digital forensics."),
("what is data science", "Data Science uses statistics, programming and domain knowledge to extract insights from data. It often includes Python, SQL, data visualization, machine learning and communicating results."),
("what is iot", "IoT connects physical devices using sensors, embedded systems and networks so they can collect and exchange data."),
("what if not eligible low cgpa credits", "If you are not eligible in this demo, check that your CGPA and completed credits are correct. The demo cannot approve exceptions. Ask your department about official criteria, improvement options or appeals."),
("can i change specialization course after selecting", "Yes. Change the specialization dropdown and check eligibility again before submitting. Changes after official college registration may need department approval."),
("is this official does it save data database", "No. This is a student-project demo. It validates the form and displays a result, but it does not save student records, reserve a seat or submit an official college registration."),
("what documents required", "Commonly requested documents may include a student ID, latest marksheet, fee receipt or institution-specific forms. The exact list depends on your college, so check its official notice."),
("hello hi hey", "Hi! I'm CampusAssist, your specialization registration helper. Ask about registration steps, CGPA cut-offs, required credits, semesters, or course choices."),
("help what can you answer", "I can help with form fields, registration steps, demo CGPA and credit cut-offs, semester options, specialization comparisons and common form errors. Try “What CGPA is required for AIML?” or “How do I register?”")
]
FAQ_Q = [x[0] for x in FAQS]
FAQ_A = [x[1] for x in FAQS]
VECTORIZER = TfidfVectorizer(ngram_range=(1,2), stop_words="english")
FAQ_MATRIX = VECTORIZER.fit_transform(FAQ_Q)

def normalize(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", (s or "").lower())).strip()

def chatbot_reply(message):
    text = normalize(message)
    if not text:
        return "Type a question about registration, CGPA, credits, semesters or specializations."
    # Dynamic requirements answers support many natural phrasings.
    aliases = [
        (["artificial intelligence", "machine learning", "aiml", "ai ml"], "Artificial Intelligence & Machine Learning (AIML)"),
        (["cybersecurity", "cyber security", "cyber"], "Cybersecurity"),
        (["data science", "datascience"], "Data Science"),
        (["internet of things", "iot"], "Internet of Things (IoT)"),
        (["information technology", " it "], "Information Technology (IT)"),
        (["cloud computing", "cloud"], "Cloud Computing"),
        (["software engineering"], "Software Engineering"),
        (["full stack", "fullstack"], "Full Stack Development"),
        (["computer networks", "networking"], "Computer Networks"),
        (["robotics", "automation"], "Robotics & Automation")
    ]
    padded = f" {text} "
    found = None
    for terms, name in aliases:
        if any(term in padded for term in terms):
            found = name
            break
    asks_requirement = any(w in text for w in ["cgpa","gpa","credit","credits","eligible","eligibility","required","requirement","cutoff","cut off","minimum"])
    if found and asks_requirement:
        r = COURSES[found]
        if "credit" in text and any(w in text for w in ["cgpa","gpa"]):
            return f"For {found}, the demo minimum is CGPA {r['cgpa']:.2f}/10.00 and {r['credits']} completed credits. These are illustrative values, not official college rules."
        if "credit" in text:
            return f"For {found}, the demo minimum is {r['credits']} completed credits. The CGPA minimum is {r['cgpa']:.2f}/10.00. Confirm official rules with your college."
        return f"For {found}, the demo minimum CGPA is {r['cgpa']:.2f}/10.00 and at least {r['credits']} completed credits. These are sample values, not official college policy."
    if any(w in text for w in ["all courses","list courses","course list","specialization options","available courses","list all"]):
        return "Demo specialization requirements:\\n" + "\\n".join(f"• {n}: CGPA ≥ {r['cgpa']:.2f}, credits ≥ {r['credits']}" for n,r in COURSES.items()) + "\\nThese are sample values only."
    scores = cosine_similarity(VECTORIZER.transform([text]), FAQ_MATRIX).flatten()
    best = int(scores.argmax())
    if scores[best] >= 0.11:
        return FAQ_A[best]
    return ("I can help with registration steps, CGPA and credit requirements, semesters 5+, course comparisons, and form issues. "
            "Try asking a more specific question such as “What CGPA is required for AIML?”, “How many credits for Cybersecurity?”, or “How do I register?”. "
            "For official college rules, confirm with your academic office.")

def eligibility(semester, cgpa, credits, course):
    rule = COURSES.get(course)
    if not rule:
        return {"eligible":False, "message":"Please choose a valid specialization."}
    issues = []
    if semester < 5: issues.append("You must be in semester 5 or above.")
    if cgpa < rule["cgpa"]: issues.append(f"Minimum demo CGPA is {rule['cgpa']:.2f}.")
    if credits < rule["credits"]: issues.append(f"Minimum demo completed credits are {rule['credits']}.")
    if issues:
        return {"eligible":False, "message":"Not eligible under demo rules: " + " ".join(issues), "requirements":rule}
    return {"eligible":True, "message":f"You meet the demo requirements for {course}. Verify official college rules before final registration.", "requirements":rule}

@app.route("/")
def home():
    return render_template("index.html", courses=COURSES)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    return jsonify({"answer":chatbot_reply(str(data.get("message","")))})

@app.route("/api/eligibility", methods=["POST"])
def check_eligibility():
    data = request.get_json(silent=True) or {}
    try:
        sem, cgpa, credits = int(data.get("semester",0)), float(data.get("cgpa",0)), int(data.get("credits",0))
    except (ValueError, TypeError):
        return jsonify({"ok":False,"message":"Enter valid semester, CGPA and credits."}), 400
    if not 1 <= cgpa <= 10:
        return jsonify({"ok":False,"message":"CGPA must be from 1.00 to 10.00."}), 400
    if not 1 <= credits <= 100:
        return jsonify({"ok":False,"message":"Completed credits must be from 1 to 100."}), 400
    return jsonify({"ok":True, **eligibility(sem,cgpa,credits,data.get("course",""))})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    fields = ["first_name","last_name","roll_no","division","email","phone","semester","cgpa","credits","course"]
    if any(not str(data.get(k,"")).strip() for k in fields):
        return jsonify({"ok":False,"message":"Please complete all required fields."}), 400
    email = str(data["email"]).strip()
    phone = re.sub(r"\D","",str(data["phone"]))
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"ok":False,"message":"Enter a valid email address."}), 400
    if len(phone) != 10:
        return jsonify({"ok":False,"message":"Enter a valid 10-digit phone number."}), 400
    try:
        semester, cgpa, credits = int(data["semester"]), float(data["cgpa"]), int(data["credits"])
    except (ValueError, TypeError):
        return jsonify({"ok":False,"message":"Check semester, CGPA and credits."}), 400
    if not 5 <= semester <= 10:
        return jsonify({"ok":False,"message":"Select semester 5th or above."}), 400
    if not 1 <= cgpa <= 10 or not 1 <= credits <= 100:
        return jsonify({"ok":False,"message":"CGPA must be 1.00–10.00 and credits must be 1–100."}), 400
    result = eligibility(semester,cgpa,credits,data["course"])
    return jsonify({"ok":True,"eligible":result["eligible"],"message":result["message"],
                    "student":{"first_name":data["first_name"],"last_name":data["last_name"],"roll_no":data["roll_no"],
                    "division":data["division"],"email":email,"phone":phone,"semester":semester,
                    "cgpa":cgpa,"credits":credits,"course":data["course"]}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
