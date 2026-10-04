/**
 * aura_auth.js - Centralized Authentication & Header State Manager for AuraAI
 * Connects forms with SQLite database backend, manages session, dynamic header & dashboard.
 */
(function(window) {
  const STORAGE_KEY = 'aura_user';

  const AuraAuth = {
    getUser: function() {
      try {
        const item = localStorage.getItem(STORAGE_KEY);
        return item ? JSON.parse(item) : null;
      } catch (e) {
        return null;
      }
    },

    setUser: function(user) {
      if (user) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    },

    clearUser: function() {
      localStorage.removeItem(STORAGE_KEY);
    },

    checkAuth: async function() {
      try {
        const res = await fetch('/api/auth/me');
        if (res.ok) {
          const data = await res.json();
          if (data.authenticated && data.user) {
            this.setUser(data.user);
            return data.user;
          }
        }
      } catch (e) {}
      
      // If server session expired but local storage has user, try sync or keep
      const local = this.getUser();
      return local;
    },

    login: async function(email, password) {
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.trim(), password: password })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          this.setUser(data.user);
          return { success: true, user: data.user };
        } else {
          return { success: false, error: data.error || 'Invalid email or password.' };
        }
      } catch (err) {
        // Local fallback if server endpoint is not hosted (e.g. Streamlit Cloud)
        try {
          const accounts = JSON.parse(localStorage.getItem('aura_accounts') || '[]');
          const found = accounts.find(a => a.email.toLowerCase() === email.trim().toLowerCase());
          if (found && found.password === password) {
            const userData = { id: found.id || 1, name: found.name, email: found.email, initials: this.getInitials(found.name) };
            this.setUser(userData);
            return { success: true, user: userData };
          } else if (found) {
            return { success: false, error: 'Incorrect password.' };
          } else {
            // If no accounts yet, accept as first demo login
            const userData = { id: 1, name: email.split('@')[0], email: email.trim(), initials: this.getInitials(email) };
            this.setUser(userData);
            return { success: true, user: userData };
          }
        } catch (e) {
          return { success: false, error: 'Authentication failed.' };
        }
      }
    },

    register: async function(name, email, password) {
      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name.trim(), email: email.trim(), password: password })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          this.setUser(data.user);
          return { success: true, user: data.user };
        } else {
          return { success: false, error: data.error || 'Failed to register account.' };
        }
      } catch (err) {
        // Local fallback if server endpoint is not hosted (e.g. Streamlit Cloud)
        try {
          let accounts = JSON.parse(localStorage.getItem('aura_accounts') || '[]');
          if (accounts.some(a => a.email.toLowerCase() === email.trim().toLowerCase())) {
            return { success: false, error: 'An account with this email already exists.' };
          }
          const newUser = { id: Date.now(), name: name.trim(), email: email.trim(), password: password };
          accounts.push(newUser);
          localStorage.setItem('aura_accounts', JSON.stringify(accounts));
          const userData = { id: newUser.id, name: newUser.name, email: newUser.email, initials: this.getInitials(newUser.name) };
          this.setUser(userData);
          return { success: true, user: userData };
        } catch (e) {
          return { success: false, error: 'Registration failed.' };
        }
      }
    },

    logout: async function() {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } catch (e) {}
      this.clearUser();
      if (window.top && window.top !== window) {
        window.top.location.search = '?page=index';
      } else {
        window.location.href = 'index.html';
      }
    },

    getInitials: function(name) {
      if (!name) return 'U';
      const parts = name.trim().split(/\s+/);
      if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }
      return name.slice(0, 2).toUpperCase();
    },

    /**
     * Updates public site headers (index.html, signin.html, signup.html, etc.)
     * Switches between [Login / Register] and [User Avatar + Dashboard Dropdown with Logout]
     */
    updatePublicHeader: function() {
      const user = this.getUser();
      const actionsContainers = document.querySelectorAll('.nav-actions, #headerAuthArea, .mobile-drawer-actions');
      
      actionsContainers.forEach(container => {
        if (!container) return;

        if (user && user.name) {
          const initials = this.getInitials(user.name);
          const firstName = user.name.split(' ')[0];

          // Check if this is the mobile drawer container
          if (container.classList.contains('mobile-drawer-actions')) {
            container.innerHTML = `
              <div style="padding: 10px 0; border-top: 1px solid rgba(85,155,255,0.2); margin-top: 8px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                  <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg, #258cff, #22e0c0); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px;">${initials}</div>
                  <div>
                    <div style="font-weight:700; color:#fff; font-size:0.95rem;">${escapeHtml(user.name)}</div>
                    <div style="font-size:0.75rem; color:#9eb5dc;">${escapeHtml(user.email)}</div>
                  </div>
                </div>
                <a class="btn btn-primary" href="dashboard.html" style="width:100%; justify-content:center; margin-bottom:8px; display:inline-flex; align-items:center; gap:8px;">
                  <span>Dashboard</span> →
                </a>
                <button type="button" class="btn" onclick="AuraAuth.logout()" style="width:100%; justify-content:center; background:rgba(239,68,68,0.15); border-color:rgba(239,68,68,0.4); color:#fca5a5;">
                  Sign Out
                </button>
              </div>
            `;
          } else {
            // Desktop Header Container
            container.innerHTML = `
              <div class="aura-user-menu" style="position:relative; display:inline-block;">
                <button type="button" class="btn btn-user-toggle" id="auraUserBtn" style="display:inline-flex; align-items:center; gap:9px; padding:7px 14px; background:rgba(14,46,109,0.7); border:1px solid rgba(85,155,255,0.4); border-radius:99px; cursor:pointer;">
                  <span style="width:26px; height:26px; border-radius:50%; background:linear-gradient(135deg, #258cff, #22e0c0); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:11px; box-shadow:0 0 10px rgba(37,140,255,0.4);">${initials}</span>
                  <span style="font-weight:600; color:#f4f8ff; font-size:0.9rem;">${escapeHtml(firstName)}</span>
                  <span style="font-size:10px; color:#9eb5dc; transition:transform 0.2s;" id="auraUserArrow">▼</span>
                </button>
                <div class="aura-dropdown" id="auraUserDropdown" style="display:none; position:absolute; right:0; top:calc(100% + 8px); width:230px; background:#07173b; border:1px solid rgba(85,155,255,0.3); border-radius:12px; box-shadow:0 12px 35px rgba(0,0,0,0.65), 0 0 20px rgba(37,140,255,0.2); padding:10px; z-index:99999;">
                  <div style="padding:8px 10px 10px; border-bottom:1px solid rgba(85,155,255,0.18);">
                    <div style="font-weight:700; color:#fff; font-size:0.92rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(user.name)}</div>
                    <div style="font-size:0.75rem; color:#9eb5dc; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(user.email)}</div>
                  </div>
                  <div style="padding:6px 0;">
                    <a href="dashboard.html" style="display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:8px; color:#d2e2fe; font-size:0.88rem; font-weight:600; text-decoration:none; transition:background 0.2s;" onmouseover="this.style.background='rgba(37,140,255,0.15)'" onmouseout="this.style.background='transparent'">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3aa0ff" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                      Dashboard
                    </a>
                  </div>
                  <div style="border-top:1px solid rgba(85,155,255,0.18); padding-top:6px;">
                    <button type="button" onclick="AuraAuth.logout()" style="width:100%; display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:8px; color:#fca5a5; font-size:0.88rem; font-weight:600; background:transparent; border:none; cursor:pointer; transition:background 0.2s; text-align:left;" onmouseover="this.style.background='rgba(239,68,68,0.15)'" onmouseout="this.style.background='transparent'">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fca5a5" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                      Sign Out (Logout)
                    </button>
                  </div>
                </div>
              </div>
            `;

            // Setup dropdown toggle
            const toggleBtn = container.querySelector('#auraUserBtn');
            const dropdown = container.querySelector('#auraUserDropdown');
            const arrow = container.querySelector('#auraUserArrow');
            if (toggleBtn && dropdown) {
              toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = dropdown.style.display === 'block';
                dropdown.style.display = isOpen ? 'none' : 'block';
                if (arrow) arrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
              });
              document.addEventListener('click', () => {
                dropdown.style.display = 'none';
                if (arrow) arrow.style.transform = 'rotate(0deg)';
              });
            }
          }
        }
      });
    },

    /**
     * Initializes user session on dashboard.html
     * Redirects to signin if not authenticated.
     */
    initDashboard: function() {
      const user = this.getUser();
      if (!user || !user.name) {
        // Not authenticated, redirect to signin
        window.location.href = 'signin.html';
        return;
      }

      // Populate user info dynamically
      const unameEl = document.getElementById('uname');
      if (unameEl) unameEl.textContent = user.name;

      const firstName = user.name.split(' ')[0];
      document.querySelectorAll('.un').forEach(el => {
        el.textContent = firstName;
      });

      const initials = this.getInitials(user.name);

      // Enhance user widget in dashboard top bar
      const userBox = document.querySelector('.user');
      if (userBox) {
        userBox.style.cursor = 'pointer';
        userBox.style.position = 'relative';
        
        // Replace avatar icon with user initials badge
        const av = userBox.querySelector('.av');
        if (av) {
          av.innerHTML = `<span style="font-size:12px; font-weight:800; color:#fff; display:flex; align-items:center; justify-content:center; width:100%; height:100%;">${initials}</span>`;
          av.style.background = 'linear-gradient(135deg, #1f6fe0, #22e0c0)';
        }

        // Add dropdown to dashboard user widget
        const existingDropdown = document.getElementById('dashUserDropdown');
        if (!existingDropdown) {
          const dropdown = document.createElement('div');
          dropdown.id = 'dashUserDropdown';
          dropdown.style.cssText = 'display:none; position:absolute; right:0; top:calc(100% + 10px); width:240px; background:#07173b; border:1px solid rgba(85,155,255,0.3); border-radius:12px; box-shadow:0 12px 35px rgba(0,0,0,0.7), 0 0 20px rgba(37,140,255,0.2); padding:10px; z-index:99999; text-align:left;';
          dropdown.innerHTML = `
            <div style="padding:8px 10px 10px; border-bottom:1px solid rgba(85,155,255,0.18);">
              <div style="font-weight:700; color:#fff; font-size:0.95rem;">${escapeHtml(user.name)}</div>
              <div style="font-size:0.75rem; color:#9eb5dc;">${escapeHtml(user.email)}</div>
            </div>
            <div style="padding:6px 0;">
              <a href="index.html" style="display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:8px; color:#d2e2fe; font-size:0.88rem; font-weight:600; text-decoration:none; transition:background 0.2s;" onmouseover="this.style.background='rgba(37,140,255,0.15)'" onmouseout="this.style.background='transparent'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3aa0ff" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                Return to Home
              </a>
            </div>
            <div style="border-top:1px solid rgba(85,155,255,0.18); padding-top:6px;">
              <button type="button" onclick="AuraAuth.logout()" style="width:100%; display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:8px; color:#fca5a5; font-size:0.88rem; font-weight:600; background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.3); cursor:pointer; transition:background 0.2s; text-align:left;" onmouseover="this.style.background='rgba(239,68,68,0.22)'" onmouseout="this.style.background='rgba(239,68,68,0.12)'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fca5a5" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                Sign Out (Logout)
              </button>
            </div>
          `;
          userBox.appendChild(dropdown);

          userBox.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = dropdown.style.display === 'block';
            dropdown.style.display = isOpen ? 'none' : 'block';
          });
          document.addEventListener('click', () => {
            dropdown.style.display = 'none';
          });
        }
      }

      // Add logout option to dashboard mobile drawer
      const mobileMenu = document.querySelector('.mobile-menu');
      if (mobileMenu && !document.getElementById('mobileLogoutBtn')) {
        const mLogout = document.createElement('button');
        mLogout.id = 'mobileLogoutBtn';
        mLogout.style.cssText = 'color:#fca5a5; border-color:rgba(239,68,68,0.3); background:rgba(239,68,68,0.1); margin-top:12px;';
        mLogout.innerHTML = `<span>⏻</span>Sign Out (${escapeHtml(firstName)})`;
        mLogout.onclick = () => AuraAuth.logout();
        mobileMenu.appendChild(mLogout);
      }
    }
  };

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Export to window
  window.AuraAuth = AuraAuth;

  // Run automatically on DOM content loaded
  document.addEventListener('DOMContentLoaded', () => {
    // If we're on dashboard.html
    if (window.location.pathname.includes('dashboard') || document.querySelector('.app aside.left')) {
      AuraAuth.initDashboard();
    } else {
      // Public pages (index, about, contact, signin, signup)
      AuraAuth.updatePublicHeader();
    }
  });

})(window);
