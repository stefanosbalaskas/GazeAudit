(function(){
  const root=document.querySelector('[data-plot-gallery]');
  if(!root) return;
  const cards=[...root.querySelectorAll('[data-gallery-card]')];
  const search=root.querySelector('[data-gallery-search]');
  const buttons=[...root.querySelectorAll('[data-gallery-filter]')];
  const empty=root.querySelector('[data-gallery-empty]');
  let category='all';
  function apply(){
    const query=(search?.value||'').trim().toLowerCase();
    let visible=0;
    cards.forEach(card=>{
      const categoryOK=category==='all'||card.dataset.category===category;
      const hay=(card.dataset.search||card.textContent||'').toLowerCase();
      const queryOK=!query||hay.includes(query);
      card.hidden=!(categoryOK&&queryOK);
      if(!card.hidden) visible++;
    });
    if(empty) empty.hidden=visible!==0;
  }
  buttons.forEach(button=>button.addEventListener('click',()=>{
    category=button.dataset.galleryFilter||'all';
    buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    apply();
  }));
  search?.addEventListener('input',apply);
  apply();
}());
