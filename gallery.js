/* Lightbox for the job gallery.
 *
 * The grid is plain <figure> elements with real <img> and captions, so it is
 * complete and readable with this file blocked. All this adds is a larger view
 * on click. <dialog> handles the backdrop, focus trapping and Esc for us.
 */
(function () {
  var items = document.querySelectorAll('.gal-item');
  if (!items.length || !window.HTMLDialogElement) return;

  var dlg = document.createElement('dialog');
  dlg.className = 'lb';
  dlg.innerHTML =
    '<figure class="lb-fig"><img alt=""><figcaption></figcaption></figure>' +
    '<button class="lb-close" type="button" aria-label="Close">' +
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" ' +
    'stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg></button>';
  document.body.appendChild(dlg);

  var big = dlg.querySelector('img');
  var cap = dlg.querySelector('figcaption');

  items.forEach(function (item) {
    var img = item.querySelector('img');
    var text = item.querySelector('figcaption');
    if (!img) return;

    // Keyboard users get a real control rather than a click-only figure.
    item.tabIndex = 0;
    item.setAttribute('role', 'button');
    item.setAttribute('aria-label', 'Enlarge: ' + (img.alt || 'photo'));

    function open() {
      big.src = img.currentSrc || img.src;
      big.alt = img.alt || '';
      cap.textContent = text ? text.textContent : '';
      cap.hidden = !cap.textContent;
      dlg.showModal();
    }

    item.addEventListener('click', open);
    item.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
  });

  dlg.querySelector('.lb-close').addEventListener('click', function () { dlg.close(); });
  // Clicking the backdrop means the click landed on the dialog box itself.
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function () { big.removeAttribute('src'); });
})();
