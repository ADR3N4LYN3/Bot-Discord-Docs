# Specifications des Quotas AI - Optralis

## Resume

Documentation des quotas AI par plan tarifaire avec calcul des couts API Claude Sonnet 4.

---

## 1. Tarification API Claude Sonnet 4

### Prix Anthropic
| Type | Prix |
|------|------|
| Input tokens | $3 / 1M tokens |
| Output tokens | $15 / 1M tokens |

### Consommation moyenne par analyse
Base sur l'analyse des prompts dans `ai-service/internal/claude/prompts.go` :

| Composant | Tokens estimes |
|-----------|----------------|
| System prompt | ~600 |
| User prompt (metriques, logs, SMART data) | ~2,500 |
| **Total Input** | **~3,100** |
| Output JSON (analyse + recommandations) | ~900 |
| **Total Output** | **~900** |

### Cout unitaire par analyse
```
Input:  3,100 x $3 / 1,000,000  = $0.0093
Output:   900 x $15 / 1,000,000 = $0.0135
-----------------------------------------
TOTAL: $0.0228 (~$0.025 arrondi)
```

---

## 2. Quotas par Plan

### Tableau recapitulatif

| Plan | Prix | Quota/mois | Machines | Cout API | Marge | Premium |
|------|------|------------|----------|----------|-------|---------|
| **Starter** | 69 EUR | 150 | 25 | ~3.50 EUR | 95% | Non |
| **Essentials** | 149 EUR | 300 | 75 | ~7 EUR | 95% | Non |
| **Pro** | 269 EUR | 1,500 | 150 | ~35 EUR | 87% | Oui |
| **Business** | 549 EUR | 5,000 | 500 | ~115 EUR | 79% | Oui |
| **Enterprise** | Devis | 15,000 | Illimite | ~350 EUR | Var. | Oui |

### Detail par plan

#### Starter (69 EUR/mois - Cout API ~3.50 EUR)
- **Quota** : 150 analyses/mois
- **Machines** : 25 maximum
- **Ratio** : 6 analyses/machine/mois (~0.2/jour)
- **Features** : Health Score, Tendances (sans priorisation)
- **Cible** : TPE, petites structures

#### Essentials (149 EUR/mois - Cout API ~7 EUR)
- **Quota** : 300 analyses/mois
- **Machines** : 75 maximum
- **Ratio** : 4 analyses/machine/mois (~0.13/jour)
- **Features** : Comme Starter
- **Cible** : PME avec parc modere

#### Pro (269 EUR/mois - Cout API ~35 EUR)
- **Quota** : 1,500 analyses/mois
- **Machines** : 150 maximum
- **Ratio** : 10 analyses/machine/mois (~0.33/jour)
- **Features Premium** :
  - Routines automatiques (scheduler)
  - Triggers intelligents
  - Analyses predictives (degradation, intermittence)
  - Correlation cross-machine
  - Generation de rapports PDF
- **Cible** : ETI, entreprises avec besoins avances

#### Business (549 EUR/mois - Cout API ~115 EUR)
- **Quota** : 5,000 analyses/mois
- **Machines** : 500 maximum
- **Ratio** : 10 analyses/machine/mois (~0.33/jour)
- **Features** : Toutes les features Pro
- **Cible** : Grandes entreprises, MSP, infogerants

#### Enterprise (Sur devis - Cout API ~350 EUR)
- **Quota** : 15,000 analyses/mois
- **Machines** : Illimite
- **Usage typique** : Usage intensif + predictif avance
- **Features** : Toutes les features + configuration AI personnalisee
- **Justification** : Grands comptes, datacenters

---

## 3. Hierarchie des Features

```
Starter/Essentials (Base)
+-- POST /ai/analyze/logs
+-- POST /ai/analyze/anomalies
+-- POST /ai/analyze/full
+-- POST /ai/recommendations
+-- POST /ai/health-score
+-- POST /ai/analyze/trends
+-- POST /ai/scripts/generate

Pro/Business/Enterprise (Premium)
+-- Tout ce qui precede +
+-- POST /ai/analyze/degradation (Priorisation intelligente)
+-- POST /ai/analyze/intermittent (Detection d'intermittence)
+-- POST /ai/correlate (Correlation cross-machine)
+-- POST /ai/predictive/maintenance (Analyse groupee)
+-- Routines automatiques (scheduler)
+-- Triggers sur evenements
+-- Rapports PDF automatiques

Enterprise (Exclusif)
+-- Configuration AI personnalisee (context custom)
+-- Machines critiques/importantes
+-- Retention donnees etendue (365 jours)
```

---

## 4. Fichiers a Modifier (Reference)

### 4.1 Quotas - `ai-service/internal/services/quota.go`

Ligne 112-118, remplacer par :

```go
monthlyLimit := 150 // starter (nouveau: 150 au lieu de 200)
switch licenseType {
case "essentials":
    monthlyLimit = 300
case "pro":
    monthlyLimit = 1500
case "business":
    monthlyLimit = 5000
case "enterprise":
    monthlyLimit = 15000
}
```

### 4.2 Types de licence - `backend/internal/database/database.go`

Ligne 362-369, ajouter les nouveaux types :

```sql
INSERT INTO license_types (name, display_name_fr, display_name_en, default_machines_limit, default_duration_months)
VALUES
    ('trial', 'Essai', 'Trial', 5, 1),
    ('starter', 'Starter', 'Starter', 25, 12),
    ('essentials', 'Essentiels', 'Essentials', 75, 12),
    ('pro', 'Pro', 'Pro', 150, 12),
    ('business', 'Business', 'Business', 500, 12),
    ('enterprise', 'Entreprise', 'Enterprise', 9999, 12)
ON CONFLICT (name) DO UPDATE SET
    default_machines_limit = EXCLUDED.default_machines_limit;
```

### 4.3 Validation - `backend/internal/services/admin.go`

Ligne 225 :

```go
validTypes := map[string]bool{
    "trial": true,
    "starter": true,
    "essentials": true,
    "pro": true,
    "business": true,
    "enterprise": true,
}
```

### 4.4 Features Premium - `ai-service/internal/services/license.go`

Ligne 39, modifier pour inclure Business :

```go
isPremium := licenseType == "pro" || licenseType == "business" || licenseType == "enterprise"
```

### 4.5 Scheduler et Triggers

Fichiers concernes :
- `ai-service/internal/services/scheduler.go` (lignes 112, 215, 226, 238)
- `backend/internal/services/ai_triggers.go` (ligne 382, 506)
- `backend/internal/services/ai_routines.go` (ligne 441, 487)

Modifier les conditions :
```sql
-- Avant
WHERE c.license_type IN ('pro', 'enterprise')

-- Apres
WHERE c.license_type IN ('pro', 'business', 'enterprise')
```

---

## 5. Tarification et Marges

### Prix de vente valides

| Plan | Prix/mois | Cout API | Marge brute | Marge % |
|------|-----------|----------|-------------|---------|
| **Starter** | 69 EUR | ~3.50 EUR | 65.50 EUR | **95%** |
| **Essentials** | 149 EUR | ~7 EUR | 142 EUR | **95%** |
| **Pro** | 269 EUR | ~35 EUR | 234 EUR | **87%** |
| **Business** | 549 EUR | ~115 EUR | 434 EUR | **79%** |
| **Enterprise** | Sur devis | ~350 EUR | Variable | Variable |

> Conversion : 1$ = 0.92 EUR

### Analyse de rentabilite

**Toutes les marges sont excellentes** :
- Starter, Essentials : Marge ~95% - tres rentable
- Pro : Marge 87% - tres rentable
- Business : Marge 79% - rentable

**Progression tarifaire coherente** :
- Starter -> Essentials : +116% (69 EUR -> 149 EUR)
- Essentials -> Pro : +81% (149 EUR -> 269 EUR)
- Pro -> Business : +104% (269 EUR -> 549 EUR)
- Business -> Enterprise : Sur devis

### Notes importantes

1. **Couts variables** : Les couts API dependent de l'usage reel. Un client utilisant 50% de son quota = 50% du cout estime.

2. **Analyses complexes** : Les analyses de rapports PDF ou predictives consomment plus de tokens (~2x une analyse standard).

3. **Cache** : Le systeme de cache (30min TTL) reduit les appels API redondants.

4. **Cooldown** : Le systeme de cooldown empeche les analyses en rafale sur une meme machine.

---

## 6. Migration

### Clients existants

Pour les clients actuels avec les anciens plans :

| Ancien plan | Ancien quota | Nouveau plan suggere | Nouveau quota |
|-------------|--------------|---------------------|---------------|
| starter | 200 | starter | 150 (ajuster si necessaire) |
| pro | 1500 | pro | 1500 (inchange) |
| enterprise | 10000 | enterprise | 15000 (bonus) |

### Script de migration SQL

```sql
-- Ajouter les nouveaux types de licence
INSERT INTO license_types (name, display_name_fr, display_name_en, default_machines_limit)
VALUES
    ('essentials', 'Essentiels', 'Essentials', 75),
    ('business', 'Business', 'Business', 500)
ON CONFLICT (name) DO NOTHING;

-- Mettre a jour les limites existantes
UPDATE license_types SET default_machines_limit = 25 WHERE name = 'starter';
UPDATE license_types SET default_machines_limit = 150 WHERE name = 'pro';

-- Mettre a jour les quotas AI existants (optionnel)
UPDATE ai_quotas aq
SET monthly_limit = CASE
    WHEN c.license_type = 'starter' THEN 150
    WHEN c.license_type = 'essentials' THEN 300
    WHEN c.license_type = 'pro' THEN 1500
    WHEN c.license_type = 'business' THEN 5000
    WHEN c.license_type = 'enterprise' THEN 15000
    ELSE 150
END
FROM clients c
WHERE aq.client_id = c.id;
```

---

## 7. Monitoring des couts

### Metriques a suivre

1. **Usage mensuel par client** : `SELECT client_id, used_this_month FROM ai_quotas`
2. **Tokens consommes** : Logs du client Claude (`TokensInput`, `TokensOutput`)
3. **Cout reel** : `(input_tokens x $3 + output_tokens x $15) / 1,000,000`

### Alertes suggerees

- Client a 80% de son quota -> Notification
- Client a 100% de son quota -> Bloquer + proposition upgrade
- Cout API depassant marge prevue -> Alerte admin