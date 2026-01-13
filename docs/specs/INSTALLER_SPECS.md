# Installateurs & Scripts - Spécifications Techniques

## Vue d'ensemble

Installateurs Windows (Go + WebView2) et Linux (bash), scripts de build multi-plateforme et déploiement Docker.

---

## Installateur Personnalisé (Recommandé)

### Nouveau flux d'installation mTLS

Le dashboard génère un installeur **personnalisé** par client avec certificat mTLS intégré.

```
Dashboard "Télécharger installeur"
         │
         ├─► Windows: optralis-setup.exe (agent + cert + config)
         │
         └─► Linux: install-optralis-agent.sh (script + cert base64)
```

**Avantages :**
- Pas de clé API à copier/coller
- Certificat mTLS unique par client
- Installation en 1 clic
- Révocation possible si compromis

**Endpoints :**
- `GET /api/installer/windows` → .exe auto-extractible
- `GET /api/installer/linux/amd64` → script shell
- `GET /api/installer/linux/arm64` → script shell ARM

**Nom de fichier versionné :**

Le backend retourne un header `Content-Disposition` avec le nom de fichier basé sur la version stable :
```
Content-Disposition: attachment; filename=optralis-agent-v1.0.0.exe
```

Le frontend extrait ce nom depuis le header pour le téléchargement :
```typescript
const contentDisposition = response.headers.get('Content-Disposition');
const match = contentDisposition?.match(/filename=([^;\s]+)/);
const filename = match?.[1] || 'optralis-agent-setup.exe';
```

> **Note:** Si aucune version stable n'existe en base de données, le fallback utilise l'ID client : `optralis-agent-{clientId}.exe`

---

## Génération EXE Windows (Backend)

### Architecture Stub + Payload

Le backend génère des EXE personnalisés en combinant un **stub pré-compilé** avec un **payload ZIP** contenant les certificats.

```
┌─────────────────────────────────────────────┐
│  optralis-agent-XXXX.exe                    │
├─────────────────────────────────────────────┤
│  optralis-stub.exe (pré-compilé ~2MB)       │
├─────────────────────────────────────────────┤
│  ---OPTRALIS_PAYLOAD---                     │
├─────────────────────────────────────────────┤
│  payload.zip                                │
│  ├── client.crt (certificat mTLS unique)   │
│  ├── client.key (clé privée)               │
│  └── config.json (URL API)                 │
└─────────────────────────────────────────────┘
```

### Flux d'exécution du Stub

```
Utilisateur double-clic sur optralis-agent-XXXX.exe
    │
    ├── 1. Lit son propre fichier
    ├── 2. Trouve le marqueur ---OPTRALIS_PAYLOAD---
    ├── 3. Extrait le ZIP vers dossier temporaire
    ├── 4. Récupère metadata-windows.json pour obtenir le nom du fichier
    ├── 5. Télécharge l'installeur principal depuis CDN
    └── 6. Lance l'installeur avec -mtls-cert et -mtls-key (mode GUI)
              │
              └── Le GUI détecte les certificats mTLS
                  └── Installation automatique (pas de formulaire)
```

> **Note :** Le stub récupère dynamiquement le nom du fichier installeur depuis `metadata-windows.json` au lieu d'utiliser une URL fixe. Cela permet de mettre à jour la version de l'installeur sans recompiler le stub.

### Détection automatique mTLS (GUI)

Quand l'installeur est lancé avec les flags `-mtls-cert` et `-mtls-key` (par le stub), le GUI :

1. **Détecte les certificats mTLS** au démarrage via `checkMTLSConfig()`
2. **Affiche un écran simplifié** avec notice verte "Certificat mTLS détecté"
3. **Cache les champs d'authentification** (clé agent, URL serveur)
4. **Affiche l'option LHM** pour permettre le choix du driver température
5. **Lance l'installation mTLS** quand l'utilisateur clique sur "Installer"

```javascript
// app.js - Vérification au démarrage
async function init() {
    const mtlsConfig = JSON.parse(await checkMTLSConfig());
    if (mtlsConfig.hasMTLS) {
        hasMTLS = true;
        // Afficher écran simplifié avec option LHM
        document.getElementById('mtls-notice').classList.remove('hidden');
        document.getElementById('auth-fields').classList.add('hidden');
        // L'utilisateur peut choisir LHM puis cliquer Installer
    }
    // ...
}

// startInstall() utilise automatiquement mTLS si disponible
if (hasMTLS) {
    setInstallLHM(installLHM);
    installWithMTLS();
}
```

**Comportement selon le mode de lancement :**

| Lancement | Certificats | Comportement |
|-----------|-------------|--------------|
| Via stub (dashboard) | mTLS présents | GUI → Écran simplifié avec option LHM |
| Direct (sans stub) | Aucun | GUI → Formulaire complet (clé agent + URL) |
| `-silent` | mTLS présents | CLI → Installation silencieuse (sans LHM par défaut) |
| `-silent -with-lhm` | mTLS présents | CLI → Installation silencieuse avec LHM |

### Fichiers du Stub

| Fichier | Description |
|---------|-------------|
| `installer/stub/main.go` | Code source du stub |
| `installer/stub/go.mod` | Module Go |
| `installer/stub/winres/winres.json` | Configuration des ressources Windows (icône, manifeste) |
| `installer/stub/winres/icon.png` | Icône de l'application |
| `installer/stub/rsrc_windows_amd64.syso` | Ressources Windows compilées (généré par go-winres) |
| `deploy/downloads/optralis-stub.exe` | Binaire pré-compilé (utilisé par le backend) |

### Configuration Backend

| Variable d'environnement | Défaut | Description |
|--------------------------|--------|-------------|
| `STUB_PATH_WINDOWS` | `/srv/downloads/optralis-stub.exe` | Chemin vers le stub |
| `AGENT_API_URL` | `https://optralis-agent-api.2lacs-it.com` | URL API agent (mTLS) |

### Fallback ZIP

Si le stub n'est pas disponible sur le serveur, le backend génère un ZIP classique contenant :
- `optralis-agent.exe`
- `client.crt` / `client.key`
- `config.json`
- `install.ps1`
- `README.txt`

### Déploiement de masse Windows

Pour installer l'agent sur plusieurs machines Windows avec le même EXE :

**Dashboard :**
1. Aller sur Installation → Windows
2. Sélectionner le nombre de machines (1, 10, 50, ou Illimité)
3. Cliquer "Télécharger Windows"
4. Distribuer l'EXE sur toutes les machines cibles

**Caractéristiques :**
- Token multi-usage : un même EXE peut installer N machines
- Validité : 24 heures
- Certificat unique par machine : chaque installation génère son propre certificat mTLS
- Suivi en temps réel : barre de progression "X/N machines installées"

**API :**
```
GET /api/installer/windows?max_usage=50
```

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `max_usage` | int | 1 | Nombre max de machines (0 = illimité) |

**Endpoint de suivi :**
```
GET /api/install-tokens/windows/active
```

Retourne le token Windows actif avec `usage_count` et `max_usage` pour afficher la progression.

**Note :** Le token disparaît automatiquement de cet endpoint quand le quota est atteint (`usage_count >= max_usage`). Les tokens illimités (`max_usage = 0`) restent visibles jusqu'à expiration.

**Révocation :**
- Révoquer un token = nouvelles installations bloquées
- Machines déjà installées = continuent de fonctionner (certificat indépendant)

---

## Installateur Windows

### Architecture

Installateur Go avec interface WebView2 (Edge) supportant GUI et CLI.

### Usage

```bash
# Mode GUI (double-clic) - pour installeur personnalisé avec cert intégré
optralis-agent.exe

# Mode silencieux (pour installeur personnalisé)
optralis-agent.exe -silent

# Avec URL personnalisée
optralis-agent.exe -silent -url https://api.example.com

# Aide
optralis-agent.exe -help
```

> **Note sécurité :** Le flag `-key` a été supprimé (visible dans `ps aux`).
> Utiliser l'installeur personnalisé depuis le dashboard qui inclut le certificat mTLS.

### Options CLI

| Option | Description | Défaut |
|--------|-------------|--------|
| `-silent` | Installation sans GUI | - |
| `-url <url>` | URL de l'API | https://optralis-api.2lacs-it.com |
| `-with-lhm` | Installer le driver LHM pour températures CPU précises | Désactivé |

### Option LHM (Températures CPU)

LibreHardwareMonitor (LHM) permet de lire les températures CPU précises via les registres MSR du processeur.

**Pourquoi c'est optionnel ?**
- Le driver WinRing0 (utilisé par LHM) est parfois détecté comme malveillant par certains antivirus
- Ce comportement est un faux positif (le driver accède au matériel de bas niveau)
- LHM est largement utilisé et fiable (HWiNFO, Open Hardware Monitor, etc.)

**Comportement par défaut :**
- LHM **désactivé** par défaut (approche sécurité d'abord)
- L'agent utilise le fallback WMI pour les températures (moins précis mais fonctionnel)

**Mode GUI :**
- Une checkbox "Installer le driver de température CPU (LHM)" est disponible
- Quand cochée, un warning et les instructions d'exclusion antivirus s'affichent
- Chemins à exclure :
  - Dossier : `C:\Program Files\Optralis Agent\lhm\`
  - Processus : `lhm-wrapper.exe`

**Mode silencieux :**
```bash
# Sans LHM (défaut)
optralis-agent.exe -silent -mtls-cert cert.crt -mtls-key key.key

# Avec LHM (opt-in explicite)
optralis-agent.exe -silent -with-lhm -mtls-cert cert.crt -mtls-key key.key
```

**Fallback température (agent) :**
1. LHM installé → Températures CPU précises (par core)
2. LHM absent → WMI ThermalZone (température système/chipset)
3. Aucun disponible → -1 (non disponible)

### Chemins d'installation

| Élément | Chemin |
|---------|--------|
| Exécutable | `C:\Program Files\Optralis Agent\optralis-agent.exe` |
| LHM | `C:\Program Files\Optralis Agent\lhm\` *(optionnel)* |
| Configuration | `C:\ProgramData\optralis-agent\config.json` |
| Certificats mTLS | `C:\ProgramData\optralis-agent\client.crt` / `client.key` |
| Service | `OptralisAgent` |

### Format config.json (mTLS)

Quand l'installeur est lancé avec des certificats mTLS, il génère automatiquement :

```json
{
  "api_url": "https://optralis-agent-api.2lacs-it.com",
  "interval": 10,
  "mtls_enabled": true,
  "mtls_cert_path": "C:\\ProgramData\\optralis-agent\\client.crt",
  "mtls_key_path": "C:\\ProgramData\\optralis-agent\\client.key"
}
```

**Champs obligatoires pour mTLS :**

| Champ | Description |
|-------|-------------|
| `mtls_enabled` | **Obligatoire** - Doit être `true` pour activer l'authentification mTLS |
| `mtls_cert_path` | Chemin absolu vers le certificat client |
| `mtls_key_path` | Chemin absolu vers la clé privée |

> **Note technique :** L'agent vérifie `mtls_enabled` avant de charger les certificats. Sans ce flag à `true`, l'agent ignore les chemins de certificats même s'ils sont présents.

### Vérification de compatibilité OS

L'installateur vérifie la version Windows **avant** l'élévation admin (UAC).

**Flux de vérification :**
1. Appel API `GET /agent/requirements` pour récupérer la config serveur
2. Si API disponible → utilise `min_windows_version` configuré
3. Si API indisponible → fallback sur Windows 10 LTSC 2019+ (build ≥ 17763)
4. Affiche une fenêtre d'erreur stylisée si OS non supporté

**Versions supportées :**
- Windows 11 (toutes versions)
- Windows 10 LTSC 2019+ (Build 17763+)
- Windows Server 2016/2019/2022/2025

**Versions non supportées :**
- Windows 10 standard (builds < 17763)
- Windows 7 (6.1)
- Windows 8 (6.2)
- Windows 8.1 (6.3)
- Windows Server 2012/R2 (6.2/6.3)

**Configuration via dashboard :**
- Page `/dashboard/admin/updates` → Section "Versions OS supportées"
- Permet de modifier `min_windows_version` (10, 6, etc.)
- Message personnalisé optionnel pour les OS non supportés

**Fichiers concernés :**
- `installer/go-installer/main.go` : `fetchAgentRequirements()`, `showUnsupportedOSErrorWithMessage()`
- `installer/go-installer/windows.go` : `isSupportedWindows()`, `isSupportedWindowsWithMinVersion()`

---

## Installateur Linux

### Installation rapide via Curl + Token (Recommandé)

Méthode simple pour déployer l'agent sur plusieurs machines Linux :

```bash
curl -fsSL https://optralis.2lacs-it.com/install.sh | sudo bash -s -- <TOKEN>
```

**Workflow :**
1. Dashboard → Installation → Clic "Générer token Linux"
2. Modal affiche la commande curl avec le token
3. Copier-coller sur les machines Linux cibles
4. Le script échange le token contre des certificats mTLS uniques
5. L'agent est installé avec mTLS activé

**Caractéristiques du token :**
- Validité : 15 minutes par défaut (configurable jusqu'à 60 min)
- Multi-usage : un même token peut installer plusieurs machines
- Sécurisé : token hashé SHA256 en base de données
- Traçabilité : compteur d'utilisation visible dans le dashboard

**Processus technique :**
```
Machine Linux                                Backend
     │                                           │
     ├──── POST /api/public/bootstrap ──────────►│
     │     {token, hostname, hardware_id, arch}  │
     │                                           │
     │     Backend:                              │
     │     1. Valide le token                    │
     │     2. Récupère ou crée la machine        │
     │     3. Génère certificat (CN=client:machine) │
     │                                           │
     │◄─── Réponse JSON ────────────────────────┤
     │     - client_id                           │
     │     - machine_id                          │
     │     - certificate (mTLS unique/machine)   │
     │     - private_key                         │
     │     - ca_cert                             │
     │     - api_url                             │
     │     - binary_url                          │
     │                                           │
     ├──── Téléchargement binaire ──────────────►│
     │                                           │
     └──── Agent démarré avec mTLS (1:1)        │
```

**Champs de la requête bootstrap :**
| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `token` | string | Oui | Token d'installation |
| `hostname` | string | Oui | Hostname de la machine |
| `hardware_id` | string | Non | ID matériel (DMI product_uuid ou machine-id) |
| `arch` | string | Non | Architecture (amd64, arm64) |

**Architectures supportées :**
- `amd64` (x86_64) - détecté automatiquement
- `arm64` (aarch64) - détecté automatiquement

**API Endpoints :**
- `POST /api/public/bootstrap` - Échange token → certificats (public, pas de mTLS)
- `POST /api/install-tokens` - Créer un token (admin requis)
- `GET /api/install-tokens` - Lister les tokens actifs
- `DELETE /api/install-tokens/:id` - Révoquer un token (admin requis)

### Script personnalisé (Alternative)

Télécharger depuis le dashboard → Installation avec certificat mTLS intégré :

```bash
# Télécharger depuis le dashboard
chmod +x install-optralis-agent.sh
sudo ./install-optralis-agent.sh
```

### Script générique (Legacy)

> **Déprécié :** Utiliser la méthode curl + token ci-dessus.

```bash
# Redirection vers le dashboard
curl -fsSL https://optralis.2lacs-it.com/install.sh | sudo bash
```

### Chemins d'installation

| Élément | Chemin |
|---------|--------|
| Exécutable | `/usr/local/bin/optralis-agent` |
| Configuration | `/etc/optralis-agent/config.json` |
| Service | `optralis-agent.service` (systemd) |
| Logs | `/var/log/optralis-agent/` |

---

## Pages Dashboard

### Page Documentation (`/dashboard/documentation`)

Page "Quick Install" pour les utilisateurs qui veulent installer rapidement via la méthode classique (clé agent).

**Fonctionnalités:**
- Bannière mTLS avec badge "NEW" redirigeant vers `/installation`
- Téléchargement EXE Windows depuis CDN (nécessite clé agent)
- Commande PowerShell one-liner
- Commande curl Linux
- Notes de sécurité

**Traductions clés:**
| Clé | Description |
|-----|-------------|
| `installation.mtlsRecommended` | Titre de la bannière mTLS |
| `installation.mtlsRecommendedDesc` | Description WebView2 + auto-détection |
| `quickInstall.option1` | "GUI installer (WebView2)" |
| `quickInstall.option1Note` | Note explicative Quick Install vs mTLS |

### Page Installation (`/dashboard/installation`)

Page principale pour générer des installeurs personnalisés avec mTLS.

**Sections:**
1. **Versions actuelles** - Affiche les dernières versions disponibles
2. **Installeur personnalisé** - Boutons de téléchargement Windows/Linux avec mTLS
3. **Installation rapide Linux** - Génération de token + commande curl
4. **Mise à jour** - Instructions de mise à jour
5. **Désinstallation** - Instructions de suppression

**Fonctionnalités clés:**
- Badge "NEW" sur Windows pour indiquer le GUI WebView2
- Génération d'installeurs personnalisés avec certificat mTLS intégré
- Tokens d'installation Linux (validité 15 min, multi-usage)
- Countdown en temps réel pour l'expiration du token

**Traductions clés:**
| Clé | Description |
|-----|-------------|
| `installation.personalizedInstallerDesc` | "Automatic installation, no configuration required" |
| `installation.windowsInstallerDesc` | "EXE installer with WebView2 GUI" |
| `installation.quickInstallLinux` | Section token Linux |

---

## Scripts de Build

### Windows (build-agent.ps1)

```powershell
# Build stable (par défaut)
.\scripts\build-agent.ps1 -Version 1.0.0 -Channel stable -Push

# Build beta
.\scripts\build-agent.ps1 -Version 1.0.0 -Channel beta -Push

# Options
# -Version 1.0.0    : Spécifier la version (obligatoire)
# -Channel stable   : Canal stable (défaut) ou beta
# -Push             : Push vers git après build
```

**Le script:**
1. Compile LibreHardwareMonitor wrapper (C# .NET)
2. Génère les ressources Windows (icône, manifest) pour l'agent
3. Compile l'agent Windows (Go)
4. Compile l'uninstaller (Go + WebView2)
5. **Génère les ressources Windows pour le stub** (icône, manifest via go-winres)
6. **Compile le stub mTLS** (Go, sans CGO)
7. Compile l'installateur Go + WebView2
8. Génère `metadata-windows.json` avec checksum SHA256 **(UTF-8 sans BOM)**
9. Copie vers deploy/downloads/<channel>/
10. **Copie le stub vers deploy/downloads/** (partagé entre canaux)
11. Push vers git (avec -Push)

**Sortie:**
- Binaire: `optralis-agent-v{version}.exe`
- Metadata: `metadata-windows.json`

> **Note technique:** Le script utilise `[System.IO.File]::WriteAllText()` avec `UTF8Encoding($false)` pour éviter le BOM UTF-8 qui causerait des erreurs de parsing JSON côté backend Go.

### Linux (build-agent.sh)

```bash
# Build stable (par défaut)
bash scripts/build-agent.sh -v 1.0.0 -c stable

# Build beta
bash scripts/build-agent.sh -v 1.0.0 -c beta

# Options
# -v, --version     : Spécifier la version (obligatoire)
# -c, --channel     : Canal stable (défaut) ou beta
```

**Le script:**
1. Compile l'agent Linux pour amd64 et arm64
2. Génère metadata-linux.json avec checksums SHA256
3. Copie les binaires vers deploy/downloads/<channel>/

**Sortie:**
- Binaires:
  - `optralis-agent-linux-amd64-v{version}`
  - `optralis-agent-linux-arm64-v{version}`
- Metadata: `metadata-linux.json`

---

## Structure des fichiers de build

```
deploy/downloads/
├── stable/
│   ├── optralis-agent-v1.0.0.exe              # Windows installer
│   ├── optralis-agent-linux-amd64-v1.0.0      # Linux amd64
│   ├── optralis-agent-linux-arm64-v1.0.0      # Linux arm64
│   ├── metadata-windows.json                   # Metadata Windows
│   └── metadata-linux.json                     # Metadata Linux
├── beta/
│   └── (même structure)
├── optralis-stub.exe                           # Stub mTLS (partagé)
├── install.sh                                  # Script installation Linux
├── install.ps1                                 # Script installation Windows
└── uninstall.sh                                # Script désinstallation Linux
```

---

## Canaux de mise à jour

| Canal | Description | Dossier |
|-------|-------------|---------|
| **stable** | Version de production | `deploy/downloads/stable/` |
| **beta** | Version de test | `deploy/downloads/beta/` |

---

## Format des fichiers metadata

### metadata-windows.json

```json
{
  "version": "1.0.0",
  "channel": "stable",
  "platform": "windows",
  "architecture": "amd64",
  "filename": "optralis-agent-v1.0.0.exe",
  "checksum_sha256": "abc123...",
  "file_size_bytes": 26000000,
  "build_time": "2025-12-17T10:30:00Z"
}
```

### metadata-linux.json

```json
{
  "version": "1.0.0",
  "channel": "stable",
  "platform": "linux",
  "architectures": {
    "amd64": {
      "filename": "optralis-agent-linux-amd64-v1.0.0",
      "checksum_sha256": "def456...",
      "file_size_bytes": 15000000
    },
    "arm64": {
      "filename": "optralis-agent-linux-arm64-v1.0.0",
      "checksum_sha256": "ghi789...",
      "file_size_bytes": 14500000
    }
  },
  "build_time": "2025-12-17T10:30:00Z"
}
```

---

## Système Multi-Plateforme

### Architecture de la base de données

**Table `agent_versions` :**
- Colonnes: `id`, `version`, `channel`, `platform`, `architecture`, `checksum_sha256`, `file_size_bytes`, `download_url`, `release_date`, `is_active`, `created_at`
- Contrainte unique: `(version, channel, platform, architecture)`

### API Multi-Plateforme

**Endpoint:** `GET /api/agent/latest-version?channel=stable&platform=windows&architecture=amd64`

Paramètres:
- `channel`: stable ou beta (défaut: stable)
- `platform`: windows ou linux (défaut: windows)
- `architecture`: amd64 ou arm64 (défaut: amd64)

### Dashboard Admin - Page Updates

**URL:** `/dashboard/admin/updates`

**Onglets par plateforme:**
- Windows - Liste des versions Windows avec statistiques
- Linux - Liste des versions Linux avec statistiques

**Statistiques par version:**
- Nombre de machines utilisant cette version
- Date de création
- Taille du fichier

**Modal de création/édition:**
- Sélecteur de plateforme (Windows/Linux)
- Sélecteur d'architecture (amd64/arm64) - affiché uniquement pour Linux
- Numéro de version
- Canal (stable/beta)
- Checksum SHA256
- Taille du fichier
- URL de téléchargement
- Bouton "Importer depuis serveur"

---

## Workflow de Build Multi-Plateforme

1. **Build Windows** (sur PC Windows):
   ```powershell
   .\scripts\build-agent.ps1 -Version 1.0.0 -Channel stable -Push
   ```

2. **Build Linux** (sur VPS ou PC):
   ```bash
   bash scripts/build-agent.sh -v 1.0.0 -c stable
   ```

3. **Déploiement** (sur VPS):
   ```bash
   bash scripts/deploy.sh
   ```

---

## Déploiement

```bash
bash scripts/deploy.sh

# Options:
# --skip-api --skip-dashboard : Agent seulement
# --skip-git : Sans git pull
# --ai-only : Rebuild uniquement le service AI
```

**Le script:**
- Pull les dernières modifications git
- Build l'agent Linux
- Rebuild et redémarre les containers (API, Dashboard, Caddy)

---

## Configuration mTLS (Prérequis)

### Initialisation de la CA

Avant le premier déploiement avec mTLS, initialiser la CA sur le serveur :

```bash
# Créer la CA interne (10 ans de validité)
sudo ./scripts/init-agent-ca.sh

# Fichiers créés :
# - /etc/optralis/ca/ca.key  (clé privée, garder sécurisé!)
# - /etc/optralis/ca/ca.crt  (certificat public)
```

### Configuration Docker

Le docker-compose monte automatiquement la CA dans Caddy :

```yaml
caddy:
  volumes:
    - /etc/optralis/ca/ca.crt:/etc/caddy/optralis-agent-ca.crt:ro
```

### Vérification

```bash
# Vérifier que la CA est accessible dans le container
docker exec optralis-caddy cat /etc/caddy/optralis-agent-ca.crt

# Vérifier les logs Caddy
docker logs optralis-caddy --tail 20
```

### Renouvellement CA

La CA expire après 10 ans. Pour renouveler :

```bash
# Backup de l'ancienne CA
sudo cp -r /etc/optralis/ca /etc/optralis/ca.backup.$(date +%Y%m%d)

# Régénérer (attention: invalide tous les certificats agents existants!)
sudo ./scripts/init-agent-ca.sh --force

# Redémarrer Caddy
docker restart optralis-caddy
```

> **Important :** Le renouvellement de la CA invalide tous les certificats agents.
> Les agents devront être réinstallés avec un nouvel installeur.

---

## Auto-Update Multi-Plateforme

L'agent détecte automatiquement sa plateforme et architecture via `runtime.GOOS` et `runtime.GOARCH`.

### Heartbeat

L'agent envoie son architecture dans le payload (authentifié via mTLS):
```json
{
  "agent_version": "1.0.0",
  "os": "linux",
  "architecture": "amd64"
}
```

### Vérification de mise à jour

Le serveur compare la version de l'agent avec la dernière version disponible. Si mise à jour disponible:
```json
{
  "status": "ok",
  "update": {
    "version": "1.1.0",
    "download_url": "https://optralis.2lacs-it.com/downloads/stable/optralis-agent-linux-amd64-v1.1.0",
    "checksum_sha256": "def456..."
  }
}
```

---

## Gestion des versions

Le numéro de version est injecté au build via `ldflags` - c'est un **label** uniquement.

**Comportement auto-update :**
- Version serveur > version agent → Mise à jour automatique
- Version serveur ≤ version agent → Rien (pas de downgrade)

Pour forcer un downgrade, réinstaller manuellement l'agent.

---

## Troubleshooting Build

### Erreur "fichier verrouillé"

```powershell
# Le build échoue car le service verrouille les fichiers
Stop-Service OptralisAgent -Force
Start-Sleep 3
Remove-Item -Recurse -Force "build"
.\scripts\build-agent.ps1 -Version "1.0.0" -Push
```

### Version incorrecte après build

Si l'agent affiche une mauvaise version, le build a réutilisé d'anciens fichiers. Le script vérifie maintenant les erreurs et échoue proprement.

### Erreur parsing JSON metadata (BOM UTF-8)

**Symptômes :** Le backend ne liste pas les versions Windows disponibles depuis `/api/agent-versions/available-downloads`, mais Linux fonctionne.

**Cause :** PowerShell ajoute un BOM UTF-8 (`EF BB BF`) par défaut avec `Out-File -Encoding utf8`. Go's `json.Unmarshal()` échoue silencieusement.

**Diagnostic :**
```powershell
# Vérifier les premiers bytes du fichier
[System.IO.File]::ReadAllBytes("deploy\downloads\stable\metadata-windows.json")[0..2]
# BOM présent si: 239, 187, 191 (0xEF 0xBB 0xBF)
```

**Solution :**
```powershell
# Réécrire sans BOM
$content = Get-Content "metadata-windows.json" -Raw
[System.IO.File]::WriteAllText("metadata-windows.json", $content, [System.Text.UTF8Encoding]::new($false))
```

> Le script `build-agent.ps1` utilise maintenant cette méthode automatiquement.

### Fichiers Windows non trackés par git

**Symptômes :** Après `git pull` sur le VPS, les fichiers Windows n'apparaissent pas.

**Cause :** Le `.gitignore` bloquait `*.exe` et `deploy/downloads/*`.

**Solution :** Le `.gitignore` a été mis à jour avec des exceptions :
```gitignore
# Allow Windows installers in deploy/downloads
!deploy/downloads/*.exe
!deploy/downloads/**/*.exe

# Deploy downloads - allow stable/beta channels
deploy/downloads/*
!deploy/downloads/stable/
!deploy/downloads/beta/
!deploy/downloads/optralis-stub.exe
deploy/downloads/stable/*
!deploy/downloads/stable/*.exe
!deploy/downloads/stable/*.json
```

Pour forcer l'ajout de fichiers existants :
```bash
git add -f deploy/downloads/stable/metadata-windows.json
git add -f deploy/downloads/optralis-stub.exe
```

---

## Troubleshooting Infrastructure

### Erreur "invalid request body" avec Cloudflare

Quand l'agent envoie des données compressées gzip à travers Cloudflare, celui-ci peut décompresser automatiquement tout en conservant le header `Content-Encoding: gzip`.

**Symptômes :**
- Logs agent : `invalid request body` ou `invalid gzip data`

**Solution implémentée** (`middleware/middleware.go`) :
1. Vérifier les magic bytes gzip (0x1f 0x8b) avant de décompresser
2. Si absent → Cloudflare a déjà décompressé
3. Appeler `c.Request().SetBody()` pour forcer Fiber à utiliser le bon buffer
4. Supprimer le header `Content-Encoding` et mettre à jour `Content-Length`

```go
// Check for gzip magic bytes (0x1f 0x8b)
if len(compressedBody) < 2 || compressedBody[0] != 0x1f || compressedBody[1] != 0x8b {
    c.Request().SetBody(compressedBody)
    c.Request().Header.Del("Content-Encoding")
    c.Request().Header.SetContentLength(len(compressedBody))
    return c.Next()
}
```

---

## Tests Complets mTLS

### Architecture des 2 domaines

```
┌─────────────────────────────────────────────────────────────────┐
│                         OPTRALIS                                 │
├──────────────────────────┬──────────────────────────────────────┤
│   Agent API (mTLS)       │   Dashboard API (JWT)                │
│   optralis-agent-api     │   optralis-api                       │
│   .2lacs-it.com          │   .2lacs-it.com                      │
├──────────────────────────┼──────────────────────────────────────┤
│   Auth: Client Cert      │   Auth: Bearer Token                 │
│   Port: 443              │   Port: 443                          │
│   Users: Agents          │   Users: Dashboard                   │
├──────────────────────────┼──────────────────────────────────────┤
│   Endpoints:             │   Endpoints:                         │
│   - POST /heartbeat      │   - POST /api/auth/login             │
│   - POST /inventory      │   - GET /api/machines                │
│   - POST /collectors     │   - GET /api/settings                │
│                          │   - POST /api/admin/clients          │
└──────────────────────────┴──────────────────────────────────────┘
```

### Checklist des Tests

#### Test 1: Génération Installeur Windows (EXE)

```
1. Se connecter au dashboard
2. Aller sur Installation
3. Cliquer "Télécharger Windows"
4. Vérifier: fichier .exe téléchargé (~5MB avec stub + payload)
5. Vérifier: nom du fichier contient le client ID
```

#### Test 2: Installation Agent Windows avec mTLS

```
1. Sur une VM Windows de test
2. Exécuter l'EXE téléchargé en tant qu'admin
3. Vérifier: UAC prompt s'affiche
4. Vérifier: GUI WebView2 s'ouvre (pas de console CMD)
5. Vérifier: Installation démarre automatiquement (pas de formulaire de clé)
6. Vérifier: Barre de progression avec 6 étapes
7. Vérifier: service Windows "Optralis Agent" démarré
8. Vérifier: connexion mTLS réussie (logs agent)
9. Vérifier: machine apparaît dans le dashboard
```

#### Test 3: Génération Installeur Linux

```
1. Cliquer "Télécharger Linux x64" ou "ARM64"
2. Vérifier: script shell téléchargé
3. Contenu attendu: certificats mTLS embarqués + commandes d'installation
```

#### Test 4: Installation Agent Linux avec mTLS

```
1. Sur une VM Linux de test
2. chmod +x le script et l'exécuter avec sudo
3. Vérifier: certificats copiés dans /etc/optralis/
4. Vérifier: binaire agent installé
5. Vérifier: service systemd actif
6. Vérifier: machine apparaît dans le dashboard
```

#### Test 5: Communication Agent ↔ API

```
Endpoint: https://optralis-agent-api.2lacs-it.com
1. Vérifier: heartbeat envoyé toutes les X secondes
2. Vérifier: inventaire remonté correctement
3. Vérifier: métriques système visibles dans dashboard
4. Vérifier: certificat expiré = rejet connexion (test négatif)
```

#### Test 6: Dashboard API (séparé de l'agent API)

```
Endpoint: https://optralis-api.2lacs-it.com
1. Login utilisateur → JWT généré
2. Liste des machines → fonctionne avec JWT
3. Création client (admin) → retourne seulement admin_password
```

#### Test 7: Page Documentation (/documentation)

```
1. Aller sur /dashboard/documentation
2. Vérifier: bannière mTLS avec badge "NEW" et bordure colorée
3. Vérifier: titre "Installation automatique avec mTLS"
4. Vérifier: description mentionne WebView2 et détection automatique
5. Vérifier: Option 1 Windows affiche "(WebView2)" dans le titre
6. Vérifier: note sous le bouton EXE explique Quick Install vs mTLS
7. Vérifier: lien "Aller à la page Installation" fonctionne
```

#### Test 7b: Page Installation (/installation)

```
1. Aller sur /dashboard/installation
2. Vérifier: section "Installeur personnalisé" avec descriptions mises à jour
3. Vérifier: Windows affiche badge "NEW" et description "WebView2 GUI"
4. Vérifier: bouton "Télécharger Windows" génère un EXE personnalisé
5. Vérifier: section "Installation rapide Linux" avec génération de token
6. Vérifier: commande curl affichée avec token temporaire
```

#### Test 8: Création Client Admin

```
1. En tant qu'admin, créer un nouveau client
2. Vérifier: modal affiche seulement le mot de passe admin
3. Vérifier: PAS d'affichage de clé agent
```

### Commandes de diagnostic

```bash
# Vérifier les certificats CA sur le serveur
ls -la /etc/optralis/ca/

# Vérifier que le container API peut lire la CA
docker exec optralis-api ls -la /etc/optralis/ca/

# Vérifier les logs agent (Windows)
Get-Content "C:\ProgramData\optralis-agent\logs\agent.log" -Tail 50

# Vérifier les logs agent (Linux)
sudo journalctl -u optralis-agent -f

# Tester la connexion mTLS manuellement
curl -v --cert client.crt --key client.key https://optralis-agent-api.2lacs-it.com/health
```

---

## Optimisations Performance

### Git LFS pour les binaires

Les fichiers `.exe` dans `deploy/downloads/` sont stockés avec **Git LFS** (Large File Storage) pour optimiser les push/pull.

**Configuration** (`.gitattributes`) :
```gitattributes
deploy/downloads/*.exe filter=lfs diff=lfs merge=lfs -text
deploy/downloads/**/*.exe filter=lfs diff=lfs merge=lfs -text
```

**Prérequis :**
- Windows (build) : `winget install GitHub.GitLFS` puis `git lfs install`
- VPS (deploy) : `sudo apt install git-lfs` puis `git lfs install`

**Impact :** Push/pull 50-70% plus rapide (les binaires sont transférés en parallèle).

**Workflow inchangé :** `git add`, `git commit`, `git push` fonctionnent comme avant. LFS gère automatiquement les fichiers .exe.

### Optimisation Docker Build

Le fichier `.dockerignore` exclut les dossiers non nécessaires pour réduire le contexte de build :

```dockerignore
docs/
build/
agent/
installer/
uninstaller/
scripts/
*.pdf
```

**Impact :** Build Docker 30-40% plus rapide (~175 MB de contexte en moins).

---

## Liens

- [Index des spécifications](README.md)
- [Agent](AGENT_SPECS.md)
- [Base de données](DATABASE_SPECS.md)
