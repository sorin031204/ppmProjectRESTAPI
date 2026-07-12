# E-commerce REST API

Studente: Sorin Andrei Enache

Tipo di progetto: REST API

Framework: Django REST Framework

## Descrizione

API REST per un e-commerce: catalogo prodotti/categorie, carrello, creazione ordini, gestione stato ordini. Ruoli: Customer e Store Manager.

## Funzionalità per ruolo

Pubblico: consultazione catalogo (prodotti, categorie).

Customer: login, gestione carrello (aggiunta/rimozione prodotti), creazione ordine dal carrello, visualizzazione propri ordini.

Store Manager: tutto quanto sopra, più creazione/modifica/eliminazione prodotti e categorie, visualizzazione di tutti gli ordini, aggiornamento stato ordine.

## Installazione locale

```bash
git clone https://github.com/sorin031204/ppmProjectRESTAPI.git
cd ppmProjectRESTAPI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API disponibile su `http://127.0.0.1:8000/`.

## Database demo

Il repository include `db.sqlite3` già popolato. Per ripopolarlo da zero:

```bash
python manage.py seed_data
```

## Account demo

- customer_demo / cust12345 - Customer
- manager_demo / manager12345 - Store Manager

## Deploy

`[LINK DA AGGIUNGERE]`

## Endpoint

Base URL locale: `http://127.0.0.1:8000`
Base URL deploy: `[DA AGGIUNGERE]`

### Autenticazione

POST `/api/auth/login/` - nessuna auth richiesta - tutti i ruoli
Request: `{"username": "customer_demo", "password": "cust12345"}`
Response: `{"token": "..."}`

### Categorie

GET `/api/categories/` - nessuna auth - tutti (lista)
GET `/api/categories/{id}/` - nessuna auth - tutti (dettaglio)
POST `/api/categories/` - auth richiesta - Store Manager
PUT/PATCH `/api/categories/{id}/` - auth richiesta - Store Manager
DELETE `/api/categories/{id}/` - auth richiesta - Store Manager

Request (POST/PUT): `{"name": "Elettronica", "description": "..."}`

### Prodotti

GET `/api/products/` - nessuna auth - tutti (lista)
GET `/api/products/{id}/` - nessuna auth - tutti (dettaglio)
POST `/api/products/` - auth richiesta - Store Manager
PUT/PATCH `/api/products/{id}/` - auth richiesta - Store Manager
DELETE `/api/products/{id}/` - auth richiesta - Store Manager

Request (POST/PUT): `{"name": "Tastiera", "description": "...", "price": "59.90", "stock": 15, "category": 1}`

### Carrello

GET `/api/cart/` - auth richiesta - Customer
POST `/api/cart/items/` - auth richiesta - Customer
DELETE `/api/cart/items/{item_id}/` - auth richiesta - Customer

Request (POST items): `{"product": 1, "quantity": 2}`

### Ordini

GET `/api/orders/` - auth richiesta - Customer (propri) / Store Manager (tutti)
GET `/api/orders/{id}/` - auth richiesta - Customer (proprio) / Store Manager
POST `/api/orders/` - auth richiesta - Customer (crea ordine dal carrello)
PATCH `/api/orders/{id}/` - auth richiesta - Store Manager (aggiorna stato)

Request (PATCH): `{"status": "shipped"}`

## Testing con HTTPie

```bash
pip install httpie
```

Sostituire `BASE_URL` con `127.0.0.1:8000` in locale o l'URL del deploy.

```bash
# Login
http POST BASE_URL/api/auth/login/ username=customer_demo password=cust12345

# Catalogo pubblico
http GET BASE_URL/api/products/

# Carrello
http GET BASE_URL/api/cart/ "Authorization:Token <TOKEN>"

# Aggiungi al carrello
http POST BASE_URL/api/cart/items/ "Authorization:Token <TOKEN>" product=1 quantity=2

# Crea ordine
http POST BASE_URL/api/orders/ "Authorization:Token <TOKEN>"

# Login come manager e aggiorna stato ordine
http POST BASE_URL/api/auth/login/ username=manager_demo password=manager12345
http PATCH BASE_URL/api/orders/1/ "Authorization:Token <TOKEN_MANAGER>" status=shipped

# Test azione vietata (customer che crea un prodotto) - atteso 403
http POST BASE_URL/api/products/ "Authorization:Token <TOKEN>" name="Test" price=10 stock=5 category=1
```
