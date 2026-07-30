/* Arrows for the horizontal rails.
 *
 * The rail itself is a scroll-snap track, so it already works with a thumb, a
 * trackpad, the arrow keys and a screen reader with this file absent. All this
 * adds is a pair of buttons for mouse users, who have no good way to scroll a
 * horizontal container. The buttons stay hidden until we know they are needed.
 */
(function () {
  document.querySelectorAll('.rail').forEach(function (rail) {
    var track = rail.querySelector('.rail-track');
    var nav = rail.querySelector('.rail-nav');
    var prev = rail.querySelector('.rail-prev');
    var next = rail.querySelector('.rail-next');
    if (!track || !nav || !prev || !next) return;

    // One tile plus its gap, so a click lands cleanly on the next snap point.
    // Whatever the track holds counts as a tile, so text cards and photographs
    // both drive the same arrows.
    function step() {
      var tile = track.firstElementChild;
      if (!tile) return track.clientWidth;
      var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return tile.getBoundingClientRect().width + gap;
    }

    function scrollable() {
      return track.scrollWidth - track.clientWidth > 4;
    }

    // The track rests a few px in because of its padding, so ends need tolerance.
    var EDGE = 8;

    function sync() {
      nav.classList.toggle('on', scrollable());
      var max = track.scrollWidth - track.clientWidth;
      prev.disabled = track.scrollLeft <= EDGE;
      next.disabled = track.scrollLeft >= max - EDGE;
    }

    // We animate the scroll ourselves rather than using behavior:'smooth', which
    // gives no control over easing. Snapping has to come off for the duration:
    // each frame moves only a few pixels, and the snap engine drags every one of
    // them back to the nearest snap point, so the rail never leaves the first
    // card. It goes back on the moment we land, so touch and trackpad still snap.
    var anim = null;
    var guard = null;

    function go(dir) {
      var max = track.scrollWidth - track.clientWidth;
      var from = track.scrollLeft;
      var to = Math.max(0, Math.min(max, from + dir * step()));
      if (Math.abs(to - from) < 1) return;

      if (anim) cancelAnimationFrame(anim);
      track.style.scrollSnapType = 'none';
      // rAF stops in a hidden tab. Without this the track would be left with
      // snapping switched off if the visitor navigated away mid-scroll.
      clearTimeout(guard);
      guard = setTimeout(function () {
        if (anim) { cancelAnimationFrame(anim); anim = null; }
        track.style.scrollSnapType = '';
      }, 1200);

      if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
        track.scrollLeft = to;
        track.style.scrollSnapType = '';
        return;
      }

      var DUR = 380;
      var t0 = 0;
      anim = requestAnimationFrame(function frame(now) {
        if (!t0) t0 = now;
        var p = Math.min(1, (now - t0) / DUR);
        var eased = 1 - Math.pow(1 - p, 4); // strong ease-out, matches --ease-out
        track.scrollLeft = from + (to - from) * eased;
        if (p < 1) { anim = requestAnimationFrame(frame); }
        else { anim = null; clearTimeout(guard); track.style.scrollSnapType = ''; sync(); }
      });
    }

    prev.addEventListener('click', function () { go(-1); });
    next.addEventListener('click', function () { go(1); });
    track.addEventListener('scroll', sync, { passive: true });
    addEventListener('resize', sync, { passive: true });
    sync();
  });
})();
