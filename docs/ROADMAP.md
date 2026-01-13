# Roadmap Optralis 2026

*Basée sur l'analyse des 500+ commits, README et PROJECT_SPECS*
*Dernière mise à jour : Décembre 2026*

---

## Résumé Exécutif

### État Actuel

| Métrique | Valeur |
|----------|--------|
| **Plateformes** | Windows, Linux (amd64/arm64) |
| **Capacité** | ~500 machines / instance |
| **Features livrées** | 50+ depuis Oct 2025 |

### Récemment Livré (Q4 2025 - Déc 2026)

| Catégorie | Fonctionnalités |
|-----------|-----------------|
| **Monitoring** | Linux complet, IO Metrics, Inventaire détaillé, Hardware ID, Détection VM/Physique |
| **Alerting** | Multi-canal (Email/Teams/Slack/Discord), Règles avancées, Mode maintenance |
| **Sécurité** | MFA/2FA (TOTP), Multi-utilisateurs (Admin/Observer) |
| **IA (Beta)** | Service d'analyse AI, Résumé exécutif, Suggestions proactives |
| **Interface** | Export CSV, Page Status publique, Onglets lazy-loaded |

### Prochaines Priorités

| Priorité | Tâche | Trimestre |
|----------|-------|-----------|
| 🔴 Haute | Monitoring température Linux | Q1 2026 |
| 🔴 Haute | API publique (Swagger/OpenAPI) | Q2 2026 |
| 🟡 Moyenne | Rapports PDF automatiques | Q1 2026 |
| 🟡 Moyenne | SSO SAML 2.0 | Q2 2026 |
| 🟢 Basse | Application mobile | Q3 2026 |

---

## Analyse de l'état actuel

### Statistiques des 500 commits analysés

| Catégorie | Commits | % |
|-----------|---------|---|
| **Build/Installer** | ~120 | 24% |
| **Features** | ~100 | 20% |
| **Fixes** | ~150 | 30% |
| **UI/Style** | ~60 | 12% |
| **Documentation** | ~30 | 6% |
| **Performance** | ~20 | 4% |
| **Security** | ~20 | 4% |

### Fonctionnalités livrées (Timeline complète)

#### Décembre 2025 - Décembre 2026
| Fonctionnalité | Status | Commits |
|----------------|--------|---------|
| **AI Service (Beta)** | ✅ Livré | a97de9e |
| **IO Metrics Collection** | ✅ Livré | a97de9e |
| **Export CSV machines** | ✅ Livré | Dec 2025 |
| **Page Status système** | ✅ Livré | Dec 2025 |
| **Page Status publique (vitrine)** | ✅ Livré | c440ab7 |
| **Règles d'alertes avancées** (seuils configurables) | ✅ Livré | Dec 2025 |
| **MFA / 2FA (TOTP)** | ✅ Livré | Dec 2025 |
| **Mode maintenance** | ✅ Livré | Dec 2025 |
| **Intervalles de collecte configurables** | ✅ Livré | b5c58eb |
| Notifications multi-canal (Teams/Slack/Discord) | ✅ Livré | a466d57, ed8ad7f |
| Multi-utilisateurs par client (Admin/Observer) | ✅ Livré | e206fc9, 8e3b2b3 |
| Hardware ID (identification persistante) | ✅ Livré | f0c970f |
| Inventaire détaillé JSONB (onglets) | ✅ Livré | 1e8055d, 069038e |
| Collecte forcée (bouton admin) | ✅ Livré | 02dff18 |
| Services/ports enrichis (métadonnées) | ✅ Livré | 902bd16, 0f431e1 |
| Détection disques virtuels (SMART) | ✅ Livré | 2ab8eb1 |
| **Détection VM/Physique multi-méthodes** | ✅ Livré | 0314611 |
| Version antivirus (Windows Defender) | ✅ Livré | 106f26d |
| Buffer hors-ligne (100 entrées, 24h) | ✅ Livré | 66b25b3, 2688c72 |
| Filtres activity logs par client | ✅ Livré | bc263aa |
| Rappels expiration licence (email) | ✅ Livré | 4b17fa2, db6374e |
| Liste clients expandable | ✅ Livré | 42f1543 |
| Recherche/filtres par onglet | ✅ Livré | 2433873 |
| En-têtes sticky tableaux | ✅ Livré | 2433873 |
| Onglets lazy-loaded | ✅ Livré | 1e8055d |
| Plans tarifaires landing | ✅ Livré | 5bd4c5e |

#### Q4 2025 - Novembre/Octobre
| Fonctionnalité | Status | Commits |
|----------------|--------|---------|
| Support Linux (agents + canaux) | ✅ Livré | 8e84990, 1eb8e4e |
| Activity Logging System | ✅ Livré | ae7416e, 1f74c73 |
| Inventaire services/ports | ✅ Livré | 1e0e97a, c3cc17a |
| Sécurité tokens (rotation, CSRF, blacklist) | ✅ Livré | 8f3cddf, 99f24c1 |
| Cache Redis + optimisations perf | ✅ Livré | cfe65c2, aa4ac04 |
| Sidebar collapsible machine details | ✅ Livré | bcb2f98, 0d91c99 |
| Installateur GUI WebView2 | ✅ Livré | d8d0440, d1c5c64 |
| Auto-update agent | ✅ Livré | 832cbfc, e388cf5 |
| Désinstallateur GUI | ✅ Livré | c491438, f759de0 |
| Docker monitoring admin | ✅ Livré | a684ce6, ff47d73 |
| Architecture 3-tier collecte | ✅ Livré | 0dec449 |
| Canaux stable/beta | ✅ Livré | 85e8022, f8387ea |
| Windows Event Viewer logging | ✅ Livré | 5998d46 |

#### Q3 2025
| Fonctionnalité | Status | Commits |
|----------------|--------|---------|
| Système de canaux stable/beta | ✅ Livré | 85e8022, f8387ea |
| i18n complet FR/EN | ✅ Livré | d371005, 745c217, bbf2820 |
| Landing page animations | ✅ Livré | fe92513, 87f2b2c, ce6c984 |
| Password expiration 90 jours | ✅ Livré | d3aa716, a84ce36 |
| Impersonation admin | ✅ Livré | b786b77, 2186eb0, cd977cc |
| Dark/Light theme complet | ✅ Livré | f785875, 8ca543d, 6f21a59 |
| Mobile responsive | ✅ Livré | 71dc0bd, 60d5290, ce88863 |

#### Q2 2025
| Fonctionnalité | Status | Commits |
|----------------|--------|---------|
| Système de licences | ✅ Livré | e96c739, 357e389 |
| Email templates personnalisés | ✅ Livré | 3cba11f, c2824c9, 004335c |
| Dashboard overview | ✅ Livré | 98cfceb, 97075ce |
| Architecture 3-tier collecte | ✅ Livré | 0dec449 |
| CustomSelect components | ✅ Livré | cac5e55, 521185d |
| Cookie consent GDPR | ✅ Livré | c15f517 |

### Architecture actuelle

```
Plateformes supportées : Windows, Linux (amd64/arm64)
Backend : Go 1.25+ / Fiber / PostgreSQL 16 + TimescaleDB + Redis
Frontend : Next.js 14 / TypeScript / Tailwind CSS
Déploiement : Docker Compose / Caddy (SSL auto)
```

### Limites actuelles estimées

| Composant | Configuration | Limite estimée |
|-----------|---------------|----------------|
| API Go | 1 instance | ~500 machines |
| PostgreSQL | 1 instance | ~1000 machines |
| Rate limit | 3000 req/min | OK pour 10s interval |
| Redis | 128 MB LRU | ~85% hit rate |

### Tendances identifiées dans les commits

```
📈 Forte activité      📊 Activité moyenne      📉 Activité faible
```

| Domaine | Tendance | Observation |
|---------|----------|-------------|
| **Agent Windows** | 📈 | ~120 commits build/installer - mature |
| **Agent Linux** | 📊 | Récent, en croissance |
| **Dashboard UX** | 📈 | Itérations continues, polish important |
| **Sécurité** | 📊 | Sprint récent Q4 2025 |
| **Performance** | 📊 | Optimisations ponctuelles mais significatives |
| **Landing/Marketing** | 📈 | Beaucoup d'efforts sur les animations |
| **Documentation** | 📉 | Présente mais pourrait être enrichie |
| **Tests automatisés** | 📉 | Peu de commits liés aux tests |
| **API publique** | 📉 | Pas encore implémentée |
| **Mobile** | 📉 | Responsive uniquement, pas d'app native |

### Dette technique identifiée

| Élément | Priorité | Impact | Notes |
|---------|----------|--------|-------|
| Documentation API | Moyenne | Frein aux intégrations | Prépare l'API publique |
| Monitoring des erreurs (Sentry/etc) | Moyenne | Debug production | |
| Tests E2E | Basse | - | Workflow actuel = itérations, pas régressions |
| CI/CD pipeline | Basse | - | Pas prioritaire pour dev solo |
| Logs centralisés | Basse | - | Déjà Activity logs |

> **Note** : Les tests E2E et CI/CD ont été réévalués. Le workflow actuel consiste en itérations successives pour trouver la bonne solution (processus normal), et non en régressions (casser du code existant). Ces outils deviendraient prioritaires en cas de travail en équipe ou de releases fréquentes automatisées.

---

## Quick Wins recommandés (1-3 jours chacun)

Basés sur les patterns de développement observés dans les commits :

| Quick Win | Effort | Valeur | Justification |
|-----------|--------|--------|---------------|
| **Swagger/OpenAPI** | 2-3j | Moyenne | Prépare l'API publique |
| **Agent macOS** | 3-5j | Moyenne | Extension naturelle du multi-plateforme |
| **Muting/Maintenance windows** | 1-2j | Moyenne | Désactiver alertes pendant maintenance |
| ~~**Notifications Slack/Teams**~~ | ~~1-2j~~ | ~~Haute~~ | ✅ Livré |
| ~~**Export CSV métriques**~~ | ~~1j~~ | ~~Moyenne~~ | ✅ Livré |
| ~~**Page Status (uptime)**~~ | ~~2-3j~~ | ~~Moyenne~~ | ✅ Livré |
| ~~**CI/CD basique**~~ | ~~2-3j~~ | ~~Haute~~ | Réévalué : pas prioritaire pour dev solo |
| ~~**Tests unitaires critiques**~~ | ~~2-3j~~ | ~~Haute~~ | Réévalué : workflow = itérations, pas régressions |

---

## Roadmap Q1 2026 (Janvier - Mars)

### Phase 1 : Consolidation Linux & Stabilité

**Priorité : Haute**

| Tâche | Description | Effort | Priorité |
|-------|-------------|--------|----------|
| Monitoring température Linux | Support des capteurs via lm-sensors | S | 🔴 Haute |
| Packaging Linux | .deb/.rpm packages pour déploiement entreprise | M | 🟡 Moyenne |
| Amélioration install.sh | Script avec détection distro, vérifications | S | 🟡 Moyenne |
| ~~Tests E2E Linux~~ | ~~Suite de tests automatisés pour agent Linux~~ | ~~M~~ | Réévalué → Basse |

> **Note Tests E2E** : Réévalué car le workflow actuel (itérations successives) ne génère pas de régressions. À reconsidérer si l'équipe s'agrandit.

### Phase 2 : Alerting Avancé

**Priorité : Haute** - ✅ Partiellement livré

| Tâche | Description | Effort |
|-------|-------------|--------|
| ~~Slack/Teams webhooks~~ | ~~Notifications vers outils de collaboration~~ | ✅ Livré |
| ~~Règles d'alertes configurables~~ | ~~Seuils CPU/RAM/disque par machine ou groupe~~ | ✅ Livré |
| Escalation policies | Alertes graduelles (email → SMS → appel) | L |
| Muting/Maintenance windows | Désactiver alertes pendant maintenance | S |

### Phase 3 : Dashboard Analytics

**Priorité : Moyenne** - ✅ Partiellement livré

| Tâche | Description | Effort |
|-------|-------------|--------|
| Rapports PDF automatiques | Génération hebdo/mensuel par client | M |
| Comparaison temporelle | Métriques semaine vs semaine précédente | M |
| ~~Export données CSV/Excel~~ | ~~Export des métriques et événements~~ | ✅ Livré |
| Widgets personnalisables | Dashboard overview customisable | L |

#### Détails Rapports PDF/HTML

**Fichiers** :
- `backend/internal/reports/generator.go` - Générateur PDF/HTML
- `backend/internal/reports/scheduler.go` - Génération automatique
- `backend/internal/reports/templates/` - Templates HTML

**Templates de rapports** :
- **Exécutif** : Résumé haut niveau, KPIs, santé globale
- **Technique** : Détails métriques, graphiques, incidents
- **Compliance** : Audit, conformité, checklist sécurité

**Endpoints API** :
- `GET /api/reports/executive/:clientId` - Rapport exécutif
- `GET /api/reports/technical/:machineId` - Rapport technique machine
- `GET /api/reports/compliance/:clientId` - Rapport compliance
- Query params : `?format=pdf|html&period=week|month|quarter`

**Automatisation** :
- Génération automatique hebdomadaire/mensuelle (cron)
- Envoi par email aux contacts client
- Stockage historique des rapports

---

## Roadmap Q2 2026 (Avril - Juin)

### Phase 4 : API & Intégrations

**Priorité : Haute**

| Tâche | Description | Effort |
|-------|-------------|--------|
| API publique documentée | Endpoints REST avec Swagger/OpenAPI | M |
| Webhooks sortants | Notifications HTTP pour intégrations | M |
| Intégration PagerDuty | Alertes vers PagerDuty | S |
| Intégration Grafana | Export métriques Prometheus format | M |

### Phase 5 : Authentification Entreprise

**Priorité : Moyenne** - ✅ Partiellement livré

| Tâche | Description | Effort |
|-------|-------------|--------|
| SSO SAML 2.0 | Single Sign-On pour entreprises | L |
| OAuth 2.0 / OIDC | Google/Microsoft/Okta login | L |
| ~~MFA / 2FA~~ | ~~Authentification multi-facteur (TOTP)~~ | ✅ Livré |
| Audit logs détaillés | Qui a fait quoi, quand, où | M |

### Phase 6 : Performance & Scalabilité

**Priorité : Moyenne**

**Objectif : Supporter 300 clients / 10K endpoints**

| Tâche | Description | Effort |
|-------|-------------|--------|
| Sharding TimescaleDB | Distribution données multi-node | L |
| Read replicas | Réplication lecture pour dashboards | M |
| Connection pooling PgBouncer | Pool connexions pour haute charge | S |
| CDN assets statiques | Accélération frontend mondial | S |

#### Phases de scaling

**Phase 6a : Optimisations sans changement d'architecture**
- [ ] Connection pooling PostgreSQL (PgBouncer, pool_size=50)
- [ ] Index optimisés sur les tables critiques
- [ ] Compression des données historiques (TimescaleDB chunks)
- [ ] Cache Redis étendu (TTL optimisés)

**Phase 6b : Scaling horizontal**
- [ ] Load balancer (Traefik/HAProxy) devant l'API
- [ ] 2-3 réplicas API Go (stateless)
- [ ] PostgreSQL read replicas pour les requêtes dashboard
- [ ] Redis cluster pour le cache distribué

**Phase 6c : Architecture haute disponibilité**
- [ ] PostgreSQL HA (Patroni ou managed RDS)
- [ ] Multi-région si nécessaire
- [ ] Message queue (NATS/RabbitMQ) pour découpler les writes

#### Architecture cible (10K+ endpoints)

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │ (Traefik/HAProxy)│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ API #1  │         │ API #2  │         │ API #3  │
   │  (Go)   │         │  (Go)   │         │  (Go)   │
   └────┬────┘         └────┬────┘         └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
        │   Redis   │  │ PostgreSQL │  │  Redis   │
        │  (Cache)  │  │  (Primary) │  │ (Queue)  │
        └───────────┘  └─────┬─────┘  └───────────┘
                             │
                    ┌────────▼────────┐
                    │   Read Replica  │
                    │  (Dashboard)    │
                    └─────────────────┘
```

#### Estimations ressources serveur

| Charge | RAM | CPU | Stockage | Coût estimé/mois |
|--------|-----|-----|----------|------------------|
| 500 machines | 4 GB | 2 vCPU | 50 GB | ~20€ |
| 2000 machines | 8 GB | 4 vCPU | 200 GB | ~50€ |
| 10K machines | 32 GB | 8 vCPU | 1 TB | ~150€ (multi-instance) |

---

## Roadmap Q3 2026 (Juillet - Septembre)

### Phase 7 : Monitoring Réseau

**Priorité : Moyenne**

| Tâche | Description | Effort |
|-------|-------------|--------|
| Ping/latence réseau | Monitoring connectivité entre machines | M |
| Bande passante | Mesure débit réseau par interface | M |
| DNS monitoring | Résolution DNS et latence | S |
| Traceroute automatique | Diagnostic problèmes réseau | S |

### Phase 8 : Automatisation & Remediation

**Priorité : Basse**

| Tâche | Description | Effort |
|-------|-------------|--------|
| Scripts remediation | Actions automatiques (restart service, clear disk) | L |
| Playbooks | Séquences d'actions prédéfinies | L |
| Approbation workflow | Validation avant actions critiques | M |
| Agent remote commands | Exécution commandes à distance sécurisée | L |

### Phase 9 : Application Mobile

**Priorité : Basse**

| Tâche | Description | Effort |
|-------|-------------|--------|
| App React Native | iOS/Android natif | XL |
| Push notifications | Alertes temps réel sur mobile | M |
| Dashboard mobile | Vue condensée des métriques | M |
| Actions rapides | Acknowledge alertes, restart services | M |

---

## Roadmap Q4 2026 (Octobre - Décembre)

### Phase 10 : Intelligence Artificielle

**Priorité : Basse** - ✅ Partiellement livré (AI Service Beta)

| Tâche | Description | Effort | Status |
|-------|-------------|--------|--------|
| ~~Service AI~~ | ~~Analyse métriques, suggestions~~ | M | ✅ Livré (Beta) |
| ~~Résumé exécutif~~ | ~~Rapport de santé automatique~~ | S | ✅ Livré (Beta) |
| ~~Analyse d'incidents~~ | ~~Explication alertes~~ | S | ✅ Livré (Beta) |
| Prédiction pannes | ML sur données S.M.A.R.T disques | XL | À faire |
| Détection anomalies (EWMA) | Alertes comportements inhabituels | XL | À faire |
| Chatbot support | Assistant IA pour troubleshooting | XL | À faire |

#### 10a : Service IA Claude + Fallback OpenAI

**Fichier** : `backend/internal/services/ai_service.go`

**Endpoints API** :
- `POST /api/ai/analyze-metrics` - Analyse des métriques d'une machine
- `POST /api/ai/suggestions` - Suggestions d'optimisation
- `POST /api/ai/summary` - Résumé exécutif d'un client/parc
- `POST /api/ai/incident-analysis` - Analyse d'incident/alerte

**Cas d'usage** :
- Résumé hebdomadaire automatique par client
- Analyse des tendances (prédiction saturation disque)
- Suggestions proactives ("3 machines ont >90% RAM depuis 7j")
- Explication des alertes en langage naturel

#### 10b : Analyse Comportementale EWMA / Z-Score

**Fichiers** :
- `backend/internal/analytics/ewma.go` - Calculs EWMA
- `backend/internal/analytics/zscore.go` - Détection anomalies
- `backend/internal/analytics/baseline.go` - Gestion baselines

**Fonctionnalités** :
- Calcul EWMA sur : CPU, RAM, Disque, Réseau
- Z-score par rapport à la baseline (z > 2 = warning, z > 3 = critical)
- Détection anomalies positives ET négatives
- Corrélation entre métriques (CPU + RAM = probable problème applicatif)

**Schema DB** :
```sql
CREATE TABLE metric_baselines (
    id UUID PRIMARY KEY,
    machine_id UUID REFERENCES machines(id),
    metric_name VARCHAR(50),  -- 'cpu', 'ram', 'disk_c', etc.
    ewma_value DOUBLE PRECISION,
    ewma_variance DOUBLE PRECISION,
    sample_count INTEGER,
    last_updated TIMESTAMPTZ
);
```

### Phase 11 : Multi-cloud & Intégrations Cloud

**Priorité : Basse**

| Tâche | Description | Effort |
|-------|-------------|--------|
| AWS CloudWatch | Import métriques EC2/RDS | L |
| Azure Monitor | Import métriques Azure VMs | L |
| GCP Stackdriver | Import métriques GCP | L |
| Kubernetes | Monitoring pods/nodes K8s | XL |

---

## Légende Effort

| Code | Signification | Durée estimée |
|------|---------------|---------------|
| S | Small | 1-3 jours |
| M | Medium | 1-2 semaines |
| L | Large | 2-4 semaines |
| XL | Extra Large | 1-2 mois |

---

## Priorités recommandées

### Court terme (Immédiat)
1. **Alerting avancé** - Demande forte des clients
2. **Consolidation Linux** - Stabiliser la nouvelle plateforme
3. **Rapports PDF** - Valeur ajoutée visible

### Moyen terme (6 mois)
1. **API publique** - Ouvre les intégrations
2. **SSO/MFA** - Requis pour entreprises
3. **Monitoring réseau** - Complète l'offre

### Long terme (12 mois)
1. **Application mobile** - Différenciation marché
2. **IA/ML** - Innovation et valeur ajoutée
3. **Multi-cloud** - Marché en croissance

---

## KPIs suggérés

| Métrique | Objectif Q1 | Objectif Q4 |
|----------|-------------|-------------|
| Machines monitorées | +50% | +200% |
| Clients actifs | +30% | +100% |
| Temps détection panne | < 1 min | < 30 sec |
| Uptime API | 99.5% | 99.9% |
| MTTR (Mean Time To Resolution) | < 2h | < 30 min |

---

## Risques identifiés

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Support Linux fragmenté (distros) | Moyen | Focus sur Ubuntu/Debian/RHEL |
| Charge TimescaleDB | Élevé | Sharding + optimisation retention |
| Sécurité agent remote | Critique | Audit externe, zero-trust |
| Adoption mobile | Faible | MVP rapide, feedback users |

---

## Vision Produit 2026

### Positionnement

```
Aujourd'hui : Solution de monitoring infrastructure pour PME françaises
Demain : Plateforme observabilité complète multi-cloud pour entreprises
```

### Axes stratégiques

| Axe | Description | Horizon |
|-----|-------------|---------|
| **Consolidation** | Stabiliser Linux, tests, CI/CD | Q1 2026 |
| **Expansion** | macOS, API publique, intégrations | Q2 2026 |
| **Différenciation** | IA prédictive, remediation auto | Q3-Q4 2026 |
| **Scalabilité** | Multi-cloud, enterprise features | 2026 |

### Concurrence & Différenciation

| Concurrent | Points forts | Opportunité Optralis |
|------------|--------------|---------------------|
| Datadog | Complet mais cher | Prix PME + support FR |
| Zabbix | Open source | Interface moderne + SaaS |
| PRTG | Windows natif | Multi-plateforme + cloud |
| Nagios | Historique | UX moderne + ML |

### Métriques de succès suggérées

| Métrique | Q1 2026 | Q2 2026 | Q4 2026 |
|----------|---------|---------|---------|
| Clients actifs | +20% | +50% | +150% |
| Machines monitorées | +30% | +80% | +250% |
| MTTR | < 1h | < 45min | < 15min |
| Uptime API | 99.5% | 99.8% | 99.95% |
| NPS Score | 30+ | 40+ | 50+ |
| Churn mensuel | < 5% | < 3% | < 2% |

---

## Recommandations stratégiques

### Court terme (Immédiat - Q1)

1. **CI/CD prioritaire** - Automatiser les 120+ builds manuels observés
2. **Tests critiques** - Réduire les régressions (150 fixes dans 500 commits)
3. **Alerting Slack/Teams** - ROI rapide, demande forte
4. **Consolider Linux** - Le support récent doit mûrir

### Moyen terme (Q2-Q3)

1. **API publique** - Ouvre le marché des intégrations
2. **SSO entreprise** - Requis pour contrats enterprise
3. **macOS** - Complète l'offre multi-plateforme
4. **Rapports automatiques** - Valeur visible pour les décideurs

### Long terme (Q4+)

1. **IA prédictive** - Différenciation concurrentielle
2. **Application mobile** - Mobilité des équipes IT
3. **Multi-cloud** - Marché en croissance rapide

---

## Cycle de release suggéré

```
┌─────────────────────────────────────────────────────────────┐
│                    CYCLE BI-MENSUEL                         │
├─────────────────────────────────────────────────────────────┤
│ Semaine 1-2 : Développement features                        │
│ Semaine 3   : Tests + stabilisation                         │
│ Semaine 4   : Release stable + documentation                │
├─────────────────────────────────────────────────────────────┤
│ Beta : Disponible en continu pour early adopters            │
│ Stable : Release tous les 15 jours                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Modules Futurs

Structure proposée pour les nouveaux modules :

```
backend/internal/
├── services/
│   └── ai_service.go          # Service IA (Claude + OpenAI)
├── analytics/
│   ├── ewma.go                 # Calculs EWMA
│   ├── zscore.go               # Détection anomalies
│   └── baseline.go             # Gestion baselines
├── reports/
│   ├── generator.go            # Générateur PDF/HTML
│   ├── templates/
│   │   ├── executive.html
│   │   ├── technical.html
│   │   └── compliance.html
│   └── scheduler.go            # Génération automatique
└── cache/
    └── redis.go                # Cache distribué (existant)
```

---

## Variables d'Environnement Futures

```env
# Connection pooling (Phase 6)
PGBOUNCER_ENABLED=true
PGBOUNCER_POOL_SIZE=50

# Clustering (Phase 6)
API_INSTANCE_ID=api-1
LOAD_BALANCER_HEALTH_PATH=/health

# AI Configuration (Phase 10)
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
AI_PRIMARY_PROVIDER=claude
AI_FALLBACK_ENABLED=true

# Analytics EWMA (Phase 10)
EWMA_ALPHA=0.3
ZSCORE_WARNING_THRESHOLD=2.0
ZSCORE_CRITICAL_THRESHOLD=3.0

# Reports (Phase 3)
REPORTS_STORAGE_PATH=/srv/reports
REPORTS_AUTO_GENERATE=true
REPORTS_SCHEDULE=0 8 * * 1    # Cron: Lundi 8h

# Webhooks (Phase 2 & 4)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/...
PAGERDUTY_API_KEY=...
```

---

## Notes

Cette roadmap est basée sur :
- **500 commits** analysés (56b86de → premiers commits projet)
- **README.md** (735 lignes)
- **PROJECT_SPECS.md** (1302 lignes)

### Observations clés des commits

- **24% des commits** sont des builds/installers → besoin CI/CD
- **30% des commits** sont des fixes → besoin de tests
- **Forte itération UX** → bonne sensibilité produit
- **Sécurité récente** → fondations solides
- **Performance optimisée** → prêt pour la croissance

Les priorités peuvent être ajustées selon :
- Retours clients (NPS, support tickets)
- Évolution du marché
- Ressources disponibles
- Opportunités business

---

*Document généré le 19 décembre 2025, mis à jour janvier 2026*
*Fusion de ROADMAP_FUTURE.md + analyse 500 commits*
*Projet : Optralis - Solution SaaS de monitoring d'infrastructure*
*Entreprise : 2 LACS INFORMATIQUE*
*Analyse : 500 commits, README, PROJECT_SPECS*
