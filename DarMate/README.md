# DarMate — Backend (API FastAPI + MySQL 8)

Plateforme immobilière : logements, colocation (binômes, groupes), demandes de location, visites, messagerie temps réel,
notifications, avis, administration.

## Contenu
- `backend/` : API FastAPI en Clean Architecture (domain / application / infrastructure / presentation), 57 tests pytest.
- `database/` : `init.sql` (création base + utilisateur), `schema.sql` (DDL MySQL complet, généré depuis la migration Alembic).
- `docs/` : `erd.md` (diagramme ERD), `data-dictionary.md` (33 tables).
- Le frontend Angular n'est **pas** inclus : il n'est pas terminé.

## Installation
1. **MySQL 8** : installez-le, puis `mysql -u root -p < database/init.sql` (changez le mot de passe dans le fichier).
2. **Backend** :
```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # renseigner DB_PASSWORD, JWT_SECRET_KEY, ADMIN_PASSWORD
alembic upgrade head      # crée les tables (ou importez database/schema.sql)
python -m app.scripts.seed   # rôles, catégories, régions/villes de Tunisie, pondérations, compte admin
uvicorn app.main:app --reload
```
API : http://localhost:8000/api/v1 — Swagger : http://localhost:8000/docs

## Tests
```bash
cd backend && pytest        # utilise SQLite temporaire, aucune base MySQL requise
```
Les tests couvrent authentification (rotation du refresh token, verrouillage), permissions/IDOR, annonces, uploads,
demandes de location, groupes, visites, messagerie, WebSocket, administration.

## Points de sécurité
Argon2id, JWT 15 min en mémoire + refresh token opaque en cookie HttpOnly (rotation + détection de réutilisation),
verrouillage de compte, rate limiting (slowapi), CORS restrictif, validation Pydantic, vérification MIME + signature + taille
des fichiers, fichiers privés (identité, pièces jointes) jamais servis statiquement, anti-IDOR (404 sur ressources d'autrui),
journal d'audit, erreurs sans fuite d'informations internes.
**Production** : `ENVIRONMENT=production`, `COOKIE_SECURE=true`, HTTPS, front et API sur le même domaine enregistrable (cookie SameSite=Strict).

## Limites connues
- Testé sur SQLite ; le DDL MySQL est généré mais **n'a pas été exécuté sur un serveur MySQL** : lancez `alembic upgrade head` et signalez toute erreur.
- L'envoi d'e-mails est simulé (journal) : `ConsoleEmailSender` à remplacer par SMTP.
- La vérification d'identité n'a pas d'écran de validation côté admin (téléversement + téléchargement sécurisé seulement).
- Alertes de recherche : notification interne à la publication (pas d'e-mail).
