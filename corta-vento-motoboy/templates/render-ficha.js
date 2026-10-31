const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1123,height:794},deviceScaleFactor:2});
await p.goto('file://'+__dirname+'/ficha.html');await p.waitForTimeout(500);
await p.pdf({path:__dirname+'/../ficha-tecnica-corta-vento.pdf',width:'297mm',height:'210mm',printBackground:true});
await p.screenshot({path:__dirname+'/../ficha-tecnica-corta-vento.png'});await b.close()})();
