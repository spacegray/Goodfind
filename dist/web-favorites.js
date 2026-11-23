(function(root){
  'use strict';
  function safeUrl(value){try{const u=new URL(value);return ['http:','https:'].includes(u.protocol)?u.href:''}catch{return ''}}
  function normalize(item){if(!item||typeof item!=='object')return null;const title=String(item.title||'').trim().slice(0,300);if(!title)return null;const link=safeUrl(item.link);const image=safeUrl(item.image);const store=String(item.store||'Retailer').slice(0,150);return {title,link,image,store,price:String(item.price||'').slice(0,100),delivery:String(item.delivery||'').slice(0,300),id:'web:'+encodeURIComponent(link||`${store}|${title}`)} }
  function searchQuery(text,department){const q=String(text||'').trim();return department==='women'?`women's ${q}`:department==='men'?`men's ${q}`:q}
  root.GoodfindWeb={normalize,searchQuery};
})(globalThis);
