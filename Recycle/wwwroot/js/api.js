/* Keep It Green — API client + auth helpers */
const API = {
    base: '',
    _key: 'kig_token',

    token() { return localStorage.getItem(this._key); },
    setToken(t) { t ? localStorage.setItem(this._key, t) : localStorage.removeItem(this._key); },
    logout() { this.setToken(null); location.hash = '#/login'; },

    decode() {
        const t = this.token();
        if (!t) return null;
        try {
            const part = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(decodeURIComponent(escape(atob(part))));
        } catch { return null; }
    },

    user() {
        const p = this.decode();
        if (!p) return null;
        if (p.exp && Date.now() / 1000 > p.exp) { return null; }   // expired
        const roleKeys = ['role', 'roles',
            'http://schemas.microsoft.com/ws/2008/06/identity/claims/role'];
        let roles = [];
        for (const k of roleKeys) { if (p[k] != null) { roles = Array.isArray(p[k]) ? p[k] : [p[k]]; break; } }
        const nameKeys = ['unique_name', 'name',
            'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name'];
        let name = 'User';
        for (const k of nameKeys) { if (p[k]) { name = p[k]; break; } }
        return { name, roles, isAdmin: roles.includes('Admin') };
    },

    async req(method, path, opts = {}) {
        const { body, auth = true } = opts;
        const headers = { 'Content-Type': 'application/json' };
        if (auth && this.token()) headers['Authorization'] = 'Bearer ' + this.token();
        let res;
        try {
            res = await fetch(this.base + path, {
                method, headers, body: body ? JSON.stringify(body) : undefined
            });
        } catch (e) {
            throw new Error('Cannot reach the server. Is the backend running?');
        }
        if (res.status === 401 && auth) { this.setToken(null); location.hash = '#/login'; }
        const txt = await res.text();
        let data = null;
        try { data = txt ? JSON.parse(txt) : null; } catch { data = txt; }
        if (!res.ok) {
            let msg = (data && (data.Message || data.title)) || res.statusText;
            if (Array.isArray(data)) msg = data.map(e => e.description || e.Description || e).join(' ');
            throw new Error(typeof msg === 'string' ? msg : 'Request failed');
        }
        return data;
    },

    // ---- auth ----
    login(email, password) { return this.req('POST', '/api/User/Login', { auth: false, body: { Email: email, Password: password } }); },
    register(userName, email, password) { return this.req('POST', '/api/User/Register', { auth: false, body: { UserName: userName, Email: email, Password: password } }); },

    // ---- user ----
    coins() { return this.req('GET', '/api/User/Coins'); },
    machines() { return this.req('GET', '/api/Machine'); },
    generateOtp(id) { return this.req('GET', '/api/Otp/Generate/' + id); },
    myTransactions() { return this.req('GET', '/api/Transaction/User'); },
    vendors() { return this.req('GET', '/api/Vendor'); },
    promos() { return this.req('GET', '/api/Promo'); },
    redeem(promoId) { return this.req('POST', '/api/Redemption/' + promoId); },
    myRedemptions() { return this.req('GET', '/api/Redemption/My'); },

    // ---- admin ----
    addMachine(m) { return this.req('POST', '/api/Machine', { body: m }); },
    updateMachine(id, isAvailable) { return this.req('PUT', '/api/Machine/' + id, { body: { IsAvailable: isAvailable } }); },
    deleteMachine(id) { return this.req('DELETE', '/api/Machine/' + id); },
    adminTransactions(machineId) { return this.req('GET', '/api/Transaction/Admin/' + machineId); },
    addVendor(v) { return this.req('POST', '/api/Vendor', { body: v }); },
    addPromo(p) { return this.req('POST', '/api/Promo', { body: p }); },
};
