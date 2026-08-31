# Copywriting — Evidence Unit Placement Registry

Ce dépôt matérialise les audits de copywriting reliés au graphe Neo4j et leur quality gate CI/CD.

Principe courant : `x = variable + valeur + unité + population + période + source` + `u = limites/incertitude/indépendance` → `F = f(x,u,b,s)` EvidenceUnit admise → `Y = séquence + buyer question + rôle NLP + CTA + XPath` → `G = g(Y,F)` décision de copy/placement publiable.

Une substitution n’est publiable que si : x est complet, l’URL canonique a réellement été relue et contient l’information citée, l’EU passe le LLM-as-a-Judge, la boundary est explicite, les sources d’effet et de recommandation sont séparées, l’offre/capability est cohérente, l’XPath cible exactement un élément DOM et la cardinalité d’EU sélectionnées de la page reste inchangée.

## CI/CD

- `.skills/evidence-unit-judge/SKILL.md` — contrat F/G et règles de preuve.
- `src/eu_pipeline.py` — génération de 5 candidats, vérification anti-hallucination des sources, LLM Judge, audit des claims/recommendations/CTA, contrôle XPath et rapport machine-readable.
- `cicd/evidence-unit-quality-gate/action.yml` — GitHub composite action réutilisable.
- `.github/workflows/evidence-unit-quality-gate.yml` — dispatcher imposé par GitHub Actions.

## Pages

### Homepage

- [`Evidence selection — Judge v2.1`](pages/homepage/evidence-selection-judge-v2.1.json) — **20 EU avant / 20 après**, **4 substitutions dominantes**, run `homepage-eu-selection:2026-08-31:judge-v2.1`.

### `/expertises/blockchain/`

- [`Macro/Microeconomic EU Placement v2`](expertises/blockchain/macro-micro-economic-eu-placement-v2.md) — **17 EU macro/micro**, **10 séquences canoniques**, **5 candidats par XPath**, valeur propositionnelle et avatar ajustés au marché ; données techniques volontairement secondaires.
- [`Technical EU Placement audit v1`](expertises/blockchain/eu-placement-audit-v1.md) — audit technique antérieur : throughput, latence, preuve, sécurité et cryptographie.

Le v2 est le référentiel prioritaire pour le **sales copy** de la page Blockchain : il commence par le déplacement de valeur économique, puis contraint la promesse aux capacités démontrables. Le v1 reste exploitable comme couche de preuve technique en aval.
