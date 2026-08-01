/* Submeniul de servicii: deschidere la click/tastatura, pe desktop si pe telefon. */
(function () {
  'use strict';
  function wire(toggle) {
    var box = document.getElementById(toggle.getAttribute('aria-controls'));
    if (!box) return;
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      box.classList.toggle('is-open', !open);
      if (box.classList.contains('mnav-sub')) {
        box.style.maxHeight = !open ? box.scrollHeight + 'px' : '';
      }
    });
  }
  document.querySelectorAll('[data-subtoggle]').forEach(wire);

  // Esc inchide, click in afara inchide (doar submeniul de pe desktop)
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.nav-sub.is-open').forEach(function (b) {
      b.classList.remove('is-open');
      var t = document.querySelector('[aria-controls="' + b.id + '"]');
      if (t) { t.setAttribute('aria-expanded', 'false'); t.focus(); }
    });
  });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.nav-sub.is-open').forEach(function (b) {
      var t = document.querySelector('[aria-controls="' + b.id + '"]');
      if (b.contains(e.target) || (t && t.contains(e.target))) return;
      b.classList.remove('is-open');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  });
})();
