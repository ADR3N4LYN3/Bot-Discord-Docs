# Optralis - Spécifications Techniques

## Vue d'ensemble

Optralis est une solution SaaS complète de monitoring d'infrastructure conçue pour surveiller vos machines Windows et Linux en temps réel. Le projet comprend:

- **Agent** (Go) : collecte métriques système, événements Windows/Linux, S.M.A.R.T
- **Backend API** (Go + Fiber) : reçoit les données, auth JWT, multi-tenant
- **Dashboard** (Next.js 14) : interface web moderne avec Glassmorphism
- **Installer** (Go + WebView2) : installateur Windows GUI/CLI
- **Docker Compose** : déploiement VPS complet

---

## Documentation Modulaire

Les spécifications sont organisées en modules thématiques :

| Module | Description | Fichier |
|--------|-------------|---------|
| **Agent** | Agent Go Windows/Linux, collecte métriques, APIs natives | [AGENT_SPECS.md](AGENT_SPECS.md) |
| **Backend** | API Go, routes, services, notifications, multi-users | [BACKEND_SPECS.md](BACKEND_SPECS.md) |
| **Dashboard** | Frontend Next.js, composants, i18n, UX | [DASHBOARD_SPECS.md](DASHBOARD_SPECS.md) |
| **Database** | PostgreSQL, TimescaleDB, cache Redis, sécurité | [DATABASE_SPECS.md](DATABASE_SPECS.md) |
| **Installer** | Installateurs, scripts build, déploiement | [INSTALLER_SPECS.md](INSTALLER_SPECS.md) |

---

## Stack Technique

| Composant | Technologies |
|-----------|--------------|
| **Agent** | Go 1.25+, gopsutil, smartctl (embarqué), LibreHardwareMonitor |
| **Backend** | Go 1.25+, Fiber, pgx, go-json, PostgreSQL + TimescaleDB + Redis |
| **Dashboard** | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| **Installer** | Go, WebView2, go-winres |
| **Déploiement** | Docker Compose, Caddy (reverse proxy + SSL) |

---

## Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| **Monitoring temps réel** | CPU, RAM, disques, uptime, température CPU, IO disques |
| **S.M.A.R.T Monitoring** | Santé disques, prédiction de pannes, secteurs défectueux |
| **Événements système** | Collecte des erreurs et avertissements Windows/Linux |
| **Score de santé** | Évaluation automatique de l'état des machines |
| **Intervalle dynamique** | Collecte adaptative selon état machine (30s/60s) |
| **Multi-tenant** | Support de plusieurs organisations |
| **Multi-utilisateurs** | Gestion des utilisateurs par client avec rôles Admin/Observer |
| **Groupes de machines** | Organisation par groupes avec codes couleurs |
| **Labels** | Système de tags key=value pour catégoriser les machines |
| **Notifications multi-canal** | Email, Teams, Slack, Discord avec types d'alertes configurables |
| **MFA / 2FA (TOTP)** | Authentification à deux facteurs |
| **AI Service (Beta)** | Analyse automatisée des métriques et anomalies |

---

## Structure du Projet

```
optralis/
├── agent/                    # Agent Go (Windows/Linux)
│   ├── cmd/agent/            # Point d'entrée + service Windows/Linux
│   ├── internal/
│   │   ├── collector/        # Collecte métriques, events, température, S.M.A.R.T
│   │   ├── config/           # Configuration + crypto par OS
│   │   ├── embedded/         # Binaires embarqués (smartctl.exe)
│   │   ├── logger/           # Logging structuré + Windows Event Viewer
│   │   ├── sender/           # Envoi vers l'API
│   │   └── updater/          # Auto-update de l'agent
│   ├── tools/
│   │   └── lhm-wrapper/      # Wrapper C# LibreHardwareMonitor
│   └── winres/               # Ressources Windows (icône, manifest)
│
├── backend/                  # API Go
│   ├── cmd/api/              # Point d'entrée
│   └── internal/
│       ├── cache/            # Cache Redis avec dégradation gracieuse
│       ├── database/         # PostgreSQL + TimescaleDB + pgx
│       ├── handlers/         # Handlers HTTP
│       ├── middleware/       # Auth JWT, CORS
│       ├── models/           # Structures de données
│       ├── errors/           # Gestion des erreurs
│       └── services/         # Logique métier
│
├── ai-service/               # Service d'analyse IA (Python/FastAPI)
│   └── ...                   # Endpoints AI, modèles, configuration
│
├── dashboard/                # Frontend Next.js
│   ├── app/                  # Pages (App Router)
│   ├── components/           # Composants React
│   ├── hooks/                # Hooks React personnalisés
│   └── lib/                  # Utilitaires
│
├── installer/                # Scripts d'installation
│   ├── go-installer/         # Installateur Windows Go + WebView2
│   └── linux/                # Scripts Linux
│
├── scripts/                  # Scripts utilitaires
│   ├── build-agent.ps1       # Build Windows
│   ├── build-agent.sh        # Build Linux
│   └── deploy.sh             # Déploiement VPS
│
├── deploy/                   # Configuration Docker
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   ├── Dockerfile.dashboard
│   └── Caddyfile
│
├── docs/                     # Documentation
│   ├── implementation/       # Docs d'implémentation détaillées
│   ├── specs/                # Spécifications techniques (ce dossier)
│   ├── ROADMAP.md            # Roadmap produit
│   └── USER_GUIDE.md         # Guide utilisateur
│
├── CHANGELOG.md              # Historique des versions
└── README.md                 # Documentation principale
```

---

## Liens Utiles

- [README principal](../../README.md)
- [CHANGELOG](../../CHANGELOG.md)
- [ROADMAP](../ROADMAP.md)
- [Guide utilisateur](../USER_GUIDE.md)

---

## Licence

**Propriétaire** - 2024-2025 2 LACS INFORMATIQUE

Ce logiciel est protégé par le droit d'auteur. Toute reproduction, distribution ou utilisation non autorisée est interdite.

---

## Support

- **Email**: support@2lacs-it.com
- **Website**: https://2lacs-it.com

---

**Optralis** - Solution professionnelle de monitoring d'infrastructure

*Voir plus loin. Agir plus vite.*
