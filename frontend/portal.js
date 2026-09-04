const q=(s,c=document)=>c.querySelector(s),qa=(s,c=document)=>[...c.querySelectorAll(s)];
const API_BASE="http://localhost:8000/api";
const draftKey="anyschool-application-draft",sessionKey="anyschool-student-session";

function apiErrorMessage(data,status){
  if(!data)return `Request failed (${status})`;
  // The backend's custom exception handler wraps DRF exceptions (validation
  // errors, permission/auth errors, 404s, ...) as {error:true, message, details}
  // where `message` is a generic per-status string and the real detail lives
  // in `details` (either {"detail":"..."} or {"<field>":["..."]}).
  if(data.error===true||typeof data.details!=="undefined"){
    const details=data.details;
    if(details&&typeof details==="object"){
      if(typeof details.detail==="string")return details.detail;
      const field=Object.keys(details)[0];
      if(field){
        const val=Array.isArray(details[field])?details[field][0]:details[field];
        return field==="non_field_errors"?val:`${field}: ${val}`;
      }
    }
    if(typeof details==="string")return details;
    if(typeof data.message==="string")return data.message;
  }
  // Hand-written view responses use plain shapes like {error:"..."} or {detail:"..."}
  if(typeof data.error==="string")return data.error;
  if(typeof data.detail==="string")return data.detail;
  if(typeof data.message==="string")return data.message;
  const first=Object.values(data).flat()[0];
  return typeof first==="string"?first:`Request failed (${status})`;
}

async function api(path,{method="GET",body,token}={}){
  const headers={};
  if(body)headers["Content-Type"]="application/json";
  if(token)headers["Authorization"]=`Token ${token}`;
  let res;
  try{res=await fetch(API_BASE+path,{method,headers,body:body?JSON.stringify(body):undefined})}
  catch{throw new Error(`Could not reach the school server at ${API_BASE}. Is it running?`)}
  let data=null;try{data=await res.json()}catch{}
  if(!res.ok){
    throw new Error(apiErrorMessage(data,res.status));
  }
  return data;
}
// Like api(), but sends a FormData body (multipart) instead of JSON —
// needed for endpoints that accept file uploads, such as the admission
// application's document fields.
async function apiUpload(path,formData,{method="POST",token}={}){
  const headers={};
  if(token)headers["Authorization"]=`Token ${token}`;
  let res;
  try{res=await fetch(API_BASE+path,{method,headers,body:formData})}
  catch{throw new Error(`Could not reach the school server at ${API_BASE}. Is it running?`)}
  let data=null;try{data=await res.json()}catch{}
  if(!res.ok){
    throw new Error(apiErrorMessage(data,res.status));
  }
  return data;
}
function saveJSON(k,v){localStorage.setItem(k,JSON.stringify(v))}
function loadJSON(k){try{return JSON.parse(localStorage.getItem(k))}catch{return null}}

const GENDER_MAP={"Female":"F","Male":"M","Prefer not to say":"O"};
const GRADE_MAP={"Form 1":"form1","Form 2":"form2","Form 3":"form3","Form 4":"form4","Lower 6":"lower6","Upper 6":"upper6"};
const GRADE_LABELS={form1:"Form 1",form2:"Form 2",form3:"Form 3",form4:"Form 4",lower6:"Lower 6",upper6:"Upper 6"};
const STATUS_LABELS={draft:"Draft",submitted:"Under review",under_review:"Under review",approved:"Accepted",rejected:"Rejected",waitlisted:"Waitlisted",admitted:"Admitted",enrolled:"Enrolled"};
function statusClass(status){
  if(["approved","admitted","enrolled"].includes(status))return "accepted";
  if(status==="rejected")return "rejected";
  return "under-review";
}
function academicYearForIntake(intake){return intake==="September 2027"?"2027-2028":"2026-2027"}

/* ---------- Public application form ---------- */
const appForm=q("#high-school-application");
if(appForm){
  let step=1;
  const saved=JSON.parse(localStorage.getItem(draftKey)||"{}");
  Object.entries(saved).forEach(([n,v])=>{const f=appForm.elements[n];if(f&&f.type!=="checkbox"&&f.type!=="file")f.value=v});
  const titles=["Learner details","School & intake","Upload documents","Parent / guardian","Payment & confirmation"];
  const show=()=>{qa(".form-step",appForm).forEach(x=>x.classList.toggle("active",+x.dataset.step===step));qa(".app-steps li").forEach((x,i)=>{x.classList.toggle("active",i+1===step);x.classList.toggle("complete",i+1<step)});q("#step-kicker").textContent=`Step ${step} of 5`;q("#step-title").textContent=titles[step-1];q("#previous-step").hidden=step===1;q("#next-step").hidden=step===5;q("#submit-application").hidden=step!==5};
  const save=()=>{const d=Object.fromEntries(new FormData(appForm));delete d.consent;delete d.paymentConfirmed;localStorage.setItem(draftKey,JSON.stringify(d));q("#save-note").textContent="Progress saved"};
  appForm.addEventListener("input",save);
  qa('input[type="file"]',appForm).forEach(input=>input.addEventListener("change",()=>{const file=input.files[0];if(file&&file.size>5*1024*1024){input.value="";alert("Each document must be 5 MB or smaller.")}}));
  q("#next-step").onclick=()=>{const fields=qa("input,select,textarea",q(`.form-step[data-step="${step}"]`));if(!fields.every(f=>f.reportValidity()))return;step++;show()};
  q("#previous-step").onclick=()=>{step--;show()};

  appForm.onsubmit=async e=>{
    e.preventDefault();
    if(!appForm.reportValidity())return;
    const d=Object.fromEntries(new FormData(appForm));
    if(d.portalPassword!==d.confirmPassword){alert("The portal passwords do not match.");return}
    const notes=[
      d.idNumber&&`Birth certificate/ID number: ${d.idNumber}`,
      d.nationality&&`Nationality: ${d.nationality}`,
      d.boarding&&`Boarding preference: ${d.boarding}`,
      d.needs&&`Learning/medical needs: ${d.needs}`,
      d.relationship&&`Guardian relationship: ${d.relationship}`,
      d.altPhone&&`Alternative phone: ${d.altPhone}`,
      d.occupation&&`Guardian occupation: ${d.occupation}`,
      d.paymentMethod&&`Payment method: ${d.paymentMethod}`,
      d.paymentReference&&`Payment reference: ${d.paymentReference}`,
    ].filter(Boolean).join(" · ");
    const fields={
      student_name:`${d.firstName} ${d.lastName}`.trim(),
      date_of_birth:d.dob,
      gender:GENDER_MAP[d.gender]||"O",
      grade_applying_for:GRADE_MAP[d.level]||"form1",
      academic_year:academicYearForIntake(d.intake),
      parent_name:d.guardianName,
      parent_email:d.email,
      parent_phone:d.phone,
      parent_address:d.address,
      previous_school:d.previousSchool||"",
      previous_grade:d.previousLevel||"",
      status:"submitted",
      additional_notes:notes,
      portal_password:d.portalPassword,
    };
    // Sent as multipart/form-data (not JSON) so the uploaded documents
    // reach the backend — admissions staff review these before deciding.
    const fd=new FormData();
    Object.entries(fields).forEach(([k,v])=>fd.append(k,v));
    if(d.birthCertificate&&d.birthCertificate.size)fd.append("birth_certificate",d.birthCertificate);
    if(d.schoolReport&&d.schoolReport.size)fd.append("transfer_certificate",d.schoolReport);
    if(d.passportPhoto&&d.passportPhoto.size)fd.append("photo",d.passportPhoto);
    if(d.supportingDocument&&d.supportingDocument.size)fd.append("aadhar_card",d.supportingDocument);
    const submitBtn=q("#submit-application");
    submitBtn.disabled=true;
    q("#save-note").textContent="Submitting application…";
    try{
      const application=await apiUpload("/admissions/applications/",fd);
      localStorage.removeItem(draftKey);
      appForm.hidden=true;q(".form-heading").hidden=true;
      q("#application-complete").hidden=false;
      q("#application-reference").textContent=application.application_number;
      const note=q("#email-status");
      if(note)note.textContent=application.email_sent
        ?`A confirmation email with this reference has been sent to ${d.email}.`
        :"We could not send a confirmation email, but your reference number above still works — save it.";
    }catch(err){
      q("#save-note").textContent="";
      alert("We could not submit your application: "+err.message);
      submitBtn.disabled=false;
    }
  };
  show();
}

/* ---------- Student portal ---------- */
const login=q("#login-form");
function initials(user){return (((user.first_name||user.username||"?")[0]||"?")+((user.last_name||"")[0]||"")).toUpperCase()}
function showDash(){q("#student-login").hidden=true;const d=q("#student-dashboard");d.hidden=false;d.style.display="grid"}

if(login)login.onsubmit=async e=>{
  e.preventDefault();
  const d=new FormData(login);
  q("#login-error").textContent="";
  try{
    const data=await api("/auth/login/",{method:"POST",body:{username:String(d.get("studentNumber")).trim(),password:String(d.get("password"))}});
    if(data.user.role!=="student"){q("#login-error").textContent="This sign-in is for student accounts only.";return}
    saveJSON(sessionKey,{token:data.token,user:data.user});
    showDash();
    loadStudentDashboard(data.token,data.user);
  }catch(err){
    q("#login-error").textContent=err.message;
  }
};
q("#forgot-password")?.addEventListener("click",()=>q("#login-error").textContent="Please contact the school office to reset your password.");

if(q("#student-dashboard")){
  const session=loadJSON(sessionKey);
  if(session&&session.token){showDash();loadStudentDashboard(session.token,session.user)}
}

async function loadStudentDashboard(token,user){
  q("#student-initials").textContent=initials(user);
  q("#student-name").textContent=(user.first_name||user.last_name)?`${user.first_name} ${user.last_name}`.trim():user.username;
  q("#student-id").textContent=user.student_id||user.username;
  q("#welcome-heading").textContent=`Welcome back, ${user.first_name||user.username}.`;
  q("#status-pill").textContent=user.role==="admin"?"Staff account":"Registered student";
  q("#today-date").textContent=new Date().toLocaleDateString(undefined,{weekday:"long",year:"numeric",month:"long",day:"numeric"});
  q("#term-label").textContent=new Date().getFullYear();

  const overview=q("#overview-stats");
  try{
    const dash=await api("/courses/dashboard/student/",{token});
    const courses=dash.enrolled_courses||[],grades=dash.grades||[];
    const graded=grades.filter(g=>g.overall_grade!=null);
    const avg=graded.length?(graded.reduce((s,g)=>s+parseFloat(g.overall_grade),0)/graded.length).toFixed(1):null;
    overview.innerHTML=`
      <article><span class="stat-icon blue">${courses.length}</span><small>Enrolled courses</small><strong>${courses.length}</strong><em>${courses.length?"Active this semester":"No active enrollments"}</em></article>
      <article><span class="stat-icon green">${avg?avg+"%":"–"}</span><small>Average grade</small><strong>${avg?avg+"%":"No grades yet"}</strong><em>${graded.length} graded course${graded.length===1?"":"s"}</em></article>
      <article><span class="stat-icon purple">${(user.role||"").slice(0,2).toUpperCase()}</span><small>Account</small><strong>${user.role[0].toUpperCase()+user.role.slice(1)}</strong><em>${user.email_verified?"Email verified":"Email not verified"}</em></article>
      <article><span class="stat-icon orange">${user.enrollment_date?new Date(user.enrollment_date).getFullYear():"–"}</span><small>Member since</small><strong>${user.enrollment_date?new Date(user.enrollment_date).toLocaleDateString():"–"}</strong><em>${user.student_id||"—"}</em></article>`;
    renderSubjects(courses);
    renderReports(grades);
  }catch(err){
    overview.innerHTML=`<p class="muted-note">Could not load your dashboard: ${err.message}</p>`;
    q("#subject-grid").innerHTML=`<p class="muted-note">Could not load your subjects.</p>`;
    q("#results-table").innerHTML=`<p class="muted-note">Could not load your results.</p>`;
  }
  loadTimetable(token);
  loadFees(token);
  loadNotices(token);
}

function renderSubjects(courses){
  const el=q("#subject-grid");
  if(!courses.length){el.innerHTML=`<div class="empty-state small-empty"><h2>No enrolled courses</h2><p>You are not enrolled in any courses yet.</p></div>`;return}
  el.innerHTML=courses.map(c=>`<article><b>${(c.code||"?").slice(0,2).toUpperCase()}</b><span><strong>${c.name}</strong><small>${c.code} · ${c.credits} credit${c.credits===1?"":"s"}</small></span><em>${c.department_name||""}</em></article>`).join("");
}

function renderReports(grades){
  const el=q("#results-table");
  if(!grades.length){el.innerHTML=`<p class="muted-note">No grades recorded yet.</p>`;return}
  el.innerHTML=grades.map(g=>`<p><b>${g.course_code||"Course"}</b><span>${g.overall_grade!=null?g.overall_grade+"%":"–"}</span><strong>${g.letter_grade||"–"}</strong></p>`).join("");
}

async function loadTimetable(token){
  const body=q("#timetable-body");
  try{
    const now=new Date();
    const startYear=now.getMonth()>=7?now.getFullYear():now.getFullYear()-1;
    const schedules=await api(`/schedule/user-schedule/?academic_year=${startYear}-${startYear+1}`,{token});
    if(!schedules.length){body.innerHTML=`<tr><td colspan="6" class="muted-note">No timetable published yet.</td></tr>`;return}
    const days=["monday","tuesday","wednesday","thursday","friday"];
    const byTime={};
    schedules.forEach(s=>{
      const slot=s.time_slot_details;if(!slot)return;
      const key=slot.start_time;
      byTime[key]=byTime[key]||{};
      byTime[key][slot.day]=`${s.course_name}${s.room?" · "+s.room:""}`;
    });
    const times=Object.keys(byTime).sort();
    body.innerHTML=times.map(t=>`<tr><th>${t.slice(0,5)}</th>${days.map(d=>`<td>${byTime[t][d]||""}</td>`).join("")}</tr>`).join("");
  }catch(err){
    body.innerHTML=`<tr><td colspan="6" class="muted-note">Could not load timetable: ${err.message}</td></tr>`;
  }
}

async function loadFees(token){
  const el=q("#finance-stats");
  try{
    const res=await api("/fees/fee-accounts/",{token});
    const accounts=res.results||res;
    if(!accounts.length){el.innerHTML=`<p class="muted-note">No fee account set up yet.</p>`;return}
    const a=accounts[0];
    el.innerHTML=`<article><small>Total fees</small><strong>US$ ${a.total_fees}</strong></article><article><small>Paid</small><strong>US$ ${a.fees_paid}</strong></article><article><small>Balance due</small><strong class="danger">US$ ${a.fees_due}</strong></article>`;
  }catch(err){
    el.innerHTML=`<p class="muted-note">Could not load fees: ${err.message}</p>`;
  }
}

async function loadNotices(token){
  const el=q("#notice-list"),timeline=q("#today-timeline");
  timeline.innerHTML=`<p class="muted-note">See the Timetable tab for your full weekly schedule.</p>`;
  try{
    const res=await api("/announcements/",{token});
    const items=res.results||res;
    el.innerHTML=items.length?items.slice(0,5).map(a=>`<p><strong>${a.title}</strong><small>${new Date(a.publish_date).toLocaleDateString()}</small></p>`).join(""):`<p class="muted-note">No notices yet.</p>`;
  }catch(err){
    el.innerHTML=`<p class="muted-note">Could not load notices: ${err.message}</p>`;
  }
}

function panel(name){qa(".side-nav nav button").forEach(x=>x.classList.toggle("active",x.dataset.section===name));qa(".dash-section").forEach(x=>x.classList.toggle("active",x.dataset.panel===name));q("#section-title").textContent=q(`.side-nav nav button[data-section="${name}"] span`)?.textContent||"Overview";q(".side-nav").classList.remove("open")}
qa(".side-nav nav button").forEach(b=>b.onclick=()=>panel(b.dataset.section));
qa("[data-go]").forEach(b=>b.onclick=()=>panel(b.dataset.go));
q("#logout-button")?.addEventListener("click",()=>{localStorage.removeItem(sessionKey);location.reload()});
q("#mobile-menu")?.addEventListener("click",()=>q(".side-nav").classList.toggle("open"));
q("#print-timetable")?.addEventListener("click",()=>print());

/* ---------- Admissions staff portal ---------- */
const adminLogin=q("#admin-login-form"),adminDash=q("#admin-dashboard");
const adminSessionStorageKey="admissions-admin-session";
function getAdminSession(){try{return JSON.parse(sessionStorage.getItem(adminSessionStorageKey))}catch{return null}}
let allApplications=[];

if(adminLogin)adminLogin.onsubmit=async e=>{
  e.preventDefault();
  const d=new FormData(adminLogin);
  q("#admin-error").textContent="";
  try{
    const data=await api("/auth/login/",{method:"POST",body:{username:d.get("username"),password:d.get("password")}});
    if(data.user.role!=="admin"){q("#admin-error").textContent="This account does not have admissions staff access.";return}
    sessionStorage.setItem(adminSessionStorageKey,JSON.stringify({token:data.token,user:data.user}));
    q("#admin-login").hidden=true;adminDash.hidden=false;
    loadAdmin();
    loadAdminOverview();
    loadAcademics();
    loadAdminStudents();
    loadTimetableAdmin();
    initAttendancePanel();
    loadFeesAdmin();
    loadResultsAdmin();
  }catch(err){
    q("#admin-error").textContent=err.message;
  }
};
if(adminDash&&getAdminSession()){q("#admin-login").hidden=true;adminDash.hidden=false;loadAdmin();loadAdminOverview();loadAcademics();loadAdminStudents();loadTimetableAdmin();initAttendancePanel();loadFeesAdmin();loadResultsAdmin()}

async function loadAdmin(){
  const target=q("#admin-applications");if(!target)return;
  const session=getAdminSession();if(!session)return;
  target.innerHTML=`<p class="muted-note">Loading…</p>`;
  try{
    const res=await api("/admissions/applications/?page_size=100",{token:session.token});
    allApplications=res.results||res;
    renderAdminList();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load applications: ${err.message}</p>`;
  }
  loadAdminNews();
  loadAdminStaff();
}

/* ---------- Admin dashboard overview (dashboard-admin.html) ---------- */
async function loadAdminOverview(){
  const target=q("#overview-kpis");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const [courseStats,appsRes,staffRes,newsRes]=await Promise.all([
      api("/courses/dashboard/admin/",{token:session.token}).catch(()=>null),
      api("/admissions/applications/?page_size=200",{token:session.token}).catch(()=>({results:[],count:0})),
      api("/staff/staff-profiles/?page_size=500",{token:session.token}).catch(()=>({results:[]})),
      api("/news/posts/?page_size=100",{token:session.token}).catch(()=>({results:[]})),
    ]);
    const applications=appsRes.results||appsRes||[];
    const staffList=staffRes.results||staffRes||[];
    const posts=newsRes.results||newsRes||[];
    const totalApplications=appsRes.count??applications.length;
    const pending=applications.filter(a=>["submitted","under_review"].includes(a.status)).length;
    const accepted=applications.filter(a=>["approved","admitted","enrolled"].includes(a.status)).length;
    const permanentTeachers=staffList.filter(s=>s.employee_type==="permanent_teacher").length;

    target.innerHTML=`
      <article><span class="stat-icon blue">${courseStats?"✓":"–"}</span><small>Total students</small><strong>${courseStats?.total_students??"–"}</strong><em>Enrolled accounts</em></article>
      <article><span class="stat-icon purple">${staffList.length}</span><small>Teachers & staff</small><strong>${staffList.length}</strong><em>${permanentTeachers} permanent teacher${permanentTeachers===1?"":"s"}</em></article>
      <article><span class="stat-icon orange">${pending}</span><small>Applications under review</small><strong>${pending}</strong><em>${totalApplications} total this year</em></article>
      <article><span class="stat-icon green">${accepted}</span><small>Accepted applicants</small><strong>${accepted}</strong><em>${posts.filter(p=>p.published).length} published post${posts.filter(p=>p.published).length===1?"":"s"}</em></article>`;

    const recent=[...applications].sort((a,b)=>new Date(b.created_at)-new Date(a.created_at)).slice(0,5);
    q("#overview-recent").innerHTML=recent.length
      ?recent.map(a=>`<p><strong>${a.student_name}</strong><small>${a.application_number} · ${STATUS_LABELS[a.status]||a.status} · ${new Date(a.created_at).toLocaleDateString()}</small></p>`).join("")
      :`<p class="muted-note">No applications yet.</p>`;

    const now=new Date();
    const upcoming=posts.filter(p=>p.category==="event"&&p.event_date&&new Date(p.event_date)>now).sort((a,b)=>new Date(a.event_date)-new Date(b.event_date)).slice(0,5);
    q("#overview-events").innerHTML=upcoming.length
      ?upcoming.map(p=>`<p><strong>${p.title}</strong><small>${new Date(p.event_date).toLocaleDateString()}${p.location?" · "+p.location:""}</small></p>`).join("")
      :`<p class="muted-note">No upcoming events scheduled.</p>`;
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load dashboard stats: ${err.message}</p>`;
  }
}

function renderAdminList(){
  const target=q("#admin-applications");if(!target)return;
  const term=(q("#admin-search")?.value||"").toLowerCase();
  const entries=allApplications.filter(a=>(a.application_number+" "+a.student_name).toLowerCase().includes(term));
  q("#admin-total").textContent=allApplications.length;
  q("#admin-review").textContent=allApplications.filter(a=>["submitted","under_review"].includes(a.status)).length;
  q("#admin-accepted").textContent=allApplications.filter(a=>["approved","admitted","enrolled"].includes(a.status)).length;
  q("#admin-rejected").textContent=allApplications.filter(a=>a.status==="rejected").length;
  target.innerHTML=entries.length?entries.map(a=>`<article class="admin-application"><div><span class="decision-status ${statusClass(a.status)}">${STATUS_LABELS[a.status]||a.status}</span><h3>${a.student_name}</h3><p>${a.application_number} · ${GRADE_LABELS[a.grade_applying_for]||a.grade_applying_for} · ${a.academic_year}${a.assigned_class?` · Class ${a.assigned_class}`:""}</p></div><div class="decision-actions"><button class="primary-button" data-review="${a.application_number}">Review application</button></div></article>`).join(""):`<div class="empty-state small-empty"><h2>No applications found</h2><p>Submit an application first or change your search.</p></div>`;
}

q("#admin-applications")?.addEventListener("click",e=>{
  const ref=e.target.dataset.review;
  if(ref)openReview(ref);
});

/* ---------- Document review modal ---------- */
const GENDER_LABELS={M:"Male",F:"Female",O:"Other"};
let reviewingRef=null;

function openReview(ref){
  const a=allApplications.find(x=>x.application_number===ref);
  if(!a)return;
  reviewingRef=ref;
  const avatar=q("#review-avatar");
  const nameParts=(a.student_name||"?").trim().split(/\s+/);
  avatar.innerHTML=a.photo?`<img src="${a.photo}" alt="">`:((nameParts[0]?.[0]||"?")+(nameParts[1]?.[0]||"")).toUpperCase();
  q("#review-status").textContent=STATUS_LABELS[a.status]||a.status;
  q("#review-status").className=`decision-status ${statusClass(a.status)}`;
  q("#review-name").textContent=a.student_name;
  q("#review-meta").textContent=`${a.application_number} · ${GRADE_LABELS[a.grade_applying_for]||a.grade_applying_for} · ${a.academic_year}`;
  const rows=[
    ["Date of birth",a.date_of_birth?new Date(a.date_of_birth).toLocaleDateString():"—"],
    ["Gender",GENDER_LABELS[a.gender]||a.gender],
    ["Previous school",a.previous_school||"—"],
    ["Previous grade",a.previous_grade||"—"],
    ["Parent / guardian",a.parent_name],
    ["Parent email",a.parent_email],
    ["Parent phone",a.parent_phone],
    ["Address",a.parent_address||"—"],
  ];
  if(a.points!=null)rows.push(["Points",a.points]);
  if(a.assigned_class)rows.push(["Assigned class",a.assigned_class]);
  if(a.additional_notes)rows.push(["Notes",a.additional_notes]);
  q("#review-details-grid").innerHTML=rows.map(([label,val])=>`<p><span>${label}</span><strong>${val}</strong></p>`).join("");
  const docs=[
    ["Passport photo",a.photo],
    ["Birth certificate",a.birth_certificate],
    ["School report / transfer certificate",a.transfer_certificate],
    ["Supporting document",a.aadhar_card],
  ];
  q("#review-doc-grid").innerHTML=docs.map(([label,url])=>url
    ?`<a class="doc-item" href="${url}" target="_blank" rel="noopener"><span>📄</span><div><strong>${label}</strong><small>View document →</small></div></a>`
    :`<div class="doc-item missing"><span>—</span><div><strong>${label}</strong><small>Not uploaded</small></div></div>`
  ).join("");
  const decided=["approved","rejected","admitted","enrolled"].includes(a.status);
  q("#review-accept").hidden=decided;
  q("#review-reject").hidden=decided;
  // Only Form 1 has a points-based class scheme (see backend/admissions/classing.py).
  q("#review-points-field").hidden=decided||a.grade_applying_for!=="form1";
  q("#review-points").value=a.points??"";
  q("#doc-review-modal").hidden=false;
}
function closeReview(){q("#doc-review-modal").hidden=true;reviewingRef=null}
q("#review-close")?.addEventListener("click",closeReview);
q("#doc-review-modal")?.addEventListener("click",e=>{if(e.target.id==="doc-review-modal")closeReview()});

async function decideReview(decision){
  if(!reviewingRef)return;
  const session=getAdminSession();if(!session)return;
  const ref=reviewingRef;
  const applicant=allApplications.find(x=>x.application_number===ref);
  const btn=decision==="approve"?q("#review-accept"):q("#review-reject");
  let body;
  if(decision==="approve"&&!q("#review-points-field").hidden){
    const points=q("#review-points").value.trim();
    if(!points){alert("Enter the applicant's points before accepting — it's used to place them in a class.");return}
    body={points};
  }
  btn.disabled=true;
  try{
    const res=await api(`/admissions/applications/${encodeURIComponent(ref)}/${decision}/`,{method:"POST",body,token:session.token});
    closeReview();
    if(decision==="approve"&&res.status==="rejected"){
      alert(`${applicant?.student_name||"This applicant"} could not be placed in a class — ${res.reason||"every class for this grade is full"} — so the application was automatically declined instead.`);
    }else if(res.assigned_class){
      alert(`Accepted. ${applicant?.student_name||"The applicant"} has been placed in class ${res.assigned_class}.`);
    }
    await loadAdmin();
  }catch(err){
    alert("Could not update application: "+err.message);
  }finally{
    btn.disabled=false;
  }
}
q("#review-accept")?.addEventListener("click",()=>decideReview("approve"));
q("#review-reject")?.addEventListener("click",()=>decideReview("reject"));
q("#admin-logout")?.addEventListener("click",()=>{sessionStorage.removeItem(adminSessionStorageKey);location.reload()});
q("#admin-search")?.addEventListener("input",renderAdminList);

// Applications and News & events are kept as separate tabs so staff never
// mix up which panel they're acting on.
qa(".admin-tabs .tab-btn").forEach(btn=>btn.addEventListener("click",()=>{
  qa(".admin-tabs .tab-btn").forEach(b=>b.classList.toggle("active",b===btn));
  qa(".admin-panel").forEach(p=>p.hidden=p.dataset.panel!==btn.dataset.tab);
}));

/* ---------- News & events admin ---------- */
let allNewsPosts=[];
const newsForm=q("#news-form");

async function loadAdminNews(){
  const target=q("#admin-news-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  target.innerHTML=`<p class="muted-note">Loading…</p>`;
  try{
    const res=await api("/news/posts/?page_size=100",{token:session.token});
    allNewsPosts=res.results||res;
    renderAdminNews();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load news & events: ${err.message}</p>`;
  }
}

function renderAdminNews(){
  const target=q("#admin-news-list");if(!target)return;
  if(!allNewsPosts.length){target.innerHTML=`<div class="empty-state small-empty"><h2>No posts yet</h2><p>Add the school's first news update or event above.</p></div>`;return}
  target.innerHTML=allNewsPosts.map(p=>`<article class="admin-application"><div><span class="decision-status ${p.category==="event"?"under-review":"accepted"}">${p.category==="event"?"Event":"News"}</span><h3>${p.title}</h3><p>${p.published?"Published":"Draft"}${p.event_date?" · "+new Date(p.event_date).toLocaleString():""}${p.location?" · "+p.location:""}</p></div><div class="decision-actions"><button class="reject-button" data-delete-news="${p.id}">Delete</button></div></article>`).join("");
}

if(newsForm)newsForm.onsubmit=async e=>{
  e.preventDefault();
  const session=getAdminSession();if(!session)return;
  const d=new FormData(newsForm);
  q("#news-form-error").textContent="";
  const payload={
    title:d.get("title"),
    category:d.get("category"),
    summary:d.get("summary"),
    body:d.get("body")||"",
    location:d.get("location")||"",
    published:d.get("published")==="on",
  };
  if(d.get("event_date"))payload.event_date=new Date(d.get("event_date")).toISOString();
  const submitBtn=newsForm.querySelector('button[type="submit"]');
  submitBtn.disabled=true;
  try{
    await api("/news/posts/",{method:"POST",body:payload,token:session.token});
    newsForm.reset();
    await loadAdminNews();
  }catch(err){
    q("#news-form-error").textContent=err.message;
  }finally{
    submitBtn.disabled=false;
  }
};

q("#admin-news-list")?.addEventListener("click",async e=>{
  const id=e.target.dataset.deleteNews;
  if(!id)return;
  if(!confirm("Delete this post? This cannot be undone."))return;
  const session=getAdminSession();if(!session)return;
  e.target.disabled=true;
  try{
    await api(`/news/posts/${id}/`,{method:"DELETE",token:session.token});
    await loadAdminNews();
  }catch(err){
    alert("Could not delete post: "+err.message);
    e.target.disabled=false;
  }
});

/* ---------- Staff & teachers admin ---------- */
const STAFF_CATEGORIES=[
  ["permanent_teacher","Permanent Teachers"],
  ["student_teacher","Student Teachers"],
  ["staff","Staff"],
  ["sdc_member","SDC Members"],
];
let allStaff=[];
const staffForm=q("#staff-form");

async function loadAdminStaff(){
  const target=q("#admin-staff-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  target.innerHTML=`<p class="muted-note">Loading…</p>`;
  try{
    const res=await api("/staff/staff-profiles/?page_size=500",{token:session.token});
    allStaff=res.results||res;
    renderAdminStaff();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load staff: ${err.message}</p>`;
  }
}

function renderAdminStaff(){
  const target=q("#admin-staff-list");if(!target)return;
  target.innerHTML=STAFF_CATEGORIES.map(([key,label])=>{
    const members=allStaff.filter(s=>s.employee_type===key);
    const rows=members.length
      ?members.map(s=>`<article class="admin-application"><div><h3>${s.display_name}</h3><p>${[s.designation,s.department,s.phone,s.email].filter(Boolean).join(" · ")||"No further details"}</p></div><div class="decision-actions"><button class="reject-button" data-delete-staff="${s.id}">Remove</button></div></article>`).join("")
      :`<p class="muted-note">No ${label.toLowerCase()} yet.</p>`;
    return `<div class="staff-category"><h3 class="staff-category-head">${label} <span>${members.length}</span></h3>${rows}</div>`;
  }).join("");
}

if(staffForm)staffForm.onsubmit=async e=>{
  e.preventDefault();
  const session=getAdminSession();if(!session)return;
  const d=new FormData(staffForm);
  q("#staff-form-error").textContent="";
  const payload={
    full_name:d.get("full_name"),
    employee_type:d.get("employee_type"),
    designation:d.get("designation")||"",
    department:d.get("department")||"",
    phone:d.get("phone")||"",
    email:d.get("email")||"",
  };
  const submitBtn=staffForm.querySelector('button[type="submit"]');
  submitBtn.disabled=true;
  try{
    await api("/staff/staff-profiles/",{method:"POST",body:payload,token:session.token});
    staffForm.reset();
    await loadAdminStaff();
  }catch(err){
    q("#staff-form-error").textContent=err.message;
  }finally{
    submitBtn.disabled=false;
  }
};

q("#admin-staff-list")?.addEventListener("click",async e=>{
  const id=e.target.dataset.deleteStaff;
  if(!id)return;
  if(!confirm("Remove this staff member? This cannot be undone."))return;
  const session=getAdminSession();if(!session)return;
  e.target.disabled=true;
  try{
    await api(`/staff/staff-profiles/${id}/`,{method:"DELETE",token:session.token});
    await loadAdminStaff();
  }catch(err){
    alert("Could not remove staff member: "+err.message);
    e.target.disabled=false;
  }
});

/* ---------- Applicant status portal ---------- */
function renderApplicant(app){
  q("#applicant-name").textContent=app.student_name;
  q("#applicant-reference").textContent=app.application_number;
  q("#applicant-decision").textContent=STATUS_LABELS[app.status]||app.status;
  q("#applicant-decision").className=statusClass(app.status);
  q("#review-stage").classList.add("done");
  q("#decision-stage").classList.toggle("done",["approved","rejected","admitted","enrolled"].includes(app.status));
  q("#decision-message").textContent=
    ["approved","admitted","enrolled"].includes(app.status)?"Congratulations. You have been offered a place.":
    app.status==="rejected"?"This application was not successful. Contact admissions for guidance.":
    "The admissions team is reviewing your information.";
  q("#submitted-date").textContent=new Date(app.submitted_date||app.created_at).toLocaleDateString();
  q("#applicant-details").innerHTML=`<p><span>Applying for</span><strong>${GRADE_LABELS[app.grade_applying_for]||app.grade_applying_for}</strong></p><p><span>Academic year</span><strong>${app.academic_year}</strong></p><p><span>Previous school</span><strong>${app.previous_school||"—"}</strong></p><p><span>Guardian</span><strong>${app.parent_name}</strong></p>${app.assigned_class?`<p><span>Class</span><strong>${app.assigned_class}</strong></p>`:""}`;
  const letterLink=q("#acceptance-letter-link");
  if(letterLink)if(app.admission_letter){letterLink.href=app.admission_letter;letterLink.hidden=false}else{letterLink.hidden=true}
}

q("#applicant-login-form")?.addEventListener("submit",async e=>{
  e.preventDefault();
  const d=new FormData(e.currentTarget);
  const ref=String(d.get("reference")).trim().toUpperCase();
  const password=String(d.get("password"));
  q("#applicant-error").textContent="";
  try{
    const app=await api(`/admissions/applications/${encodeURIComponent(ref)}/login/`,{method:"POST",body:{password}});
    sessionStorage.setItem("active-applicant",JSON.stringify(app));
    q("#applicant-login").hidden=true;q("#applicant-dashboard").hidden=false;
    renderApplicant(app);
  }catch(err){
    q("#applicant-error").textContent=err.message||"Application reference or password is incorrect.";
  }
});
if(q("#applicant-dashboard")){
  let cached=null;try{cached=JSON.parse(sessionStorage.getItem("active-applicant"))}catch{}
  if(cached){
    q("#applicant-login").hidden=true;q("#applicant-dashboard").hidden=false;
    renderApplicant(cached);
  }
}
q("#applicant-logout")?.addEventListener("click",()=>{sessionStorage.removeItem("active-applicant");location.reload()});

/* ---------- Generic admin CRUD wiring (reused by every simple add-list-
   delete panel on dashboard-admin.html: academic structure, and more as
   they get added) ---------- */
function wireAdminForm(formSelector,endpoint,payloadFn,errorSelector,onSuccess){
  const form=q(formSelector);
  if(!form)return;
  form.onsubmit=async e=>{
    e.preventDefault();
    const session=getAdminSession();if(!session)return;
    const d=new FormData(form);
    const errEl=q(errorSelector);
    if(errEl)errEl.textContent="";
    const submitBtn=form.querySelector('button[type="submit"]');
    submitBtn.disabled=true;
    try{
      await api(endpoint,{method:"POST",body:payloadFn(d),token:session.token});
      form.reset();
      await onSuccess();
    }catch(err){
      if(errEl)errEl.textContent=err.message;else alert(err.message);
    }finally{
      submitBtn.disabled=false;
    }
  };
}
function wireAdminDeleteList(listSelector,dataKey,endpointFn,onSuccess,confirmText){
  q(listSelector)?.addEventListener("click",async e=>{
    const id=e.target.dataset[dataKey];
    if(!id)return;
    if(confirmText&&!confirm(confirmText))return;
    const session=getAdminSession();if(!session)return;
    e.target.disabled=true;
    try{
      await api(endpointFn(id),{method:"DELETE",token:session.token});
      await onSuccess();
    }catch(err){
      alert("Could not delete: "+err.message);
      e.target.disabled=false;
    }
  });
}

/* ---------- Academic structure admin ---------- */
const GRADE_LABELS_FULL={form1:"Form 1",form2:"Form 2",form3:"Form 3",form4:"Form 4",lower6:"Lower 6",upper6:"Upper 6"};
let allDepartments=[],allSubjects=[],allTerms=[],allClassrooms=[];

async function loadAcademics(){
  const target=q("#department-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const [deps,subs,terms,rooms,staffRes]=await Promise.all([
      api("/academics/departments/",{token:session.token}),
      api("/academics/subjects/",{token:session.token}),
      api("/academics/terms/",{token:session.token}),
      api("/academics/classrooms/",{token:session.token}),
      api("/staff/staff-profiles/?page_size=500",{token:session.token}),
    ]);
    allDepartments=deps.results||deps;
    allSubjects=subs.results||subs;
    allTerms=terms.results||terms;
    allClassrooms=rooms.results||rooms;
    const teachers=(staffRes.results||staffRes).filter(s=>["permanent_teacher","student_teacher"].includes(s.employee_type));

    const depSelect=q("#subject-department-select");
    if(depSelect)depSelect.innerHTML=`<option value="">— none —</option>`+allDepartments.map(d=>`<option value="${d.id}">${d.name}</option>`).join("");
    const teacherSelect=q("#classroom-teacher-select");
    if(teacherSelect)teacherSelect.innerHTML=`<option value="">— none —</option>`+teachers.map(s=>`<option value="${s.id}">${s.display_name}</option>`).join("");

    renderDepartments();renderAcademicSubjects();renderTerms();renderClassrooms();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load academic structure: ${err.message}</p>`;
  }
}
function renderDepartments(){
  const target=q("#department-list");if(!target)return;
  target.innerHTML=allDepartments.length?allDepartments.map(d=>`<article class="admin-application"><div><h3>${d.name}</h3><p>${d.code||"—"}</p></div><div class="decision-actions"><button class="reject-button" data-delete-department="${d.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No departments yet.</p>`;
}
function renderAcademicSubjects(){
  const target=q("#subject-list");if(!target)return;
  target.innerHTML=allSubjects.length?allSubjects.map(s=>`<article class="admin-application"><div><h3>${s.name}</h3><p>${s.code||"—"}${s.department_name?" · "+s.department_name:""}${s.compulsory?" · Compulsory":""}</p></div><div class="decision-actions"><button class="reject-button" data-delete-subject="${s.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No subjects yet.</p>`;
}
function renderTerms(){
  const target=q("#term-list");if(!target)return;
  target.innerHTML=allTerms.length?allTerms.map(t=>`<article class="admin-application"><div><h3>${t.term_label} ${t.academic_year}${t.is_current?" (current)":""}</h3><p>${new Date(t.start_date).toLocaleDateString()} – ${new Date(t.end_date).toLocaleDateString()}</p></div><div class="decision-actions"><button class="reject-button" data-delete-term="${t.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No terms yet.</p>`;
}
function renderClassrooms(){
  const target=q("#classroom-list");if(!target)return;
  target.innerHTML=allClassrooms.length?allClassrooms.map(c=>`<article class="admin-application"><div><h3>${c.name}</h3><p>${c.grade_label} · ${c.academic_year}${c.room?" · "+c.room:""} · ${c.student_count}/${c.capacity} students${c.class_teacher_name?" · "+c.class_teacher_name:""}</p></div><div class="decision-actions"><button class="reject-button" data-delete-classroom="${c.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No classrooms yet.</p>`;
}

wireAdminForm("#department-form","/academics/departments/",d=>({name:d.get("name"),code:d.get("code")||""}),"#department-form-error",loadAcademics);
wireAdminForm("#subject-form","/academics/subjects/",d=>({name:d.get("name"),code:d.get("code")||"",department:d.get("department")||null,compulsory:d.get("compulsory")==="on"}),"#subject-form-error",loadAcademics);
wireAdminForm("#term-form","/academics/terms/",d=>({academic_year:d.get("academic_year"),term:d.get("term"),start_date:d.get("start_date"),end_date:d.get("end_date"),is_current:d.get("is_current")==="on"}),"#term-form-error",loadAcademics);
wireAdminForm("#classroom-form","/academics/classrooms/",d=>({grade:d.get("grade"),stream:d.get("stream"),academic_year:d.get("academic_year"),room:d.get("room")||"",capacity:d.get("capacity")||40,class_teacher:d.get("class_teacher")||null}),"#classroom-form-error",loadAcademics);

wireAdminDeleteList("#department-list","deleteDepartment",id=>`/academics/departments/${id}/`,loadAcademics,"Delete this department?");
wireAdminDeleteList("#subject-list","deleteSubject",id=>`/academics/subjects/${id}/`,loadAcademics,"Delete this subject?");
wireAdminDeleteList("#term-list","deleteTerm",id=>`/academics/terms/${id}/`,loadAcademics,"Delete this term?");
wireAdminDeleteList("#classroom-list","deleteClassroom",id=>`/academics/classrooms/${id}/`,loadAcademics,"Delete this classroom? Students already placed in it keep their record but lose the class link.");

/* ---------- Student management admin ---------- */
let allStudents=[],pendingApplications=[];

async function loadAdminStudents(){
  const target=q("#student-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  target.innerHTML=`<p class="muted-note">Loading…</p>`;
  try{
    const [studentsRes,appsRes]=await Promise.all([
      api("/auth/users/?role=student",{token:session.token}),
      api("/admissions/applications/?page_size=200",{token:session.token}),
    ]);
    allStudents=studentsRes.results||studentsRes;
    const applications=appsRes.results||appsRes;
    pendingApplications=applications.filter(a=>["approved","admitted","enrolled"].includes(a.status)&&!a.has_student_account);
    renderPendingConversions();
    renderStudentList();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load students: ${err.message}</p>`;
  }
}
function renderPendingConversions(){
  const target=q("#pending-conversions");if(!target)return;
  target.innerHTML=pendingApplications.length?pendingApplications.map(a=>`<article class="admin-application"><div><h3>${a.student_name}</h3><p>${a.application_number} · ${GRADE_LABELS_FULL[a.grade_applying_for]||a.grade_applying_for}${a.assigned_class?" · Class "+a.assigned_class:""}</p></div><div class="decision-actions"><button class="accept-button" data-convert="${a.application_number}">Create student account</button></div></article>`).join(""):`<p class="muted-note">No accepted applicants waiting on a student account.</p>`;
}
function renderStudentList(){
  const target=q("#student-list");if(!target)return;
  const term=(q("#student-search")?.value||"").toLowerCase();
  const entries=allStudents.filter(s=>`${s.first_name} ${s.last_name} ${s.student_id||""} ${s.username}`.toLowerCase().includes(term));
  target.innerHTML=entries.length?entries.map(s=>`<article class="admin-application"><div><h3>${(s.first_name||s.last_name)?`${s.first_name} ${s.last_name}`.trim():s.username}</h3><p>${s.student_id||s.username} · ${s.classroom_name?"Class "+s.classroom_name:"No class assigned"} · ${s.student_status[0].toUpperCase()+s.student_status.slice(1)}</p></div></article>`).join(""):`<div class="empty-state small-empty"><h2>No students found</h2><p>Convert an accepted applicant above, or adjust your search.</p></div>`;
}
q("#student-search")?.addEventListener("input",renderStudentList);

q("#pending-conversions")?.addEventListener("click",async e=>{
  const ref=e.target.dataset.convert;
  if(!ref)return;
  const session=getAdminSession();if(!session)return;
  e.target.disabled=true;
  try{
    const res=await api(`/admissions/applications/${encodeURIComponent(ref)}/convert_to_student/`,{method:"POST",token:session.token});
    alert(`Student account created.\n\nUsername: ${res.username}\nTemporary password: ${res.temporary_password}\n\nShare these with the student or parent now — this password is shown only once.`);
    await loadAdminStudents();
  }catch(err){
    alert("Could not create the student account: "+err.message);
    e.target.disabled=false;
  }
});

/* ---------- Timetable admin ---------- */
const DAY_LABELS={monday:"Monday",tuesday:"Tuesday",wednesday:"Wednesday",thursday:"Thursday",friday:"Friday",saturday:"Saturday",sunday:"Sunday"};
let allTimeSlots=[],allPeriods=[];

async function loadTimetableAdmin(){
  const target=q("#timeslot-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const [slotsRes,periodsRes,roomsRes,subjRes,staffRes]=await Promise.all([
      api("/schedule/time-slots/",{token:session.token}),
      api("/schedule/periods/",{token:session.token}),
      api("/academics/classrooms/",{token:session.token}),
      api("/academics/subjects/",{token:session.token}),
      api("/staff/staff-profiles/?page_size=500",{token:session.token}),
    ]);
    allTimeSlots=slotsRes.results||slotsRes;
    allPeriods=periodsRes.results||periodsRes;
    const rooms=roomsRes.results||roomsRes;
    const subjects=subjRes.results||subjRes;
    const teachers=(staffRes.results||staffRes).filter(s=>["permanent_teacher","student_teacher"].includes(s.employee_type));

    const slotSelect=q("#period-timeslot-select");
    if(slotSelect)slotSelect.innerHTML=allTimeSlots.map(t=>`<option value="${t.id}">${DAY_LABELS[t.day]||t.day} ${t.start_time.slice(0,5)}-${t.end_time.slice(0,5)}</option>`).join("")||`<option value="">Add a time slot first</option>`;
    const classroomSelect=q("#period-classroom-select");
    if(classroomSelect)classroomSelect.innerHTML=rooms.map(c=>`<option value="${c.id}">${c.name} (${c.academic_year})</option>`).join("")||`<option value="">Add a classroom first</option>`;
    const subjectSelect=q("#period-subject-select");
    if(subjectSelect)subjectSelect.innerHTML=subjects.map(s=>`<option value="${s.id}">${s.name}</option>`).join("")||`<option value="">Add a subject first</option>`;
    const teacherSelect=q("#period-teacher-select");
    if(teacherSelect)teacherSelect.innerHTML=`<option value="">— none —</option>`+teachers.map(s=>`<option value="${s.id}">${s.display_name}</option>`).join("");

    renderTimeSlots();renderPeriods();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load the timetable: ${err.message}</p>`;
  }
}
function renderTimeSlots(){
  const target=q("#timeslot-list");if(!target)return;
  target.innerHTML=allTimeSlots.length?allTimeSlots.map(t=>`<article class="admin-application"><div><h3>${DAY_LABELS[t.day]||t.day}</h3><p>${t.start_time.slice(0,5)} – ${t.end_time.slice(0,5)}</p></div><div class="decision-actions"><button class="reject-button" data-delete-timeslot="${t.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No time slots yet.</p>`;
}
function renderPeriods(){
  const target=q("#period-list");if(!target)return;
  target.innerHTML=allPeriods.length?allPeriods.map(p=>`<article class="admin-application"><div><h3>${p.classroom_name} · ${p.subject_name}</h3><p>${DAY_LABELS[p.time_slot_details.day]||p.time_slot_details.day} ${p.time_slot_details.start_time.slice(0,5)}-${p.time_slot_details.end_time.slice(0,5)} · ${p.teacher_name||"No teacher assigned"}${p.room?" · "+p.room:""}</p></div><div class="decision-actions"><button class="reject-button" data-delete-period="${p.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No periods scheduled yet.</p>`;
}

wireAdminForm("#timeslot-form","/schedule/time-slots/",d=>({day:d.get("day"),start_time:d.get("start_time"),end_time:d.get("end_time")}),"#timeslot-form-error",loadTimetableAdmin);
wireAdminForm("#period-form","/schedule/periods/",d=>({classroom:d.get("classroom"),subject:d.get("subject"),teacher:d.get("teacher")||null,time_slot:d.get("time_slot"),room:d.get("room")||"",academic_year:d.get("academic_year")}),"#period-form-error",loadTimetableAdmin);
wireAdminDeleteList("#timeslot-list","deleteTimeslot",id=>`/schedule/time-slots/${id}/`,loadTimetableAdmin,"Delete this time slot? Periods using it will need to be removed too.");
wireAdminDeleteList("#period-list","deletePeriod",id=>`/schedule/periods/${id}/`,loadTimetableAdmin,"Delete this class period?");

/* ---------- Attendance admin ---------- */
async function initAttendancePanel(){
  const select=q("#attendance-classroom-select");if(!select)return;
  const session=getAdminSession();if(!session)return;
  try{
    const res=await api("/academics/classrooms/",{token:session.token});
    const rooms=res.results||res;
    select.innerHTML=`<option value="">Select a classroom…</option>`+rooms.map(c=>`<option value="${c.id}">${c.name} (${c.academic_year})</option>`).join("");
  }catch{
    select.innerHTML=`<option value="">Could not load classrooms</option>`;
  }
  const dateInput=q("#attendance-date");
  if(dateInput&&!dateInput.value)dateInput.value=new Date().toISOString().slice(0,10);
  loadRecentAttendance();
}

q("#attendance-load-form")?.addEventListener("submit",async e=>{
  e.preventDefault();
  const session=getAdminSession();if(!session)return;
  const classroomId=q("#attendance-classroom-select").value;
  const date=q("#attendance-date").value;
  if(!classroomId||!date)return;
  const target=q("#attendance-register");
  target.innerHTML=`<p class="muted-note">Loading…</p>`;
  try{
    const [studentsRes,existingRes]=await Promise.all([
      api("/auth/users/?role=student",{token:session.token}),
      api(`/attendance/daily/?date=${date}&classroom=${classroomId}`,{token:session.token}),
    ]);
    const roster=(studentsRes.results||studentsRes).filter(s=>String(s.classroom)===String(classroomId));
    const existing=existingRes.results||existingRes;
    const existingByStudent={};
    existing.forEach(r=>existingByStudent[r.student]=r);
    if(!roster.length){target.innerHTML=`<p class="muted-note">No students are placed in this classroom yet.</p>`;return}
    target.innerHTML=`<div class="attendance-rows">${roster.map(s=>{
      const mark=existingByStudent[s.id];
      const name=(s.first_name||s.last_name)?`${s.first_name} ${s.last_name}`.trim():s.username;
      return `<div class="attendance-row" data-student="${s.id}"><span>${name} <small>${s.student_id||s.username}</small></span><select class="attendance-status"><option value="present"${!mark||mark.status==="present"?" selected":""}>Present</option><option value="absent"${mark&&mark.status==="absent"?" selected":""}>Absent</option><option value="late"${mark&&mark.status==="late"?" selected":""}>Late</option><option value="excused"${mark&&mark.status==="excused"?" selected":""}>Excused</option></select><input class="attendance-reason" placeholder="Reason (optional)" value="${mark?mark.reason:""}"></div>`;
    }).join("")}</div><div class="attendance-actions"><button class="primary-button" id="save-register" type="button">Save register</button><p id="attendance-form-error" class="form-error"></p></div>`;
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load the register: ${err.message}</p>`;
  }
});

q("#attendance-register")?.addEventListener("click",async e=>{
  if(e.target.id!=="save-register")return;
  const session=getAdminSession();if(!session)return;
  const classroomId=q("#attendance-classroom-select").value;
  const date=q("#attendance-date").value;
  const entries=qa(".attendance-row").map(row=>({
    student:row.dataset.student,
    status:row.querySelector(".attendance-status").value,
    reason:row.querySelector(".attendance-reason").value,
  }));
  e.target.disabled=true;
  try{
    const res=await api("/attendance/daily/bulk_mark/",{method:"POST",body:{classroom:classroomId,date,entries},token:session.token});
    q("#attendance-form-error").textContent="";
    alert(`Register saved for ${res.marked} student${res.marked===1?"":"s"}.`);
    loadRecentAttendance();
  }catch(err){
    q("#attendance-form-error").textContent=err.message;
  }finally{
    e.target.disabled=false;
  }
});

async function loadRecentAttendance(){
  const target=q("#attendance-recent");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const res=await api("/attendance/daily/?page_size=20",{token:session.token});
    const records=res.results||res;
    target.innerHTML=records.length?records.map(r=>`<p><strong>${r.student_name}</strong><small>${r.date} · ${r.status[0].toUpperCase()+r.status.slice(1)}${r.reason?" · "+r.reason:""}</small></p>`).join(""):`<p class="muted-note">No attendance recorded yet.</p>`;
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load recent records: ${err.message}</p>`;
  }
}

/* ---------- Fees & finance admin ---------- */
const FEE_TYPE_LABELS={tuition:"Tuition",admission:"Admission",transportation:"Transportation",meals:"Meals/Cafeteria",lab:"Laboratory",library:"Library",sports:"Sports",extracurricular:"Extracurricular",technology:"Technology",annual:"Annual",other:"Other"};
let allFeeStructures=[],allFeeAccounts=[],allFeePayments=[];

async function loadFeesAdmin(){
  const target=q("#fee-structure-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const [structRes,acctRes,payRes,studentsRes]=await Promise.all([
      api("/fees/fee-structures/",{token:session.token}),
      api("/fees/fee-accounts/",{token:session.token}),
      api("/fees/fee-payments/",{token:session.token}),
      api("/auth/users/?role=student",{token:session.token}),
    ]);
    allFeeStructures=structRes.results||structRes;
    allFeeAccounts=acctRes.results||acctRes;
    allFeePayments=payRes.results||payRes;
    const students=studentsRes.results||studentsRes;

    const studentSelect=q("#fee-account-student-select");
    if(studentSelect)studentSelect.innerHTML=students.map(s=>`<option value="${s.id}">${(s.first_name||s.last_name)?`${s.first_name} ${s.last_name}`.trim():s.username} (${s.student_id||s.username})</option>`).join("")||`<option value="">No students yet</option>`;
    const acctSelect=q("#fee-payment-account-select");
    if(acctSelect)acctSelect.innerHTML=allFeeAccounts.map(a=>`<option value="${a.id}">${a.student_name} · ${a.academic_year} · Due US$ ${a.fees_due}</option>`).join("")||`<option value="">Open a fee account first</option>`;

    renderFeeStructures();renderFeeAccounts();renderFeePayments();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load fees: ${err.message}</p>`;
  }
}
function renderFeeStructures(){
  const target=q("#fee-structure-list");if(!target)return;
  target.innerHTML=allFeeStructures.length?allFeeStructures.map(f=>`<article class="admin-application"><div><h3>${f.name}</h3><p>${FEE_TYPE_LABELS[f.fee_type]||f.fee_type} · ${GRADE_LABELS_FULL[f.grade_level]||f.grade_level} · ${f.academic_year} · US$ ${f.amount}${f.due_date?" · Due "+f.due_date:""}</p></div><div class="decision-actions"><button class="reject-button" data-delete-feestructure="${f.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No fee structures yet.</p>`;
}
function renderFeeAccounts(){
  const target=q("#fee-account-list");if(!target)return;
  target.innerHTML=allFeeAccounts.length?allFeeAccounts.map(a=>`<article class="admin-application"><div><h3>${a.student_name}</h3><p>${a.academic_year} · Total US$ ${a.total_fees} · Paid US$ ${a.fees_paid} · Due US$ ${a.fees_due}</p></div></article>`).join(""):`<p class="muted-note">No fee accounts opened yet.</p>`;
}
function renderFeePayments(){
  const target=q("#fee-payment-list");if(!target)return;
  target.innerHTML=allFeePayments.length?allFeePayments.map(p=>`<article class="admin-application"><div><h3>${p.student_name}</h3><p>${p.receipt_number} · US$ ${p.amount} · ${p.payment_method.replace("_"," ")} · ${new Date(p.payment_date).toLocaleDateString()}</p></div></article>`).join(""):`<p class="muted-note">No payments recorded yet.</p>`;
}

wireAdminForm("#fee-structure-form","/fees/fee-structures/",d=>({name:d.get("name"),fee_type:d.get("fee_type"),grade_level:d.get("grade_level"),academic_year:d.get("academic_year"),amount:d.get("amount"),due_date:d.get("due_date")||null}),"#fee-structure-form-error",loadFeesAdmin);
wireAdminForm("#fee-account-form","/fees/fee-accounts/",d=>({student:d.get("student"),academic_year:d.get("academic_year"),total_fees:d.get("total_fees")}),"#fee-account-form-error",loadFeesAdmin);
wireAdminForm("#fee-payment-form","/fees/fee-payments/",d=>({fee_account:d.get("fee_account"),amount:d.get("amount"),payment_method:d.get("payment_method"),notes:d.get("notes")||""}),"#fee-payment-form-error",loadFeesAdmin);
wireAdminDeleteList("#fee-structure-list","deleteFeestructure",id=>`/fees/fee-structures/${id}/`,loadFeesAdmin,"Delete this fee structure?");

/* ---------- Marks & results admin ---------- */
let allAssessments=[];

async function loadResultsAdmin(){
  const target=q("#assessment-list");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const [assessRes,subjRes,roomsRes,termsRes]=await Promise.all([
      api("/examinations/assessments/",{token:session.token}),
      api("/academics/subjects/",{token:session.token}),
      api("/academics/classrooms/",{token:session.token}),
      api("/academics/terms/",{token:session.token}),
    ]);
    allAssessments=assessRes.results||assessRes;
    const subjects=subjRes.results||subjRes;
    const rooms=roomsRes.results||roomsRes;
    const terms=termsRes.results||termsRes;

    const subjSelect=q("#assessment-subject-select");
    if(subjSelect)subjSelect.innerHTML=subjects.map(s=>`<option value="${s.id}">${s.name}</option>`).join("")||`<option value="">Add a subject first</option>`;
    const roomSelect=q("#assessment-classroom-select");
    if(roomSelect)roomSelect.innerHTML=rooms.map(c=>`<option value="${c.id}">${c.name} (${c.academic_year})</option>`).join("")||`<option value="">Add a classroom first</option>`;
    const termSelect=q("#assessment-term-select");
    if(termSelect)termSelect.innerHTML=`<option value="">— none —</option>`+terms.map(t=>`<option value="${t.id}">${t.term_label} ${t.academic_year}</option>`).join("");
    const markSelect=q("#marks-assessment-select");
    if(markSelect)markSelect.innerHTML=`<option value="">Select an assessment…</option>`+allAssessments.map(a=>`<option value="${a.id}">${a.name} · ${a.classroom_name} · ${a.subject_name}</option>`).join("");

    renderAssessments();
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load assessments: ${err.message}</p>`;
  }
}
function renderAssessments(){
  const target=q("#assessment-list");if(!target)return;
  target.innerHTML=allAssessments.length?allAssessments.map(a=>`<article class="admin-application"><div><h3>${a.name}</h3><p>${a.classroom_name} · ${a.subject_name} · ${a.assessment_type} · ${a.date} · ${a.marked_count} marked${a.class_average!=null?" · Avg "+a.class_average:""}${a.published?" · Published":""}</p></div><div class="decision-actions"><button class="reject-button" data-delete-assessment="${a.id}">Delete</button></div></article>`).join(""):`<p class="muted-note">No assessments yet.</p>`;
}
wireAdminForm("#assessment-form","/examinations/assessments/",d=>({name:d.get("name"),subject:d.get("subject"),classroom:d.get("classroom"),term:d.get("term")||null,assessment_type:d.get("assessment_type"),max_score:d.get("max_score")||100,date:d.get("date"),published:d.get("published")==="on"}),"#assessment-form-error",loadResultsAdmin);
wireAdminDeleteList("#assessment-list","deleteAssessment",id=>`/examinations/assessments/${id}/`,loadResultsAdmin,"Delete this assessment and all its marks?");

q("#marks-load-form")?.addEventListener("submit",async e=>{
  e.preventDefault();
  const session=getAdminSession();if(!session)return;
  const assessmentId=q("#marks-assessment-select").value;
  if(!assessmentId)return;
  const assessment=allAssessments.find(a=>String(a.id)===assessmentId);
  const target=q("#marks-sheet");
  target.innerHTML=`<p class="muted-note">Loading…</p>`;
  try{
    const [studentsRes,existingRes]=await Promise.all([
      api("/auth/users/?role=student",{token:session.token}),
      api(`/examinations/marks/?assessment=${assessmentId}`,{token:session.token}),
    ]);
    const roster=(studentsRes.results||studentsRes).filter(s=>String(s.classroom)===String(assessment.classroom));
    const existing=existingRes.results||existingRes;
    const existingByStudent={};
    existing.forEach(m=>existingByStudent[m.student]=m);
    if(!roster.length){target.innerHTML=`<p class="muted-note">No students are placed in ${assessment.classroom_name} yet.</p>`;return}
    target.innerHTML=`<div class="attendance-rows">${roster.map(s=>{
      const mark=existingByStudent[s.id];
      const name=(s.first_name||s.last_name)?`${s.first_name} ${s.last_name}`.trim():s.username;
      return `<div class="attendance-row" data-student="${s.id}"><span>${name} <small>${s.student_id||s.username}</small></span><input class="mark-score" type="number" min="0" max="${assessment.max_score}" step="0.5" placeholder="/ ${assessment.max_score}" value="${mark?mark.score:""}"><input class="mark-comments" placeholder="Comments (optional)" value="${mark?mark.comments:""}"></div>`;
    }).join("")}</div><div class="attendance-actions"><button class="primary-button" id="save-marks" type="button">Save marks</button><p id="marks-form-error" class="form-error"></p></div><div id="marks-report"></div>`;
    loadMarksReport(assessmentId);
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load the mark sheet: ${err.message}</p>`;
  }
});

q("#marks-sheet")?.addEventListener("click",async e=>{
  if(e.target.id!=="save-marks")return;
  const session=getAdminSession();if(!session)return;
  const assessmentId=q("#marks-assessment-select").value;
  const entries=qa(".attendance-row").map(row=>({
    student:row.dataset.student,
    score:row.querySelector(".mark-score").value,
    comments:row.querySelector(".mark-comments").value,
  })).filter(entry=>entry.score!=="");
  e.target.disabled=true;
  try{
    const res=await api("/examinations/marks/bulk_mark/",{method:"POST",body:{assessment:assessmentId,entries},token:session.token});
    q("#marks-form-error").textContent=res.errors&&res.errors.length?res.errors.join(" "):"";
    alert(`Saved ${res.marked} mark${res.marked===1?"":"s"}.`);
    await loadResultsAdmin();
    loadMarksReport(assessmentId);
  }catch(err){
    q("#marks-form-error").textContent=err.message;
  }finally{
    e.target.disabled=false;
  }
});

async function loadMarksReport(assessmentId){
  const target=q("#marks-report");if(!target)return;
  const session=getAdminSession();if(!session)return;
  try{
    const res=await api(`/examinations/assessments/${assessmentId}/report/`,{token:session.token});
    target.innerHTML=`<h3 class="staff-category-head">Ranking <span>Class average: ${res.class_average!=null?res.class_average:"—"}</span></h3>`+
      (res.rows.length?res.rows.map(r=>`<p><strong>#${r.rank} ${r.student_name}</strong><small>${r.score} (${r.percentage}%) · Grade ${r.letter_grade}</small></p>`).join(""):`<p class="muted-note">No marks recorded yet.</p>`);
  }catch(err){
    target.innerHTML=`<p class="muted-note">Could not load the report: ${err.message}</p>`;
  }
}
