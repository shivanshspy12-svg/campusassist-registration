const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
const form = $("#registration-form");
const resultBox = $("#registration-result");
const courseSelect = $("#course");
const criteriaBox = $("#course-criteria");
const rules = {
 "Artificial Intelligence & Machine Learning (AIML)":{cgpa:8.5,credits:60,about:"AI, machine learning, neural networks, and intelligent applications."},
 "Cybersecurity":{cgpa:8,credits:50,about:"Network security, ethical hacking, digital forensics, and secure systems."},
 "Data Science":{cgpa:7.5,credits:45,about:"Statistics, data analysis, visualization, and predictive modelling."},
 "Internet of Things (IoT)":{cgpa:7,credits:40,about:"Connected devices, sensors, embedded systems, and edge computing."},
 "Information Technology (IT)":{cgpa:6.5,credits:30,about:"Software systems, databases, networking, and IT infrastructure."},
 "Cloud Computing":{cgpa:7,credits:40,about:"Cloud platforms, deployment, distributed systems, and DevOps."},
 "Software Engineering":{cgpa:6.5,credits:30,about:"Software design, testing, requirements, and project development."},
 "Full Stack Development":{cgpa:6.5,credits:30,about:"Frontend, backend, APIs, databases, and web applications."},
 "Computer Networks":{cgpa:6.5,credits:30,about:"Network architecture, protocols, routing, and communications."},
 "Robotics & Automation":{cgpa:7.5,credits:45,about:"Robotics, control systems, automation, and intelligent machines."}
};
function showResult(message,type="info"){resultBox.hidden=false;resultBox.className=`result-box ${type}`;resultBox.textContent=message;}
function getData(){return {first_name:$("#first-name").value.trim(),last_name:$("#last-name").value.trim(),roll_no:$("#roll-no").value.trim(),division:$("#division").value,email:$("#email").value.trim(),phone:$("#phone").value.trim(),semester:$("#semester").value,cgpa:$("#cgpa").value,credits:$("#credits").value,course:courseSelect.value};}
function validate(){
 if(!form.reportValidity()) return false;
 const d=getData();
 if(!/^\d{10}$/.test(d.phone.replace(/\D/g,""))){showResult("Please enter a valid 10-digit phone number.","error");return false;}
 if(Number(d.cgpa)<1||Number(d.cgpa)>10){showResult("CGPA must be from 1.00 to 10.00.","error");return false;}
 if(!Number.isInteger(Number(d.credits))||Number(d.credits)<1||Number(d.credits)>100){showResult("Completed credits must be a whole number from 1 to 100.","error");return false;}
 if(Number(d.semester)<5||Number(d.semester)>10){showResult("Choose semester 5 or above.","error");return false;}
 return true;
}
function renderCriteria(){
 const course=courseSelect.value, r=rules[course];
 if(!r){criteriaBox.classList.add("hidden");return;}
 criteriaBox.classList.remove("hidden");
 criteriaBox.innerHTML=`<strong>${course.replace(/</g,"&lt;")}</strong><div>${r.about}</div><div class="criteria-pills"><span>Minimum demo CGPA: <b>${r.cgpa.toFixed(2)}/10</b></span><span>Completed credits: <b>${r.credits}+</b></span></div>`;
 resultBox.hidden=true;
}
courseSelect.addEventListener("change",renderCriteria);
$$(".specialization-card").forEach(b=>b.addEventListener("click",()=>{courseSelect.value=b.dataset.course;renderCriteria();$("#registration").scrollIntoView({behavior:"smooth",block:"start"});}));
$("#check-eligibility").addEventListener("click",async()=>{
 if(!validate())return;
 const b=$("#check-eligibility");b.disabled=true;b.textContent="Checking…";
 try{
  const r=await fetch("/api/eligibility",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({semester:getData().semester,cgpa:getData().cgpa,credits:getData().credits,course:getData().course})});
  const d=await r.json();showResult(d.message||"Could not check eligibility.",d.eligible?"success":"error");
 }catch(e){showResult("Could not connect to the app. Make sure the server is running.","error");}
 finally{b.disabled=false;b.innerHTML='Check eligibility <span>→</span>';}
});
form.addEventListener("submit",async e=>{
 e.preventDefault();if(!validate())return;
 const b=$("#submit-registration");b.disabled=true;b.textContent="Checking…";
 try{
  const r=await fetch("/api/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(getData())});
  const d=await r.json();
  if(!r.ok||!d.ok){showResult(d.message||"Please check the form.","error");return;}
  const s=d.student;
  showResult(`Demo registration checked for ${s.first_name} ${s.last_name} (${s.roll_no}), Semester ${s.semester}.\\nSpecialization: ${s.course}\\nResult: ${d.eligible?"MEETS DEMO REQUIREMENTS":"DOES NOT MEET DEMO REQUIREMENTS"}.\\n${d.message}\\n\\nNothing has been saved or submitted to your college.`,d.eligible?"success":"error");
 }catch(e){showResult("Could not connect to the app. Make sure the server is running.","error");}
 finally{b.disabled=false;b.innerHTML='Submit registration <span>↗</span>';}
});
const chatMessages=$("#chat-messages");
function addChat(text,who){
 const el=document.createElement("div");el.className=who==="user"?"chat-message-user":"chat-message-bot";el.textContent=text;chatMessages.appendChild(el);chatMessages.scrollTop=chatMessages.scrollHeight;
}
async function askBot(message){
 addChat(message,"user");
 const loading=document.createElement("div");loading.className="chat-message-bot";loading.textContent="Thinking…";chatMessages.appendChild(loading);
 try{const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const d=await r.json();loading.remove();addChat(d.answer||"I couldn't find an answer. Ask about a specific course or registration step.","bot");}
 catch(e){loading.remove();addChat("I can't connect to the helper. Make sure the app is running and try again.","bot");}
}
$("#chat-form").addEventListener("submit",e=>{e.preventDefault();const q=$("#chat-input").value.trim();if(q){$("#chat-input").value="";askBot(q);}});
$$(".suggestion").forEach(b=>b.addEventListener("click",()=>askBot(b.textContent)));
