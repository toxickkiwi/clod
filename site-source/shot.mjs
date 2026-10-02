import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const b = await chromium.launch();
for (const [name, vp] of [['desktop',{width:1440,height:900}],['mobile',{width:390,height:844}]]) {
  const p = await b.newPage({viewport: vp});
  await p.goto('https://robimgood.beer/mestaprodazh', {waitUntil:'networkidle', timeout:60000}).catch(e=>console.log(e.message));
  await p.waitForTimeout(2500);
  await p.screenshot({path:`${name}-top.png`});
  await p.screenshot({path:`${name}-full.png`, fullPage:true});
  console.log(name, await p.evaluate(()=>document.body.scrollHeight));
}
await b.close();
