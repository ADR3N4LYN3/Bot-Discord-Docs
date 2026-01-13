# Migration : 1 Certificat par Machine

> **Statut** : ✅ Implémenté
> **Date** : 2026-01-03
> **Commits** : `4cb0375`, `051c388`

## Objectif

Migrer l'architecture certificats de "1 certificat par client" vers "1 certificat par machine".
Chaque machine possède son propre certificat mTLS unique, permettant une révocation granulaire.

**Migration forcée** : Tous les anciens certificats sont supprimés, les agents doivent être réinstallés.

---

## Architecture

### Avant
```
Client → 1 Certificat (CN=client_id) → N Machines
Révocation = Toutes les machines du client bloquées
```

### Après
```
Client → N Certificats → N Machines (1:1)
CN = client_id:machine_id
Révocation = 1 seule machine bloquée
```

---

## Fichiers modifiés

### Backend

| Fichier | Modification |
|---------|--------------|
| `backend/internal/services/installer/cert.go` | `GenerateMachineCertificate(clientID, machineID)` avec CN=client_id:machine_id |
| `backend/internal/services/installer/cert_db.go` | Colonne machine_id, `StoreMachineCertificateMetadata()`, `RestoreCertificate()` |
| `backend/internal/handlers/bootstrap.go` | Request avec hostname/hardware_id, créer machine au bootstrap |
| `backend/internal/middleware/middleware.go` | Parser `CN=client_id:machine_id`, extraire les deux IDs |
| `backend/internal/middleware/revocation.go` | Vérifier révocation par machine_id |
| `backend/internal/handlers/certificate_renewal.go` | Renouveler par machine |
| `backend/internal/handlers/certificates.go` | Endpoints admin : stats, list, restore, purge |
| `backend/cmd/api/main.go` | Routes certificates admin |

### Installer (Windows)

| Fichier | Modification |
|---------|--------------|
| `installer/stub/main.go` | Support bootstrap API avec token |
| `backend/internal/handlers/downloads.go` | Créer token pour Windows au lieu de certificat |
| `backend/internal/services/installer/windows.go` | `GenerateWindowsSelfExtractorWithToken()` |
| `backend/internal/services/installer/tokens.go` | `GetLatestActiveToken()` |

### Database

```sql
-- Migration: 1 cert per machine
-- 1. Supprimer tous les anciens certificats
DELETE FROM client_certificates;

-- 2. Ajouter colonne machine_id
ALTER TABLE client_certificates ADD COLUMN machine_id UUID REFERENCES machines(id);

-- 3. Index pour performance
CREATE INDEX idx_client_certificates_machine_id ON client_certificates(machine_id);

-- 4. Contrainte: 1 certificat actif par machine
CREATE UNIQUE INDEX idx_client_certificates_active_machine
ON client_certificates(machine_id)
WHERE revoked_at IS NULL AND expires_at > NOW();
```

---

## Flow d'installation

### Linux (curl)

```bash
curl -fsSL https://optralis.2lacs-it.com/install.sh | sudo bash -s -- TOKEN
```

1. Script shell télécharge le token
2. Appelle `POST /api/public/bootstrap` avec token + hostname + hardware_id
3. Backend valide le token, crée/trouve la machine
4. Backend génère certificat CN=client_id:machine_id
5. Retourne certificat + clé privée + CA cert + URL binaire
6. Script installe l'agent avec le certificat

### Windows (EXE)

```
Téléchargement EXE depuis dashboard → Exécution → Installation automatique
```

1. Admin télécharge l'installeur depuis le dashboard
2. Backend crée un token d'installation (24h, usage unique)
3. Backend génère EXE = stub + token (pas de certificat)
4. User exécute l'EXE sur la machine cible
5. Stub lit le token, appelle `POST /api/public/bootstrap`
6. Backend génère certificat spécifique à cette machine
7. Stub installe l'agent avec le certificat reçu

---

## Format du CN (Common Name)

```
CN = {client_id}:{machine_id}
Exemple: CN = 550e8400-e29b-41d4-a716-446655440000:6ba7b810-9dad-11d1-80b4-00c04fd430c8
```

Le middleware parse ce CN pour extraire :
- `clientID` → Identifie le client/organisation
- `machineID` → Identifie la machine spécifique

---

## API Bootstrap

### Endpoint
```
POST /api/public/bootstrap
```

### Request
```json
{
  "token": "base64_encoded_install_token",
  "hostname": "DESKTOP-ABC123",
  "hardware_id": "4C4C4544-0044-4810-8031-B3C04F4A5331",
  "arch": "amd64"
}
```

### Response
```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "machine_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "certificate": "-----BEGIN CERTIFICATE-----...",
  "private_key": "-----BEGIN PRIVATE KEY-----...",
  "ca_cert": "-----BEGIN CERTIFICATE-----...",
  "api_url": "https://optralis-agent-api.2lacs-it.com",
  "binary_url": "https://optralis.2lacs-it.com/downloads/stable/optralis-agent-windows-amd64.exe",
  "expires_at": "2027-01-03T00:00:00Z"
}
```

---

## Avantages

| Avant | Après |
|-------|-------|
| Révocation = toutes les machines du client | Révocation = 1 machine uniquement |
| Pas de traçabilité par machine | Certificat lié à une machine spécifique |
| Réinstallation = même certificat | Réinstallation = nouveau certificat |
| Impossible de savoir quelle machine utilise le cert | Dashboard affiche machine ↔ certificat |

---

## Sécurité

| Mesure | Description |
|--------|-------------|
| Token unique | Chaque téléchargement Windows génère un token usage unique |
| Token éphémère | Validité 24h maximum |
| Certificat par machine | Révocation granulaire possible |
| Hardware ID | Identification unique de la machine physique |
| Bootstrap sécurisé | Le token est validé avant génération du certificat |

---

## Commandes utiles

```bash
# Vérifier le CN d'un certificat
openssl x509 -in client.crt -text -noout | grep "Subject:"

# Parser le CN
CN="550e8400-e29b-41d4-a716-446655440000:6ba7b810-9dad-11d1-80b4-00c04fd430c8"
CLIENT_ID=$(echo $CN | cut -d: -f1)
MACHINE_ID=$(echo $CN | cut -d: -f2)

# Vérifier les certificats d'un client (SQL)
SELECT c.serial, c.machine_id, m.hostname, c.expires_at, c.revoked_at
FROM client_certificates c
JOIN machines m ON c.machine_id = m.id
WHERE c.client_id = 'YOUR_CLIENT_ID';
```
