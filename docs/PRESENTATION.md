---
marp: true
theme: default
paginate: true
backgroundColor: #0a0a1a
color: #ffffff
style: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

  section {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d1b2a 100%);
    position: relative;
  }

  section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
    pointer-events: none;
  }

  h1 {
    color: #00d4ff;
    font-weight: 700;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    font-size: 2.8em;
    margin-bottom: 0.2em;
  }

  h2 {
    color: #a855f7;
    font-weight: 600;
    font-size: 1.4em;
    margin-top: 0;
  }

  strong {
    color: #00d4ff;
    font-weight: 600;
  }

  em {
    color: #a855f7;
    font-style: normal;
    font-weight: 300;
  }

  table {
    font-size: 0.85em;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 30px rgba(0, 212, 255, 0.2);
  }

  th {
    background: linear-gradient(135deg, #00d4ff 0%, #a855f7 100%);
    color: #0a0a1a;
    font-weight: 600;
    padding: 12px 16px;
  }

  td {
    background: rgba(255, 255, 255, 0.05);
    padding: 10px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  tr:hover td {
    background: rgba(0, 212, 255, 0.1);
  }

  code {
    background: rgba(0, 212, 255, 0.15);
    border-radius: 6px;
    padding: 2px 8px;
    color: #00d4ff;
  }

  pre {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
  }

  pre code {
    background: transparent;
    color: #e2e8f0;
  }

  blockquote {
    border-left: 4px solid #a855f7;
    background: linear-gradient(90deg, rgba(168, 85, 247, 0.2) 0%, transparent 100%);
    padding: 16px 24px;
    border-radius: 0 12px 12px 0;
    font-style: italic;
  }

  ul {
    list-style: none;
    padding-left: 0;
  }

  ul li {
    position: relative;
    padding-left: 28px;
    margin-bottom: 12px;
  }

  ul li::before {
    content: '▸';
    position: absolute;
    left: 0;
    color: #00d4ff;
    font-size: 1.2em;
  }

  section.lead h1 {
    font-size: 3.5em;
    text-align: center;
  }

  section.lead h2 {
    text-align: center;
    font-size: 1.6em;
  }

  footer {
    color: rgba(255, 255, 255, 0.4);
    font-size: 0.7em;
  }

  /* Classes personnalisées */
  .highlight {
    background: linear-gradient(90deg, #00d4ff, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
  }

  .card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(10px);
  }

footer: Optralis - 2 LACS INFORMATIQUE
---

<!-- _class: lead -->

# Optralis

## Solution SaaS de Monitoring d'Infrastructure

*Voir plus loin. Agir plus vite.*

![bg right:40% 80%](../dashboard/public/Optralis.png)

---

# Qui sommes-nous ?

## 2 LACS INFORMATIQUE

- Entreprise spécialisée en **solutions IT**
- Basée en **France**
- Expertise en **monitoring** et **infrastructure**

> **Notre mission** : Simplifier la surveillance de votre parc informatique

---

# Le Problème

## Les défis du monitoring traditionnel

- Outils **complexes** et **coûteux**
- Installation **difficile**
- Pas de **vision unifiée**
- **Alertes tardives**
- Données **S.M.A.R.T ignorées**

![bg right:35% 90%](https://img.icons8.com/fluency/512/warning-shield.png)

---

<!-- _class: lead -->

# La Solution

## **Optralis**

*Monitoring simplifié et efficace*

---

# Optralis en un coup d'oeil

| Avantage | Description |
|----------|-------------|
| **Simple** | Installation en **1 commande** |
| **Complet** | CPU, RAM, Disques, S.M.A.R.T, Events |
| **Temps réel** | Données à **intervalles configurables** |
| **Multi-plateforme** | Windows & Linux |
| **SaaS** | Aucune infrastructure à gérer |

---

# Architecture

## Comment fonctionne Optralis ?

```
    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │             │         │             │         │             │
    │   Agent     │ ──────▶ │   API Go    │ ──────▶ │  Dashboard  │
    │  Win/Linux  │  HTTPS  │   Fiber     │         │   Next.js   │
    │             │         │             │         │             │
    └─────────────┘         └──────┬──────┘         └─────────────┘
                                   │
                            ┌──────▼──────┐
                            │  PostgreSQL │
                            │ TimescaleDB │
                            └─────────────┘
```

---

# Monitoring Complet

## Toutes vos métriques en un seul endroit

| Métrique | Ce qu'on surveille |
|----------|-------------|
| **CPU** | Utilisation %, modèle, température |
| **RAM** | Utilisation %, type, vitesse |
| **Disques** | Espace, S.M.A.R.T, **prédiction pannes** |
| **Uptime** | Temps de fonctionnement |
| **Events** | Erreurs Windows/Linux |

---

# S.M.A.R.T

## Prédiction de pannes disques

- Température disque
- Heures d'utilisation
- Secteurs réalloués
- Secteurs en attente
- **Prédiction automatique de panne**

> Anticipez les pannes **avant** qu'elles ne surviennent !

![bg right:30% 80%](https://img.icons8.com/fluency/512/ssd.png)

---

# Score de Santé

## Évaluation automatique de 0 à 100

| Condition | Impact sur le score |
|-----------|--------|
| CPU > 80% | **-10 pts** |
| RAM > 85% | **-15 pts** |
| Disque > 90% | **-20 pts** |
| S.M.A.R.T failure | **-50 pts** |

### Indicateurs visuels
🟢 **Excellent** ≥80 | 🟡 **Attention** 50-79 | 🔴 **Critique** <50

---

# Alertes Intelligentes

## Ne manquez plus rien

- **Alertes email** pour machines hors ligne
- **Délai configurable** (évite les faux positifs)
- **Intervalle dynamique** :
  - `60s` en temps normal
  - `30s` si CPU > 80% ou RAM > 85%

![bg right:35% 90%](https://img.icons8.com/fluency/512/alarm.png)

---

# Organisation

## Gestion simplifiée du parc

- **Groupes de machines** avec codes couleurs
- **Multi-tenant** : isolation totale par client
- **Rôles** : Admin, Viewer
- **Impersonation** : visualiser comme un client

![bg right:35% 90%](https://img.icons8.com/fluency/512/org-unit.png)

---

# Interface Moderne

## Dashboard élégant et responsive

- **Thème sombre/clair**
- **Style Glassmorphism**
- **Bilingue** FR/EN
- **100% Responsive** mobile & tablette
- **Auto-refresh** configurable
- **Auto-logout** sécurisé

![bg right:40% 95%](https://img.icons8.com/fluency/512/dashboard-layout.png)

---

# Installation Windows

## 3 méthodes au choix

**PowerShell (1 ligne) :**
```powershell
irm https://optralis.2lacs-it.com/install.ps1 | iex
```

**Installateur GUI :**
Télécharger depuis le dashboard → Double-clic → Entrer la clé

**Silencieux (déploiement GPO) :**
```powershell
optralis-agent.exe -silent -key "VOTRE_CLE"
```

---

# Installation Linux

## Simple et rapide

```bash
curl -fsSL https://optralis.2lacs-it.com/install.sh \
  | sudo bash -s -- VOTRE_CLE_AGENT
```

### Distributions supportées

- Ubuntu / Debian
- CentOS / RHEL / Rocky
- Fedora
- Arch Linux

---

# Sécurité

## Protection des données

| Mesure | Description |
|--------|-------------|
| **JWT** | Access token 15min / Refresh 7j |
| **Bcrypt** | Hashage mots de passe |
| **SHA256** | Clés agent hashées en base |
| **TLS 1.3** | Communication 100% chiffrée |
| **Expiration** | Mots de passe 90 jours |

---

# Offres & Tarifs

## Des formules adaptées à vos besoins

| Offre | Machines | Rétention données |
|------|----------|-----------|
| **Trial** | 5 | 7 jours |
| **Starter** | 25 | 30 jours |
| **Pro** | 150 | 90 jours |
| **Enterprise** | Illimité | Personnalisée (6-24 mois) |

---

# Panel Admin

## Pour les super administrateurs

- Dashboard avec **stats globales**
- Gestion des **clients**
- Gestion des **licences**
- Monitoring **Docker**
- **Impersonation** clients

![bg right:35% 90%](https://img.icons8.com/fluency/512/admin-settings-male.png)

---

# Stack Technique

## Technologies modernes & performantes

| Composant | Technologies |
|-----------|--------------|
| **Agent** | Go, gopsutil, smartctl |
| **Backend** | Go, Fiber, JWT |
| **Database** | PostgreSQL + TimescaleDB |
| **Frontend** | Next.js 14, TypeScript, Tailwind |
| **Deploy** | Docker, Caddy |

---

<!-- _class: lead -->

# Démo Live

## Découvrez Optralis en action

🌐 **optralis.2lacs-it.com/dashboard**

---

# Pourquoi choisir Optralis ?

## Récapitulatif

- ✅ Installation en **1 minute**
- ✅ Monitoring **complet** (CPU, RAM, Disques, S.M.A.R.T)
- ✅ **Prédiction de pannes** disques
- ✅ **Alertes email** temps réel
- ✅ Interface **moderne** et intuitive
- ✅ **Multi-plateforme** Windows/Linux
- ✅ **SaaS** - Aucune maintenance

---

<!-- _class: lead -->

# Questions ?

📧 **support@2lacs-it.com**
🌐 **2lacs-it.com**
📍 **optralis.2lacs-it.com**

---

<!-- _class: lead -->

# Merci !

## Optralis

*Voir plus loin. Agir plus vite.*

![bg right:40% 80%](../dashboard/public/Optralis.png)

**2 LACS INFORMATIQUE**
