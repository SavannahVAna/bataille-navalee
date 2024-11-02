## Bataille navale

### important :

la version de python dans laquelle ce projet a été réalisé est python 3.11.9

Si vous avez des problèmes pour executer ce programme je vous conseille donc de switch sur cette version.

## mode d'emploi :

### server :

Pour lancer le serveur lancer le script gameserever
>python3 gameserever.py

Une fois lancé le script va attendre 3 connections avant de démarrer la partie.

### players :

il est recommandé de faire des copies des scripts gameclient et test dans différents répértoires (un par player) car des fichiers positions json seront crées par la suite

>mkdir 1 2 && cp gameclient.py test.py 1/ && cp gameclient.py test.py 2/

pour lancer une intance de joueur, lancer test

>python3 test.py

vous devriez voir une grille apparaitre pour placer vos bateaux

Une fois que tous les joueurs ont placé leur bateaux, la partie commence.

## Controls

### mode placement

apres avoir lancé le fichier test.py, une interface graphique apparait.

Votre bateau se trouve en haut a gauche au début de la phase de placement, vous pouvez le faire bouger en utilisant les flèches directionnelles, ainsi que le faire tourner en appuyant sur la touche T. Une fois que sa position vous convient, appuyez sur entrée pour le placer définitivement.

il vous faudra placer plusieurs bateaux :

- 2 bateaux de taille 2
- 1 bateau de taille 3
- 1 bateau de taille 4 
- 1 bateau de taille 5

Note : L'interface vous permet de superposer des bateaux car les collisions n'ont pas été implémentées. Cela peut cependant engendrer des bugs et il n'est pas recommandé de superposer vos bateaux, de plus c'est contre les règles officielles.

### mode combat

Lorsque la partie commence, chaque joueur va jouer tour par tour. Lorsque votre tour arrive une croix bleue s'affiche en haut de la grille de droite.

Vous pouvez la bouger avec les flèches directionnelles, puis appuyer sur entrée pour tirer.

Si vous touchez un bateau ennemi une croix rouge apparait a l'endroit ou vous avez tiré, sinon elle sera noire. Lorsque vous coulez un bateau, un message apparait dans la console.

### Règles

C'est un jeu tour par tour, si tous vos bateaux se font couler, vous perdez et la partie s'arrête pour vous. Le dernier en vie a gagné.



