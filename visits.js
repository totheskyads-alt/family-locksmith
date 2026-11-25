/* Anti click fraud: la fiecare vizita venita dintr-o reclama Google
 * (link cu gclid, gbraid sau wbraid) trimite ora, pagina si id-ul clicului.
 * IP-ul il citeste serverul din cerere; scriptul nu pune cookie-uri.
 * Rezultatele ajung intr-un tabel, din care se vad IP-urile repetate. */
(function () {
  try {
    var q = new URLSearchParams(location.search);
    var data = { page: location.pathname || '/', ref: document.referrer || '' };
    var hit = false;
    ['gclid', 'gbraid', 'wbraid'].forEach(function (k) {
      var v = q.get(k);
      if (v) { data[k] = v; hit = true; }
    });
    if (!hit) return;
    data.campaign = q.get('utm_campaign') || q.get('campaignid') || '';
    data.keyword = q.get('utm_term') || q.get('keyword') || '';

    // o singura inregistrare per clic, chiar daca pagina se reincarca
    var id = data.gclid || data.gbraid || data.wbraid;
    try {
      if (sessionStorage.getItem('fl_v_' + id)) return;
      sessionStorage.setItem('fl_v_' + id, '1');
    } catch (e) {}

    fetch('https://iyrqlykoncdvwxvkkzqq.supabase.co/functions/v1/fl-visit', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify(data),
      keepalive: true,
      mode: 'cors',
      credentials: 'omit'
    }).catch(function () {});
  } catch (e) {}
})();
