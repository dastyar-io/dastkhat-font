/* Dastkhat landing page interactions */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;
  const fa = n => String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const WEIGHTS = ['نازک', 'خیلی سبک', 'سبک', 'معمولی', 'متوسط', 'نیمه‌ضخیم', 'ضخیم', 'خیلی ضخیم', 'سیاه'];

  /* ---------- global dot style ---------- */
  function setDots(v) {
    root.dataset.dots = v;
    try { localStorage.setItem('dk-dots', v); } catch (e) {}
    $$('[data-set-dots]').forEach(b => b.setAttribute('aria-pressed', b.dataset.setDots === v));
    $$('.fam .state').forEach(s => {
      s.textContent = s.parentElement.dataset.setDots === v ? s.dataset.on : s.dataset.off;
    });
  }
  $$('[data-set-dots]').forEach(b => b.addEventListener('click', () => setDots(b.dataset.setDots)));
  setDots(root.dataset.dots || 'square');

  /* ---------- nav ---------- */
  const nav = $('#nav'), hero = $('.hero');
  const navState = () => nav.classList.toggle('solid', scrollY > hero.offsetHeight - 70);

  /* ---------- reveal ---------- */
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    $$('[data-count]', e.target).forEach(count);
    io.unobserve(e.target);
  }), { threshold: 0.14 });
  $$('.rv').forEach(el => io.observe(el));

  /* ---------- count up ---------- */
  function count(el) {
    const to = +el.dataset.count;
    if (calm) { el.textContent = fa(to); return; }
    const t0 = performance.now();
    (function tick(t) {
      const p = Math.min(1, (t - t0) / 900);
      el.textContent = fa(Math.round(to * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    })(t0);
  }
  $$('.stats [data-count]').forEach(count);

  /* ---------- marquee: duplicate for a seamless loop ---------- */
  $$('.mq-track').forEach(t => { t.innerHTML += t.innerHTML; });

  /* ---------- hero: dot grid + pointer-driven weight ---------- */
  const cv = $('#grid'), cx = cv.getContext('2d');
  const word = $('#word'), wread = $('#wread'), whint = $('#whint');
  let W = 0, H = 0, px = -9999, py = -9999, inside = false, heroVisible = true, w = 900, shown = 0;
  function size() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    W = hero.clientWidth; H = hero.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr;
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function draw(t) {
    cx.clearRect(0, 0, W, H);
    const gap = W < 700 ? 30 : 38, mode = root.dataset.dots, R = 230;
    cx.fillStyle = '#fff';
    for (let y = gap / 2; y < H; y += gap) {
      for (let x = gap / 2; x < W; x += gap) {
        const d = Math.hypot(x - px, y - py);
        const k = d < R ? (1 - d / R) ** 2 : 0;
        const wave = calm ? 0.5 : 0.5 + 0.5 * Math.sin(x * 0.011 + y * 0.017 + t * 0.0009);
        const s = 2.4 + wave * 1.4 + k * 13;
        cx.globalAlpha = 0.14 + wave * 0.08 + k * 0.7;
        if (mode === 'bar') {
          cx.fillRect(x - s * 1.15, y - s * 0.27, s * 2.3, s * 0.54);
        } else {
          const a = mode === 'diamond' ? Math.PI / 4 : k * Math.PI / 2;
          if (a) { cx.save(); cx.translate(x, y); cx.rotate(a); cx.fillRect(-s / 2, -s / 2, s, s); cx.restore(); }
          else cx.fillRect(x - s / 2, y - s / 2, s, s);
        }
      }
    }
    cx.globalAlpha = 1;
  }
  function loop(t) {
    if (heroVisible) {
      draw(t);
      // reading direction is right to left, so the word gets heavier as the pointer moves left
      const target = inside ? 100 + 800 * (1 - px / W) : 520 + 380 * Math.sin(t * 0.0007);
      w += (target - w) * 0.09;
      const r = Math.round(w);
      if (r !== shown) { shown = r; word.style.fontWeight = r; wread.textContent = fa(r); }
    }
    requestAnimationFrame(loop);
  }
  hero.addEventListener('pointermove', e => {
    const r = hero.getBoundingClientRect();
    px = e.clientX - r.left; py = e.clientY - r.top;
    if (e.pointerType === 'mouse') { inside = true; whint.textContent = ''; }
  });
  hero.addEventListener('pointerleave', () => { inside = false; px = py = -9999; });
  new IntersectionObserver(es => { heroVisible = es[0].isIntersecting; }).observe(hero);
  addEventListener('resize', () => { size(); if (calm) draw(0); });
  size();
  if (calm) { draw(0); whint.textContent = ''; new MutationObserver(() => draw(0)).observe(root, { attributes: true, attributeFilter: ['data-dots'] }); }
  else requestAnimationFrame(loop);

  /* ---------- one dot changes the word ---------- */
  $$('.pair').forEach(b => b.addEventListener('click', () => {
    const on = b.getAttribute('aria-pressed') !== 'true';
    b.setAttribute('aria-pressed', on);
    b.classList.remove('fall');
    if (on) { void b.offsetWidth; b.classList.add('fall'); }
  }));

  /* ---------- scroll-driven weight ---------- */
  const sw = $('.sw'), swLine = $('#sw-line'), swNum = $('#sw-num'), swName = $('#sw-name'), stops = $$('#sw-stops i');
  let swShown = -1;
  function swUpdate() {
    const r = sw.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, -r.top / (r.height - innerHeight)));
    const v = Math.round(100 + 800 * p);
    if (v === swShown) return;
    swShown = v;
    swLine.style.fontWeight = v;
    swNum.textContent = fa(v);
    const i = Math.min(8, Math.round((v - 100) / 100));
    swName.textContent = WEIGHTS[i];
    stops.forEach((s, j) => { s.classList.toggle('on', j < i); s.classList.toggle('cur', j === i); });
  }
  let ticking = false;
  addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { navState(); swUpdate(); ticking = false; });
  }, { passive: true });
  navState(); swUpdate();

  /* ---------- type tester ---------- */
  const live = $('#t-live'), box = $('#t-box');
  const press = (group, btn) => $$('button', group).forEach(x => x.setAttribute('aria-pressed', x === btn));
  $$('#t-fam button').forEach(b => b.addEventListener('click', () => {
    press($('#t-fam'), b);
    live.style.fontFamily = `'${b.dataset.f}', Tahoma, sans-serif`;
  }));
  const tw = $('#t-w'), ts = $('#t-s'), tl = $('#t-l');
  const tSync = () => {
    live.style.fontWeight = tw.value; $('#t-wv').textContent = fa(tw.value);
    live.style.fontSize = ts.value + 'px'; $('#t-sv').textContent = fa(ts.value);
    live.style.lineHeight = tl.value / 10; $('#t-lv').textContent = fa((tl.value / 10).toFixed(1)).replace('.', '٫');
  };
  [tw, ts, tl].forEach(i => i.addEventListener('input', tSync));
  $$('.swatches button').forEach(b => b.addEventListener('click', () => {
    press($('.swatches'), b); box.dataset.theme = b.dataset.t;
  }));
  const PRESETS = {
    title: { t: 'پاییز، فصل کتاب و چای', w: 900, s: 96, l: 14 },
    poem: { t: 'توانا بود هر که دانا بود\nز دانش دل پیر برنا بود', w: 300, s: 56, l: 20 },
    price: { t: '۱٬۲۸۵٬۰۰۰ تومان\n۲۴ قسط، بدون پیش‌پرداخت', w: 800, s: 72, l: 16 },
    ui: { t: 'ورود به حساب · فراموشی رمز · ثبت‌نام رایگان · افزودن به سبد · پیگیری سفارش · تنظیمات', w: 500, s: 22, l: 20 },
    para: { t: 'متن فارسی به‌خاطر کشیدگی حروف و نقطه‌ها به فاصله خطوط بیشتری از لاتین نیاز دارد. اگر متن فشرده به نظر می‌رسد، به‌جای کوچک‌کردن اندازه، اول فاصله خطوط را زیاد کنید.', w: 400, s: 20, l: 20 },
    mix: { t: 'نسخه ۲ اپلیکیشن با Dark Mode و پشتیبانی از iOS 18 منتشر شد', w: 700, s: 48, l: 17 }
  };
  $$('#t-presets button').forEach(b => b.addEventListener('click', () => {
    const p = PRESETS[b.dataset.p];
    live.innerText = p.t; live.style.whiteSpace = 'pre-wrap';
    tw.value = p.w; ts.value = innerWidth < 680 ? Math.min(p.s, 46) : p.s; tl.value = p.l;
    tSync();
  }));
  live.addEventListener('paste', e => {
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData('text/plain');
    const sel = getSelection();
    if (!sel.rangeCount) return;
    sel.deleteFromDocument();
    sel.getRangeAt(0).insertNode(document.createTextNode(text));
    sel.collapseToEnd();
  });
  if (innerWidth < 680) ts.value = 44;
  tSync();

  /* ---------- Jalali calendar, live ---------- */
  (function calendar() {
    const MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
    const DAYS = ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'];
    const cal = $('#cal');
    let parts;
    try {
      const f = new Intl.DateTimeFormat('en-US-u-ca-persian-nu-latn', { year: 'numeric', month: 'numeric', day: 'numeric' });
      parts = d => Object.fromEntries(f.formatToParts(d).filter(p => p.type !== 'literal').map(p => [p.type, parseInt(p.value, 10)]));
      if (!(parts(new Date()).year > 1300)) throw 0;
    } catch (e) { cal.closest('.tile').hidden = true; return; }
    const now = new Date(), today = parts(now);
    const first = new Date(now); first.setDate(now.getDate() - (today.day - 1));
    let len = 28;
    for (; len < 32; len++) { const d = new Date(first); d.setDate(first.getDate() + len); if (parts(d).month !== today.month) break; }
    const offset = (first.getDay() + 1) % 7; // week starts on Saturday
    let html = 'شیدسچپج'.split('').map(c => `<span class="wd">${c}</span>`).join('');
    html += '<span></span>'.repeat(offset);
    for (let d = 1; d <= len; d++) {
      const col = (offset + d - 1) % 7;
      html += `<span class="${d === today.day ? 'today' : col === 6 ? 'fri' : ''}">${fa(d)}</span>`;
    }
    cal.innerHTML = html;
    $('#cal-m').textContent = MONTHS[today.month - 1];
    $('#cal-y').textContent = fa(today.year);
    $('#cal-today').textContent = `${DAYS[now.getDay()]} ${fa(today.day)} ${MONTHS[today.month - 1]}`;
    const clock = $('#cal-clock');
    const tick = () => { const n = new Date(); clock.textContent = fa(`${String(n.getHours()).padStart(2, '0')}:${String(n.getMinutes()).padStart(2, '0')}`); };
    tick(); setInterval(tick, 15000);
  })();

  /* ---------- poetry ---------- */
  const POEMS = [
    ['توانا بود هر که دانا بود', 'ز دانش دل پیر برنا بود', 'فردوسی'],
    ['بنی‌آدم اعضای یکدیگرند', 'که در آفرینش ز یک گوهرند', 'سعدی'],
    ['بشنو این نی چون شکایت می‌کند', 'از جدایی‌ها حکایت می‌کند', 'مولوی'],
    ['هرگز نمیرد آن که دلش زنده شد به عشق', 'ثبت است بر جریدهٔ عالم دوام ما', 'حافظ']
  ];
  const poem = $('#poem'), pdots = $('#pdots');
  let pi = 0, ptimer;
  pdots.innerHTML = POEMS.map(() => '<i></i>').join('');
  function showPoem(i) {
    pi = (i + POEMS.length) % POEMS.length;
    const [a, b, c] = POEMS[pi];
    $('#pv1').textContent = a; $('#pv2').textContent = b; $('#pp').textContent = c;
    $$('i', pdots).forEach((d, j) => d.classList.toggle('on', j === pi));
  }
  function nextPoem() {
    poem.classList.add('out');
    setTimeout(() => { showPoem(pi + 1); poem.classList.remove('out'); }, calm ? 0 : 520);
  }
  function autoPoem() { clearInterval(ptimer); if (!calm) ptimer = setInterval(nextPoem, 6000); }
  poem.addEventListener('click', () => { nextPoem(); autoPoem(); });
  poem.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); nextPoem(); autoPoem(); } });
  showPoem(0); autoPoem();

  /* ---------- FaNum demo ---------- */
  const fin = $('#fn-in'), fout = $('#fn-out');
  fin.addEventListener('input', () => { fout.textContent = fin.value || '0'; });

  /* ---------- glyph explorer ---------- */
  const GLYPHS = 'ا ب پ ت ث ج چ ح خ د ذ ر ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ه ی آ ئ ؤ ء ۰ ۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹ ، ؛ ؟ « » ٪ A a G g R Q & @'.split(' ');
  const FORMS = [['تنها', c => c], ['آغازی', c => c + '‍'], ['میانی', c => '‍' + c + '‍'], ['پایانی', c => '‍' + c]];
  const ggrid = $('#g-grid'), gbig = $('#g-big'), gcode = $('#g-code'), gforms = $('#g-forms');
  ggrid.innerHTML = GLYPHS.map(c => `<button aria-pressed="false">${c.replace('&', '&amp;')}</button>`).join('');
  function pick(btn) {
    const c = btn.textContent;
    press(ggrid, btn);
    gbig.textContent = c;
    gcode.textContent = 'U+' + c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0');
    const joins = /[ؠ-يپچژکگی]/.test(c) && c !== 'ء';
    gforms.innerHTML = joins
      ? FORMS.map(([n, f]) => `<div><b>${f(c)}</b><span>${n}</span></div>`).join('')
      : [100, 400, 700, 900].map(wt => `<div><b style="font-weight:${wt}">${c.replace('&', '&amp;')}</b><span>${fa(wt)}</span></div>`).join('');
  }
  ggrid.addEventListener('click', e => { const b = e.target.closest('button'); if (b) pick(b); });
  pick($$('button', ggrid)[15]);

  /* ---------- code tabs + copy ---------- */
  const tabs = $$('.tabs button'), panes = $$('.pane pre'), copy = $('#copy');
  tabs.forEach(t => t.addEventListener('click', () => {
    tabs.forEach(x => x.setAttribute('aria-selected', x === t));
    panes.forEach(p => { p.hidden = p.dataset.pane !== t.dataset.tab; });
  }));
  copy.addEventListener('click', async () => {
    const text = panes.find(p => !p.hidden).textContent;
    try { await navigator.clipboard.writeText(text); copy.textContent = 'کپی شد'; copy.classList.add('ok'); }
    catch (e) { copy.textContent = 'کپی نشد'; }
    setTimeout(() => { copy.textContent = 'کپی'; copy.classList.remove('ok'); }, 1600);
  });
})();
