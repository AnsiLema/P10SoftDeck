Voici le fichier `README.md` mis à jour selon tes demandes :

```markdown
# 📌 Projet Django REST API

Ce projet est une API REST basée sur Django et Django REST Framework (DRF) qui permet la gestion de projets, de contributeurs, de problèmes (issues) et de commentaires.

---
```

## 📦 Installation et Configuration


---

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/AnsiLema/P10SoftDeck.git
cd P10SoftDeck
```

---

### 2️⃣ Créer un environnement virtuel

Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.

```bash
python -m venv env
source env/bin/activate  # Sur macOS/Linux
env\Scripts\activate     # Sur Windows
```

---

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```


---

### 4️⃣ Configuration de la base de données (SQLite)

Ce projet utilise **SQLite 3** comme base de données par défaut. Aucune configuration supplémentaire n'est requise.

Appliquez simplement les migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Lancer le serveur

```bash
cd SoftDeck/
python manage.py runserver
```

L'API est maintenant accessible à l'adresse : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔑 Authentification

L'API utilise JSON Web Tokens (JWT) pour l'authentification.

### 🔹 Obtenir un token JWT

Effectuez une requête POST à :

```
POST /login/
```

Avec les identifiants d'un utilisateur enregistré :

```json
{
  "username": "admin",
  "password": "motdepasse"
}
```

Vous recevrez un token JWT en réponse :

```json
{
  "refresh": "token_refresh",
  "access": "token_access"
}
```
Copiez le token access.
Ajoutez ce token dans l’en-tête de vos requêtes :

```
Authorization: Bearer <votre_token_access>
```

---

## 📌 Endpoints de l'API

### 🔹 Gestion des utilisateurs

| Méthode | Endpoint            | Description                         |
|---------|---------------------|-------------------------------------|
| `POST`  | `/register/`        | Inscription d'un utilisateur       |
| `GET`   | `/users/`           | Liste des utilisateurs             |
| `GET`   | `/users/<id>/`      | Détails d'un utilisateur           |
| `PATCH` | `/users/<id>/`      | Modifier un utilisateur            |
| `DELETE`| `/users/<id>/`      | Supprimer un utilisateur           |

---

### 🔹 Gestion des projets

| Méthode | Endpoint                     | Description                             |
|---------|------------------------------|-----------------------------------------|
| `GET`   | `/projects/`                 | Liste des projets                      |
| `POST`  | `/projects/`                 | Créer un projet                        |
| `GET`   | `/projects/<id>/`            | Détails d'un projet                    |
| `PATCH` | `/projects/<id>/`            | Modifier un projet                     |
| `DELETE`| `/projects/<id>/`            | Supprimer un projet                    |

---

### 🔹 Gestion des contributeurs

| Méthode | Endpoint                                       | Description                          |
|---------|----------------------------------------------|--------------------------------------|
| `GET`   | `/projects/<project_id>/contributors/`      | Liste des contributeurs du projet  |
| `POST`  | `/projects/<project_id>/contributors/`      | Ajouter un contributeur            |
| `DELETE`| `/projects/<project_id>/contributors/<id>/` | Supprimer un contributeur          |

---

### 🔹 Gestion des issues

| Méthode | Endpoint                                | Description                    |
|---------|-----------------------------------------|--------------------------------|
| `GET`   | `/projects/<project_id>/issues/`       | Liste des issues d'un projet  |
| `POST`  | `/projects/<project_id>/issues/`       | Ajouter une issue             |
| `GET`   | `/projects/<project_id>/issues/<id>/`  | Détails d'une issue           |
| `PATCH` | `/projects/<project_id>/issues/<id>/`  | Modifier une issue            |
| `DELETE`| `/projects/<project_id>/issues/<id>/`  | Supprimer une issue           |

---

### 🔹 Gestion des commentaires

| Méthode | Endpoint                                                   | Description                     |
|---------|------------------------------------------------------------|---------------------------------|
| `GET`   | `/projects/<project_id>/issues/<issue_id>/comments/`       | Liste des commentaires         |
| `POST`  | `/projects/<project_id>/issues/<issue_id>/comments/`       | Ajouter un commentaire         |
| `GET`   | `/projects/<project_id>/issues/<issue_id>/comments/<id>/`  | Détails d'un commentaire       |
| `PATCH` | `/projects/<project_id>/issues/<issue_id>/comments/<id>/`  | Modifier un commentaire        |
| `DELETE`| `/projects/<project_id>/issues/<issue_id>/comments/<id>/`  | Supprimer un commentaire       |

---

## 📌 Technologies utilisées

- **Django** : Framework web pour le backend.
- **Django REST Framework** : Pour créer des API RESTful.
- **SQLite 3** : Base de données utilisée dans ce projet.
- **JWT (JSON Web Token)** : Pour l'authentification.

---

## 📩 Contact

Si vous avez des questions ou des suggestions, n'hésitez pas à m'envoyer un email : ansilema@gmail.com ! 🚀

