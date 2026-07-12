/* Keep It Green — SPA front-end
 *
 * File map (hash-router SPA, no build step; API calls live in api.js):
 *   theme/helpers  – applyTheme, toast, modal, esc, Cairo date formatting
 *   AUTH VIEWS     – loginView, registerView
 *   USER VIEWS     – dashboard, machines, transactions, rewards, redemptions
 *   ADMIN VIEWS    – dashboard, machines, transactions, vendors, promos
 *   router()       – maps #/routes to views (bottom of file)
 */
const app = document.getElementById('app');
const navEl = document.getElementById('nav');

/* ----------------------------- theme ------------------------------ */
function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('kig_theme', t);
    const m = document.querySelector('meta[name="theme-color"]');
    if (m) m.content = (t === 'dark') ? '#0a2018' : '#0C3B2A';
}
function toggleTheme() {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
}
(function () {                       // apply saved theme as early as possible
    const t = localStorage.getItem('kig_theme');
    if (t) document.documentElement.setAttribute('data-theme', t);
})();

/* ----------------------------- helpers ----------------------------- */
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
// All times shown in Cairo time (Africa/Cairo). Backend sends UTC (…Z).
const _CAIRO = 'Africa/Cairo';
const fmtDate = (s) => { try { return new Date(s).toLocaleString('en-GB', { timeZone: _CAIRO, day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }); } catch { return s; } };
const fmtDay = (s) => { try { return new Date(s).toLocaleDateString('en-GB', { timeZone: _CAIRO, day: 'numeric', month: 'short', year: 'numeric' }); } catch { return s; } };

function toast(msg, type = 'ok', title) {
    const root = document.getElementById('toast-root');
    const t = document.createElement('div');
    t.className = 'toast ' + (type === 'error' ? 'error' : '');
    t.innerHTML = (title ? `<div class="title">${esc(title)}</div>` : '') + esc(msg);
    root.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 200); }, 3600);
}

function openModal(title, bodyHtml, footHtml) {
    const root = document.getElementById('modal-root');
    root.innerHTML = `
      <div class="modal-overlay" data-overlay>
        <div class="modal">
          <div class="modal-head"><h3>${title}</h3><button class="x" data-close>&times;</button></div>
          <div class="modal-body">${bodyHtml}</div>
          ${footHtml ? `<div class="modal-foot">${footHtml}</div>` : ''}
        </div>
      </div>`;
    root.querySelector('[data-close]').onclick = closeModal;
    root.querySelector('[data-overlay]').onclick = (e) => { if (e.target.dataset.overlay !== undefined) closeModal(); };
    return root;
}
function closeModal() { document.getElementById('modal-root').innerHTML = ''; }

function emptyRow(cols, text) { return `<tr><td colspan="${cols}"><div class="empty">${esc(text)}</div></td></tr>`; }

/* ---------------- filter/sort bar (shared by all long lists) ----------------
 * Usage: html includes fsBar('key', ['All','X'], ['Newest','Oldest']);
 * after render call wireFs('key', renderRows); read state from _fs['key'].    */
const _fs = {};
function fsBar(key, filters, sorts) {
    const st = (_fs[key] ??= { f: (filters[0] || ''), s: (sorts[0] || '') });
    return `<div class="fsbar">
      ${filters.length > 1 ? `<div class="fs-chips">${filters.map(f =>
        `<button type="button" class="chip${st.f === f ? ' on' : ''}" data-fskey="${key}" data-f="${esc(f)}">${esc(f)}</button>`).join('')}</div>` : '<div class="fs-chips"></div>'}
      ${sorts.length ? `<select class="input fs-sort" data-fskey="${key}" title="Sort by">
        ${sorts.map(s => `<option${st.s === s ? ' selected' : ''}>${esc(s)}</option>`).join('')}</select>` : ''}
    </div>`;
}
function wireFs(key, rerender) {
    document.querySelectorAll(`[data-fskey="${key}"]`).forEach(el => {
        if (el.tagName === 'SELECT') el.onchange = () => { _fs[key].s = el.value; rerender(); };
        else el.onclick = () => {
            _fs[key].f = el.dataset.f;
            document.querySelectorAll(`.chip[data-fskey="${key}"]`).forEach(c => c.classList.toggle('on', c.dataset.f === _fs[key].f));
            rerender();
        };
    });
}

// Show/hide password fields rendered with [data-eye]
function wireEyes() {
    document.querySelectorAll('[data-eye]').forEach(b => b.onclick = () => {
        const i = b.previousElementSibling;
        if (i) { i.type = i.type === 'password' ? 'text' : 'password'; b.textContent = i.type === 'password' ? '👁' : '🙈'; }
    });
}

/* ------------------------------- nav ------------------------------- */
function renderNav() {
    const u = API.user();
    if (!u) { navEl.innerHTML = ''; return; }
    const links = u.isAdmin ? [
        ['#/admin', 'Dashboard'],
        ['#/admin/machines', 'Machines'],
        ['#/admin/transactions', 'Transactions'],
        ['#/admin/vendors', 'Vendors'],
        ['#/admin/promos', 'Promo Codes'],
    ] : [
        ['#/dashboard', 'Dashboard'],
        ['#/machines', 'Find a Machine'],
        ['#/transactions', 'My Items'],
        ['#/rewards', 'Rewards'],
        ['#/redemptions', 'My Redemptions'],
    ];
    const cur = location.hash || '#/';
    navEl.innerHTML = `
      <div class="navbar">
        <div class="brand"><img class="leaf" src="/img/logo-leaf-white.svg" alt="" /> Keep It Green</div>
        <nav class="nav-links" id="navLinks">
          ${links.map(([h, t]) => `<a href="${h}" class="${cur === h ? 'active' : ''}">${t}</a>`).join('')}
        </nav>
        <div class="nav-user">
          <button class="theme-btn" id="themeBtn" aria-label="Toggle dark mode" title="Toggle dark mode">🌗</button>
          <span class="pill">${esc(u.name)}<span class="role"> · ${u.isAdmin ? 'Admin' : 'User'}</span></span>
          <button class="btn btn-ghost btn-sm" id="logoutBtn" style="color:#cfe6d3;border-color:rgba(255,255,255,.25)">Logout</button>
        </div>
        <button class="nav-toggle" id="navToggle" aria-label="Toggle menu">☰</button>
      </div>`;
    document.getElementById('logoutBtn').onclick = () => API.logout();
    document.getElementById('themeBtn').onclick = toggleTheme;
    const navLinks = document.getElementById('navLinks');
    document.getElementById('navToggle').onclick = () => navLinks.classList.toggle('open');
    navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));
}

/* ============================ AUTH VIEWS ============================ */
function loginView() {
    navEl.innerHTML = '';
    app.innerHTML = `
      <div class="auth-wrap"><div class="auth-card">
        <div class="logo"><img src="/img/logo-app-icon.svg" alt="Keep It Green" width="66" height="66" /></div>
        <h1>Welcome back</h1>
        <p class="tagline">Sign in to your Keep It Green account</p>
        <form id="loginForm">
          <div class="form-row"><label>Email</label><input class="input" type="email" id="email" required placeholder="you@example.com"></div>
          <div class="form-row"><label>Password</label><div class="input-group"><input class="input" type="password" id="password" required placeholder="••••••••"><button type="button" class="toggle-eye" data-eye>👁</button></div></div>
          <button class="btn btn-primary btn-block" type="submit">Sign In</button>
        </form>
        <div class="auth-switch">No account? <a href="#/register">Create one</a></div>
      </div></div>`;
    document.getElementById('loginForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        btn.disabled = true; btn.textContent = 'Signing in…';
        try {
            const r = await API.login(email.value.trim(), password.value);
            API.setToken(r.Token);
            const u = API.user();
            toast('Signed in', 'ok', `Hi ${u.name}!`);
            location.hash = u.isAdmin ? '#/admin' : '#/dashboard';
        } catch (err) {
            toast(err.message, 'error', 'Login failed');
            btn.disabled = false; btn.textContent = 'Sign In';
        }
    };
}

function registerView() {
    navEl.innerHTML = '';
    app.innerHTML = `
      <div class="auth-wrap"><div class="auth-card">
        <div class="logo"><img src="/img/logo-app-icon.svg" alt="Keep It Green" width="66" height="66" /></div>
        <h1>Create account</h1>
        <p class="tagline">Start earning points for recycling</p>
        <form id="regForm">
          <div class="form-row"><label>Username</label><input class="input" id="userName" required placeholder="Your name"></div>
          <div class="form-row"><label>Email</label><input class="input" type="email" id="email" required placeholder="you@example.com"></div>
          <div class="form-row"><label>Password</label><div class="input-group"><input class="input" type="password" id="password" required placeholder="Min 6 chars · upper/lower/digit/symbol"><button type="button" class="toggle-eye" data-eye>👁</button></div></div>
          <button class="btn btn-primary btn-block" type="submit">Create Account</button>
        </form>
        <div class="auth-switch">Already have an account? <a href="#/login">Sign in</a></div>
      </div></div>`;
    document.getElementById('regForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        btn.disabled = true; btn.textContent = 'Creating…';
        try {
            await API.register(userName.value.trim(), email.value.trim(), password.value);
            toast('Account created — please sign in', 'ok');
            location.hash = '#/login';
        } catch (err) {
            toast(err.message, 'error', 'Registration failed');
            btn.disabled = false; btn.textContent = 'Create Account';
        }
    };
}

/* ============================ USER VIEWS ============================ */
async function userDashboard() {
    const u = API.user();
    const data = await API.coins().catch(() => ({ Coins: 0 }));
    app.innerHTML = `
      <h1 class="page-title">Hello, ${esc(u.name)} 👋</h1>
      <p class="page-sub">Recycle plastic & aluminum, earn points, redeem rewards.</p>
      <div class="grid cols-3">
        <div class="card stat coins spotlight"><span class="value"><span class="coin-ic" style="width:.62em;height:.62em"></span>${data.Coins ?? 0}</span><span class="label">Your Points</span></div>
        <a class="card action-card" href="#/machines"><div class="icon">📍</div><h3>Find a Machine</h3><div class="muted">Get an OTP to start recycling</div></a>
        <a class="card action-card" href="#/rewards"><div class="icon">🎁</div><h3>Browse Rewards</h3><div class="muted">Redeem points for promo codes</div></a>
      </div>
      <div class="grid cols-2 section-gap">
        <a class="card action-card" href="#/transactions"><div class="icon">📦</div><h3>My Recycled Items</h3><div class="muted">View your recycling history</div></a>
        <a class="card action-card" href="#/redemptions"><div class="icon">🧾</div><h3>My Redemptions</h3><div class="muted">Promo codes you've claimed</div></a>
      </div>`;
}

async function userMachines() {
    const machines = await API.machines();
    app.innerHTML = `
      <h1 class="page-title">Find a Machine</h1>
      <p class="page-sub">Pick a machine and generate an OTP — then enter it on the machine screen.</p>
      <div class="grid cols-3" id="mlist">
        ${machines.length ? machines.map(m => `
          <div class="card">
            <h3>${esc(m.Name)}</h3>
            <div class="muted">📍 ${esc(m.Location)}</div>
            <div style="margin:12px 0">${m.IsAvailable ? '<span class="badge badge-green">Available</span>' : '<span class="badge badge-red">Unavailable</span>'}</div>
            <button class="btn btn-primary btn-block otp-btn" data-id="${m.Id}" ${m.IsAvailable ? '' : 'disabled'}>Generate OTP</button>
          </div>`).join('') : '<div class="card"><div class="empty">No machines available yet.</div></div>'}
      </div>`;
    app.querySelectorAll('.otp-btn').forEach(b => b.onclick = async () => {
        b.disabled = true; b.textContent = 'Generating…';
        try {
            const r = await API.generateOtp(b.dataset.id);
            openModal('Your Session OTP', `
              <div class="otp-display">
                <p class="muted">Enter this code on the recycling machine to start your session:</p>
                <div class="otp-code">${esc(r.Otp)}</div>
                <p class="muted">Valid for 5 minutes.</p>
              </div>`, `<button class="btn btn-primary" data-close-ok>Done</button>`);
            document.querySelector('[data-close-ok]').onclick = closeModal;
        } catch (err) { toast(err.message, 'error'); }
        b.disabled = false; b.textContent = 'Generate OTP';
    });
}

async function userTransactions() {
    const tx = await API.myTransactions();
    app.innerHTML = `
      <h1 class="page-title">My Recycled Items</h1>
      <p class="page-sub">Every item you've recycled and the points you earned.</p>
      ${fsBar('utx', ['All', 'Plastic', 'Aluminum'], ['Newest', 'Oldest', 'Most points'])}
      <div class="table-wrap"><table>
        <thead><tr><th>Item</th><th>Points</th><th>Date</th></tr></thead>
        <tbody id="utxBody"></tbody>
      </table></div>`;
    const renderRows = () => {
        const { f, s } = _fs.utx;
        const rows = tx.filter(t => f === 'All' || t.ItemType === f)
            .sort((a, b) => s === 'Oldest' ? String(a.CreatedAt).localeCompare(String(b.CreatedAt))
                : s === 'Most points' ? (b.CoinsEarned || 0) - (a.CoinsEarned || 0)
                : String(b.CreatedAt).localeCompare(String(a.CreatedAt)));
        document.getElementById('utxBody').innerHTML = rows.length ? rows.map(t => `
          <tr>
            <td data-label="Item"><span class="badge ${t.ItemType === 'Plastic' ? 'badge-blue' : 'badge-amber'}">${esc(t.ItemType)}</span></td>
            <td data-label="Points"><span class="coin-ic"></span>${t.CoinsEarned}</td>
            <td data-label="Date">${fmtDate(t.CreatedAt)}</td>
          </tr>`).join('') : emptyRow(3, tx.length ? 'Nothing matches this filter.' : 'No items yet — recycle something to get started!');
    };
    wireFs('utx', renderRows); renderRows();
}

async function userRewards() {
    const [promos, coins] = await Promise.all([API.promos(), API.coins().catch(() => ({ Coins: 0 }))]);
    const bal = coins.Coins ?? 0;
    app.innerHTML = `
      <h1 class="page-title">Rewards</h1>
      <p class="page-sub">Redeem your points for promo codes from partner vendors.</p>
      <div class="hint">Your balance: <span class="coins-num"><span class="coin-ic"></span>${bal}</span> points</div>
      ${fsBar('urew', ['All', 'Affordable'], ['Lowest cost', 'Highest cost', 'Expiring soon'])}
      <div class="grid cols-3" id="urewGrid"></div>`;
    const renderCards = () => {
        const { f, s } = _fs.urew;
        const rows = promos.filter(p => f === 'All' || bal >= p.RequiredCoins)
            .sort((a, b) => s === 'Highest cost' ? b.RequiredCoins - a.RequiredCoins
                : s === 'Expiring soon' ? String(a.ExpirationDate).localeCompare(String(b.ExpirationDate))
                : a.RequiredCoins - b.RequiredCoins);
        document.getElementById('urewGrid').innerHTML = rows.length ? rows.map(p => {
            const can = bal >= p.RequiredCoins;
            return `<div class="card">
              <div style="display:flex;justify-content:space-between;align-items:start">
                <h3>${esc(p.VendorName)}</h3>
                <span class="badge badge-gray">${p.RemainingUsage} left</span>
              </div>
              <div class="muted">🔒 Redeem to reveal code</div>
              <div style="font-size:22px;font-weight:800;color:var(--gold);margin:10px 0"><span class="coin-ic"></span>${p.RequiredCoins}</div>
              <div class="muted" style="margin-bottom:12px">Expires ${fmtDay(p.ExpirationDate)}</div>
              <button class="btn ${can ? 'btn-gold' : 'btn-ghost'} btn-block redeem-btn" data-id="${p.Id}" data-coins="${p.RequiredCoins}" ${can ? '' : 'disabled'}>
                ${can ? 'Redeem' : 'Not enough points'}</button>
            </div>`;
        }).join('') : `<div class="card"><div class="empty">${promos.length ? 'No rewards match this filter.' : 'No rewards available right now.'}</div></div>`;
        wireRedeem();
    };
    const wireRedeem = () => app.querySelectorAll('.redeem-btn').forEach(b => b.onclick = () => {
        openModal('Confirm Redemption', `<p>Redeem this reward for <strong><span class="coin-ic"></span>${b.dataset.coins} points</strong>?</p>`,
            `<button class="btn btn-ghost" data-cancel>Cancel</button><button class="btn btn-gold" data-ok>Redeem</button>`);
        document.querySelector('[data-cancel]').onclick = closeModal;
        document.querySelector('[data-ok]').onclick = async () => {
            try {
                const r = await API.redeem(b.dataset.id);
                closeModal();
                openModal('🎉 Redeemed!', `
                  <div class="otp-display">
                    <p class="muted">Use this promo code at the vendor:</p>
                    <div class="otp-code" style="letter-spacing:3px;font-size:32px">${esc(r.PromoCode)}</div>
                    <p class="muted">Points remaining: <strong><span class="coin-ic"></span>${r.RemainingCoins}</strong></p>
                  </div>`, `<button class="btn btn-primary" data-close-ok>Done</button>`);
                document.querySelector('[data-close-ok]').onclick = () => { closeModal(); userRewards(); };
            } catch (err) { closeModal(); toast(err.message, 'error', 'Redemption failed'); }
        };
    });
    wireFs('urew', renderCards); renderCards();
}

async function userRedemptions() {
    const data = await API.myRedemptions();
    app.innerHTML = `
      <h1 class="page-title">My Redemptions</h1>
      <p class="page-sub">Promo codes you've claimed with your points.</p>
      ${fsBar('ured', [], ['Newest', 'Oldest', 'Most points'])}
      <div class="table-wrap"><table>
        <thead><tr><th>Promo Code</th><th>Points Spent</th><th>Date</th><th>Status</th></tr></thead>
        <tbody id="uredBody"></tbody>
      </table></div>`;
    const renderRows = () => {
        const { s } = _fs.ured;
        const rows = [...data].sort((a, b) => s === 'Oldest' ? String(a.RedemptionDate).localeCompare(String(b.RedemptionDate))
            : s === 'Most points' ? (b.CoinsDeducted || 0) - (a.CoinsDeducted || 0)
            : String(b.RedemptionDate).localeCompare(String(a.RedemptionDate)));
        document.getElementById('uredBody').innerHTML = rows.length ? rows.map(r => `
          <tr>
            <td data-label="Promo Code"><strong class="mono">${esc(r.PromoCode)}</strong></td>
            <td data-label="Points"><span class="coin-ic"></span>${r.CoinsDeducted}</td>
            <td data-label="Date">${fmtDate(r.RedemptionDate)}</td>
            <td data-label="Status"><span class="badge badge-green">${esc(r.Status)}</span></td>
          </tr>`).join('') : emptyRow(4, 'No redemptions yet.');
    };
    wireFs('ured', renderRows); renderRows();
}

/* =========================== ADMIN VIEWS =========================== */
async function adminDashboard() {
    const [machines, vendors, promos] = await Promise.all([
        API.machines().catch(() => []), API.vendors().catch(() => []), API.promos().catch(() => [])]);
    app.innerHTML = `
      <h1 class="page-title">Admin Dashboard</h1>
      <p class="page-sub">Manage machines, monitor recycling, and run the rewards program.</p>
      <div class="grid cols-3">
        <div class="card stat"><span class="value">${machines.length}</span><span class="label">Machines</span></div>
        <div class="card stat"><span class="value">${vendors.length}</span><span class="label">Vendors</span></div>
        <div class="card stat"><span class="value">${promos.length}</span><span class="label">Active Promo Codes</span></div>
      </div>
      <div class="grid cols-2 section-gap">
        <a class="card action-card" href="#/admin/machines"><div class="icon">🗄️</div><h3>Manage Machines</h3><div class="muted">Add, toggle, remove machines</div></a>
        <a class="card action-card" href="#/admin/transactions"><div class="icon">🔍</div><h3>Monitor Transactions</h3><div class="muted">AI detections, confidence & images</div></a>
        <a class="card action-card" href="#/admin/vendors"><div class="icon">🏪</div><h3>Vendors</h3><div class="muted">Manage partner vendors</div></a>
        <a class="card action-card" href="#/admin/promos"><div class="icon">🎟️</div><h3>Promo Codes</h3><div class="muted">Create reward promo codes</div></a>
      </div>`;
}

async function adminMachines() {
    const machines = await API.machines();
    app.innerHTML = `
      <div class="toolbar">
        <div><h1 class="page-title" style="margin:0">Machines</h1></div>
        <div class="spacer"></div>
        <button class="btn btn-primary" id="addMachine">+ Add Machine</button>
      </div>
      ${fsBar('am', ['All', 'Available', 'Unavailable'], ['Name', 'Location', 'Newest'])}
      <div class="table-wrap"><table>
        <thead><tr><th>ID</th><th>Name</th><th>Location</th><th>Status</th><th style="text-align:right">Actions</th></tr></thead>
        <tbody id="amBody"></tbody>
      </table></div>`;
    const renderRows = () => {
        const { f, s } = _fs.am;
        const rows = machines.filter(m => f === 'All' || (f === 'Available') === !!m.IsAvailable)
            .sort((a, b) => s === 'Location' ? String(a.Location).localeCompare(String(b.Location))
                : s === 'Newest' ? b.Id - a.Id
                : String(a.Name).localeCompare(String(b.Name)));
        document.getElementById('amBody').innerHTML = rows.length ? rows.map(m => `
          <tr>
            <td data-label="ID">${m.Id}</td>
            <td data-label="Name">${esc(m.Name)}</td>
            <td data-label="Location">${esc(m.Location)}</td>
            <td data-label="Status">${m.IsAvailable ? '<span class="badge badge-green">Available</span>' : '<span class="badge badge-red">Unavailable</span>'}</td>
            <td data-label="Actions" style="text-align:right">
              <button class="btn btn-ghost btn-sm toggle" data-id="${m.Id}" data-av="${m.IsAvailable}">${m.IsAvailable ? 'Disable' : 'Enable'}</button>
              <button class="btn btn-danger btn-sm del" data-id="${m.Id}" data-name="${esc(m.Name)}">Delete</button>
            </td>
          </tr>`).join('') : emptyRow(5, machines.length ? 'No machines match this filter.' : 'No machines yet.');
        wireActions();
    };

    document.getElementById('addMachine').onclick = () => {
        openModal('Add Machine', `
          <div class="form-row"><label>Name</label><input class="input" id="mName" placeholder="Machine-01"></div>
          <div class="form-row"><label>Location</label><input class="input" id="mLoc" placeholder="Cairo - Mall"></div>
          <div class="form-row"><label><input type="checkbox" id="mAvail" checked> Available</label></div>`,
            `<button class="btn btn-ghost" data-cancel>Cancel</button><button class="btn btn-primary" data-ok>Add</button>`);
        document.querySelector('[data-cancel]').onclick = closeModal;
        document.querySelector('[data-ok]').onclick = async () => {
            try {
                await API.addMachine({ Name: mName.value.trim(), Location: mLoc.value.trim(), IsAvailable: mAvail.checked });
                closeModal(); toast('Machine added'); adminMachines();
            } catch (err) { toast(err.message, 'error'); }
        };
    };
    const wireActions = () => {
        app.querySelectorAll('.toggle').forEach(b => b.onclick = async () => {
            try { await API.updateMachine(b.dataset.id, b.dataset.av !== 'true'); toast('Updated'); adminMachines(); }
            catch (err) { toast(err.message, 'error'); }
        });
        app.querySelectorAll('.del').forEach(b => b.onclick = () => {
            openModal('Delete Machine', `<p>Delete <strong>${esc(b.dataset.name)}</strong>? This cannot be undone.</p>`,
                `<button class="btn btn-ghost" data-cancel>Cancel</button><button class="btn btn-danger" data-ok>Delete</button>`);
            document.querySelector('[data-cancel]').onclick = closeModal;
            document.querySelector('[data-ok]').onclick = async () => {
                try { await API.deleteMachine(b.dataset.id); closeModal(); toast('Machine deleted'); adminMachines(); }
                catch (err) { closeModal(); toast(err.message, 'error'); }
            };
        });
    };
    wireFs('am', renderRows); renderRows();
}

async function adminTransactions() {
    const machines = await API.machines();
    app.innerHTML = `
      <h1 class="page-title">Monitor Transactions</h1>
      <p class="page-sub">AI detections per machine — includes confidence score & capture path (continuous-learning data).</p>
      <div class="toolbar">
        <label style="font-weight:600">Machine:</label>
        <select class="input" id="mSel" style="max-width:280px">
          ${machines.map(m => `<option value="${m.Id}">${esc(m.Name)} — ${esc(m.Location)}</option>`).join('')}
        </select>
      </div>
      <div id="txArea"><div class="loader"></div></div>`;
    const sel = document.getElementById('mSel');
    let txRows = [];
    const renderRows = () => {
        const body = document.getElementById('atxBody');
        if (!body) return;
        const { f, s } = _fs.atx;
        const rows = txRows.filter(r => f === 'All' || r.ItemType === f)
            .sort((a, b) => s === 'Oldest' ? String(a.CreatedAt).localeCompare(String(b.CreatedAt))
                : s === 'Most points' ? (b.CoinsEarned || 0) - (a.CoinsEarned || 0)
                : s === 'Confidence' ? (b.ConfidenceScore || 0) - (a.ConfidenceScore || 0)
                : String(b.CreatedAt).localeCompare(String(a.CreatedAt)));
        body.innerHTML = rows.length ? rows.map(r => `
          <tr>
            <td data-label="User">${esc(r.UserName)}<div class="muted" style="font-size:12px">${esc(r.Email)}</div></td>
            <td data-label="Item"><span class="badge ${r.ItemType === 'Plastic' ? 'badge-blue' : 'badge-amber'}">${esc(r.ItemType)}</span></td>
            <td data-label="Points"><span class="coin-ic"></span>${r.CoinsEarned}</td>
            <td data-label="Confidence">${r.ConfidenceScore != null ? (r.ConfidenceScore * 100).toFixed(0) + '%' : '<span class="muted">—</span>'}</td>
            <td data-label="Image" style="font-size:12px;color:var(--muted);max-width:220px;overflow:hidden;text-overflow:ellipsis" class="mono">${r.ImagePath ? esc(r.ImagePath) : '—'}</td>
            <td data-label="Date">${fmtDate(r.CreatedAt)}</td>
          </tr>`).join('') : emptyRow(6, txRows.length ? 'Nothing matches this filter.' : 'No transactions for this machine.');
    };
    const load = async () => {
        const area = document.getElementById('txArea');
        area.innerHTML = '<div class="loader"></div>';
        try {
            txRows = await API.adminTransactions(sel.value);
            area.innerHTML = `
              ${fsBar('atx', ['All', 'Plastic', 'Aluminum'], ['Newest', 'Oldest', 'Most points', 'Confidence'])}
              <div class="table-wrap"><table>
                <thead><tr><th>User</th><th>Item</th><th>Points</th><th>Confidence</th><th>Image</th><th>Date</th></tr></thead>
                <tbody id="atxBody"></tbody>
              </table></div>`;
            wireFs('atx', renderRows); renderRows();
        } catch (err) { area.innerHTML = `<div class="card"><div class="empty">${esc(err.message)}</div></div>`; }
    };
    sel.onchange = load;
    if (machines.length) load(); else document.getElementById('txArea').innerHTML = '<div class="card"><div class="empty">Add a machine first.</div></div>';
}

async function adminVendors() {
    const vendors = await API.vendors();
    app.innerHTML = `
      <div class="toolbar">
        <h1 class="page-title" style="margin:0">Vendors</h1>
        <div class="spacer"></div>
        <button class="btn btn-primary" id="addVendor">+ Add Vendor</button>
      </div>
      ${fsBar('av', ['All', 'Active', 'Inactive'], ['Name', 'Newest'])}
      <div class="table-wrap"><table>
        <thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Email</th><th>Status</th></tr></thead>
        <tbody id="avBody"></tbody>
      </table></div>`;
    const renderRows = () => {
        const { f, s } = _fs.av;
        const rows = vendors.filter(v => f === 'All' || (f === 'Active') === !!v.IsActive)
            .sort((a, b) => s === 'Newest' ? b.Id - a.Id : String(a.Name).localeCompare(String(b.Name)));
        document.getElementById('avBody').innerHTML = rows.length ? rows.map(v => `
          <tr>
            <td data-label="ID">${v.Id}</td><td data-label="Name">${esc(v.Name)}</td><td data-label="Description">${esc(v.Description || '—')}</td><td data-label="Email">${esc(v.Email)}</td>
            <td data-label="Status">${v.IsActive ? '<span class="badge badge-green">Active</span>' : '<span class="badge badge-gray">Inactive</span>'}</td>
          </tr>`).join('') : emptyRow(5, vendors.length ? 'No vendors match this filter.' : 'No vendors yet.');
    };
    wireFs('av', renderRows); renderRows();
    document.getElementById('addVendor').onclick = () => {
        openModal('Add Vendor', `
          <div class="form-row"><label>Name</label><input class="input" id="vName" placeholder="GreenCafe"></div>
          <div class="form-row"><label>Description</label><input class="input" id="vDesc" placeholder="Coffee discounts"></div>
          <div class="form-row"><label>Email</label><input class="input" type="email" id="vEmail" placeholder="promo@vendor.com"></div>`,
            `<button class="btn btn-ghost" data-cancel>Cancel</button><button class="btn btn-primary" data-ok>Add</button>`);
        document.querySelector('[data-cancel]').onclick = closeModal;
        document.querySelector('[data-ok]').onclick = async () => {
            try {
                await API.addVendor({ Name: vName.value.trim(), Description: vDesc.value.trim(), Email: vEmail.value.trim() });
                closeModal(); toast('Vendor added'); adminVendors();
            } catch (err) { toast(err.message, 'error'); }
        };
    };
}

async function adminPromos() {
    const [promos, vendors] = await Promise.all([API.promos(), API.vendors()]);
    app.innerHTML = `
      <div class="toolbar">
        <h1 class="page-title" style="margin:0">Promo Codes</h1>
        <div class="spacer"></div>
        <button class="btn btn-primary" id="addPromo" ${vendors.length ? '' : 'disabled title="Add a vendor first"'}>+ Add Promo</button>
      </div>
      ${vendors.length ? '' : '<div class="hint">Add a vendor before creating promo codes.</div>'}
      ${fsBar('ap', ['All', 'In stock', 'Sold out'], ['Lowest cost', 'Highest cost', 'Expiring soon', 'Remaining'])}
      <div class="table-wrap"><table>
        <thead><tr><th>ID</th><th>Vendor</th><th>Code</th><th>Cost</th><th>Remaining</th><th>Expires</th></tr></thead>
        <tbody id="apBody"></tbody>
      </table></div>`;
    const renderRows = () => {
        const { f, s } = _fs.ap;
        const rows = promos.filter(p => f === 'All' || (f === 'In stock') === (p.RemainingUsage > 0))
            .sort((a, b) => s === 'Highest cost' ? b.RequiredCoins - a.RequiredCoins
                : s === 'Expiring soon' ? String(a.ExpirationDate).localeCompare(String(b.ExpirationDate))
                : s === 'Remaining' ? b.RemainingUsage - a.RemainingUsage
                : a.RequiredCoins - b.RequiredCoins);
        document.getElementById('apBody').innerHTML = rows.length ? rows.map(p => `
          <tr>
            <td data-label="ID">${p.Id}</td><td data-label="Vendor">${esc(p.VendorName)}</td><td data-label="Code"><strong class="mono">${esc(p.Code)}</strong></td>
            <td data-label="Cost"><span class="coin-ic"></span>${p.RequiredCoins}</td><td data-label="Remaining">${p.RemainingUsage}</td><td data-label="Expires">${fmtDay(p.ExpirationDate)}</td>
          </tr>`).join('') : emptyRow(6, promos.length ? 'No promo codes match this filter.' : 'No promo codes yet.');
    };
    wireFs('ap', renderRows); renderRows();
    const addBtn = document.getElementById('addPromo');
    if (addBtn && vendors.length) addBtn.onclick = () => {
        openModal('Add Promo Code', `
          <div class="form-row"><label>Vendor</label><select class="input" id="pVendor">${vendors.map(v => `<option value="${v.Id}">${esc(v.Name)}</option>`).join('')}</select></div>
          <div class="form-row"><label>Code</label><input class="input" id="pCode" placeholder="GREEN20"></div>
          <div class="form-row"><label>Required Coins</label><input class="input" type="number" id="pCoins" value="20" min="1"></div>
          <div class="form-row"><label>Usage Limit</label><input class="input" type="number" id="pLimit" value="10" min="1"></div>
          <div class="form-row"><label>Expiration Date</label><input class="input" type="date" id="pExp"></div>`,
            `<button class="btn btn-ghost" data-cancel>Cancel</button><button class="btn btn-primary" data-ok>Create</button>`);
        document.querySelector('[data-cancel]').onclick = closeModal;
        document.querySelector('[data-ok]').onclick = async () => {
            try {
                const exp = pExp.value ? new Date(pExp.value).toISOString() : new Date(Date.now() + 30 * 864e5).toISOString();
                await API.addPromo({
                    VendorId: parseInt(pVendor.value), Code: pCode.value.trim(),
                    RequiredCoins: parseInt(pCoins.value), UsageLimit: parseInt(pLimit.value), ExpirationDate: exp
                });
                closeModal(); toast('Promo code created'); adminPromos();
            } catch (err) { toast(err.message, 'error'); }
        };
    };
}

/* ----------------------------- router ----------------------------- */
const routes = {
    '#/login': { fn: loginView, public: true },
    '#/register': { fn: registerView, public: true },
    '#/dashboard': { fn: userDashboard },
    '#/machines': { fn: userMachines },
    '#/transactions': { fn: userTransactions },
    '#/rewards': { fn: userRewards },
    '#/redemptions': { fn: userRedemptions },
    '#/admin': { fn: adminDashboard, admin: true },
    '#/admin/machines': { fn: adminMachines, admin: true },
    '#/admin/transactions': { fn: adminTransactions, admin: true },
    '#/admin/vendors': { fn: adminVendors, admin: true },
    '#/admin/promos': { fn: adminPromos, admin: true },
};

async function router() {
    const u = API.user();
    let hash = location.hash || '#/';
    let route = routes[hash];

    // default landing
    if (hash === '#/' || !route) {
        if (!u) { location.hash = '#/login'; return; }
        location.hash = u.isAdmin ? '#/admin' : '#/dashboard'; return;
    }
    // auth guard
    if (!route.public && !u) { location.hash = '#/login'; return; }
    // admin guard
    if (route.admin && (!u || !u.isAdmin)) { location.hash = '#/dashboard'; return; }
    // already logged in → keep out of auth pages
    if (route.public && u) { location.hash = u.isAdmin ? '#/admin' : '#/dashboard'; return; }

    renderNav();
    app.innerHTML = '<div class="loader"></div>';
    try {
        await route.fn();
    } catch (err) {
        app.innerHTML = `<div class="card"><h3>Something went wrong</h3><p class="muted">${esc(err.message)}</p></div>`;
        toast(err.message, 'error');
    }
    wireEyes();
    window.scrollTo(0, 0);
}

window.addEventListener('hashchange', router);
window.addEventListener('load', router);
