const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1123,height:794},deviceScaleFactor:2});
await p.goto('file://'+__dirname+'/ficha-preta.html');await p.waitForTimeout(500);
await p.pdf({path:__dirname+'/../versao-preta/ficha-tecnica-corta-vento-preto.pdf',width:'297mm',height:'210mm',printBackground:true});
await p.screenshot({path:__dirname+'/../versao-preta/ficha-tecnica-corta-vento-preto.png'});await b.close()})();
