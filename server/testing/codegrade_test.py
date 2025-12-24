
import pytest
import json
import os
import tempfile
from app import app, db
from models import Pet


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as client:
        # Create all tables
        with app.app_context():
            db.create_all()
            # Start with clean session
            db.session.rollback()
        yield client
        # Clean up database and session
        with app.app_context():
            db.session.rollback()
        # Clean up file
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database after each test to ensure isolation"""
    yield
    with app.app_context():
        db.drop_all()
        db.create_all()


@pytest.fixture
def sample_pets():
    """Create sample pets for testing"""
    return [
        {'name': 'Fido', 'species': 'Dog'},
        {'name': 'Whiskers', 'species': 'Cat'},
        {'name': 'Goldie', 'species': 'Fish'}
    ]


class TestPetCreation:
    """Test pet creation operations"""
    
    def test_create_pet_success(self, client):
        """Test successful pet creation"""
        response = client.post('/pets', 
                             json={'name': 'Fido', 'species': 'Dog'},
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Fido'
        assert data['species'] == 'Dog'
        assert 'id' in data
        assert data['id'] == 1
    
    def test_create_pet_missing_name(self, client):
        """Test pet creation with missing name"""
        response = client.post('/pets', 
                             json={'species': 'Dog'},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Name and species are required' in data['error']
    
    def test_create_pet_missing_species(self, client):
        """Test pet creation with missing species"""
        response = client.post('/pets', 
                             json={'name': 'Fido'},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Name and species are required' in data['error']
    
    def test_create_pet_empty_request(self, client):
        """Test pet creation with empty request"""
        response = client.post('/pets', 
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestPetReading:
    """Test pet reading operations"""
    
    def test_get_all_pets_empty(self, client):
        """Test getting all pets when database is empty"""
        response = client.get('/pets')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_get_all_pets_with_data(self, client, sample_pets):
        """Test getting all pets when database has data"""
        # Create pets first
        for pet_data in sample_pets:
            client.post('/pets', json=pet_data, content_type='application/json')
        
        response = client.get('/pets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 3
        
        # Check first pet
        assert data[0]['name'] == 'Fido'
        assert data[0]['species'] == 'Dog'
        
        # Check second pet
        assert data[1]['name'] == 'Whiskers'
        assert data[1]['species'] == 'Cat'
    
    def test_get_pet_by_id_success(self, client, sample_pets):
        """Test getting a specific pet by ID"""
        # Create a pet first
        create_response = client.post('/pets', 
                                    json=sample_pets[0], 
                                    content_type='application/json')
        pet_id = json.loads(create_response.data)['id']
        
        # Get the pet
        response = client.get(f'/pets/{pet_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Fido'
        assert data['species'] == 'Dog'
        assert data['id'] == pet_id
    
    def test_get_pet_by_id_not_found(self, client):
        """Test getting a pet that doesn't exist"""
        response = client.get('/pets/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Pet not found' in data['error']
    
    def test_get_pets_filter_by_species(self, client, sample_pets):
        """Test filtering pets by species"""
        # Create pets
        for pet_data in sample_pets:
            client.post('/pets', json=pet_data, content_type='application/json')
        
        # Filter by species
        response = client.get('/pets?species=Cat')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Whiskers'
        assert data[0]['species'] == 'Cat'


class TestPetUpdate:
    """Test pet update operations"""
    
    def test_update_pet_success(self, client, sample_pets):
        """Test successful pet update"""
        # Create a pet first
        create_response = client.post('/pets', 
                                    json=sample_pets[0], 
                                    content_type='application/json')
        pet_id = json.loads(create_response.data)['id']
        
        # Update the pet
        update_data = {'name': 'Fido Updated', 'species': 'Big Dog'}
        response = client.put(f'/pets/{pet_id}', 
                            json=update_data,
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Fido Updated'
        assert data['species'] == 'Big Dog'
        assert data['id'] == pet_id
    
    def test_update_pet_partial(self, client, sample_pets):
        """Test partial pet update"""
        # Create a pet first
        create_response = client.post('/pets', 
                                    json=sample_pets[0], 
                                    content_type='application/json')
        pet_id = json.loads(create_response.data)['id']
        
        # Update only the name
        update_data = {'name': 'Fido the Great'}
        response = client.patch(f'/pets/{pet_id}', 
                              json=update_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Fido the Great'
        assert data['species'] == 'Dog'  # species should remain unchanged
    
    def test_update_pet_not_found(self, client):
        """Test updating a pet that doesn't exist"""
        response = client.put('/pets/999', 
                            json={'name': 'Nonexistent'},
                            content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Pet not found' in data['error']


class TestPetDeletion:
    """Test pet deletion operations"""
    
    def test_delete_pet_success(self, client, sample_pets):
        """Test successful pet deletion"""
        # Create a pet first
        create_response = client.post('/pets', 
                                    json=sample_pets[0], 
                                    content_type='application/json')
        pet_id = json.loads(create_response.data)['id']
        
        # Delete the pet
        response = client.delete(f'/pets/{pet_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Pet deleted successfully' in data['message']
        
        # Verify pet is deleted
        get_response = client.get(f'/pets/{pet_id}')
        assert get_response.status_code == 404
    
    def test_delete_pet_not_found(self, client):
        """Test deleting a pet that doesn't exist"""
        response = client.delete('/pets/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Pet not found' in data['error']
    
    def test_delete_all_pets_via_query(self, client, sample_pets):
        """Test deleting all pets using query.delete()"""
        # Create multiple pets
        for pet_data in sample_pets:
            client.post('/pets', json=pet_data, content_type='application/json')
        
        # Verify pets exist
        response = client.get('/pets')
        assert len(json.loads(response.data)) == 3
        
        # Delete all pets (simulating Pet.query.delete())
        with app.app_context():
            deleted_count = Pet.query.delete()
            db.session.commit()
            assert deleted_count == 3
        
        # Verify all pets are deleted
        response = client.get('/pets')
        assert json.loads(response.data) == []


class TestFlaskShellOperations:
    """Test Flask shell CRUD operations as described in the lesson"""
    
    def test_flask_shell_add_and_commit(self, client):
        """Test shell-like add() and commit() operations"""
        with app.app_context():
            # Create pet instance (not yet persisted)
            pet = Pet(name="Fido", species="Dog")
            assert pet.id is None
            
            # Add to session and commit
            db.session.add(pet)
            db.session.commit()
            
            # Verify ID is now assigned
            assert pet.id == 1
            assert pet.name == "Fido"
            assert pet.species == "Dog"
    
    def test_flask_shell_query_operations(self, client):
        """Test shell-like query operations"""
        with app.app_context():
            # Add some pets
            pet1 = Pet(name="Fido", species="Dog")
            pet2 = Pet(name="Whiskers", species="Cat")
            db.session.add(pet1)
            db.session.add(pet2)
            db.session.commit()
            
            # Test query.all()
            all_pets = Pet.query.all()
            assert len(all_pets) == 2
            
            # Test query.filter()
            cats = Pet.query.filter(Pet.species == 'Cat').all()
            assert len(cats) == 1
            assert cats[0].name == 'Whiskers'
            
            # Test query.filter_by()
            dogs = Pet.query.filter_by(species='Dog').all()
            assert len(dogs) == 1
            assert dogs[0].name == 'Fido'
            
            # Test query.first()
            first_pet = Pet.query.first()
            assert first_pet.name == 'Fido'
            
            # Test db.session.get()
            pet = db.session.get(Pet, 1)
            assert pet.name == 'Fido'
            
            # Test order_by()
            ordered_pets = Pet.query.order_by('species').all()
            assert ordered_pets[0].species == 'Cat'
            assert ordered_pets[1].species == 'Dog'
    
    def test_flask_shell_update_operations(self, client):
        """Test shell-like update operations"""
        with app.app_context():
            # Create and persist a pet
            pet = Pet(name="Fido", species="Dog")
            db.session.add(pet)
            db.session.commit()
            
            # Update attributes
            pet.name = "Fido the mighty"
            pet.species = "Big Dog"
            db.session.commit()
            
            # Verify update with fresh session
            db.session.expire_all()  # Clear any cached objects
            updated_pet = db.session.get(Pet, 1)
            assert updated_pet.name == "Fido the mighty"
            assert updated_pet.species == "Big Dog"
    
    def test_flask_shell_delete_operations(self, client):
        """Test shell-like delete operations"""
        with app.app_context():
            # Create pets
            pet1 = Pet(name="Fido", species="Dog")
            pet2 = Pet(name="Whiskers", species="Cat")
            db.session.add(pet1)
            db.session.add(pet2)
            db.session.commit()
            
            # Verify pets exist
            assert Pet.query.count() == 2
            
            # Delete one pet
            db.session.delete(pet1)
            db.session.commit()
            
            # Verify deletion
            assert Pet.query.count() == 1
            remaining_pet = Pet.query.first()
            assert remaining_pet.name == "Whiskers"
            
            # Delete all remaining pets
            Pet.query.delete()
            db.session.commit()
            
            # Verify all pets deleted
            assert Pet.query.count() == 0


# Keep the original test for compatibility
def test_codegrade_placeholder():
    """Codegrade placeholder test"""
    assert 1 == 1
