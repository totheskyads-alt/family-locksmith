/* Conversion tracking, provider-agnostic.
 *
 * The only metric that matters for this business is "did the visitor make
 * contact". This records every call, WhatsApp tap and form submit into
 * window.dataLayer, which is what GA4 and Google Tag Manager both read.
 *
 * No third-party script is loaded here, so it costs nothing and sets no
 * cookies until the client actually adds GA4/GTM. Until then the events simply
 * queue up harmlessly in dataLayer.
 */
(function () {
  window.dataLayer = window.dataLayer || [];

  function push(event, detail) {
    window.dataLayer.push(Object.assign({
      event: event,
      page: location.pathname.split('/').pop() || 'index.html'
    }, detail || {}));
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('tel:') === 0) {
      push('contact_call', { method: 'phone', location: placement(a) });
    } else if (href.indexOf('wa.me') > -1) {
      push('contact_whatsapp', { method: 'whatsapp', location: placement(a) });
    }
  }, { passive: true });

  var form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', function () {
      push('contact_form', { method: 'form' });
    });
  }

  // Where on the page the tap happened, so we can see which CTA earns its keep.
  function placement(a) {
    if (a.closest('.header')) return 'header';
    if (a.closest('.mobile-bar')) return 'sticky-bar';
    if (a.closest('.mnav')) return 'mobile-menu';
    if (a.closest('.hero, .page-hero')) return 'hero';
    if (a.closest('.side-card')) return 'side-card';
    if (a.closest('.cta-band')) return 'cta-band';
    if (a.closest('.footer')) return 'footer';
    return 'body';
  }
})();
