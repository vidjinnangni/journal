---
title: Construire le menu de navigation et les liens du footer
date: 2026-05-10
summary: Les liens du menu et les réseaux sociaux du footer ne sont pas générés automatiquement. Ils sont dans les templates/base.html.
category: Personnalisation
meta_description: Comment ajouter des liens au menu de navigation et remplacer les réseaux sociaux du footer dans templates/base.html.
keywords: menu navigation flask, footer, réseaux sociaux, templates jinja
---

Les pages statiques apparaissent automatiquement dans `/sitemap.xml`, mais pas dans le menu du site : contrairement aux articles, la navigation ne se déduit pas du contenu des dossiers. Elle est écrite à la main dans `templates/base.html`.

## Ajouter un lien au menu

Le menu se trouve dans le bloc `nav-links` :

```html
<div class="nav-links">
  <a href="{{ url_for('index') }}">Articles</a>
  <a href="{{ url_for('page', slug='about') }}">À propos</a>
  <!-- bouton de thème -->
</div>
```

Pour ajouter une page (par exemple `pages/contact/`), il suffit d'insérer une ligne similaire avant le bouton de thème :

```html
<a href="{{ url_for('page', slug='contact') }}">Contact</a>
```

Un lien par page à ajouter. L'ordre d'affichage suit celui du code.

## Remplacer les réseaux sociaux du footer

Le footer contient quatre icônes (GitHub, X, LinkedIn, Instagram), chacune avec un `href="#"` provisoire. Il suffit de remplacer ce `#` par la véritable URL du profil correspondant, et de supprimer les blocs `<a class="social-link">` des réseaux non utilisés.

## Le copyright s'ajuste tout seul

La ligne de copyright (`&copy; {{ site_name }}. Fait avec Flask & Markdown.`) réutilise directement `SITE_NAME`. Changer le nom du blog comme vu dans l'article précédent suffit à la mettre à jour partout, footer compris.
