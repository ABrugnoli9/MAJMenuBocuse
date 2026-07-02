# -*- coding: utf-8 -*-
"""Génère index.html à partir du snapshot (données embarquées, tout côté navigateur)."""
import json


def generer(snap, prec, titre_extra=""):
    donnees = json.dumps(snap, ensure_ascii=False)
    semaine = snap["semaine"]
    semaine_prec = prec["semaine"] if prec else None
    genere_le = snap["genere_le"]

    return TEMPLATE.replace("/*__DATA__*/null", donnees) \
        .replace("__SEMAINE__", semaine) \
        .replace("__SEMAINE_PREC__", semaine_prec or "—") \
        .replace("__GENERE_LE__", genere_le) \
        .replace("__TITRE_EXTRA__", titre_extra)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cost Carte — Maisons Bocuse</title>
<style>
  :root{
    --bg:#f6f7f9; --card:#fff; --ink:#1c2430; --muted:#6b7683;
    --line:#e6e9ed; --accent:#8a1538; --up:#c0392b; --down:#1e8449; --flat:#95a5a6;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
       background:var(--bg);color:var(--ink);font-size:15px}
  header{background:var(--accent);color:#fff;padding:18px 22px}
  header h1{margin:0;font-size:20px;font-weight:600}
  header .sub{opacity:.85;font-size:13px;margin-top:4px}
  .demo{background:#f39c12;color:#fff;font-size:12px;font-weight:600;padding:6px 22px}
  .wrap{max-width:1180px;margin:0 auto;padding:20px 22px 60px}
  .bar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:18px 0 22px}
  select,input[type=search]{font-size:15px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:#fff}
  select{min-width:240px}
  input[type=search]{min-width:280px;flex:1}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:22px}
  .kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
  .kpi .v{font-size:24px;font-weight:700}
  .kpi .l{font-size:12px;color:var(--muted);margin-top:2px}
  table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
  th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);font-size:14px}
  th{background:#fafbfc;font-weight:600;color:var(--muted);white-space:nowrap}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  tr.cat td{background:#f0eef1;font-weight:700;color:var(--accent);font-size:13px;text-transform:uppercase;letter-spacing:.03em}
  .up{color:var(--up);font-weight:600}
  .down{color:var(--down);font-weight:600}
  .flat{color:var(--flat)}
  .ecart-pos{color:var(--down)} .ecart-neg{color:var(--up)}
  .tag{font-size:11px;padding:1px 6px;border-radius:6px;background:#eef1f4;color:var(--muted)}
  .foot{margin-top:26px;color:var(--muted);font-size:12px}
  h2{font-size:16px;margin:26px 0 10px}
  a{color:var(--accent)}
  .count{color:var(--muted);font-size:13px}
</style>
</head>
<body>
<header>
  <h1>Cost Carte — Maisons Bocuse</h1>
  <div class="sub">Semaine <b>__SEMAINE__</b> · comparé à <b>__SEMAINE_PREC__</b> · généré le __GENERE_LE__</div>
</header>
__TITRE_EXTRA__
<div class="wrap">
  <div class="bar">
    <label for="sel"><b>Vue :</b></label>
    <select id="sel"></select>
    <input type="search" id="q" placeholder="🔍 Rechercher un plat…" style="display:none">
    <a href="archives/index.html" style="margin-left:auto;color:var(--accent);font-weight:600;text-decoration:none">📅 Semaines archivées</a>
  </div>
  <div id="content"></div>
  <div class="foot">Valeur suivie : <b>Coût de revient (HT)</b>. Colonnes Ratio / PV cible 26 % / Écart lues telles quelles dans l'Excel (à jour avec le dernier prix). Lecture du 1er onglet « Récap. cost carte » de chaque fichier.</div>
</div>

<script>
const DATA = /*__DATA__*/null;

// Ordre métier des catégories (le reste vient après, par ordre alpha)
const ORDRE_CAT = ["À PARTAGER","ENTRÉES","PLATS - PÂTES & RISOTTOS","PLATS - POISSONS","PLATS - VIANDES","PLATS - AUTRES","DESSERTS"];
function catRank(c){
  const i = ORDRE_CAT.findIndex(x => x.toUpperCase() === (c||"").trim().toUpperCase());
  return i<0 ? [999, (c||"").toUpperCase()] : [i, ""];
}
function triCat(a,b){
  const ra=catRank(a.categorie), rb=catRank(b.categorie);
  if(ra[0]!==rb[0]) return ra[0]-rb[0];
  return ra[1].localeCompare(rb[1]);
}

const eur = v => (v==null? "—" : v.toLocaleString("fr-FR",{style:"currency",currency:"EUR"}));
const pct = v => (v==null? "" : (v>0?"+":"")+v.toLocaleString("fr-FR",{maximumFractionDigits:1})+"%");
const pctVal = v => (v==null? "—" : (v*100).toLocaleString("fr-FR",{maximumFractionDigits:1})+"%");

function deltaCell(p){
  if(p.delta==null) return '<span class="flat">—</span>';
  if(Math.abs(p.delta) < 0.005) return '<span class="flat">=</span>';
  const cls = p.delta>0 ? "up":"down";
  const arr = p.delta>0 ? "▲":"▼";
  return `<span class="${cls}">${arr} ${eur(Math.abs(p.delta))} <small>(${pct(p.delta_pct)})</small></span>`;
}
function ecartCell(v){
  if(v==null) return "—";
  const cls = v>0 ? "ecart-pos" : (v<0 ? "ecart-neg" : "");
  return `<span class="${cls}">${eur(v)}</span>`;
}

function statsMaison(m){
  let hausse=0, baisse=0, stable=0, somme=0, n=0, deltaTot=0;
  m.plats.forEach(p=>{
    somme+=p.cout; n++;
    if(p.delta==null || Math.abs(p.delta)<0.005) stable++;
    else if(p.delta>0){hausse++; deltaTot+=p.delta;}
    else {baisse++; deltaTot+=p.delta;}
  });
  return {hausse,baisse,stable,n,moy:n?somme/n:0,deltaTot};
}

function ligneColonnes(p){
  return `
      <td class="num">${eur(p.cout_prec)}</td>
      <td class="num"><b>${eur(p.cout)}</b></td>
      <td>${deltaCell(p)}</td>
      <td class="num">${pctVal(p.ratio)}</td>
      <td class="num">${eur(p.pv)}</td>
      <td class="num">${eur(p.pv_cible)}</td>
      <td class="num">${ecartCell(p.ecart)}</td>`;
}
const ENTETE_COLS = `
      <th class="num">Coût sem. préc.</th>
      <th class="num">Coût actuel</th>
      <th>Évolution</th>
      <th class="num">Ratio théo.</th>
      <th class="num">PV TTC</th>
      <th class="num">PV cible 26%</th>
      <th class="num">Écart</th>`;

function renderMaison(m){
  const s = statsMaison(m);
  let h = `<div class="cards">
    <div class="kpi"><div class="v">${s.n}</div><div class="l">plats costés</div></div>
    <div class="kpi"><div class="v">${eur(s.moy)}</div><div class="l">coût moyen</div></div>
    <div class="kpi"><div class="v up">${s.hausse}</div><div class="l">en hausse</div></div>
    <div class="kpi"><div class="v down">${s.baisse}</div><div class="l">en baisse</div></div>
    <div class="kpi"><div class="v flat">${s.stable}</div><div class="l">stables</div></div>
  </div>`;

  h += `<table><thead><tr><th>Plat</th><th>Statut</th>${ENTETE_COLS}</tr></thead><tbody>`;
  let cat=null;
  m.plats.slice().sort(triCat).forEach(p=>{
    if(p.categorie!==cat){cat=p.categorie; h+=`<tr class="cat"><td colspan="9">${cat||"—"}</td></tr>`;}
    h += `<tr><td>${p.nom_court||p.nom}</td>
      <td><span class="tag">${p.statut||""}</span></td>${ligneColonnes(p)}</tr>`;
  });
  h += `</tbody></table>`;
  return h;
}

function renderTous(filtre){
  const q=(filtre||"").trim().toLowerCase();
  const tous=[];
  DATA.maisons.forEach(m=>m.plats.forEach(p=>tous.push({...p, maison:m.maison})));
  const list = tous.filter(p=> !q || (p.nom_court||p.nom||"").toLowerCase().includes(q) || (p.nom||"").toLowerCase().includes(q) || p.maison.toLowerCase().includes(q));
  list.sort((a,b)=>{ const c=triCat(a,b); if(c) return c; return (a.nom_court||a.nom).localeCompare(b.nom_court||b.nom); });

  let h = `<div class="count">${list.length} plat(s) affiché(s)${q?` pour « ${filtre} »`:""} — toutes maisons confondues.</div>`;
  h += `<table><thead><tr><th>Plat</th><th>Maison</th><th>Catégorie</th>${ENTETE_COLS}</tr></thead><tbody>`;
  list.forEach(p=>{
    h += `<tr><td>${p.nom_court||p.nom}</td>
      <td><b>${p.maison}</b></td>
      <td><span class="tag">${p.categorie||""}</span></td>${ligneColonnes(p)}</tr>`;
  });
  h += `</tbody></table>`;
  return h;
}

function renderRecap(){
  let totH=0,totB=0,totN=0;
  const lignes = DATA.maisons.map(m=>{ const s=statsMaison(m); totH+=s.hausse; totB+=s.baisse; totN+=s.n; return {m,s}; });
  let h = `<div class="cards">
    <div class="kpi"><div class="v">${DATA.maisons.length}</div><div class="l">maisons</div></div>
    <div class="kpi"><div class="v">${totN}</div><div class="l">plats costés</div></div>
    <div class="kpi"><div class="v up">${totH}</div><div class="l">hausses (semaine)</div></div>
    <div class="kpi"><div class="v down">${totB}</div><div class="l">baisses (semaine)</div></div>
  </div>`;

  h += `<h2>Par maison</h2><table><thead><tr>
      <th>Maison</th><th class="num">Plats</th><th class="num">Coût moyen</th>
      <th class="num">Hausses</th><th class="num">Baisses</th><th class="num">Impact total</th>
    </tr></thead><tbody>`;
  lignes.sort((a,b)=> b.s.deltaTot - a.s.deltaTot).forEach(({m,s})=>{
    const cls = s.deltaTot>0.005?"up":(s.deltaTot<-0.005?"down":"flat");
    h += `<tr>
      <td><a href="#" onclick="selectVue('${m.maison.replace(/'/g,"")}');return false;"><b>${m.maison}</b></a></td>
      <td class="num">${s.n}</td><td class="num">${eur(s.moy)}</td>
      <td class="num up">${s.hausse}</td><td class="num down">${s.baisse}</td>
      <td class="num ${cls}">${(s.deltaTot>0?"+":"")+eur(s.deltaTot)}</td>
    </tr>`;
  });
  h += `</tbody></table>`;

  const tous=[];
  DATA.maisons.forEach(m=>m.plats.forEach(p=>{ if(p.delta!=null && p.delta>0.005) tous.push({...p,maison:m.maison}); }));
  tous.sort((a,b)=>b.delta-a.delta);
  if(tous.length){
    h += `<h2>Top 10 hausses de la semaine</h2><table><thead><tr>
      <th>Plat</th><th>Maison</th><th class="num">Avant</th><th class="num">Après</th><th>Évolution</th>
    </tr></thead><tbody>`;
    tous.slice(0,10).forEach(p=>{
      h+=`<tr><td>${p.nom_court||p.nom}</td><td>${p.maison}</td>
        <td class="num">${eur(p.cout_prec)}</td><td class="num">${eur(p.cout)}</td>
        <td>${deltaCell(p)}</td></tr>`;
    });
    h+=`</tbody></table>`;
  }
  return h;
}

function render(){
  const v = document.getElementById("sel").value;
  const c = document.getElementById("content");
  const q = document.getElementById("q");
  q.style.display = (v==="__tous__") ? "" : "none";
  if(v==="__recap__"){ c.innerHTML = renderRecap(); return; }
  if(v==="__tous__"){ c.innerHTML = renderTous(q.value); return; }
  const m = DATA.maisons.find(x=>x.maison===v);
  c.innerHTML = m ? renderMaison(m) : "Aucune donnée.";
}
function selectVue(v){ document.getElementById("sel").value=v; render(); window.scrollTo(0,0); }

(function init(){
  const sel = document.getElementById("sel");
  sel.innerHTML = `<option value="__recap__">📊 Récap Chef (toutes maisons)</option>` +
    `<option value="__tous__">🔍 Tous les plats (recherche)</option>` +
    DATA.maisons.map(m=>`<option value="${m.maison}">${m.maison}</option>`).join("");
  sel.addEventListener("change", render);
  document.getElementById("q").addEventListener("input", render);
  render();
})();
</script>
</body>
</html>
"""
