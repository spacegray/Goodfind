(function(root){
  'use strict';
  const entries=[
    ['jacket-r','Cropped faux leather jacket','Fashion','Revolve',128,'Faux leather · size S','jacket leather cropped fitted small', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=650&q=80'],
    ['jacket-p','Cropped leather moto jacket','Fashion','Poshmark',75,'Leather · size S · pre-owned','jacket leather cropped fitted small','https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=650&q=80'],
    ['jacket-d','Fitted faux leather jacket','Fashion','Dolls Kill',98,'Faux leather · size S','jacket leather cropped fitted small','https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=650&q=80'],
    ['eye-t','Energizing eye masks · 24 pairs','Beauty','Target',24,'Gold eye masks · 24 pairs','grace stella energizing eye pads masks','https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=650&q=80'],
    ['eye-a','Energizing eye masks · 24 pairs','Beauty','Amazon',22,'Gold eye masks · 24 pairs','grace stella energizing eye pads masks','https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=650&q=80'],
    ['panties-n','Black cotton cropped top','Fashion','Nordstrom',18,'Cotton blend · size S','black cotton fitted top small','https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=650&q=80'],
    ['panties-a','Black ribbed cotton top','Fashion','Amazon',16,'Cotton blend · size S','black cotton fitted top small','https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=650&q=80'],
    ['socks-t','Warm boot socks · black 3-pack','Accessories','Target',20,'Black · 3 pairs','set black warm boot socks','https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?auto=format&fit=crop&w=650&q=80'],
    ['socks-a','Black cozy boot socks · 3-pack','Accessories','Amazon',18,'Black · 3 pairs','set black warm boot socks','https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?auto=format&fit=crop&w=650&q=80'],
    ['pumps-d','Black platform Mary Jane pumps','Accessories','Dolls Kill',89,'Black · size 7','black platform pumps shoes 7','assets/mary-jane-pumps.jpg'],
    ['pumps-r','Black platform pumps','Accessories','Revolve',148,'Black · size 7','black platform pumps shoes 7','assets/platform-pumps.jpg']
  ];
  const stores={Amazon:'https://www.amazon.com/s?k=',Revolve:'https://www.revolve.com/r/Search.jsp?search=', 'Dolls Kill':'https://www.dollskill.com/search?q=',Poshmark:'https://poshmark.com/search?query=',Target:'https://www.target.com/s?searchTerm=',Nordstrom:'https://www.nordstrom.com/sr?keyword='};
  const catalog=entries.map(([id,title,category,store,price,detail,tags,img])=>({id,title,category,store,price,detail,tags:tags.split(' '),img,badge:'Demo listing',delivery:null,rating:null,reviews:null,link:stores[store]+encodeURIComponent(title)}));
  const stop=new Set(['a','an','and','of','the','for','of','size','set','pair','pairs']);
  function words(text){return String(text).toLowerCase().replace(/&/g,' ').replace(/[^a-z0-9\s]/g,' ').split(/\s+/).filter(w=>w&&!stop.has(w)).map(w=>({pads:'pad',masks:'mask',panties:'panty',pumps:'pump',socks:'sock'}[w]||w))}
  function search(items,query){const terms=words(query);if(!terms.length)return items.slice();return items.map(p=>{const hay=words([p.title,p.category,p.store,p.detail,...p.tags].join(' '));let score=terms.filter(t=>hay.some(h=>h===t||h.startsWith(t)||t.startsWith(h))).length;return {p,score}}).filter(x=>x.score>=Math.max(1,Math.ceil(terms.length*0.5))).sort((a,b)=>b.score-a.score).map(x=>x.p)}
  function groupByStore(items){return items.reduce((groups,p)=>{(groups[p.store||'Sample store']??=[]).push(p);return groups},{})}
  root.GoodfindCatalog={catalog,search,groupByStore};
})(typeof globalThis!=='undefined'?globalThis:this);
