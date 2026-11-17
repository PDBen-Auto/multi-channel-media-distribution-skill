# Diffusion média coordonnée

[简体中文](README.zh-CN.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Español](README.es.md) | [Português](README.pt.md)

Utiliser la langue explicitement demandée, sinon celle de la demande. Conserver les commandes, identifiants de Skill, clés JSON, valeurs d’énumération, unités et citations originales. Distinguer traduction et original. Ne déduire ni pays, ni devise, ni juridiction de la langue. Lire les références détaillées utiles et maintenir tous les contrôles et autorisations existants.

## Installation et utilisation

Télécharger ou cloner le dépôt, puis copier le répertoire du Skill indiqué, avec ses references, scripts, assets et autres dépendances existantes, dans le répertoire de Skills de l’hôte. Conserver son nom et SKILL.md. Changer la langue de documentation ne demande pas de nouvelle installation. Les commandes proposées ne prouvent ni installation ni activation.

```sh
git clone https://github.com/PDBen-Auto/multi-channel-media-distribution-skill.git
```

## Diffusion média coordonnée

`multi-channel-media-distribution`

Adapter une campagne vérifiée à Facebook, Reddit, TikTok, YouTube, X, Instagram et LinkedIn selon les seuls canaux et l’ordre choisis.

Répertoire du Skill: `.`

**Fondements et dépendances**

Agent, preuves, médias autorisés et écriture locale. Python 3.10+ pour utilitaires ; outils média/FFmpeg et règles actuelles selon besoin. Actions en ligne : compte vérifié, connexion et autorisation précise.

**Entrées**

Brief audience/objectif/langue/CTA/ordre, droits des médias, permissions édition/soumission par canal, destination/visibilité/règles et historique. Par défaut, aucune écriture externe.

**Sorties**

Sous input/work/output : preuves et médias réels communs, textes par canal, revue/transfert, journal d’exécution et rapport Markdown/HTML autonome transportable.

[Déroulement · Limites et conditions d’arrêt · Exemple de demande](references/i18n/fr.md)

> Utilise `$multi-channel-media-distribution` — Préparer sept dossiers anglais à partir de faits vérifiés, ouvrir les éditeurs successivement et réserver l’envoi final à l’utilisateur ; réponds en français en conservant les preuves, les inconnues et les limites d’autorisation.

## Couverture linguistique et validation

Ce guide localisé couvre objectif, prérequis, entrées, sorties, étapes, exemples et limites. Il ne traduit pas chaque référence ligne par ligne. Les références techniques détaillées, cas historiques, erreurs de scripts, interfaces d’exemple et images restent dans leur langue originale et peuvent être expliqués à la demande. Structure, liens et contraintes essentielles sont vérifiés ; aucune relecture par un locuteur natif de chaque langue n’est revendiquée.

Avant livraison, rapprocher entrées, preuves, valeurs manquantes, fichiers et critères d’achèvement d’origine. Marquer les étapes non exécutées comme non vérifiées ; la réussite d’un script ne valide pas une conclusion métier.
