---
title: Changer le titre et le sous-titre du blog
date: 2026-04-02
summary: Le nom du site et sa description courte ne sont pas dans le frontmatter, mais dans deux constantes en haut de app.py.
category: Personnalisation
meta_description: Comment modifier le titre (SITE_NAME) et le sous-titre (SITE_TAGLINE) de Journal, utilisés dans l'en-tête, le référencement et le footer.
keywords: nom du blog, sous-titre, site_name, personnalisation flask
---

Contrairement au contenu des articles, l'identité du site (son nom et sa courte description) n'est pas un fichier Markdown. Elle est définie une seule fois, en haut de `app.py` :

```python
SITE_NAME = "Journal"
SITE_TAGLINE = "Notes sur le design, le code et les idées."
```

Il suffit de remplacer ces deux valeurs par les vôtres.

## Où ces valeurs apparaissent

Ces deux constantes sont injectées automatiquement dans tous les templates, et réutilisées à plusieurs endroits :

- Le texte alternatif du logo dans l'en-tête.
- Le titre `<title>` des pages qui ne définissent pas le leur.
- La description par défaut (balise `meta description`, Open Graph, Twitter Card) quand un article ou une page ne précise pas `meta_description`.
- Le sous-titre affiché sous le titre sur la page d'accueil.
- La mention de copyright en bas de page.

Un seul changement se répercute donc partout, sans avoir à modifier chaque template un par un.

## Voir le changement

`app.py` n'est pas un template : il n'est relu automatiquement que si le serveur tourne avec le rechargeur activé (`FLASK_DEBUG=1`). Sans cette variable, un redémarrage manuel du serveur est nécessaire après modification.
