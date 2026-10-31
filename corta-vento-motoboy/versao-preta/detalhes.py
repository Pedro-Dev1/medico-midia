# Versão preta com detalhes vermelhos: punhos, barras, zíper central e zíperes dos bolsos
from PIL import Image, ImageFilter, ImageDraw
import numpy as np, math
src=Image.open('clean.png').convert('RGB')
im=np.asarray(src).astype(float); L=im.mean(2); H,W=L.shape
red=np.array([248,62,62.])
Ls=np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.6))).astype(float)
g=(0.46+(Ls/48)*0.72)[...,None]
fab=red*np.minimum(g,1.0); hi=np.clip((g-1.0)/1.2,0,1); fab=fab+(255-fab)*hi*0.55
dark=np.clip((98-L)/20,0,1)
# regiões (topo, faixa de x, curva de baixo)
bot=np.full(W,2000.)
def seg(x0,x1,f):
    for x in range(x0,x1+1): bot[x]=f(x)
seg(205,675,lambda x:950+24*math.sin(math.pi*min(max((x-212)/456,0),1)))
seg(45,145,lambda x:976-(x-55)*13/83)
seg(722,820,lambda x:min(964+(x-735)*24/75,979))
seg(880,960,lambda x:933 if x<938 else 924)
seg(961,987,lambda x:915)
seg(988,1388,lambda x:938+17*math.sin(math.pi*min(max((x-995)/385,0),1)))
seg(1513,1535,lambda x:925)
seg(1425,1512,lambda x:941 if x>1446 else 932)
reg=Image.new('L',(W,H),0); d=ImageDraw.Draw(reg)
for (x0,x1,top) in [(205,360,888),(546,675,888),(40,150,904),(720,825,902),(985,1390,885),(878,962,890),(1425,1515,895)]:
    d.rectangle((x0,top,x1,H),fill=255)
d.rectangle((446,96,469,990),fill=255)              # zíper central
d.line((254,612,231,816),fill=255,width=6); d.line((640,612,663,808),fill=255,width=6)  # bolsos
reg=np.asarray(reg.filter(ImageFilter.GaussianBlur(1.2))).astype(float)/255
yy=np.arange(H)[:,None]*np.ones((1,W))
m=(dark*reg*np.clip((bot[None,:]-yy)/2.5,0,1))[...,None]
out=im*(1-m)+fab*m
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save('clean_det.png')
