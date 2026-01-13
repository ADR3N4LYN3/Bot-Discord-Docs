# Renouvellement automatique des certificats mTLS agents

> **Statut** : ✅ Implémenté
> **Date de planification** : 2026-01-02
> **Date d'implémentation** : 2026-01-02
> **Priorité** : Moyenne

## Résumé

Système de renouvellement automatique des certificats mTLS pour les agents Optralis. Les certificats ont une validité de 1 an et sont renouvelés automatiquement 30 jours avant expiration sans intervention manuelle.

---

## Fonctionnalités Implémentées

### ✅ Phase 1 : Vérification de révocation en temps réel

**Fichiers** :
- `backend/internal/middleware/revocation.go` (nouveau)
- `backend/internal/services/installer/cert_db.go` (modifié)
- `backend/internal/cache/cache.go` (modifié)

**Fonctionnalités** :
- Middleware `CheckCertificateRevocation()` vérifie chaque requête agent
- Cache Redis : 5 min pour certificats valides, 24h pour révoqués
- Blocage immédiat des certificats révoqués

### ✅ Phase 2 : Endpoint de renouvellement agent

**Fichier** : `backend/internal/handlers/certificate_renewal.go`

**Route** : `POST /agent/certificate/renew`

**Logique** :
1. Récupère le client ID depuis le certificat mTLS actuel
2. Vérifie que le certificat expire dans les 30 prochains jours
3. Génère un nouveau certificat via `installer.GenerateClientCertificate()`
4. Stocke les métadonnées dans `client_certificates`
5. Soft-revoke l'ancien certificat (+24h grace period)
6. Retourne le nouveau certificat + clé privée + CA cert

**Réponse** :
```json
{
  "certificate": "-----BEGIN CERTIFICATE-----...",
  "private_key": "-----BEGIN PRIVATE KEY-----...",
  "ca_certificate": "-----BEGIN CERTIFICATE-----...",
  "expires_at": "2027-01-02T00:00:00Z"
}
```

### ✅ Phase 3 : Renouvellement automatique côté agent

**Fichier** : `agent/internal/certmanager/certmanager.go`

**Fonctionnalités** :
- `CheckCertificateExpiry()` : Parse le certificat X.509 et calcule les jours restants
- `Manager.renewCertificate()` : Appelle POST /agent/certificate/renew
- Vérification toutes les 24 heures
- Sauvegarde atomique des nouveaux fichiers (temp → rename)
- Rechargement HTTP client après renouvellement

**Intégration** :
- `agent/cmd/agent/main.go` : Mode interactif
- `agent/cmd/agent/service_windows.go` : Mode service Windows

### ✅ Phase 4 : Système d'alerting automatique

**Fichiers** :
- `backend/internal/services/cert_alerting.go`
- `backend/internal/services/templates/emails/certificate-expiration.html`

**Fonctionnalités** :
- Worker quotidien à 9h00
- Détection des certificats expirant dans les 30 jours
- Classification par sévérité :
  - **expired** : Déjà expiré
  - **critical** : < 7 jours
  - **warning** : 7-30 jours
- Emails aux administrateurs du client
- Support bilingue FR/EN

### ✅ Phase 5 : Support CRL (Certificate Revocation List)

**Fichiers** :
- `backend/internal/services/installer/crl.go`
- `backend/internal/handlers/crl.go`

**Endpoint** : `GET /api/public/crl`

**Fonctionnalités** :
- Génération CRL au format DER (application/pkix-crl)
- Validité 24 heures
- Cache 5 minutes pour performance
- Invalidation automatique lors des révocations
- Liste tous les certificats révoqués

---

## Architecture Finale

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT                                     │
│                                                                  │
│  certmanager.Manager:                                           │
│  - Ticker 24h → checkAndRenew()                                 │
│  - CheckCertificateExpiry() → Parse X.509                       │
│  - Si < 30 jours → renewCertificate()                          │
└─────────────────────────────────────────────────────────────────┘
         │                                        ▲
         │ POST /agent/certificate/renew          │
         │ (mTLS avec ancien certificat)          │
         ▼                                        │
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND                                   │
│                                                                  │
│  Middleware Chain:                                               │
│  1. AgentMTLSAuth() → Extrait client_id                         │
│  2. CheckCertificateRevocation() → Vérifie révocation (cache)   │
│                                                                  │
│  Handler AgentCertificateRenewal():                             │
│  1. Vérifie expiration < 30 jours                               │
│  2. GenerateClientCertificate()                                 │
│  3. StoreCertificateMetadata()                                  │
│  4. Soft-revoke ancien cert (+24h grace)                        │
│  5. Retourne nouveau cert + key + CA                            │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Nouveau certificat
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT                                     │
│                                                                  │
│  1. Sauvegarde atomique (temp → rename)                         │
│  2. sender.ReloadHTTPClient()                                   │
│  3. Continue avec nouveau certificat                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fichiers Créés/Modifiés

### Backend (nouveaux)

| Fichier | Description |
|---------|-------------|
| `backend/internal/handlers/certificate_renewal.go` | Handler renouvellement agent |
| `backend/internal/handlers/crl.go` | Handler endpoint CRL public |
| `backend/internal/middleware/revocation.go` | Middleware vérification révocation |
| `backend/internal/services/cert_alerting.go` | Service d'alerting certificats |
| `backend/internal/services/installer/crl.go` | Génération CRL |
| `backend/internal/services/templates/emails/certificate-expiration.html` | Template email |

### Backend (modifications)

| Fichier | Description |
|---------|-------------|
| `backend/cmd/api/main.go` | Routes + middleware + worker |
| `backend/internal/services/installer/cert_db.go` | Cache révocation + soft-revoke |
| `backend/internal/cache/cache.go` | Fonctions cache certificats |

### Agent (nouveaux)

| Fichier | Description |
|---------|-------------|
| `agent/internal/certmanager/certmanager.go` | Gestionnaire cycle de vie certificats |

### Agent (modifications)

| Fichier | Description |
|---------|-------------|
| `agent/cmd/agent/main.go` | Intégration certmanager |
| `agent/cmd/agent/service_windows.go` | Intégration certmanager Windows |
| `agent/internal/sender/sender.go` | Export GetHTTPClient/ReloadHTTPClient |

---

## Configuration

### Constantes Backend

```go
// Renouvellement
const RenewalWindowDays = 30    // Fenêtre de renouvellement avant expiration
const GracePeriodHours = 24     // Grace period pour ancien certificat

// CRL
const CRLValidityDuration = 24 * time.Hour  // Validité CRL
const CRLCacheDuration = 5 * time.Minute    // Cache CRL

// Alerting
const AlertCheckTime = "09:00"  // Heure de vérification quotidienne
```

### Constantes Agent

```go
const checkInterval = 24 * time.Hour  // Intervalle de vérification
const renewalThreshold = 30           // Jours avant expiration pour renouveler
```

### Cache Redis

| Clé | TTL | Description |
|-----|-----|-------------|
| `cert:revoked:<client_id>` | 24h | Certificat révoqué |
| `cert:valid:<client_id>` | 5min | Certificat valide |

---

## Sécurité

| Mesure | Description |
|--------|-------------|
| Authentification | Le renouvellement nécessite un certificat mTLS valide (pas encore expiré) |
| Fenêtre de renouvellement | Uniquement si le certificat expire dans < 30 jours |
| Grace period | L'ancien certificat reste valide 24h après renouvellement |
| Vérification révocation | Middleware vérifie chaque requête agent |
| Cache invalidation | La révocation invalide immédiatement le cache |
| Sauvegarde atomique | Agent utilise temp file + rename pour éviter corruption |

---

## Tests Recommandés

### Tests unitaires
1. `certmanager.CheckCertificateExpiry()` avec différentes dates
2. Parsing de la réponse de renouvellement
3. Validation du nouveau certificat avant sauvegarde
4. Génération CRL avec certificats révoqués

### Tests d'intégration
1. Agent avec certificat expirant dans 25 jours → renouvellement déclenché
2. Agent avec certificat expirant dans 60 jours → pas de renouvellement
3. Vérifier que l'ancien certificat fonctionne pendant la grace period
4. Vérifier que le nouveau certificat fonctionne immédiatement
5. Vérifier que la révocation bloque les requêtes

### Tests manuels
1. Forcer l'expiration d'un certificat (modifier DB)
2. Vérifier le log de l'agent pour le renouvellement
3. Vérifier que le dashboard affiche le bon statut
4. Tester l'endpoint CRL avec openssl

---

## Commandes Utiles

```bash
# Vérifier un certificat agent
openssl x509 -in /etc/optralis-agent/client.crt -text -noout

# Vérifier la CRL
curl -s https://optralis-agent-api.2lacs-it.com/api/public/crl -o optralis.crl
openssl crl -in optralis.crl -inform DER -text -noout

# Forcer un renouvellement (test)
# Modifier cert_expires_at dans client_certificates à NOW() + 25 days
```

---

## Résultat

✅ Les certificats se renouvellent automatiquement 30 jours avant expiration
✅ Aucune intervention manuelle requise
✅ Grace period de 24h pour éviter les interruptions
✅ Logs détaillés des renouvellements
✅ Dashboard affiche le statut à jour
✅ Alertes email pour les certificats expirants
✅ CRL accessible publiquement pour validation externe
✅ Vérification de révocation en temps réel

---

## Interface Dashboard

### ✅ Phase 6 : UI de gestion des certificats (2026-01-02)

**Fonctionnalités implémentées** :

#### Onglet "Certificat machine" (page détail machine)

**Fichiers** :
- `dashboard/components/MachineDetailsSidebar.tsx` (modifié)
- `dashboard/app/dashboard/machines/[hostname]/tabs/CertificateTab.tsx` (nouveau)
- `dashboard/app/dashboard/machines/[hostname]/page.tsx` (modifié)

**Fonctionnalités** :
- Nouvel onglet "Certificat machine" dans la sidebar de navigation
- Indicateur coloré sur l'onglet selon le statut du certificat
- Affichage complet : statut, serial, dates d'émission/expiration/révocation
- Boutons Révoquer et Renouveler (admin uniquement)
- Modal de confirmation pour la révocation
- Section certificat retirée de l'overview pour éviter la duplication

#### Page admin "Certificats" (super_admin uniquement)

**Fichiers** :
- `dashboard/components/AdminSidebar.tsx` (modifié)
- `dashboard/app/dashboard/admin/certificates/page.tsx` (nouveau)
- `backend/internal/handlers/certificates.go` (nouveau)
- `dashboard/lib/api.ts` (modifié)

**Endpoints API** :
- `GET /api/admin/certificates` - Liste tous les certificats avec filtres
- `GET /api/admin/certificates/stats` - Statistiques des certificats

**Fonctionnalités** :
- Vue globale de tous les certificats cross-clients
- Cards de statistiques : total, valides, expirant bientôt (<30j), expirant (<7j), expirés, révoqués
- Filtres : par statut, par client, recherche (hostname/serial)
- Tableau avec colonnes : statut, machine (lien), client, serial, dates
- Pagination (25 par page)
- Liens directs vers les pages machines

#### Logging d'activité

**Fichiers modifiés** :
- `backend/internal/models/activity.go` - Nouvelle catégorie `certificate`
- `backend/internal/handlers/certificate_renewal.go` - Log auto-renouvellement agent
- `backend/internal/handlers/machines.go` - Log révocation/renouvellement admin
- `backend/internal/handlers/bootstrap.go` - Log création certificat bootstrap
- `dashboard/app/dashboard/admin/activity/page.tsx` - Icône et badge certificat

**Événements loggés** :
- `Agent certificate auto-renewed` - Renouvellement automatique par agent
- `Certificate revoked by admin` - Révocation manuelle par admin
- `Certificate renewed by admin` - Renouvellement manuel par admin
- `Agent certificate created (bootstrap)` - Création lors de l'installation

#### Traductions

**Fichier** : `dashboard/lib/i18n.tsx`

Nouvelles clés ajoutées :
- `tabs.certificate` - Label de l'onglet
- `cert.machineDescription` - Description dans l'onglet
- `cert.noCertDescription` - Message si pas de certificat
- `cert.revokedAt` - Label date de révocation
- `cert.status`, `cert.machine`, `cert.client`, `cert.total` - Labels tableau
- `cert.adminDescription` - Description page admin
- `cert.searchPlaceholder`, `cert.filterByStatus`, `cert.filterByClient` - Placeholders filtres
- `cert.noCertificates` - Message si aucun résultat
- `admin.sidebar.certificates` - Label sidebar admin
- `common.showingResults` - Pagination
- `activity.category.certificate` - Catégorie journal d'activité

---

### ✅ Phase 7 : Amélioration de la page admin certificats (2026-01-03)

**Fichiers modifiés** :
- `dashboard/app/dashboard/admin/certificates/page.tsx` - Refonte complète
- `dashboard/lib/api.ts` - Nouvelles fonctions API
- `dashboard/lib/i18n.tsx` - Nouvelles traductions

**Nouvelles fonctionnalités** :

#### Séparation en deux tableaux
- **Tableau "Certificats actifs"** : valid, expiring_soon, expiring
- **Tableau "Certificats inactifs"** : expired, revoked
- Compteurs affichés dans l'en-tête de chaque tableau
- Pagination indépendante pour chaque tableau

#### Menu d'actions par certificat
- Icône ⋮ (trois points verticaux) sur chaque ligne
- **Copier le serial** : Copie le numéro de série dans le presse-papier
- **Révoquer** : Pour les certificats actifs uniquement
- **Restaurer** : Pour les certificats révoqués uniquement

#### Modales de confirmation
- Confirmation avant révocation avec avertissement
- Confirmation avant restauration
- Confirmation avant purge des certificats inactifs

#### Bouton "Purger inactifs"
- Affiché dans le header si des certificats inactifs existent
- Supprime tous les certificats expirés et révoqués en une action

#### Nouvelles fonctions API
```typescript
// Révoquer un certificat par serial
revokeCertificate(serial: string, reason?: string): Promise<{ status: string; serial: string; message: string }>

// Restaurer un certificat révoqué
restoreCertificate(serial: string): Promise<{ status: string; serial: string; message: string }>

// Purger tous les certificats expirés/révoqués
purgeCertificates(): Promise<{ deleted: number; message: string }>
```

#### Nouvelles traductions (14 clés)
- `common.actions` - Label colonne actions
- `cert.activeCertificates` / `cert.inactiveCertificates` - Titres tableaux
- `cert.noActiveCertificates` / `cert.noInactiveCertificates` - Messages vides
- `cert.copySerial` - Option copier
- `cert.revokeTitle` / `cert.revokeMessage` - Modal révocation
- `cert.restore` / `cert.restoreTitle` / `cert.restoreMessage` - Modal restauration
- `cert.purgeInactive` / `cert.purgeTitle` / `cert.purgeMessage` / `cert.purgeConfirm` - Modal purge

#### Design responsive
- **Mobile** : Vue cartes avec détails compacts et menu d'actions
- **Desktop** : Tableau complet avec colonnes triables et actions
