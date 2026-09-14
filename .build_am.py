#!/usr/bin/env python3
"""Génère ~/am-residence/index.html à partir du gabarit du site Villa Lune de Miel."""
import os, re, json, shutil
from PIL import Image

HOME = os.path.expanduser('~')
VILLA = os.path.join(HOME, 'villa-lune-de-miel')
OUT = os.path.join(HOME, 'am-residence')
IMG = os.path.join(OUT, 'images')
SITE_URL = 'https://amresidence.rentanoo.com/'
MAPS = 'https://maps.app.goo.gl/PBUCJAsTMguuWiBfA'
LAT, LNG = -13.3874274, 48.2505708
PRICE = '500&nbsp;000&nbsp;Ar'

src = open(os.path.join(VILLA, 'index.html'), encoding='utf-8').read()
css = src[src.index('<style>') + 7: src.index('</style>')]
script_main = src[src.index("<script>\n  document.addEventListener('DOMContentLoaded'"): src.index('</script>', src.index("document.addEventListener('DOMContentLoaded'")) + 9]
script_form = src[src.index("<script>\n(function(){\n  var form=document.getElementById('resa-form')"):]
script_form = script_form[: script_form.index('</script>') + 9]

# ---------- Traductions ----------
TR = {}
def t(fr, it, en):
    # clé = texte FR sans espaces de bord (le script i18n compare le nœud texte « trimé »)
    TR[fr.strip()] = {'it': it.strip(), 'en': en.strip()}
    return fr

# ---------- Aides HTML ----------
EYEBROW = "font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:var(--apt-accent);margin-bottom:12px"
H2 = "font-family:'Fraunces',serif;font-weight:300;font-size:clamp(30px,4.2vw,58px);line-height:1.03;letter-spacing:-.01em;margin:0"
P = "font-size:16.5px;line-height:1.62;color:rgba(22,33,31,.72)"
CHAT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-12.1 7.5L3 20.5l1.6-5.7A8.5 8.5 0 1 1 21 11.5Z"/></svg>'
CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#C9A45C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 13 4 4L19 7"/></svg>'

def em(fr):
    return f'<span style="font-style:italic;font-weight:400">{fr}</span>'

def specs(items):
    return ''.join(f'<span class="lm-spec">{s}</span>' for s in items)

def book_btn(room, label):
    return (f'<a href="#reservation" class="h-book" data-book="{room}" style="display:inline-flex;align-items:center;gap:11px;padding:15px 26px;'
            f'border-radius:999px;background:#1785C0;color:#fff;font-weight:600;font-size:16px;box-shadow:0 16px 38px -16px rgba(10,20,19,.45);'
            f'transition:background .25s ease,transform .25s ease">{label}</a>')

used = set()
def img_path(name):
    used.add(name + '.webp')
    return f'images/{name}.webp'

def size(name):
    with Image.open(os.path.join(IMG, name + '.webp')) as im:
        return im.size

SUN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
MOON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 1 1 9.5 3.5a7 7 0 0 0 11 11Z"/></svg>'

def mode_tabs():
    return (f'<div class="mode-tabs" role="group" aria-label="Jour / nuit">'
            f'<button type="button" class="mt-day" data-set-mode="day">{SUN}{t("De jour", "Di giorno", "By day")}</button>'
            f'<button type="button" class="mt-night" data-set-mode="night">{MOON}{t("De nuit", "Di notte", "By night")}</button></div>')

def photo_set(mode, covers, extras, fallback=False):
    c1, c2 = covers
    w1, h1 = size(c1[0]); w2, h2 = size(c2[0])
    icon, label = (SUN, t('Vue de jour', 'Vista di giorno', 'Daytime view')) if (mode == 'day' or fallback) else (MOON, t('Vue de nuit', 'Vista di notte', 'Night view'))
    tag = f'<span class="photo-tag">{icon}{label}</span>'
    extra_html = ''.join(f'<img loading="lazy" decoding="async" src="{img_path(n)}" alt="{a}">' for n, a in extras)
    more = f'<button type="button" class="room-more"><span>{t("Voir plus de photos", "Vedi altre foto", "See more photos")}</span> <span class="n">+{len(extras)}</span></button>' if extras else ''
    note = f'<p class="mode-note">{MOON}{t("Photos de nuit bientôt disponibles : voici la pièce de jour.", "Foto notturne in arrivo: ecco la stanza di giorno.", "Night photos coming soon: here is the room by day.")}</p>' if fallback else ''
    return f'''<div class="photo-set set-{mode}">
        {note}
        <div class="room-photos">
          <div data-reveal style="position:relative;border-radius:10px;overflow:hidden;aspect-ratio:3/4">{tag}<img class="slot" loading="lazy" decoding="async" src="{img_path(c1[0])}" width="{w1}" height="{h1}" alt="{c1[1]}"></div>
          <div data-reveal style="position:relative;border-radius:10px;overflow:hidden;aspect-ratio:3/4;margin-top:clamp(28px,5vw,64px)"><img class="slot" loading="lazy" decoding="async" src="{img_path(c2[0])}" width="{w2}" height="{h2}" alt="{c2[1]}"></div>
        </div>
        {more}
        <div class="gallery-extra" hidden>{extra_html}</div>
      </div>'''

def room_section(sid, room_attr, eyebrow, title, text, spec_list, covers, extras, reverse, bg, cta=None, night=None):
    day_html = photo_set('day', covers, extras)
    night_html = photo_set('night', night[0], night[1]) if night else photo_set('night', covers, extras, fallback=True)
    cta_html = f'\n      {cta}' if cta else ''
    return f'''
<!-- ===== {eyebrow.upper()} ===== -->
<section class="theme-am" id="{sid}" data-room="{room_attr}" aria-label="{eyebrow}" style="background:{bg};padding:clamp(56px,8vw,104px) clamp(20px,5vw,64px);scroll-margin-top:76px;border-top:1px solid rgba(22,33,31,.07)">
  <div class="room-grid{' is-reverse' if reverse else ''}" style="max-width:1240px;margin:0 auto">
    <div data-reveal>
      <div style="{EYEBROW}">{eyebrow}</div>
      <h2 style="{H2}">{title}</h2>
      <p style="{P};margin:18px 0 0;max-width:46ch">{text}</p>
      <div style="display:flex;flex-wrap:wrap;gap:10px 12px;margin:clamp(22px,3vw,30px) 0 clamp(24px,3.4vw,34px)">
        {specs(spec_list)}
      </div>{cta_html}
    </div>
    <div class="room-photos-wrap">
      {mode_tabs()}
      {day_html}
      {night_html}
    </div>
  </div>
</section>
'''

# ---------- Contenu ----------
A = 'AM Résidence — '
HERO = [('piscine-jour-1375', 'piscine-nuit-6c64ee76', A + 'la piscine et son deck en bois'),
        ('bar-1380', 'piscine-nuit-1222', A + 'le bar face à la piscine'),
        ('chambre-double-1363', 'chambre-double-1363', A + 'une chambre double prête à vous accueillir'),
        ('piscine-jour-1376', 'piscine-nuit-1f7798e9', A + 'la piscine et les transats'),
        ('piscine-jour-1378', 'exterieur-1240', A + "l'hôtel et sa façade")]

hero_slides = '\n'.join(
    f'      <div class="hero-slide{" is-active" if i == 0 else ""}"><img src="{img_path(d)}" data-day="{img_path(d)}" data-night="{img_path(nt)}" alt="{a}"></div>' for i, (d, nt, a) in enumerate(HERO))
hero_dots = '\n'.join(
    f'    <button class="hero-dot{" is-active" if i == 0 else ""}" type="button" aria-label="Photo {i+1}"></button>' for i in range(len(HERO)))

def band_item(icon, label):
    return (f'<div style="display:flex;align-items:center;gap:10px;font-size:15px;font-weight:500;color:rgba(22,33,31,.86)">'
            f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22385C" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="flex:none">{icon}</svg>{label}</div>')

ICON = {
    'hotel': '<path d="M4 20V9l8-5 8 5v11M4 20h16M9 20v-6h6v6"/>',
    'pool': '<path d="M2 17c2-1.4 4-1.4 6 0s4 1.4 6 0 4-1.4 6 0M2 21c2-1.4 4-1.4 6 0s4 1.4 6 0 4-1.4 6 0M8 14V5a2 2 0 0 1 4 0M16 14V5a2 2 0 0 0-4 0M8 9h8"/>',
    'bar': '<path d="M4 4h16l-8 9-8-9Z"/><path d="M12 13v6M8 21h8"/>',
    'pin': '<path d="M12 21c5-6 8-9 8-12a8 8 0 1 0-16 0c0 3 3 6 8 12Z"/><circle cx="12" cy="9" r="2.5"/>',
    'plane': '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    'wave': '<path d="M2 7c2-1.4 4-1.4 6 0s4 1.4 6 0 4-1.4 6 0M2 12c2-1.4 4-1.4 6 0s4 1.4 6 0 4-1.4 6 0"/>',
    'snow': '<path d="M12 2v20M12 6l3.5-3M12 6 8.5 3M12 18l3.5 3M12 18l-3.5 3M2 12h20M6 12 3 8.5M6 12 3 15.5M18 12l3-3.5M18 12l3 3.5"/>',
    'tv': '<rect x="2.5" y="5" width="19" height="12.5" rx="2"/><path d="M8 21h8M12 17.5V21"/>',
    'shower': '<path d="M4 20V8a4 4 0 0 1 8 0M9 8h6M11 12v.01M14 12v.01M17 12v.01M11 15v.01M14 15v.01M17 15v.01"/>',
    'desk': '<path d="M3 7h18M5 7v13M19 7v13M5 12h14"/>',
    'car': '<path d="M3 16v-4l2-5h9l4 5h2a1 1 0 0 1 1 1v3h-3M3 16h3M9 16h9M6 16a2 2 0 1 0 4 0M17 16a2 2 0 1 0 4 0"/>',
    'bell': '<path d="M4 18h16M6 18a6 6 0 0 1 12 0M12 9V7M10 7h4"/>',
    'wifi': '<path d="M2 8.5a15 15 0 0 1 20 0M5 12a10 10 0 0 1 14 0M8 15.5a5 5 0 0 1 8 0"/><circle cx="12" cy="19.3" r="1.1"/>',
    'bolt': '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>',
}

band = f'''
<!-- ===== BANDEAU ATOUTS ===== -->
<section id="decouvrir" aria-label="Atouts" style="background:#ffffff;color:#16211F;padding:clamp(52px,6.5vw,80px) clamp(20px,5vw,64px);border-top:1px solid rgba(22,33,31,.07)">
  <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;gap:34px 28px">
    <div data-reveal style="min-width:140px">
      <div style="font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:rgba(22,33,31,.42);margin-bottom:16px">{t("L'hôtel", "L'hotel", "The hotel")}</div>
      <div style="display:flex;flex-direction:column;gap:11px">
        {band_item(ICON['hotel'], t('15 chambres', '15 camere', '15 rooms'))}
        {band_item(ICON['pool'], t('Piscine', 'Piscina', 'Swimming pool'))}
        {band_item(ICON['bar'], t('Bar', 'Bar', 'Bar'))}
      </div>
    </div>
    <div class="band-sep" style="width:1px;height:82px;background:rgba(22,33,31,.12)"></div>
    <div data-reveal style="min-width:150px">
      <div style="font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:rgba(22,33,31,.42);margin-bottom:16px">{t("L'emplacement", 'La posizione', 'Location')}</div>
      <div style="display:flex;flex-direction:column;gap:11px">
        {band_item(ICON['pin'], t('Djabala, Hell-Ville', 'Djabala, Hell-Ville', 'Djabala, Hell-Ville'))}
        {band_item(ICON['wave'], t('Ambatoloaka ~10 min', 'Ambatoloaka ~10 min', 'Ambatoloaka ~10 min'))}
        {band_item(ICON['plane'], t('Aéroport ~20 min', 'Aeroporto ~20 min', 'Airport ~20 min'))}
      </div>
    </div>
    <div class="band-sep" style="width:1px;height:82px;background:rgba(22,33,31,.12)"></div>
    <div data-reveal style="min-width:150px">
      <div style="font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:rgba(22,33,31,.42);margin-bottom:16px">{t('Les chambres', 'Le camere', 'The rooms')}</div>
      <div style="display:flex;flex-direction:column;gap:11px">
        {band_item(ICON['snow'], t('Climatisation', 'Aria condizionata', 'Air conditioning'))}
        {band_item(ICON['tv'], t('TV & minibar', 'TV e minibar', 'TV & minibar'))}
        {band_item(ICON['desk'], t('Espace de travail', 'Spazio di lavoro', 'Workspace'))}
      </div>
    </div>
    <div class="band-sep" style="width:1px;height:82px;background:rgba(22,33,31,.12)"></div>
    <div data-reveal style="min-width:130px">
      <div style="font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:rgba(22,33,31,.42);margin-bottom:16px">{t('Sur place', 'In loco', 'On site')}</div>
      <div style="display:flex;flex-direction:column;gap:11px">
        {band_item(ICON['wifi'], t('Wifi Starlink', 'Wi-Fi Starlink', 'Starlink Wi-Fi'))}
        {band_item(ICON['bolt'], t('Groupe électrogène', 'Gruppo elettrogeno', 'Backup generator'))}
        {band_item(ICON['car'], t('Parking', 'Parcheggio', 'Parking'))}
      </div>
    </div>
    <div class="band-sep" style="width:1px;height:82px;background:rgba(22,33,31,.12)"></div>
    <div data-reveal style="min-width:120px">
      <div style="font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:rgba(22,33,31,.42);margin-bottom:16px">{t('Le tarif', 'La tariffa', 'Rate')}</div>
      <div style="font-family:'Fraunces',serif;font-weight:400;font-size:clamp(28px,3vw,40px);line-height:1;color:#C9A45C;white-space:nowrap">{PRICE}</div>
      <div style="font-size:13px;letter-spacing:.02em;color:rgba(22,33,31,.55);margin-top:9px">{t('la nuit, prix de base', 'a notte, prezzo base', 'per night, base rate')}</div>
    </div>
  </div>
</section>
'''

def room_card(href, img, alt, flag, name, text):
    return f'''
    <a href="#{href}" data-reveal class="h-card theme-am" style="display:block;border-radius:14px;overflow:hidden;border:1px solid rgba(22,33,31,.1);background:#fff;box-shadow:0 20px 50px -30px rgba(10,20,19,.3);transition:transform .3s ease,box-shadow .3s ease;color:inherit">
      <div style="position:relative;aspect-ratio:16/11;overflow:hidden"><img loading="lazy" decoding="async" src="{img_path(img)}" alt="{alt}" style="width:100%;height:100%;object-fit:cover">
        <span style="position:absolute;top:14px;left:14px;color:#fff;font-size:11px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;padding:6px 11px;border-radius:999px;background:rgba(34,56,92,.86)">{flag}</span></div>
      <div style="padding:22px 24px 24px">
        <div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap">
          <h3 style="font-family:'Fraunces',serif;font-weight:400;font-size:clamp(22px,2.4vw,30px);margin:0">{name}</h3>
          <div style="font-family:'Fraunces',serif;font-size:21px;color:#C9A45C;white-space:nowrap">{PRICE}<span style="font-size:13px;color:rgba(22,33,31,.5);font-family:'Manrope',sans-serif"> {t('/ nuit', '/ notte', '/ night')}</span></div>
        </div>
        <p style="font-size:15px;line-height:1.6;color:rgba(22,33,31,.66);margin:12px 0 16px">{text}</p>
        <span class="h-link" style="display:inline-flex;align-items:center;gap:8px;font-weight:600;font-size:14.5px;color:#1785C0">{t('Voir la chambre', 'Vedi la camera', 'See the room')}<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>
      </div>
    </a>'''

NAV = [('chambre-double', t('Chambre double', 'Camera doppia', 'Double room')),
       ('chambre-simple', t('Chambre simple', 'Camera singola', 'Single room')),
       ('salle-de-bain', t('La salle de bain', 'Il bagno', 'The bathroom')),
       ('piscine', t('La piscine', 'La piscina', 'The pool')),
       ('bar', t('Le bar', 'Il bar', 'The bar')),
       ('espaces-communs', t('Les espaces communs', 'Gli spazi comuni', 'Shared spaces')),
       ('exterieur', t("L'extérieur", "L'esterno", 'Outside'))]

daynight = f'''
<!-- ===== JOUR / NUIT ===== -->
<section id="jour-nuit" class="theme-am" aria-label="Jour ou nuit" style="background:var(--apt-tint);padding:clamp(48px,6vw,80px) clamp(20px,5vw,64px);border-top:1px solid rgba(22,33,31,.07)">
  <div class="dn-grid" style="max-width:1240px;margin:0 auto">
    <div data-reveal>
      <div style="{EYEBROW}">{t('Visite jour & nuit', 'Visita giorno e notte', 'Day & night tour')}</div>
      <h2 style="{H2}">{t("Visitez l'hôtel ", "Visitate l'hotel ", 'Tour the hotel ')}{em(t('de jour… ou de nuit', 'di giorno… o di notte', 'by day… or by night'))}.</h2>
      <p style="{P};margin:18px 0 26px;max-width:48ch">{t("Un seul geste et tout le site bascule : chaque pièce, la piscine, le bar et l'extérieur s'affichent en photos de jour ou de nuit. Changez de mode quand vous voulez, en haut de page ou dans chaque section.", "Un solo gesto e tutto il sito cambia: ogni stanza, la piscina, il bar e l'esterno appaiono in foto di giorno o di notte. Cambiate modalità quando volete, in alto o in ogni sezione.", "One tap and the whole site switches: every room, the pool, the bar and the outside appear in daytime or night-time photos. Switch whenever you like, at the top of the page or in each section.")}</p>
      {mode_tabs()}
    </div>
    <div data-reveal class="dn-preview">
      <div class="dn-card"><img loading="lazy" decoding="async" src="{img_path('piscine-jour-1375')}" alt="{A}la piscine de jour"><span class="photo-tag">{SUN}{t('Vue de jour', 'Vista di giorno', 'Daytime view')}</span></div>
      <div class="dn-card"><img loading="lazy" decoding="async" src="{img_path('piscine-nuit-6c64ee76')}" alt="{A}la piscine de nuit"><span class="photo-tag">{MOON}{t('Vue de nuit', 'Vista di notte', 'Night view')}</span></div>
    </div>
  </div>
</section>
'''

rooms = f'''
<!-- ===== NOS CHAMBRES ===== -->
<section id="chambres" class="theme-am" aria-label="Nos chambres" style="padding:clamp(64px,9vw,120px) clamp(20px,5vw,64px) clamp(40px,5vw,64px);max-width:1240px;margin:0 auto;scroll-margin-top:76px">
  <div data-reveal style="text-align:center;max-width:720px;margin:0 auto clamp(40px,5vw,64px)">
    <div style="font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:var(--apt-accent);margin-bottom:14px">{t('Nos chambres', 'Le nostre camere', 'Our rooms')}</div>
    <h2 style="font-family:'Fraunces',serif;font-weight:300;font-size:clamp(30px,4vw,54px);line-height:1.06;letter-spacing:-.01em;margin:0 0 14px">{t('15 chambres, ', '15 camere, ', '15 rooms, ')}{em(t('un même confort', 'lo stesso comfort', 'the same comfort'))}.</h2>
    <p style="{P};margin:0">{t("Chambres doubles ou simples, toutes climatisées, avec espace de travail, salle de bain privative, TV et minibar. Wifi Starlink dans tout l'hôtel et groupe électrogène contre les coupures de courant. Un seul tarif de base pour toutes les chambres.", "Camere doppie o singole, tutte climatizzate, con spazio di lavoro, bagno privato, TV e minibar. Wi-Fi Starlink in tutto l'hotel e gruppo elettrogeno contro i blackout. Un'unica tariffa base per tutte le camere.", "Double or single rooms, all air-conditioned, with a workspace, private bathroom, TV and minibar. Starlink Wi-Fi throughout the hotel and a backup generator against power cuts. One base rate for every room.")}</p>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:clamp(20px,3vw,32px)">
    {room_card('chambre-double', 'chambre-double-1363', A + 'chambre double', t('Lit double', 'Letto matrimoniale', 'Double bed'), t('Chambre double', 'Camera doppia', 'Double room'), t("Un grand lit double, des appliques douces et un décor sobre et soigné, pour des nuits au calme.", "Un grande letto matrimoniale, luci soffuse e un arredamento sobrio e curato, per notti tranquille.", "A large double bed, soft wall lights and a clean, carefully designed decor for quiet nights."))}
    {room_card('chambre-simple', 'chambre-simple-1347', A + 'chambre simple', t('Lits simples', 'Letti singoli', 'Single beds'), t('Chambre simple', 'Camera singola', 'Single room'), t("Des lits simples, idéale entre amis, entre collègues ou pour un voyage d'affaires.", "Letti singoli, ideale tra amici, colleghi o per un viaggio di lavoro.", "Single beds, ideal for friends, colleagues or a business trip."))}
  </div>
  <nav class="room-nav" aria-label="Visite détaillée">
    <span class="room-nav-label">{t("Visiter l'hôtel", "Visita l'hotel", 'Tour the hotel')}</span>
    {''.join(f'<a href="#{h}">{l}</a>' for h, l in NAV)}
  </nav>
</section>
'''

sections = ''
sections += room_section('chambre-double', 'chambre-double', t('Chambre double', 'Camera doppia', 'Double room'),
    t('Des nuits ', 'Notti ', 'Nights ') + em(t('au calme', 'tranquille', 'of calm')) + '.',
    t("Grand lit double aux draps blancs, éclairage d'ambiance, climatisation et moustiquaire. La chambre dispose d'un espace de travail, d'une TV, d'un minibar, de rangements et de chaussons à votre arrivée.",
      "Grande letto matrimoniale con lenzuola bianche, luci d'atmosfera, aria condizionata e zanzariera. La camera dispone di spazio di lavoro, TV, minibar, armadi e pantofole al vostro arrivo.",
      "Large double bed with white linen, mood lighting, air conditioning and mosquito net. The room has a workspace, TV, minibar, storage and slippers waiting on arrival."),
    [t('Lit double', 'Letto matrimoniale', 'Double bed'), t('Climatisation', 'Aria condizionata', 'Air conditioning'), t('Espace de travail', 'Spazio di lavoro', 'Workspace'), t('Wifi Starlink', 'Wi-Fi Starlink', 'Starlink Wi-Fi'), t('TV', 'TV', 'TV'), t('Minibar', 'Minibar', 'Minibar'), t('Salle de bain privative', 'Bagno privato', 'Private bathroom')],
    [('chambre-double-1318', A + 'chambre double avec moustiquaire'), ('chambre-double-1363', A + 'le lit double et ses serviettes')],
    [('chambre-double-1319-tv', A + 'chambre double, le lit et la TV'), ('chambre-double-1336', A + 'chambre double, vue d\'ensemble'), ('chambre-double-1334', A + 'la chambre et sa fenêtre'),
     ('chambre-double-1321-tv', A + 'le lit double face à la TV'), ('chambre-double-1323', A + 'le lit double et les appliques'),
     ('chambre-double-1338', A + 'le lit double et les rangements'), ('chambre-double-1320-tv', A + 'la chambre, la TV et le grand dressing'),
     ('chambre-double-1364-tv', A + 'la TV face au lit'), ('chambre-double-1366-tv', A + 'chambre double avec TV'),
     ('chambre-1357', A + 'le bureau et le minibar'), ('chambre-1358', A + 'le minibar et l\'eau offerte'),
     ('chambre-1325', A + 'le dressing'), ('chambre-1360', A + 'les chaussons offerts')],
    False, 'var(--apt-tint)', book_btn('Chambre double', t('Réserver une chambre double', 'Prenota una camera doppia', 'Book a double room')))

sections += room_section('chambre-simple', 'chambre-simple', t('Chambre simple', 'Camera singola', 'Single room'),
    t('Pratique, ', 'Pratica, ', 'Practical, ') + em(t('tout confort', 'tutto comfort', 'fully equipped')) + '.',
    t("Lits simples, climatisation, espace de travail, TV et salle de bain privative : tout le confort de l'hôtel, pour voyager entre amis ou pour le travail.",
      "Letti singoli, aria condizionata, spazio di lavoro, TV e bagno privato: tutto il comfort dell'hotel, per viaggiare tra amici o per lavoro.",
      "Single beds, air conditioning, workspace, TV and private bathroom: all the hotel's comfort, for travelling with friends or for work."),
    [t('Lits simples', 'Letti singoli', 'Single beds'), t('Climatisation', 'Aria condizionata', 'Air conditioning'), t('Espace de travail', 'Spazio di lavoro', 'Workspace'), t('Wifi Starlink', 'Wi-Fi Starlink', 'Starlink Wi-Fi'), t('TV', 'TV', 'TV'), t('Salle de bain privative', 'Bagno privato', 'Private bathroom')],
    [('chambre-simple-1347', A + 'chambre simple, deux lits'), ('chambre-simple-1352-tv', A + 'chambre simple avec TV')],
    [('chambre-simple-1346', A + 'chambre simple, vue d\'ensemble'), ('chambre-simple-1349', A + 'les lits simples'),
     ('chambre-simple-1335-tv', A + 'chambre simple depuis l\'entrée'), ('chambre-simple-1351-tv', A + 'chambre simple et sa fenêtre'),
     ('chambre-simple-1353-tv', A + 'les lits et la TV'), ('chambre-simple-1348-tv', A + 'les lits simples face à la TV'), ('chambre-simple-1354-tv', A + 'chambre simple, la TV et la fenêtre'), ('chambre-simple-1345-tv', A + 'chambre simple depuis l\'entrée'),
     ('chambre-simple-1317', A + 'l\'entrée de la chambre')],
    True, '#ffffff', book_btn('Chambre simple', t('Réserver une chambre simple', 'Prenota una camera singola', 'Book a single room')))

sections += room_section('salle-de-bain', 'salle-de-bain', t('La salle de bain', 'Il bagno', 'The bathroom'),
    t('Moderne et ', 'Moderno e ', 'Modern and ') + em(t('lumineuse', 'luminoso', 'bright')) + '.',
    t("Chaque chambre a sa salle de bain privative : douche à l'italienne derrière une paroi vitrée, vasque posée, meuble en bois et miroir rétroéclairé.",
      "Ogni camera ha il suo bagno privato: doccia a filo pavimento con parete in vetro, lavabo d'appoggio, mobile in legno e specchio retroilluminato.",
      "Every room has its own private bathroom: walk-in shower behind a glass screen, vessel basin, wooden vanity and backlit mirror."),
    [t("Douche à l'italienne", 'Doccia a filo pavimento', 'Walk-in shower'), t('Miroir LED', 'Specchio LED', 'LED mirror'), t('WC', 'WC', 'Toilet'), t('Serviettes fournies', 'Asciugamani forniti', 'Towels provided')],
    [('sdb-1331', A + 'la salle de bain et son miroir rétroéclairé'), ('sdb-1327', A + 'la vasque et la douche')],
    [('sdb-1326', A + 'la salle de bain, vue d\'ensemble'), ('sdb-1328', A + "la douche à l'italienne"),
     ('sdb-1330', A + 'le miroir LED et les étagères'), ('sdb-1329', A + 'la vasque posée')],
    False, 'var(--apt-tint)')

sections += room_section('piscine', 'piscine', t('La piscine', 'La piscina', 'The pool'),
    t('Le jour au soleil, ', 'Di giorno al sole, ', 'Sunny by day, ') + em(t('le soir illuminée', 'di sera illuminata', 'lit up at night')) + '.',
    t("Une grande piscine entourée d'un deck en bois, de transats et de parasols. Le soir, elle s'illumine et devient le cœur de l'hôtel, juste à côté du bar.",
      "Una grande piscina circondata da un deck in legno, lettini e ombrelloni. La sera si illumina e diventa il cuore dell'hotel, proprio accanto al bar.",
      "A large pool surrounded by a wooden deck, sun loungers and parasols. In the evening it lights up and becomes the heart of the hotel, right next to the bar."),
    [t('Deck en bois', 'Deck in legno', 'Wooden deck'), t('Transats & parasols', 'Lettini e ombrelloni', 'Loungers & parasols'), t('Éclairage de nuit', 'Illuminazione notturna', 'Night lighting'), t('À côté du bar', 'Accanto al bar', 'Next to the bar')],
    [('piscine-jour-1376', A + 'la piscine en journée'), ('piscine-jour-1375', A + 'la piscine et le deck en bois')],
    [('piscine-jour-1372', A + 'la piscine et la vue sur la campagne'), ('piscine-jour-1374', A + 'les transats au bord de la piscine'),
     ('piscine-jour-1378', A + "la piscine au pied de l'hôtel")],
    True, '#ffffff',
    night=([('piscine-nuit-1215', A + 'la piscine illuminée le soir'), ('piscine-nuit-6c64ee76', A + 'la piscine et les parasols le soir')],
           [('piscine-nuit-1f7798e9', A + 'la piscine de nuit'), ('piscine-nuit-1216', A + 'la piscine illuminée'),
            ('piscine-nuit-7b17d2d7', A + 'la piscine et la façade la nuit'), ('piscine-nuit-c8eb0b7d', A + 'le bassin illuminé'),
            ('piscine-nuit-1273db16', A + 'la terrasse de la piscine le soir'), ('piscine-nuit-1219', A + "le coin détente et le logo de l'hôtel")]))

sections += room_section('bar', 'bar', t('Le bar', 'Il bar', 'The bar'),
    t('Un verre ', 'Un drink ', 'A drink ') + em(t('au bord de l\'eau', 'a bordo piscina', 'by the pool')) + '.',
    t("Face à la piscine, le bar vous accueille pour un cocktail, avec ou sans alcool, en fin de journée ou à la tombée de la nuit.",
      "Di fronte alla piscina, il bar vi accoglie per un cocktail, alcolico o analcolico, a fine giornata o al calar della sera.",
      "Facing the pool, the bar welcomes you for a cocktail, with or without alcohol, at the end of the day or as night falls."),
    [t('Face à la piscine', 'Fronte piscina', 'Poolside'), t('Cocktails', 'Cocktail', 'Cocktails'), t('Cocktails sans alcool', 'Cocktail analcolici', 'Mocktails')],
    [('bar-1380', A + 'le comptoir du bar en journée'), ('bar-1379', A + 'les tabourets du bar')],
    [('piscine-jour-1378', A + "le bar au pied de l'hôtel, face à la piscine")],
    False, 'var(--apt-tint)',
    night=([('piscine-nuit-1222', A + 'le bar le soir, face à la piscine'), ('bar-1236', A + 'le comptoir du bar le soir')],
           [('piscine-nuit-1220', A + 'le bar au bout de la piscine'), ('piscine-nuit-1224', A + 'le bar illuminé'),
            ('piscine-nuit-1226', A + 'le bar et la terrasse la nuit'), ('piscine-nuit-1227', A + 'le bar et son enseigne'),
            ('bar-1232', A + 'la carte des cocktails')]))

sections += room_section('espaces-communs', 'espaces-communs', t('Les espaces communs', 'Gli spazi comuni', 'Shared spaces'),
    t('Un accueil ', 'Un\'accoglienza ', 'A ') + em(t('soigné', 'curata', 'warm welcome')) + '.',
    t("Une réception pour vous accueillir, des couloirs lumineux décorés avec goût et une terrasse ouverte sur les collines de Nosy Be.",
      "Una reception per accogliervi, corridoi luminosi decorati con gusto e una terrazza aperta sulle colline di Nosy Be.",
      "A reception desk to welcome you, bright tastefully decorated corridors and a terrace open to the hills of Nosy Be."),
    [t('Réception', 'Reception', 'Reception'), t('Terrasse', 'Terrazza', 'Terrace'), t('Décoration soignée', 'Arredamento curato', 'Stylish decor')],
    [('espaces-1314', A + 'la réception'), ('espaces-1368', A + 'la terrasse ouverte sur les collines')],
    [('espaces-1373', A + 'le mur « Smile » dans les parties communes')],
    True, '#ffffff',
    night=([('espaces-9da1ee24', A + 'le couloir et sa décoration le soir'), ('espaces-497c9e03', A + 'le salon extérieur le soir')], []))

sections += room_section('exterieur', 'exterieur', t("L'extérieur", "L'esterno", 'Outside'),
    t('Un hôtel ', 'Un hotel ', 'A ') + em(t('neuf et sécurisé', 'nuovo e protetto', 'new, enclosed hotel')) + '.',
    t("Un bâtiment récent dans une propriété close, avec allées paysagées et parking dans l'enceinte. Le soir, la façade s'illumine.",
      "Un edificio recente in una proprietà recintata, con vialetti curati e parcheggio interno. La sera la facciata si illumina.",
      "A recent building on an enclosed property, with landscaped paths and on-site parking. At night the facade lights up."),
    [t('Propriété close', 'Proprietà recintata', 'Enclosed property'), t('Parking', 'Parcheggio', 'Parking'), t('Allées paysagées', 'Vialetti curati', 'Landscaped paths')],
    [('exterieur-1381', A + "l'allée paysagée en journée"), ('exterieur-1384', A + "l'allée le long de l'hôtel")],
    [('exterieur-1382', A + "le parking dans l'enceinte")],
    False, 'var(--apt-tint)',
    night=([('exterieur-1240', A + "la façade de l'hôtel le soir"), ('exterieur-1238', A + "la façade et l'allée éclairée")],
           [('exterieur-1239', A + 'la façade de nuit'), ('exterieur-1242', A + "l'hôtel illuminé")]))

TF_SEL = json.load(open('/private/tmp/claude-501/-Users-christopher-rentanoo/6fa53245-17be-4c66-889d-fd2899d22144/scratchpad/tf-selection.json', encoding='utf-8')) if os.path.exists('/private/tmp/claude-501/-Users-christopher-rentanoo/6fa53245-17be-4c66-889d-fd2899d22144/scratchpad/tf-selection.json') else json.load(open(os.path.join(OUT, '.tf-selection.json'), encoding='utf-8'))
TF_NAMES = {'Kebab (ou assiette)': 'Kebab', 'Reine': 'Pizza Reine', 'Le patron': 'Burger Le Patron', 'Tacos': 'Tacos XL'}
def tf_course(k):
    return (t('Entrée', 'Antipasto', 'Starter') if k < 6 else t('Plat', 'Piatto', 'Main') if k < 15 else t('Dessert', 'Dessert', 'Dessert'))
def tf_item(k, o, dup=False):
    nm = TF_NAMES.get(o['name'], o['name']); price = f"{o['price']:,}".replace(',', '&nbsp;') + '&nbsp;Ar'
    hid = ' aria-hidden="true" tabindex="-1"' if dup else ''
    return (f'<a class="tf-item" href="https://taxifoodnosybe.distripro207.com/" target="_blank" rel="noopener"{hid}>'
            f'<span class="tf-ph"><img loading="lazy" decoding="async" src="{img_path(o["slug"])}" alt="{"" if dup else nm + " — " + o["resto"]}" width="640" height="640"><span class="tf-course">{tf_course(k)}</span></span>'
            f'<span class="tf-name">{nm}</span><span class="tf-meta"><span>{o["resto"]}</span><strong>{price}</strong></span></a>')
tf_items = ''.join(tf_item(k, o) for k, o in enumerate(TF_SEL)) + ''.join(tf_item(k, o, True) for k, o in enumerate(TF_SEL))

taxifood = f"""
<!-- ===== TAXI FOOD ===== -->
<section id="taxi-food" aria-label="Taxi Food, livraison de repas" style="background:#ffffff;padding:clamp(48px,6vw,80px) clamp(20px,5vw,64px);scroll-margin-top:76px;border-top:1px solid rgba(22,33,31,.07)">
  <div data-reveal class="tf-card">
    <img class="tf-logo" src="{img_path('taxifood-logo')}" width="256" height="256" alt="Logo Taxi Food Nosy Be" loading="lazy" decoding="async">
    <div class="tf-body">
      <div class="tf-eyebrow">{t('Taxi Food · Livraison à Nosy Be', 'Taxi Food · Consegna a Nosy Be', 'Taxi Food · Delivery in Nosy Be')}</div>
      <h2 class="tf-title">{t('Entrée, plat, dessert ? ', 'Antipasto, piatto, dessert? ', 'Starter, main, dessert? ')}<span>{t('Faites-vous livrer.', 'Fateveli consegnare.', 'Get it delivered.')}</span></h2>
      <p class="tf-text">{t("Foie gras poêlé, carpaccio de zébu, marmite du pêcheur, kebab, tacos, crème brûlée… Avec Taxi Food, commandez chez Chez Bidul & Truc et La Cabane et faites-vous livrer directement à l'hôtel.", "Foie gras in padella, carpaccio di zebù, zuppa del pescatore, kebab, tacos, crème brûlée… Con Taxi Food ordinate da Chez Bidul & Truc e La Cabane e fatevi consegnare direttamente in hotel.", "Pan-seared foie gras, zebu carpaccio, fisherman's stew, kebab, tacos, crème brûlée… With Taxi Food, order from Chez Bidul & Truc and La Cabane and get it delivered straight to the hotel.")}</p>
      <a class="tf-cta" href="https://taxifoodnosybe.distripro207.com/" target="_blank" rel="noopener">{t('Commander sur Taxi Food', 'Ordina su Taxi Food', 'Order on Taxi Food')}</a>
    </div>
    <div class="tf-marquee" aria-label="{t('20 plats à se faire livrer', '20 piatti da farsi consegnare', '20 dishes to get delivered')}">
      <div class="tf-track">{tf_items}</div>
    </div>
    <p class="tf-foot">{t('Prix indicatifs de la carte Taxi Food, hors frais de livraison.', 'Prezzi indicativi del menu Taxi Food, consegna esclusa.', 'Indicative Taxi Food menu prices, delivery not included.')}</p>
  </div>
</section>
"""

def lieu_row(label, value, last=False):
    bb = 'border-bottom:1px solid rgba(22,33,31,.1);' if last else ''
    return f'<div style="display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 0;border-top:1px solid rgba(22,33,31,.1);{bb}"><span style="font-size:15.5px;font-weight:500">{label}</span><span style="font-family:\'Fraunces\',serif;font-size:18px;color:#22385C">{value}</span></div>'

lieu = f'''
<!-- ===== LE LIEU ===== -->
<section id="lieu" aria-label="Le lieu" style="padding:clamp(64px,9vw,120px) clamp(20px,5vw,64px);max-width:1240px;margin:0 auto;scroll-margin-top:76px">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:clamp(32px,5vw,72px);align-items:center">
    <div data-reveal style="position:relative;border-radius:10px;overflow:hidden;background:#e6f0ef;aspect-ratio:5/4;border:1px solid rgba(22,33,31,.08)">
      <iframe title="AM Résidence sur la carte" src="https://maps.google.com/maps?q={LAT},{LNG}&z=14&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" style="position:absolute;inset:0;width:100%;height:100%;border:0"></iframe>
      <a href="{MAPS}" target="_blank" rel="noopener" style="position:absolute;left:16px;bottom:14px;display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:600;color:#16211F;background:#fff;padding:9px 14px;border-radius:999px;box-shadow:0 4px 14px -4px rgba(10,20,19,.35)"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#C9A45C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21c5-6 8-9 8-12a8 8 0 1 0-16 0c0 3 3 6 8 12Z"/><circle cx="12" cy="9" r="2.5"/></svg>{t('Voir sur Google Maps', 'Vedi su Google Maps', 'View on Google Maps')}</a>
    </div>
    <div data-reveal>
      <div style="font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:#22385C;margin-bottom:14px">{t('Le lieu', 'Il luogo', 'The location')}</div>
      <h2 style="font-family:'Fraunces',serif;font-weight:300;font-size:clamp(28px,3.6vw,48px);line-height:1.08;letter-spacing:-.01em;margin:0 0 18px">{t('À Djabala, aux portes de Hell-Ville.', 'A Djabala, alle porte di Hell-Ville.', 'In Djabala, on the edge of Hell-Ville.')}</h2>
      <p style="font-size:16px;line-height:1.65;color:rgba(22,33,31,.68);margin:0 0 30px;max-width:46ch">{t("Dans le quartier calme de Djabala, à quelques minutes du centre de Hell-Ville, la capitale de Nosy Be : son port, son marché, ses restaurants. Idéal pour explorer toute l'île.", "Nel tranquillo quartiere di Djabala, a pochi minuti dal centro di Hell-Ville, la capitale di Nosy Be: il porto, il mercato, i ristoranti. Ideale per esplorare tutta l'isola.", "In the quiet Djabala neighbourhood, a few minutes from central Hell-Ville, Nosy Be's main town: its harbour, market and restaurants. Ideal for exploring the whole island.")}</p>
      <div style="display:flex;flex-direction:column">
        {lieu_row(t('Centre de Hell-Ville & port', 'Centro di Hell-Ville e porto', 'Hell-Ville centre & harbour'), t('~5 min', '~5 min', '~5 min'))}
        {lieu_row(t("Plage d'Ambatoloaka", 'Spiaggia di Ambatoloaka', 'Ambatoloaka beach'), t('~10 min', '~10 min', '~10 min'))}
        {lieu_row(t('Aéroport de Fascène', 'Aeroporto di Fascène', 'Fascène airport'), t('~20 min', '~20 min', '~20 min'), last=True)}
      </div>
      <p style="font-size:12.5px;color:rgba(22,33,31,.5);margin:14px 0 0">{t('Temps indicatifs en voiture.', 'Tempi indicativi in auto.', 'Approximate driving times.')}</p>
    </div>
  </div>
</section>
'''

def check_item(label):
    return f'<div style="display:flex;align-items:center;gap:10px;font-size:15px;color:rgba(251,251,249,.85)">{CHECK}{label}</div>'

tarif = f'''
<!-- ===== LE TARIF ===== -->
<section id="tarif" aria-label="Le tarif" style="background:#16211F;color:#ffffff;padding:clamp(64px,9vw,120px) clamp(20px,5vw,64px)">
  <div style="max-width:1080px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:clamp(36px,5vw,72px);align-items:center">
    <div data-reveal>
      <div style="font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:#C9A45C;margin-bottom:16px">{t('Le tarif', 'La tariffa', 'Rate')}</div>
      <div style="font-family:'Fraunces',serif;font-weight:300;font-size:clamp(46px,7vw,84px);line-height:.95;letter-spacing:-.02em;color:#E9CE8E;white-space:nowrap">{PRICE}</div>
      <div style="font-size:16px;color:rgba(251,251,249,.6);margin-top:10px">{t('la nuit · prix de base, chambre double ou simple', 'a notte · prezzo base, camera doppia o singola', 'per night · base rate, double or single room')}</div>
      <div style="height:1px;background:rgba(251,251,249,.14);margin:30px 0"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px 24px">
        {check_item(t('Climatisation', 'Aria condizionata', 'Air conditioning'))}
        {check_item(t('Wifi Starlink', 'Wi-Fi Starlink', 'Starlink Wi-Fi'))}
        {check_item(t('Espace de travail', 'Spazio di lavoro', 'Workspace'))}
        {check_item(t('Groupe électrogène', 'Gruppo elettrogeno', 'Backup generator'))}
        {check_item(t('Accès piscine', 'Accesso piscina', 'Pool access'))}
        {check_item(t('Parking', 'Parcheggio', 'Parking'))}
      </div>
    </div>
    <div data-reveal style="background:rgba(251,251,249,.05);border:1px solid rgba(251,251,249,.1);border-radius:14px;padding:clamp(26px,3vw,38px)">
      <h3 style="font-family:'Fraunces',serif;font-weight:400;font-size:clamp(22px,2.4vw,30px);line-height:1.14;margin:0 0 12px">{t('Réservez en direct, au meilleur tarif.', 'Prenotate direttamente, alla migliore tariffa.', 'Book direct, at the best rate.')}</h3>
      <p style="font-size:15px;line-height:1.6;color:rgba(251,251,249,.68);margin:0 0 24px">{t("En nous écrivant directement, vous obtenez le meilleur prix, une réponse rapide et de vrais conseils pour votre séjour.", "Scrivendoci direttamente ottenete il miglior prezzo, una risposta rapida e veri consigli per il vostro soggiorno.", "Writing to us directly gets you the best price, a quick reply and real advice for your stay.")}</p>
      <a href="#contact" class="h-cta" style="display:flex;align-items:center;justify-content:center;gap:10px;padding:16px 24px;border-radius:999px;background:#1785C0;color:#fff;font-weight:600;font-size:16px;transition:background .25s ease,transform .25s ease">{CHAT}{t('Écrire sur WhatsApp', 'Scrivici su WhatsApp', 'Message us on WhatsApp')}</a>
      <a href="#reservation" style="display:flex;align-items:center;justify-content:center;gap:9px;margin-top:10px;padding:13px;border-radius:10px;border:1px solid rgba(233,206,142,.6);background:rgba(233,206,142,.1);color:#fff;font-size:14px;font-weight:600">{t('Demander mes dates', 'Richiedi le mie date', 'Request my dates')}</a>
      <!-- À COMPLÉTER : liens Rentanoo / Booking / Airbnb de l'hôtel dès qu'ils existent -->
    </div>
  </div>
</section>
'''

reservation = f'''
<!-- ===== DEMANDE DE RÉSERVATION ===== -->
<section id="reservation" aria-label="Demande de réservation" style="background:#22385C;color:#fff;padding:clamp(64px,9vw,110px) clamp(20px,5vw,64px);scroll-margin-top:72px">
  <div style="max-width:760px;margin:0 auto">
    <div data-reveal style="text-align:center;margin-bottom:clamp(26px,4vw,40px)">
      <div style="font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:#E9CE8E;margin-bottom:14px">{t('Réservation', 'Prenotazione', 'Booking')}</div>
      <h2 style="font-family:'Fraunces',serif;font-weight:300;font-size:clamp(30px,4.4vw,54px);line-height:1.05;letter-spacing:-.01em;margin:0 0 14px;color:#fff">{t('Demandez vos dates', 'Richiedete le vostre date', 'Request your dates')}</h2>
      <p style="font-size:16px;line-height:1.6;color:rgba(251,251,249,.75);margin:0 auto;max-width:52ch">{t("Choisissez vos dates et laissez-nous vos coordonnées : on revient vers vous très vite pour confirmer les disponibilités.", "Scegliete le date e lasciateci i vostri contatti: vi ricontattiamo molto presto per confermare la disponibilità.", "Pick your dates and leave your details: we'll get back to you very quickly to confirm availability.")}</p>
    </div>
    <form id="resa-form" data-reveal novalidate style="background:#ffffff;color:#16211F;border-radius:16px;padding:clamp(22px,3.5vw,38px);box-shadow:0 30px 70px -30px rgba(0,0,0,.5)">
      <div class="resa-grid">
        <label class="resa-field" style="grid-column:1/-1"><span>{t('Chambre', 'Camera', 'Room')}</span>
          <select id="resa-logement" name="logement">
            <option value="Chambre double">{t('Chambre double · 500 000 Ar / nuit', 'Camera doppia · 500 000 Ar / notte', 'Double room · 500,000 Ar / night')}</option>
            <option value="Chambre simple">{t('Chambre simple · 500 000 Ar / nuit', 'Camera singola · 500 000 Ar / notte', 'Single room · 500,000 Ar / night')}</option>
            <option value="Plusieurs chambres">{t('Plusieurs chambres (groupe)', 'Più camere (gruppo)', 'Several rooms (group)')}</option>
          </select>
        </label>
        <label class="resa-field"><span>{t('Arrivée', 'Arrivo', 'Check-in')}</span><input type="date" name="arrivee" required></label>
        <label class="resa-field"><span>{t('Départ', 'Partenza', 'Check-out')}</span><input type="date" name="depart" required></label>
        <label class="resa-field"><span>{t('Prénom', 'Nome', 'First name')}</span><input name="prenom" autocomplete="given-name" required></label>
        <label class="resa-field"><span>{t('Nom', 'Cognome', 'Last name')}</span><input name="nom" autocomplete="family-name" required></label>
        <label class="resa-field"><span>{t('Téléphone', 'Telefono', 'Phone')}</span><input type="tel" name="telephone" autocomplete="tel" required></label>
        <label class="resa-field"><span>{t('E-mail', 'E-mail', 'Email')}</span><input type="email" name="email" autocomplete="email" required></label>
        <label class="resa-field" style="grid-column:1/-1"><span>{t('Message (optionnel)', 'Messaggio (facoltativo)', 'Message (optional)')}</span><textarea name="message" rows="3"></textarea></label>
      </div>
      <button type="submit" class="resa-submit">{t('Envoyer ma demande', 'Invia la richiesta', 'Send my request')}</button>
      <p id="resa-msg" role="status" aria-live="polite" style="margin:14px 0 0;font-size:14.5px;text-align:center"></p>
      <p style="margin:12px 0 0;font-size:12.5px;color:rgba(22,33,31,.5);text-align:center">{t('Gratuit et sans engagement · réponse rapide en direct', 'Gratuito e senza impegno · risposta rapida', 'Free, no commitment · quick direct reply')}</p>
    </form>
  </div>
</section>
'''

contact = f'''
<!-- ===== CTA FINAL ===== -->
<section id="contact" aria-label="Contact" style="position:relative;min-height:78vh;display:flex;align-items:center;overflow:hidden">
  <div style="position:absolute;inset:0;z-index:0">
    <img class="slot" loading="lazy" decoding="async" src="{img_path('piscine-jour-1374')}" data-day="{img_path('piscine-jour-1374')}" data-night="{img_path('piscine-nuit-1f7798e9')}" alt="{A}la piscine">
    <div style="position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,rgba(10,20,19,.84) 0%,rgba(10,20,19,.52) 55%,rgba(10,20,19,.22) 100%)"></div>
  </div>
  <div data-reveal style="position:relative;z-index:2;padding:clamp(48px,7vw,96px) clamp(20px,5vw,64px);max-width:1240px;margin:0 auto;width:100%;color:#fff">
    <div style="max-width:640px">
      <h2 style="font-family:'Fraunces',serif;font-weight:300;font-size:clamp(36px,5.5vw,76px);line-height:1.03;letter-spacing:-.015em;margin:0 0 20px">{t('Votre base pour découvrir Nosy Be.', 'La vostra base per scoprire Nosy Be.', 'Your base to discover Nosy Be.')}</h2>
      <p style="font-size:clamp(16px,1.5vw,19px);line-height:1.55;color:rgba(255,255,255,.88);margin:0 0 34px;max-width:48ch">{t('Écrivez-nous vos dates. On vous répond vite, avec de vrais conseils pour votre séjour.', 'Scriveteci le vostre date. Rispondiamo in fretta, con veri consigli per il vostro soggiorno.', "Send us your dates. We'll reply quickly, with real advice for your stay.")}</p>
      <div style="display:flex;flex-wrap:wrap;align-items:center;gap:14px 18px">
        <a href="#contact" class="h-cta" style="display:inline-flex;align-items:center;gap:11px;padding:17px 30px;border-radius:999px;background:#1785C0;color:#fff;font-weight:600;font-size:16.5px;box-shadow:0 18px 42px -16px rgba(10,20,19,.5);transition:background .25s ease,transform .25s ease">{CHAT}{t('Écrire sur WhatsApp', 'Scrivici su WhatsApp', 'Message us on WhatsApp')}</a>
        <a href="#reservation" class="h-chip3" style="display:inline-flex;align-items:center;gap:9px;padding:16px 26px;border-radius:999px;border:1px solid rgba(255,255,255,.42);color:#fff;font-weight:600;font-size:15.5px;transition:border-color .25s ease">{t('Demander mes dates', 'Richiedi le mie date', 'Request my dates')}</a>
      </div>
      <div style="margin-top:18px;font-size:13px;color:rgba(255,255,255,.75)">{t('Ou par e-mail : ', 'Oppure via e-mail: ', 'Or by email: ')}<a href="mailto:chrisrentanoo@gmail.com" style="color:#fff;text-decoration:underline">chrisrentanoo@gmail.com</a></div>
    </div>
  </div>
</section>
'''

# Partenaire + footer : repris du gabarit, adapté
partner = src[src.index('<!-- ===== ⑨ PARTENAIRE + FOOTER ===== -->'): src.index('<div id="apt-badge"')]
partner = partner.replace('<img src="images/logo-color-v2.webp" alt="Lune de Miel & Clair de Lune" width="300" height="300" style="height:82px;width:auto;display:block;margin-bottom:12px">',
                          '<div class="wordmark" style="color:#22385C;margin-bottom:12px"><span class="wm-mono">AM</span><span class="wm-name">Résidence</span></div>')
partner = partner.replace('Andilana · Nosy Be · Madagascar', 'Djabala · Hell-Ville · Nosy Be')
partner = re.sub(r'\s*<a href="https://www.facebook.com/profile.php[^\n]*Facebook</a>', '', partner)
partner = partner.replace('villalunedemiel.rentanoo.com', 'amresidence.rentanoo.com')
partner = partner.replace('<a href="#logements" class="h-flink">Les logements</a>', f'<a href="#chambres" class="h-flink">{t("Les chambres", "Le camere", "The rooms")}</a>')
partner = partner.replace("© 2026 · Andilana, les pieds dans l'eau. Tous droits réservés.", '© 2026 · AM Résidence, Hell-Ville. Tous droits réservés.')
partner = partner.replace('</div>\n\n', '\n', 1) if False else partner
used.add('rentanoo-logo.webp')
t('Partenaire local', 'Partner locale', 'Local partner')
t('Ton séjour facilité par Rentanoo.', 'Il tuo soggiorno semplificato da Rentanoo.', 'Your stay made easy by Rentanoo.')
t('Découvrir Rentanoo', 'Scopri Rentanoo', 'Discover Rentanoo')
t('Contact', 'Contatti', 'Contact')
t('Mentions légales', 'Note legali', 'Legal notice')
t('Partager sur Facebook', 'Condividi su Facebook', 'Share on Facebook')
t('Site propulsé par', 'Sito realizzato da', 'Powered by')
t('© 2026 · AM Résidence, Hell-Ville. Tous droits réservés.', '© 2026 · AM Résidence, Hell-Ville. Tutti i diritti riservati.', '© 2026 · AM Résidence, Hell-Ville. All rights reserved.')
t("La plateforme locale de Nosy Be : location de véhicules (scooters, motos, quads, voitures, 4×4), hébergements, excursions & activités et transferts aéroport. De quoi organiser tout ton séjour au même endroit.",
  "La piattaforma locale di Nosy Be: noleggio veicoli (scooter, moto, quad, auto, 4×4), alloggi, escursioni e attività e transfer aeroportuali. Tutto il soggiorno in un solo posto.",
  "Nosy Be's local platform: vehicle rental (scooters, motorbikes, quads, cars, 4×4s), accommodation, excursions & activities and airport transfers. Your whole stay in one place.")
for a, b, c in [('Scooters & motos', 'Scooter e moto', 'Scooters & motorbikes'), ('Quads', 'Quad', 'Quads'), ('Voitures & 4×4', 'Auto e 4×4', 'Cars & 4×4s'),
                ('Hébergements', 'Alloggi', 'Accommodation'), ('Excursions & activités', 'Escursioni e attività', 'Excursions & activities'), ('Transferts aéroport', 'Transfer aeroporto', 'Airport transfers')]:
    t(a, b, c)
t('Voir plus de photos', 'Vedi altre foto', 'See more photos')

header = f'''
<!-- ===== HEADER ===== -->
<header id="site-header" style="position:fixed;top:0;left:0;right:0;z-index:50;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:18px clamp(20px,5vw,64px);transition:background .4s ease,box-shadow .4s ease,padding .4s ease,color .4s ease;color:#fff">
  <a id="brand-home" href="#" class="wordmark" aria-label="AM Résidence — accueil" style="color:inherit"><span class="wm-mono">AM</span><span class="wm-name">Résidence</span><span id="wm-sub" class="wm-sub">Hell-Ville · Nosy Be</span></a>
  <div style="display:flex;align-items:center;gap:clamp(10px,2vw,18px)">
    <div id="lang-switch" style="display:flex;align-items:center;gap:3px;font-family:'Manrope',sans-serif;font-size:12px;font-weight:600;letter-spacing:.1em">
      <button type="button" class="lang-btn" data-lang="fr" aria-label="Français">FR</button>
      <span class="lang-sep">·</span>
      <button type="button" class="lang-btn" data-lang="it" aria-label="Italiano">IT</button>
      <span class="lang-sep">·</span>
      <button type="button" class="lang-btn" data-lang="en" aria-label="English">EN</button>
    </div>
    <div id="mode-switch" class="mode-switch" role="group" aria-label="Jour / nuit"><button type="button" class="ms-day" data-set-mode="day" aria-label="Mode jour" title="Mode jour">{SUN}</button><button type="button" class="ms-night" data-set-mode="night" aria-label="Mode nuit" title="Mode nuit">{MOON}</button></div>
    <a href="#reservation" id="nav-book" class="h-navcta" style="display:inline-flex;align-items:center;gap:8px;padding:11px 20px;border-radius:999px;background:#1785C0;color:#fff;font-weight:600;font-size:14px;white-space:nowrap;transition:background .25s ease,transform .25s ease">{t('Réserver', 'Prenota', 'Book')}</a>
  </div>
</header>
'''

hero = f'''
<!-- ===== HERO ===== -->
<section aria-label="Hero" style="position:relative;min-height:100svh;display:flex;flex-direction:column;justify-content:flex-end;padding:0">
  <div style="position:absolute;inset:0;overflow:hidden;z-index:0">
    <div class="hero-carousel" id="hero-carousel">
{hero_slides}
    </div>
    <div style="position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,rgba(9,20,38,.25) 0%,rgba(9,20,38,0) 30%,rgba(9,20,38,.25) 58%,rgba(9,20,38,.72) 100%)"></div>
  </div>
  <div class="hero-dots" id="hero-dots" role="tablist" aria-label="Photos de l'hôtel">
{hero_dots}
  </div>
  <div style="position:relative;z-index:2;padding:0 clamp(20px,5vw,64px) clamp(40px,7vh,84px);max-width:1240px;width:100%;margin:0 auto">
    <div style="color:#fff;max-width:860px;text-shadow:0 2px 8px rgba(9,20,38,.42),0 1px 30px rgba(9,20,38,.5)">
      <div style="font-size:12.5px;letter-spacing:.26em;text-transform:uppercase;color:#E9CE8E;margin-bottom:18px;animation:riseIn .9s .15s ease both">{t('Hôtel · 15 chambres · Nosy Be', 'Hotel · 15 camere · Nosy Be', 'Hotel · 15 rooms · Nosy Be')}</div>
      <h1 id="hero-title" style="font-family:'Fraunces',serif;font-weight:300;font-size:clamp(40px,6.2vw,90px);line-height:1.02;letter-spacing:-.015em;margin:0;animation:riseIn .9s .28s ease both"></h1>
      <div style="display:inline-flex;align-items:center;gap:11px;margin:24px 0 36px;font-size:clamp(14px,1.4vw,17px);color:rgba(255,255,255,.92);animation:riseIn .9s .4s ease both"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#E9CE8E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" style="flex:none">{ICON['pin']}</svg>{t('Djabala, à 5 minutes du centre de Hell-Ville', 'Djabala, a 5 minuti dal centro di Hell-Ville', 'Djabala, 5 minutes from central Hell-Ville')}</div>
      <div style="animation:riseIn .9s .6s ease both">
        <div style="display:flex;flex-wrap:wrap;align-items:center;gap:16px 20px">
          <a href="#reservation" class="h-book" style="display:inline-flex;align-items:center;gap:11px;padding:17px 30px;border-radius:999px;background:#1785C0;color:#fff;font-weight:600;font-size:16.5px;box-shadow:0 18px 42px -16px rgba(10,20,19,.5);transition:background .25s ease,transform .25s ease">{t('Demander mes dates', 'Richiedi le mie date', 'Request my dates')}</a>
          <a href="#contact" class="h-cta" style="display:inline-flex;align-items:center;gap:9px;color:#fff;font-weight:600;font-size:15.5px;padding:14px 6px;border-bottom:1px solid rgba(255,255,255,.35);background:none;transition:border-color .25s ease">{t('Écrire sur WhatsApp', 'Scrivici su WhatsApp', 'Message us on WhatsApp')}</a>
        </div>
        <div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;margin-top:18px;font-size:13.5px;color:rgba(255,255,255,.85)">
          <span style="display:inline-flex;align-items:center;gap:7px">{CHECK}{t('Dès 500 000 Ar la nuit · réponse rapide · contact humain', 'Da 500 000 Ar a notte · risposta rapida · contatto umano', 'From 500,000 Ar a night · quick reply · real people')}</span>
        </div>
      </div>
    </div>
  </div>
  <div style="position:absolute;left:50%;bottom:22px;transform:translateX(-50%);z-index:2;pointer-events:none">
    <div style="width:22px;height:36px;border:1.5px solid rgba(255,255,255,.55);border-radius:12px;display:flex;justify-content:center;padding-top:7px"><span style="width:3px;height:7px;border-radius:2px;background:#fff;animation:scrollDot 1.9s ease-in-out infinite"></span></div>
  </div>
</section>
'''

# ---------- CSS ----------
css_am = css
css_am += '''
  /* ===== AM Résidence : identité bleu nuit + or ===== */
  .theme-am{--apt-accent:#22385C;--apt-accent-2:#C9A45C;--apt-soft:rgba(34,56,92,.07);--apt-line:rgba(34,56,92,.22);--apt-tint:#f6f5f1}
  .theme-am .lm-spec{background:var(--apt-soft);border-color:var(--apt-line)}
  .theme-am .lm-spec::before{background:var(--apt-accent-2)}
  .theme-am .room-nav a{border-color:var(--apt-line)}
  .theme-am .room-nav a:hover{background:var(--apt-soft);border-color:var(--apt-accent)}
  .theme-am .room-nav a::after,.theme-am .room-more .n{color:var(--apt-accent-2)}
  .theme-am .room-more:hover{border-color:var(--apt-accent);background:var(--apt-soft)}
  .wordmark{display:inline-flex;align-items:baseline;gap:9px;text-decoration:none;line-height:1}
  .wm-mono{font-family:'Fraunces',serif;font-weight:500;font-size:clamp(24px,2.6vw,30px);letter-spacing:.04em;color:#C9A45C}
  .wm-name{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(20px,2.2vw,25px);letter-spacing:.01em}
  .wm-sub{font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;opacity:.8;margin-left:6px}
  #site-header .wordmark:hover{color:inherit}
  @media (max-width:1024px){.wm-sub{display:none}}
  /* ===== Carrousel Taxi Food ===== */
  .tf-card{flex-wrap:wrap;overflow:hidden}
  .tf-card .tf-body{flex:1 1 320px;min-width:0}
  .tf-marquee{flex:0 0 100%;width:100%;min-width:0;position:relative;overflow:hidden;margin-top:clamp(4px,1vw,10px);padding:6px 0 4px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent);mask-image:linear-gradient(90deg,transparent,#000 6%,#000 94%,transparent)}
  .tf-track{display:flex;gap:16px;width:max-content;animation:tfScroll 75s linear infinite}
  .tf-marquee:hover .tf-track,.tf-marquee:focus-within .tf-track{animation-play-state:paused}
  @keyframes tfScroll{from{transform:translateX(0)}to{transform:translateX(calc(-50% - 8px))}}
  .tf-item{flex:none;width:clamp(160px,15vw,196px);display:flex;flex-direction:column;border-radius:16px;overflow:hidden;background:#fff;border:1px solid rgba(232,52,42,.14);box-shadow:0 16px 36px -26px rgba(10,20,19,.45);color:#16211F;text-decoration:none;transition:transform .3s ease,box-shadow .3s ease}
  .tf-item:hover{transform:translateY(-4px);box-shadow:0 22px 44px -24px rgba(232,52,42,.45);color:#16211F}
  .tf-ph{position:relative;display:block;aspect-ratio:1/1;background:radial-gradient(circle at 50% 40%,#fff8ee,#f4e6d2)}
  .tf-ph img{width:100%;height:100%;object-fit:cover;display:block}
  .tf-course{position:absolute;top:10px;left:10px;padding:5px 10px;border-radius:999px;background:linear-gradient(90deg,#E8342A,#FF8A1E);color:#FFFFFF;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
  .tf-name{display:block;padding:10px 12px 2px;font-family:'Fraunces',serif;font-size:15.5px;line-height:1.2;text-align:left}
  .tf-meta{display:flex;flex-direction:column;align-items:flex-start;gap:2px;padding:2px 12px 12px;font-size:12px;text-align:left;color:rgba(22,33,31,.58)}
  .tf-meta strong{color:#E8342A;font-weight:700;white-space:nowrap}
  .tf-foot{flex:0 0 100%;text-align:center;font-size:12px;color:rgba(22,33,31,.5);margin:0}
  html[data-mode="night"] .tf-item{background:#15223A;border-color:rgba(255,138,30,.22)}
  @media (prefers-reduced-motion:reduce){.tf-track{animation:none}.tf-marquee{overflow-x:auto}}
  /* ===== Mode jour / nuit ===== */
  html:not([data-mode="night"]) .set-night,html[data-mode="night"] .set-day{display:none}
  body,section,.shared-card,.room-more,.mode-tabs{transition:background-color .5s ease,color .5s ease,border-color .5s ease}
  .mode-tabs{display:inline-flex;gap:4px;padding:4px;border-radius:999px;border:1px solid var(--apt-line,rgba(22,33,31,.15));background:#fff;margin:0 0 18px}
  .mode-tabs button{display:inline-flex;align-items:center;gap:7px;border:0;background:none;color:rgba(22,33,31,.62);font:600 13.5px/1 'Manrope',sans-serif;padding:9px 15px;border-radius:999px;cursor:pointer;transition:background .3s ease,color .3s ease}
  .mode-tabs button:hover{color:#16211F}
  html:not([data-mode="night"]) .mode-tabs .mt-day{background:#22385C;color:#FFFFFF}
  html[data-mode="night"] .mode-tabs .mt-night{background:#E9CE8E;color:#0D1624}
  .photo-tag{position:absolute;top:10px;left:10px;z-index:2;display:inline-flex;align-items:center;gap:6px;padding:6px 11px;border-radius:999px;background:rgba(9,20,38,.62);color:#FFFFFF;font-size:11.5px;font-weight:600;letter-spacing:.03em;pointer-events:none;backdrop-filter:blur(3px)}
  .photo-tag svg{width:13px;height:13px}
  .mode-note{display:flex;align-items:center;justify-content:center;gap:8px;font-size:13.5px;font-style:italic;color:rgba(22,33,31,.62);margin:0 0 14px}
  .photo-set{animation:setFade .5s ease}
  @keyframes setFade{from{opacity:0}to{opacity:1}}
  .mode-switch{display:inline-flex;align-items:center;gap:2px;padding:3px;border-radius:999px;background:rgba(9,30,43,.34);box-shadow:inset 0 0 0 1px rgba(255,255,255,.16)}
  #site-header.scrolled .mode-switch{background:rgba(22,33,31,.06);box-shadow:inset 0 0 0 1px rgba(22,33,31,.1)}
  .mode-switch button{width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:50%;background:none;color:currentColor;opacity:.75;cursor:pointer;transition:background .3s ease,color .3s ease,opacity .3s ease}
  .mode-switch button:hover{opacity:1}
  html:not([data-mode="night"]) .mode-switch .ms-day{background:#FFFFFF;color:#C9A45C;opacity:1}
  html[data-mode="night"] .mode-switch .ms-night{background:#E9CE8E;color:#0D1624;opacity:1}
  .dn-grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:clamp(28px,5vw,64px);align-items:center}
  .dn-preview{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .dn-card{position:relative;border-radius:12px;overflow:hidden;aspect-ratio:4/5;box-shadow:0 20px 50px -30px rgba(10,20,19,.4);transition:opacity .5s ease,transform .5s ease}
  .dn-card img{width:100%;height:100%;object-fit:cover;display:block}
  html:not([data-mode="night"]) .dn-card:last-child,html[data-mode="night"] .dn-card:first-child{opacity:.5;transform:scale(.95)}
  @media (max-width:860px){.dn-grid{grid-template-columns:1fr}}
  @media (max-width:640px){.mode-switch button{width:28px;height:28px}#nav-book{padding:9px 14px!important;font-size:13px!important}}
  html[data-mode="night"]{--bg-alt:#101B2C;--card:#15223A;--ink:#EDF0F5;--ink-rgb:237,240,245;--hdr-bg:rgba(13,22,36,.92);color-scheme:dark}
  html[data-mode="night"] body{background:#0D1624}
  html[data-mode="night"] .theme-am{--apt-accent:#E9CE8E;--apt-soft:rgba(233,206,142,.09);--apt-line:rgba(233,206,142,.26);--apt-tint:#111C2E}
  html[data-mode="night"] .tf-card,html[data-mode="night"] .tf-wink{background:linear-gradient(120deg,#1d1a24,#16192a);border-color:rgba(232,52,42,.32)}
  html[data-mode="night"] img[src$="rentanoo-logo.webp"]{filter:brightness(0) invert(1)}
  html[data-mode="night"] #lieu iframe{filter:invert(.9) hue-rotate(180deg) saturate(.7)}
  html[data-mode="night"] .h-link{color:#7CC4EA!important}
  html[data-mode="night"] #lieu [style*="color:#22385C"]{color:#E9CE8E!important}
'''

# ---------- Scripts ----------
T_json = json.dumps(TR, ensure_ascii=False, indent=8)
main = script_main
main = re.sub(r'      var T = \{.*?\n      \};', lambda m: '      var T = ' + T_json + ';', main, count=1, flags=re.S)
main = re.sub(r'var titleHtml = \{.*?\};', lambda m: 'var titleHtml = { fr: "Piscine, bar et calme à deux pas de " + emp("Hell-Ville") + ".", it: "Piscina, bar e tranquillità a due passi da " + emp("Hell-Ville") + ".", en: "Pool, bar and calm, minutes from " + emp("Hell-Ville") + "." };', main, count=1, flags=re.S)
main = re.sub(r'var waMsg = \{.*?\n      \};', lambda m: '''var waMsg = {
        gen: { fr: "Bonjour, je suis intéressé(e) par un séjour à l'hôtel AM Résidence (Hell-Ville, Nosy Be). Pouvez-vous me renseigner ?", it: "Buongiorno, sono interessato/a a un soggiorno all'hotel AM Résidence (Hell-Ville, Nosy Be). Potete darmi informazioni?", en: "Hello, I'm interested in a stay at AM Résidence hotel (Hell-Ville, Nosy Be). Could you tell me more?" }
      };''', main, count=1, flags=re.S)
main = main.replace("var sec = el.closest('[data-gallery]') || el.closest('section') || document.body;", "var sec = el.closest('.photo-set') || el.closest('[data-gallery]') || el.closest('section') || document.body;")
main = main.replace("var first = b.closest('section').querySelector('.gallery-extra img');", "var first = (b.closest('.photo-set') || b.closest('section')).querySelector('.gallery-extra img');")
main = main.replace("header.style.background = 'rgba(251,251,249,.94)';", "header.style.background = 'var(--hdr-bg)';")
main = main.replace("header.style.color = '#16211F';", "header.style.color = 'var(--ink)';")
main = main.replace("if (wm) wm.style.color = '#16211F';", "")
mode_js = '''
<script>
(function(){
  var root = document.documentElement;
  function apply(mode, anchor){
    var before = anchor ? anchor.getBoundingClientRect().top : null;
    root.setAttribute('data-mode', mode);
    [].forEach.call(document.querySelectorAll('img[data-day]'), function(im){
      var src = im.getAttribute(mode === 'night' ? 'data-night' : 'data-day');
      if (src && im.getAttribute('src') !== src) im.setAttribute('src', src);
    });
    [].forEach.call(document.querySelectorAll('[data-set-mode]'), function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-set-mode') === mode ? 'true' : 'false'); });
    var tc = document.querySelector('meta[name=theme-color]'); if (tc) tc.setAttribute('content', mode === 'night' ? '#0D1624' : '#22385C');
    if (anchor && before !== null) window.scrollBy(0, anchor.getBoundingClientRect().top - before);
    window.dispatchEvent(new Event('scroll'));
  }
  [].forEach.call(document.querySelectorAll('[data-set-mode]'), function(b){
    b.addEventListener('click', function(){
      var mode = b.getAttribute('data-set-mode');
      try { localStorage.setItem('amr_mode', mode); } catch(e){}
      apply(mode, b.closest('section') ? b : null);
    });
  });
  apply(root.getAttribute('data-mode') === 'night' ? 'night' : 'day');
})();
</script>
'''
main = main.replace("localStorage.setItem('dds_lang'", "localStorage.setItem('amr_lang'").replace("localStorage.getItem('dds_lang')", "localStorage.getItem('amr_lang')")
main = main.replace('a.setAttribute("target", "_blank"); a.setAttribute("rel", "noopener");', 'a.setAttribute("target", "_blank"); a.setAttribute("rel", "noopener");')
main = main.replace('// Liens plateformes câblés en dur dans le HTML (2 logements distincts)', '')
main = main.replace("header.style.background = 'rgba(251,251,249,.92)';", "header.style.background = 'var(--hdr-bg)';")

form_js = script_form.replace("var SITE='villa-lune-de-miel';", "var SITE='am-residence';")

# ---------- Head ----------
DESC = "AM Résidence, hôtel de 15 chambres à Djabala, aux portes de Hell-Ville (Nosy Be) : piscine, bar, chambres climatisées avec espace de travail, wifi Starlink et groupe électrogène. Dès 500 000 Ar la nuit. Réservez en direct."
schema = {
    "@context": "https://schema.org", "@type": "Hotel", "name": "AM Résidence",
    "description": DESC, "url": SITE_URL,
    "image": [SITE_URL + "images/og.jpg", SITE_URL + "images/piscine-jour-1375.webp"],
    "telephone": "+261373437912", "email": "chrisrentanoo@gmail.com",
    "priceRange": "À partir de 500 000 Ar la nuit", "currenciesAccepted": "MGA", "numberOfRooms": 15,
    "address": {"@type": "PostalAddress", "streetAddress": "Djabala", "addressLocality": "Hell-Ville", "addressRegion": "Nosy Be", "addressCountry": "MG"},
    "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LNG},
    "hasMap": MAPS,
    "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in ["Piscine", "Bar", "Climatisation", "Wifi Starlink", "Groupe électrogène", "Espace de travail", "Parking", "Réception", "TV", "Minibar"]],
}

head = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(){{var m=null;try{{m=localStorage.getItem('amr_mode')}}catch(e){{}}var q=(location.search.match(/[?&]mode=(\\w+)/)||[])[1];if(q==='nuit'||q==='night')m='night';if(q==='jour'||q==='day')m='day';if(m!=='day'&&m!=='night'){{var h=(new Date().getUTCHours()+3)%24;m=(h>=18||h<6)?'night':'day'}}document.documentElement.setAttribute('data-mode',m)}})();</script>
<title>AM Résidence — Hôtel avec piscine et bar à Hell-Ville, Nosy Be</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE_URL}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#22385C">
<meta name="author" content="Rentanoo">
<meta name="geo.region" content="MG">
<meta name="geo.placename" content="Hell-Ville, Nosy Be">
<meta name="geo.position" content="{LAT};{LNG}">
<meta name="ICBM" content="{LAT}, {LNG}">
<link rel="icon" type="image/svg+xml" href="images/favicon.svg">
<link rel="apple-touch-icon" href="images/favicon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AM Résidence · Nosy Be">
<meta property="og:locale" content="fr_FR">
<meta property="og:locale:alternate" content="it_IT">
<meta property="og:locale:alternate" content="en_US">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:title" content="AM Résidence — Hôtel avec piscine et bar à Hell-Ville, Nosy Be">
<meta property="og:description" content="15 chambres climatisées, wifi Starlink, piscine et bar, à 5 minutes du centre de Hell-Ville. Dès 500 000 Ar la nuit. Réservez en direct.">
<meta property="og:image" content="{SITE_URL}images/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="La piscine illuminée d'AM Résidence, Hell-Ville, Nosy Be">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="AM Résidence — Hôtel avec piscine et bar à Hell-Ville">
<meta name="twitter:description" content="15 chambres, piscine et bar à Djabala, Hell-Ville (Nosy Be). Dès 500 000 Ar la nuit.">
<meta name="twitter:image" content="{SITE_URL}images/og.jpg">
<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False)}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{css_am}</style>
</head>
<body>

<div style="position:relative;width:100%;overflow:hidden">
'''

tail = '''
</div>

<div id="lightbox" aria-hidden="true" role="dialog" aria-label="Photos"><span class="lb-close" aria-label="Fermer">&times;</span><button type="button" class="lb-nav lb-prev" aria-label="Photo précédente">&#8249;</button><img alt=""><button type="button" class="lb-nav lb-next" aria-label="Photo suivante">&#8250;</button><div class="lb-count"></div></div>

'''

def themable(x):
    x = x.replace('rgba(22,33,31,', 'rgba(var(--ink-rgb),')
    x = re.sub(r'color:#16211F(?=[;"\'}!\s])', 'color:var(--ink)', x)
    x = re.sub(r'background:#fff(?:fff)?(?=[;"\'}!\s])', 'background:var(--card)', x)
    x = x.replace('#fbfbf9', 'var(--bg-alt)')
    return x
_css_orig = css_am
_css_new = ':root{--bg-alt:#fbfbf9;--card:#ffffff;--ink:#16211F;--ink-rgb:22,33,31;--hdr-bg:rgba(251,251,249,.94)}\n' + themable(css_am)
head = head.replace(_css_orig, _css_new)
header = themable(header); band = themable(band); rooms = themable(rooms); sections = themable(sections)
taxifood = themable(taxifood); lieu = themable(lieu); reservation = themable(reservation); partner = themable(partner)
daynight = themable(daynight)
html = head + header + hero + band + daynight + rooms + sections + taxifood + lieu + tarif + reservation + contact + partner + tail + main + '\n\n' + form_js + '\n' + mode_js + '\n</body>\n</html>\n'
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

# ---------- Fichiers annexes ----------
for f in ('taxifood-logo.webp', 'rentanoo-logo.webp'):
    shutil.copy(os.path.join(VILLA, 'images', f), os.path.join(IMG, f))
open(os.path.join(IMG, 'favicon.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#22385C"/><text x="32" y="41" text-anchor="middle" font-family="Georgia,serif" font-size="26" font-weight="600" fill="#C9A45C">AM</text></svg>')
fav = Image.new('RGB', (180, 180), '#22385C')
from PIL import ImageDraw, ImageFont
dr = ImageDraw.Draw(fav)
try:
    fnt = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Bold.ttf', 72)
except Exception:
    fnt = ImageFont.load_default()
dr.text((90, 92), 'AM', fill='#C9A45C', font=fnt, anchor='mm')
fav.save(os.path.join(IMG, 'favicon.png'))
used.update({'favicon.svg', 'favicon.png', 'og.jpg'})
og = Image.open(os.path.join(IMG, 'piscine-nuit-6c64ee76.webp')).convert('RGB')
w, h = og.size; th = int(w * 630 / 1200); top = max(0, (h - th) // 2)
og.crop((0, top, w, top + th)).resize((1200, 630), Image.LANCZOS).save(os.path.join(IMG, 'og.jpg'), quality=86)
open(os.path.join(OUT, 'CNAME'), 'w').write('amresidence.rentanoo.com\n')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n')
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{SITE_URL}</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>\n</urlset>\n')
open(os.path.join(OUT, '.gitignore'), 'w').write('.DS_Store\nCLAUDE.md\n')

# Photos converties mais non utilisées : retirées du site (les originaux restent dans le dossier du Bureau)
unused = sorted(f for f in os.listdir(IMG) if f not in used)
for f in unused:
    os.remove(os.path.join(IMG, f))
print('HTML', len(html), 'car. · photos utilisées', len([u for u in used if u.endswith('.webp')]), '· retirées', len(unused))
print('non utilisées :', ' '.join(unused))
print('traductions', len(TR))
