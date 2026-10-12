// uso: node render.js <pastaFrames> [fps] [t1,t2,... para prévias]
const {chromium}=require('playwright');(async()=>{
const out=process.argv[2],fps=+(process.argv[3]||30),only=process.argv[4];
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+__dirname+'/video.html');await p.waitForTimeout(500);
const D=await p.evaluate(()=>DURATION);const ts=only?only.split(',').map(Number):[...Array(Math.ceil(D*fps)).keys()].map(i=>i/fps);
require('fs').mkdirSync(out,{recursive:true});
for(let i=0;i<ts.length;i++){await p.evaluate(t=>seek(t),ts[i]);
 await p.screenshot({path:`${out}/f${String(i).padStart(5,'0')}.${only?'png':'jpg'}`,type:only?'png':'jpeg',quality:only?undefined:95});}
console.log('frames',ts.length,'dur',D);await b.close()})();
