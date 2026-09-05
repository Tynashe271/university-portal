const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];
// See the matching comment in portal.js — same site served from every
// environment, so the API host is resolved at runtime, not baked in.
const API_BASE=(()=>{
  const metaOverride=document.querySelector('meta[name="api-base"]')?.content;
  const host=location.hostname;
  if(metaOverride&&metaOverride!=="http://localhost:8000/api")return metaOverride;
  if(host==="anyschool-frontend-6c22.onrender.com")return "https://anyschool-backend-0hbm.onrender.com/api";
  if(host==="localhost"||host==="127.0.0.1")return "http://localhost:8000/api";
  return `${location.protocol}//${host}:8000/api`;
})();
// The header/footer/nav themselves are now rendered server-side by Blade
// (resources/views/partials/header.blade.php + footer.blade.php) instead
// of being injected here at runtime — this file only wires up their
// interactive bits.
const menu=$(".menu-toggle"),nav=$("#primary-nav");
if(menu)menu.addEventListener("click",()=>{const open=menu.getAttribute("aria-expanded")==="true";menu.setAttribute("aria-expanded",String(!open));nav.classList.toggle("open",!open)});
$("#year")&&($("#year").textContent=new Date().getFullYear());
const contrast=$("#contrast-toggle");
if(contrast){if(localStorage.getItem("anyschool-contrast")==="true"){document.body.classList.add("high-contrast");contrast.setAttribute("aria-pressed","true")}contrast.addEventListener("click",()=>{const active=document.body.classList.toggle("high-contrast");contrast.setAttribute("aria-pressed",String(active));localStorage.setItem("anyschool-contrast",String(active))})}
if("[data-count]"&&$("[data-count]")){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target,target=Number(el.dataset.count),start=performance.now();const tick=now=>{const n=Math.min(1,(now-start)/900);el.textContent=Math.round(target*(1-Math.pow(1-n,3)));if(n<1)requestAnimationFrame(tick)};requestAnimationFrame(tick);observer.unobserve(el)}),{threshold:.6});$$("[data-count]").forEach(el=>observer.observe(el))}
const appForm=$("#application-form");
if(appForm)appForm.addEventListener("submit",e=>{e.preventDefault();if(!appForm.reportValidity())return;const data=Object.fromEntries(new FormData(appForm).entries()),ref=`AH-2027-${Math.floor(1000+Math.random()*9000)}`,apps=JSON.parse(localStorage.getItem("anyschool-applications")||"{}");apps[ref]={...data,status:"Application received",date:new Date().toISOString()};localStorage.setItem("anyschool-applications",JSON.stringify(apps));$("#application-success").innerHTML=`<strong>Application saved.</strong> Your reference is <b>${ref}</b>. Keep it safe for tracking.`;appForm.reset()});
const trackForm=$("#track-form");
if(trackForm)trackForm.addEventListener("submit",e=>{e.preventDefault();const ref=$("#track-ref").value.trim().toUpperCase(),apps=JSON.parse(localStorage.getItem("anyschool-applications")||"{}"),app=apps[ref],result=$("#track-result");result.className=`track-result ${app?"success":"error"}`;result.textContent=app?`✓ ${app.status} — ${app.firstName} ${app.lastName}, ${app.level}. Submitted ${new Date(app.date).toLocaleDateString()}.`:"No application was found on this device. Check the reference and try again."});
const contactForm=$("#contact-form");
if(contactForm)contactForm.addEventListener("submit",e=>{e.preventDefault();const data=new FormData(contactForm),subject=encodeURIComponent(`[${data.get("topic")}] Website enquiry from ${data.get("name")}`),body=encodeURIComponent(`${data.get("message")}\n\nFrom: ${data.get("name")}\nEmail: ${data.get("email")}`);$("#contact-note").textContent="Your email application will open. Replace the placeholder school email before publishing.";location.href=`mailto:office@anyschool.example?subject=${subject}&body=${body}`});

/* ---------- Public news & events feed ---------- */
const newsGrid=$("#news-grid");
if(newsGrid){
  const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const catLabel=p=>p.category==="event"?"Event":"News";
  const dateFor=p=>new Date(p.category==="event"&&p.event_date?p.event_date:p.created_at);
  const longDate=d=>d.toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric"});
  const dayNum=d=>String(d.getDate()).padStart(2,"0");
  const monAbbr=d=>d.toLocaleDateString("en-GB",{month:"short"}).toUpperCase();
  fetch(API_BASE+"/news/posts/").then(r=>r.json()).then(data=>{
    const posts=data.results||data;
    if(!posts.length){newsGrid.innerHTML=`<p class="placeholder-note">No news or events have been posted yet — check back soon.</p>`;return}
    const [featured,...rest]=posts;
    const featuredHtml=`<article class="news-card main-news"><div class="news-art"><span>${catLabel(featured)}</span><b>${dayNum(dateFor(featured))}</b></div><div class="news-body"><small>${catLabel(featured)} · ${longDate(dateFor(featured))}${featured.location?" · "+esc(featured.location):""}</small><h3>${esc(featured.title)}</h3><p>${esc(featured.summary)}</p></div></article>`;
    const updatesHtml=rest.length?rest.map(p=>`<article><time><b>${dayNum(dateFor(p))}</b>${monAbbr(dateFor(p))}</time><div><small>${catLabel(p)}</small><h3>${esc(p.title)}</h3><p>${esc(p.summary)}</p></div></article>`).join(""):`<p class="placeholder-note">No further updates yet.</p>`;
    newsGrid.innerHTML=featuredHtml+`<div class="updates">${updatesHtml}</div>`;
  }).catch(()=>{newsGrid.innerHTML=`<p class="placeholder-note">Could not load news and events right now. Please try again later.</p>`});
}
