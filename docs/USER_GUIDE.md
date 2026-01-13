# Guide Utilisateur Optralis

> **Optralis** - Solution SaaS de monitoring d'infrastructure
> *Voir plus loin. Agir plus vite.*

---

## Table des matières

1. [Présentation](#présentation)
2. [Accès au Dashboard](#accès-au-dashboard)
3. [Authentification Multi-Facteur (MFA)](#authentification-multi-facteur-mfa)
4. [Vue d'ensemble](#vue-densemble)
5. [Gestion des Machines](#gestion-des-machines)
6. [Groupes de Machines](#groupes-de-machines)
7. [Labels](#labels)
8. [Notifications & Alertes](#notifications--alertes)
9. [Mode Maintenance](#mode-maintenance)
10. [Gestion des Certificats](#gestion-des-certificats)
11. [Paramètres](#paramètres)
12. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
13. [Installation de l'Agent](#installation-de-lagent)
14. [Guide Administrateur](#guide-administrateur)
15. [FAQ](#faq)

---

## Présentation

Optralis est une solution complète de monitoring d'infrastructure qui permet de surveiller vos machines Windows et Linux en temps réel.

### Fonctionnalités principales

| Fonctionnalité | Description |
|----------------|-------------|
| **Monitoring temps réel** | CPU, RAM, disques, température, uptime |
| **S.M.A.R.T** | Santé des disques et prédiction de pannes |
| **Événements système** | Collecte des erreurs et avertissements |
| **Score de santé** | Évaluation automatique de l'état des machines |
| **Alertes email** | Notifications pour machines hors ligne |
| **Multi-tenant** | Isolation des données par organisation |
| **Groupes** | Organisation des machines avec codes couleurs |

### Langues supportées

- Français
- Anglais

Changez la langue via l'icône 🌐 dans le header.

### Thèmes

- **Mode sombre** (par défaut)
- **Mode clair**
- **Style Glassmorphism** ou **Classique**

---

## Accès au Dashboard

### Connexion

1. Accédez à `https://optralis.2lacs-it.com/dashboard/login`
2. Entrez votre email et mot de passe
3. Cliquez sur **Se connecter**

### Première connexion

Lors de votre première connexion, vous devrez changer votre mot de passe.

**Exigences du mot de passe :**
- Minimum 12 caractères
- Au moins 1 majuscule (A-Z)
- Au moins 1 minuscule (a-z)
- Au moins 1 chiffre (0-9)
- Au moins 1 caractère spécial (!@#$%^&*...)

### Mot de passe oublié

1. Cliquez sur **Mot de passe oublié ?**
2. Entrez votre adresse email
3. Consultez votre boîte de réception
4. Cliquez sur le lien de réinitialisation (valide 1 heure)

---

## Authentification Multi-Facteur (MFA)

L'authentification à deux facteurs (2FA/MFA) ajoute une couche de sécurité supplémentaire à votre compte.

### Activer le MFA

1. Allez dans **Paramètres**
2. Section **Sécurité** → **Authentification à deux facteurs**
3. Cliquez sur **Activer le MFA**
4. Scannez le QR code avec une application authenticator :
   - Google Authenticator
   - Microsoft Authenticator
   - Authy
   - 1Password
5. Entrez le code à 6 chiffres affiché
6. Sauvegardez vos **codes de secours** (10 codes à usage unique)

### Connexion avec MFA

1. Entrez votre email et mot de passe
2. Entrez le code à 6 chiffres de votre application
3. Cliquez sur **Vérifier**

### Codes de secours

Si vous n'avez plus accès à votre application authenticator :

1. Utilisez un de vos 10 codes de secours
2. Chaque code ne peut être utilisé qu'une seule fois
3. Après connexion, régénérez vos codes ou reconfigurez le MFA

### Désactiver le MFA

1. Allez dans **Paramètres** → **Sécurité**
2. Cliquez sur **Désactiver le MFA**
3. Confirmez avec votre mot de passe

---

## Vue d'ensemble

La page **Vue d'ensemble** affiche un résumé de votre parc informatique.

### Statistiques affichées

| Statistique | Description |
|-------------|-------------|
| **Machines totales** | Nombre total de machines surveillées |
| **En ligne** | Machines ayant envoyé un heartbeat < 5 min |
| **Hors ligne** | Machines sans heartbeat depuis > 5 min |
| **Score de santé moyen** | Moyenne des scores de toutes les machines |

### Indicateurs de statut

| Couleur | Signification |
|---------|---------------|
| 🟢 Vert | En ligne, bonne santé (score ≥ 80) |
| 🟡 Jaune | Attention requise (score 50-79) |
| 🔴 Rouge | Critique ou hors ligne (score < 50) |

---

## Gestion des Machines

### Liste des machines

La page **Machines** affiche toutes vos machines sous forme de cartes.

Chaque carte affiche :
- **Icône** : Laptop ou Desktop (détecté automatiquement)
- **Hostname** : Nom de la machine
- **Adresse IP** : IP principale
- **Statut** : En ligne / Hors ligne
- **Score de santé** : 0-100 avec icône coeur
- **Groupe** : Badge coloré (si assigné)

### Détails d'une machine

Cliquez sur une carte pour voir les détails :

#### Informations système
- Système d'exploitation et version
- Modèle CPU, coeurs, threads, fréquence
- RAM totale, type, vitesse
- Température CPU (si disponible)
- Uptime

#### Graphique CPU/RAM
- Évolution dans le temps
- Plages : 1h, 12h, 1j, 7j, 30j
- Filtres : Tout, CPU seul, RAM seule

#### Disques
- Nom et point de montage
- Espace total / utilisé / libre
- Barre de progression colorée
- Statut S.M.A.R.T

#### Événements système
- Erreurs et avertissements Windows/Linux
- Source, message, date
- Filtrage par type

### Score de santé

Le score est calculé automatiquement :

| Condition | Impact |
|-----------|--------|
| CPU > 80% | -10 points |
| RAM > 85% | -15 points |
| Disque > 90% | -20 points |
| S.M.A.R.T failure prédit | -50 points |
| Secteurs réalloués > 10 | -10 points |

### Supprimer une machine

1. Ouvrez les détails de la machine
2. Cliquez sur **Supprimer** (icône poubelle)
3. Confirmez la suppression

> ⚠️ La suppression est définitive. L'agent continuera d'envoyer des données et la machine réapparaîtra.

---

## Groupes de Machines

Les groupes permettent d'organiser vos machines par catégorie (Production, Dev, Bureautique, etc.).

### Créer un groupe

1. Allez dans **Machines**
2. Cliquez sur **Gérer les groupes**
3. Cliquez sur **+ Nouveau groupe**
4. Entrez un nom et choisissez une couleur
5. Cliquez sur **Créer**

### Assigner des machines

**Méthode 1 : Sélection multiple**
1. Cochez les machines à assigner (checkbox en haut à gauche des cartes)
2. Une barre d'action apparaît en bas
3. Sélectionnez le groupe dans le menu déroulant
4. Cliquez sur **Assigner**

**Méthode 2 : Depuis les détails**
1. Ouvrez les détails d'une machine
2. Utilisez le sélecteur de groupe

### Modifier/Supprimer un groupe

1. **Gérer les groupes** → Cliquez sur un groupe
2. Modifiez le nom ou la couleur
3. Ou cliquez sur **Supprimer**

> ⚠️ Supprimer un groupe ne supprime pas les machines, elles deviennent simplement non groupées.

---

## Labels

Les labels sont des tags key=value qui permettent de catégoriser finement vos machines.

### Créer un label

1. Allez dans **Machines**
2. Cliquez sur l'icône **Tags** dans l'en-tête
3. Cliquez sur **+ Nouveau label**
4. Entrez une clé (ex: `environnement`) et une valeur (ex: `production`)
5. Cliquez sur **Créer**

### Assigner des labels

1. Ouvrez les détails d'une machine
2. Section **Labels**
3. Sélectionnez les labels à assigner (max 10 par machine)

### Utilisation des labels

Les labels peuvent être utilisés pour :
- **Filtrer** les machines dans la liste
- **Cibler** les règles d'alertes (alerter uniquement les machines avec `environnement=production`)
- **Configurer** les intervalles de collecte par label

---

## Notifications & Alertes

Optralis supporte plusieurs canaux de notification pour vous alerter en temps réel.

### Canaux disponibles

| Canal | Format | Configuration |
|-------|--------|---------------|
| **Email** | HTML formaté | Liste d'adresses email |
| **Microsoft Teams** | MessageCard | URL Webhook Incoming |
| **Slack** | Block Kit | URL Webhook |
| **Discord** | Embed | URL Webhook |

### Types d'alertes

| Type | Description | Configurable |
|------|-------------|--------------|
| Machine hors ligne | Machine sans heartbeat | Délai (minutes) |
| CPU élevé | Usage CPU > seuil | Seuil (%) |
| RAM élevée | Usage RAM > seuil | Seuil (%) |
| Disque critique | Espace disque > seuil | Seuil (%) |
| Alerte SMART | Problème disque détecté | On/Off |

### Configurer un canal

1. Allez dans **Notifications**
2. Onglet **Canaux**
3. Cliquez sur **+ Nouveau canal**
4. Sélectionnez le type (Email, Teams, Slack, Discord)
5. Configurez les paramètres (email ou URL webhook)
6. Sélectionnez les types d'alertes à recevoir
7. Cliquez sur **Créer**

### Configurer une règle d'alerte

1. Allez dans **Notifications**
2. Onglet **Règles**
3. Cliquez sur **+ Nouvelle règle**
4. Configurez :
   - Métrique (CPU, RAM, Disque, Température, Offline)
   - Opérateur (>, <, >=, <=, ==)
   - Seuil
   - Sévérité (info, warning, critical)
   - Cible (toutes machines, groupe, label, machine spécifique)
5. Cliquez sur **Créer**

### Tester un canal

1. Dans la liste des canaux, cliquez sur **Tester**
2. Une notification de test est envoyée
3. Vérifiez la réception

### Cooldown

Chaque canal a un délai de cooldown (défaut: 60 minutes) pour éviter le spam de notifications.

---

## Mode Maintenance

Le mode maintenance permet de désactiver temporairement les alertes pour une machine.

### Activer le mode maintenance

1. Ouvrez les détails de la machine
2. Cliquez sur **Mode maintenance** (icône outil)
3. Sélectionnez la durée :
   - 30 minutes
   - 1 heure
   - 4 heures
   - 8 heures
   - 24 heures
   - 7 jours
4. Optionnel : ajoutez une note

### Pendant la maintenance

- Un badge **Maintenance** apparaît sur la carte de la machine
- Aucune alerte n'est envoyée pour cette machine
- Les métriques continuent d'être collectées normalement

### Terminer la maintenance

1. Ouvrez les détails de la machine
2. Cliquez sur **Terminer la maintenance**

---

## Gestion des Certificats

Chaque agent Optralis utilise un certificat mTLS (mutual TLS) pour s'authentifier de manière sécurisée auprès du serveur.

### Comprendre les certificats mTLS

| Élément | Description |
|---------|-------------|
| **Certificat client** | Fichier unique pour chaque machine, validité 1 an |
| **Clé privée** | Associée au certificat, stockée sur la machine |
| **CA** | Autorité de certification interne Optralis |

### Statuts des certificats

| Statut | Couleur | Description |
|--------|---------|-------------|
| **Valide** | 🟢 Vert | Plus de 30 jours avant expiration |
| **Expire bientôt** | 🟡 Jaune | Entre 7 et 30 jours avant expiration |
| **Expire très bientôt** | 🟠 Orange | Moins de 7 jours avant expiration |
| **Expiré** | 🔴 Rouge | Certificat expiré |
| **Révoqué** | 🔴 Rouge | Certificat manuellement révoqué |

### Voir le certificat d'une machine

1. Ouvrez les détails d'une machine
2. Cliquez sur l'onglet **Certificat machine**
3. Consultez les informations :
   - Statut actuel
   - Numéro de série
   - Date d'émission
   - Date d'expiration
   - Date de révocation (si applicable)

### Renouvellement automatique

Les certificats sont renouvelés automatiquement par l'agent :
- L'agent vérifie son certificat toutes les 24 heures
- Si l'expiration est dans moins de 30 jours, il demande un renouvellement
- Le nouveau certificat est appliqué automatiquement
- L'ancien certificat reste valide 24h (grace period)

### Actions administrateur

Les administrateurs peuvent effectuer des actions manuelles sur les certificats :

#### Révoquer un certificat

1. Ouvrez les détails de la machine
2. Onglet **Certificat machine**
3. Cliquez sur **Révoquer**
4. Confirmez l'action

> ⚠️ **Attention** : La révocation est immédiate. L'agent ne pourra plus s'authentifier et devra être réinstallé.

#### Renouveler un certificat

1. Ouvrez les détails de la machine
2. Onglet **Certificat machine**
3. Cliquez sur **Renouveler**
4. Le nouveau certificat est généré

> Note : Le renouvellement manuel génère un nouveau certificat côté serveur. L'agent récupérera automatiquement ce nouveau certificat lors de sa prochaine tentative de renouvellement.

### Alertes d'expiration

Le système envoie automatiquement des alertes email :
- **30 jours avant** : Avertissement aux administrateurs
- **7 jours avant** : Alerte critique
- Notifications classifiées par sévérité

---

## Paramètres

### Informations du compte

- Nom de l'organisation
- ID de licence
- Type de licence
- Nombre de machines utilisées / limite

### Auto-déconnexion

Configurez la déconnexion automatique après inactivité :
- Jamais
- 15 minutes
- 30 minutes
- 1 heure
- 2 heures

### Thème et langue

- **Thème** : Sombre / Clair
- **Style** : Glassmorphism / Classique
- **Langue** : Français / English

### Intervalles de collecte

Les administrateurs peuvent configurer les intervalles de collecte des agents.

1. Allez dans **Paramètres** → **Intervalles de collecte**
2. Configurez les intervalles par niveau de priorité :
   - **Global** : Appliqué à toutes les machines
   - **Groupe** : Appliqué aux machines d'un groupe
   - **Label** : Appliqué aux machines avec un label spécifique
   - **Machine** : Appliqué à une machine spécifique

| Type d'intervalle | Plage |
|-------------------|-------|
| Heartbeat | 5 - 300 secondes |
| Inventaire | 5 min - 2 heures |
| Mises à jour | 1 - 24 heures |

---

## Gestion des Utilisateurs

Les administrateurs peuvent gérer plusieurs utilisateurs au sein de leur organisation.

### Rôles disponibles

| Rôle | Description | Permissions |
|------|-------------|-------------|
| **Admin** | Administrateur client | Configuration, notifications, gestion utilisateurs |
| **Observer** | Observateur | Lecture seule (dashboard, machines) |

### Créer un utilisateur

1. Allez dans **Utilisateurs** (menu sidebar)
2. Cliquez sur **+ Ajouter un utilisateur**
3. Remplissez :
   - Adresse email
   - Prénom et nom
   - Rôle (Admin ou Observer)
4. Cliquez sur **Créer**
5. L'utilisateur reçoit un email avec un mot de passe temporaire

### Modifier un utilisateur

1. Cliquez sur l'icône crayon à côté de l'utilisateur
2. Modifiez les informations (le rôle ne peut être changé)
3. Cliquez sur **Enregistrer**

### Réinitialiser un mot de passe

1. Cliquez sur l'icône clé à côté de l'utilisateur
2. Confirmez l'action
3. L'utilisateur reçoit un email avec un nouveau mot de passe temporaire

### Supprimer un utilisateur

1. Cliquez sur l'icône poubelle
2. Confirmez la suppression

> ⚠️ Le dernier administrateur ne peut pas être supprimé.

---

## Installation de l'Agent

L'agent Optralis collecte les métriques de vos machines et les envoie au serveur. Chaque agent reçoit automatiquement un **certificat mTLS unique** pour s'authentifier de manière sécurisée.

### Windows

1. Allez dans la page **Installation** du dashboard
2. Section **Windows**, cliquez sur **Télécharger l'installateur**
3. Un fichier EXE personnalisé est généré (contient un token temporaire)
4. Exécutez l'installateur en tant qu'administrateur
5. L'agent s'enregistre automatiquement et reçoit son certificat mTLS

> 💡 Le token intégré dans l'EXE est à usage unique et expire après 24h ou après X machines installées (selon votre licence).

**Option températures CPU précises (LHM) :**

L'installeur propose une option pour installer le driver LibreHardwareMonitor (LHM) permettant de lire les températures CPU précises.

- **Par défaut** : LHM désactivé (utilise WMI, moins précis mais fonctionnel)
- **Avec LHM** : Températures CPU précises via registres MSR

> ⚠️ **Note antivirus** : Le driver LHM peut être signalé par certains antivirus (faux positif). Si vous activez LHM, ajoutez ces exclusions :
> - Dossier : `C:\Program Files\Optralis Agent\lhm\`
> - Processus : `lhm-wrapper.exe`

### Linux

1. Allez dans la page **Installation** du dashboard
2. Section **Linux**, cliquez sur **Générer un token**
3. Un token temporaire est affiché avec une commande curl à exécuter
4. Copiez et exécutez la commande sur votre machine Linux :

```bash
curl -fsSL "https://optralis.2lacs-it.com/install.sh?token=VOTRE_TOKEN" | sudo bash
```

> 💡 Le token expire après 1 heure ou après utilisation.

### Vérification

Après installation, la machine apparaît dans le dashboard sous 1-2 minutes.

### Désinstallation

**Windows :**
```powershell
optralis-agent.exe -uninstall
```

**Linux :**
```bash
sudo /opt/optralis-agent/uninstall.sh
```

---

## Guide Administrateur

Cette section est réservée aux **Super Administrateurs**.

### Accès au panel admin

Si vous êtes super admin, un menu **Administration** apparaît dans la sidebar.

### Dashboard Admin

Vue globale de la plateforme :
- Total clients (actifs / expirés)
- Total machines (en ligne / hors ligne)
- Top clients par nombre de machines
- Timeline d'activité

### Gestion des Clients

#### Créer un client

1. **Administration** → **Clients**
2. Cliquez sur **+ Nouveau client**
3. Remplissez :
   - Nom de l'organisation
   - Email du premier utilisateur
   - Mot de passe temporaire
   - Type de licence
   - Date d'expiration (optionnel)
4. Cliquez sur **Créer**

#### Modifier un client

1. Cliquez sur l'icône crayon
2. Modifiez les informations
3. Cliquez sur **Enregistrer**

#### Impersonation

Visualisez le dashboard d'un client sans vous déconnecter :

1. Cliquez sur l'icône œil à côté du client
2. Un nouvel onglet s'ouvre avec le dashboard du client
3. Un bandeau orange indique le mode impersonation
4. Cliquez sur **Quitter** pour fermer

### Gestion des Licences

#### Types de licences

| Type | Machines | Rétention |
|------|----------|-----------|
| Trial | 5 | 7 jours |
| Starter | 25 | 30 jours |
| Pro | 150 | 90 jours |
| Enterprise | Illimité | Personnalisée (6-24 mois) |

#### Créer un type de licence

1. **Administration** → **Licences**
2. Onglet **Types de licences**
3. Cliquez sur **+ Nouveau type**
4. Configurez les limites
5. Cliquez sur **Créer**

### Monitoring Docker

Surveillez les containers Docker du serveur :

1. **Administration** → **Docker**
2. Liste des containers avec statut
3. Actions : Démarrer, Arrêter, Redémarrer
4. Cliquez sur un container pour voir :
   - Logs en temps réel
   - Statistiques CPU/RAM
   - Configuration

### Gestion des Certificats (Super Admin)

Vue globale de tous les certificats mTLS de la plateforme.

1. **Administration** → **Certificats**
2. Consultez les statistiques :
   - Total des certificats
   - Certificats valides
   - Expirant bientôt (7-30 jours)
   - Expirant (< 7 jours)
   - Expirés
   - Révoqués

#### Filtres disponibles

| Filtre | Description |
|--------|-------------|
| **Statut** | Filtrer par état du certificat |
| **Client** | Filtrer par organisation |
| **Recherche** | Rechercher par hostname ou numéro de série |

#### Actions

- Cliquez sur une machine pour accéder directement à ses détails
- Pagination par 25 certificats
- Tri par date d'expiration (les plus urgents en premier)

---

## FAQ

### L'agent ne se connecte pas

1. Vérifiez que le certificat mTLS est présent :
   - Windows : `C:\ProgramData\optralis-agent\certs\`
   - Linux : `/etc/optralis-agent/certs/`
2. Vérifiez la connectivité réseau vers `optralis-api.2lacs-it.com`
3. Vérifiez que le pare-feu autorise HTTPS (port 443)
4. Consultez les logs de l'agent :
   - Windows : Observateur d'événements → Application
   - Linux : `journalctl -u optralis-agent`
5. Si le certificat est expiré ou révoqué, réinstallez l'agent avec un nouveau token

### La température CPU n'apparaît pas

**Windows :**

L'agent peut utiliser deux méthodes pour collecter les températures :

1. **LibreHardwareMonitor (LHM)** - Températures précises par core CPU
   - Doit être activé lors de l'installation (checkbox ou flag `-with-lhm`)
   - Peut être signalé par l'antivirus (ajouter exclusions si nécessaire)
   - Chemin : `C:\Program Files\Optralis Agent\lhm\`

2. **WMI ThermalZone** - Fallback automatique si LHM absent
   - Moins précis (température système/chipset)
   - Aucune configuration requise
   - Fonctionne sans alertes antivirus

> 💡 **Conseil** : Si vous avez besoin de températures CPU précises et que votre antivirus bloque LHM, ajoutez les exclusions puis réinstallez l'agent avec l'option LHM activée.

**Linux :** Vérifiez que le module `coretemp` est chargé :
```bash
sudo modprobe coretemp
```

### Les données S.M.A.R.T ne s'affichent pas

**Comportement :** La carte "Santé S.M.A.R.T" s'affiche toujours avec un message "Aucune donnée SMART disponible" si aucune donnée n'est collectée.

**Disques supportés :**
- Disques NVMe : Supportés
- Disques SATA : Supportés
- Disques USB : Non supportés
- RAID matériel : Dépend du contrôleur (HP Smart Array, Dell PERC : support limité)

**Étapes de diagnostic (Windows) :**

1. **Vérifier smartctl.exe :**
   ```cmd
   dir "C:\ProgramData\optralis-agent\bin\smartctl.exe"
   ```

2. **Tester manuellement :**
   ```cmd
   "C:\ProgramData\optralis-agent\bin\smartctl.exe" -a -j /dev/pd0
   ```

3. **Vérifier le mapping WMIC :**
   ```cmd
   wmic logicaldisk where "DeviceID='C:'" assoc /assocclass:Win32_LogicalDiskToPartition
   ```

4. **Vérifier les logs agent :**
   ```
   C:\ProgramData\optralis-agent\logs\
   ```

**Causes fréquentes :**
| Cause | Solution |
|-------|----------|
| RAID matériel | Contrôleurs RAID peuvent masquer les données SMART |
| Droits admin | Vérifier que le service tourne en admin |
| Collector pas exécuté | Attendre 2h (intervalle par défaut) |
| WMIC désactivé | Réactiver WMIC sur Windows |

### Comment changer le mot de passe d'un utilisateur ?

**En tant qu'utilisateur :**
1. Cliquez sur votre profil (en haut à droite)
2. **Changer le mot de passe**

**En tant qu'admin :**
1. Éditez le client
2. Cochez **Réinitialiser le mot de passe**
3. L'utilisateur recevra un email

### Quelle est la fréquence de collecte ?

La fréquence de collecte est entièrement configurable selon vos besoins. Vous pouvez définir des intervalles personnalisés par :
- Machine individuelle
- Groupe de machines
- Labels
- Configuration globale

Les intervalles peuvent être configurés dans la section **Paramètres > Intervalles de collecte** du dashboard.

### Comment exporter les données ?

**Export CSV des machines :**

1. Allez dans **Machines**
2. Cliquez sur le bouton **Exporter** (icône téléchargement)
3. Un fichier CSV avec 18 colonnes est téléchargé :
   - Hostname, OS, IP, Agent Version
   - CPU (modèle, coeurs, fréquence)
   - RAM (total, type, vitesse)
   - Score de santé, dernier heartbeat
   - Et plus...

---

## Support

- **Email** : support@2lacs-it.com
- **Site web** : https://2lacs-it.com

---

*Optralis - Solution professionnelle de monitoring d'infrastructure*

*Développé par [2 LACS INFORMATIQUE](https://2lacs-it.com)*
