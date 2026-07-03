---
title: Personnaliser l'apparence de votre blog
date: 2026-02-10
summary: Thème clair/sombre automatique, logo, favicon et pages statiques ; tout ce qui s'ajuste sans toucher au code Python.
category: Personnalisation
meta_description: Comment personnaliser Journal (thème clair et sombre automatique, logo, favicon et ajout de pages statiques comme une page À propos).
keywords: personnalisation blog, thème sombre, logo svg, page à propos
image: imgs/hierarchie.svg
---

Le code de Journal n'a pas besoin d'être modifié pour adapter le blog à son identité. La plupart des ajustements se font en remplaçant un fichier ou en ajoutant un dossier.

## Le thème suit vos visiteurs

Le site s'affiche en clair ou en sombre selon la préférence système du visiteur, sans configuration. Un bouton permet aussi de forcer manuellement un thème : le choix est alors mémorisé pour ses prochaines visites.

## Changer le logo et l'icône

Deux fichiers SVG suffisent :

- `static/img/logo.svg` : le logo affiché dans l'en-tête.
- `static/img/favicon.svg` : l'icône affichée dans l'onglet du navigateur.

Ce sont de simples fichiers texte : remplacez-les par vos propres SVG (même nom), ou éditez-les directement.

## Ajouter une page statique

Une page « À propos », « Contact » ou autre suit la même logique qu'un article, mais sans date ni catégorie, dans `pages/` :

```markdown
---
title: À propos
meta_description: Une description optimisée pour les moteurs de recherche.
---

Le contenu de la page, en Markdown.
```

La page est servie à la racine du site (`pages/about/` devient `/about`) et apparaît automatiquement dans `/sitemap.xml`. Elle n'est en revanche pas ajoutée automatiquement à la navigation : un lien manuel dans `templates/base.html` s'en charge, comme celui déjà en place vers `/about`.
