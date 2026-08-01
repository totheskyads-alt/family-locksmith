/* Family Locksmith — cookie banner + Google Consent Mode v2
   Starea implicita (toate refuzate) se seteaza inline in <head>, INAINTE de GTM.
   Fisierul asta doar deseneaza bannerul si trimite update-ul cand userul alege. */
(function () {
  'use strict';

  var STORE = 'fl_consent';
  var VERSION = 1;            // creste-l daca se schimba categoriile: cere consimtamant din nou
  var MAX_AGE_DAYS = 182;     // ~6 luni, apoi reintrebam

  var CATS = [
    { id: 'necessary', label: 'Strictly necessary', locked: true,
      desc: 'Needed for the site to work, such as remembering this cookie choice. These cannot be switched off.' },
    { id: 'analytics', label: 'Statistics',
      desc: 'Help us understand which pages people use, so we can improve the site. Nothing here identifies you personally.' },
    { id: 'marketing', label: 'Marketing',
      desc: 'Used to measure our adverts and show relevant ones. Switched off unless you allow them.' }
  ];

  function signalsFor(p) {
    return {
      ad_storage:          p.marketing ? 'granted' : 'denied',
      ad_user_data:        p.marketing ? 'granted' : 'denied',
      ad_personalization:  p.marketing ? 'granted' : 'denied',
      analytics_storage:   p.analytics ? 'granted' : 'denied',
      functionality_storage: 'granted',
      security_storage:      'granted'
    };
  }

  function read() {
    try {
      var raw = localStorage.getItem(STORE);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (v.version !== VERSION) return null;
      if (Date.now() - v.at > MAX_AGE_DAYS * 864e5) return null;
      return v;
    } catch (e) { return null; }
  }

  function save(prefs) {
    var payload = { version: VERSION, at: Date.now(), prefs: prefs, signals: signalsFor(prefs) };
    try { localStorage.setItem(STORE, JSON.stringify(payload)); } catch (e) {}
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag === 'function') window.gtag('consent', 'update', payload.signals);
    window.dataLayer.push({
      event: 'consent_update',
      consent_analytics: prefs.analytics ? 'granted' : 'denied',
      consent_marketing: prefs.marketing ? 'granted' : 'denied'
    });
  }

  /* ---------- stiluri, injectate ca sa nu atingem styles.css ---------- */
  var CSS = ''
    + '.flc-backdrop{position:fixed;inset:0;background:rgba(18,19,25,.55);z-index:2147483000;display:none}'
    + '.flc-backdrop.is-open{display:block}'
    + '.flc{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483001;background:#fff;color:#121319;'
    + 'border:1px solid #DCDEE4;border-radius:18px;box-shadow:0 18px 50px rgba(18,19,25,.22);'
    + 'padding:20px;max-width:560px;margin:0 auto;font-family:inherit;display:none}'
    + '.flc.is-open{display:block}'
    + '.flc h2{font-size:18px;line-height:1.3;margin:0 0 8px;font-weight:800;color:#121319}'
    + '.flc p{font-size:14.5px;line-height:1.55;margin:0 0 14px;color:#3C3F47}'
    + '.flc a{color:#B4770A;text-decoration:underline}'
    + '.flc-row{display:flex;gap:10px;flex-wrap:wrap}'
    + '.flc-btn{flex:1 1 160px;min-height:46px;padding:12px 16px;border-radius:999px;border:1px solid transparent;'
    + 'font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;line-height:1.2}'
    + '.flc-btn:focus-visible{outline:3px solid #B4770A;outline-offset:2px}'
    + '.flc-accept{background:#F5A524;color:#3E2803}'
    + '.flc-accept:hover{background:#EA9310}'
    + '.flc-reject{background:#F6F7F9;color:#121319;border-color:#DCDEE4}'
    + '.flc-reject:hover{background:#EEF0F3}'
    + '.flc-link{background:none;border:none;color:#65676E;text-decoration:underline;cursor:pointer;'
    + 'font-size:14px;padding:10px 4px;min-height:44px;font-family:inherit}'
    + '.flc-link:focus-visible{outline:3px solid #B4770A;outline-offset:2px}'
    + '.flc-cats{margin:4px 0 16px;border-top:1px solid #EAEBEE}'
    + '.flc-cat{border-bottom:1px solid #EAEBEE;padding:12px 0;display:flex;gap:12px;align-items:flex-start}'
    + '.flc-cat label{font-weight:700;font-size:14.5px;display:block;margin-bottom:2px;color:#121319}'
    + '.flc-cat p{font-size:13.5px;margin:0;color:#65676E}'
    + '.flc-cat input{width:22px;height:22px;margin-top:2px;accent-color:#F5A524;flex:none}'
    + '.flc-cat input:disabled{opacity:.55}'
    + '.flc-reopen{position:fixed;left:16px;bottom:16px;z-index:2147482000;width:44px;height:44px;border-radius:50%;'
    + 'background:#fff;border:1px solid #DCDEE4;box-shadow:0 6px 18px rgba(18,19,25,.16);cursor:pointer;'
    + 'display:none;align-items:center;justify-content:center;padding:0}'
    + '.flc-reopen.is-on{display:flex}'
    + '.flc-reopen:focus-visible{outline:3px solid #B4770A;outline-offset:2px}'
    + '@media(min-width:640px){.flc{padding:24px}}'
    + '@media(prefers-reduced-motion:no-preference){.flc.is-open{animation:flcIn .22s ease-out}'
    + '@keyframes flcIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}}';

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  var backdrop, panel, reopenBtn, lastFocus;

  function build() {
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    backdrop = el('div', 'flc-backdrop');
    backdrop.addEventListener('click', function () { closePanel(); });

    panel = el('div', 'flc');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'false');
    panel.setAttribute('aria-labelledby', 'flc-title');
    panel.setAttribute('aria-describedby', 'flc-desc');

    reopenBtn = el('button', 'flc-reopen',
      '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#65676E" stroke-width="1.9" '
      + 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
      + '<circle cx="9.5" cy="10" r="1.1" fill="#65676E"/><circle cx="14.5" cy="9.5" r="1.1" fill="#65676E"/>'
      + '<circle cx="12" cy="14.5" r="1.1" fill="#65676E"/></svg>');
    reopenBtn.type = 'button';
    reopenBtn.setAttribute('aria-label', 'Cookie settings');
    reopenBtn.addEventListener('click', function () { openPanel(true); });

    document.body.appendChild(backdrop);
    document.body.appendChild(panel);
    document.body.appendChild(reopenBtn);

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) {
        // Esc = refuz, la fel ca X. Nu inseamna niciodata acceptare.
        decide({ analytics: false, marketing: false });
      }
    });
  }

  function renderChoice() {
    panel.innerHTML = ''
      + '<h2 id="flc-title">Cookies on this site</h2>'
      + '<p id="flc-desc">We use cookies that are needed to run the site, and, only if you allow them, cookies that '
      + 'help us measure how the site is used and how our adverts perform. You can change your mind at any time. '
      + 'See our <a href="cookies.html">cookie policy</a>.</p>'
      + '<div class="flc-row">'
      + '<button type="button" class="flc-btn flc-reject" data-act="reject">Reject all</button>'
      + '<button type="button" class="flc-btn flc-accept" data-act="accept">Accept all</button>'
      + '</div>'
      + '<div class="flc-row" style="margin-top:6px"><button type="button" class="flc-link" data-act="custom">Customise</button></div>';
    wire();
  }

  function renderCustom(prefs) {
    var rows = CATS.map(function (c) {
      var on = c.locked ? true : !!prefs[c.id];
      return '<div class="flc-cat">'
        + '<input type="checkbox" id="flc-' + c.id + '"' + (on ? ' checked' : '')
        + (c.locked ? ' disabled' : '') + '>'
        + '<div><label for="flc-' + c.id + '">' + c.label + (c.locked ? ' (always on)' : '') + '</label>'
        + '<p>' + c.desc + '</p></div></div>';
    }).join('');
    panel.innerHTML = ''
      + '<h2 id="flc-title">Choose your cookies</h2>'
      + '<p id="flc-desc">Pick what you are happy with. Necessary cookies keep the site working and cannot be turned off.</p>'
      + '<div class="flc-cats">' + rows + '</div>'
      + '<div class="flc-row">'
      + '<button type="button" class="flc-btn flc-reject" data-act="reject">Reject all</button>'
      + '<button type="button" class="flc-btn flc-accept" data-act="save">Save choices</button>'
      + '</div>';
    wire();
  }

  function wire() {
    panel.querySelectorAll('[data-act]').forEach(function (b) {
      b.addEventListener('click', function () {
        var a = b.getAttribute('data-act');
        if (a === 'accept') decide({ analytics: true, marketing: true });
        else if (a === 'reject') decide({ analytics: false, marketing: false });
        else if (a === 'custom') renderCustom(currentPrefs());
        else if (a === 'save') decide({
          analytics: !!panel.querySelector('#flc-analytics').checked,
          marketing: !!panel.querySelector('#flc-marketing').checked
        });
      });
    });
    var first = panel.querySelector('button');
    if (first) first.focus();
  }

  function currentPrefs() {
    var v = read();
    return v ? v.prefs : { analytics: false, marketing: false };
  }

  function decide(prefs) {
    save(prefs);
    closePanel();
    reopenBtn.classList.add('is-on');
  }

  function openPanel(fromIcon) {
    lastFocus = document.activeElement;
    if (fromIcon) renderCustom(currentPrefs()); else renderChoice();
    panel.classList.add('is-open');
    if (fromIcon) backdrop.classList.add('is-open');
  }

  function closePanel() {
    panel.classList.remove('is-open');
    backdrop.classList.remove('is-open');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function start() {
    build();
    var saved = read();
    if (saved) {
      // alegerea a fost deja aplicata inline in <head>; aici doar aratam iconita de revocare
      reopenBtn.classList.add('is-on');
    } else {
      openPanel(false);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
