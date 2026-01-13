# Base de Données & Sécurité - Spécifications Techniques

## Vue d'ensemble

PostgreSQL avec TimescaleDB pour les séries temporelles, Redis pour le cache, et architecture de sécurité complète.

---

## TimescaleDB

Tables converties en hypertables avec compression automatique:

| Table | Intervalle chunk | Compression | Rétention |
|-------|-----------------|-------------|-----------|
| `metrics` | 1 jour | Après 2 jours | Par licence |
| `disk_info` | 1 jour | Après 2 jours | Par licence |
| `event_logs` | 1 jour | Après 2 jours | Par licence |
| `smart_data` | 1 jour | Après 2 jours | Par licence |
| `activity_logs` | 1 jour | Après 2 jours | 30 jours (fixe) |
| `service_uptime` | 1 jour | Après 2 jours | 30 jours (fixe) |

### Tables Snapshot (non time-series)

| Table | Description | Stratégie |
|-------|-------------|-----------|
| `machine_collector_data` | Dernière valeur de chaque collector par machine | UPSERT (ON CONFLICT DO UPDATE) |
| `machine_inventory` | Données enrichies backward-compat | UPDATE |

La table `machine_collector_data` stocke le dernier snapshot JSON de chaque collector :
- Clé unique : `(machine_id, collector)`
- Collectors : `metrics`, `storage`, `storage_health`, `network`, `services`, `security`, `software`, `patches`

### Colonnes `disk_info` (time-series)

| Colonne | Type | Description |
|---------|------|-------------|
| `mount_point` | VARCHAR(255) | Point de montage (C:\, /, etc.) |
| `device` | VARCHAR(255) | Périphérique (/dev/sda1, etc.) |
| `fs_type` | VARCHAR(50) | Type de système de fichiers (NTFS, ext4, etc.) |
| `total_gb` | DECIMAL(10,2) | Capacité totale en Go |
| `used_gb` | DECIMAL(10,2) | Espace utilisé en Go |
| `used_percent` | DECIMAL(5,2) | Pourcentage d'utilisation |
| `model` | VARCHAR(255) | Modèle du disque |
| `interface` | VARCHAR(50) | Interface (SATA, NVMe, etc.) |

### Colonnes `machine_inventory` (snapshot)

| Colonne | Type | Collector source | Description |
|---------|------|------------------|-------------|
| `antivirus_name` | VARCHAR(255) | security | Nom de l'antivirus |
| `antivirus_version` | TEXT | security | Version de l'antivirus |
| `antivirus_enabled` | BOOLEAN | security | Antivirus activé |
| `antivirus_updated` | BOOLEAN | security | Définitions à jour |
| `firewall_enabled` | BOOLEAN | security | Pare-feu activé |
| `bitlocker_enabled` | BOOLEAN | security | Chiffrement BitLocker |
| `secure_boot_enabled` | BOOLEAN | security | Secure Boot activé |
| `services_total` | INT | services | Nombre total de services |
| `services_running` | INT | services | Services en cours |
| `services_failed` | INT | services | Services en échec |
| `all_services` | JSONB | services | Liste complète des services |
| `failed_services` | JSONB | services | Détails des services échoués |
| `software_count` | INT | software | Nombre de logiciels installés |
| `software_details` | JSONB | software | Liste des logiciels |
| `users_total` | INT | software | Nombre d'utilisateurs locaux |
| `users_admin` | INT | software | Nombre d'admins |
| `users_details` | JSONB | software | Détails des utilisateurs |
| `ports_open` | INT | security | Ports en écoute |
| `ports_risky_open` | INT | security | Ports risqués ouverts |
| `all_ports` | JSONB | security | Liste de tous les ports |
| `risky_ports_details` | JSONB | security | Détails ports risqués |
| `network_interfaces` | JSONB | network | Interfaces réseau (MAC, IPs, état) |
| `pending_updates` | INT | patches | Mises à jour en attente |
| `security_updates` | INT | patches | Mises à jour de sécurité |
| `reboot_required` | BOOLEAN | patches | Redémarrage requis |
| `patches_auto_update` | BOOLEAN | patches | Auto-update Windows activé |
| `patches_last_check` | TIMESTAMPTZ | patches | Dernière vérif Windows Update |

---

## Rétention par Licence

| Licence | Métriques & Agrégats | Événements |
|---------|---------------------|------------|
| Trial | 7 jours | 7 jours |
| Starter | 30 jours | 30 jours |
| Pro | 90 jours | 90 jours |
| Enterprise | Personnalisée (6-24 mois) | Personnalisée (6-24 mois) |

> **Note** : Les agrégats (résumés horaires) suivent la même rétention que les métriques brutes.

---

## Système de Cleanup

### Architecture Hybride

Le système utilise une approche hybride combinant :
1. **Cleanup Go manuel** : Granularité par client selon sa licence
2. **TimescaleDB natif** : Filet de sécurité automatique (365 jours max)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cleanup Routine (1h)                          │
│                                                                  │
│  CleanupOldData() - Par client selon licence                    │
│  ├── metrics (MetricsRetentionDays)                             │
│  ├── disk_info (MetricsRetentionDays)                           │
│  ├── event_logs (EventsRetentionDays)                           │
│  ├── smart_data (MetricsRetentionDays)                          │
│  └── metric_aggregates (MetricsRetentionDays)                   │
│                                                                  │
│  cleanupSecondaryTables() - Global avec rétention fixe          │
│  ├── notification_history (30 jours)                            │
│  ├── alert_rule_history (90 jours)                              │
│  ├── ai_analysis_results (expires_at ou 90 jours)               │
│  ├── ai_trigger_history (90 jours)                              │
│  └── ai_routine_history (90 jours)                              │
└─────────────────────────────────────────────────────────────────┘
                              +
┌─────────────────────────────────────────────────────────────────┐
│            TimescaleDB Native (Filet de sécurité)               │
│  add_retention_policy('table', INTERVAL '365 days')             │
│  → Suppression automatique des chunks > 365 jours               │
└─────────────────────────────────────────────────────────────────┘
```

### Tables avec rétention par licence

| Table | Colonne rétention | Cleanup par |
|-------|-------------------|-------------|
| `metrics` | MetricsRetentionDays | Client |
| `disk_info` | MetricsRetentionDays | Client |
| `event_logs` | EventsRetentionDays | Client |
| `smart_data` | MetricsRetentionDays | Client |
| `metric_aggregates` | MetricsRetentionDays | Client |

### Tables avec rétention fixe (global)

| Table | Rétention | Condition |
|-------|-----------|-----------|
| `notification_history` | 30 jours | sent_at |
| `alert_rule_history` | 90 jours | triggered_at |
| `ai_analysis_results` | expires_at ou 90 jours | created_at |
| `ai_trigger_history` | 90 jours | executed_at |
| `ai_routine_history` | 90 jours | executed_at |
| `metric_baselines` | N/A (snapshot) | last_updated |
| `activity_logs` | 30 jours | TimescaleDB natif |
| `service_uptime` | 30 jours | TimescaleDB natif |

### Table `metric_baselines` (drift detection)

Stocke les baselines statistiques et les dérives détectées par machine.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | UUID | Identifiant unique |
| `machine_id` | UUID (FK) | Référence vers machines |
| `metric_type` | VARCHAR(50) | Type de métrique (cpu_percent, ram_percent, disk_latency_ms) |
| `baseline_mean` | DECIMAL(10,2) | Moyenne mobile sur 7 jours |
| `baseline_stddev` | DECIMAL(10,2) | Écart-type sur 7 jours |
| `baseline_p95` | DECIMAL(10,2) | Percentile 95 |
| `current_value` | DECIMAL(10,2) | Valeur actuelle (dernière heure) |
| `z_score` | DECIMAL(10,2) | Score Z calculé |
| `warning_threshold` | DECIMAL(5,2) | Seuil warning (défaut: 2.0) |
| `critical_threshold` | DECIMAL(5,2) | Seuil critical (défaut: 3.0) |
| `drift_detected` | BOOLEAN | Dérive détectée |
| `drift_severity` | VARCHAR(20) | Sévérité: warning, critical |
| `drift_explanation` | TEXT | Explication générée par Claude API |
| `last_updated` | TIMESTAMPTZ | Dernière mise à jour |

**Contrainte** : UNIQUE(machine_id, metric_type)

### Politiques TimescaleDB natives

Filet de sécurité pour garantir qu'aucune donnée > 365 jours ne reste :

```sql
SELECT add_retention_policy('metrics', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('disk_info', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('event_logs', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('smart_data', INTERVAL '365 days', if_not_exists => TRUE);
SELECT add_retention_policy('activity_logs', INTERVAL '30 days', if_not_exists => TRUE);
```

### Logging

Toutes les suppressions sont loggées :
```
[Cleanup] Deleted 1234 rows from metrics for client abc123
[Cleanup] Deleted 56 rows from notification_history (global)
```

**Fichiers concernés** :
- `backend/internal/services/machines/cleanup.go` : CleanupOldData(), cleanupSecondaryTables()
- `backend/internal/database/database.go` : configureRetentionPolicy()
- `backend/cmd/api/main.go` : startCleanupRoutine()

---

## Continuous Aggregates

Vues matérialisées TimescaleDB pour l'agrégation horaire des métriques, utilisées pour les filtres longue durée (7j, 30j).

### Vues créées

| Vue | Table source | Métriques agrégées |
|-----|--------------|-------------------|
| `metrics_hourly` | `metrics` | cpu_avg/min/max, ram_avg/min/max, cpu_temp_avg/min/max |
| `disk_hourly` | `disk_info` | disk_usage_avg/max |
| `network_hourly` | `metrics` | bytes_recv/sent_avg/max, packet_loss_avg/max, latency_avg/max |

### Politique de rafraîchissement

```sql
SELECT add_continuous_aggregate_policy('metrics_hourly',
    start_offset => INTERVAL '31 days',  -- Couvre 31 jours d'historique
    end_offset => INTERVAL '1 hour',      -- Exclut l'heure en cours (données non finalisées)
    schedule_interval => INTERVAL '1 hour', -- Rafraîchit toutes les heures
    if_not_exists => TRUE
)
```

**Important** : Le `start_offset` de 31 jours garantit que toutes les données historiques sont agrégées, pas seulement les données récentes.

### Rafraîchissement initial

Au démarrage du backend, les données historiques sont matérialisées :

```sql
CALL refresh_continuous_aggregate('metrics_hourly', NULL, NOW())
```

### Fallback vers données brutes

Si la vue agrégée contient moins de 5 points (ex: base nouvellement créée), le système utilise automatiquement les données brutes avec échantillonnage horaire :

```sql
SELECT DISTINCT ON (date_trunc('hour', recorded_at))
    id, machine_id, cpu_percent, ram_percent, ...
FROM metrics
WHERE machine_id = $1 AND recorded_at > NOW() - INTERVAL '1 hour' * $2
ORDER BY date_trunc('hour', recorded_at), recorded_at DESC
```

**Fichiers concernés** :
- `backend/internal/database/database.go` : Création des vues et politiques
- `backend/internal/services/machines/queries.go` : Requêtes CPU/RAM avec fallback
- `backend/internal/services/machines/network_metrics.go` : Requêtes réseau avec fallback

---

## Intervalle Dynamique

| État machine | Intervalle | Condition |
|--------------|------------|-----------|
| Alerte | 30 secondes | CPU > 80% OU RAM > 85% |
| Normal | 60 secondes | Valeur par défaut |

---

## Optimisations Performance

### Backend / API

| Optimisation | Description | Impact |
|--------------|-------------|--------|
| **Driver pgx** | Remplace lib/pq (driver natif Go) | 2-3x plus rapide |
| **JSON Encoder** | go-json au lieu de encoding/json | 2-3x plus rapide |
| **Compression Gzip** | Middleware Fiber LevelBestSpeed | ~70% réduction |
| **Timeouts HTTP** | Read: 30s, Write: 30s, Idle: 120s | Protection timeout |
| **Statement Timeout** | 30s max par query PostgreSQL | Prévention queries longues |
| **Request ID** | Header X-Request-ID pour tracing | Debug facilité |
| **Transaction Grouping** | Opérations heartbeat en 1 transaction | -80% round-trips DB |
| **Queries Parallèles** | getMachineDetails : 4 queries en parallèle | ~3x plus rapide |
| **Rate Limiting** | 3000 req/min heartbeat, 5 req/15min auth | Protection DoS |
| **Cloudflare Gzip** | Détection décompression proxy via magic bytes | Compatibilité CDN |

### Base de Données

| Optimisation | Description | Impact |
|--------------|-------------|--------|
| **Connection Pool** | 25 max, 10 idle, 5min lifetime | Réutilisation connexions |
| **Index Fonctionnel** | Index sur LOWER(hostname) | Queries hostname rapides |
| **Index client_id** | Index sur machines(client_id) | Queries instantanées |
| **DELETE avec JOIN** | Cleanup utilise USING au lieu de subquery | O(1) vs O(n) |
| **Batch Inserts** | Insertion groupée disks/events/smart_data | 10-50x plus rapide |
| **Hypertables** | TimescaleDB avec compression auto | -90% stockage |
| **Continuous Aggregates** | metrics_hourly, disk_hourly pré-calculés | Dashboards rapides |

### Résumé des Gains

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Queries/heartbeat | ~6 | ~1 (transaction) | -83% |
| Cache hit rate | 0% | ~85% | +85% |
| Machine details latency | ~50ms | ~15ms | -70% |
| JSON encoding | 1x | 2-3x | +200% |
| Stockage DB (compression) | 100% | ~10% | -90% |

---

## Cache Redis

Service Redis optionnel avec **dégradation gracieuse** (l'API fonctionne sans Redis).

### Configuration Docker

- Image: `redis:7-alpine`
- Mémoire max: 128MB avec politique LRU (`allkeys-lru`)
- Persistance: AOF (`appendonly yes`)
- Healthcheck: `redis-cli ping`

### TTLs configurés

| Donnée | TTL | Clé | Usage |
|--------|-----|-----|-------|
| Client (ID) | 5 min | `client:id:<uuid>` | Lookups API, mTLS auth |
| Machine count | 1 min | `machines:count:<clientID>` | Validation licence |
| Machine list | 30 sec | `machines:list:<clientID>` | Dashboard |
| Agent version | 5 min | `agent:version:<channel>` | Auto-update |

### Invalidation automatique

- `InvalidateMachineCache(clientID)` appelé lors de création/suppression de machines
- Supprime les clés `machines:count:*` et `machines:list:*` du client

---

## Sécurité

### Authentification

- JWT avec refresh tokens (15min access, 7j refresh)
- Bcrypt pour les passwords (cost 12)
- mTLS avec certificats clients pour l'authentification agent
- Rate limiting sur /agent/heartbeat (3000 req/min)
- Rate limiting sur auth endpoints (5 req/15min)

### Token Rotation & Theft Detection

| Fonctionnalité | Description |
|----------------|-------------|
| **Family ID** | Chaque session login crée une famille de tokens |
| **Rotation Count** | Compteur incrémenté à chaque refresh |
| **Soft Delete** | Tokens révoqués marqués `is_revoked=true` |
| **Theft Detection** | Réutilisation d'un token révoqué → révocation de toute la famille |
| **Audit Trail** | IP et User-Agent stockés pour chaque token |

**Flux de détection de vol :**
1. Attaquant vole le refresh token de la victime
2. Victime refresh → ancien token marqué `is_revoked`
3. Attaquant tente d'utiliser le token volé (déjà révoqué)
4. Système détecte la réutilisation → révoque TOUTE la famille
5. Victime et attaquant sont tous deux déconnectés

### Token Blacklist

Invalidation immédiate des access tokens (logout, révocation).

| Composant | Description |
|-----------|-------------|
| **Redis Blacklist** | Lookup O(1) avec TTL automatique (15min) |
| **DB Audit** | Table `token_blacklist` pour traçabilité |
| **Middleware Check** | Vérifie blacklist avant validation JWT |
| **Cleanup Job** | Nettoyage des entrées expirées (toutes les heures) |

### HttpOnly Cookies & CSRF

| Cookie | HttpOnly | Secure | SameSite | Path | Usage |
|--------|----------|--------|----------|------|-------|
| `optralis_access` | ✅ | ✅ (prod) | Strict | `/` | Access token JWT |
| `optralis_refresh` | ✅ | ✅ (prod) | Strict | `/api/auth` | Refresh token |
| `optralis_csrf` | ❌ | ✅ (prod) | Strict | `/` | Token CSRF (JS lisible) |

**Protection CSRF :**
- Header `X-CSRF-Token` requis sur POST/PUT/DELETE/PATCH
- Validation constant-time (`subtle.ConstantTimeCompare`)
- Uniquement si authentification par cookie (pas Bearer)

### Containers Non-Root

| Container | User | UID |
|-----------|------|-----|
| `optralis-api` | `appuser` | 1000 |
| `optralis-dashboard` | `node` | 1000 |

### Politique des Mots de Passe

| Règle | Valeur |
|-------|--------|
| **Longueur minimum** | 12 caractères |
| **Complexité** | Majuscule, minuscule, chiffre, caractère spécial |
| **Expiration** | 90 jours |
| **Rappels email** | 30, 10 et 3 jours avant expiration |
| **Premier login** | Changement obligatoire |
| **Reset token** | Valide 1 heure |

### Rappels Expiration Licence

- **Rappels automatiques** : Emails à 30, 14, 7 et 3 jours avant expiration
- **Destinataires** : Tous les utilisateurs admin du client
- **Fréquence** : Vérification quotidienne à 9h UTC

### Hardening Backend

| Mesure | Description |
|--------|-------------|
| **JWT_SECRET obligatoire** | Min 32 caractères, pas de fallback |
| **DATABASE_URL obligatoire** | Pas de fallback avec credentials par défaut |
| **CORS Whitelist** | Variable `CORS_ALLOWED_ORIGINS` |
| **Rate Limiting Auth** | 5 tentatives / 15 minutes par IP |
| **Security Headers** | X-Frame-Options, X-Content-Type-Options, X-XSS-Protection |
| **Body Limit** | Maximum 10 MB par requête |
| **Masquage erreurs** | Erreurs internes loggées, messages génériques retournés |

### Validation des Entrées

| Type | Regex/Règle |
|------|-------------|
| **Email** | RFC 5322 simplifié |
| **Hostname** | RFC 1123 |
| **Couleur Hex** | Format #XXXXXX |
| **Nom de groupe** | 1-50 caractères, trimmed |

### Agent

- mTLS pour communication avec backend (certificat client obligatoire)
- Config file en 0600 permissions

---

## Certificats mTLS Machines

### Architecture 1 Certificat par Machine

Chaque machine possède son propre certificat mTLS unique, permettant une révocation granulaire sans affecter les autres machines du client.

**Format du certificat :**
- **Common Name (CN)** : `client_id:machine_id` (format UUID:UUID)
- **Validité** : 1 an par défaut
- **Émetteur** : CA interne Optralis

```
Avant (legacy) :
Client → 1 Certificat (CN=client_id) → N Machines
Révocation = Toutes les machines bloquées

Après :
Client → N Certificats → N Machines (1:1)
CN = client_id:machine_id
Révocation = 1 machine bloquée
```

### Table `client_certificates`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | UUID | Identifiant unique |
| `client_id` | UUID | Client associé (FK → clients) |
| `machine_id` | UUID | Machine associée (FK → machines) |
| `serial` | VARCHAR(64) | Numéro de série unique du certificat |
| `issued_at` | TIMESTAMPTZ | Date d'émission |
| `expires_at` | TIMESTAMPTZ | Date d'expiration (défaut: 1 an) |
| `revoked_at` | TIMESTAMPTZ | Date de révocation (NULL = valide) |
| `revocation_reason` | TEXT | Raison de révocation (optionnel) |
| `created_by` | UUID | Utilisateur créateur (FK → users, optionnel) |
| `created_at` | TIMESTAMPTZ | Date de création |

**Index :**
- `idx_client_certificates_machine_id` sur `machine_id`
- `idx_client_certificates_active_machine` : index unique sur `machine_id` WHERE `revoked_at IS NULL AND expires_at > NOW()` (garantit 1 cert actif par machine)

### Colonnes certificat dans `machines`

| Colonne | Type | Description |
|---------|------|-------------|
| `cert_serial` | VARCHAR(64) | Numéro de série du certificat (UUID) |
| `cert_issued_at` | TIMESTAMPTZ | Date d'émission du certificat |
| `cert_expires_at` | TIMESTAMPTZ | Date d'expiration (défaut: 1 an) |
| `cert_revoked_at` | TIMESTAMPTZ | Date de révocation (NULL = valide) |

### Calcul du statut certificat

Le statut est calculé dynamiquement (non stocké en DB) :

| Statut | Condition |
|--------|-----------|
| `unknown` | `cert_serial` vide ou NULL (machine pas encore synchronisée) |
| `revoked` | `cert_revoked_at` IS NOT NULL |
| `expired` | `cert_expires_at` < NOW() |
| `expiring` | `cert_expires_at` < NOW() + 30 jours |
| `valid` | Aucune des conditions ci-dessus |

> **Note** : Le statut `legacy` a été supprimé car tous les agents utilisent maintenant l'authentification mTLS avec certificats par machine.

**Fonction Go :** `services/machines/certificate.go:GetCertificateStatus()`

### Synchronisation automatique des certificats

Lors de chaque heartbeat, le backend :
1. Récupère le certificat actif de la machine depuis `client_certificates` (via machine_id)
2. Renseigne automatiquement les champs `cert_serial`, `cert_issued_at`, `cert_expires_at` dans la table `machines`
3. Propage la révocation (`cert_revoked_at`) si le certificat a été révoqué

**Fonction Go :** `services/machines/certificate_lookup.go:GetMachineCertificate()`

### Colonne de synchronisation configuration

| Colonne | Type | Description |
|---------|------|-------------|
| `last_config_sync` | TIMESTAMPTZ | Dernière récupération de config par l'agent |

**Mise à jour :** Automatique lors de `GET /agent/config/collectors`

**Usage :** Affichée sur la page détails machine pour indiquer la dernière synchronisation de configuration avec le serveur.

**Migration :**
```sql
ALTER TABLE machines ADD COLUMN last_config_sync TIMESTAMPTZ;
```

---

## Tables de Configuration Globale

### agent_requirements

Configuration des prérequis OS pour l'installateur agent (table singleton). Supporte la distinction Windows Client / Windows Server / Linux.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | UUID | Clé primaire |
| `windows_client_enabled` | BOOLEAN | Activer Windows Client (Win11/10 LTSC) |
| `windows_client_min_build` | INT | Build minimum Client (ex: 17763 pour W10 LTSC 2019) |
| `windows_server_enabled` | BOOLEAN | Activer Windows Server |
| `windows_server_min_build` | INT | Build minimum Server (ex: 17763 pour Server 2019) |
| `linux_enabled` | BOOLEAN | Activer Linux |
| `unsupported_os_message` | TEXT | Message personnalisé pour OS non supporté |
| `updated_at` | TIMESTAMPTZ | Dernière modification |

**Valeurs par défaut :**
- `windows_client_enabled`: true
- `windows_client_min_build`: 0 (pas de restriction)
- `windows_server_enabled`: true
- `windows_server_min_build`: 0 (pas de restriction)
- `linux_enabled`: true

**Détection Server vs Client :**
L'installer utilise `ProductType` de `RtlGetVersion()` :
- ProductType 1 = Workstation (Client)
- ProductType 2/3 = Server

**Endpoints associés :**
- `GET /agent/requirements` - Public (pour installer)
- `GET /api/admin/agent-requirements` - Admin
- `PUT /api/admin/agent-requirements` - Admin

### windows_builds

Table de référence des versions Windows connues. Utilisée par le dashboard pour peupler les dropdowns de sélection de build minimum. Les données sont seedées automatiquement à la migration.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | UUID | Clé primaire |
| `os_type` | VARCHAR(20) | Type d'OS: 'client' ou 'server' |
| `build_number` | INT | Numéro de build Windows |
| `name` | VARCHAR(100) | Nom affiché (ex: "Windows 10 LTSC 2019", "Windows 11 (24H2)") |
| `release_date` | DATE | Date de sortie |
| `is_active` | BOOLEAN | Si le build est affiché dans les dropdowns |
| `sort_order` | INT | Ordre d'affichage |
| `created_at` | TIMESTAMPTZ | Date de création |

**Contrainte :** UNIQUE(os_type, build_number)

**Builds Windows Client seedés :**
- Windows 10 LTSC: 1809/LTSC 2019 (17763) → LTSC 2021 (19044)
- Windows 10: 1903 (18362) → 22H2 (19045)
- Windows 11: 21H2 (22000) → 24H2 (26100)

> **Note :** Les versions Windows 10 antérieures à LTSC 2019 (build < 17763) ne sont plus supportées.

**Builds Windows Server seedés :**
- Server 2016 (14393), 2019 (17763), 2022 (20348), 2025 (26100)

**Endpoints associés :**
- `GET /api/admin/windows-builds` - Admin (retourne les builds groupés par type)
- `POST /api/admin/windows-builds/refresh` - Admin (rafraîchit depuis URL externe)

**Rafraîchissement depuis endoflife.date API :**

L'endpoint POST permet de mettre à jour les builds depuis l'API publique [endoflife.date](https://endoflife.date/windows) :
- URL : `https://endoflife.date/api/windows.json`
- Classification automatique Client/Server basée sur le champ `cycle`
- Extraction du build number depuis le champ `latest` (ex: "10.0.26100" → 26100)
- Filtrage : exclut les éditions IoT/Embedded et les versions < Windows 10 LTSC 2019 (build 17763)
- Formatage des noms : "Windows 10 LTSC 2019", "Windows 11 (24H2)", "Windows Server 2025"
- Upsert automatique : insert ou update selon existence du build

---

## Install Tokens (Installation Linux via Curl)

Table de gestion des tokens temporaires pour l'installation d'agents Linux via curl.

### Table `install_tokens`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | UUID | Identifiant unique |
| `client_id` | UUID | Client associé (FK → clients) |
| `token_hash` | VARCHAR(255) | Hash SHA256 du token (jamais le token brut) |
| `name` | VARCHAR(100) | Nom optionnel pour identification |
| `expires_at` | TIMESTAMPTZ | Date d'expiration (défaut: 15 min) |
| `usage_count` | INT | Nombre d'utilisations |
| `max_usage` | INT | Limite d'utilisations (0 = illimité) |
| `revoked_at` | TIMESTAMPTZ | Date de révocation (NULL = actif) |
| `created_by` | UUID | Utilisateur créateur (FK → users) |
| `created_at` | TIMESTAMPTZ | Date de création |
| `updated_at` | TIMESTAMPTZ | Dernière modification |

**Index :** `idx_install_tokens_hash` sur `token_hash` pour validation rapide.

### Sécurité

- **Token** : 256-bit random, encodé Base64 URL-safe (44 caractères)
- **Stockage** : SHA256 du token (jamais en clair)
- **Validation** : Hash du token fourni comparé au hash stocké
- **Expiration** : 15 minutes par défaut, max 60 minutes
- **Révocation** : Possible via dashboard ou API

### Workflow

```
Dashboard                   Backend                     Agent Linux
    │                          │                            │
    ├── POST /api/install-tokens ─►│                            │
    │   (génère token 256-bit)     │                            │
    │◄── Token + curl command ─────┤                            │
    │                              │                            │
    │                              │◄── POST /api/public/bootstrap
    │                              │    {token, arch}           │
    │                              │                            │
    │                              │    (valide hash, +usage)   │
    │                              │                            │
    │                              │─── Certificats mTLS ───────►│
    │                              │                            │
```

### Cleanup automatique

`CleanupExpiredTokens()` supprime les tokens expirés depuis > 24h :

```sql
DELETE FROM install_tokens WHERE expires_at < NOW() - INTERVAL '24 hours'
```

**Fichiers concernés :**
- `backend/internal/services/installer/tokens.go` : CRUD tokens
- `backend/internal/handlers/install_tokens.go` : API handlers
- `backend/internal/handlers/bootstrap.go` : Échange token → certificats

---

## Service Uptime Tracking

Système de suivi de la disponibilité des services pour la page de statut public.

### Table `service_uptime`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | UUID | Identifiant unique |
| `service_name` | VARCHAR(50) | Nom du service (api, database, ai) |
| `status` | VARCHAR(20) | Statut (online, degraded, offline) |
| `response_time_ms` | INT | Temps de réponse en ms |
| `checked_at` | TIMESTAMPTZ | Horodatage du check |

**Hypertable TimescaleDB** avec rétention automatique de 30 jours.

### Routine de Health Check

La routine `StartUptimeTrackingRoutine()` vérifie les services toutes les 30 minutes :

| Service | Méthode de vérification | Dégradé si |
|---------|------------------------|------------|
| API | Toujours online (si code s'exécute) | - |
| Database | `database.DB.Ping()` | > 1000ms |
| AI | HTTP GET `/health` | status != "healthy" |

### Calcul de l'Uptime 15 jours

`GetUptime15Days()` retourne 30 valeurs (2 par jour × 15 jours) :

- Chaque période de 12h est moyennée sur tous les services
- "online" ou "degraded" = service disponible (compte comme 100%)
- "offline" = indisponible (compte comme 0%)
- Sans données = 100% (nouveau déploiement)

**Endpoint associé :** `GET /status` (public)

---

## Docker Compose

### Services déployés

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| postgres | timescale/timescaledb:latest-pg16 | 5432 | Base de données + TimescaleDB |
| redis | redis:7-alpine | 6379 | Cache LRU 128MB avec AOF |
| api | build local | 3000 | Backend Go + Fiber |
| dashboard | build local | 3001 | Frontend Next.js |
| caddy | caddy:2-alpine | 80/443 | Reverse proxy + SSL auto |

### Variables d'Environnement

#### Backend

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string (obligatoire) | - |
| `JWT_SECRET` | Secret pour JWT (obligatoire, min 32 car.) | - |
| `CORS_ALLOWED_ORIGINS` | Origines autorisées | `*` (dev) |
| `PORT` | Port serveur | `3000` |
| `DEFAULT_ADMIN_PASSWORD` | Password admin initial | `admin123` |
| `SMTP_HOST` | Serveur SMTP | - |
| `SMTP_PORT` | Port SMTP | `587` |
| `SMTP_USER` | Username SMTP | - |
| `SMTP_PASS` | Password SMTP | - |
| `SMTP_FROM` | Email expéditeur | - |
| `REDIS_URL` | URL Redis (optionnel) | - |

#### Dashboard

| Variable | Description | Défaut |
|----------|-------------|--------|
| `NEXT_PUBLIC_API_URL` | URL de l'API | `http://localhost:3000` |

---

## Maintenance

### Backup/Restore PostgreSQL

```bash
# Backup
docker exec optralis-db pg_dump -U monitoring monitoring > backup.sql

# Restore
docker exec -i optralis-db psql -U monitoring monitoring < backup.sql
```

### Logs

```bash
# Backend
docker compose logs -f api

# Dashboard
docker compose logs -f dashboard

# Agent Windows
Get-EventLog -LogName Application -Source "Optralis Agent"

# Agent Linux
journalctl -u optralis-agent -f
```

---

## Liens

- [Index des spécifications](README.md)
- [Backend API](BACKEND_SPECS.md)
- [Installer & Scripts](INSTALLER_SPECS.md)
