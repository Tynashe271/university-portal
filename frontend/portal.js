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
  }catch(err){
    q("#admin-error").textContent=err.message;
  }
};
if(adminDash&&getAdminSession()){q("#admin-login").hidden=true;adminDash.hidden=false;loadAdmin()}

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
}

function renderAdminList(){
  const target=q("#admin-applications");if(!target)return;
  const term=(q("#admin-search")?.value||"").toLowerCase();
  const entries=allApplications.filter(a=>(a.application_number+" "+a.student_name).toLowerCase().includes(term));
  q("#admin-total").textContent=allApplications.length;
  q("#admin-review").textContent=allApplications.filter(a=>["submitted","under_review"].includes(a.status)).length;
  q("#admin-accepted").textContent=allApplications.filter(a=>["approved","admitted","enrolled"].includes(a.status)).length;
  q("#admin-rejected").textContent=allApplications.filter(a=>a.status==="rejected").length;
  target.innerHTML=entries.length?entries.map(a=>`<article class="admin-application"><div><span class="decision-status ${statusClass(a.status)}">${STATUS_LABELS[a.status]||a.status}</span><h3>${a.student_name}</h3><p>${a.application_number} · ${GRADE_LABELS[a.grade_applying_for]||a.grade_applying_for} · ${a.academic_year}</p></div><div class="decision-actions"><button class="primary-button" data-review="${a.application_number}">Review application</button></div></article>`).join(""):`<div class="empty-state small-empty"><h2>No applications found</h2><p>Submit an application first or change your search.</p></div>`;
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
  q("#doc-review-modal").hidden=false;
}
function closeReview(){q("#doc-review-modal").hidden=true;reviewingRef=null}
q("#review-close")?.addEventListener("click",closeReview);
q("#doc-review-modal")?.addEventListener("click",e=>{if(e.target.id==="doc-review-modal")closeReview()});

async function decideReview(decision){
  if(!reviewingRef)return;
  const session=getAdminSession();if(!session)return;
  const btn=decision==="approve"?q("#review-accept"):q("#review-reject");
  btn.disabled=true;
  try{
    await api(`/admissions/applications/${encodeURIComponent(reviewingRef)}/${decision}/`,{method:"POST",token:session.token});
    closeReview();
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
  q("#applicant-details").innerHTML=`<p><span>Applying for</span><strong>${GRADE_LABELS[app.grade_applying_for]||app.grade_applying_for}</strong></p><p><span>Academic year</span><strong>${app.academic_year}</strong></p><p><span>Previous school</span><strong>${app.previous_school||"—"}</strong></p><p><span>Guardian</span><strong>${app.parent_name}</strong></p>`;
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
