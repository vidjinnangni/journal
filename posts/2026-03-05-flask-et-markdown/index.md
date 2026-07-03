---
title: Référencer et mettre son blog en ligne
date: 2026-03-05
summary: Renseigner quelques champs de frontmatter suffit pour un bon référencement. Ensuite, un simple gunicorn suffit à déployer.
category: Mise en ligne
meta_description: Optimiser le référencement de vos articles et déployer votre blog Journal en production avec gunicorn, sitemap et robots.txt automatiques.
keywords: seo blog, déploiement flask, gunicorn, sitemap xml
---

Une fois les premiers articles écrits, deux questions se posent naturellement : seront-ils bien référencés, et comment mettre le site en ligne ?

## Le référencement, en trois champs

Trois champs optionnels du frontmatter affinent le référencement de chaque article :

```markdown
---
title: Mon nouvel article
date: 2026-04-01
summary: Une courte description.
meta_description: Une description optimisée (150-160 caractères).
keywords: mot-clé un, mot-clé deux
image: imgs/mon-image.jpg
---
```

`meta_description` alimente la balise description ainsi que les balises Open Graph et Twitter Card ; à défaut, `summary` prend le relais. `image` sert à la fois d'image de partage sur les réseaux sociaux et de vignette dans la liste des articles.

## Sitemap et robots.txt automatiques

Pas de configuration à écrire : `/sitemap.xml` et `/robots.txt` sont générés automatiquement à partir des articles et pages existants, à chaque requête.

## Déployer

Le site est une application Flask standard. En production, on la sert derrière un serveur comme `gunicorn` plutôt qu'avec `python app.py` :

```bash
pip install gunicorn
gunicorn app:app
```

Elle peut ensuite être déployée telle quelle sur Render, Railway, Fly.io, PythonAnywhere, ou tout hébergeur qui supporte une application WSGI Python.
