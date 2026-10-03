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

/* Public header: logo + navigation live on the same line. */
.public-brand{height:62px;display:flex;align-items:center;gap:11px;white-space:nowrap;padding-left:2px}
.public-brand .brand-mark{font-size:31px;line-height:1;color:#3aa0ff;filter:drop-shadow(0 0 10px rgba(31,139,255,.75))}
.public-brand .brand-name{font-size:25px;font-weight:800;letter-spacing:-.03em}.public-brand .brand-name span{color:#1f8bff}
.public-brand .brand-divider{height:30px;width:1px;background:var(--line);margin:0 3px}
.public-brand .brand-sub{font-size:13px;color:#a9c1e6}
.contact-hero{padding:42px 0 22px;max-width:850px}
.contact-hero h2{font-size:clamp(34px,5vw,52px);line-height:1.08;margin:17px 0 10px;letter-spacing:-1.8px}
.contact-info-card,.contact-form-card{background:linear-gradient(145deg,rgba(10,36,91,.86),rgba(5,22,57,.82));border:1px solid var(--line);border-radius:20px;box-shadow:0 18px 45px rgba(0,0,0,.2)}
.contact-info-card{padding:28px;min-height:100%}.contact-info-card h3,.contact-form-card h3{font-size:21px;margin:0 0 7px}.contact-info-icon{width:52px;height:52px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(145deg,#1688ff,#0b4fa9);box-shadow:0 10px 25px rgba(31,139,255,.22);font-size:23px;margin-bottom:20px}
.contact-detail{display:flex;flex-direction:column;gap:3px;padding:16px 0;border-bottom:1px solid rgba(77,140,255,.14)}.contact-detail:last-child{border-bottom:0}.contact-detail b{font-size:12px;color:#76b9ff;text-transform:uppercase;letter-spacing:.08em}.contact-detail span{font-size:14px;color:#dbe7ff;line-height:1.55}
.contact-form-card{padding:28px}.contact-form-card .stTextInput,.contact-form-card .stTextArea{margin-top:3px}.contact-form-card [data-testid="stFormSubmitButton"]{margin-top:8px}
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
@media(max-width:1100px){
  .public-brand .brand-sub{display:none}.public-brand .brand-divider{display:none}
}
@media(max-width:900px){
  .block-container{padding:0 16px 24px!important}.topbar{margin:0 -16px 10px;padding:0 18px;min-height:64px}.brand-sub,.brand-divider{display:none}
  .hero{grid-template-columns:1fr;padding:32px 0 24px}.hero h1{font-size:clamp(38px,9vw,58px);letter-spacing:-2px}.hero-copy{font-size:16px}.aura-stage{width:min(350px,72vw);margin:26px auto 42px}.feature-grid,.cards{grid-template-columns:1fr 1fr}.dash{grid-template-columns:1fr;height:auto;min-height:0}.side{display:block}.recent{max-height:250px}.right-panel{display:none}
}
@media(max-width:640px){
  .block-container{padding:0 12px 20px!important}
  .public-brand{height:52px;gap:7px}.public-brand .brand-mark{font-size:26px}.public-brand .brand-name{font-size:20px}
  .contact-hero{padding:30px 0 16px}.contact-info-card,.contact-form-card{padding:20px}.contact-hero h2{font-size:35px}
  .topbar{margin:0 -12px 8px;padding:0 14px;min-height:58px}.brand-mark{font-size:27px}.brand-name{font-size:22px}
  .topbar + div [data-testid="stHorizontalBlock"]{gap:5px!important}
  .topbar + div .stButton>button{min-height:38px!important;padding:0 7px!important;font-size:11px!important;border-radius:9px!important}
  .hero{padding:24px 0 18px}.hero h1{font-size:40px}.hero-copy{font-size:15px;line-height:1.6}.aura-stage{width:min(300px,76vw)}.aura-bubble{right:-4px;bottom:-20px;max-width:205px;padding:11px 13px}.aura-bubble span{font-size:11px}
  .feature-grid,.cards{grid-template-columns:1fr}.feature{min-height:auto}.section{padding:38px 0}.footer{font-size:11px}
  .chat-head{padding:0 14px}.online{padding:6px 9px;font-size:10px}.msg-area{padding:14px}.bubble{max-width:94%;font-size:13px}.chip-row{padding:0 10px 8px}.input-row{padding:0 10px 12px}
}
@media(max-width:420px){
  .public-brand .brand-name{font-size:18px}
  .topbar + div .stButton>button{font-size:10px!important;padding:0 4px!important;min-height:36px!important}.hero h1{font-size:34px}.eyebrow{font-size:11px}.primary-btn .stButton>button{width:100%!important}.aura-stage{width:250px}.aura-bubble{position:relative;right:auto;bottom:auto;margin:-10px auto 0;width:max-content;max-width:92%}
}

/* Dashboard profile, notification and account controls */
.profile-menu-avatar{display:flex;justify-content:center;margin:8px 0 14px}.profile-menu-avatar img{width:72px;height:72px;border-radius:50%;border:2px solid rgba(62,150,255,.55);box-shadow:0 0 24px rgba(31,139,255,.25)}
.profile-panel{padding:28px;min-height:360px}.profile-large{display:flex;justify-content:center;margin:6px 0 16px}.profile-large img{width:120px;height:120px;border-radius:50%;border:3px solid rgba(62,150,255,.7);box-shadow:0 0 35px rgba(31,139,255,.28)}.profile-panel h2{text-align:center;margin:0}.profile-panel>p{text-align:center}.profile-progress{display:flex;justify-content:space-between;align-items:center;margin-top:28px}.profile-progress strong{color:#67b8ff;font-size:22px}.progress-bar{height:10px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden;margin:10px 0 24px}.progress-bar span{display:block;height:100%;background:linear-gradient(90deg,#1468d6,#36a2ff);border-radius:999px;transition:width .35s ease}.recent-time{display:block;color:var(--muted);font-size:10px;margin:-8px 4px 8px}.recent [data-testid="stButton"]>button{background:transparent!important;border:0!important;padding:5px 4px!important;text-align:left!important;font-size:12px!important;box-shadow:none!important}.recent [data-testid="stButton"]>button:hover{background:rgba(31,139,255,.08)!important}
[data-testid="stPopover"] button{border-color:rgba(62,150,255,.25)!important;background:rgba(8,31,78,.55)!important}
[data-testid="stPopover"] [data-testid="stVerticalBlock"]{gap:.45rem}
@media(max-width:640px){.profile-panel{padding:20px}.profile-menu-avatar img{width:60px;height:60px}}
/* ---------- Dashboard viewport / exact reference proportions ---------- */
.st-key-dashboard-shell{
  margin-top:86px!important;
  height:calc(100vh - 100px)!important;
  min-height:720px!important;
  width:100%!important;
  overflow:hidden!important;
}
.st-key-dashboard-shell > div[data-testid="stHorizontalBlock"]{
  height:100%!important;
  align-items:stretch!important;
  gap:16px!important;
}
.st-key-dashboard-shell [data-testid="column"]{
  min-width:0!important;
  height:100%!important;
  display:flex!important;
  flex-direction:column!important;
}
.st-key-dashboard-shell [data-testid="column"] > div{
  min-height:0!important;
  height:100%!important;
}

/* Dashboard header: never allow the brand to wrap into the distorted vertical logo. */
.topbar-brand{
  height:64px;display:flex;align-items:center;gap:11px;white-space:nowrap;overflow:hidden;
}
.topbar-brand .brand-mark{font-size:30px;line-height:1;color:#3aa0ff;filter:drop-shadow(0 0 10px rgba(31,139,255,.8));flex:0 0 auto}
.topbar-brand .brand-name{font-size:25px;font-weight:800;letter-spacing:-.03em;line-height:1;flex:0 0 auto}.topbar-brand .brand-name span{color:#1f8bff}
.topbar-brand .brand-divider{height:30px;width:1px;background:var(--line);flex:0 0 auto}
.topbar-brand .brand-sub{font-size:13px;color:#a9c1e6;overflow:hidden;text-overflow:ellipsis}

/* Three dashboard columns */
.st-key-dashboard-shell [data-testid="column"]:first-child{flex:1 1 19%!important}
.st-key-dashboard-shell [data-testid="column"]:nth-child(2){flex:1 1 56%!important}
.st-key-dashboard-shell [data-testid="column"]:nth-child(3){flex:1 1 25%!important}

/* Left navigation matches the supplied dashboard: compact, stacked blue controls. */
.st-key-dashboard-shell .side{height:100%;min-height:0;overflow:hidden}
.st-key-dashboard-shell .side > .stButton{margin-bottom:10px}
.st-key-dashboard-shell .side > .stButton > button{
  height:48px!important;min-height:48px!important;border-radius:12px!important;text-align:left!important;
  justify-content:flex-start!important;padding:0 18px!important;background:linear-gradient(180deg,rgba(18,73,151,.92),rgba(8,48,108,.94))!important;
  border-color:rgba(61,143,255,.38)!important;font-size:13px!important;font-weight:700!important;
}
.st-key-dashboard-shell .side > .stButton > button:hover{background:linear-gradient(180deg,#1688ff,#0b63d8)!important}
.st-key-dashboard-shell .side > .selected > div > button,
.st-key-dashboard-shell .side > .selected button{background:linear-gradient(180deg,#1688ff,#0b63d8)!important;box-shadow:0 8px 24px rgba(15,108,231,.28)!important}
.st-key-dashboard-shell .progress-card{margin-top:4px!important;border-radius:18px!important}
.st-key-dashboard-shell .recent{min-height:0!important;overflow:auto!important}

/* Center chat is the dominant panel and fills from the header to the bottom. */
.st-key-dashboard-shell .chat-panel{
  height:100%!important;min-height:0!important;width:100%!important;
  display:flex!important;flex-direction:column!important;border-radius:18px!important;
}
.st-key-dashboard-shell .chat-head{height:72px;min-height:72px!important;flex:0 0 72px!important}
.st-key-dashboard-shell .msg-area{
  flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;
  padding:22px 24px 14px!important;scrollbar-width:thin;
}
.st-key-dashboard-shell .msg-area::-webkit-scrollbar{width:7px}.st-key-dashboard-shell .msg-area::-webkit-scrollbar-thumb{background:rgba(78,151,255,.28);border-radius:10px}
.st-key-dashboard-shell .bubble{max-width:min(88%,820px)!important}
.st-key-dashboard-shell .welcome-bubble{margin-top:auto!important}
.st-key-dashboard-shell .chip-row{flex:0 0 auto!important}
.st-key-dashboard-shell .input-row{flex:0 0 auto!important}
.st-key-dashboard-shell .chat-panel [data-testid="stForm"]{margin-top:0!important}
.st-key-dashboard-shell .chat-panel [data-testid="stForm"] [data-testid="stHorizontalBlock"]{align-items:center!important}

/* Keep the right information rail stable rather than letting it distort the chat. */
.st-key-dashboard-shell .right-panel{height:100%!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;padding-right:2px}
.st-key-dashboard-shell .aura-card{min-height:365px!important}
.st-key-dashboard-shell .aura-pic{width:min(240px,82%)!important;height:250px!important}
.st-key-dashboard-shell .aura-pic img{width:min(220px,100%)!important;height:250px!important}
.st-key-dashboard-shell .quick{margin-top:14px!important}

/* Make Streamlit's native form controls look like the reference input bar. */
.st-key-dashboard-shell .chat-panel [data-testid="stTextInput"] input{
  height:46px!important;border-radius:11px!important;background:rgba(3,10,31,.72)!important;
  border:1px solid rgba(77,140,255,.28)!important;color:#f5f8ff!important;font-size:13px!important;
}
.st-key-dashboard-shell .chat-panel [data-testid="stTextInput"] input:focus{border-color:#299bff!important;box-shadow:0 0 0 1px #299bff!important}
.st-key-dashboard-shell .chat-panel [data-testid="stFormSubmitButton"] button{height:46px!important;border-radius:11px!important}

/* Header controls on dashboard */
[data-testid="stPopover"] > button{height:44px!important;border-radius:10px!important;background:rgba(9,31,78,.75)!important}
[data-testid="stPopover"] > div{background:linear-gradient(160deg,#0b2458,#061634)!important;border:1px solid rgba(62,151,255,.4)!important}

@media(max-width:1250px){
  .st-key-dashboard-shell [data-testid="column"]:nth-child(3){display:none!important}
  .st-key-dashboard-shell [data-testid="column"]:first-child{flex-basis:240px!important;flex-grow:0!important}
  .st-key-dashboard-shell [data-testid="column"]:nth-child(2){flex:1 1 auto!important}
}
@media(max-width:900px){
  .st-key-dashboard-shell{height:auto!important;min-height:0!important;overflow:visible!important}
  .st-key-dashboard-shell > div[data-testid="stHorizontalBlock"]{height:auto!important}
  .st-key-dashboard-shell [data-testid="column"]{height:auto!important;display:block!important}
  .st-key-dashboard-shell [data-testid="column"] > div{height:auto!important}
  .st-key-dashboard-shell .chat-panel{height:calc(100vh - 110px)!important;min-height:620px!important}
  .st-key-dashboard-shell [data-testid="column"]:first-child{display:block!important}
  .st-key-dashboard-shell .side{height:auto!important;overflow:visible!important}
}
@media(max-width:640px){
  .topbar-brand .brand-sub,.topbar-brand .brand-divider{display:none}
  .topbar-brand .brand-name{font-size:21px}
  .st-key-dashboard-shell .chat-panel{height:calc(100vh - 96px)!important;min-height:560px!important}
  .st-key-dashboard-shell .chat-head{padding:0 14px!important}
  .st-key-dashboard-shell .msg-area{padding:16px 12px 10px!important}
  .st-key-dashboard-shell .bubble{max-width:94%!important;font-size:13px!important}
}


/* Streamlit-native dashboard containers: these are the actual widget parents. */
.st-key-dashboard-chat{
  height:100%!important;min-height:0!important;display:flex!important;flex-direction:column!important;
  background:rgba(7,24,60,.72);border:1px solid var(--line);border-radius:18px;overflow:hidden;
  box-shadow:0 16px 40px rgba(0,0,0,.18);padding:0!important;
}
.st-key-dashboard-chat > div{min-height:0!important}
.st-key-dashboard-chat > div:first-child{flex:0 0 auto!important}
.st-key-dashboard-messages{
  flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;
  padding:20px 22px 10px!important;scrollbar-width:thin;
}
.st-key-dashboard-messages::-webkit-scrollbar{width:7px}
.st-key-dashboard-messages::-webkit-scrollbar-thumb{background:rgba(78,151,255,.28);border-radius:10px}
.st-key-dashboard-messages .bubble{max-width:min(88%,820px)!important}
.st-key-dashboard-left{
  height:100%!important;min-height:0!important;overflow:hidden!important;display:flex!important;flex-direction:column!important;
}
.st-key-dashboard-left .progress-card{flex:0 0 auto!important}
.st-key-dashboard-left .recent{flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important}
.st-key-dashboard-right{
  height:100%!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;
}
.st-key-dashboard-right .aura-card{background:rgba(7,24,60,.72);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 16px 40px rgba(0,0,0,.18)}
.st-key-dashboard-right .facts-card{background:rgba(7,24,60,.62);border:1px solid var(--line);border-radius:18px;margin-top:12px;overflow:hidden}
.st-key-dashboard-right .quick{background:rgba(7,24,60,.62);border:1px solid var(--line);border-radius:18px;margin-top:12px;padding:16px}
.st-key-dashboard-right .quote{background:transparent;padding:16px 8px}
.st-key-dashboard-right .stButton>button{min-height:42px!important}

@media(max-width:1250px){
  .st-key-dashboard-chat{min-height:calc(100vh - 120px)!important}
}
@media(max-width:900px){
  .st-key-dashboard-chat{height:calc(100vh - 110px)!important;min-height:620px!important}
  .st-key-dashboard-messages{min-height:0!important}
}
@media(max-width:640px){
  .st-key-dashboard-chat{height:calc(100vh - 96px)!important;min-height:560px!important}
  .st-key-dashboard-messages{padding:14px 12px 8px!important}
}



/* =========================================================
   FINAL RESPONSIVE PASS
   Purpose: eliminate horizontal overflow and keep the AuraAI
   dashboard usable on phones from ~320px to tablets.
   ========================================================= */

/* Global viewport protection */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
  width:100% !important;
  max-width:100% !important;
  min-width:0 !important;
  overflow-x:hidden !important;
}
.block-container {
  padding-left:22px !important;
  padding-right:22px !important;
}

/* Dashboard header: compact single-row reference-style header */
.st-key-dashboard-header {
  position:fixed !important;
  top:0 !important;
  left:0 !important;
  right:0 !important;
  width:100vw !important;
  margin:0 !important;
  padding:0 28px !important;
  min-height:72px !important;
  height:72px !important;
  background:rgba(2,8,23,.94) !important;
  border-bottom:1px solid rgba(77,140,255,.20) !important;
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  z-index:9999 !important;
}
.st-key-dashboard-header > div[data-testid="stHorizontalBlock"] {
  min-height:72px !important;
  align-items:center !important;
  gap:12px !important;
}
.st-key-dashboard-header [data-testid="column"] {
  min-width:0 !important;
  display:flex !important;
  align-items:center !important;
}
.st-key-dashboard-header [data-testid="column"]:first-child {
  flex:1 1 auto !important;
}
.st-key-dashboard-header [data-testid="column"]:nth-child(2) {
  flex:0 0 24px !important;
}
.st-key-dashboard-header [data-testid="column"]:nth-child(3) {
  flex:0 0 46px !important;
}
.st-key-dashboard-header [data-testid="column"]:nth-child(4) {
  flex:0 0 190px !important;
}
.st-key-dashboard-header .topbar-brand {
  width:100% !important;
  min-width:0 !important;
  height:64px !important;
}
.st-key-dashboard-header .brand-sub {
  white-space:nowrap !important;
  overflow:hidden !important;
  text-overflow:ellipsis !important;
}
.st-key-dashboard-header [data-testid="stPopover"] > button {
  width:100% !important;
  min-width:0 !important;
  overflow:hidden !important;
  white-space:nowrap !important;
  text-overflow:ellipsis !important;
}

/* Mobile navigation blocks are hidden until the phone breakpoint */
.st-key-mobile-dashboard-nav,
.st-key-mobile-public-nav {
  display:none !important;
}

/* Keep dashboard rails from creating minimum-width overflow */
.st-key-dashboard-shell,
.st-key-dashboard-shell > div[data-testid="stHorizontalBlock"],
.st-key-dashboard-shell [data-testid="column"] {
  min-width:0 !important;
  max-width:100% !important;
}
.st-key-dashboard-shell .chat-panel,
.st-key-dashboard-shell .msg-area,
.st-key-dashboard-shell .right-panel,
.st-key-dashboard-shell .side {
  min-width:0 !important;
  max-width:100% !important;
}

/* Chat controls must be allowed to shrink */
.st-key-dashboard-chat [data-testid="stForm"] [data-testid="stHorizontalBlock"],
.st-key-dashboard-chat [data-testid="stForm"] [data-testid="column"] {
  min-width:0 !important;
}
.st-key-dashboard-chat [data-testid="stTextInput"] {
  min-width:0 !important;
}
.st-key-dashboard-chat [data-testid="stTextInput"] input {
  max-width:100% !important;
  min-width:0 !important;
}
.st-key-dashboard-chat .chip-row {
  max-width:100% !important;
  overflow:hidden !important;
}

/* Public header desktop/mobile */
.st-key-public-header {
  margin:0 -22px 12px !important;
  padding:0 22px !important;
  border-bottom:1px solid rgba(77,140,255,.18) !important;
  background:rgba(2,8,23,.86) !important;
  min-height:70px !important;
}
.st-key-public-header > div[data-testid="stHorizontalBlock"] {
  min-height:70px !important;
  align-items:center !important;
}
.st-key-public-header [data-testid="column"] {
  min-width:0 !important;
}

/* Make all cards and media shrink instead of pushing the viewport */
img, video, iframe, svg, canvas {
  max-width:100% !important;
}
.feature, .glass, .panel, .contact-info-card, .contact-form-card,
.aura-card, .facts-card, .quick, .section-box {
  min-width:0 !important;
  max-width:100% !important;
}

/* Tablet */
@media (max-width: 900px) {
  .block-container {
    padding-left:16px !important;
    padding-right:16px !important;
  }

  /* Dashboard header */
  .st-key-dashboard-header {
    padding:0 18px !important;
    min-height:64px !important;
    height:64px !important;
  }
  .st-key-dashboard-header > div[data-testid="stHorizontalBlock"] {
    min-height:64px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(4) {
    flex-basis:150px !important;
  }
  .st-key-dashboard-header .brand-sub {
    display:none !important;
  }
  .st-key-dashboard-header .brand-divider {
    display:none !important;
  }

  /* On tablet the right information rail is hidden; chat gets the space. */
  .st-key-dashboard-shell [data-testid="column"]:nth-child(3) {
    display:none !important;
  }
  .st-key-dashboard-shell [data-testid="column"]:first-child {
    flex:0 0 220px !important;
  }
  .st-key-dashboard-shell [data-testid="column"]:nth-child(2) {
    flex:1 1 auto !important;
    width:auto !important;
  }
}

/* Phone */
@media (max-width: 640px) {
  .block-container {
    padding-left:12px !important;
    padding-right:12px !important;
    padding-bottom:18px !important;
  }

  /* ---- Dashboard top navigation ---- */
  .st-key-dashboard-header {
    padding:0 12px !important;
    min-height:58px !important;
    height:58px !important;
    border-radius:0 !important;
  }
  .st-key-dashboard-header > div[data-testid="stHorizontalBlock"] {
    min-height:58px !important;
    height:58px !important;
    gap:6px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:first-child {
    flex:1 1 auto !important;
    width:auto !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(2) {
    display:none !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(3) {
    display:flex !important;
    flex:0 0 42px !important;
    width:42px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(4) {
    display:flex !important;
    flex:0 0 112px !important;
    width:112px !important;
  }
  .st-key-dashboard-header .topbar-brand {
    height:54px !important;
    gap:7px !important;
    overflow:hidden !important;
  }
  .st-key-dashboard-header .brand-mark {
    font-size:26px !important;
  }
  .st-key-dashboard-header .brand-name {
    font-size:20px !important;
  }
  .st-key-dashboard-header .brand-divider,
  .st-key-dashboard-header .brand-sub {
    display:none !important;
  }
  .st-key-dashboard-header [data-testid="stPopover"] > button {
    height:40px !important;
    min-height:40px !important;
    padding:0 7px !important;
    border-radius:10px !important;
    font-size:11px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(3) [data-testid="stPopover"] > button {
    font-size:18px !important;
    padding:0 !important;
  }

  /* ---- Mobile dashboard menu ---- */
  .st-key-mobile-dashboard-nav {
    display:block !important;
    margin:0 0 10px !important;
  }
  .st-key-mobile-dashboard-nav [data-testid="stExpander"] {
    border:1px solid rgba(62,151,255,.28) !important;
    border-radius:12px !important;
    background:rgba(7,24,60,.62) !important;
    overflow:hidden !important;
  }
  .st-key-mobile-dashboard-nav [data-testid="stExpander"] summary {
    padding:11px 13px !important;
  }
  .st-key-mobile-dashboard-nav [data-testid="stExpanderDetails"] {
    padding:8px 10px 12px !important;
  }
  .st-key-mobile-dashboard-nav [data-testid="stButton"] > button {
    min-height:42px !important;
    padding:0 10px !important;
    font-size:11px !important;
    border-radius:9px !important;
  }
  .mobile-progress {
    display:flex !important;
    justify-content:space-between !important;
    align-items:center !important;
    gap:10px !important;
    margin-top:9px !important;
    padding:10px 12px !important;
    border:1px solid rgba(62,151,255,.20) !important;
    border-radius:10px !important;
    background:rgba(8,31,78,.48) !important;
    font-size:11px !important;
  }
  .mobile-progress span {
    color:var(--muted) !important;
    white-space:nowrap !important;
  }

  /* ---- Dashboard content: chat only on phone ---- */
  .st-key-dashboard-shell {
    margin-top:68px !important;
    height:auto !important;
    min-height:0 !important;
    overflow:visible !important;
    width:100% !important;
  }
  .st-key-dashboard-shell > div[data-testid="stHorizontalBlock"] {
    display:block !important;
    height:auto !important;
  }
  .st-key-dashboard-shell [data-testid="column"] {
    width:100% !important;
    max-width:100% !important;
    min-width:0 !important;
    display:block !important;
    height:auto !important;
  }
  .st-key-dashboard-shell [data-testid="column"]:first-child,
  .st-key-dashboard-shell [data-testid="column"]:nth-child(3) {
    display:none !important;
  }
  .st-key-dashboard-shell [data-testid="column"]:nth-child(2) {
    display:block !important;
    flex:none !important;
  }

  .st-key-dashboard-chat {
    width:100% !important;
    max-width:100% !important;
    height:calc(100dvh - 150px) !important;
    min-height:520px !important;
    max-height:calc(100dvh - 110px) !important;
    border-radius:14px !important;
  }
  .st-key-dashboard-chat .chat-head {
    min-height:62px !important;
    height:62px !important;
    padding:0 12px !important;
  }
  .st-key-dashboard-chat .chat-title {
    gap:8px !important;
    min-width:0 !important;
  }
  .st-key-dashboard-chat .chat-title > div {
    min-width:0 !important;
  }
  .st-key-dashboard-chat .chat-title .muted {
    white-space:nowrap !important;
    overflow:hidden !important;
    text-overflow:ellipsis !important;
  }
  .st-key-dashboard-chat .spark {
    font-size:23px !important;
  }
  .st-key-dashboard-chat .online {
    padding:5px 8px !important;
    font-size:9px !important;
    flex:0 0 auto !important;
  }
  .st-key-dashboard-messages {
    padding:13px 10px 7px !important;
    min-width:0 !important;
  }
  .st-key-dashboard-messages .bubble {
    max-width:96% !important;
    padding:11px 12px !important;
    margin-bottom:11px !important;
    font-size:12.5px !important;
    line-height:1.55 !important;
    overflow-wrap:anywhere !important;
  }
  .st-key-dashboard-messages .section-box {
    padding:10px !important;
    margin:9px 0 !important;
  }
  .st-key-dashboard-messages .section-box ul {
    padding-left:16px !important;
  }

  /* Quick prompt chips: wrap instead of forcing four narrow columns. */
  .st-key-dashboard-chat .chip-row {
    display:flex !important;
    flex-wrap:wrap !important;
    gap:6px !important;
    padding:5px 8px 7px !important;
    overflow:visible !important;
  }
  .st-key-dashboard-chat .chip-row [data-testid="column"] {
    flex:1 1 calc(50% - 6px) !important;
    width:auto !important;
    min-width:0 !important;
  }
  .st-key-dashboard-chat .chip-row [data-testid="stButton"] > button {
    min-height:36px !important;
    padding:0 6px !important;
    font-size:9.5px !important;
    white-space:normal !important;
    line-height:1.15 !important;
  }

  /* Chat input: icon, field and send button stay in one shrinkable row. */
  .st-key-dashboard-chat [data-testid="stForm"] {
    padding:0 8px 9px !important;
  }
  .st-key-dashboard-chat [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
    gap:6px !important;
    align-items:center !important;
  }
  .st-key-dashboard-chat [data-testid="stForm"] [data-testid="column"]:first-child {
    flex:0 0 28px !important;
    width:28px !important;
  }
  .st-key-dashboard-chat [data-testid="stForm"] [data-testid="column"]:nth-child(2) {
    flex:1 1 auto !important;
    width:auto !important;
  }
  .st-key-dashboard-chat [data-testid="stForm"] [data-testid="column"]:nth-child(3) {
    flex:0 0 42px !important;
    width:42px !important;
  }
  .st-key-dashboard-chat [data-testid="stTextInput"] input {
    height:42px !important;
    font-size:12px !important;
    padding:0 10px !important;
  }
  .st-key-dashboard-chat [data-testid="stFormSubmitButton"] button {
    height:42px !important;
    min-height:42px !important;
    padding:0 !important;
    font-size:16px !important;
  }

  /* Approval actions stack cleanly on narrow screens. */
  .st-key-dashboard-chat [data-testid="stWarning"] + [data-testid="stHorizontalBlock"] {
    flex-direction:column !important;
  }

  /* ---- Public header ---- */
  .st-key-public-header {
    margin-left:-12px !important;
    margin-right:-12px !important;
    margin-bottom:8px !important;
    padding:0 12px !important;
    min-height:58px !important;
  }
  .st-key-public-header > div[data-testid="stHorizontalBlock"] {
    min-height:58px !important;
    height:58px !important;
  }
  .st-key-public-header [data-testid="column"]:first-child {
    flex:1 1 100% !important;
    width:100% !important;
  }
  .st-key-public-header [data-testid="column"]:not(:first-child) {
    display:none !important;
  }
  .st-key-public-header .public-brand {
    height:52px !important;
    gap:7px !important;
  }
  .st-key-public-header .brand-mark {
    font-size:27px !important;
  }
  .st-key-public-header .brand-name {
    font-size:21px !important;
  }
  .st-key-public-header .brand-divider,
  .st-key-public-header .brand-sub {
    display:none !important;
  }

  .st-key-mobile-public-nav {
    display:block !important;
    margin:0 0 10px !important;
  }
  .st-key-mobile-public-nav [data-testid="stExpander"] {
    border:1px solid rgba(62,151,255,.28) !important;
    border-radius:12px !important;
    background:rgba(7,24,60,.62) !important;
  }
  .st-key-mobile-public-nav [data-testid="stButton"] > button {
    min-height:42px !important;
    font-size:11px !important;
    border-radius:9px !important;
  }

  /* Home / About / Contact */
  .hero {
    display:block !important;
    padding:24px 0 18px !important;
  }
  .hero h1 {
    font-size:clamp(34px,10vw,44px) !important;
    letter-spacing:-1.8px !important;
    overflow-wrap:anywhere !important;
  }
  .hero-copy {
    font-size:14px !important;
    line-height:1.6 !important;
  }
  .aura-stage {
    width:min(280px,78vw) !important;
    margin:28px auto 40px !important;
  }
  .aura-bubble {
    right:0 !important;
    bottom:-20px !important;
    max-width:calc(100% - 10px) !important;
  }
  .feature-grid, .cards {
    grid-template-columns:1fr !important;
  }
  .contact-hero h2 {
    font-size:34px !important;
  }
  .contact-info-card, .contact-form-card {
    padding:18px !important;
  }

  /* Native Streamlit inputs and buttons */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stSelectbox"] > div {
    max-width:100% !important;
  }
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea {
    font-size:16px !important; /* prevents iOS zoom */
  }
}

/* Very small phones */
@media (max-width: 380px) {
  .block-container {
    padding-left:10px !important;
    padding-right:10px !important;
  }
  .st-key-dashboard-header {
    margin-left:-10px !important;
    margin-right:-10px !important;
    padding:0 9px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(3) {
    flex-basis:38px !important;
    width:38px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(4) {
    flex-basis:96px !important;
    width:96px !important;
  }
  .st-key-dashboard-header [data-testid="column"]:nth-child(4) [data-testid="stPopover"] > button {
    font-size:10px !important;
    padding:0 5px !important;
  }
  .st-key-dashboard-header .brand-name {
    font-size:19px !important;
  }
  .st-key-dashboard-chat {
    min-height:500px !important;
    height:calc(100dvh - 145px) !important;
  }
  .st-key-dashboard-chat .online {
    display:none !important;
  }
  .st-key-dashboard-chat .chip-row [data-testid="column"] {
    flex-basis:100% !important;
  }
  .st-key-dashboard-chat .chip-row [data-testid="stButton"] > button {
    font-size:10px !important;
  }
}

/* Aura profile card */
.st-key-dashboard-right .aura-card {
  padding: 18px !important;
  display: block !important;
  overflow: hidden !important;
}

.st-key-dashboard-right .aura-pic {
  width: 220px !important;
  height: 240px !important;
  margin: 0 auto 4px !important;
  position: relative !important;
}

.st-key-dashboard-right .aura-card h2 {
  margin: -28px 0 0 !important;
  font-size: 28px !important;
  line-height: 1.15 !important;
}

.st-key-dashboard-right .aura-card .aura-role {
  margin: 7px 0 2px !important;
  color: var(--text) !important;
  font-size: 13px !important;
}

.st-key-dashboard-right .aura-card .muted {
  margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)
