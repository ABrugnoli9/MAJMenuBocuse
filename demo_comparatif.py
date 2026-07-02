# -*- coding: utf-8 -*-
"""
Génère une page de DÉMONSTRATION du comparatif semaine à semaine,
avec des variations de prix simulées. Ne touche pas aux vraies données.

Usage : python demo_comparatif.py  ->  exemple-comparatif.html
"""
import os, json, copy, random
from generer_html import generer

ICI = os.path.dirname(os.path.abspath(__file__))
random.seed(42)

# On part du vrai snapshot de la semaine
snap = json.load(open(os.path.join(ICI, "data", "snapshot-2026-W27.json"), encoding="utf-8"))

# On fabrique une "semaine précédente" simulée en faisant varier les coûts
prec = copy.deepcopy(snap)
prec["semaine"] = "2026-W26 (simulée)"
for m in prec["maisons"]:
    for p in m["plats"]:
        for k in ("cout_prec", "delta", "delta_pct"):
            p.pop(k, None)
        if p["cout"]:
            r = random.random()
            if r < 0.30:      # 30% étaient moins chers -> hausse cette semaine
                p["cout"] = round(p["cout"] * random.uniform(0.85, 0.98), 4)
            elif r < 0.50:    # 20% étaient plus chers -> baisse cette semaine
                p["cout"] = round(p["cout"] * random.uniform(1.03, 1.15), 4)
            # les 50% restants : inchangés

# Index des coûts précédents
idx = {m["maison"]: {p["nom"]: p["cout"] for p in m["plats"]} for m in prec["maisons"]}

# Recalcule les deltas du snapshot actuel vs la semaine simulée
for m in snap["maisons"]:
    anc = idx.get(m["maison"], {})
    for p in m["plats"]:
        ancien = anc.get(p["nom"])
        p["cout_prec"] = ancien
        if ancien is None or p["cout"] is None:
            p["delta"] = p["delta_pct"] = None
        else:
            p["delta"] = round(p["cout"] - ancien, 4)
            p["delta_pct"] = round((p["cout"] - ancien) / ancien * 100, 2) if ancien else None

banniere = '<div class="demo">⚠️ PAGE DE DÉMONSTRATION — les évolutions ci-dessous sont SIMULÉES pour illustrer le rendu du comparatif hebdomadaire.</div>'
html = generer(snap, prec, titre_extra=banniere)
out = os.path.join(ICI, "exemple-comparatif.html")
open(out, "w", encoding="utf-8").write(html)
print("Démo ->", out)
