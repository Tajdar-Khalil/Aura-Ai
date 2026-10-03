from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{
  --bg:#020817;--bg2:#071a3f;--panel:rgba(7,24,60,.82);--panel2:rgba(9,31,78,.72);
  --line:rgba(62,151,255,.34);--blue:#1688ff;--blue2:#0b63d8;--blue3:#55b2ff;
  --cyan:#27e2c0;--violet:#a96cff;--text:#f5f8ff;--muted:#9db8e6;
}
*{box-sizing:border-box}
html,body,.stApp{margin:0!important;padding:0!important;min-width:0!important}
.stApp{font-family:'Plus Jakarta Sans',system-ui,sans-serif;color:var(--text);background:
  radial-gradient(900px 520px at 88% 5%,rgba(22,136,255,.25),transparent 62%),
  radial-gradient(700px 480px at 8% 0%,rgba(30,91,210,.22),transparent 62%),
  linear-gradient(155deg,var(--bg) 0%,#041330 55%,#08275d 100%);
background-attachment:fixed}
#MainMenu,footer,header{visibility:hidden;height:0}
.block-container{width:100%;max-width:1540px!important;padding:0 22px 30px!important;margin:0 auto!important}

/* ---------- Public header / navigation ---------- */
.topbar{
  min-height:70px;display:flex;align-items:center;justify-content:space-between;gap:24px;
  margin:0 -22px 12px;padding:0 28px;border-bottom:1px solid rgba(77,140,255,.18);
  background:rgba(2,8,23,.88);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  position:sticky;top:0;z-index:50;
}
.brand{display:flex;align-items:center;gap:11px;min-width:0}.brand-mark{font-size:31px;line-height:1;color:#45a9ff;text-shadow:0 0 20px rgba(69,169,255,.9)}
.brand-name{font-size:25px;font-weight:800;letter-spacing:-.8px;white-space:nowrap}.brand-name span{color:#39a4ff}.brand-divider{height:29px;width:1px;background:var(--line);margin:0 3px}.brand-sub{font-size:14px;color:#a9c2e9;white-space:nowrap}

/* Streamlit's public navigation buttons: compact, blue, consistent */
.topbar + div [data-testid="stButton"]>button,
.stButton>button,.stFormSubmitButton>button{
  min-height:42px!important;border-radius:12px!important;border:1px solid rgba(64,150,255,.36)!important;
  background:linear-gradient(180deg,rgba(17,76,157,.92),rgba(8,50,112,.94))!important;
  color:#f4f8ff!important;font-weight:700!important;font-size:13px!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 6px 18px rgba(0,0,0,.18)!important;
  transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease,background .16s ease!important;
}
.stButton>button:hover,.stFormSubmitButton>button:hover{
  transform:translateY(-1px)!important;border-color:rgba(83,178,255,.82)!important;
  background:linear-gradient(180deg,#1688ff,#0c5fc8)!important;box-shadow:0 9px 24px rgba(9,100,220,.28)!important}
.stButton>button:active,.stFormSubmitButton>button:active{transform:translateY(0)!important}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{
  background:linear-gradient(180deg,#299bff,#0b63d8)!important;border-color:rgba(100,190,255,.65)!important;
  box-shadow:0 8px 25px rgba(14,119,239,.34)!important}

/* Keep the public nav close to the header instead of creating a huge empty band. */
.hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(360px,.95fr);gap:46px;align-items:center;
  padding:42px 0 34px;min-height:0}
.eyebrow{display:inline-flex;align-items:center;padding:8px 16px;border:1px solid #2685ec;border-radius:999px;
  color:#7cc3ff;background:rgba(22,136,255,.10);font-weight:700;font-size:13px;box-shadow:0 0 22px rgba(22,136,255,.08)}
.hero h1{font-size:clamp(42px,5.1vw,72px);line-height:1.04;letter-spacing:-2.8px;margin:22px 0 17px;max-width:820px}.gradient{background:linear-gradient(90deg,#42a9ff,#aa75ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-copy{color:#a9c1e6;font-size:17px;line-height:1.72;max-width:650px;margin-bottom:25px}
.primary-btn{display:inline-block}.primary-btn .stButton>button{min-width:190px!important}
.feature-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:12px 0 30px}.feature,.glass{background:linear-gradient(145deg,rgba(10,36,91,.82),rgba(6,25,63,.78));border:1px solid var(--line);border-radius:18px;box-shadow:0 14px 35px rgba(0,0,0,.14)}
.feature{padding:20px;min-height:150px}.feature-icon{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(145deg,#124caa,#08285f);color:#55b2ff;font-size:23px;margin-bottom:14px;box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}
.feature h3{font-size:15px;margin:0 0 8px}.feature p,.muted{color:var(--muted);font-size:13px;margin:0;line-height:1.55}
.aura-stage{position:relative;width:min(410px,84vw);aspect-ratio:1;margin:0 auto}.aura-stage:before{content:"";position:absolute;inset:-15px;border-radius:50%;border:2px solid rgba(25,145,255,.72);box-shadow:0 0 60px rgba(31,139,255,.32),inset 0 0 40px rgba(31,139,255,.13)}
.aura-stage:after{content:"";position:absolute;inset:-28px;border-radius:50%;border:1px solid rgba(67,154,255,.18)}
.aura-stage img{position:relative;z-index:1;width:100%;height:100%;object-fit:cover;object-position:50% 15%;border-radius:50%;border:3px solid rgba(83,173,255,.82);box-shadow:0 0 35px rgba(24,128,255,.22)}
.aura-bubble{position:absolute;z-index:3;right:-24px;bottom:-24px;max-width:245px;background:linear-gradient(145deg,#103c88,#08275f);border:1px solid rgba(70,157,255,.55);border-radius:18px;padding:14px 17px;box-shadow:0 18px 40px rgba(0,0,0,.45)}
.aura-bubble b{display:block}.aura-bubble span{font-size:12px;color:#abc4eb;display:block;margin-top:4px}
.section{padding:55px 0;border-top:1px solid rgba(77,140,255,.18)}.section h2{font-size:clamp(30px,4vw,42px);margin:0 0 10px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.glass{padding:22px}.glass h3{color:#79b9ff;font-size:16px;margin-top:0}.glass p{color:var(--muted);font-size:14px;line-height:1.7}
.footer{border-top:1px solid rgba(77,140,255,.18);padding:20px 0;color:#829bc5;font-size:12px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}

/* ---------- Dashboard ---------- */
.dash{display:grid;grid-template-columns:270px minmax(0,1fr) 330px;gap:16px;height:calc(100vh - 108px);min-height:650px}.panel{background:rgba(7,24,60,.72);border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 16px 40px rgba(0,0,0,.18)}
.side{display:flex;flex-direction:column;min-height:0}.side-menu{padding:12px}.side-menu .stButton>button{display:flex;justify-content:flex-start;text-align:left;background:rgba(8,31,78,.45)!important;border-color:rgba(64,150,255,.18)!important;height:45px}.side-menu .selected>button{background:linear-gradient(180deg,#1688ff,#0b63d8)!important;color:#fff!important;box-shadow:0 6px 18px rgba(31,139,255,.35)!important}
.progress-card{padding:18px;margin-top:14px}.progress-row{display:flex;align-items:center;gap:14px}.ring{--p:0;width:70px;height:70px;border-radius:50%;background:conic-gradient(#1f8bff calc(var(--p)*1%),rgba(255,255,255,.09) 0);display:grid;place-items:center;flex:none;box-shadow:0 0 24px rgba(31,139,255,.15)}.ring>div{width:54px;height:54px;border-radius:50%;background:#0a2054;display:grid;place-items:center;font-weight:800}
.recent{margin-top:14px;padding:16px;overflow:auto;flex:1}.chat-row{padding:12px 4px;border-bottom:1px solid rgba(77,140,255,.14)}.chat-row b{font-size:12px}.chat-row small{color:var(--muted);display:block;font-size:10px;margin-top:4px}
.chat-panel{display:flex;flex-direction:column;min-width:0}.chat-head{min-height:66px;display:flex;align-items:center;justify-content:space-between;padding:0 20px;border-bottom:1px solid var(--line)}.chat-title{display:flex;align-items:center;gap:12px}.spark{color:#3aa0ff;font-size:28px}.online{padding:7px 13px;border:1px solid rgba(34,224,192,.5);border-radius:999px;color:#7df0d8;font-size:11px;white-space:nowrap}.msg-area{padding:18px 20px;overflow:auto;flex:1}.bubble{max-width:88%;padding:14px 18px;border-radius:18px;background:rgba(20,52,120,.7);border:1px solid var(--line);margin:0 0 16px;font-size:14px;line-height:1.65}.bubble.me{margin-left:auto;background:linear-gradient(180deg,#1b4a9a,#143b80);border-top-right-radius:6px}.bubble.assistant{border-top-left-radius:6px}.bubble small{display:block;text-align:right;color:var(--muted);font-size:10px;margin-top:5px}.section-box{background:rgba(7,22,60,.65);border:1px solid var(--line);border-radius:14px;padding:14px;margin:12px 0}.section-box h5{color:#4db3ff;font-size:13px;margin:0 0 4px}.section-box ul{margin:5px 0 0;padding-left:18px;color:#dbe7ff;font-size:12px}.chip-row{display:flex;gap:8px;flex-wrap:wrap;padding:0 18px 10px}.input-row{padding:0 18px 18px}.input-row input{background:rgba(3,10,31,.55)!important;color:#fff!important}
.right-panel{overflow:auto}.aura-card{padding:18px}.aura-pic{width:220px;height:240px;margin:auto;position:relative}.aura-pic:before{content:"";position:absolute;inset:0 8px 22px;border-radius:50%;border:2px solid rgba(31,139,255,.7);box-shadow:0 0 40px rgba(31,139,255,.4)}.aura-pic img{position:absolute;left:50%;top:0;transform:translateX(-50%);width:200px;height:240px;object-fit:cover;object-position:50% 15%;border-radius:50% 50% 14px 14px;mask-image:linear-gradient(#000 70%,transparent)}.aura-card h2{margin:-28px 0 0;font-size:28px}.aura-card h2 span{font-size:10px;background:#1f8bff;padding:3px 8px;border-radius:7px}.fact{display:flex;gap:12px;align-items:center;padding:12px 16px;border-bottom:1px solid rgba(77,140,255,.14)}.fact:last-child{border:0}.fact-icon{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:rgba(31,139,255,.18);color:#7db8ff;flex:none}.fact b{font-size:12px;display:block}.fact small{color:var(--muted);font-size:10px}.quick{padding:16px}.quick h4{margin:0 0 10px}.quote{padding:12px 16px;color:#b9cdf0;font-size:11px}.profile-pill{display:flex;align-items:center;gap:8px}.profile-pill img{width:32px;height:32px;border-radius:50%;border:1px solid var(--line)}
[data-testid="stDialog"]{background:linear-gradient(170deg,#0d2a66,#071a45)!important;border:1px solid var(--line)!important;border-radius:20px!important}.auth-note{color:var(--muted);font-size:13px}.error{color:#ff8d99}.success{color:#7df0d8}

/* ---------- Responsive ---------- */
@media(max-width:1250px){
  .hero{grid-template-columns:1fr .82fr;gap:28px}.dash{grid-template-columns:240px minmax(0,1fr)}.right-panel{display:none}
}
@media(max-width:900px){
  .block-container{padding:0 16px 24px!important}.topbar{margin:0 -16px 10px;padding:0 18px;min-height:64px}.brand-sub,.brand-divider{display:none}
  .hero{grid-template-columns:1fr;padding:32px 0 24px}.hero h1{font-size:clamp(38px,9vw,58px);letter-spacing:-2px}.hero-copy{font-size:16px}.aura-stage{width:min(350px,72vw);margin:26px auto 42px}.feature-grid,.cards{grid-template-columns:1fr 1fr}.dash{grid-template-columns:1fr;height:auto;min-height:0}.side{display:block}.recent{max-height:250px}.right-panel{display:none}
}
@media(max-width:640px){
  .block-container{padding:0 12px 20px!important}.topbar{margin:0 -12px 8px;padding:0 14px;min-height:58px}.brand-mark{font-size:27px}.brand-name{font-size:22px}
  /* public navigation becomes a compact horizontal strip */
  .topbar + div [data-testid="stHorizontalBlock"]{gap:5px!important}
  .topbar + div .stButton>button{min-height:38px!important;padding:0 7px!important;font-size:11px!important;border-radius:9px!important}
  .hero{padding:24px 0 18px}.hero h1{font-size:40px}.hero-copy{font-size:15px;line-height:1.6}.aura-stage{width:min(300px,76vw)}.aura-bubble{right:-4px;bottom:-20px;max-width:205px;padding:11px 13px}.aura-bubble span{font-size:11px}
  .feature-grid,.cards{grid-template-columns:1fr}.feature{min-height:auto}.section{padding:38px 0}.footer{font-size:11px}
  .chat-head{padding:0 14px}.online{padding:6px 9px;font-size:10px}.msg-area{padding:14px}.bubble{max-width:94%;font-size:13px}.chip-row{padding:0 10px 8px}.input-row{padding:0 10px 12px}
}
@media(max-width:420px){
  .topbar + div .stButton>button{font-size:10px!important;padding:0 4px!important;min-height:36px!important}.hero h1{font-size:34px}.eyebrow{font-size:11px}.primary-btn .stButton>button{width:100%!important}.aura-stage{width:250px}.aura-bubble{position:relative;right:auto;bottom:auto;margin:-10px auto 0;width:max-content;max-width:92%}
}
</style>
""", unsafe_allow_html=True)
