const {chromium}=require('playwright');
const [,,PKG,BUILD]=process.argv;
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({deviceScaleFactor:1});
 const p=await ctx.newPage();
 // PDFs
 for (const [src,dst] of [[BUILD+'/specimen.html',PKG+'/Specimen/Dastkhat-Specimen.pdf']]){
   await p.goto('file://'+src); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(500);
   await p.pdf({path:dst,preferCSSPageSize:true,printBackground:true});
 }
 // frames
 await p.setViewportSize({width:2000,height:1200});
 await p.goto('file://'+BUILD+'/frames.html'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
 for (const id of ['cover','dot-styles','keywords','weights','glyphs','ui','poster','social-1','social-2','social-3']){
   await p.locator('#'+id).screenshot({path:PKG+'/Demos/images/dastkhat-'+id+'.png'});
 }
 // page screenshots for checking
 for (const f of ['index','type-tester','glyph-map','ui-demo','poster']){
   await p.setViewportSize({width:1280,height:900});
   await p.goto('file://'+PKG+'/Demos/'+f+'.html'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(400);
   await p.screenshot({path:BUILD+'/shot-'+f+'.png',fullPage:true});
 }
 for (const f of ['Helps/guide','Webfonts/webfont-test']){
   await p.goto('file://'+PKG+'/'+f+'.html'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(400);
   await p.screenshot({path:BUILD+'/shot-'+f.split('/')[1]+'.png',fullPage:true});
 }
 await b.close(); console.log('rendered');
})();
