# Flask-SQLAlchemy CRUD API Documentation

## Base URL

```
http://localhost:5555
```

## Endpoints

### 1. Create Pet

**POST** `/pets`

Create a new pet in the database.

**Request Body:**

```json
{
  "name": "Fido",
  "species": "Dog"
}
```

**Required Fields:**

- `name` (string): Pet's name
- `species` (string): Pet's species

**Response:**

```json
{
  "id": 1,
  "name": "Fido",
  "species": "Dog"
}
```

**Status Codes:**

- `201`: Pet created successfully
- `400`: Missing required fields

**Example:**

```bash
curl -X POST http://localhost:5555/pets \
  -H "Content-Type: application/json" \
  -d '{"name": "Fido", "species": "Dog"}'
```

---

### 2. Get All Pets

**GET** `/pets`

Retrieve all pets from the database.

**Query Parameters (optional):**

- `species` (string): Filter pets by species

**Response:**

```json
[
  {
    "id": 1,
    "name": "Fido",
    "species": "Dog"
  },
  {
    "id": 2,
    "name": "Whiskers",
    "species": "Cat"
  }
]
```

**Status Codes:**

- `200`: Success

**Examples:**

```bash
# Get all pets
curl http://localhost:5555/pets

# Filter by species
curl "http://localhost:5555/pets?species=Cat"
```

---

### 3. Get Pet by ID

**GET** `/pets/<id>`

Retrieve a specific pet by its ID.

**Response:**

```json
{
  "id": 1,
  "name": "Fido",
  "species": "Dog"
}
```

**Status Codes:**

- `200`: Pet found
- `404`: Pet not found

**Example:**

```bash
curl http://localhost:5555/pets/1
```

---

### 4. Update Pet

**PUT/PATCH** `/pets/<id>`

Update an existing pet's information.

**Request Body (partial or full):**

```json
{
  "name": "Fido Updated",
  "species": "Big Dog"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Fido Updated",
  "species": "Big Dog"
}
```

**Status Codes:**

- `200`: Pet updated successfully
- `404`: Pet not found

**Examples:**

```bash
# Full update with PUT
curl -X PUT http://localhost:5555/pets/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Fido Updated", "species": "Big Dog"}'

# Partial update with PATCH
curl -X PATCH http://localhost:5555/pets/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Fido the Great"}'
```

---

### 5. Delete Pet

**DELETE** `/pets/<id>`

Delete a pet from the database.

**Response:**

```json
{
  "message": "Pet deleted successfully"
}
```

**Status Codes:**

- `200`: Pet deleted successfully
- `404`: Pet not found

**Example:**

```bash
curl -X DELETE http://localhost:5555/pets/1
```

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**

```json
{
  "error": "Name and species are required"
}
```

**404 Not Found:**

```json
{
  "error": "Pet not found"
}
```

---

## Testing the API

### Using curl

```bash
# Create a pet
curl -X POST http://localhost:5555/pets \
  -H "Content-Type: application/json" \
  -d '{"name": "Fido", "species": "Dog"}'

# Get all pets
curl http://localhost:5555/pets

# Get specific pet
curl http://localhost:5555/pets/1

# Update pet
curl -X PUT http://localhost:5555/pets/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Fido Updated", "species": "Big Dog"}'

# Delete pet
curl -X DELETE http://localhost:5555/pets/1
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5555"

# Create pet
response = requests.post(f"{base_url}/pets",
                        json={"name": "Fido", "species": "Dog"})
print(response.json())

# Get all pets
response = requests.get(f"{base_url}/pets")
print(response.json())

# Get specific pet
response = requests.get(f"{base_url}/pets/1")
print(response.json())

# Update pet
response = requests.put(f"{base_url}/pets/1",
                       json={"name": "Fido Updated", "species": "Big Dog"})
print(response.json())

# Delete pet
response = requests.delete(f"{base_url}/pets/1")
print(response.json())
```

---

## Flask Shell Commands Reference

The Flask shell provides direct access to database operations without writing SQL. Start the shell with:

```bash
cd server
flask shell
```

### Basic CRUD Operations

#### Create (Add and Commit)

```python
# Create a pet instance (not yet persisted)
pet = Pet(name="Fido", species="Dog")
pet.id  # None (not yet assigned)

# Add to session
db.session.add(pet)

# Commit to persist
db.session.commit()
pet.id  # Now assigned (e.g., 1)
```

#### Read (Query)

```python
# Get all pets
Pet.query.all()

# Get first pet
Pet.query.first()

# Filter by exact match
Pet.query.filter_by(species='Cat').all()

# Filter with complex conditions
Pet.query.filter(Pet.name.startswith('F')).all()

# Get by primary key
pet = db.session.get(Pet, 1)

# Order results
Pet.query.order_by('species').all()
```

#### Update

```python
# Get pet to update
pet = db.session.get(Pet, 1)

# Modify attributes
pet.name = "Fido the Great"
pet.species = "Big Dog"

# Commit changes
db.session.commit()
```

#### Delete

```python
# Delete single pet
pet = db.session.get(Pet, 1)
db.session.delete(pet)
db.session.commit()

# Delete all pets
Pet.query.delete()
db.session.commit()
```

#### Count and Aggregation

```python
from sqlalchemy import func

# Count total pets
db.session.query(func.count(Pet.id)).first()
```

### Session Management

#### Transaction Workflow

```python
# Begin transaction (automatic with session)
pet1 = Pet(name="Fido", species="Dog")
pet2 = Pet(name="Whiskers", species="Cat")

# Add to session
db.session.add(pet1)
db.session.add(pet2)

# Commit transaction
db.session.commit()
```

#### Rollback (if needed)

```python
# If something goes wrong, rollback
db.session.rollback()
```

### Shell Context

The Flask shell automatically imports:

- `db` - Database session object
- `Pet` - Pet model class

Example shell session:

```python
>>> Pet.query.all()
[<Pet 1, Fido, Dog>, <Pet 2, Whiskers, Cat>]

>>> Pet.query.filter_by(species='Dog').all()
[<Pet 1, Fido, Dog>]

>>> pet = db.session.get(Pet, 1)
>>> pet.name
'Fido'

>>> exit()
```

---

## Database Schema

### Pets Table

| Column  | Type    | Constraints                 |
| ------- | ------- | --------------------------- |
| id      | Integer | Primary Key, Auto-increment |
| name    | String  | Not Null                    |
| species | String  | Not Null                    |

### Model Representation

```python
class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    species = db.Column(db.String)
```

---

## Running the Application

1. **Install Dependencies:**

```bash
pipenv install
pipenv shell
```

2. **Initialize Database:**

```bash
cd server
flask db init
flask db migrate -m "Initial migration."
flask db upgrade head
```

3. **Start Flask Server:**

```bash
export FLASK_APP=app.py
export FLASK_RUN_PORT=5555
flask run
```

4. **Run Tests:**

```bash
pytest server/testing/codegrade_test.py -v
```
