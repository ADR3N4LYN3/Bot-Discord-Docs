# Optralis Discord Docs Bot

Bot Discord en Python qui surveille automatiquement votre documentation Optralis et publie les mises à jour dans des canaux Discord spécifiques.

## Fonctionnalités

- 🔍 **Surveillance automatique** : Détecte les modifications de fichiers .md en temps réel
- 📝 **Formatage intelligent** : Parse le markdown et crée des embeds Discord colorés
- ✂️ **Division automatique** : Divise les longs documents (jusqu'à 86 KB) en plusieurs messages
- 🎯 **Mapping intelligent** : Route automatiquement vers les bons canaux Discord
- 📊 **Support complet** : Tables, code blocks, emojis, cross-links
- 🛡️ **Robuste** : Gestion d'erreurs, rate limiting, retry logic

## Structure de Mapping

| Dossier source | Canal Discord cible |
|----------------|---------------------|
| `docs/` (racine) | `#documentation` |
| `docs/specs/` | `#specifications` |
| `docs/implementation/` | `#implementation` |
| `docs/plans/` | `#planning` |

## Prérequis

- Python 3.9 ou supérieur
- Un compte Discord avec accès administrateur sur le serveur cible
- Git (pour cloner le repo)

## Installation

### 1. Créer le Bot Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur **New Application**
3. Donnez un nom à votre bot (ex: "Optralis Docs Bot")
4. Allez dans l'onglet **Bot**
5. Cliquez sur **Add Bot**
6. Activez les **Privileged Gateway Intents** suivants :
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
7. Copiez le **Token** (vous en aurez besoin pour `.env`)
8. Allez dans **OAuth2** → **URL Generator**
9. Sélectionnez les scopes :
   - `bot`
10. Sélectionnez les permissions :
    - ✅ View Channels
    - ✅ Send Messages
    - ✅ Embed Links
    - ✅ Read Message History
11. Copiez l'URL générée et ouvrez-la pour inviter le bot sur votre serveur

### 2. Créer les Canaux Discord

Dans votre serveur Discord, créez ces 4 canaux texte :

- `#documentation`
- `#specifications`
- `#implementation`
- `#planning`

### 3. Installer le Bot

```bash
# Cloner le repository
git clone <url-du-repo>
cd Bot-Discord-Docs

# Créer un virtual environment
python -m venv venv

# Activer le virtual environment
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copier le template de configuration
copy .env.example .env

# Éditer .env avec vos valeurs
notepad .env
```

Remplissez les valeurs suivantes dans `.env` :

```env
DISCORD_BOT_TOKEN=votre_token_bot_ici
GUILD_ID=id_de_votre_serveur
DOCS_PATH=D:\REVOIRE\Documents\GitHub\Bot-Discord-Docs\docs
```

**Pour trouver votre GUILD_ID :**
1. Dans Discord, allez dans **Paramètres Utilisateur** → **Avancé**
2. Activez **Mode développeur**
3. Faites un clic droit sur votre serveur → **Copier l'identifiant du serveur**

## Utilisation

### Démarrer le Bot

```bash
python main.py
```

Vous devriez voir :

```
[INFO] Configuration chargée avec succès
[INFO] Bot connecté en tant que Optralis Docs Bot#1234
[INFO] Cache de canaux construit : 4 canaux trouvés
[INFO] Surveillance démarrée sur : D:\...\docs
[INFO] Bot prêt !
```

### Tester le Bot

1. Modifiez un fichier dans le dossier `docs/` (ex: `docs/USER_GUIDE.md`)
2. Sauvegardez le fichier
3. Vérifiez que le message apparaît dans le canal Discord correspondant (`#documentation`)

### Arrêter le Bot

Appuyez sur `Ctrl+C` dans le terminal pour arrêter gracieusement le bot.

## Structure du Projet

```
Bot-Discord-Docs/
├── .env                    # Configuration (NON commité)
├── .env.example            # Template de configuration
├── .gitignore              # Fichiers à ignorer
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
├── config.py               # Chargement de la config
├── main.py                 # Point d'entrée
├── bot/                    # Package Discord bot
│   ├── client.py           # Client Discord
│   └── events.py           # Event handlers
├── watcher/                # Package file watcher
│   ├── file_watcher.py     # Observateur watchdog
│   └── event_handler.py    # Traitement événements
├── processors/             # Package de traitement
│   ├── markdown_parser.py  # Parsing markdown
│   ├── message_splitter.py # Division des messages
│   └── embed_builder.py    # Création d'embeds
└── utils/                  # Utilitaires
    ├── logger.py           # Configuration logging
    └── channel_resolver.py # Résolution de canaux
```

## Configuration Avancée

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DISCORD_BOT_TOKEN` | (requis) | Token du bot Discord |
| `GUILD_ID` | (requis) | ID du serveur Discord |
| `DOCS_PATH` | (requis) | Chemin vers le dossier docs |
| `AUTO_START_WATCHER` | `true` | Démarrer la surveillance auto |
| `WATCH_RECURSIVE` | `true` | Surveiller les sous-dossiers |
| `EMBED_COLOR` | `0x5865F2` | Couleur des embeds (hex) |
| `MAX_MESSAGE_LENGTH` | `2000` | Longueur max des messages |
| `MESSAGE_DELAY` | `0.5` | Délai entre messages (sec) |
| `LOG_LEVEL` | `INFO` | Niveau de log |
| `LOG_FILE` | `bot.log` | Fichier de log |

## Dépannage

### Le bot ne se connecte pas

- Vérifiez que le token dans `.env` est correct
- Assurez-vous que les intents sont activés dans le Developer Portal
- Vérifiez votre connexion internet

### Les messages n'apparaissent pas dans Discord

- Vérifiez que les 4 canaux existent avec les bons noms
- Vérifiez les permissions du bot (droit d'envoyer des messages)
- Consultez les logs dans `bot.log` pour plus de détails

### Erreur "Documentation path does not exist"

- Vérifiez que le chemin `DOCS_PATH` dans `.env` est correct
- Utilisez des chemins absolus (complets)
- Sur Windows, utilisez `\` ou `\\` comme séparateurs

### Le bot ne détecte pas les changements de fichiers

- Vérifiez que `AUTO_START_WATCHER=true` dans `.env`
- Assurez-vous que les fichiers sont bien des `.md`
- Consultez les logs pour voir si des erreurs sont reportées

## Développement

### Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-asyncio

# Lancer les tests
pytest
```

### Structure des Logs

Les logs sont écrits dans `bot.log` avec le format :

```
[2026-01-13 15:30:00] [INFO] [DocsBot] Message ici
```

Niveaux de log :
- **DEBUG** : Détails techniques
- **INFO** : Informations normales
- **WARNING** : Avertissements
- **ERROR** : Erreurs non critiques
- **CRITICAL** : Erreurs critiques

## Licence

**Propriétaire** - 2024-2025 2 LACS INFORMATIQUE

Ce logiciel est protégé par le droit d'auteur. Toute reproduction, distribution ou utilisation non autorisée est interdite.

## Support

- **Email** : support@2lacs-it.com
- **Website** : https://2lacs-it.com

---

**Optralis Docs Bot** - Synchronisation automatique de documentation vers Discord
