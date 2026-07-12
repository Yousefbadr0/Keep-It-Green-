/* Keep It Green — kiosk screen logic.
   Driven by the machine program (pywebview) via window.kioskApply().
   Open /kiosk/?demo in a browser to preview the flow. */

const MACHINE = { location: '—' };
const $ = (id) => document.getElementById(id);
let _choiceTimer = null;

function countUp(el, to, dur = 800) {
    const from = parseInt(el.textContent, 10) || 0;
    to = Math.round(to || 0);
    if (from === to) { el.textContent = to; return; }
    const start = performance.now();
    (function tick(now) {
        const t = Math.min(1, (now - start) / dur);
        const e = 1 - Math.pow(1 - t, 3);
        el.textContent = Math.round(from + (to - from) * e);
        if (t < 1) requestAnimationFrame(tick);
    })(start);
}

function apply(msg) {
    if (msg.state !== 'choice' && _choiceTimer) { clearInterval(_choiceTimer); _choiceTimer = null; }
    switch (msg.state) {
        case 'idle':
            document.body.dataset.state = 'idle';
            if (msg.location) $('stationName').textContent = msg.location;
            $('pairCode').textContent = (msg.code && /^\d+$/.test(msg.code)) ? msg.code : '——————';
            if (msg.qr) { $('qrImg').src = msg.qr; $('qrImg').hidden = false; $('qrPlaceholder').hidden = true; }
            else { $('qrImg').hidden = true; $('qrPlaceholder').hidden = false; }
            kp.buf = ''; kpRender();
            const e0 = $('kpError'); if (e0) e0.textContent = '';
            break;
        case 'connected':
            document.body.dataset.state = 'connected';
            $('userName').textContent = msg.userName || '—';
            countUp($('sessionPts'), msg.sessionPts || 0);
            { const cf = $('camFeed'); if (cf) cf.hidden = true; const cs = $('camStripes'); if (cs) cs.hidden = false; }
            break;
        case 'detected':
            document.body.dataset.state = 'detected';
            $('detItem').textContent = msg.item || '';
            $('detConf').textContent = Math.round(msg.confidence || 0);
            $('detPts').textContent = msg.points || 0;
            break;
        case 'drop': {
            document.body.dataset.state = 'drop';
            const isPlastic = String(msg.item || '').toLowerCase().includes('plastic');
            $('binPlastic').classList.toggle('open', isPlastic);
            $('binAluminum').classList.toggle('open', !isPlastic);
            $('binPlastic').querySelector('.st').textContent = isPlastic ? 'OPEN' : 'closed';
            $('binAluminum').querySelector('.st').textContent = isPlastic ? 'closed' : 'OPEN';
            $('servoLabel').textContent = isPlastic ? 'plastic' : 'aluminum';
            break;
        }
        case 'choice':
            document.body.dataset.state = 'choice';
            $('choiceItem').textContent = msg.item || '';
            $('choicePts').textContent = msg.points || 0;
            startChoiceTimer(msg.seconds || 12);
            break;
        case 'summary':
            document.body.dataset.state = 'summary';
            $('sumName').textContent = msg.userName || 'there';
            $('sumItems').textContent = msg.items || 0;
            countUp($('sumPts'), msg.points || 0);
            {
                const w = $('sumTotalWrap');
                if (msg.total != null) { $('sumTotal').textContent = '0'; countUp($('sumTotal'), msg.total); if (w) w.hidden = false; }
                else if (w) w.hidden = true;
            }
            break;
    }
}

/* ---- "add another / finish" choice ---- */
function chooseAction(what) {
    if (_choiceTimer) { clearInterval(_choiceTimer); _choiceTimer = null; }
    if (window.pywebview && window.pywebview.api && window.pywebview.api.choose) {
        window.pywebview.api.choose(what);
    }
}
function startChoiceTimer(seconds) {
    if (_choiceTimer) clearInterval(_choiceTimer);
    let s = seconds;
    const el = $('choiceTimer'); if (el) el.textContent = s;
    _choiceTimer = setInterval(() => {
        s -= 1;
        if (el) el.textContent = Math.max(0, s);
        if (s <= 0) { clearInterval(_choiceTimer); _choiceTimer = null; chooseAction('finish'); }
    }, 1000);
}
function setupChoice() {
    const a = $('btnAnother'); if (a) a.onclick = () => chooseAction('another');
    const f = $('btnFinish'); if (f) f.onclick = () => chooseAction('finish');
}
window.kioskApply = apply;

// the machine program pushes live camera frames here (data:image/jpeg;base64,…)
window.kioskFrame = (uri) => {
    const i = $('camFeed');
    if (i) { i.src = uri; i.hidden = false; const s = $('camStripes'); if (s) s.hidden = true; }
};

/* ---- on-screen keypad: enter a code generated in the app ---- */
const kp = { buf: '' };
function kpRender() {
    const d = $('kpDisplay');
    if (d) d.textContent = (kp.buf + '••••••').slice(0, 6).split('').join(' ');
}
function setupKeypad() {
    document.querySelectorAll('.kp').forEach(b => b.onclick = () => {
        const k = b.dataset.k;
        if (k === 'del') kp.buf = kp.buf.slice(0, -1);
        else if (k === 'ok') { if (kp.buf.length >= 4) submitCode(kp.buf); }
        else if (kp.buf.length < 6) kp.buf += b.textContent.trim();
        kpRender();
    });
    kpRender();
}
function submitCode(code) {
    const err = $('kpError');
    if (window.pywebview && window.pywebview.api && window.pywebview.api.submit_code) {
        if (err) err.textContent = 'Checking…';
        window.pywebview.api.submit_code(code);
    } else if (err) {
        err.textContent = 'Code entry works on the machine.';
    }
}
// the machine program calls this if a typed code is invalid
window.kioskError = (msg) => { const e = $('kpError'); if (e) e.textContent = msg || ''; kp.buf = ''; kpRender(); };

/* ---- demo cycle (browser preview only) — mirrors the real machine loop ---- */
function runDemo() {
    const seq = [
        { state: 'idle', code: '703647', location: 'Riverside Park' },
        { state: 'connected', userName: 'Lina', sessionPts: 0 },
        { state: 'detected', item: 'Plastic bottle', confidence: 96, points: 10 },
        { state: 'drop', item: 'Plastic' },
        { state: 'choice', item: 'Plastic bottle', points: 10, seconds: 12 },
        { state: 'connected', userName: 'Lina', sessionPts: 10 },
        { state: 'detected', item: 'Aluminum can', confidence: 88, points: 15 },
        { state: 'drop', item: 'Aluminum' },
        { state: 'choice', item: 'Aluminum can', points: 15, seconds: 12 },
        { state: 'summary', userName: 'Lina', items: 2, points: 25, total: 140 },
    ];
    let i = 0; apply(seq[0]);
    setInterval(() => { i = (i + 1) % seq.length; apply(seq[i]); }, 2600);
}

setupKeypad();
setupChoice();
if (new URLSearchParams(location.search).has('demo')) {
    runDemo();
} else {
    apply({ state: 'idle', code: '——————', location: MACHINE.location });
}
