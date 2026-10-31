// NODE_PATH=$(npm root -g) node render.js  -> mockups PNG + artes PDF/PNG 300 dpi
const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch();
const out=__dirname+'/../';
for(const [f,w,h] of [['mockup-frente-costas',2200,900],['mockup-frente',1200,900],['mockup-costas',1200,900]]){
 const p=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:2});
 await p.goto('file://'+__dirname+'/'+f+'.html');await p.waitForTimeout(400);await p.screenshot({path:out+f+'.png'});await p.close();}
const A=out+'arte-confeccao/';
for(const f of fs.readdirSync(A).filter(x=>x.endsWith('.svg'))){
 const svg=fs.readFileSync(A+f,'utf8');const wmm=parseFloat(svg.match(/width="([\d.]+)mm"/)[1]),hmm=parseFloat(svg.match(/height="([\d.]+)mm"/)[1]);
 const px=mm=>Math.ceil(mm/25.4*96);
 const p=await b.newPage({viewport:{width:px(wmm),height:px(hmm)},deviceScaleFactor:300/96});
 await p.setContent(`<html><head><style>@page{size:${wmm}mm ${hmm}mm;margin:0}html,body{margin:0;background:transparent}svg{display:block;width:${wmm}mm;height:${hmm}mm}</style></head><body>${svg}</body></html>`);
 const base=A+f.replace('.svg','');
 await p.pdf({path:base+'.pdf',width:wmm+'mm',height:hmm+'mm',printBackground:true});
 await p.screenshot({path:base+'-300dpi.png',omitBackground:true});await p.close();}
await b.close()})();
