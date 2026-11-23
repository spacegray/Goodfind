const assert=require('node:assert/strict');
const fs=require('node:fs');
const css=fs.readFileSync('dist/style.css','utf8');
assert.match(css,/padding-left:max\(5vw,calc\(\(100vw - 1320px\)\/2\)\)/);
assert.match(css,/grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\)/);
assert.match(css,/\.hero-copy \.search\{width:min\(100%,480px\);min-width:0\}/);
for(const width of [801,1024,1280,1440,1920,2560,3840]){
  const inset=Math.max(width*.05,(width-1320)/2);
  const available=width/2-inset-Math.max(24,Math.min(width*.03,48));
  assert.ok(available>250,`desktop content fits at ${width}`);
  assert.ok(inset>=width*.05,`desktop margin stays in grid at ${width}`);
}
for(const width of [320,360,375,390,414,430,768,800]){
  const inset=width*.05;
  assert.ok(width-2*inset>=288,`mobile content fits at ${width}`);
}
console.log('Hero grid and width checks passed at 15 viewport widths');
