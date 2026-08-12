/* Validare pentru formularele de lead: telefon UK real + cod postal UK valid.
   Aceleasi reguli se aplica si pe server, in /api/lead. */
(function () {
  'use strict';

  // Cod postal UK, formatul oficial. Accepta si fara spatiu: "M12AB" sau "M1 2AB".
  var POSTCODE = /^(GIR ?0AA|[A-PR-UWYZ](?:[0-9]{1,2}|[A-HK-Y][0-9](?:[0-9]|[ABEHMNPRVWXY])?|[0-9][A-HJKPSTUW]) ?[0-9][ABD-HJLNP-UW-Z]{2})$/i;

  function cleanPhone(v) {
    return String(v || '').replace(/[\s()\-.]/g, '');
  }

  function checkPhone(v) {
    var p = cleanPhone(v);
    if (p.indexOf('+44') === 0) p = '0' + p.slice(3);
    else if (p.indexOf('0044') === 0) p = '0' + p.slice(4);
    if (!/^0[1237]\d{8,9}$/.test(p)) return null;      // fix, mobil sau non-geografic UK
    if (/^(\d)\1+$/.test(p.slice(1))) return null;      // 0000000000, 1111111111 etc
    return p;
  }

  function checkPostcode(v) {
    var p = String(v || '').trim().toUpperCase().replace(/\s+/g, ' ');
    if (!POSTCODE.test(p)) return null;
    var flat = p.replace(/\s/g, '');
    return flat.slice(0, flat.length - 3) + ' ' + flat.slice(-3);   // normalizat: "M1 2AB"
  }

  window.FLform = {
    checkPhone: checkPhone,
    checkPostcode: checkPostcode,

    /* Verifica formularul, arata mesajele si returneaza valorile curatate sau null. */
    validate: function (form) {
      var ok = true;
      var out = {};

      [['phone', checkPhone, 'Please enter a real UK phone number, for example 07123 456789.'],
       ['postcode', checkPostcode, 'Please enter a valid UK postcode, for example M1 2AB.']
      ].forEach(function (row) {
        var field = form.querySelector('[name="' + row[0] + '"]');
        if (!field) return;
        var err = form.querySelector('[data-err="' + row[0] + '"]');
        var raw = field.value.trim();
        var val = raw ? row[1](raw) : null;

        if (!val) {
          ok = false;
          field.setAttribute('aria-invalid', 'true');
          if (err) { err.textContent = raw ? row[2] : 'This one we do need.'; err.hidden = false; }
          if (ok === false && !out._first) out._first = field;
        } else {
          field.removeAttribute('aria-invalid');
          field.value = val;                 // scriem inapoi forma curatata
          if (err) { err.hidden = true; err.textContent = ''; }
          out[row[0]] = val;
        }
      });

      if (!ok && out._first) { out._first.focus(); }
      return ok ? out : null;
    }
  };

  /* Ascunde mesajul de eroare imediat ce omul incepe sa corecteze. */
  document.addEventListener('input', function (e) {
    var n = e.target && e.target.name;
    if (n !== 'phone' && n !== 'postcode') return;
    var form = e.target.form; if (!form) return;
    var err = form.querySelector('[data-err="' + n + '"]');
    if (err && !err.hidden) { err.hidden = true; e.target.removeAttribute('aria-invalid'); }
  });
})();
