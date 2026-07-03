---
title: Bien démarrer avec Journal
date: 2026-01-15
summary: Pas de base de données, pas de back-office. Chaque article est un simple dossier. Voici comment écrire et publier le vôtre.
category: Guide
meta_description: Comment démarrer avec Journal, un blog Flask minimaliste sans base de données (structure des articles, frontmatter et première publication).
keywords: tutoriel blog flask, markdown, frontmatter, guide de démarrage
---

Ce blog ne repose sur aucune base de données ni interface d'administration. Chaque article est un simple fichier Markdown, lu directement depuis le disque à chaque visite. Pas de compte à créer, pas de tableau de bord à apprendre : juste des fichiers texte.

## Un article, un dossier

Un article vit dans son propre dossier, sous `posts/` :

```text
posts/2026-04-01-mon-article/
  index.md
  imgs/
    photo.jpg
```

Le nom du dossier n'a pas d'importance pour l'URL. C'est seulement le contenu du fichier `index.md` qui compte.

## Le frontmatter minimal

En haut du fichier, un bloc `---` délimite quelques informations sur l'article :

```markdown
---
title: Mon nouvel article
date: 2026-04-01
summary: Une courte description qui apparaît dans la liste des articles.
---

Le contenu de l'article, en Markdown : titres, listes, code, citations...
```

`title`, `date` et `summary` suffisent pour commencer. D'autres champs optionnels (catégorie, image, référencement) viennent s'ajouter au fur et à mesure des besoins.

## Publier

Aucune étape supplémentaire : le fichier ajouté apparaît automatiquement sur la page d'accueil, trié par date décroissante. En développement, il suffit de rafraîchir la page ; en production, un redéploiement suffit.

> Le moins d'outils possible entre l'idée et la publication.
