# Artes da versão preta: ícone vermelho + MediCo branco + tracinho vermelho; @ branco. Unidades em mm.
import os
import gen
from gen import logo, text_path, text_width, ig_icon, LOGO_RATIO, CAP
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','versao-preta','arte-confeccao')
RED='#F83E3E'; W='#FFFFFF'
def stack(word_w, icon_h, gap, tr_w, tr_h, tgap):
    iw=icon_h*LOGO_RATIO; cx=word_w/2
    s=logo(cx-iw/2,0,icon_h,RED)
    fs=100; fs*=word_w/text_width('MediCo',700,fs,-0.03)
    base=icon_h+gap+fs*CAP
    s+=text_path('MediCo',700,fs,cx,base,W,-0.03,'middle')[0]
    ty=base+tgap
    s+=f'<rect x="{cx-tr_w/2:.2f}" y="{ty:.2f}" width="{tr_w}" height="{tr_h}" rx="{tr_h/2}" fill="{RED}"/>'
    return s, word_w, ty+tr_h
def insta(w):
    fs=40; tw=text_width('@medico.oficial.br',700,fs); ic=fs*0.95; g=fs*0.33
    k=w/(ic+g+tw); fs*=k; ic*=k; g*=k
    y=fs*CAP+1
    s=ig_icon(0,y-fs*CAP/2-ic/2,ic,W)+text_path('@medico.oficial.br',700,fs,ic+g,y,W)[0]
    return s,w,y+fs*0.25
# escala relativa medida na imagem aprovada (costas: palavra 300 px ~ 30 cm)
pecas={'peito-logo':stack(90,35,7,15,1.8,7.5),'costas-logo':stack(300,140,22,46,5,22),'costas-instagram':insta(250)}
for n,(b,w,h) in pecas.items(): gen.write_svg  # noqa
import re
for n,(b,w,h) in pecas.items():
    pad=5; Wd,Hd=w+2*pad,h+2*pad
    open(os.path.join(OUT,n+'.svg'),'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd:.2f}mm" height="{Hd:.2f}mm" viewBox="0 0 {Wd:.2f} {Hd:.2f}"><g transform="translate({pad} {pad})">{b}</g></svg>')
    print(n, round(w,1), 'x', round(h,1), 'mm')
