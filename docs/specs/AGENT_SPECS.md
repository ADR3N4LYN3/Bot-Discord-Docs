# Agent Optralis - Spécifications Techniques

## Vue d'ensemble

L'agent Optralis est un service léger écrit en Go qui collecte les métriques système et les envoie au backend API.

### Fonctionnalités

- Collecte CPU, RAM, disques, uptime
- Collecte température CPU (LibreHardwareMonitor sur Windows, /sys/thermal sur Linux)
- Collecte métriques IO disques (lecture/écriture bytes/sec, IOPS)
- Collecte événements Windows (Event Viewer) et Linux (journalctl/syslog)
- Détection S.M.A.R.T détaillée des disques (via smartctl embarqué)
- Buffer local en cas de panne réseau
- Intervalle de collecte (10s par défaut, configurable)
- Installation comme service Windows/Linux
- Configuration via fichier JSON ou mTLS
- Logging structuré avec niveaux (DEBUG/INFO/WARN/ERROR) et rotation automatique
- Intégration Windows Event Viewer avec filtrage intelligent
- **Authentification mTLS** (certificat client unique par machine)
- **HTTP/2** avec multiplexing et connexions persistantes
- **Compression zstd** (fallback gzip) pour payloads > 10KB
- **Graceful degradation** avec timeouts et tracking des échecs

---

## APIs Windows Natives

L'agent Windows utilise exclusivement des APIs Windows natives en Go, **sans aucun appel PowerShell**. Cette architecture évite les blocages par les antivirus (Bitdefender, Windows Defender, etc.) qui détectent l'exécution de scripts PowerShell comme suspecte (MITRE ATT&CK T1059.001).

### Packages Go utilisés

| Package | Usage |
|---------|-------|
| `golang.org/x/sys/windows/registry` | Lecture registre (logiciels installés) |
| `golang.org/x/sys/windows/svc/mgr` | Service Control Manager (services Windows) |
| `github.com/shirou/gopsutil/v3` | Métriques système, réseau, processus |
| `github.com/go-ole/go-ole` | COM/OLE pour WMI (sécurité, mises à jour, température) |

### APIs Windows par collecteur

| Collecteur | API Native | Description |
|------------|------------|-------------|
| `software.go` | Registry API | Énumère `HKLM\SOFTWARE\...\Uninstall` |
| `services.go` | SCM API (`OpenSCManager`, `EnumServicesStatusEx`) | Liste services et statuts |
| `network.go` | IP Helper API (via gopsutil) | Ports en écoute, interfaces réseau |
| `users.go` | NetAPI32 (`NetUserEnum`, `NetLocalGroupGetMembers`) | Utilisateurs locaux et admins |
| `processes.go` | Tool Help Library (via gopsutil) | Statistiques processus |
| `events.go` | Windows Event Log API (`EvtQuery`, `EvtNext`) | Événements système |
| `security.go` | WMI via go-ole + Registry | Antivirus, firewall, UAC, Secure Boot |
| `updates.go` | COM via go-ole (`Microsoft.Update.*`) | Mises à jour Windows |
| `temperature.go` | WMI via go-ole + LHM wrapper | Température CPU |

### Avantages

| Avantage | Description |
|----------|-------------|
| **Compatible AV/EDR** | Aucune exécution PowerShell détectable |
| **Performance** | APIs natives plus rapides que PowerShell |
| **Fiabilité** | Pas de dépendance à l'interpréteur PowerShell |
| **Permissions** | Fonctionne avec les permissions service standard |

---

## Architecture 8 Collectors (v2.0)

L'agent utilise maintenant une architecture modulaire avec **8 collectors indépendants**, chacun avec son propre intervalle de collecte configurable.

### Vue d'ensemble

| Collector | Code | Intervalle défaut | Min | Max |
|-----------|------|-------------------|-----|-----|
| Métriques système | `metrics` | 10s | 5s | 60s |
| Stockage | `storage` | 5min | 1min | 30min |
| Santé disques | `storage_health` | 2h | 30min | 24h |
| Réseau | `network` | 30s | 10s | 5min |
| Services | `services` | 2min | 30s | 30min |
| Sécurité | `security` | 15min | 5min | 2h |
| Logiciels | `software` | 4h | 30min | 24h |
| Mises à jour | `patches` | 6h | 1h | 24h |

### Fichiers de l'architecture

| Fichier | Description |
|---------|-------------|
| `collector/collector.go` | Interface Collector et types |
| `collector/registry.go` | Registry global des collectors |
| `collector/collectors/metrics_collector.go` | Collector métriques système |
| `collector/collectors/storage_collector.go` | Collector stockage |
| `collector/collectors/storage_health_collector.go` | Collector S.M.A.R.T. |
| `collector/collectors/network_collector.go` | Collector réseau |
| `collector/collectors/services_collector.go` | Collector services |
| `collector/collectors/security_collector.go` | Collector sécurité |
| `collector/collectors/software_collector.go` | Collector logiciels |
| `collector/collectors/patches_collector.go` | Collector mises à jour |
| `collector/collectors/register.go` | RegisterAll() |
| `scheduler/scheduler.go` | Multi-ticker scheduler |

### Interface Collector

```go
type Collector interface {
    Type() CollectorType
    Collect() (interface{}, error)
    DefaultInterval() time.Duration
    MinInterval() time.Duration
    MaxInterval() time.Duration
}
```

### Endpoint unifié

```
POST /agent/collect
{
    "hostname": "machine-01",
    "collector": "metrics",
    "collected_at": "2026-01-01T00:00:00Z",
    "data": { ... }
}
```

> **Note** : L'authentification se fait via mTLS. Le client_id et machine_id sont extraits du certificat (CN=client_id:machine_id).

### Configuration dynamique

L'agent récupère sa configuration depuis le serveur :

```
GET /agent/config/collectors?hostname=machine-01

Response:
{
    "collectors": [
        {"type": "metrics", "enabled": true, "interval": 10},
        {"type": "storage", "enabled": true, "interval": 300},
        ...
    ]
}
```

### Synchronisation périodique de la configuration

L'agent synchronise automatiquement sa configuration avec le serveur pour recevoir les changements d'intervalles configurés depuis le dashboard.

| Comportement | Description |
|--------------|-------------|
| **Au démarrage** | Récupère les configs via `GET /agent/config/collectors` |
| **Toutes les 5 minutes** | Vérifie les changements et met à jour le scheduler |
| **Si changement détecté** | Log `[Config] Applied N configuration changes` |
| **Délai de propagation** | Max 5 minutes entre modification dashboard et application agent |

**Flux de synchronisation :**

```
1. Dashboard: Admin modifie intervalle (ex: metrics 10s → 30s)
2. Backend: Sauvegarde dans collection_settings
3. Agent: (toutes les 5 min) GET /agent/config/collectors
4. Backend: Résout intervalles (machine > label > group > global > default)
5. Agent: scheduler.UpdateConfig() met à jour les tickers
6. Agent: Les collectors utilisent les nouveaux intervalles
```

**Résolution des intervalles (priorité) :**

| Niveau | Priorité | Description |
|--------|----------|-------------|
| Machine | 100 | Configuration spécifique à une machine |
| Label | 50 | Sélecteur par labels (ex: `env: production`) |
| Group | 20 | Configuration par groupe de machines |
| Global | 10 | Configuration globale du client |
| Default | 0 | Valeurs par défaut hardcodées |

---

## Métriques Collectées

### Métriques Système (metrics.go)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `cpu_percent` | Usage CPU global (%) | gopsutil `cpu.Percent()` |
| `ram_percent` | Usage RAM (%) | gopsutil `mem.VirtualMemory()` |
| `ram_used_mb` | RAM utilisée (MB) | gopsutil `mem.VirtualMemory()` |
| `ram_total_mb` | RAM totale (MB) | gopsutil `mem.VirtualMemory()` |
| `uptime` | Temps depuis démarrage (secondes) | gopsutil `host.Info()` |
| `cpu_temperature` | Température CPU (°C) | LHM wrapper ou WMI ThermalZone |
| `io_wait_percent` | Temps CPU en attente I/O (%) | gopsutil `cpu.Times()` |

### Informations Système

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `hostname` | Nom de la machine | gopsutil `host.Info()` |
| `os` | Système d'exploitation | gopsutil `host.Info()` |
| `os_version` | Version de l'OS | gopsutil `host.Info()` |
| `ip` | Adresse IP principale | UDP dial vers 8.8.8.8 |
| `cpu_model` | Modèle du processeur | gopsutil `cpu.Info()` |
| `cpu_cores` | Nombre de cœurs physiques | gopsutil `cpu.Info()` |
| `cpu_threads` | Nombre de threads logiques | gopsutil `cpu.Counts(true)` |
| `cpu_freq_mhz` | Fréquence CPU (MHz) | gopsutil `cpu.Info()` |
| `ram_type` | Type de RAM (DDR4, DDR5...) | WMIC (Win) / dmidecode (Linux) |
| `ram_speed_mhz` | Vitesse RAM (MHz) | WMIC (Win) / dmidecode (Linux) |
| `ram_total_gb` | RAM totale (GB) | gopsutil `mem.VirtualMemory()` |

### Disques

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `mount_point` | Point de montage (C:\, /home) | gopsutil `disk.Partitions()` |
| `device` | Périphérique (/dev/sda, C:) | gopsutil `disk.Partitions()` |
| `fs_type` | Type système fichiers (NTFS, ext4, etc.) | gopsutil `disk.Partitions()` |
| `total_gb` | Capacité totale (GB) | gopsutil `disk.Usage()` |
| `used_gb` | Espace utilisé (GB) | gopsutil `disk.Usage()` |
| `used_percent` | Utilisation (%) | gopsutil `disk.Usage()` |
| `smart_status` | État S.M.A.R.T (healthy/warning/critical) | smartctl embarqué |
| `temperature` | Température disque (°C) | smartctl |
| `model` | Modèle du disque | WMIC (Win) / /sys/block (Linux) |
| `interface` | Interface (SATA, NVMe) | WMIC (Win) / smartctl (Linux) |
| `volume_label` | Label du volume | WMIC (Win) / lsblk (Linux) |

### IO Disques (Nouveau)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `disk_read_bytes_per_sec` | Débit lecture (bytes/sec) | gopsutil `disk.IOCounters()` |
| `disk_write_bytes_per_sec` | Débit écriture (bytes/sec) | gopsutil `disk.IOCounters()` |
| `disk_read_iops` | IOPS lecture | gopsutil `disk.IOCounters()` |
| `disk_write_iops` | IOPS écriture | gopsutil `disk.IOCounters()` |

### S.M.A.R.T Détaillé (smart.go)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `device` | Identifiant du disque | smartctl -a -j |
| `model` | Modèle du disque (Samsung SSD 980 PRO, etc.) | smartctl JSON `model_name` |
| `serial` | Numéro de série | smartctl JSON `serial_number` |
| `firmware` | Version firmware | smartctl JSON `firmware_version` |
| `smart_status` | État SMART (healthy/warning/critical/virtual/unavailable) | smartctl JSON |
| `is_virtual` | true si disque virtuel (VM) | Détection vendor/product |
| `overall_health_test` | Test santé global | smartctl -a -j |
| `temperature` | Température disque (°C) | smartctl JSON |
| `power_on_hours` | Heures de fonctionnement | smartctl JSON |
| `power_cycle_count` | Nombre de cycles d'alimentation | smartctl JSON |
| `reallocated_sectors` | Secteurs réalloués (ID 5) - **CRITIQUE** | smartctl JSON |
| `current_pending_sectors` | Secteurs en attente (ID 197) - **CRITIQUE** | smartctl JSON |
| `offline_uncorrectable` | Secteurs non corrigibles (ID 198) - **CRITIQUE** | smartctl JSON |
| `predicted_failure` | Prédiction de panne | Analyse des attributs S.M.A.R.T |

**Détection VM pour SMART :**

L'agent détecte automatiquement les disques virtuels et retourne `is_virtual: true` avec `smart_status: "virtual"` :

| Hyperviseur | Indicateurs détectés |
|-------------|---------------------|
| **QEMU/KVM** | `scsi_vendor: "QEMU"`, `model_name: "*virtual*"` |
| **VMware** | `scsi_vendor: "VMware"` |
| **VirtualBox** | `scsi_vendor: "VBOX"` |
| **Hyper-V** | `scsi_vendor: "MSFT"` |
| **Xen** | `scsi_vendor: "Xen"` |
| **VirtIO** | `scsi_vendor: "virtio"` |

**Note :** Les disques virtuels n'ont pas de données SMART réelles. Les champs `temperature`, `power_on_hours`, etc. seront à 0 pour les VMs.

### Sécurité (security_windows.go)

Le Security Collector (intervalle 15min) collecte les données de sécurité suivantes :

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `antivirus_installed` | Antivirus présent | WMI SecurityCenter2 via go-ole |
| `antivirus_name` | Nom de l'antivirus | WMI `AntivirusProduct.displayName` |
| `antivirus_enabled` | Protection temps réel active | WMI `productState` bit 12 (0x1000) |
| `antivirus_up_to_date` | Définitions à jour | WMI `productState` bit 4 (0x0010) |
| `firewall_enabled` | Firewall actif (global) | COM `HNetCfg.FwPolicy2` |
| `firewall_domain` | Profil Domain actif | COM `FirewallEnabled(1)` |
| `firewall_private` | Profil Private actif | COM `FirewallEnabled(2)` |
| `firewall_public` | Profil Public actif | COM `FirewallEnabled(4)` |
| `bitlocker_enabled` | BitLocker activé sur au moins un volume | WMI `Win32_EncryptableVolume.ProtectionStatus` |
| `secure_boot_enabled` | Secure Boot activé | Registry `SYSTEM\...\SecureBoot\State` |
| `uac_enabled` | UAC activé | Registry `SOFTWARE\...\Policies\System` |
| `failed_logins` | Tentatives de connexion échouées (24h) | Event Log API (Event ID 4625) |
| `events` | Logs Windows System/Application | Event Log API (voir section Événements Système) |
| `listening_ports[]` | Ports en écoute | `netstat`/`ss` via gopsutil |
| `risky_ports[]` | Ports à risque détectés | Filtrage sur `listening_ports` |

**Structure `listening_ports[]` :**

| Champ | Description |
|-------|-------------|
| `protocol` | Protocole (tcp, udp) |
| `local_port` | Numéro de port |
| `process_name` | Nom du processus écoutant |
| `pid` | Process ID |
| `is_risky` | Port dans la liste des ports à risque |
| `risky_meta` | Métadonnées enrichies (si port à risque) |

**Structure RiskyPortMeta :**

| Champ | Description | Valeurs |
|-------|-------------|---------|
| `category` | Catégorie de risque | `ransomware`, `remote_access`, `database`, `legacy`, `c2`, `web` |
| `risk_level` | Niveau de risque | `critical`, `high`, `medium` |
| `service_name` | Nom lisible du service | ex: RDP, SMB, SSH |
| `expected_state` | État attendu | `open`, `closed`, `context` |
| `desc_key` | Clé i18n description | `port.{name}.desc` |
| `reason_key` | Clé i18n raison | `port.{name}.reason` |

**Ports à risque surveillés : 42 ports (ransomware, remote_access, database, legacy, c2, web)**

**Logs Windows System/Application :**
- Collectés via le Security Collector (toutes les 15 minutes)
- Maximum 100 événements (50 System + 50 Application)
- Filtres : Critical (Level 1), Error (Level 2), Warning (Level 3)
- Période : 30 derniers jours
- Stockage : Table `event_logs` (TimescaleDB hypertable)
- Rétention selon licence (7j Trial, 30j Starter, 90j Pro, custom Enterprise)

**Détection BitLocker :**
- Namespace WMI : `root\cimv2\Security\MicrosoftVolumeEncryption`
- Classe : `Win32_EncryptableVolume`
- `ProtectionStatus = 1` → Protection active (BitLocker ON)
- Nécessite Windows Pro/Enterprise (pas disponible sur Home)

### Services (services_windows.go)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `name` | Nom du service | SCM `mgr.ListServices()` |
| `display_name` | Nom affiché | SCM `s.Config().DisplayName` |
| `status` | État (running/stopped/paused) | SCM `s.Query().State` |
| `start_type` | Type démarrage (auto/manual/disabled) | SCM `s.Config().StartType` |
| `account` | Compte de service | SCM `s.Config().ServiceStartName` |
| `is_critical` | Service critique | Map `criticalWindowsServices` / `criticalLinuxServices` |
| `critical_meta` | Métadonnées enrichies | Structure `CriticalServiceMeta` |

**Structure CriticalServiceMeta :**

| Champ | Description | Valeurs |
|-------|-------------|---------|
| `category` | Catégorie de sécurité | `security_core`, `network_vector`, `system_core`, `server_role` |
| `risk_level` | Niveau de risque | `critical`, `high`, `medium` |
| `expected_state` | État attendu | `running`, `stopped`, `context` |
| `desc_key` | Clé i18n description | `service.{name}.desc` |
| `reason_key` | Clé i18n raison | `service.{name}.reason` |

**Services critiques surveillés : 35 Windows, 16 Linux (52 total)**

**Services Windows par catégorie :**

| Catégorie | Services | Niveau |
|-----------|----------|--------|
| **security_core** | EventLog, WinDefend, mpssvc, wscsvc, CryptSvc, VSS, SamSs, Spooler, wbengine | critical/high |
| **network_vector** | TermService, LanmanServer, LanmanWorkstation, RpcSs, Winmgmt, WinRM, RemoteRegistry, WebClient, SSDPSRV, upnphost, SessionEnv | critical/high |
| **system_core** | wuauserv, BITS, Schedule, Dnscache, Dhcp, vds | high/medium |
| **server_role** | NTDS, DNS, Kdc, Dfs, DFSR, IsmServ, Netlogon, W32Time, CertSvc, ADWS | critical/high/medium |

**Services Linux par catégorie :**

| Catégorie | Services | Niveau |
|-----------|----------|--------|
| **security_core** | systemd-journald, rsyslog, firewalld, ufw, auditd, fail2ban, apparmor, selinux, polkit | critical/high |
| **network_vector** | sshd | high |
| **system_core** | systemd-logind, cron, NetworkManager, systemd-timesyncd, chronyd, ntpd | high/medium |

**Sources de sécurité :** MITRE ATT&CK (T1003, T1068, T1490, T1021, T1562), Microsoft Security Baseline, CVE-2021-34527 (PrintNightmare), CVE-2021-4034 (PwnKit)

### Événements Système (events_windows.go)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `source` | Source de l'événement | Event Log API `EvtRender` (XML Provider/@Name) |
| `level` | Niveau (critical/error/warning/info) | Event Log API Level (1=critical, 2=error, 3=warning) |
| `message` | Message de l'événement | Event Log API EventData/Message |
| `occurred_at` | Date de l'événement | Event Log API SystemTime (ISO 8601 UTC) |

**Journaux consultés :** System, Application
**Filtre :** Erreurs et avertissements des 30 derniers jours via XPath

**Parsing des timestamps Windows :**
- Windows Event Log XML utilise des **guillemets simples** (`SystemTime='...'`) pour les attributs
- Format ISO 8601 avec précision variable (1-7 chiffres décimaux)
- La fonction `parseWindowsTimestamp()` gère automatiquement les différentes précisions

### Réseau (network_collector.go)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `bytes_recv_mbps` | Débit descendant (Mbps) | gopsutil `net.IOCounters()` |
| `bytes_sent_mbps` | Débit montant (Mbps) | gopsutil `net.IOCounters()` |
| `packet_loss_in` | Perte paquets entrants (%) | gopsutil `net.IOCounters()` |
| `packet_loss_out` | Perte paquets sortants (%) | gopsutil `net.IOCounters()` |
| `gateway_latency_ms` | Latence vers passerelle (ms) | Ping ICMP |
| `interface_name` | Interface principale | gopsutil `net.Interfaces()` |
| `interfaces[]` | Liste interfaces réseau | gopsutil `net.Interfaces()` |

**Structure `interfaces[]` :**

| Champ | Description |
|-------|-------------|
| `name` | Nom de l'interface (eth0, Ethernet) |
| `mac` | Adresse MAC |
| `ips[]` | Adresses IP assignées |
| `is_up` | Interface active |
| `speed` | Vitesse en Mbps |

### Mises à jour Windows (patches_collector.go)

| Métrique | Description | API/Méthode |
|----------|-------------|-------------|
| `pending_updates[]` | Liste des mises à jour en attente | COM `Microsoft.Update.Session` |
| `pending_count` | Nombre total de mises à jour | Comptage |
| `security_count` | Mises à jour de sécurité | Filtrage par catégorie |
| `last_check_time` | Dernière vérification WU | COM `IAutomaticUpdates` |
| `reboot_required` | Redémarrage requis | COM `ISystemInformation` |
| `auto_update_enabled` | Mises à jour auto activées | COM `IAutomaticUpdates.EnableService` |

**Structure `pending_updates[]` :**

| Champ | Description |
|-------|-------------|
| `title` | Nom de la mise à jour |
| `kb` | Numéro KB (ex: KB5028997) |
| `category` | Security, Critical, Definition, Other |
| `size` | Taille (ex: "45.2 MB") |
| `is_important` | Mise à jour importante |

---

## Payload Heartbeat

> **Note**: L'authentification se fait via mTLS (certificat client), pas de clé dans le payload.

```go
type HeartbeatPayload struct {
    // NOTE: AgentKey removed - authentication via mTLS certificates
    AgentVersion string
    Hostname     string
    HardwareID   string       // Identifiant matériel persistant
    OS           string       // "windows" ou "linux"
    OSVersion    string
    Architecture string       // "amd64" ou "arm64" (pour auto-update)
    IP           string
    CPUModel     string
    CPUCores     int
    CPUThreads   int
    CPUFreqMHz   float64
    RAMType      string
    RAMSpeedMHz  int
    RAMTotalGB   float64
    Metrics      Metrics      // CPU%, RAM%, Uptime, Temperature
    Disks        []DiskInfo
    SmartData    []SmartData
    Events       []Event
    IOMetrics    IOMetrics    // Nouveau: métriques IO
}
```

---

## LibreHardwareMonitor Wrapper (Windows)

Wrapper C# utilisant LibreHardwareMonitor pour lire la vraie température CPU via les registres MSR Intel/AMD.

- **Fichiers:** `agent/tools/lhm-wrapper/`
- **Build:** `dotnet publish -c Release -r win-x64 --self-contained`
- **Taille:** ~15 MB (self-contained)

---

## Smartctl Embarqué

Sur Windows, `smartctl.exe` est embarqué dans le binaire via `go:embed` et extrait vers `C:\ProgramData\optralis-agent\bin\` au premier lancement.

---

## Authentification mTLS

L'agent utilise l'authentification par certificat client (mTLS), avec un certificat **unique par machine** permettant une révocation granulaire.

### Architecture 1 Certificat par Machine

Chaque machine possède son propre certificat unique :

| Élément | Description |
|---------|-------------|
| **Format CN** | `client_id:machine_id` (UUID:UUID) |
| **Validité** | 1 an par défaut |
| **Révocation** | Par machine (les autres machines du client ne sont pas affectées) |

```
Avant (legacy) :
Client → 1 Certificat (CN=client_id) → N Machines
Révocation = Toutes les machines bloquées

Après :
Machine A → Certificat A (CN=client:machine_a)
Machine B → Certificat B (CN=client:machine_b)
Révocation Machine A → Seule Machine A bloquée
```

### Flux d'authentification

```
┌─────────────┐     mTLS      ┌─────────────┐     Header      ┌─────────────┐
│    Agent    │ ───────────── │    Caddy    │ ───────────────│   Backend   │
│ (cert.crt)  │               │  (CA.crt)   │  X-Client-CN   │             │
│ CN=cli:mach │               │             │  cli:mach      │             │
└─────────────┘               └─────────────┘                └─────────────┘
                                                               │
                                                               ▼
                                                        Parse CN →
                                                        client_id + machine_id
```

### Configuration mTLS

**Fichiers certificat :**

| Plateforme | Certificat | Clé privée |
|------------|------------|------------|
| Windows | `C:\ProgramData\optralis-agent\client.crt` | `C:\ProgramData\optralis-agent\client.key` |
| Linux | `/etc/optralis-agent/client.crt` | `/etc/optralis-agent/client.key` |

**Config JSON :**

```json
{
  "api_url": "https://optralis-api.2lacs-it.com",
  "mtls_enabled": true,
  "mtls_cert_path": "/etc/optralis-agent/client.crt",
  "mtls_key_path": "/etc/optralis-agent/client.key"
}
```

### Bootstrap avec hostname/hardware_id

Lors de l'installation via token, l'agent envoie son hostname et hardware_id pour créer ou récupérer sa machine :

```json
{
  "token": "xxx",
  "hostname": "srv-prod-01",
  "hardware_id": "dmi-uuid-or-machine-id",
  "arch": "amd64"
}
```

Le backend crée alors un certificat unique pour cette machine.

> **Note :** Les anciens certificats au format `CN=client_id` ne sont plus supportés.

---

## Renouvellement Automatique des Certificats

**Package:** `agent/internal/certmanager/`

L'agent inclut un gestionnaire de certificats qui renouvelle automatiquement le certificat mTLS avant son expiration. Le renouvellement génère un nouveau certificat unique pour cette machine spécifique (CN=client_id:machine_id).

### Fonctionnement

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| **Intervalle de vérification** | 24 heures | Fréquence de vérification de l'expiration |
| **Seuil de renouvellement** | 30 jours | Renouvellement si expiration < 30 jours |
| **Endpoint** | `POST /agent/certificate/renew` | API backend de renouvellement |
| **Format certificat** | CN=client_id:machine_id | Conserve le même format après renouvellement |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   certmanager.Manager                            │
├─────────────────────────────────────────────────────────────────┤
│  • Ticker 24h → checkAndRenew()                                 │
│  • CheckCertificateExpiry() → Parse X.509, calcule jours        │
│  • renewCertificate() → POST /agent/certificate/renew           │
│  • Sauvegarde atomique (temp → rename)                          │
│  • Recharge HTTP client après renouvellement                    │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de renouvellement

1. **Vérification** : Le manager parse le certificat X.509 et calcule les jours restants
2. **Déclenchement** : Si < 30 jours, appelle `POST /agent/certificate/renew`
3. **Réception** : Le backend retourne le nouveau certificat + clé + CA
4. **Sauvegarde** : Écriture atomique via fichier temporaire + rename
5. **Rechargement** : `sender.ReloadHTTPClient()` recharge le client HTTP

### Code d'intégration

```go
// main.go
import "github.com/2lacs-informatique/optralis/agent/internal/certmanager"

// Démarrage (si mTLS actif)
var certMgr *certmanager.Manager
if sender.IsMTLSActive() {
    certMgr = certmanager.New(sender.GetHTTPClient(), sender.ReloadHTTPClient)
    certMgr.Start()
}

// Arrêt propre
if certMgr != nil {
    certMgr.Stop()
}
```

### Fonctions exportées

| Fonction | Description |
|----------|-------------|
| `CheckCertificateExpiry(certPath)` | Retourne (daysRemaining, needsRenewal, error) |
| `New(httpClient, reloadFunc)` | Crée un nouveau Manager |
| `Manager.Start()` | Démarre la boucle de vérification |
| `Manager.Stop()` | Arrête proprement le manager |

### Gestion des erreurs

| Erreur | Comportement |
|--------|--------------|
| Certificat introuvable | Log warning, skip renouvellement |
| Erreur réseau | Retry au prochain intervalle (24h) |
| Réponse invalide | Log error, garde l'ancien certificat |
| Erreur sauvegarde | Log error, garde l'ancien certificat |

### Logs

```
[CertManager] Certificate expires in 25 days, initiating renewal...
[CertManager] Certificate renewed successfully, expires at 2027-01-02
[CertManager] HTTP client reloaded with new certificate
```

---

## Système de Logging

**Package:** `agent/internal/logger/`

| Fonctionnalité | Description |
|----------------|-------------|
| **Niveaux** | DEBUG, INFO, WARN, ERROR |
| **Rotation** | Automatique via lumberjack (1 MB max, 5 fichiers, 7 jours) |
| **Compression** | Anciens logs compressés en gzip |
| **Format** | `2025/01/15 10:30:45 [INFO ] Message` |
| **Console** | Sortie stderr en mode CLI (non-service) |
| **Event Viewer** | Windows uniquement, événements importants seulement |

**Configuration rotation (lumberjack) :**

```go
lumberjack.Logger{
    Filename:   logPath,
    MaxSize:    1,     // 1 MB par fichier
    MaxBackups: 5,     // Garder 5 anciens fichiers
    MaxAge:     7,     // Supprimer après 7 jours
    Compress:   true,  // Compresser en gzip
}
```

**Chemins des fichiers log:**

| Plateforme | Chemin |
|------------|--------|
| Windows | `C:\ProgramData\optralis-agent\logs\agent.log` |
| Linux | `/var/log/optralis-agent/agent.log` |

---

## Buffering Hors-ligne

**Package:** `agent/internal/sender/`

Quand l'agent ne peut pas joindre le serveur, les heartbeats sont bufferisés localement.

**Chemins des fichiers buffer:**

| Plateforme | Chemin |
|------------|--------|
| Windows | `C:\ProgramData\optralis-agent\buffer.json` |
| Linux | `/var/lib/optralis-agent/buffer.json` |

**Limites:**
- Maximum 100 entrées
- Expiration après 24h

**Gestion des erreurs d'authentification:**

| Type d'erreur | Retry | Buffer | Message log |
|---------------|-------|--------|-------------|
| Réseau | 3x | Oui | "(data buffered)" |
| 5xx serveur | 3x | Oui | "(data buffered)" |
| 401/403 auth | Non | **Non** | "(NOT buffered - check agent key)" |
| Autres 4xx | Non | Non | Message standard |

---

## Hardware ID (Identification Persistante)

Le système identifie les machines par un identifiant matériel persistant (`hardware_id`) au lieu du hostname seul.

**Fichiers:**
- `agent/internal/collector/hardware_id_windows.go`
- `agent/internal/collector/hardware_id_linux.go`

### Sources Hardware ID

| Plateforme | Source Principale | Fallback |
|------------|-------------------|----------|
| **Windows** | Registry `MachineGuid` | BIOS UUID via WMIC |
| **Linux** | `/etc/machine-id` (systemd) | SMBIOS UUID via dmidecode |

### Caractéristiques

| Propriété | Description |
|-----------|-------------|
| **Persistance** | ID généré à l'installation de l'OS, survit aux renames |
| **Unicité** | Unique par machine physique/VM |
| **Rétrocompatibilité** | Colonne nullable, fallback hostname si non fourni |

---

## Détection VM/Physique

Le système détecte automatiquement si une machine est virtuelle ou physique.

**Fichiers:**
- `agent/internal/collector/virtualization_linux.go`
- `agent/internal/collector/virtualization_windows.go`

### Méthodes de Détection (Linux)

| Priorité | Méthode | Description |
|----------|---------|-------------|
| 1 | `gopsutil` | Utilise DMI, /sys/hypervisor |
| 2 | `systemd-detect-virt` | Commande système fiable |
| 3 | `/sys/class/dmi/id/product_name` | Nom produit DMI |
| 4 | `/sys/class/dmi/id/sys_vendor` | Vendeur système |
| 5 | CPU model | Mots-clés dans le nom CPU |
| 6 | Fichiers système | `/sys/hypervisor/`, `/.dockerenv` |

### Hyperviseurs Détectés

| Hyperviseur | Indicateurs |
|-------------|-------------|
| **KVM/QEMU** | "kvm", "qemu", "Standard PC" |
| **VMware** | "vmware" |
| **Hyper-V** | "hyperv", "Microsoft Corporation" |
| **VirtualBox** | "virtualbox", "Oracle Corporation" |
| **Xen** | "xen", "/proc/xen" |
| **Docker** | "docker", "/.dockerenv" |
| **Cloud** | AWS, GCE, Azure, DigitalOcean, OVH, etc. |

---

## Auto-Update

L'agent vérifie les mises à jour au démarrage et périodiquement.

| Condition | Comportement |
|-----------|-------------|
| Version serveur > version agent | Télécharge et installe |
| Version serveur = version agent | Rien |
| Version serveur < version agent | Rien (pas de downgrade) |

### Processus de mise à jour (Windows)

1. Télécharge l'installeur dans `C:\ProgramData\optralis-agent\updates\`
2. Vérifie le checksum SHA256
3. Arrête le service, lance l'installeur en mode silent, redémarre

### Processus de mise à jour (Linux)

1. Télécharge le binaire via HTTPS
2. Vérifie le checksum SHA256
3. Utilise `systemd-run` pour exécuter le script de mise à jour
4. Arrête le service, copie le nouveau binaire, redémarre

**Note :** L'utilisation de `systemd-run` garantit que le processus de mise à jour continue même si le service agent est arrêté.

---

## Transport HTTP

### HTTP/2 avec Multiplexing

L'agent utilise HTTP/2 par défaut pour de meilleures performances :

```go
transport := &http.Transport{
    ForceAttemptHTTP2:   true,
    MaxIdleConns:        100,
    MaxIdleConnsPerHost: 10,
    IdleConnTimeout:     90 * time.Second,
}
http2.ConfigureTransport(transport)
```

**Avantages :**
- Connexion persistante unique
- Multiplexing des requêtes
- Réduction overhead TLS handshake

### Compression zstd

Les payloads > 10KB sont compressés automatiquement :

| Algorithme | Priorité | Condition |
|------------|----------|-----------|
| **zstd** | 1 | Si réduction > 20% |
| **gzip** | 2 | Fallback si zstd < 20% |
| Aucun | 3 | Si aucune réduction > 20% |

```go
// Seuil minimum de 20% de réduction pour activer la compression
if len(compressed) < len(data)*80/100 {
    return compressed, "zstd"
}
```

### Retry avec Exponential Backoff

En cas d'échec réseau, retry avec backoff exponentiel + jitter :

```go
// Délais: 1s, 2s, 4s, 8s, 16s, 32s, 60s (max)
delay := BaseDelay * (1 << attempt)  // Exponential
jitter := random(0, delay/4)          // 0-25% jitter
```

---

## Graceful Degradation

### Timeouts par Collector

Chaque collector a un timeout adapté à sa complexité :

| Collector | Timeout | Raison |
|-----------|---------|--------|
| `metrics` | 5s | Rapide - métriques basiques |
| `storage` | 10s | Modéré - énumération disques |
| `storage_health` | 30s | Lent - requêtes SMART |
| `network` | 10s | Modéré - interfaces réseau |
| `services` | 15s | Modéré - listing services |
| `security` | 20s | Modéré - checks sécurité |
| `software` | 60s | Lent - énumération logiciels |
| `patches` | 120s | Très lent - Windows Update API |

### Tracking des Échecs

Le registry suit les échecs consécutifs par collector :

```go
// Alerte après 3 échecs consécutifs
if failures[collector] == MaxConsecutiveFailures {
    log.Printf("[Alert] Collector %s has failed %d times", collector, failures)
}

// Reset à 0 si succès
if err == nil && failures[collector] > 0 {
    log.Printf("[Collector] %s recovered after %d failures", collector, failures)
}
```

---

## Configuration

### Arguments CLI

| Argument | Description |
|----------|-------------|
| `-url=XXX` | URL de l'API (défaut: https://optralis-api.2lacs-it.com) |
| `-install` | Installer comme service Windows |
| `-uninstall` | Désinstaller le service |
| `-version` | Afficher la version |

> **Note sécurité :** Le flag `-key` a été supprimé (visible dans `ps aux`). Utiliser mTLS ou le fichier config.

### Fichier de configuration

**Windows:** `C:\ProgramData\optralis-agent\config.json`
**Linux:** `/etc/optralis-agent/config.json`

**Configuration mTLS (recommandé) :**

```json
{
  "api_url": "https://optralis-api.2lacs-it.com",
  "mtls_enabled": true,
  "mtls_cert_path": "/etc/optralis-agent/client.crt",
  "mtls_key_path": "/etc/optralis-agent/client.key",
  "log_level": "info"
}
```

> **Note :** Les champs `interval`, `inventory_interval` et `updates_interval` sont obsolètes depuis la v2.0.

---

## Liens

- [Index des spécifications](README.md)
- [Backend API](BACKEND_SPECS.md)
- [Base de données](DATABASE_SPECS.md)
