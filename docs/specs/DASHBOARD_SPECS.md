# Dashboard Next.js - Spécifications Techniques

## Vue d'ensemble

Frontend Next.js 16 avec App Router, React 19, TypeScript, Tailwind CSS et interface Glassmorphism.

---

## Providers

Le dashboard utilise plusieurs providers imbriqués:

- `ThemeProvider` - Dark/Light mode + Glassmorphism
- `I18nProvider` - Français/Anglais
- `AuthProvider` - Gestion authentification + impersonation

---

## Design System (Thème Linear)

Le dashboard utilise un design system inspiré de Linear avec des couleurs neutres et des accents orange.

### Palette de couleurs

| Type | Classe Tailwind | Usage |
|------|-----------------|-------|
| **Background** | `bg-white/10`, `bg-white/5` | Fonds semi-transparents |
| **Hover** | `hover:bg-white/10`, `hover:bg-white/5` | États hover |
| **Border** | `border-white/10` | Bordures subtiles |
| **Neutral** | `bg-neutral-50` à `bg-neutral-900` | Gris purs (remplace slate) |
| **Brand** | `bg-brand-400` à `bg-brand-700` | Accents orange/coral |

### Classes CSS du design system

| Classe | Description |
|--------|-------------|
| `dashboard-card` | Card avec fond glassmorphism |
| `dashboard-glass-card` | Card avec effet verre |
| `dashboard-neon-card` | Card avec bordure lumineuse |
| `dashboard-inner-box` | Encadré interne (remplace `bg-slate-100 dark:bg-slate-800`) |
| `dashboard-input` | Input stylé |
| `dashboard-code-block` | Bloc de code |
| `dashboard-badge-success` | Badge vert (succès) |
| `dashboard-badge-warning` | Badge amber (attention) |
| `dashboard-badge-error` | Badge rouge (erreur) |
| `dashboard-badge-info` | Badge bleu (info) |

### Convention de couleurs

⚠️ **Ne pas utiliser** les couleurs `slate-*` (teinte bleutée). Utiliser `neutral-*` ou `white/10` à la place.

| ❌ Éviter | ✅ Utiliser |
|-----------|-------------|
| `bg-slate-100 dark:bg-slate-800` | `bg-white/10 dark:bg-white/5` ou `dashboard-inner-box` |
| `hover:bg-slate-200 dark:hover:bg-slate-700` | `hover:bg-white/10` |
| `border-slate-200 dark:border-slate-700` | `border-white/10` |
| `bg-slate-50 dark:bg-slate-900` | `bg-neutral-50 dark:bg-neutral-900` |

### Couleurs de statut (conservées)

| Statut | Couleurs |
|--------|----------|
| Succès | `text-green-500`, `bg-green-500/20` |
| Attention | `text-amber-500`, `bg-amber-500/20` |
| Erreur | `text-red-500`, `bg-red-500/20` |
| Info | `text-blue-500`, `bg-blue-500/20` |

---

## Composants Principaux

| Composant | Description |
|-----------|-------------|
| `Sidebar.tsx` | Navigation principale |
| `Header.tsx` | Header avec langue, thème, user menu |
| `AdminSidebar.tsx` | Navigation admin |
| `MachineCard.tsx` | Card machine dans la liste (avec badge conformité OS) |
| `MetricsChart.tsx` | Graphique CPU/RAM |
| `TimelineChart.tsx` | Graphique timeline |
| `EventsTable.tsx` | Table des événements |
| `AdminDashboard.tsx` | Stats admin : clients (actifs/expirés) et machines (en ligne/hors ligne) |
| `ClientList.tsx` | Liste clients admin avec lignes expandables |
| `LicenseOverview.tsx` | Vue globale des licences avec filtres et statistiques |
| `ActivityPage.tsx` | Journal d'activité admin avec graphique, filtres avancés et export CSV |
| `AgentVersionList.tsx` | Liste des versions agent avec stats |
| `ChannelManager.tsx` | Gestion des canaux de mise à jour (stable/beta) |
| `AutoRefresh.tsx` | Contrôle auto-refresh avec bouton manuel |
| `MachineDetailsSidebar.tsx` | Navigation verticale collapsible pour détails machine |
| `StatsCard.tsx` | Card statistiques avec badge optionnel |
| `InlineMessage.tsx` | Messages contextuels inline (success/error/info) |

---

## Carte S.M.A.R.T (Page Machine Details)

**Fichier:** `dashboard/app/dashboard/machines/[hostname]/page.tsx`

La carte "Santé S.M.A.R.T" affiche les informations de santé des disques physiques.

### Comportement d'affichage

| État | Affichage |
|------|-----------|
| Données SMART disponibles | Carte avec détails par disque (température, cycles, secteurs) |
| Uniquement disques virtuels | Carte compacte avec badges "Disque virtuel OK" |
| Aucune donnée | Carte avec message "Aucune donnée SMART disponible" |

**Note :** La carte s'affiche **toujours**, même sans données, pour informer l'utilisateur.

### Statuts des disques

| Statut | Couleur | Condition |
|--------|---------|-----------|
| `healthy` | Vert | SMART OK, aucune erreur |
| `warning` | Jaune | Secteurs réalloués ou en attente > 0 |
| `critical` | Rouge | Secteurs non corrigibles > 0 ou prédiction de panne |
| `virtual` | Vert | Disque virtuel (VM) |
| `unavailable` | - | SMART non supporté |

### Traductions i18n

| Clé | FR | EN |
|-----|----|----|
| `smart.title` | Santé S.M.A.R.T | S.M.A.R.T Health |
| `smart.noData` | Aucune donnée SMART disponible | No SMART data available |
| `smart.healthy` | Bon état | Healthy |
| `smart.warning` | Attention | Warning |
| `smart.critical` | Critique | Critical |
| `smart.virtual` | Disque virtuel OK | Virtual disk OK |

---

## Cartes Overview (Page Machine Details)

**Fichier:** `dashboard/app/dashboard/machines/[hostname]/page.tsx`

Les cartes d'overview affichent un résumé rapide de l'état de la machine avec des barres de progression visuelles.

### Structure des cartes

```
┌─────────────────────────────────────────────────────────────────┐
│  Services                                     Voir détails →    │
├─────────────────────────────────────────────────────────────────┤
│  [En cours: 144]  [Critiques: 0]  [Total: 301]                 │
│  ████████████████████████░░░░░░░░░░░░ 48% actifs               │
├─────────────────────────────────────────────────────────────────┤
│  Mises à jour                                 Voir détails →    │
├─────────────────────────────────────────────────────────────────┤
│  [En attente: 0]  [Sécurité: 0]  [Redémarrage: ✓]              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Réseau                                       Voir détails →    │
├─────────────────────────────────────────────────────────────────┤
│  ⚠️ 10 port(s) à risque: 135/tcp, 445/tcp... [cliquable →]     │
├─────────────────────────────────────────────────────────────────┤
│  [Ports ouverts: 99]  [À risque: 10]                           │
│  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 10% à risque             │
├─────────────────────────────────────────────────────────────────┤
│  Sécurité                                     Voir détails →    │
├─────────────────────────────────────────────────────────────────┤
│  [✓ Antivirus]  [✓ Pare-feu]  [✓ BitLocker]                    │
│  ████████████████████████████████████████████ 100% protégé      │
└─────────────────────────────────────────────────────────────────┘
```

### Barres de progression

| Section | Calcul | Couleurs |
|---------|--------|----------|
| **Services** | `running / total` | Vert (informatif) |
| **Réseau** | `risky / open` | Vert (<5%), Jaune (5-15%), Rouge (>15%) |
| **Sécurité** | `actifs / total` | Vert (100%), Jaune (66%+), Rouge (<66%) |

### Calcul du score Sécurité

| OS | Protections comptées | Total |
|----|---------------------|-------|
| Windows | Antivirus + Firewall + BitLocker | 3 |
| Linux | Firewall uniquement | 1 |

### Bannière ports à risque

La bannière des ports à risque est **cliquable** et navigue vers l'onglet Réseau :
- Affiche les 3 premiers ports avec leur protocole
- Effet hover avec transition de couleur
- Flèche indicative au survol

### Traductions i18n

| Clé | FR | EN |
|-----|----|----|
| `overview.active` | actifs | active |
| `overview.atRisk` | à risque | at risk |
| `overview.protected` | protégé | protected |

---

## Page Journal d'Activité (Activity Page)

**Fichier:** `dashboard/app/dashboard/admin/activity/page.tsx`

### Structure de la page

```
┌─────────────────────────────────────────────────┐
│  AutoRefresh (30s)                               │
├─────────────────────────────────────────────────┤
│  Header (Titre + Sous-titre)                     │
├─────────────────────────────────────────────────┤
│  Stats Cards (4 cartes)                          │
│  [Total] [24h] [Erreurs] [Warnings]              │
├─────────────────────────────────────────────────┤
│  Graphique répartition par catégorie             │
│  (Barres horizontales colorées)                  │
├─────────────────────────────────────────────────┤
│  Filtres (Search + Dropdowns + Dates + Export)   │
├─────────────────────────────────────────────────┤
│  Tableau des logs (Desktop) / Cards (Mobile)     │
└─────────────────────────────────────────────────┘
```

### Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **Graphique catégories** | Barres horizontales avec couleurs par catégorie (auth=violet, email=vert, alert=orange, system=gris, user=bleu, machine=cyan) |
| **Filtres avancés** | Client, Catégorie, Niveau, Pagination, Date début/fin |
| **Export CSV** | Télécharge les logs affichés avec encodage UTF-8 + BOM (compatible Excel FR) |
| **Colonnes redimensionnables** | Drag & drop pour ajuster les colonnes, persisté en localStorage |
| **Vue mobile** | Cards au lieu du tableau sur écrans <768px |

### Catégories d'activité

| Catégorie | Icône | Couleur barre | Messages loggés |
|-----------|-------|---------------|-----------------|
| `auth` | Shield | Violet | Login, reset password, création utilisateur |
| `email` | Mail | Vert | Envoi emails (bienvenue, reset, contact, alertes) |
| `alert` | Bell | Orange | Alertes machines hors ligne |
| `system` | Server | Gris | Groupes, labels, paramètres collecte, config IA |
| `user` | User | Bleu | Actions utilisateur |
| `machine` | Monitor | Cyan | Suppression, maintenance, certificats, groupes |

### Traductions i18n (nouvelles)

| Clé | FR | EN |
|-----|----|----|
| `activity.categoryDistribution` | Répartition par catégorie | Distribution by category |
| `activity.startDate` | Date début | Start date |
| `activity.endDate` | Date fin | End date |
| `activity.export` | Exporter | Export |
| `activity.exportCSV` | Exporter en CSV | Export to CSV |

---

## Système de Messages Inline

**Fichier:** `dashboard/components/InlineMessage.tsx`

Système de notifications contextuelles remplaçant les Toast globaux. Les messages apparaissent à côté de l'élément modifié pour une meilleure UX.

### Hook `useInlineMessage`

```typescript
import { useInlineMessage, InlineMessage } from '@/components/InlineMessage';

function MyComponent() {
  const { showMessage, message, dismissMessage } = useInlineMessage();

  const handleSave = async () => {
    try {
      await saveData();
      showMessage('Sauvegarde réussie', 'success');
    } catch (err) {
      showMessage('Erreur de sauvegarde', 'error');
    }
  };

  return (
    <div>
      <InlineMessage message={message} onDismiss={dismissMessage} className="mb-4" />
      <button onClick={handleSave}>Sauvegarder</button>
    </div>
  );
}
```

### Types de messages

| Type | Couleur | Icône | Usage |
|------|---------|-------|-------|
| `success` | Vert | CheckCircle | Opération réussie |
| `error` | Rouge | AlertCircle | Erreur |
| `info` | Bleu | Info | Information |

### Comportement

| Fonctionnalité | Description |
|----------------|-------------|
| **Auto-dismiss** | Disparaît après 3 secondes |
| **Animation** | Fade-in à l'apparition (`animate-fade-in`) |
| **Dismiss manuel** | Bouton X pour fermer immédiatement |
| **Contextuel** | Placé proche de l'élément concerné |

### Configuration

```typescript
// dashboard/lib/config.ts
MESSAGE_DURATION_MS: 3000 // Durée d'affichage en ms
```

### Pages utilisant InlineMessage

| Page | Actions avec toast |
|------|-------------------|
| `machines/page.tsx` | Export CSV |
| `machines/[hostname]/page.tsx` | Delete, Force collect, Maintenance |
| `machines/[hostname]/tabs/CertificateTab.tsx` | Actions certificat |
| `settings/collection/page.tsx` | Create/Edit/Delete intervals |
| `settings/users/page.tsx` | Create/Edit/Delete users, Reset password |
| `settings/notifications/page.tsx` | CRUD canaux et règles, Toggle |
| `users/page.tsx` | Create/Edit/Delete users |
| `admin/certificates/page.tsx` | Revoke, Restore, Purge, Refresh cache |
| `admin/docker/page.tsx` | Start, Stop, Restart container |
| `ai-config/page.tsx` | Analyze, Save config |

---

## IntervalSelect (Dropdown Custom)

**Fichier:** `dashboard/components/CollectionSettingsModal.tsx`

Composant dropdown personnalisé remplaçant le `<select>` natif pour supporter le thème dark mode. Les options natives `<option>` héritent du style OS et ne respectent pas le CSS dark.

### Props

| Prop | Type | Description |
|------|------|-------------|
| `value` | `number \| undefined` | Valeur sélectionnée (undefined = hériter) |
| `onChange` | `(value: number \| undefined) => void` | Callback de changement |
| `options` | `Array<{ value, label, labelEn, isDefault? }>` | Options disponibles |
| `disabled` | `boolean` | Désactivé si le collector est désactivé |
| `language` | `string` | Langue courante (fr/en) |

### Comportement

| Fonctionnalité | Description |
|----------------|-------------|
| **Portal rendering** | Menu rendu via `createPortal` pour éviter overflow |
| **Position auto** | S'ouvre vers le haut si pas d'espace en bas |
| **Fermeture auto** | Clic extérieur, Escape, resize (pas scroll - contexte modal) |
| **Checkmark** | Icône Check sur l'option sélectionnée |
| **Dark theme** | Classe `dashboard-dropdown` avec thème Linear |
| **Hover states** | `hover:bg-black/5 dark:hover:bg-white/5` |

---

## FilterDropdown (Dropdown Générique)

**Fichier:** `dashboard/components/FilterDropdown.tsx`

Composant dropdown générique avec support thème dark via la classe CSS `dashboard-dropdown`. Utilisé pour remplacer les `<select>` natifs dans tout le dashboard.

### Props

| Prop | Type | Description |
|------|------|-------------|
| `value` | `string` | Valeur sélectionnée |
| `onChange` | `(value: string) => void` | Callback de changement |
| `options` | `Array<{ value: string, label: string }>` | Options disponibles |
| `placeholder` | `string` | Texte quand aucune sélection |
| `className` | `string` | Classes CSS additionnelles |

### Comportement

| Fonctionnalité | Description |
|----------------|-------------|
| **Portal rendering** | Menu rendu via `createPortal` pour éviter overflow |
| **Position auto** | S'ouvre vers le haut si pas d'espace en bas |
| **Fermeture auto** | Clic extérieur, Escape, scroll |
| **Dark theme** | Classe `dashboard-dropdown` avec styles globaux |
| **Option reset** | Première option permet de réinitialiser |

### Utilisation

```tsx
import FilterDropdown from '@/components/FilterDropdown';

<FilterDropdown
  value={selectedMetric}
  onChange={setSelectedMetric}
  options={[
    { value: 'cpu', label: 'CPU' },
    { value: 'ram', label: 'Mémoire' },
    { value: 'disk', label: 'Disque' }
  ]}
  placeholder="Sélectionner une métrique"
  className="w-full"
/>
```

### Style CSS global

```css
/* globals.css */
.dashboard-dropdown {
  @apply rounded-xl shadow-lg border border-black/10 dark:border-white/10
         bg-white/95 dark:bg-[rgba(10,10,10,0.95)] backdrop-blur-xl;
}
```

---

## Validation Formulaires

### Pattern recommandé

Pour éviter les bulles de validation natives du navigateur (non stylisées), utiliser :

```tsx
<form onSubmit={handleSubmit} noValidate>
  <input type="text" ... /> {/* pas type="email" */}
</form>
```

### Validation JavaScript

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Validation email custom
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(formData.email)) {
    setError(t('users.invalidEmail'));
    return;
  }

  // ... suite du traitement
};
```

### Avantages

| Aspect | Natif | Custom |
|--------|-------|--------|
| **Style** | Bulle OS non stylisable | InlineMessage stylisé |
| **Position** | Sous le champ | Où vous voulez |
| **i18n** | Langue du navigateur | Traduit via t() |
| **UX** | Bloque la soumission | Message inline contextuel |

---

## Barre de Recherche (SearchInput)

Convention de style uniforme pour toutes les barres de recherche du dashboard.

### Structure standard

```tsx
<div className="relative flex-1">
  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" />
  <input
    type="text"
    value={search}
    onChange={(e) => setSearch(e.target.value)}
    placeholder={t('common.search')}
    className="w-full pl-10 pr-4 py-2 text-sm bg-white/5 border border-white/10 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500/50 focus:ring-2 focus:ring-brand-500/10 transition-all"
  />
  {search && (
    <button
      onClick={() => setSearch('')}
      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
    >
      <X className="w-4 h-4" />
    </button>
  )}
</div>
```

### Classes CSS obligatoires

| Élément | Classes |
|---------|---------|
| **Container** | `relative flex-1` |
| **Icône Search** | `absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500` |
| **Input** | `w-full pl-10 pr-4 py-2 text-sm bg-white/5 border border-white/10 rounded-xl text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-500/50 focus:ring-2 focus:ring-brand-500/10 transition-all` |
| **Bouton clear (X)** | `absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200` |

### Pages utilisant ce pattern

| Page | Fichier |
|------|---------|
| Machines | `machines/page.tsx` |
| Certificats | `admin/certificates/page.tsx` |
| Activité | `admin/activity/page.tsx` |
| Logs Docker | `admin/docker/[id]/logs/page.tsx` |
| ChannelManager | `components/ChannelManager.tsx` |
| UsersTab | `machines/[hostname]/tabs/UsersTab.tsx` |
| NetworkTab | `machines/[hostname]/tabs/NetworkTab.tsx` |
| SoftwareTab | `machines/[hostname]/tabs/SoftwareTab.tsx` |
| ServicesTab | `machines/[hostname]/tabs/ServicesTab.tsx` |

---

## EmptyState

Composant partagé pour afficher un état vide (aucune donnée) ou un message d'erreur/accès refusé.

### Import

```tsx
import EmptyState from '@/components/EmptyState';
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `icon` | `LucideIcon` | requis | Icône à afficher |
| `title` | `string` | - | Titre principal (optionnel) |
| `description` | `string` | - | Description (optionnel) |
| `variant` | `'empty' \| 'error' \| 'denied'` | `'empty'` | Variante de couleur |
| `cardStyle` | `'neon' \| 'static'` | `'neon'` | Style de card |

### Variantes

| Variant | Couleur icône | Usage |
|---------|---------------|-------|
| `empty` | `text-slate-400` | Aucune donnée |
| `error` | `text-red-400` | Erreur API |
| `denied` | `text-red-400` | Accès refusé |

### Exemples

```tsx
// État vide simple
<EmptyState
  icon={Container}
  title={t('admin.docker.noContainers')}
  description={t('admin.docker.noContainersDesc')}
/>

// Accès refusé
<EmptyState
  icon={Shield}
  title={t('users.accessDenied')}
  description={t('users.adminOnly')}
  variant="denied"
  cardStyle="static"
/>

// Sans titre (description seule)
<EmptyState
  icon={KeyRound}
  description={t('cert.noCertificates')}
/>
```

### Pages utilisant ce composant

| Page | Fichier |
|------|---------|
| Docker | `admin/docker/page.tsx` |
| Users | `users/page.tsx` |
| Settings Users | `settings/users/page.tsx` |
| Collection Settings | `settings/collection/page.tsx` |
| Certificates | `admin/certificates/page.tsx` |

---

## Toggle Switch

Convention de style pour les boutons toggle (on/off) dans le dashboard.

### Couleurs standard

| État | Classe CSS |
|------|------------|
| **Activé** | `bg-green-500` |
| **Désactivé** | `bg-slate-300 dark:bg-slate-600` |

### Structure HTML

```tsx
<button
  type="button"
  onClick={() => setEnabled(!enabled)}
  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
    enabled ? 'bg-green-500' : 'bg-slate-300 dark:bg-slate-600'
  }`}
>
  <span
    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
      enabled ? 'translate-x-6' : 'translate-x-1'
    }`}
  />
</button>
```

### Fichiers utilisant des toggles

| Fichier | Nombre | Usage |
|---------|--------|-------|
| `CollectionSettingsModal.tsx` | 2 | Activation collecteurs + config |
| `notifications/page.tsx` | 4 | Canaux + règles + modals |
| `SupportedVersions.tsx` | 3 | Filtres OS (Windows/Linux) |

---

## Composants Landing

Tous les composants landing utilisent le système i18n avec `useI18n()` et `t()` pour le support FR/EN.

| Composant | Description |
|-----------|-------------|
| `HeroSection.tsx` | Hero avec ECG animation, stats traduites |
| `FeaturesGrid.tsx` | Grille fonctionnalités 3D |
| `PricingCards.tsx` | Cartes tarifs (5 plans, layout 2 rangées) |
| `ContactForm.tsx` | Formulaire avec captcha |
| `GridBackground.tsx` | Particules interactives |
| `LandingHeader.tsx` | Header vitrine avec logo dual-render |
| `LandingFooter.tsx` | Footer vitrine |
| `HowItWorks.tsx` | Section fonctionnement |
| `Benefits.tsx` | Section avantages avec typewriter |
| `FAQAccordion.tsx` | FAQ accordéon |
| `MockupStack.tsx` | Carousel screenshots avec rotation auto (3s) |

### Plans Tarifaires (PricingCards.tsx)

**Layout 2 rangées :**
- Rangée 1 : Starter, Essentials, Pro (3 colonnes)
- Rangée 2 : Business, Enterprise (2 colonnes centrées, max-w-4xl)

| Plan | Prix | Machines | Couleur | Tagline |
|------|------|----------|---------|---------|
| Starter | 69€/mois | ≤25 | Bleu (`blue-500`) | "Voir clair" |
| Essentials | 149€/mois | ≤75 | Teal (`teal-500`) | "Prioriser" |
| Pro ⭐ | 269€/mois | ≤150 | Brand orange | "Anticiper" |
| Business | 549€/mois | ≤500 | Orange (`orange-500`) | "Piloter" |
| Enterprise | Sur devis | Illimité | Violet (`purple-500`) | "S'adapter" |

**Fonctionnalités UI :**
- Bordures neon animées (dark mode) : `neon-border-{blue,teal,orange,purple}`
- Badge "Recommandé" sur Pro (populaire)
- Affichage du nombre de machines sous le prix
- Sections "Non inclus" avec icônes X (upsell)
- Boutons CTA colorés par plan
- Effet 3D tilt au survol

**Clés i18n :** `pricing.{plan}.feature{N}`, `pricing.{plan}.notIncluded{N}`

---

## MachineDetailsSidebar

Composant de navigation verticale pour la page de détails machine.

| Fonctionnalité | Description |
|----------------|-------------|
| **Mode collapsé** | Icônes uniquement, état persisté dans localStorage |
| **Mode étendu** | Icônes + labels, largeur 224px |
| **Mobile drawer** | Slide-in depuis la gauche avec overlay |
| **Indicateurs** | Points colorés (rouge/jaune) pour alertes par onglet |

**Onglets avec indicateurs:**

| Onglet | Indicateur | Condition |
|--------|------------|-----------|
| Security | Jaune | Antivirus ou Firewall désactivé |
| Services | Rouge | Services en échec > 0 |
| Updates | Rouge | Reboot requis |
| Updates | Jaune | Mises à jour en attente > 0 |
| Certificate | Vert | Certificat valide (> 30 jours) |
| Certificate | Jaune | Certificat expire bientôt (7-30 jours) |
| Certificate | Orange | Certificat expire très bientôt (< 7 jours) |
| Certificate | Rouge | Certificat expiré ou révoqué |

---

## Badge Conformité OS (MachineCard)

Le composant `MachineCard` affiche un badge d'avertissement si la machine ne respecte pas les prérequis OS configurés dans `agent_requirements`.

| Condition | Badge | Couleur |
|-----------|-------|---------|
| `is_os_compliant === false` | "OS non supporté" | Rouge (red-100/red-400) |

**Affichage :**
- Icône `AlertTriangle` + texte (desktop) ou icône seule (mobile)
- Tooltip avec message explicatif complet
- Position : ligne 3 avec les autres badges (VM, labels, groupe, maintenance)

---

## Composants Onglets Machine (Lazy-loaded)

**Dossier:** `dashboard/app/dashboard/machines/[hostname]/tabs/`

Les onglets sont chargés à la demande via `next/dynamic` pour les performances.

| Composant | Description |
|-----------|-------------|
| `SecurityTab.tsx` | Antivirus, Firewall, BitLocker avec version |
| `ServicesTab.tsx` | Statistiques + tableau services critiques |
| `SoftwareTab.tsx` | Tableau logiciels |
| `UsersTab.tsx` | Tableau utilisateurs avec badges Admin/User |
| `NetworkTab.tsx` | Tableau ports ouverts avec flag risqué |
| `UpdatesTab.tsx` | Mises à jour en attente, reboot requis |
| `CertificateTab.tsx` | Certificat mTLS : statut, serial, dates, actions admin |

**Import lazy:**
```typescript
const SecurityTab = dynamic(() => import('./tabs/SecurityTab'), { ssr: false });
```

---

## Données Inventaire (JSONB)

| Colonne | Type | Description |
|---------|------|-------------|
| `software_details` | JSONB | Liste complète des logiciels installés |
| `users_details` | JSONB | Liste des utilisateurs locaux |
| `all_ports` | JSONB | Tous les ports en écoute |
| `antivirus_version` | TEXT | Version des signatures antivirus |

**Types TypeScript:**

```typescript
interface SoftwareInfo {
  name: string;
  version: string;
  publisher?: string;
  install_date?: string;
}

interface LocalUser {
  username: string;
  full_name?: string;
  enabled: boolean;
  is_admin: boolean;
  last_logon?: string;
}

interface ListeningPort {
  protocol: string;
  local_port: number;
  process_name?: string;
  pid?: number;
  is_risky: boolean;
}
```

---

## Système d'Internationalisation (i18n)

**Fichier principal:** `dashboard/lib/i18n.tsx`

### Pages traduites

| Section | Pages |
|---------|-------|
| **Landing** | Home, Features, Pricing, FAQ, About, Contact |
| **Dashboard** | Overview, Machines, Settings, Installation |
| **Documentation** | Quick Install, System Requirements, FAQ |
| **Composants** | ContactForm, FeaturesGrid, Header, Sidebar |

### Structure des clés

```typescript
const translations: Record<string, { fr: string; en: string }> = {
  'nav.overview': { fr: 'Vue d\'ensemble', en: 'Overview' },
  'landing.features.title': { fr: 'Fonctionnalités', en: 'Features' },
  'overview.machine': { fr: 'machine', en: 'machine' },
  // ...
};
```

### Utilisation

```tsx
import { useI18n } from '@/lib/i18n';

function MyComponent() {
  const { t, language, setLanguage } = useI18n();
  return <h1>{t('nav.overview')}</h1>;
}
```

### Fonctionnalités avancées

| Fonctionnalité | Description |
|----------------|-------------|
| **Pluralisation** | Gestion singulier/pluriel |
| **Formatage dates** | `formatTimeAgo()` selon la langue |
| **TypewriterText** | Textes séparés par `\|` |
| **Persistance** | Langue stockée dans localStorage |

---

## Améliorations UX/UI

### Page Installation - mTLS uniquement

**Sections affichées :**

| Section | Description |
|---------|-------------|
| **Version actuelle** | Affiche les versions Windows, Linux x64 et ARM64 |
| **Installeur personnalisé** | Boutons de téléchargement mTLS (Windows EXE, Linux scripts) |
| **Mise à jour** | Instructions de mise à jour par plateforme |
| **Désinstallation** | Instructions de désinstallation |

**Supprimé (legacy) :**
- Section "Clé Agent" - remplacé par certificats mTLS
- Section "Installation classique" - remplacé par installeurs personnalisés

**Token Windows (déploiement masse) :**

| Élément | Description |
|---------|-------------|
| **Sélecteur machines** | 1 / 10 / 50 / Illimité |
| **Barre de progression** | Affiche X/N machines installées |
| **Countdown** | Temps restant (24h) avec format `Xh XXmin` |
| **Bouton révoquer** | Invalide le token immédiatement |

**Comportement technique :**
- Le token est chargé **après authentification** (dépendance `[user]` dans useEffect)
- Le token persiste après refresh de page
- **Télécharger un nouvel EXE révoque automatiquement l'ancien token** (un seul EXE actif à la fois)
- Chaque machine reçoit son propre certificat mTLS unique via API bootstrap
- Le token expire après 24h ou quand `usage_count >= max_usage`

### Page Documentation - Bannière mTLS

La page `/dashboard/documentation` affiche une bannière recommandant l'installation via mTLS avec un lien vers la page Installation.

```tsx
<Link href="/dashboard/installation">
  {t('installation.goToInstallation')}
</Link>
```

### Modal Création Client (Admin)

**Après création d'un client :**
- Affiche uniquement le **mot de passe admin**
- Plus d'affichage de clé agent (supprimé)

Les agents s'authentifient désormais via certificats mTLS générés lors du téléchargement de l'installeur.

### Page Notifications - Architecture Simplifiée

**Structure en 2 sections :**

| Section | Description |
|---------|-------------|
| **Canaux** | Vue compacte avec chips colorés par type (Email, Teams, Slack, Discord) |
| **Règles** | Liste détaillée des règles d'alerte avec toute la configuration |

**Section Canaux (compact) :**
- Chips colorés : Email (bleu), Teams (violet), Slack (vert), Discord (indigo)
- Badge avec nombre de canaux par type
- Dropdown au hover pour gérer les canaux du type
- Actions : activer/désactiver, supprimer, tester
- Modal simplifié : type + nom + config (emails ou webhook_url)

**Section Règles (détaillée) :**
- Liste avec cards pour chaque règle
- Affichage : nom, métrique, opérateur, seuil, sévérité, cooldown, scope, canaux
- Modal complet : tous les paramètres + multi-sélection des canaux de destination
- Actions : éditer, supprimer, activer/désactiver

### Mobile Responsive

| Composant | Adaptation Mobile |
|-----------|-------------------|
| ClientList | Vue cartes avec `md:hidden`, cards expandables |
| LicenseOverview | Vue cartes avec grille d'infos |
| ActivityPage | Filtres en grille 2 colonnes |
| Tableaux | Colonnes masquées (`hidden sm:table-cell`) |

---

## Thème Glassmorphism

### Couleurs Custom

```css
/* Palette Navy */
navy-50: #f0f7ff
navy-100: #e0efff
navy-900: #0b1929
navy-950: #071019

/* Palette Brand */
brand-50: #fff7ed
brand-500: #f97316
brand-600: #ea580c
```

### Classes Glassmorphism

```css
/* Effet verre */
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Mode sombre */
.dark .glass {
  background: rgba(0, 0, 0, 0.3);
}
```

---

## Pages Structure

### Site Vitrine (publiques)

| Route | Description |
|-------|-------------|
| `/` | Accueil avec hero, fonctionnalités, CTA |
| `/features` | Fonctionnalités détaillées |
| `/pricing` | Tarifs et plans |
| `/about` | À propos de 2 LACS IT |
| `/contact` | Formulaire de contact |
| `/faq` | Questions fréquentes |
| `/legal` | Mentions légales |
| `/privacy` | Politique de confidentialité |
| `/status` | Page de statut système publique |

### Dashboard (authentifiées)

| Route | Description |
|-------|-------------|
| `/dashboard/login` | Connexion (avec support MFA) |
| `/dashboard/overview` | Vue d'ensemble du parc |
| `/dashboard/machines` | Liste des machines (avec export CSV) |
| `/dashboard/machines/[hostname]` | Détails d'une machine |
| `/dashboard/settings` | Paramètres utilisateur |
| `/dashboard/settings/collection` | Configuration intervalles (admin) |
| `/dashboard/settings/notifications` | Canaux (destinations) et règles d'alerte |
| `/dashboard/users` | Gestion des utilisateurs (admin) |
| `/dashboard/status` | Page de statut système |

### Admin (super admin)

| Route | Description |
|-------|-------------|
| `/dashboard/admin/dashboard` | Statistiques admin |
| `/dashboard/admin/clients` | Gestion des clients |
| `/dashboard/admin/licenses` | Vue globale des licences |
| `/dashboard/admin/licenses/types` | Types de licences |
| `/dashboard/admin/updates` | Versions agents et canaux |
| `/dashboard/admin/docker` | Monitoring des containers |
| `/dashboard/admin/activity` | Journal d'activité système |
| `/dashboard/admin/certificates` | Gestion des certificats mTLS (tous clients) |

---

## Optimisations Performance

| Optimisation | Description |
|--------------|-------------|
| **App Router** | Next.js 14 avec Server Components |
| **Image Optimization** | next/image avec lazy loading |
| **Code Splitting** | Chunks automatiques par page |
| **Static Generation** | Pages landing pré-générées |
| **Lazy Loading Tabs** | Onglets chargés à la demande |

---

## Sécurité Frontend

### Protection XSS

- **DOMPurify** : Sanitization sur tout contenu injecté
- **Fichier** : `dashboard/lib/sanitize.ts`
- **Usage** : `<div dangerouslySetInnerHTML={{ __html: sanitizeHtml(content) }} />`

### Timeout Requêtes

- **Timeout** : 30 secondes par défaut
- **AbortController** : Annulation propre des requêtes
- **Fichier** : `dashboard/lib/api.ts`

---

## Hooks Personnalisés

| Hook | Description | Fichier |
|------|-------------|---------|
| `useAuth` | Authentification et impersonation | `lib/auth.tsx` |
| `useI18n` | Internationalisation | `lib/i18n.tsx` |
| `useTheme` | Thème dark/light | `lib/theme.tsx` |
| `useAutoLogout` | Déconnexion auto après inactivité | `lib/useAutoLogout.ts` |
| `usePasswordValidation` | Validation mot de passe | `lib/passwordValidation.ts` |
| `useInlineMessage` | Messages contextuels inline | `components/InlineMessage.tsx` |

---

## Authentification

### Mécanisme de session

Le dashboard utilise un système d'authentification basé sur des cookies HttpOnly :

| Élément | Description |
|---------|-------------|
| **Access Token** | JWT valide 15 minutes, stocké en cookie HttpOnly |
| **Refresh Token** | Token opaque valide 7 jours, cookie HttpOnly sur `/api/auth` |
| **CSRF Token** | Cookie lisible par JavaScript pour protection CSRF |

### Configuration fetch

Toutes les requêtes API authentifiées utilisent `credentials: 'include'` pour envoyer automatiquement les cookies HttpOnly :

```typescript
fetch(url, {
  ...options,
  credentials: 'include', // Envoie les cookies HttpOnly
});
```

### Persistance de session

- Au chargement de page, `getMe()` est toujours appelé (les cookies peuvent être valides même sans token en mémoire)
- Le refresh automatique se déclenche sur 401, indépendamment de l'état mémoire
- Les sessions persistent après rechargement de page grâce aux cookies

---

## Liens

- [Index des spécifications](README.md)
- [Backend API](BACKEND_SPECS.md)
- [Base de données](DATABASE_SPECS.md)
