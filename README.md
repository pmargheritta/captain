# Captain

Captain est un bot IRC de divertissement. Sa principale caractéristique est de s'exprimer avec le [langage du capitaine Haddock](https://fr.wikipedia.org/wiki/Vocabulaire_du_capitaine_Haddock).

Le bot utilise le [module `irc` de Python](https://github.com/jaraco/irc). Captain a été écrit en Python 2 sous le nom de Pinpin, probablement autour de 2010, et a été adapté en Python 3 en 2016. Le bot est fonctionnel mais son code est largement améliorable.

## Fonctionnement général

Captain charge la configuration décrite dans `params.json` et s'en sert pour se connecter à un serveur IRC et rejoindre un canal. Une instance du bot ne peut être présente que sur un seul canal IRC à la fois.

Les événements liés au bot sont journalisés de manière exhaustive dans un fichier `log`.

## Réactions et interventions

Une fois présent sur un canal, le bot reconnaît divers événements et y réagit par des insultes tirées du vocabulaire du capitaine Haddock. Il intervient notamment :
* à son arrivée sur un canal ;
* lors de la désactivation du mode silencieux ;
* à la détection d'un smiley ;
* à la détection d'une action (commande IRC `/me`) ;
* lorsque son nom est mentionné sur le canal.

## Commandes du bot

Captain peut recevoir des commandes de la manière suivante (entre autres) : `Captain: <commande> <arguments>`.

Parmi les commandes disponibles, on trouve :
* `silence` : active le mode silencieux ;
* `parle` : désactive le mode silencieux ;
* `insulte <utilisateur>` : envoie une insulte privée à l'utilisateur donné ;
* `dictée <n>` : lance une dictée de `n` mots ;
* `rappel` : rappelle le dernier mot de la dictée ;
* `stop` : arrête la dictée en cours ;
* `charge` : recharge les paramètres après modification ;
* `sors` : demande au bot de quitter le canal ;
* `meurs` : tue le bot (réservé au propriétaire du bot).

## Invitation et exclusion

Si Captain est invité sur un canal par la commande IRC `/invite`, il quitte le canal actuellement occupé et rejoint automatiquement ce nouveau canal.

Captain rejoint automatiquement un canal duquel il est explusé par la commande IRC `/kick`.

## Mode silencieux

En mode silencieux, Captain n'intervient plus spontanément. Il est en revanche toujours actif s'il est explicitement sollicité (insulte privée, dictée...). En mode silencieux, un préfixe est automatiquement ajouté à son pseudo.

## Insulte privée

La fonctionnalité d'insulte privée, à utiliser avec prudence, envoie une insulte aléatoire par message privé à un utilisateur donné. L'insulte envoyée est consignée dans le journal `log`, ainsi que les réactions éventuelles des utilisateurs visés.

## Dictée

La dictée est le jeu proposé par Captain. Le bot propose aux utilisateurs d'écrire un mot souvent complexe. L'utilisateur ayant écrit le plus vite le mot demandé marque un point et le bot passe au mot suivant. Les scores sont affichés à la fin du jeu.

Le nombre de mots par défaut est 10.

## Contrôle du propriétaire

Le propriétaire peut demander dans le canal à Captain de se tuer. Une requête de ce type faite par un autre utilisateur que le propriétaire aboutit à une réaction énervée de Captain.

Il est également possible pour le propriétaire de pouvoir déclencher un message ou une action personnalisée de la part de Captain. Le bot reconnaît ses messages privées qui lui sont adressés par le propriétaire sous cette forme :
* `!msg <message>` fait écrire `<message>` dans le canal ;
* `!act <action>` fait exécuter l'action (`/me`) `<action>` dans le canal.
