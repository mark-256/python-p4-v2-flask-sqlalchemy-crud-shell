# server/app.py

from flask import Flask, request, jsonify
from flask_migrate import Migrate

from models import db, Pet

# create a Flask application instance 
app = Flask(__name__)

# configure the database connection to the local file app.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# configure flag to disable modification tracking and use less memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a Migrate object to manage schema modifications
migrate = Migrate(app, db)

# initialize the Flask application to use the database
db.init_app(app)

# Create all tables
with app.app_context():
    db.create_all()


# CRUD Routes

@app.route('/pets', methods=['POST'])
def create_pet():
    """Create a new pet"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('name') or not data.get('species'):
        return jsonify({'error': 'Name and species are required'}), 400
    
    # Create new pet
    pet = Pet(name=data['name'], species=data['species'])
    db.session.add(pet)
    db.session.commit()
    
    return jsonify({
        'id': pet.id,
        'name': pet.name,
        'species': pet.species
    }), 201


@app.route('/pets', methods=['GET'])
def get_pets():
    """Get all pets"""
    # Get query parameters for filtering
    species_filter = request.args.get('species')
    
    # Build query
    query = Pet.query
    if species_filter:
        query = query.filter_by(species=species_filter)
    
    pets = query.all()
    
    return jsonify([{
        'id': pet.id,
        'name': pet.name,
        'species': pet.species
    } for pet in pets])


@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    """Get a specific pet by ID"""
    pet = db.session.get(Pet, pet_id)
    
    if pet is None:
        return jsonify({'error': 'Pet not found'}), 404
    
    return jsonify({
        'id': pet.id,
        'name': pet.name,
        'species': pet.species
    })


@app.route('/pets/<int:pet_id>', methods=['PUT', 'PATCH'])
def update_pet(pet_id):
    """Update a pet"""
    pet = db.session.get(Pet, pet_id)
    
    if pet is None:
        return jsonify({'error': 'Pet not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'name' in data:
        pet.name = data['name']
    if 'species' in data:
        pet.species = data['species']
    
    db.session.commit()
    
    return jsonify({
        'id': pet.id,
        'name': pet.name,
        'species': pet.species
    })


@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    """Delete a pet"""
    pet = db.session.get(Pet, pet_id)
    
    if pet is None:
        return jsonify({'error': 'Pet not found'}), 404
    
    db.session.delete(pet)
    db.session.commit()
    
    return jsonify({'message': 'Pet deleted successfully'}), 200


# Flask shell context for easy database operations
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Pet': Pet}


if __name__ == '__main__':
    app.run(port=5555, debug=True)
