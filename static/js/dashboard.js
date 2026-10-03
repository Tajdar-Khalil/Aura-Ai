const messages = document.getElementById("messages");
const input = document.getElementById("messageInput");
const sidebar = document.getElementById("sidebar");
const backdrop = document.getElementById("backdrop");
const mobileMenu = document.getElementById("mobileMenu");

function closeMenu(){sidebar?.classList.remove("open");backdrop?.classList.remove("show");mobileMenu?.setAttribute("aria-expanded","false")}
mobileMenu?.addEventListener("click",()=>{const open=sidebar.classList.toggle("open");backdrop.classList.toggle("show",open);mobileMenu.setAttribute("aria-expanded",String(open))});
backdrop?.addEventListener("click",closeMenu);

document.querySelectorAll(".nav-button").forEach(btn=>btn.addEventListener("click",()=>{
  document.querySelectorAll(".nav-button").forEach(b=>b.classList.remove("active"));
  btn.classList.add("active");
  document.getElementById("pageTitle").textContent=btn.dataset.page;
  closeMenu();
}));

function sendMessage(text){
  const value=(text ?? input.value).trim();
  if(!value)return;
  const row=document.createElement("div");
  row.className="message user-message";
  row.innerHTML='<div class="message-avatar">◉</div><div class="bubble"></div>';
  row.querySelector(".bubble").textContent=value;
  const time=document.createElement("time"); time.textContent="Just now ✓"; row.querySelector(".bubble").appendChild(time);
  messages.appendChild(row);
  messages.scrollTop=messages.scrollHeight;
  input.value="";
}

document.getElementById("composer")?.addEventListener("submit",e=>{e.preventDefault();sendMessage();});
document.querySelectorAll("[data-question]").forEach(btn=>btn.addEventListener("click",()=>sendMessage(btn.dataset.question)));
messages.scrollTop=messages.scrollHeight;
