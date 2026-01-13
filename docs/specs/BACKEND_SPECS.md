# Backend API - Spécifications Techniques

## Vue d'ensemble

API REST Go avec Fiber framework, authentification JWT, et architecture multi-tenant.

---

## Routes API

### Public (No Auth)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Health check basique |
| `GET` | `/status` | Status public des services (cache 60s) |
| `GET` | `/status/incidents` | 10 derniers incidents |
| `GET` | `/status/external` | Monitors externes (UptimeRobot) |

### Authentification

| Méthode | Endpoint | Description | Rate Limit |
|---------|----------|-------------|------------|
| `POST` | `/auth/login` | Connexion | 5 req/15min |
| `POST` | `/auth/refresh` | Refresh token | 5 req/15min |
| `POST` | `/auth/logout` | Déconnexion | - |
| `POST` | `/auth/request-password-reset` | Demande reset | 5 req/15min |
| `POST` | `/auth/reset-password` | Reset password | 5 req/15min |
| `GET` | `/auth/validate-reset-token` | Valider token reset | - |
| `POST` | `/auth/mfa/verify` | Vérifier code MFA | 5 req/15min |

#### GET /auth/validate-reset-token

Valide un token de réinitialisation de mot de passe.

**Query Parameters :**
| Param | Type | Requis | Description |
|-------|------|--------|-------------|
| `token` | string | Oui | Token de reset reçu par email |

**Réponse (200) :**
```json
{
  "valid": true
}
```

**Réponse (token invalide/expiré) :**
```json
{
  "valid": false
}
```

**Exemple curl :**
```bash
curl -s "https://api.optralis.com/auth/validate-reset-token?token=abc123"
```

---

#### POST /auth/mfa/verify

Vérifie le code MFA après login initial pour obtenir les tokens d'accès.

**Request Body :**
```json
{
  "mfa_session_id": "session-uuid-from-login",
  "code": "123456"
}
```

**Réponse (200) :**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin",
    "client_id": "uuid",
    "client_name": "Acme Corp"
  }
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Request invalide (champs manquants) |
| 401 | Session MFA invalide/expirée ou code incorrect |
| 429 | Rate limit dépassé |
| 500 | Erreur serveur |

**Exemple curl :**
```bash
curl -s -X POST https://api.optralis.com/auth/mfa/verify \
  -H "Content-Type: application/json" \
  -d '{"mfa_session_id":"abc123","code":"123456"}'
```

### API Publique (No Auth)

Endpoints publics accessibles sans authentification.

| Méthode | Endpoint | Description | Rate Limit |
|---------|----------|-------------|------------|
| `POST` | `/api/public/contact` | Soumettre formulaire contact | 3 req/5min/IP |
| `GET` | `/api/public/landing-stats` | Statistiques landing page | Cache 60s |
| `GET` | `/api/public/latest-version` | Dernière version agent | - |
| `GET` | `/api/public/crl` | Certificate Revocation List (DER) | Cache 5min |

#### POST /api/public/contact

Soumet un formulaire de contact. Envoie un email à l'équipe support.

**Protection anti-spam :**
- **Cloudflare Turnstile** : Token de vérification requis (sauf si `TURNSTILE_SECRET_KEY` non configuré)
- **Honeypot** : Le champ `website` doit rester vide (les bots le remplissent automatiquement)
- **Rate limiting** : 5 requêtes/minute par IP

**Request Body :**
```json
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "company": "Acme Corp",
  "subject": "demo",
  "message": "Je souhaite une démonstration...",
  "language": "fr",
  "turnstile_token": "0.xxxx...",
  "website": ""
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `name` | string | Oui | Nom complet |
| `email` | string | Oui | Email valide |
| `company` | string | Non | Nom entreprise |
| `subject` | string | Non | Sujet : `demo`, `technical`, `enterprise` ou vide |
| `message` | string | Oui | Message (max 5000 car.) |
| `language` | string | Non | Langue (fr/en, défaut: fr) |
| `turnstile_token` | string | Oui* | Token Cloudflare Turnstile (*optionnel en dev) |
| `website` | string | Non | Honeypot - doit rester vide |

**Réponse (200) :**
```json
{
  "success": true,
  "message": "message sent successfully"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Champs requis manquants, email invalide, ou vérification Turnstile échouée |
| 429 | Rate limit dépassé (5 req/min par IP) |
| 500 | Erreur d'envoi email |

**Variables d'environnement :**
| Variable | Description |
|----------|-------------|
| `TURNSTILE_SECRET_KEY` | Clé secrète Cloudflare Turnstile (backend) |

**Exemple curl :**
```bash
curl -s -X POST https://api.optralis.com/api/public/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Jean","email":"jean@example.com","subject":"demo","message":"Hello","turnstile_token":"xxx"}'
```

---

#### GET /api/public/landing-stats

Retourne les statistiques publiques pour la landing page (cachées 60s).

**Réponse (200) :**
```json
{
  "total_machines": 1250,
  "active_clients": 45,
  "total_monitoring_hours": 2500000
}
```

| Champ | Description |
|-------|-------------|
| `total_machines` | Nombre total de machines supervisées |
| `active_clients` | Nombre de clients actifs |
| `total_monitoring_hours` | Heures cumulées de monitoring |

**Headers de cache :**
```
Cache-Control: public, max-age=60
```

**Exemple curl :**
```bash
curl -s https://api.optralis.com/api/public/landing-stats
```

---

#### GET /api/public/latest-version

Retourne la dernière version disponible de l'agent pour une plateforme donnée.
Utilisé par le dashboard pour afficher les versions sur la page d'installation.

**Query Parameters :**

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `channel` | string | `stable` | Canal de distribution (`stable`, `beta`) |
| `platform` | string | `windows` | Plateforme (`windows`, `linux`) |
| `architecture` | string | `amd64` | Architecture (`amd64`, `arm64`) |

**Réponse (200) :**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "1.0.0",
  "channel": "stable",
  "platform": "windows",
  "architecture": "amd64",
  "download_url": "https://optralis.2lacs-it.com/downloads/stable/optralis-agent-v1.0.0.exe",
  "checksum_sha256": "a8ea22f3...",
  "file_size_bytes": 34895872,
  "changelog": "- Fix: ...\n- Feature: ...",
  "is_active": true,
  "created_at": "2026-12-18T10:30:00Z"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 404 | Aucune version trouvée pour les critères |

**Exemple curl :**
```bash
curl -s "https://api.optralis.com/api/public/latest-version?channel=stable&platform=windows&architecture=amd64"
```

---

#### GET /api/public/crl

Retourne la Certificate Revocation List (CRL) au format DER. Utilisé par les clients externes pour vérifier si un certificat agent a été révoqué.

**Réponse (200)** : Fichier binaire DER

**Headers de réponse :**
```
Content-Type: application/pkix-crl
Content-Disposition: attachment; filename="optralis-agent.crl"
Cache-Control: public, max-age=300
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 500 | Erreur génération CRL |
| 503 | CA non configurée |

**Vérification avec OpenSSL :**
```bash
# Télécharger et afficher la CRL
curl -s https://optralis-agent-api.2lacs-it.com/api/public/crl -o optralis.crl
openssl crl -in optralis.crl -inform DER -text -noout
```

**Caractéristiques :**
- **Validité** : 24 heures
- **Cache** : 5 minutes (invalidé automatiquement lors des révocations)
- **Format** : DER (binaire X.509 CRL)

---

### API (Auth Required)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/me` | Info utilisateur |
| `POST` | `/api/change-password` | Changer password |
| `GET` | `/api/status` | Status authentifié |
| `GET` | `/api/overview` | Vue d'ensemble flotte |
| `GET` | `/api/machines` | Liste machines |
| `GET` | `/api/machines/:id` | Détails machine |
| `GET` | `/api/machines/by-hostname/:hostname` | Machine par hostname |
| `GET` | `/api/machines/by-hostname/:hostname/inventory` | Inventaire complet |
| `GET` | `/api/machines/by-hostname/:hostname/metrics` | Historique métriques |
| `GET` | `/api/machines/by-hostname/:hostname/network-metrics` | Métriques réseau |
| `GET` | `/api/machines/by-hostname/:hostname/risk-overrides` | Liste des overrides de risque |
| `POST` | `/api/machines/by-hostname/:hostname/risk-overrides` | Créer/modifier un override |
| `DELETE` | `/api/machines/by-hostname/:hostname/risk-overrides/:id` | Supprimer un override |
| `POST` | `/api/machines/by-hostname/:hostname/force-collect` | Forcer collecte (admin) |
| `DELETE` | `/api/machines/by-hostname/:hostname` | Supprimer machine (admin) |
| `PUT` | `/api/machines/:id/channel` | Modifier canal update (admin) |
| `PUT` | `/api/machines/:id/maintenance` | Mode maintenance (admin) |
| `GET` | `/api/machines/:id/effective-intervals` | Intervalles effectifs |
| `POST` | `/api/machines/:id/certificate/revoke` | Révoquer certificat mTLS (admin) |
| `POST` | `/api/machines/:id/certificate/renew` | Renouveler certificat mTLS (admin) |
| `GET` | `/api/groups` | Liste groupes |
| `POST` | `/api/groups` | Créer groupe |
| `PUT` | `/api/groups/:id` | Modifier groupe |
| `DELETE` | `/api/groups/:id` | Supprimer groupe |
| `PUT` | `/api/machines/assign-group` | Assigner à un groupe |
| `PUT` | `/api/machines/remove-group` | Retirer d'un groupe |
| `GET` | `/api/settings` | Paramètres client |
| `GET` | `/api/windows-versions` | Mapping versions Windows |
| `POST` | `/api/windows-versions/refresh` | Rafraîchir versions (admin) |
| `GET` | `/api/export/machines` | Export machines CSV |

### MFA (Multi-Factor Authentication)

Gestion de l'authentification à deux facteurs pour les utilisateurs.

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `POST` | `/api/users/mfa/setup` | Initialiser MFA | Auth |
| `POST` | `/api/users/mfa/verify` | Activer MFA | Auth |
| `DELETE` | `/api/users/mfa/disable` | Désactiver MFA | Auth |
| `GET` | `/api/users/mfa/status` | Statut MFA | Auth |

#### POST /api/users/mfa/setup

Génère un nouveau secret TOTP et QR code pour l'utilisateur.

**Headers requis :**
```
Authorization: Bearer <token>
```

**Réponse (200) :**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "otpauth://totp/Optralis:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Optralis",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344",
    "44332211"
  ]
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | MFA déjà activé |
| 401 | Non authentifié |
| 500 | Erreur génération secret |

---

#### POST /api/users/mfa/verify

Vérifie le code TOTP et active MFA pour l'utilisateur.

**Request Body :**
```json
{
  "code": "123456"
}
```

**Réponse (200) :**
```json
{
  "message": "MFA enabled successfully"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Code invalide, MFA déjà activé, ou setup non trouvé |
| 401 | Non authentifié |
| 500 | Erreur serveur |

---

#### DELETE /api/users/mfa/disable

Désactive MFA pour l'utilisateur (nécessite le mot de passe).

**Request Body :**
```json
{
  "password": "current-password"
}
```

**Réponse (200) :**
```json
{
  "message": "MFA disabled successfully"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Password requis ou MFA non activé |
| 401 | Password incorrect |
| 500 | Erreur serveur |

---

#### GET /api/users/mfa/status

Retourne le statut MFA actuel de l'utilisateur.

**Réponse (200) :**
```json
{
  "enabled": true,
  "verified_at": "2026-01-15T10:30:00Z",
  "backup_codes_left": 4
}
```

| Champ | Description |
|-------|-------------|
| `enabled` | MFA actif ou non |
| `verified_at` | Date d'activation (null si non activé) |
| `backup_codes_left` | Nombre de codes backup restants |

### Notifications

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/notifications/channels` | Liste des canaux |
| `GET` | `/api/notifications/channels/:id` | Détails d'un canal |
| `POST` | `/api/notifications/channels` | Créer un canal (admin) |
| `PUT` | `/api/notifications/channels/:id` | Modifier un canal (admin) |
| `DELETE` | `/api/notifications/channels/:id` | Supprimer un canal (admin) |
| `POST` | `/api/notifications/channels/:id/test` | Tester un canal (admin) |
| `GET` | `/api/notifications/history` | Historique notifications |
| `GET` | `/api/notifications/types` | Types d'alertes |
| `GET` | `/api/notifications/channel-types` | Types de canaux |

### Labels (Tags Machines)

Système de tags key-value pour organiser et filtrer les machines.

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `GET` | `/api/labels` | Liste des labels | Auth |
| `POST` | `/api/labels` | Créer un label | Admin |
| `PUT` | `/api/labels/:id` | Modifier un label | Admin |
| `DELETE` | `/api/labels/:id` | Supprimer un label | Admin |
| `POST` | `/api/labels/assign` | Assigner label aux machines | Admin |
| `DELETE` | `/api/labels/assign` | Retirer label des machines | Admin |
| `GET` | `/api/labels/:id/machines` | Machines avec ce label | Auth |
| `GET` | `/api/machines/:id/labels` | Labels d'une machine | Auth |
| `POST` | `/api/machines/labels/batch` | Labels de plusieurs machines | Auth |

#### GET /api/labels

Retourne tous les labels du client.

**Réponse (200) :**
```json
[
  {
    "id": "uuid",
    "client_id": "uuid",
    "key": "environment",
    "color": "#3b82f6",
    "created_at": "2026-01-15T10:00:00Z"
  }
]
```

---

#### POST /api/labels

Crée un nouveau label.

**Request Body :**
```json
{
  "key": "environment",
  "color": "#3b82f6"
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `key` | string | Oui | Clé du label (max 50 car.) |
| `color` | string | Non | Couleur hex (défaut: bleu) |

**Réponse (201) :**
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "key": "environment",
  "color": "#3b82f6",
  "created_at": "2026-01-15T10:00:00Z"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Clé manquante ou trop longue |
| 409 | Label avec cette clé existe déjà |

---

#### POST /api/labels/assign

Assigne un label avec une valeur à plusieurs machines.

**Request Body :**
```json
{
  "label_id": "uuid",
  "value": "production",
  "machine_ids": ["uuid1", "uuid2"]
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `label_id` | uuid | Oui | ID du label |
| `value` | string | Non | Valeur (défaut: clé du label, max 100 car.) |
| `machine_ids` | uuid[] | Oui | Liste des machines |

**Réponse (200) :**
```json
{
  "success": true,
  "assigned_count": 2
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Limite max labels par machine atteinte (10) |
| 404 | Label ou machine non trouvé |
| 403 | Accès refusé |

---

#### DELETE /api/labels/assign

Retire un label de plusieurs machines.

**Request Body :**
```json
{
  "label_id": "uuid",
  "machine_ids": ["uuid1", "uuid2"]
}
```

**Réponse (200) :**
```json
{
  "success": true,
  "unassigned_count": 2
}
```

---

#### GET /api/labels/:id/machines

Retourne les machines ayant ce label.

**Query Parameters :**
| Param | Type | Description |
|-------|------|-------------|
| `value` | string | Filtrer par valeur (optionnel) |

**Réponse (200) :**
```json
[
  {
    "machine_id": "uuid",
    "label_id": "uuid",
    "value": "production",
    "assigned_at": "2026-01-15T10:00:00Z"
  }
]
```

---

#### POST /api/machines/labels/batch

Récupère les labels de plusieurs machines en une seule requête (optimisation N+1).

**Request Body :**
```json
{
  "machine_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Limites :** Maximum 100 machines par batch.

**Réponse (200) :**
```json
{
  "uuid1": [
    {"label_id": "uuid", "key": "env", "value": "prod", "color": "#3b82f6"}
  ],
  "uuid2": [],
  "uuid3": [
    {"label_id": "uuid", "key": "env", "value": "dev", "color": "#22c55e"}
  ]
}
```

### Utilisateurs (Multi-Utilisateurs)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/users` | Liste des utilisateurs du client |
| `POST` | `/api/users` | Créer un utilisateur (admin) |
| `PUT` | `/api/users/:id` | Modifier un utilisateur (admin) |
| `DELETE` | `/api/users/:id` | Supprimer un utilisateur (admin) |
| `POST` | `/api/users/:id/reset-password` | Réinitialiser mot de passe (admin) |

### Alert Rules (Règles d'Alerte)

Configuration des règles d'alerte pour le monitoring automatique.

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `GET` | `/api/alert-rules` | Liste des règles | Auth |
| `GET` | `/api/alert-rules/:id` | Détails d'une règle | Auth |
| `GET` | `/api/alert-rules/history` | Historique des déclenchements | Auth |
| `GET` | `/api/alert-rules/metadata` | Métriques, opérateurs, sévérités | Auth |
| `POST` | `/api/alert-rules` | Créer une règle | Admin |
| `PUT` | `/api/alert-rules/:id` | Modifier une règle | Admin |
| `DELETE` | `/api/alert-rules/:id` | Supprimer une règle | Admin |

#### GET /api/alert-rules

Retourne toutes les règles d'alerte du client.

**Réponse (200) :**
```json
{
  "rules": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "name": "CPU critique",
      "metric": "cpu",
      "operator": ">",
      "threshold": 90,
      "severity": "critical",
      "enabled": true,
      "cooldown_minutes": 60,
      "machine_id": null,
      "group_id": null,
      "channel_ids": ["uuid1", "uuid2"],
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

---

#### POST /api/alert-rules

Crée une nouvelle règle d'alerte.

**Request Body :**
```json
{
  "name": "CPU critique",
  "metric": "cpu",
  "operator": ">",
  "threshold": 90,
  "severity": "critical",
  "cooldown_minutes": 60,
  "machine_id": null,
  "group_id": null,
  "channel_ids": ["uuid1"]
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `name` | string | Oui | Nom de la règle |
| `metric` | string | Oui | Métrique (cpu, ram, disk, temperature, offline_minutes) |
| `operator` | string | Oui | Opérateur (>, <, >=, <=, ==) |
| `threshold` | float | Oui | Seuil de déclenchement |
| `severity` | string | Oui | Sévérité (low, warning, critical) |
| `cooldown_minutes` | int | Non | Délai min entre alertes (défaut: 60, min: 5) |
| `machine_id` | uuid | Non | Cibler une machine spécifique |
| `group_id` | uuid | Non | Cibler un groupe |
| `channel_ids` | uuid[] | Non | Canaux de notification |

---

#### GET /api/alert-rules/history

Retourne l'historique des déclenchements d'alertes.

**Query Parameters :**
| Param | Type | Description |
|-------|------|-------------|
| `rule_id` | uuid | Filtrer par règle |
| `machine_id` | uuid | Filtrer par machine |
| `limit` | int | Limite (défaut: 50) |
| `offset` | int | Offset pagination |

**Réponse (200) :**
```json
{
  "history": [
    {
      "id": "uuid",
      "rule_id": "uuid",
      "machine_id": "uuid",
      "machine_hostname": "SRV-01",
      "triggered_value": 95.5,
      "triggered_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/alert-rules/metadata

Retourne les valeurs valides pour créer des règles.

**Réponse (200) :**
```json
{
  "metrics": ["cpu", "ram", "disk", "temperature", "offline_minutes"],
  "operators": [">", "<", ">=", "<=", "=="],
  "severities": ["low", "warning", "critical"]
}
```

### Collection Settings (Intervalles de Collecte)

Configuration des intervalles de collecte personnalisés pour les machines.

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `GET` | `/api/collection-settings` | Liste des paramètres | Auth |
| `GET` | `/api/collection-settings/:id` | Détails d'un paramètre | Auth |
| `POST` | `/api/collection-settings` | Créer un paramètre | Admin |
| `PUT` | `/api/collection-settings/:id` | Modifier un paramètre | Admin |
| `DELETE` | `/api/collection-settings/:id` | Supprimer un paramètre | Admin |
| `GET` | `/api/machines/:id/effective-intervals` | Intervalles effectifs d'une machine | Auth |

#### GET /api/collection-settings

Retourne les paramètres de collecte du client.

**Réponse (200) :**
```json
{
  "settings": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "name": "Production servers",
      "priority": 10,
      "scope": "group",
      "machine_id": null,
      "group_id": "uuid",
      "intervals": {
        "metrics": 5,
        "storage": 120,
        "network": 15,
        "services": 60
      },
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

#### POST /api/collection-settings

Crée un nouveau paramètre de collecte.

**Request Body :**
```json
{
  "name": "Production servers",
  "priority": 10,
  "machine_id": null,
  "group_id": "uuid",
  "intervals": {
    "metrics": 5,
    "storage": 120,
    "network": 15
  }
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `name` | string | Oui | Nom du paramètre |
| `priority` | int | Non | Priorité (défaut: 0, plus haut = prioritaire) |
| `machine_id` | uuid | Non | Machine ciblée (scope: machine) |
| `group_id` | uuid | Non | Groupe ciblé (scope: group) |
| `intervals` | object | Oui | Intervalles en secondes par collector |

**Collectors disponibles :**
| Collector | Min | Max | Défaut |
|-----------|-----|-----|--------|
| `metrics` | 5 | 300 | 10 |
| `storage` | 60 | 3600 | 300 |
| `storage_health` | 1800 | 86400 | 7200 |
| `network` | 10 | 600 | 30 |
| `services` | 30 | 1800 | 120 |
| `security` | 300 | 86400 | 900 |
| `software` | 3600 | 86400 | 14400 |
| `patches` | 3600 | 86400 | 21600 |

---

#### GET /api/machines/:id/effective-intervals

Retourne les intervalles effectifs pour une machine (debug).

**Réponse (200) :**
```json
{
  "machine_id": "uuid",
  "intervals": {
    "metrics": 5,
    "storage": 120,
    "storage_health": 7200,
    "network": 15,
    "services": 60,
    "security": 900,
    "software": 14400,
    "patches": 21600
  },
  "source": "group_setting",
  "setting_id": "uuid",
  "setting_name": "Production servers"
}
```

| Champ | Description |
|-------|-------------|
| `source` | Origine des intervalles (default, client_setting, group_setting, machine_setting) |

### Agent

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/agent/heartbeat` | Vérification mises à jour (retourne `UpdateInfo` si dispo) |
| `POST` | `/agent/collect` | Envoyer données collector (8 types : metrics, storage, etc.) |
| `GET` | `/agent/config` | Récupérer config serveur |
| `GET` | `/agent/config/collectors` | Récupérer config 8 collectors |
| `GET` | `/agent/latest-version` | Dernière version agent |
| `GET` | `/agent/requirements` | Prérequis OS (public, pour installer) |
| `POST` | `/agent/certificate/renew` | Renouveler certificat mTLS (auto-renewal) |

> **Note** : Les endpoints `/agent/inventory` et `/agent/updates` ont été supprimés. Toutes les données transitent via `/agent/collect` avec le paramètre `collector` (metrics, storage, storage_health, network, services, security, software, patches).

#### Machine Lookup

Lors du bootstrap et des heartbeats, le système recherche une machine existante dans cet ordre :
1. Par `hardware_id` (case-insensitive avec `LOWER()`)
2. Par `hostname` (fallback pour compatibilité)

> **Note technique** : La recherche par `hardware_id` utilise `LOWER()` car le stub Windows envoie le GUID en minuscules tandis que l'agent peut l'envoyer avec la casse originale de la registry.

#### GET /agent/config/collectors

Retourne la configuration des 8 collectors pour une machine. Les intervalles sont résolus depuis `collection_settings` avec priorité : machine > label > group > global > default.

**Query Parameters :**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `hostname` | string | Hostname de la machine (optionnel) |

**Réponse (200) :**
```json
{
  "collectors": [
    {"type": "metrics", "enabled": true, "interval": 10},
    {"type": "storage", "enabled": true, "interval": 300},
    {"type": "storage_health", "enabled": true, "interval": 7200},
    {"type": "network", "enabled": true, "interval": 30},
    {"type": "services", "enabled": true, "interval": 120},
    {"type": "security", "enabled": true, "interval": 900},
    {"type": "software", "enabled": true, "interval": 14400},
    {"type": "patches", "enabled": true, "interval": 21600}
  ]
}
```

**Effet secondaire :** Met à jour `last_config_sync` de la machine (asynchrone).

**Usage agent :** Appelé au démarrage et toutes les 5 minutes pour synchroniser la configuration.

---

#### POST /agent/certificate/renew

Permet à un agent de renouveler son certificat mTLS avant expiration. L'agent doit s'authentifier avec son certificat actuel (pas encore expiré). Le renouvellement génère un nouveau certificat unique pour cette machine spécifique.

**Conditions de renouvellement :**
- Le certificat actuel doit expirer dans les 30 prochains jours
- Le certificat actuel ne doit pas être révoqué
- L'agent doit être authentifié via mTLS
- Le nouveau certificat conserve le même format CN=client_id:machine_id

**Réponse (200) :**
```json
{
  "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
  "ca_certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
  "expires_at": "2027-01-02T00:00:00Z"
}
```

| Champ | Description |
|-------|-------------|
| `certificate` | Nouveau certificat client (PEM) |
| `private_key` | Nouvelle clé privée (PEM) |
| `ca_certificate` | Certificat CA pour validation (PEM) |
| `expires_at` | Date d'expiration du nouveau certificat |

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 400 | Certificat n'expire pas dans les 30 jours |
| 401 | Authentification mTLS requise |
| 403 | Certificat révoqué |
| 500 | Erreur génération certificat |

**Comportement backend :**
1. Génère un nouveau certificat avec validité 1 an
2. Stocke les métadonnées dans `client_certificates`
3. Soft-revoke l'ancien certificat avec grace period 24h
4. Invalide le cache Redis

**Usage agent :**
- L'agent vérifie l'expiration toutes les 24 heures
- Si expiration < 30 jours, appelle cet endpoint
- Sauvegarde les nouveaux fichiers de manière atomique
- Recharge le client HTTP avec le nouveau certificat

---

### Gestion Certificats mTLS (Admin)

Ces endpoints permettent de gérer les certificats par machine. Chaque machine possède son propre certificat unique (format CN=client_id:machine_id), permettant une révocation granulaire.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/machines/:id/certificate/revoke` | Révoquer le certificat d'une machine |
| `POST` | `/api/machines/:id/certificate/renew` | Renouveler le certificat d'une machine |

#### POST /api/machines/:id/certificate/revoke

Révoque le certificat mTLS de cette machine spécifique. Seule cette machine sera bloquée, les autres machines du client ne sont pas affectées.

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Certificate revoked successfully"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 403 | Accès admin requis |
| 404 | Machine non trouvée |
| 500 | Erreur serveur |

---

#### POST /api/machines/:id/certificate/renew

Renouvelle le certificat d'une machine. Génère un nouveau certificat avec validité 1 an.

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Certificate renewed successfully",
  "expires_at": "2027-01-01T00:00:00Z"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 403 | Accès admin requis |
| 404 | Machine non trouvée |
| 500 | Erreur serveur |

---

### Installeur Personnalisé (Auth JWT)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/installer/windows` | Télécharger installeur Windows (.exe) |
| `GET` | `/api/installer/linux/amd64` | Télécharger installeur Linux AMD64 (.sh) |
| `GET` | `/api/installer/linux/arm64` | Télécharger installeur Linux ARM64 (.sh) |

**Fonctionnement :**
- Génère un certificat client unique (CN = client_id)
- Embed le certificat dans l'installeur
- Windows: Archive auto-extractible avec agent + cert
- Linux: Script shell avec cert en base64

### Authentification Agent mTLS

L'agent s'authentifie via certificat mTLS avec un certificat unique par machine.

**Format du certificat :**
- **CN** : `client_id:machine_id` (format UUID:UUID)
- **Validité** : 1 an par défaut
- **Émetteur** : CA interne Optralis

**Flow mTLS :**
```
Agent --[cert.crt (CN=client:machine)]--> Caddy --[X-Client-CN: client_id:machine_id]--> Backend
```

**Middleware :** `middleware.AgentMTLSAuth()` parse le CN pour extraire :
- `mtls_client_id` : UUID du client
- `mtls_machine_id` : UUID de la machine

**Vérification révocation :** `middleware.CheckCertificateRevocation()` vérifie par `machine_id` si le certificat est révoqué.

> **Note :** Les anciens certificats au format `CN=client_id` ne sont plus supportés et retournent une erreur `ErrCertificateLegacy`.

### Collectors (8 types)

L'endpoint `/agent/collect` accepte les données de 8 collectors différents :

| Collector | Description | Intervalle défaut |
|-----------|-------------|-------------------|
| `metrics` | CPU, RAM, uptime, température | 10s |
| `storage` | Usage disques, espace libre | 5min |
| `storage_health` | S.M.A.R.T. détaillé | 2h |
| `network` | Bandwidth, latence | 30s |
| `services` | État services Windows/Linux | 2min |
| `security` | AV, firewall, ports | 15min |
| `software` | Apps installées, utilisateurs | 4h |
| `patches` | Windows Update, KB | 6h |

#### Architecture de Stockage des Collectors

Les collectors utilisent deux stratégies de stockage distinctes :

| Collector | Snapshot (`machine_collector_data`) | Time-Series (`metrics` hypertable) | Backward Compat | Notes |
|-----------|-------------------------------------|-----------------------------------|-----------------|-------|
| `metrics` | ❌ | ✅ CPU, RAM, uptime, température | ❌ | |
| `storage` | ✅ | ❌ | ✅ `disk_info` table | Dashboard lit `disk_info` |
| `storage_health` | ✅ | ❌ | ✅ `smart_data` table | Dashboard lit `smart_data` |
| `network` | ✅ | ✅ bandwidth, latence, packet loss | ❌ | |
| `services` | ✅ | ❌ | ✅ `machine_inventory` | |
| `security` | ✅ | ❌ | ✅ `machine_inventory` | AV, firewall, bitlocker, ports |
| `software` | ✅ | ❌ | ✅ `machine_inventory` | |
| `patches` | ✅ | ❌ | ✅ `machine_inventory` | |

**Explication :**
- **Snapshot** (`machine_collector_data`) : Stocke uniquement la dernière valeur (ON CONFLICT DO UPDATE). Utilisé pour l'affichage du statut actuel.
- **Time-Series** (`metrics` hypertable) : Stocke chaque mesure avec timestamp. Utilisé pour les graphiques d'historique (CPU/RAM, réseau).
- **Backward Compat** (`machine_inventory`) : Mise à jour pour compatibilité avec le code legacy.

> **Important** : Les collectors `metrics` et `network` nécessitent l'insertion dans la hypertable `metrics` pour alimenter les graphiques d'historique du dashboard (voir `GetCPUHistory()`, `GetNetworkMetricHistory()`).

**Fichier source :** `backend/internal/services/machines/collectors_storage.go`

#### Modèles de Données des Collectors

Les structures de données sont alignées entre l'agent Go, le backend Go et le frontend TypeScript.

**SmartDiskInfo (storage_health):**

| Champ | Type | Description |
|-------|------|-------------|
| `device` | string | Identifiant du disque (C:, /dev/sda) |
| `model` | string? | Modèle du disque (Samsung SSD 980 PRO) |
| `serial` | string? | Numéro de série |
| `firmware` | string? | Version firmware |
| `smart_status` | string | État: healthy, warning, critical, virtual, unavailable |
| `is_virtual` | bool | true si disque VM (QEMU, VMware, Hyper-V, etc.) |
| `overall_health_test` | string? | Résultat du test santé SMART |
| `temperature` | int? | Température en °C |
| `power_on_hours` | int? | Heures de fonctionnement |
| `power_cycle_count` | int? | Cycles d'alimentation |
| `reallocated_sectors` | int? | Secteurs réalloués (CRITIQUE) |
| `current_pending_sectors` | int? | Secteurs en attente (CRITIQUE) |
| `offline_uncorrectable` | int? | Secteurs non corrigeables (CRITIQUE) |
| `predicted_failure` | bool | Prédiction de panne SMART |

**Note VM :** Pour les disques virtuels, seuls `device`, `model`, `smart_status: "virtual"` et `is_virtual: true` sont renseignés.

**PendingUpdateInfo (patches):**

| Champ | Type | Description |
|-------|------|-------------|
| `title` | string | Titre de la mise à jour |
| `kb` | string? | Numéro KB (ex: "KB5028997") |
| `category` | string | Security, Critical, Definition, Other |
| `size` | string? | Taille lisible (ex: "45.2 MB") |
| `is_important` | bool | Mise à jour importante/sécurité |

**UserInfoData (software):**

| Champ | Type | Description |
|-------|------|-------------|
| `username` | string | Nom d'utilisateur |
| `full_name` | string? | Nom complet |
| `is_admin` | bool | Membre du groupe Administrateurs |
| `enabled` | bool | Compte activé (pas désactivé) |
| `last_logon` | string? | Dernière connexion |
| `groups` | string[]? | Groupes (backend only) |

**Fichier source :** `backend/internal/models/collectors.go`

### AI Automation (Pro+ seulement)

Vue d'ensemble de toute l'automatisation IA : routines et triggers.

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `GET` | `/api/ai/automation` | Config complète routines + triggers | Auth (Pro+) |

#### GET /api/ai/automation

Retourne la configuration complète d'automatisation IA avec routines, triggers et statistiques.

**Réponse (200) :**
```json
{
  "routines": [
    {
      "routine": {
        "id": "uuid",
        "routine_type": "daily_health_check",
        "enabled": true,
        "schedule": "0 8 * * *",
        "last_run_at": "2026-01-15T08:00:00Z"
      },
      "last_history": { ... }
    }
  ],
  "triggers": [
    {
      "trigger": {
        "id": "uuid",
        "trigger_type": "critical_machine",
        "enabled": true,
        "conditions": { ... },
        "last_triggered_at": "2026-01-15T10:00:00Z"
      },
      "last_history": { ... }
    }
  ],
  "routine_stats": {
    "total": 3,
    "enabled": 2,
    "last_24h_runs": 5
  },
  "trigger_stats": {
    "total": 2,
    "enabled": 2,
    "last_24h_triggers": 3
  }
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 403 | Licence Pro ou Enterprise requise |

---

### AI Routines (Pro+ seulement)

Routines d'analyse IA planifiées (cron-like).

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `GET` | `/api/ai/routines` | Liste des routines | Auth (Pro+) |
| `GET` | `/api/ai/routines/stats` | Statistiques routines | Auth (Pro+) |
| `GET` | `/api/ai/routines/:id` | Détails d'une routine | Auth (Pro+) |
| `GET` | `/api/ai/routines/:id/history` | Historique exécutions | Auth (Pro+) |
| `POST` | `/api/ai/routines` | Créer une routine | Admin (Pro+) |
| `PUT` | `/api/ai/routines/:id` | Modifier une routine | Admin (Pro+) |
| `DELETE` | `/api/ai/routines/:id` | Supprimer une routine | Admin (Pro+) |

#### POST /api/ai/routines

Crée une nouvelle routine d'analyse planifiée.

**Request Body :**
```json
{
  "routine_type": "daily_health_check",
  "schedule": "0 8 * * *",
  "enabled": true,
  "config": {
    "analysis_type": "full",
    "machines": "all",
    "notify_channels": ["uuid1"]
  }
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `routine_type` | string | Oui | Type (daily_health_check, weekly_report, trend_analysis) |
| `schedule` | string | Oui | Expression cron (ex: "0 8 * * *" = 8h chaque jour) |
| `enabled` | bool | Non | Activé (défaut: true) |
| `config` | object | Non | Configuration spécifique au type |

**Types de routines :**
| Type | Description |
|------|-------------|
| `daily_health_score` | Analyse santé quotidienne des machines |
| `weekly_report` | Rapport hebdomadaire par email |
| `daily_report` | Synthèse quotidienne avec vue d'ensemble du parc |
| `drift_detection` | Détection de dérives et analyse baseline (z-score) |

**Drift Detection - Fonctionnement :**
1. Calcul baseline sur 7 jours (moyenne, écart-type)
2. Calcul z-score = (valeur_actuelle - moyenne) / écart-type
3. Si z-score > 2 → warning, > 3 → critical
4. Appel Claude API pour expliquer le drift détecté
5. Stockage dans `metric_baselines` avec explication

**Métriques surveillées :** cpu_percent, ram_percent, disk_latency_ms

---

#### GET /api/ai/routines/:id/history

Retourne l'historique d'exécution d'une routine.

**Query Parameters :**
| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Limite (défaut: 20) |

**Réponse (200) :**
```json
{
  "history": [
    {
      "id": "uuid",
      "routine_id": "uuid",
      "started_at": "2026-01-15T08:00:00Z",
      "completed_at": "2026-01-15T08:02:30Z",
      "status": "success",
      "machines_analyzed": 25,
      "issues_found": 3
    }
  ]
}
```

---

### AI Triggers (Pro+ seulement)

Triggers d'analyse IA basés sur des conditions (événements).

| Méthode | Endpoint | Description | Permission |
|---------|----------|-------------|------------|
| `GET` | `/api/ai/triggers` | Liste des triggers | Auth (Pro+) |
| `GET` | `/api/ai/triggers/stats` | Statistiques triggers | Auth (Pro+) |
| `GET` | `/api/ai/triggers/:id` | Détails d'un trigger | Auth (Pro+) |
| `GET` | `/api/ai/triggers/:id/history` | Historique déclenchements | Auth (Pro+) |
| `POST` | `/api/ai/triggers` | Créer un trigger | Admin (Pro+) |
| `PUT` | `/api/ai/triggers/:id` | Modifier un trigger | Admin (Pro+) |
| `DELETE` | `/api/ai/triggers/:id` | Supprimer un trigger | Admin (Pro+) |

#### POST /api/ai/triggers

Crée un nouveau trigger d'analyse automatique.

**Request Body :**
```json
{
  "trigger_type": "critical_machine",
  "enabled": true,
  "conditions": {
    "health_score_below": 50,
    "offline_minutes": 15,
    "cpu_above": 95
  },
  "actions": {
    "analysis_type": "full",
    "notify_channels": ["uuid1"]
  }
}
```

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `trigger_type` | string | Oui | Type (critical_machine, new_machine, degradation) |
| `enabled` | bool | Non | Activé (défaut: true) |
| `conditions` | object | Oui | Conditions de déclenchement |
| `actions` | object | Oui | Actions à exécuter |

**Types de triggers :**
| Type | Description |
|------|-------------|
| `critical_machine` | Machine avec health score critique |
| `new_machine` | Nouvelle machine détectée |
| `degradation` | Dégradation progressive détectée |

---

#### GET /api/ai/triggers/:id/history

Retourne l'historique de déclenchement d'un trigger.

**Query Parameters :**
| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Limite (défaut: 20) |

**Réponse (200) :**
```json
{
  "history": [
    {
      "id": "uuid",
      "trigger_id": "uuid",
      "triggered_at": "2026-01-15T10:00:00Z",
      "machine_id": "uuid",
      "machine_hostname": "SRV-PROD-01",
      "trigger_reason": "Health score below 50",
      "analysis_result": { ... }
    }
  ]
}
```

### Admin (Super Admin)

Tous les endpoints `/api/admin/*` requièrent le rôle `super_admin`.

#### Dashboard & Statistiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/dashboard` | Statistiques globales |
| `GET` | `/api/admin/stats/timeline` | Timeline clients/machines |

#### Gestion des Clients

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/clients` | Liste clients |
| `GET` | `/api/admin/clients/:id` | Détails client |
| `POST` | `/api/admin/clients` | Créer client |
| `PUT` | `/api/admin/clients/:id` | Modifier client |
| `DELETE` | `/api/admin/clients/:id` | Supprimer client |
| `POST` | `/api/admin/clients/:id/regenerate-license-id` | Régénérer license ID |
| `POST` | `/api/admin/impersonate/:clientId` | Impersonation token |

#### Gestion des Licences

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/licenses` | Liste licences |
| `PUT` | `/api/admin/clients/:clientId/extend` | Prolonger licence |
| `GET` | `/api/admin/license-types` | Types de licences |
| `POST` | `/api/admin/license-types` | Créer type licence |
| `PUT` | `/api/admin/license-types/:id` | Modifier type licence |
| `DELETE` | `/api/admin/license-types/:id` | Supprimer type licence |

#### Gestion Docker

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/docker/containers` | Liste containers |
| `GET` | `/api/admin/docker/containers/:id` | Détails container |
| `GET` | `/api/admin/docker/containers/:id/logs` | Logs container |
| `GET` | `/api/admin/docker/containers/:id/stats` | Stats container |
| `POST` | `/api/admin/docker/containers/:id/start` | Démarrer container |
| `POST` | `/api/admin/docker/containers/:id/stop` | Arrêter container |
| `POST` | `/api/admin/docker/containers/:id/restart` | Redémarrer container |

#### Gestion Agent Versions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/agent-versions` | Liste des versions |
| `GET` | `/api/admin/agent-versions/:id` | Détails version |
| `POST` | `/api/admin/agent-versions` | Créer version |
| `PUT` | `/api/admin/agent-versions/:id` | Modifier version |
| `DELETE` | `/api/admin/agent-versions/:id` | Supprimer version + fichiers |
| `POST` | `/api/admin/agent-versions/:id/promote` | Promouvoir en stable |
| `PUT` | `/api/admin/machines/bulk-channel` | Maj canal machines en lot |
| `GET` | `/api/admin/machines/all` | Toutes machines (tous clients) |
| `GET` | `/api/admin/agent-downloads` | Téléchargements disponibles |

**DELETE /api/admin/agent-versions/:id** - Suppression complète :
- Supprime l'entrée en base de données
- Supprime le fichier EXE sur le serveur
- Met à jour/supprime les fichiers metadata selon la plateforme :
  - Windows : `metadata-windows.json` et `metadata.json`
  - Linux : `metadata-linux.json`
- Si la version supprimée était active, active automatiquement la version suivante (même channel/platform/architecture)

#### Prérequis OS & Activity

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/agent-requirements` | Prérequis OS agent |
| `PUT` | `/api/admin/agent-requirements` | Modifier prérequis OS |
| `GET` | `/api/admin/windows-builds` | Builds Windows (Client/Server) |
| `POST` | `/api/admin/windows-builds/refresh` | Rafraîchir depuis endoflife.date |
| `GET` | `/api/admin/activity` | Journal d'activité |
| `GET` | `/api/admin/activity/stats` | Statistiques d'activité |

#### Gestion des Certificats (Admin)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/admin/certificates` | Liste tous les certificats (tous clients) |
| `GET` | `/api/admin/certificates/stats` | Statistiques des certificats |
| `DELETE` | `/api/admin/certificates/purge` | Supprimer les certificats inactifs (expired/revoked) |
| `POST` | `/api/admin/certificates/:serial/restore` | Restaurer un certificat révoqué |
| `POST` | `/api/admin/certificates/refresh-cache` | Rafraîchir le cache Redis des certificats |

##### DELETE /api/admin/certificates/purge

Supprime uniquement les certificats **inactifs** (expired ou revoked) de la base de données. Les certificats actifs sont préservés.

**Certificats supprimés :**
- `expired` : Certificats dont `expires_at <= NOW()` et non révoqués
- `revoked` : Certificats avec `revoked_at IS NOT NULL`

**Certificats préservés :**
- `valid` : Expiration > 30 jours
- `expiring_soon` : Expiration entre 7 et 30 jours
- `expiring` : Expiration < 7 jours

**Réponse (200) :**
```json
{
  "message": "inactive certificates purged successfully",
  "deleted": 42
}
```

**Réponse (aucun certificat inactif) :**
```json
{
  "message": "no inactive certificates to purge",
  "deleted": 0
}
```

---

##### POST /api/admin/certificates/:serial/restore

Restaure un certificat précédemment révoqué (annule la révocation).

**Réponse (200) :**
```json
{
  "success": true,
  "message": "Certificate restored successfully"
}
```

**Codes d'erreur :**
| Code | Description |
|------|-------------|
| 404 | Certificat non trouvé ou non révoqué |
| 500 | Erreur serveur |

---

##### POST /api/admin/certificates/refresh-cache

Vide le cache Redis des statuts de révocation des certificats. Utilisé pour corriger les désynchronisations entre Redis et PostgreSQL.

**Cas d'usage :**
- Un agent affiche "certificate revoked" alors que le certificat est valide dans le dashboard
- Après une migration ou restauration de base de données
- Debug de problèmes de cache

**Réponse (200) :**
```json
{
  "message": "certificate cache refreshed successfully"
}
```

**Note technique :** Cette opération supprime toutes les clés Redis avec le pattern `cert:revoked:*`. Les prochaines requêtes des agents reconstruiront le cache depuis PostgreSQL.

---

##### GET /api/admin/certificates

Liste tous les certificats mTLS avec filtrage et pagination.

**Query Parameters :**
| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filtrer par statut (valid, expiring_soon, expiring, expired, revoked) |
| `client_id` | uuid | Filtrer par client |
| `search` | string | Rechercher par hostname ou serial |
| `limit` | int | Limite (défaut: 50, max: 200) |
| `offset` | int | Offset pagination |

**Réponse (200) :**
```json
{
  "certificates": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "client_name": "Acme Corp",
      "machine_id": "uuid",
      "machine_hostname": "SRV-PROD-01",
      "serial": "ABC123...",
      "issued_at": "2026-01-01T00:00:00Z",
      "expires_at": "2026-01-01T00:00:00Z",
      "revoked_at": null,
      "revocation_reason": "",
      "status": "valid"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**Statuts possibles :**
| Statut | Description |
|--------|-------------|
| `valid` | Certificat valide (> 30 jours avant expiration) |
| `expiring_soon` | Expire dans 7-30 jours |
| `expiring` | Expire dans < 7 jours |
| `expired` | Certificat expiré |
| `revoked` | Certificat révoqué |

---

##### GET /api/admin/certificates/stats

Retourne les statistiques globales des certificats.

**Réponse (200) :**
```json
{
  "total": 150,
  "valid": 120,
  "expiring_soon": 15,
  "expiring": 5,
  "expired": 3,
  "revoked": 7
}
```

### Validation Conformité OS

Le backend valide automatiquement la conformité OS de chaque machine à chaque heartbeat (INSERT et UPDATE).

**Logique de validation :**
1. Parse le build number depuis `os_version` (patterns: "Build XXXXX", "10.0.XXXXX")
2. Détecte le type Windows (Server si contient "Server", sinon Client)
3. Compare avec `WindowsClientMinBuild` ou `WindowsServerMinBuild` des `agent_requirements`
4. Stocke le résultat dans `is_os_compliant`

**Cas particuliers :**
- Linux : Toujours compliant si `linux_enabled = true`
- Erreur de parsing : Considéré compliant (fail-safe)
- Build = 0 (non parseable) : Considéré compliant

**Cache :**
- Les `agent_requirements` sont mis en cache (TTL 5 minutes)
- Évite une requête DB à chaque heartbeat

### Configuration IA (Enterprise only)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/ai-config` | Récupérer la config IA du client |
| `PUT` | `/api/ai-config` | Mettre à jour la config (admin) |
| `POST` | `/api/ai-config/analyze` | Lancer l'auto-détection (admin) |

**Fonctionnalités :**
- Auto-détection de la criticité des machines basée sur les hostnames (patterns PROD, SQL, WMS, ERP, etc.)
- Classification manuelle ajustable (critique, important, standard)
- Contexte personnalisé injecté dans les prompts IA
- Configuration par client (chaque client Enterprise a sa propre config)

**Patterns auto-détectés :**
| Pattern | Criticité | Raison |
|---------|-----------|--------|
| `*PROD*`, `*PRD*` | Critique | Production |
| `*SQL*`, `*DB*`, `*BDD*` | Critique | Base de données |
| `*WMS*`, `*ERP*`, `*SAP*` | Critique | Métier critique |
| `*COMPTA*`, `*PAIE*` | Critique | Finance |
| `*WEB*`, `*WWW*`, `*API*` | Important | Services exposés |
| `*MAIL*`, `*SMTP*` | Important | Communication |
| `*DEV*`, `*TEST*`, `*UAT*` | Standard | Non-prod |
| `*BACKUP*`, `*BKP*` | Standard | Secondaire |

### AI Service (via service interne :3002)

#### Endpoints standards (toutes licences)

| Méthode | Endpoint | Description | Coût quota |
|---------|----------|-------------|------------|
| `GET` | `/health` | Health check (DB, Redis, Claude) | 0 |
| `GET` | `/ai/quota` | Vérifier quota restant | 0 |
| `POST` | `/ai/analyze/logs` | Analyse des logs critiques | 1 |
| `POST` | `/ai/analyze/anomalies` | Détection d'anomalies métriques | 1 |
| `POST` | `/ai/analyze/full` | Analyse complète (logs + anomalies + reco) | 3 |
| `POST` | `/ai/recommendations` | Recommandations priorisées | 1 |
| `POST` | `/ai/health-score` | Score de santé IA (0-100) avec catégories | 1 |
| `POST` | `/ai/analyze/trends` | Analyse des tendances p95/p99 (7/30 jours) | 1 |
| `POST` | `/ai/scripts/generate` | Génération de scripts remédiation | 1 |
| `POST` | `/ai/reports/generate` | Génération rapport hebdo/mensuel | 2 |
| `GET` | `/ai/reports/:id` | Récupérer un rapport | 0 |
| `GET` | `/ai/reports` | Lister les rapports | 0 |

**Détail des endpoints standards :**

| Endpoint | Fonctionnalité détaillée |
|----------|--------------------------|
| `/ai/analyze/logs` | Analyse les logs système (error, critical) et identifie les patterns problématiques, les erreurs récurrentes et les causes potentielles |
| `/ai/analyze/anomalies` | Détecte les anomalies dans les métriques (CPU, RAM, disque) via analyse statistique par rapport aux baselines historiques |
| `/ai/analyze/full` | Combine logs + anomalies + recommandations en une seule analyse exhaustive de la machine |
| `/ai/recommendations` | Génère des recommandations d'actions priorisées (avec scripts optionnels) basées sur l'état actuel de la machine |
| `/ai/health-score` | Calcule un score global 0-100 avec sous-scores par catégorie (CPU, RAM, disque, sécurité, stabilité) et tendance |
| `/ai/analyze/trends` | Analyse les tendances sur 7 ou 30 jours : percentiles p95/p99, dérives et prédictions de saturation |
| `/ai/scripts/generate` | Génère des scripts PowerShell/Bash pour remédier aux problèmes identifiés, avec avertissements de sécurité |
| `/ai/reports/generate` | Crée un rapport hebdomadaire ou mensuel (format exécutif ou technique) avec synthèse et graphiques |

#### Endpoints Maintenance Prédictive Avancée (Pro/Enterprise uniquement)

| Méthode | Endpoint | Description | Coût quota |
|---------|----------|-------------|------------|
| `POST` | `/ai/analyze/degradation` | Priorisation intelligente - dégradation progressive | 1 |
| `POST` | `/ai/analyze/intermittent` | Détection d'intermittence (latence disque, IO wait) | 1 |
| `POST` | `/ai/correlate` | Priorisation intelligente - corrélation événements/métriques | 1 |
| `POST` | `/ai/predictive/maintenance` | Analyse prédictive complète groupée | 5 |

**Détail des endpoints avancés :**

| Endpoint | Fonctionnalité détaillée |
|----------|--------------------------|
| `/ai/analyze/degradation` | Identifie les dégradations progressives de performance (CPU/RAM/disque qui augmentent lentement) avec prédiction de date critique |
| `/ai/analyze/intermittent` | Détecte les problèmes sporadiques : pics de latence disque >50ms, IO wait >15%, patterns (aléatoire, périodique, escalade) |
| `/ai/correlate` | Corrèle les événements système avec les pics de métriques pour identifier les causes racines (ex: mise à jour Windows → pic CPU) |
| `/ai/predictive/maintenance` | Analyse groupée complète : health-score + trends + degradation + correlations + intermittent en un seul appel avec synthèse globale |

**Notes** :
- Le header `X-Client-ID` est requis pour tous les endpoints (sauf `/health`).
- Les endpoints Avancés retournent une erreur `403 PREMIUM_REQUIRED` pour les licences Starter/Trial.

---

## Modèles de Données

```go
type Client struct {
    ID        uuid.UUID
    Name      string
    LicenseID uuid.UUID
    CreatedAt time.Time
}

type User struct {
    ID                 uuid.UUID
    ClientID           uuid.UUID
    Email              string
    FirstName          string
    LastName           string
    Role               string  // super_admin, admin, observer
    MustChangePassword bool
    PasswordChangedAt  time.Time
    CreatedAt          time.Time
    UpdatedAt          time.Time
}

type Machine struct {
    ID            uuid.UUID
    ClientID      uuid.UUID
    GroupID       uuid.UUID
    Hostname      string
    HardwareID    string     // Identifiant matériel persistant
    OS            string
    OSVersion     string
    IP            string
    AgentVersion  string
    LastSeen      time.Time
    HealthScore   int
    IsOSCompliant bool       // true si OS respecte agent_requirements (build number)
    // mTLS certificate fields
    CertSerial    string     // Numéro de série du certificat
    CertIssuedAt  *time.Time // Date d'émission
    CertExpiresAt *time.Time // Date d'expiration
    CertRevokedAt *time.Time // Date de révocation (null si valide)
    CertStatus    string     // Calculé: valid, expiring, expired, revoked, legacy
}

type NotificationChannel struct {
    ID          uuid.UUID
    ClientID    uuid.UUID
    Type        string                 // email, webhook_teams, webhook_slack, webhook_discord
    Name        string
    Enabled     bool
    Config      map[string]interface{} // Configuration JSONB (emails ou webhook_url)
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

type AlertRule struct {
    ID              uuid.UUID
    ClientID        uuid.UUID
    Name            string
    Metric          string      // cpu, ram, disk, temperature, offline_minutes
    Operator        string      // >, <, >=, <=, ==
    Threshold       float64
    Severity        string      // low, warning, critical
    Enabled         bool
    CooldownMinutes int         // Délai minimum entre deux alertes
    MachineID       *uuid.UUID  // Optionnel : cibler une machine spécifique
    GroupID         *uuid.UUID  // Optionnel : cibler un groupe
    ChannelIDs      []uuid.UUID // Canaux de destination pour cette règle
    CreatedAt       time.Time
    UpdatedAt       time.Time
}

type ActivityLog struct {
    ID        uuid.UUID
    Timestamp time.Time
    Level     string                 // info, warn, error
    Category  string                 // auth, email, alert, system, user, machine
    Message   string
    Metadata  map[string]interface{} // Données additionnelles (JSON)
    ClientID  *uuid.UUID
    UserID    *uuid.UUID
    IPAddress string
}

type ServiceIncident struct {
    ID          uuid.UUID
    ServiceName string     // api, database, ai
    Status      string     // degraded, offline
    StartedAt   time.Time
    ResolvedAt  *time.Time
    Description *string
    CreatedAt   time.Time
}
```

---

## Page Status Publique

### Endpoint GET /status

Retourne le status de tous les services avec cache de 60 secondes.

**Optimisations (v2.3.12) :**
- Checks parallélisés avec goroutines (AI + uptime en parallèle)
- Timeout service AI : 2s (au lieu de 5s)
- Cache TTL : 60s (au lieu de 30s)

**Réponse :**
```json
{
  "overall_status": "online",
  "services": {
    "api": {
      "status": "online",
      "response_time_ms": 0,
      "uptime_15d": [100.0, 100.0, ...]
    },
    "database": {
      "status": "online",
      "response_time_ms": 5,
      "uptime_15d": [100.0, 99.8, ...]
    },
    "ai": {
      "status": "online",
      "response_time_ms": 150,
      "uptime_15d": [100.0, 100.0, ...]
    }
  },
  "metrics": {
    "total_machines": 100,
    "online_machines": 95,
    "offline_machines": 5,
    "average_health_score": 87.5
  },
  "timestamp": "2026-01-01T12:00:00Z"
}
```

**Services monitorés :**
- `api` : Toujours online si l'API répond
- `database` : Ping PostgreSQL (degraded si >1s)
- `ai` : Health check service AI (:3002)

**Uptime :**
- 30 valeurs = 15 jours × 2 demi-journées
- Pourcentage calculé par service
- Requête SQL optimisée (1 au lieu de 30)

### Endpoint GET /status/incidents

Retourne les 10 derniers incidents de service.

**Réponse :**
```json
{
  "incidents": [
    {
      "id": "uuid",
      "service_name": "database",
      "status": "degraded",
      "started_at": "2026-01-01T10:00:00Z",
      "resolved_at": "2026-01-01T10:15:00Z",
      "description": "Latence élevée"
    }
  ],
  "total": 1
}
```

### Cache Status

Le cache en mémoire (TTL 30s) stocke :
- Status des 3 services + temps de réponse
- Métriques machines (total, online, health score)
- Uptime 15 jours par service

**Invalidation :** Automatique après expiration TTL.

### Endpoint GET /status/external

Retourne le status des monitors externes (UptimeRobot).

**Configuration requise :**
```env
UPTIMEROBOT_API_KEY=ur1234567-xxxxxxxxxxxxxxxxxxxx
```

**Réponse :**
```json
{
  "monitors": [
    {
      "id": "802079181",
      "name": "Optralis - API",
      "status": "online",
      "uptime_ratio": 99.95,
      "response_time": 150,
      "url": "https://optralis-api.2lacs-it.com/health",
      "uptime_15d": [100.0, 100.0, 99.8, ...]
    },
    {
      "id": "802079169",
      "name": "Optralis - Frontend",
      "status": "online",
      "uptime_ratio": 99.98,
      "response_time": 85,
      "url": "https://optralis.2lacs-it.com/status",
      "uptime_15d": [100.0, 100.0, 100.0, ...]
    }
  ],
  "timestamp": "2026-01-01T12:00:00Z"
}
```

**Champs :**
| Champ | Description |
|-------|-------------|
| `uptime_ratio` | Uptime sur 15 jours (%) |
| `uptime_15d` | 30 valeurs (15 jours × 2 demi-journées de 12h) calculées depuis les logs d'événements UptimeRobot |

**Calcul `uptime_15d` :**
- L'API UptimeRobot est appelée avec `logs=1&logs_limit=1000&custom_uptime_ratios=15`
- Les logs sont triés chronologiquement (UptimeRobot les retourne du plus récent au plus ancien)
- Les logs d'événements (type 1=down, 2=up) sont analysés pour calculer le temps de panne réel
- Pour chaque période de 12 heures (AM: 00:00-11:59, PM: 12:00-23:59), on calcule:
  - Le temps de panne total en secondes (chevauchement des pannes avec le bucket)
  - Le pourcentage de disponibilité: `(43200 - secondesPanne) / 43200 × 100`
- Résultat: 30 valeurs représentant les 15 derniers jours, du plus ancien au plus récent

**Types de logs UptimeRobot :**
- `1` → Monitor down (début de panne)
- `2` → Monitor up (fin de panne)
- `98` → Monitoring started
- `99` → Monitoring paused

**Status UptimeRobot :**
- `2` → online
- `8` → degraded (seems_down)
- `9` → offline (down)

**Intégration Dashboard :**
Les moniteurs "Optralis - API" et "Optralis - Frontend" sont affichés dans le tableau principal des services (page /status), avec le même graphique d'uptime que les services internes.

---

## Système de Notifications Multi-Canal

### Vue d'Ensemble

| Canal | Format | Configuration |
|-------|--------|---------------|
| Email | HTML templated | Liste d'adresses email |
| Microsoft Teams | MessageCard | URL Webhook Incoming |
| Slack | Block Kit | URL Webhook Incoming |
| Discord | Embeds | URL Webhook |

### Types d'Alertes

| Type | Clé | Description |
|------|-----|-------------|
| Machine hors ligne | `machine_offline` | Machine non vue depuis X minutes |
| Machine en ligne | `machine_online` | Machine revenue en ligne (après offline) |
| CPU élevé | `high_cpu` | Usage CPU > seuil configuré |
| RAM élevée | `high_ram` | Usage RAM > seuil configuré |
| Disque critique | `disk_critical` | Espace disque > seuil configuré |
| Alerte SMART | `smart_warning` | Erreur SMART détectée |

### Anti-Spam Machine Offline

Le système évite les notifications répétitives pour les machines constamment offline :

```
Machine online → offline : NOTIFICATION "Machine hors ligne" 🔴
Machine reste offline    : SILENCE (pas de re-notification)
Machine offline → online : NOTIFICATION "Retour en ligne" 🟢
```

**Mécanisme :**
- Colonne `machines.offline_notified_at` : `NULL` = online/jamais notifié, `timestamp` = date notification
- La routine monitoring ne notifie que si `offline_notified_at IS NULL`
- Après notification offline : `offline_notified_at = NOW()`
- Au heartbeat : si `offline_notified_at` était set → notification "retour en ligne" + reset à `NULL`

### Architecture Simplifiée

**Canaux = Destinations simples** (Email, Teams, Slack, Discord)
- Configuration : type + nom + config (emails ou webhook_url)
- Pas de logique métier, juste des endpoints de livraison

**Règles = Toute la logique**
- Métrique + opérateur + seuil
- Scope : toutes machines / machine / groupe
- Cooldown configurable par règle
- Liste des canaux de destination (channel_ids)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Service                            │
│    Évalue les règles (cpu > 85%, offline_minutes > 5, etc.)     │
└─────────────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Alert Rule Triggered                        │
│   - Vérifie le cooldown de la règle                             │
│   - Récupère les channel_ids de la règle                        │
│   - Enregistre dans alert_rule_history                          │
└───────┬─────────────┬─────────────┬─────────────┬───────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
    ┌───────┐     ┌───────┐     ┌───────┐     ┌───────┐
    │ Email │     │ Teams │     │ Slack │     │Discord│
    └───────┘     └───────┘     └───────┘     └───────┘
```

### Cooldown

Chaque **règle** a son propre cooldown configurable (minimum: 5 minutes, défaut: 60 minutes). Le système vérifie la dernière alerte déclenchée pour:
- La même règle
- La même machine

### Formats Webhook

**Microsoft Teams (MessageCard):**
```json
{
  "@type": "MessageCard",
  "themeColor": "FF0000",
  "summary": "Alerte Optralis",
  "sections": [{
    "activityTitle": "Machine hors ligne",
    "facts": [
      {"name": "Machine", "value": "SRV-PROD-01"},
      {"name": "Client", "value": "Acme Corp"}
    ]
  }]
}
```

**Slack (Block Kit):**
```json
{
  "blocks": [
    {"type": "header", "text": {"type": "plain_text", "text": "Machine hors ligne"}},
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Machine:*\nSRV-PROD-01"}
      ]
    }
  ]
}
```

**Discord (Embeds):**
```json
{
  "embeds": [{
    "title": "Machine hors ligne",
    "color": 16711680,
    "fields": [
      {"name": "Machine", "value": "SRV-PROD-01", "inline": true}
    ]
  }]
}
```

---

## Système Multi-Utilisateurs

### Rôles

| Rôle | Description | Accès |
|------|-------------|-------|
| `super_admin` | Administrateur global Optralis | Tout (panel admin inclus) |
| `admin` | Administrateur client | Configuration, notifications, gestion utilisateurs |
| `observer` | Observateur | Lecture seule (dashboard, machines) |

### Matrice des Permissions

| Action | super_admin | admin | observer |
|--------|-------------|-------|----------|
| Voir machines/métriques | ✅ | ✅ | ✅ |
| Voir notifications | ✅ | ✅ | ✅ |
| Créer/modifier notifications | ✅ | ✅ | ❌ |
| Gérer groupes | ✅ | ✅ | ❌ |
| Gérer utilisateurs | ✅ | ✅ | ❌ |
| Supprimer machines | ✅ | ✅ | ❌ |
| Panel admin global | ✅ | ❌ | ❌ |

### Middleware

```go
// AdminRequired - Autorise admin et super_admin
func AdminRequired() fiber.Handler {
    return func(c *fiber.Ctx) error {
        role := c.Locals("role").(string)
        if role == "super_admin" || role == "admin" {
            return c.Next()
        }
        return errors.Forbidden(c, "admin access required")
    }
}
```

### Protections

| Protection | Description |
|------------|-------------|
| **Dernier admin** | Impossible de supprimer/changer le rôle du dernier admin |
| **Auto-modification** | Un admin ne peut pas modifier son propre rôle |
| **Auto-suppression** | Un admin ne peut pas se supprimer lui-même |
| **Email unique** | Contrainte UNIQUE sur email |
| **Validation rôle** | Seuls "admin" et "observer" sont acceptés |

---

## Activity Logging System

### Architecture

| Composant | Description | Fichier |
|-----------|-------------|---------|
| **Table activity_logs** | Hypertable TimescaleDB avec rétention 30 jours | `database/database.go` |
| **Service** | LogActivity, LogInfo, LogWarn, LogError | `services/activity.go` |
| **Handler** | GetActivityLogs, GetActivityStats | `handlers/activity.go` |

### Catégories d'événements

| Catégorie | Logs actifs | Messages loggés |
|-----------|-------------|-----------------|
| `auth` | 5+ | Login succès/échec, demande reset password, création utilisateur |
| `email` | 5 | "Email de réinitialisation envoyé", "Email de bienvenue envoyé", "Email de nouveau mot de passe envoyé", "Email de contact envoyé", "Email d'alerte envoyé" |
| `alert` | 2+ | Machines offline détectées, alerte résolue |
| `system` | 8 | "Groupe créé/modifié/supprimé", "Label créé/modifié/supprimé", "Paramètres de collecte modifiés", "Configuration IA modifiée" |
| `user` | 2+ | Création compte, modification profil |
| `machine` | 8 | "Machine supprimée", "Mode maintenance activé/désactivé", "Certificat révoqué/renouvelé", "Canal de mise à jour modifié", "Machines assignées/retirées du groupe", "Label assigné aux machines" |
| `certificate` | 2+ | Création, renouvellement, révocation |

### Niveaux de log

| Niveau | Description | Couleur dashboard |
|--------|-------------|-------------------|
| `info` | Événement normal | Bleu |
| `warn` | Avertissement | Jaune |
| `error` | Erreur | Rouge |

### Utilisation Backend

```go
import "github.com/2lacs-informatique/optralis/backend/internal/services"

// Log simple
services.LogInfo("auth", "User logged in successfully", map[string]interface{}{
    "email": user.Email,
}, &clientID, &userID)

// Log erreur
services.LogError("email", "Failed to send alert email", map[string]interface{}{
    "error": err.Error(),
}, &clientID, nil)
```

---

## AI Service

### Vue d'Ensemble

Service Go/Fiber autonome pour l'analyse intelligente des métriques via Claude (Anthropic).

**Stack technique :**
- Go + Fiber v2
- Claude API (Anthropic)
- PostgreSQL (partage la même DB que l'API principale)
- Redis (cache et rate limiting)

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    optralis-ai (:3002)                        │
│                     (service interne)                         │
└─────────────────────────────┬────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌──────────┐          ┌─────────┐
   │ Claude  │          │PostgreSQL│          │  Redis  │
   │   API   │          │   :5432  │          │  :6379  │
   └─────────┘          └──────────┘          └─────────┘
```

### Configuration

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | Clé API Anthropic (obligatoire) | - |
| `AI_SERVICE_PORT` | Port du service | `3002` |
| `AI_MODEL` | Modèle Claude | `claude-sonnet-4-20250514` |
| `AI_MAX_TOKENS` | Tokens max par requête | `4096` |
| `AI_DEFAULT_LANGUAGE` | Langue par défaut | `fr` |
| `AI_RATE_LIMIT_PER_MINUTE` | Rate limit | `60` |
| `AI_CACHE_TTL_MINUTES` | TTL cache Redis | `30` |
| `DATABASE_URL` | URL PostgreSQL | (partagée avec API) |
| `REDIS_URL` | URL Redis | `redis://redis:6379` |

### Système de Quota

Chaque client a un quota mensuel de requêtes AI (basé sur `license_type` dans la table `clients`).

| Licence | Quota mensuel |
|---------|---------------|
| Starter | 200 |
| Pro | 1500 |
| Enterprise | 10000 |

**Référence code** : `ai-service/internal/services/quota.go:112-118`

### Système Anti-Spam

Le service AI implémente un double système de protection contre les requêtes inutiles :

#### 1. Cooldown par Machine

Chaque type d'analyse a un cooldown spécifique par machine :

| Endpoint | Cooldown |
|----------|----------|
| `health-score` | 30 min |
| `analyze/logs` | 15 min |
| `analyze/anomalies` | 15 min |
| `analyze/full` | 2 heures |
| `analyze/trends` | 15 min |
| `analyze/degradation` | 15 min |
| `correlate` | 15 min |
| `recommendations` | 1 heure |
| `reports/generate` | 6 heures |
| `scripts/generate` | 30 min |

**Réponse si en cooldown (HTTP 429)** :
```json
{
  "error": "Analysis on cooldown",
  "cooldown": true,
  "remaining_secs": 420,
  "next_available": "2026-12-28T18:15:00Z"
}
```

**Référence code** : `ai-service/internal/services/cooldown.go`

#### 2. Détection de Changements Significatifs

Avant de lancer une analyse, le système vérifie si des changements significatifs ont eu lieu depuis la dernière analyse :

| Type de changement | Seuil significatif |
|-------------------|-------------------|
| Alertes | Nouvelle alerte ou alerte résolue |
| CPU/RAM/Disk | Variation ≥ 15% |
| Logs erreur | ≥ 3 nouveaux logs ERROR/CRITICAL |
| Événements | Nouveaux événements severity high/critical |

**Réponse si aucune nouvelle donnée (HTTP 304)** :
```json
{
  "error": "No new data since last analysis",
  "code": "NO_NEW_DATA",
  "last_analysis": "2026-12-28T17:30:00Z"
}
```

**Réponse si pas de changement significatif (HTTP 304)** :
```json
{
  "error": "No significant changes detected",
  "code": "NO_SIGNIFICANT_CHANGES",
  "message": "Les problèmes identifiés précédemment sont toujours présents...",
  "previous_issues": ["High CPU usage", "Low disk space"],
  "last_analysis": "2026-12-28T17:30:00Z"
}
```

**Référence code** : `ai-service/internal/services/change_detection.go`

#### Ordre des vérifications

```
1. Cooldown expiré ?          → Non → HTTP 429 (cooldown)
2. Nouvelles données ?        → Non → HTTP 304 (no_new_data)
3. Changements significatifs ? → Non → HTTP 304 (no_significant_changes)
4. Quota disponible ?         → Non → HTTP 429 (quota_exceeded)
5. OK → Lancer l'analyse
```

### Fonctionnement

| Mode | Description | Status |
|------|-------------|--------|
| **Automatique** | Page `/status` affiche le health de l'AI service | ✅ Implémenté |
| **Manuel (CLI)** | Appels curl depuis le VPS | ✅ Implémenté |
| **Dashboard** | Intégration UI pour déclencher analyses | 🔜 À faire |

### Exemple d'appel

```bash
# Health check
curl -s http://localhost:3002/health | jq

# Score de santé d'une machine
curl -s -X POST http://localhost:3002/ai/health-score \
  -H "Content-Type: application/json" \
  -H "X-Client-ID: <CLIENT_UUID>" \
  -d '{
    "machine_id": "<MACHINE_UUID>",
    "language": "fr"
  }' | jq
```

### Réponse type (health-score)

```json
{
  "id": "uuid",
  "machine_id": "uuid",
  "overall_score": 92,
  "category_scores": {
    "cpu": 95,
    "ram": 85,
    "disk": 95,
    "security": 80,
    "stability": 95
  },
  "trend": "stable",
  "risk_level": "low",
  "summary": "Système en excellente santé...",
  "top_issues": [
    {
      "type": "issue",
      "title": "Issue #1",
      "description": "Description du problème",
      "severity": "high"
    }
  ],
  "confidence": 0.75,
  "created_at": "2026-12-28T17:27:51Z"
}
```

### Déploiement

```bash
# Rebuild uniquement le service AI
bash scripts/deploy.sh --ai-only

# Vérifier les logs
docker logs optralis-ai --tail 50
```

### Fichiers

| Fichier | Description |
|---------|-------------|
| `ai-service/cmd/main.go` | Point d'entrée |
| `ai-service/internal/config/config.go` | Configuration |
| `ai-service/internal/handlers/analyze.go` | Handlers d'analyse |
| `ai-service/internal/handlers/health.go` | Health check |
| `ai-service/internal/handlers/reports.go` | Génération de rapports |
| `ai-service/internal/handlers/scripts.go` | Génération de scripts |
| `ai-service/internal/services/analyzer.go` | Logique d'analyse |
| `ai-service/internal/services/quota.go` | Gestion des quotas |
| `ai-service/internal/services/cooldown.go` | Système de cooldown |
| `ai-service/internal/services/change_detection.go` | Détection de changements |
| `ai-service/internal/claude/client.go` | Client Claude API |
| `ai-service/internal/claude/prompts.go` | Prompts système |

---

## Fichiers Backend

| Fichier | Description |
|---------|-------------|
| `models/notifications.go` | NotificationChannel, NotificationHistory |
| `services/notifications.go` | SendNotification, GetEnabledChannels |
| `services/webhook.go` | SendTeamsWebhook, SendSlackWebhook, SendDiscordWebhook |
| `handlers/notifications.go` | CRUD API + test endpoint |
| `services/users.go` | Gestion utilisateurs multi-tenant |
| `handlers/users.go` | API utilisateurs |
| `services/activity.go` | Logging activité |
| `handlers/activity.go` | API journal activité |

---

## Architecture Backend

### Pattern Handler → Service → Database

Le backend suit une architecture en couches stricte :

```
┌─────────────────────────────────────────────────────────────────┐
│                     handlers/ (HTTP Layer)                        │
│   - Parse requêtes HTTP, validation params                        │
│   - Appelle les services, retourne JSON                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     services/ (Business Logic)                    │
│   - Logique métier, transactions, cache                          │
│   - JAMAIS d'import fiber, JAMAIS de c.JSON()                    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     database/ (Data Layer)                        │
│   - Connexion PostgreSQL via pgx                                 │
│   - SQL brut paramétré ($1, $2...)                               │
└─────────────────────────────────────────────────────────────────┘
```

**Règles importantes :**
- Les handlers ne font JAMAIS de requêtes SQL directes
- Les services retournent des structs Go, pas des `fiber.Map`
- Les transactions utilisent `defer tx.Rollback()` systématiquement

### Transactions

```go
// Pattern correct avec defer rollback
func CreateResourceTx(tx *sql.Tx, data *Data) error {
    // tx.Rollback() est no-op si Commit() réussit
    defer tx.Rollback()

    _, err := tx.Exec(`INSERT INTO ...`)
    if err != nil {
        return err // Rollback automatique via defer
    }

    return tx.Commit()
}
```

### Batch Operations

Pour éviter les patterns N+1, utiliser `pq.Array` et `unnest()` :

```go
import "github.com/lib/pq"

// ❌ N+1 - À éviter
for _, id := range ids {
    database.DB.Exec(`INSERT INTO ... WHERE id = $1`, id)
}

// ✅ Batch - Correct
machineIDStrs := make([]string, len(machineIDs))
for i, id := range machineIDs {
    machineIDStrs[i] = id.String()
}

_, err = database.DB.Exec(`
    INSERT INTO machine_labels (machine_id, label_id, value)
    SELECT unnest($1::uuid[]), $2, $3
    ON CONFLICT (machine_id, label_id) DO UPDATE SET value = EXCLUDED.value
`, pq.Array(machineIDStrs), labelID, value)
```

### Optimisation des COUNT

Utiliser `FILTER` pour éviter plusieurs requêtes :

```go
// ❌ 6 requêtes - À éviter
database.DB.QueryRow(`SELECT COUNT(*) FROM certs WHERE status = 'valid'`)
database.DB.QueryRow(`SELECT COUNT(*) FROM certs WHERE status = 'expired'`)
// ...

// ✅ 1 requête avec FILTER - Correct
err := database.DB.QueryRow(`
    SELECT
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE revoked_at IS NULL AND expires_at > $2) as valid,
        COUNT(*) FILTER (WHERE revoked_at IS NULL AND expires_at <= $1) as expired,
        COUNT(*) FILTER (WHERE revoked_at IS NOT NULL) as revoked
    FROM client_certificates
`, now, thirtyDays).Scan(&stats.Total, &stats.Valid, &stats.Expired, &stats.Revoked)
```

### Cascade Deletes

Les foreign keys utilisent `ON DELETE CASCADE`. Ne pas supprimer manuellement les données dépendantes :

```go
// ❌ Redondant - Les DELETEs sont inutiles
database.DB.Exec(`DELETE FROM metrics WHERE machine_id = $1`, machineID)
database.DB.Exec(`DELETE FROM disk_info WHERE machine_id = $1`, machineID)
database.DB.Exec(`DELETE FROM machines WHERE id = $1`, machineID)

// ✅ Correct - CASCADE gère le cleanup
database.DB.Exec(`DELETE FROM machines WHERE id = $1 AND client_id = $2`, machineID, clientID)
```

### Structure des Services

```
services/
├── auth/                    # Authentification (clients, users)
│   ├── clients.go           # CreateClient, CreateClientTx, GetClientByID
│   └── users.go             # CreateUser, CreateUserTx, GetUserByEmail
├── machines/                # Gestion machines
│   ├── heartbeat.go         # ProcessHeartbeatWithClientID
│   ├── inventory.go         # ProcessInventoryWithClientID
│   ├── queries.go           # GetMachinesByClientID, DeleteMachine
│   ├── storage.go           # storeMetricsTx, storeDisksTx (Tx only)
│   └── collectors_storage.go # Store*FromCollectorByClientID (mTLS)
├── certificates.go          # GetCertificateStats, PurgeInactiveCertificates
├── labels.go                # AssignLabelToMachines (batch)
├── admin.go                 # CreateClientWithAdmin (transactionnel)
└── *_wrapper.go             # Backward compatibility wrappers
```

### Authentification Agent (mTLS)

Tous les endpoints agent utilisent l'authentification mTLS via `ClientID` :

```go
// ✅ Pattern mTLS - Utiliser
func StoreMetricsFromCollectorByClientID(clientID uuid.UUID, ...) error
```

> **Note**: Les fonctions legacy `*AgentKey*` ont été supprimées en v2.3.0.

Le middleware `AgentMTLSAuth` extrait le `ClientID` du certificat CN.

---

## Email Templates

### Structure des fichiers

```
backend/internal/services/templates/emails/
├── password-reset.html         # Réinitialisation mot de passe
├── welcome.html                # Bienvenue nouvel utilisateur
├── contact-confirmation.html   # Confirmation formulaire contact
├── contact-notification.html   # Notification admin (nouveau contact)
├── machine-alert.html          # Alerte machine hors ligne
├── password-expiration.html    # Rappel expiration mot de passe (90j)
├── license-expiration.html     # Rappel expiration licence
├── license-extended.html       # Confirmation prolongation licence
└── certificate-expiration.html # Alerte certificats mTLS expirés
```

### Design System (Linear Theme)

Tous les templates utilisent le design system Linear, compatible Gmail/Outlook :

| Élément | Couleur | Usage |
|---------|---------|-------|
| Page background | `#09090b` | Fond de page (zinc-950) |
| Card background | `#0a0a0a` | Carte principale |
| Header/boxes | `#0f0f0f` | En-têtes et encarts |
| Bordure subtile | `#1f1f1f` | Séparateurs |
| Texte principal | `#fafafa` | Titres, noms |
| Texte secondaire | `#a1a1aa` | Paragraphes |
| Texte tertiaire | `#71717a` | Mentions légales |
| Accent orange | `#f97316` | Boutons CTA, liens |
| Warning ambre | `#f59e0b` | Alertes expiration |
| Success vert | `#22c55e` | Confirmations |
| Danger rouge | `#ef4444` | Alertes critiques |

### Accents par template

Chaque template a un accent de couleur spécifique (ligne en haut du header + couleur du titre) :

| Template | Accent | Type |
|----------|--------|------|
| password-reset | `#f97316` Orange | Standard |
| welcome | `#f97316` Orange | Standard |
| contact-confirmation | `#22c55e` Vert | Succès |
| contact-notification | `#f97316` Orange | Standard |
| machine-alert | `#ef4444` Rouge | Danger |
| password-expiration | `#f59e0b` Ambre | Warning |
| license-expiration | `#f59e0b` Ambre | Warning |
| license-extended | `#22c55e` Vert | Succès |
| certificate-expiration | `#ef4444` Rouge | Danger |

### Variables communes

Tous les templates reçoivent ces variables :

```go
type EmailData struct {
    Language    string // "fr" ou "en"
    BaseURL     string // URL du site
    CompanyURL  string // URL de 2LACS IT
    CompanyName string // "2LACS IT"
    Year        int    // Année courante
    LogoCID     string // Content-ID pour logo inline
}
```

### Compatibilité Email

- **Pas de CSS externe** : Tout est inline
- **Pas de `rgba()`** : Couleurs hex uniquement
- **Pas de `background-clip: text`** : Non supporté Gmail
- **Tables pour layout** : Structure en tables imbriquées
- **Logo via CID** : `<img src="cid:{{.LogoCID}}" />` pour embedding inline

---

## Liens

- [Index des spécifications](README.md)
- [Agent](AGENT_SPECS.md)
- [Base de données](DATABASE_SPECS.md)
- [Dashboard](DASHBOARD_SPECS.md)
