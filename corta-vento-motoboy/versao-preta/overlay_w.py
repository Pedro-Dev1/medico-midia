import sys, os
T='/mnt/project-files/medico-instagram/corta-vento-motoboy/templates'
sys.path.insert(0,T); os.chdir(T)
import gen
from gen import logo, text_path, text_width, ig_icon, LOGO_RATIO, CAP
RED='#F83E3E'; W='#FFFFFF'; S=2
parts=[]
def block(cx, icon_top, icon_h, word_w, gap, traco_w, traco_h, tgap):
    iw=icon_h*LOGO_RATIO
    parts.append(logo(cx-iw/2, icon_top, icon_h, W))
    fs=100; tw=text_width('MediCo',700,fs,-0.03); fs*=word_w/tw
    base=icon_top+icon_h+gap+fs*CAP
    parts.append(text_path('MediCo',700,fs,cx,base,W,-0.03,'middle')[0])
    ty=base+tgap
    parts.append(f'<rect x="{cx-traco_w/2}" y="{ty}" width="{traco_w}" height="{traco_h}" rx="{traco_h/2}" fill="{W}"/>')
# costas
block(1195*S, 205*S, 140*S, 300*S, 22*S, 46*S, 5*S, 22*S)
# frente
block(598*S, 266*S, 44*S, 112*S, 8*S, 18*S, 2.2*S, 9*S)
# instagram nas costas, abaixo da faixa
fs=30*S; ic=fs*0.95; g=10*S
tw=text_width('@medico.oficial.br',700,fs); tot=ic+g+tw; x0=1195*S-tot/2; y=625*S
parts.append(ig_icon(x0, y-fs*CAP/2-ic/2, ic, W))
parts.append(text_path('@medico.oficial.br',700,fs,x0+ic+g,y,W)[0])
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="3072" height="2048" viewBox="0 0 3072 2048">{"".join(parts)}</svg>'
open('/tmp/claude-0/-home-user-medico-midia/67e66be9-a472-581b-adb3-9c5617098a8b/scratchpad/ed/ov_w.svg','w').write(svg)
