const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:3072,height:2048}});
await p.goto('file://'+__dirname+'/ov.svg');await p.screenshot({path:__dirname+'/ov.png',omitBackground:true});await b.close()})();
