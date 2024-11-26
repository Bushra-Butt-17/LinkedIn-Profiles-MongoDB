from flask import Flask, jsonify
from flask import Flask, request, jsonify
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
from pymongo import MongoClient

# Replace with your MongoDB Atlas connection string
MONGO_URI = "<ur connection string>"

# Initialize the MongoDB client
client = MongoClient(MONGO_URI)

# Select the database and collection
db = client["linkedin_profiles"]
collection = db["profiles"]

# Export the collection to be used in other files
def get_collection():
    return collection


# Home route - Render index page (frontend)
@app.route('/')
def home():
    return render_template("index.html")  # Render the main HTML template

# Fetch all profiles and display them on the frontend
@app.route('/profiles')
def profiles():
    profiles = list(collection.find())  # Fetch profiles from the database
    for profile in profiles:
        profile['_id'] = str(profile['_id'])  # Convert ObjectId to string for rendering
    return render_template("profiles.html", profiles=profiles)  # Render the profiles in HTML



# Function to get all documents from the collection
def get_all_documents():
    try:
        # Fetch all documents from the collection
        documents = list(collection.find())  # Convert the cursor to a list
        return documents
    except Exception as e:
        return str(e)

# Define an endpoint to fetch all documents
@app.route('/api/profiles', methods=['GET'])
def fetch_all_profiles():
    documents = get_all_documents()
    
    if isinstance(documents, str):  # In case an error occurs
        return jsonify({"error": documents}), 500
    
    # Remove the '_id' field before returning the response (MongoDB includes '_id' by default)
    for doc in documents:
        doc.pop('_id', None)
    
    return jsonify(documents)



# Function to update a document in the collection by email
def update_document_by_email(email, updated_data):
    try:
        # Update the document with the given email
        result = collection.update_one(
            {"email": email},  # Filter by email
            {"$set": updated_data}  # Set the updated data
        )
        # Check if any document was modified
        if result.modified_count == 0:
            return {"message": "No document found with the given email or no changes made."}, 404
        return {"message": "Document updated successfully."}, 200
    except Exception as e:
        return str(e), 500

@app.route('/edit/<email>', methods=['GET', 'POST'])
def edit_profile(email):
    if request.method == 'GET':
        # Fetch the profile by email
        profile = collection.find_one({"email": email})
        if profile:
            profile['_id'] = str(profile['_id'])  # Convert _id to string
            return render_template('edit_profile.html', profile=profile)
        return "Profile not found", 404
    
    if request.method == 'POST':
        # Get the updated data from the form
        updated_data = {
            "name": request.form['name'],
            "email": request.form['email'],
            "headline": request.form['headline'],
            "skills": request.form['skills'].split(',')
        }
        # Update the profile in MongoDB
        collection.update_one({"email": email}, {"$set": updated_data})
        return redirect('/profiles')

    


@app.route('/delete/<email>', methods=['GET'])
def delete_profile(email):
    result = collection.delete_one({"email": email})
    if result.deleted_count > 0:
        return redirect('/profiles')
    return "Profile not found", 404

@app.route('/add', methods=['GET', 'POST'])
def add_profile():
    if request.method == 'GET':
        return render_template('add_profile.html')

    if request.method == 'POST':
        # Get data from the form
        new_profile = {
            "name": request.form['name'],
            "email": request.form['email'],
            "headline": request.form['headline'],
            "skills": request.form['skills'].split(',')
        }
        # Insert the new profile into MongoDB
        collection.insert_one(new_profile)
        return redirect('/profiles')




@app.route('/profile/<email>')
def view_profile(email):
    # Fetch the profile by email
    profile = collection.find_one({"email": email})
    if profile:
        profile['_id'] = str(profile['_id'])  # Convert _id to string
        return render_template('view_profile.html', profile=profile)
    return "Profile not found", 404




from collections import Counter

@app.route('/dashboard')
def dashboard():
    # Get all profiles
    profiles = get_all_documents()

    # Extract all skills
    all_skills = []
    for profile in profiles:
        all_skills.extend(profile.get('skills', []))  # Add skills from each profile to the list

    # Count the frequency of each skill
    skill_counts = Counter(all_skills)

    # Sort the skills by frequency (highest to lowest)
    sorted_skill_counts = skill_counts.most_common()  # returns a list of (skill, count) tuples

    # Optionally, limit the number of top skills shown (e.g., top 10)
    top_skills = sorted_skill_counts[:10]

    # Get the total number of profiles
    profile_count = len(profiles)

    # Render the dashboard with profile count and top skills
    return render_template('dashboard.html', profile_count=profile_count, top_skills=top_skills)




if __name__ == "__main__":
    app.run(debug=True)



