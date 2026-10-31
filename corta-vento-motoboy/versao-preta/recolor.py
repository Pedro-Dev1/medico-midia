from PIL import Image, ImageFilter
import numpy as np, sys
im=np.asarray(Image.open('clean.png').convert('RGB')).astype(float); R,G,B=im[...,0],im[...,1],im[...,2]
L=im.mean(2); H,W=L.shape
red=np.array([248,62,62.])
m=np.clip((98-L)/20,0,1)
# corta a sombra de contato abaixo das barras e punhos (curvas medidas na imagem)
import math
xs=np.arange(W).astype(float); bot=np.full(W,2000.)
def seg(x0,x1,f):
    for x in range(x0,x1+1): bot[x]=f(x)
seg(205,675,lambda x:950+24*math.sin(math.pi*min(max((x-212)/456,0),1)))
seg(45,145,lambda x:976-(x-55)*13/83)
seg(722,820,lambda x:min(964+(x-735)*24/75,979))
seg(880,960,lambda x:933 if x<938 else 924)
seg(988,1388,lambda x:938+17*math.sin(math.pi*min(max((x-995)/385,0),1)))
seg(961,987,lambda x:915)
seg(1513,1535,lambda x:925)
seg(1425,1512,lambda x:941 if x>1446 else 932)
yy=np.arange(H)[:,None]*np.ones((1,W))
m=m*np.clip((bot[None,:]-yy)/2.5,0,1)
pip=np.clip((R-np.maximum(G,B)-60)/40,0,1)
m=np.clip(m-pip,0,1)[...,None]
Ls=np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.6))).astype(float)
g=(0.46+(Ls/48)*0.72)[...,None]
fab=red*np.minimum(g,1.0); hi=np.clip((g-1.0)/1.2,0,1); fab=fab+(255-fab)*hi*0.55
out=im*(1-m)+fab*m
pl=np.clip(L/np.percentile(L[pip>0.5],80),0,1)[...,None]
white=np.array([238,238,240.])*(0.75+0.25*pl)
out=out*(1-pip[...,None])+white*pip[...,None]
o=Image.fromarray(np.clip(out,0,255).astype(np.uint8)); o.save('clean_red.png')
o.crop((150,900,1536,1024)).save('z_bottom.png')
