# monbackofficeAPI

API back-office basée sur Django + Django REST Framework pour gérer plusieurs applications internes (mytig, myImageBank, monTiGMagasin). Le projet expose une API REST, une interface d'administration Django et des endpoints d'authentification JWT.

## Stack
- Langage : Python 3 (projet créé avec Django 3.1.4)
- Framework : Django + Django REST Framework
- Notable libs : djangorestframework, django-cors-headers, djangorestframework-simplejwt
- Base de données : SQLite (fichier `mySearchEngine/db.sqlite3` inclus)

## Structure du dépôt (fichiers et dossiers importants)
```
mySearchEngine/
  manage.py                     # point d'entrée Django (commandes manage)
  db.sqlite3                    # base SQLite (fichier présent dans le dépôt)
  mySearchEngine/                # projet Django (settings, urls, wsgi/asgi)
    settings.py                 # configuration (installed apps, JWT, CORS, SECRET_KEY)
    urls.py                     # routes principales (admin, apps, endpoints JWT)
    wsgi.py / asgi.py
  mytig/                        # application 'mytig' (routes, vues, modèles)
  myImageBank/                  # application 'myImageBank' (admin, views, urls, models)
  monTiGMagasin/                # application 'monTiGMagasin'
.gitignore
```

Comment ça s'articule : mySearchEngine/ est le projet Django qui inclut et routage les trois applications (mytig, myImageBank, monTiGMagasin). L'URLconf du projet inclut les urls de chaque app et expose aussi les endpoints JWT pour récupérer/rafraîchir les tokens.

## Fonctionnalités visibles (extraites du code)
- Authentification JWT via `rest_framework_simplejwt` :
  - POST `/api/token/` (obtenir pair access/refresh)
  - POST `/api/token/refresh/` (rafraîchir access)
- Interface d'administration Django : `/admin/`
- CORS autorisé pour toutes les origines (`CORS_ALLOW_ALL_ORIGINS = True` dans settings)
- Applications enregistrées dans `INSTALLED_APPS` : `mytig`, `myImageBank`, `monTiGMagasin`, plus `rest_framework`, `corsheaders`, etc.

## Exécution en local (rapide)
1. Créer et activer un environnement virtuel :
   ```
   python -m venv venv
   source venv/bin/activate    # macOS / Linux
   venv\Scripts\activate       # Windows
   ```
2. Installer dépendances (exemple des paquets requis) :
   ```
   pip install Django==3.1.4 djangorestframework django-cors-headers djangorestframework-simplejwt
   ```
   Si vous avez un fichier requirements.txt, faites `pip install -r requirements.txt`.
3. Migrer la base de données (ou utiliser le `db.sqlite3` fourni) :
   ```
   python mySearchEngine/manage.py migrate
   ```
   Si vous souhaitez repartir d'une DB propre, supprimez `mySearchEngine/db.sqlite3` avant `migrate`.
4. Créer un superutilisateur (optionnel, pour accéder à /admin/) :
   ```
   python mySearchEngine/manage.py createsuperuser
   ```
5. Lancer le serveur de développement :
   ```
   python mySearchEngine/manage.py runserver
   ```
6. Points d'accès utiles pendant le développement :
   - Admin : http://127.0.0.1:8000/admin/
   - Auth JWT : http://127.0.0.1:8000/api/token/ et /api/token/refresh/
   - Les routes des apps sont incluses à la racine via `include('<app>.urls')` (voir `mySearchEngine/mySearchEngine/urls.py`)

## Configuration recommandée / Sécurité
- Le fichier `mySearchEngine/mySearchEngine/settings.py` contient une clé `SECRET_KEY` et `DEBUG = True`. Ne laissez pas ces valeurs en production.
  - Recommander : lire la clé depuis une variable d'environnement (ex. `DJANGO_SECRET_KEY`) et définir `DEBUG=False`.
- Pour la production :
  - Configurer `ALLOWED_HOSTS`
  - Utiliser une base de données plus robuste (Postgres, etc.)
  - Désactiver `CORS_ALLOW_ALL_ORIGINS = True` ou restreindre les origines autorisées
  - Gérer correctement les certificats/HTTPS et settings de sécurité Django

## Suggestions / next steps
- Ajouter un fichier `requirements.txt` (ou pyproject/Poetry) listant les dépendances exactes.
- Ajouter un fichier `LICENSE` si projet destiné à être publié.
- Documenter les endpoints spécifiques des apps (mytig, myImageBank, monTiGMagasin) : exemples de requêtes, schémas JSON, permissions.
- Supprimer le fichier `db.sqlite3` du dépôt si la DB ne doit pas être versionnée, ou l'ignorer via `.gitignore`.

## Contribution
1. Fork & clone
2. Créer une branche feature/bugfix
3. Tester localement, ajouter migrations si nécessaire
4. Ouvrir une pull request décrivant le changement

## Questions utiles à poser
- Quelles routes et ressources fournissent `mytig`, `myImageBank` et `monTiGMagasin` (exemples d'URLs et schémas JSON) ?
- Voulez-vous que la clé SECRET_KEY soit lue depuis une variable d'environnement et que DEBUG soit mis à False par défaut en production ?
- Faut-il supprimer `db.sqlite3` du dépôt et fournir un script d'initialisation / fixtures pour peupler la base ?

---
