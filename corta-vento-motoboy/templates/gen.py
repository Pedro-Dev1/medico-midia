# Gera as artes de confecção (SVG em mm, texto convertido em curvas) e o HTML dos mockups.
# Uso: python3 gen.py  (depois: NODE_PATH=$(npm root -g) node render.js)
import os, re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, '..', 'arte-confeccao')
os.makedirs(OUT, exist_ok=True)

RED = '#F83E3E'
WHITE = '#FFFFFF'

# ---------- logo (vetor reconstruído do logo.png, viewBox recortado) ----------
LOGO_VB = (170, 106, 682, 811)  # x, y, w, h
LOGO_RATIO = LOGO_VB[2] / LOGO_VB[3]
_logo_src = open(os.path.join(D, 'logo-tpl.svg')).read()
_logo_inner = re.search(r'<svg[^>]*>(.*)</svg>', _logo_src, re.S).group(1)
_uid = [0]

def logo(x, y, h, color):
    """Logo com altura h (unidades do SVG pai), canto superior esquerdo em x,y."""
    _uid[0] += 1
    inner = _logo_inner.replace('COLOR', color).replace('id="fade"', f'id="fade{_uid[0]}"').replace('url(#fade)', f'url(#fade{_uid[0]})')
    s = h / LOGO_VB[3]
    return f'<g transform="translate({x:.3f} {y:.3f}) scale({s:.5f}) translate({-LOGO_VB[0]} {-LOGO_VB[1]})">{inner}</g>'

# ---------- texto em curvas ----------
FONTS = {w: TTFont(os.path.join(D, f'manrope-{w}.woff2')) for w in (500, 700, 800)}

def text_path(txt, weight, size, x, y, color, tracking=0.0, anchor='start'):
    """Texto convertido em curvas. y = linha de base. size = tamanho do corpo. tracking em em."""
    f = FONTS[weight]; upm = f['head'].unitsPerEm; gs = f.getGlyphSet(); cmap = f.getBestCmap(); hmtx = f['hmtx']
    s = size / upm
    names = [cmap[ord(c)] for c in txt]
    adv = [hmtx[n][0] + tracking * upm for n in names]
    width = (sum(adv) - tracking * upm) * s
    x0 = x - width / 2 if anchor == 'middle' else x
    pen = SVGPathPen(gs); cx = 0
    for n, a in zip(names, adv):
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, x0 + cx * s, y)))
        cx += a
    return f'<path fill="{color}" d="{pen.getCommands()}"/>', width

def text_width(txt, weight, size, tracking=0.0):
    return text_path(txt, weight, size, 0, 0, '#000', tracking)[1]

CAP = 1440 / 2000  # altura da maiúscula / corpo (Manrope)

def ig_icon(x, y, s, color):
    """Ícone do Instagram, quadrado de lado s, canto em x,y."""
    k = s / 24
    return (f'<g transform="translate({x:.3f} {y:.3f}) scale({k:.5f})" fill="none" stroke="{color}" stroke-width="2.2">'
            f'<rect x="2.2" y="2.2" width="19.6" height="19.6" rx="5.6"/><circle cx="12" cy="12" r="4.6"/>'
            f'<circle cx="17.6" cy="6.4" r="1.1" fill="{color}" stroke="none"/></g>')

# ---------- peças de arte (unidades = mm) ----------
def peca_peito(color):
    """Logo horizontal do peito: 100 mm de largura."""
    ih = 30.0; iw = ih * LOGO_RATIO; gap = 4.5
    fs = 17.5
    tw = text_width('MediCo', 700, fs, -0.02)
    W = iw + gap + tw
    H = ih
    base = ih / 2 + fs * CAP / 2
    t, _ = text_path('MediCo', 700, fs, iw + gap, base, color, -0.02)
    body = logo(0, 0, ih, color) + t
    k = 100.0 / W
    return f'<g transform="scale({k:.5f})">{body}</g>', 100.0, H * k

def peca_costas_sup(color):
    """Logo grande das costas: ícone + MediCo + tracinho. 300 mm de largura."""
    W = 260.0
    fs = 92.0
    tw = text_width('MediCo', 700, fs, -0.03)
    k = W / tw  # ajusta corpo para 300 mm
    fs *= k
    ih = 120.0; iw = ih * LOGO_RATIO
    y_txt = ih + 18 + fs * CAP
    t, _ = text_path('MediCo', 700, fs, W / 2, y_txt, color, -0.03, 'middle')
    tr_y = y_txt + 20
    traco = f'<rect x="{W/2-22:.2f}" y="{tr_y:.2f}" width="44" height="4.5" rx="2.25" fill="{color}"/>'
    return logo(W / 2 - iw / 2, 0, ih, color) + t + traco, W, tr_y + 4.5

def peca_costas_inf(color):
    """Frase + @ abaixo da faixa refletiva. 290 mm de largura."""
    fs = 34.0
    l1, l2 = 'Marque sua consulta', 'sem telefonar.'
    w1 = text_width(l1, 700, fs, -0.01)
    k = 280.0 / w1; fs *= k
    W = 280.0
    lh = fs * 1.18
    a, _ = text_path(l1, 700, fs, W / 2, fs * CAP, color, -0.01, 'middle')
    b, _ = text_path(l2, 700, fs, W / 2, fs * CAP + lh, color, -0.01, 'middle')
    # @ com ícone
    fs2 = 22.0; ic = fs2 * 0.95; g = 4.0
    tw = text_width('@medico.oficial.br', 700, fs2)
    tot = ic + g + tw; x0 = W / 2 - tot / 2
    y2 = fs * CAP + lh + 34
    at, _ = text_path('@medico.oficial.br', 700, fs2, x0 + ic + g, y2, color)
    icon = ig_icon(x0, y2 - fs2 * CAP / 2 - ic / 2 - 0.4, ic, color)
    return a + b + icon + at, W, y2 + 4

def write_svg(name, body, w, h, pad=0, bg=None):
    W, H = w + 2 * pad, h + 2 * pad
    bgr = f'<rect width="{W:.2f}" height="{H:.2f}" fill="{bg}"/>' if bg else ''
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H:.2f}mm" viewBox="0 0 {W:.2f} {H:.2f}">'
           f'{bgr}<g transform="translate({pad} {pad})">{body}</g></svg>')
    open(os.path.join(OUT, name), 'w').write(svg)
    return W, H

SIZES = {}
for nome, fn in [('peito-logo', peca_peito), ('costas-logo', peca_costas_sup), ('costas-frase', peca_costas_inf)]:
    b, w, h = fn(WHITE)
    SIZES[nome] = (w, h)
    write_svg(f'{nome}-branco.svg', b, w, h, pad=5)
    b2, _, _ = fn(RED)
    write_svg(f'{nome}-vermelho.svg', b2, w, h, pad=5)
print({k: (round(v[0], 1), round(v[1], 1)) for k, v in SIZES.items()})

# ---------- mockup (1 px = MM mm) ----------
MM = 1.56
P = lambda mm: mm / MM

FAB = '#E9271F'; FAB_D = '#B8150F'; FAB_L = '#FF4A3D'
GR = '#2A2C31'; GR_L = '#3B3E45'
REF = 'url(#refl)'
BAND = P(50)  # faixa refletiva 5 cm
K = 0.60  # achatamento vertical do desenho (proporção real tam. M: peito 58 cm x comprimento ~75 cm + punho)
Y = lambda y: 92 + (y - 92) * K  # y do desenho -> y na tela
B1, B2 = 476, 839  # faixas refletivas (y do desenho)

# meia jaqueta (lado esquerdo da imagem); a outra metade é espelhada
SLEEVE = 'M302,212 C262,222 236,250 226,292 L152,872 L240,884 L312,440 C312,330 308,262 302,212 Z'
CUFF = 'M152,872 L146,928 L236,940 L240,884 Z'
BODY = 'M500,178 C470,176 445,168 432,155 L302,212 C310,290 314,370 312,440 L318,955 L500,965 Z'
BODY_BACK = 'M500,150 C470,152 445,152 432,155 L302,212 C310,290 314,370 312,440 L318,955 L500,965 Z'
HEM = 'M318,955 L316,1012 L500,1020 L500,965 Z'

def sx(y, a, b):
    (x1, y1), (x2, y2) = a, b
    return x1 + (x2 - x1) * (y - y1) / (y2 - y1)

def band_half(y, back=False):
    h = BAND / K
    # corpo
    xs1, xs2 = sx(y, (312, 440), (318, 955)), sx(y + h, (312, 440), (318, 955))
    xe = 500 if back else 492
    body = f'<path fill="{REF}" d="M{xs1:.1f},{y:.1f} L{xe},{y:.1f} L{xe},{y+h:.1f} L{xs2:.1f},{y+h:.1f} Z"/>'
    return body

def band_sleeve(y):
    h = BAND / K
    o1, o2 = sx(y, (226, 292), (152, 872)), sx(y + h, (226, 292), (152, 872))
    i1, i2 = sx(y, (312, 440), (240, 884)), sx(y + h, (312, 440), (240, 884))
    return f'<path fill="{REF}" d="M{o1:.1f},{y:.1f} L{i1:.1f},{y:.1f} L{i2:.1f},{y+h:.1f} L{o2:.1f},{y+h:.1f} Z"/>'

DEFS = f'''<defs>
<linearGradient id="fab" x1="0" x2="1"><stop offset="0" stop-color="{FAB_D}"/><stop offset=".22" stop-color="{FAB}"/><stop offset=".5" stop-color="{FAB_L}"/><stop offset=".78" stop-color="{FAB}"/><stop offset="1" stop-color="{FAB_D}"/></linearGradient>
<linearGradient id="slv" x1="0" x2="1"><stop offset="0" stop-color="{FAB_D}"/><stop offset=".45" stop-color="{FAB}"/><stop offset=".7" stop-color="{FAB_L}"/><stop offset="1" stop-color="{FAB_D}"/></linearGradient>
<linearGradient id="gr" x1="0" x2="1"><stop offset="0" stop-color="#1C1D21"/><stop offset=".5" stop-color="{GR_L}"/><stop offset="1" stop-color="#1C1D21"/></linearGradient>
<linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9BA1AA"/><stop offset=".35" stop-color="#E9ECF0"/><stop offset=".55" stop-color="#C3C8CF"/><stop offset="1" stop-color="#8E949D"/></linearGradient>
<linearGradient id="vshade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".10"/><stop offset=".25" stop-color="#000" stop-opacity="0"/><stop offset=".85" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".16"/></linearGradient>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="drop" x="-20%" y="-10%" width="140%" height="130%"><feGaussianBlur in="SourceAlpha" stdDeviation="14"/><feOffset dy="16"/><feComponentTransfer><feFuncA type="linear" slope=".28"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>'''

RIB = lambda x1, y1, x2, y2, n: ''.join(
    f'<line x1="{x1 + (x2-x1)*i/n:.1f}" y1="{y1 + (y2-y1)*i/n:.1f}" x2="{x1 + (x2-x1)*i/n:.1f}" y2="{y1 + (y2-y1)*i/n + 52:.1f}" stroke="#000" stroke-opacity=".25" stroke-width="1"/>'
    for i in range(1, n))

def folds(back=False):
    # vincos suaves do tecido (nylon com brilho)
    dark = [
        'M330,520 C360,560 372,640 360,720', 'M340,800 C380,840 420,880 440,950',
        'M200,520 C210,600 205,680 190,760', 'M262,300 C270,360 268,400 258,430',
    ]
    light = ['M400,600 C420,680 420,780 404,880', 'M220,400 C226,470 222,540 214,600', 'M455,450 C470,520 470,600 462,660']
    s = ''.join(f'<path d="{d}" fill="none" stroke="#5a0000" stroke-opacity=".2" stroke-width="10" filter="url(#soft)"/>' for d in dark)
    s += ''.join(f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="12" filter="url(#soft)"/>' for d in light)
    return s

def half(back=False):
    body = BODY_BACK if back else BODY
    s = f'<path d="{SLEEVE}" fill="url(#slv)"/>'
    s += band_sleeve(B1)
    s += f'<path d="{CUFF}" fill="url(#gr)"/>' + RIB(152, 878, 240, 890, 9)
    s += f'<path d="{body}" fill="url(#fab)"/>'
    s += f'<path d="{body}" fill="url(#vshade)"/>'
    s += band_half(B1, back) + band_half(B2, back)
    s += f'<path d="{HEM}" fill="url(#gr)"/>' + RIB(318, 960, 500, 968, 16)
    # costuras
    s += f'<path d="M302,212 C310,290 314,370 312,440" fill="none" stroke="#7a0a06" stroke-width="1.6" stroke-dasharray="4 3" opacity=".7"/>'
    if not back:
        # bolso com zíper
        s += '<path d="M352,620 L384,760" stroke="#1C1D21" stroke-width="5" stroke-linecap="round"/><path d="M352,620 L384,760" stroke="#555" stroke-width="1" stroke-dasharray="2 2"/>'
        s += '<rect x="379" y="724" width="7" height="22" rx="2" fill="#1C1D21" transform="rotate(-14 382 735)"/>'
    else:
        pass
    s += folds(back)
    return s

def jacket(back=False):
    h = half(back)
    mir = f'<g transform="translate(1000 0) scale(-1 1)">{h}</g>'
    s = f'<g filter="url(#drop)"><g transform="translate(0 92) scale(1 {K}) translate(0 -92)">{h}{mir}'
    if back:
        s += f'<path d="M432,158 L436,92 Q500,104 564,92 L568,158 Q500,148 432,158 Z" fill="url(#gr)"/>'
        s += '<path d="M436,120 Q500,130 564,120" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="1" stroke-dasharray="3 3"/>'
    else:
        s += '<path d="M436,92 Q500,78 564,92 Q500,104 436,92 Z" fill="#141518"/>'
        s += f'<path d="M432,158 L436,92 Q500,104 564,92 L568,158 Q500,184 432,158 Z" fill="url(#gr)"/>'
        # zíper
        s += '<rect x="495" y="100" width="10" height="920" fill="#16171A"/>'
        s += '<line x1="500" y1="100" x2="500" y2="1020" stroke="#8a8d93" stroke-width="3" stroke-dasharray="2 2"/>'
        s += '<rect x="493" y="118" width="14" height="22" rx="3" fill="#C9CCD1"/><rect x="496" y="138" width="8" height="26" rx="3" fill="#2A2C31" stroke="#C9CCD1" stroke-width="1.5"/>'
    s += '</g></g>'
    # arte
    if back:
        b, w, hh = peca_costas_sup(WHITE)
        y0 = Y(155) + P(55)
        s += f'<g transform="translate({500 - P(w)/2:.2f} {y0:.2f}) scale({1/MM:.5f})">{b}</g>'
        b, w, hh = peca_costas_inf(WHITE)
        y1 = Y(B1) + BAND + P(38)
        s += f'<g transform="translate({500 - P(w)/2:.2f} {y1:.2f}) scale({1/MM:.5f})">{b}</g>'
    else:
        b, w, hh = peca_peito(WHITE)
        cx = 500 + P(95) + P(w) / 2 - P(w) / 2
        s += f'<g transform="translate({500 + P(60):.2f} {Y(178) + P(110):.2f}) scale({1/MM:.5f})">{b}</g>'
    return s

def page(views, W, H, label=True):
    n = len(views); cell = W / n
    g = ''
    for i, (back, title) in enumerate(views):
        sc = min(cell / 1080, (H - 140) / 640)
        ox = i * cell + (cell - 1000 * sc) / 2
        g += f'<g transform="translate({ox:.1f} 40) scale({sc:.4f})">{jacket(back)}</g>'
        if label:
            g += f'<text x="{i*cell + cell/2:.1f}" y="{H-36}" text-anchor="middle" font-family="Manrope" font-weight="700" font-size="30" fill="#6b6f76" letter-spacing="6">{title}</text>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>@font-face{{font-family:Manrope;font-weight:700;src:url(manrope-700.woff2)}}'
            f'html,body{{margin:0;width:{W}px;height:{H}px;background:radial-gradient(ellipse at 50% 40%,#FAFAFA,#E4E5E8)}}</style></head><body>'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}{g}</svg></body></html>')

open(os.path.join(D, 'mockup-frente-costas.html'), 'w').write(page([(False, 'FRENTE'), (True, 'COSTAS')], 2200, 900))
open(os.path.join(D, 'mockup-frente.html'), 'w').write(page([(False, 'FRENTE')], 1200, 900))
open(os.path.join(D, 'mockup-costas.html'), 'w').write(page([(True, 'COSTAS')], 1200, 900))
print('ok')
