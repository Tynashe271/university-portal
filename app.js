const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];
const toast=(message)=>{const el=$("#toast");el.textContent=message;el.classList.add("show");clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>el.classList.remove("show"),3200)};

const menu=$(".menu-toggle"),nav=$("#primary-nav");
menu.addEventListener("click",()=>{const open=menu.getAttribute("aria-expanded")==="true";menu.setAttribute("aria-expanded",String(!open));nav.classList.toggle("open",!open)});
$$("nav a").forEach(a=>a.addEventListener("click",()=>{nav.classList.remove("open");menu.setAttribute("aria-expanded","false")}));
$("#year").textContent=new Date().getFullYear();

const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
  if(!entry.isIntersecting)return;
  const el=entry.target,target=Number(el.dataset.count),start=performance.now(),duration=900;
  const tick=now=>{const n=Math.min(1,(now-start)/duration);el.textContent=Math.round(target*(1-Math.pow(1-n,3)));if(n<1)requestAnimationFrame(tick)};
  requestAnimationFrame(tick);observer.unobserve(el);
}),{threshold:.6});
$$("[data-count]").forEach(el=>observer.observe(el));

const contrast=$("#contrast-toggle");
if(localStorage.getItem("chongogwe-contrast")==="true"){document.body.classList.add("high-contrast");contrast.setAttribute("aria-pressed","true")}
contrast.addEventListener("click",()=>{const active=document.body.classList.toggle("high-contrast");contrast.setAttribute("aria-pressed",String(active));localStorage.setItem("chongogwe-contrast",String(active))});

const dialog=$("#application-dialog"),form=$("#application-form"),steps=$$(".form-step",form),bars=$$(".progress span"),success=$("#application-success");
let currentStep=0;
function showStep(index){currentStep=index;steps.forEach((s,i)=>s.classList.toggle("active",i===index));bars.forEach((b,i)=>b.classList.toggle("active",i<=index));if(index===2){const d=new FormData(form);$("#application-summary").innerHTML=`<p><strong>Learner:</strong> ${escapeHtml(d.get("firstName"))} ${escapeHtml(d.get("lastName"))}</p><p><strong>Applying for:</strong> ${escapeHtml(d.get("level"))}</p><p><strong>Guardian:</strong> ${escapeHtml(d.get("guardianName"))}</p><p><strong>Contact:</strong> ${escapeHtml(d.get("phone"))} · ${escapeHtml(d.get("email"))}</p>`}}
function openApplication(){form.reset();success.hidden=true;form.hidden=false;showStep(0);dialog.showModal()}
$$("[data-open-application]").forEach(b=>b.addEventListener("click",openApplication));
$(".dialog-close").addEventListener("click",()=>dialog.close());
$(".dialog-done").addEventListener("click",()=>dialog.close());
dialog.addEventListener("click",e=>{if(e.target===dialog)dialog.close()});
$$(".next-step").forEach(button=>button.addEventListener("click",()=>{const fields=$$("input,select",steps[currentStep]);if(fields.some(field=>!field.reportValidity()))return;showStep(currentStep+1)}));
$$(".prev-step").forEach(button=>button.addEventListener("click",()=>showStep(currentStep-1)));
const escapeHtml=value=>String(value||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));

form.addEventListener("submit",e=>{
  e.preventDefault();
  if(!form.reportValidity())return;
  const data=Object.fromEntries(new FormData(form).entries());
  const ref=`CH-2027-${Math.floor(1000+Math.random()*9000)}`;
  const applications=JSON.parse(localStorage.getItem("chongogwe-applications")||"{}");
  applications[ref]={...data,status:"Application received",date:new Date().toISOString()};
  localStorage.setItem("chongogwe-applications",JSON.stringify(applications));
  form.hidden=true;success.hidden=false;$("#application-reference").textContent=ref;
});

$("#track-form").addEventListener("submit",e=>{
  e.preventDefault();const input=$("#track-ref"),ref=input.value.trim().toUpperCase(),result=$("#track-result");
  const applications=JSON.parse(localStorage.getItem("chongogwe-applications")||"{}"),app=applications[ref];
  if(app){result.className="track-result success";result.textContent=`✓ ${app.status} — ${app.firstName} ${app.lastName}, ${app.level}. Submitted ${new Date(app.date).toLocaleDateString()}.`}
  else{result.className="track-result error";result.textContent="No application was found on this device. Check the reference and try again."}
});

$("#contact-form").addEventListener("submit",e=>{
  e.preventDefault();const data=new FormData(e.currentTarget);
  const subject=encodeURIComponent(`[${data.get("topic")}] Website enquiry from ${data.get("name")}`);
  const body=encodeURIComponent(`${data.get("message")}\n\nFrom: ${data.get("name")}\nEmail: ${data.get("email")}`);
  $("#contact-note").textContent="Your email application will open. Replace the placeholder school email before publishing.";
  window.location.href=`mailto:office@chongogwe.example?subject=${subject}&body=${body}`;
});
