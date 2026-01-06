from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['DEBUG'] = True

# In-memory storage for development (no MongoDB required)
notes_data = []
pyqs_data = []
videos_data = []
orders_data = []
uploads_data = []
admin_data = {
    'email': 'pkh99314930@gmail.com',
    'password': generate_password_hash('pk88488848'),  # Hashed password
    'name': 'PK.Hindustani'
}

# Mock database collections
class MockCollection:
    def __init__(self, data_list):
        self.data = data_list
    
    def find(self, query=None):
        return self.data
    
    def insert_one(self, document):
        document['_id'] = str(len(self.data) + 1)
        self.data.append(document)
        return document
    
    def find_one(self, query):
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None
    
    def update_one(self, filter_query, update_query):
        for item in self.data:
            if all(item.get(k) == v for k, v in filter_query.items()):
                if '$set' in update_query:
                    item.update(update_query['$set'])
                return True
        return False
    
    def delete_one(self, query):
        for i, item in enumerate(self.data):
            if all(item.get(k) == v for k, v in query.items()):
                self.data.pop(i)
                return True
        return False
    
    def sort(self, key, direction):
        # For find() method chaining - fix the sort method
        return sorted(self.data, key=lambda x: x.get(key, ''), reverse=(direction == -1))

# Initialize mock collections
notes_collection = MockCollection(notes_data)
pyqs_collection = MockCollection(pyqs_data)
videos_collection = MockCollection(videos_data)
orders_collection = MockCollection(orders_data)
uploads_collection = MockCollection(uploads_data)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class Admin(UserMixin):
    def __init__(self, email):
        self.email = email
    
    def get_id(self):
        return self.email
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(email):
    return Admin(email)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_admin():
    # Simple admin check for in-memory storage
    return admin_data

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/notes')
def notes():
    notes = list(notes_collection.find())
    notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('notes.html', notes=notes)

@app.route('/pyqs')
def pyqs():
    pyqs = list(pyqs_collection.find())
    pyqs = sorted(pyqs, key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('pyqs.html', pyqs=pyqs)

@app.route('/videos')
def videos():
    videos = list(videos_collection.find())
    videos = sorted(videos, key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('videos.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        upload_type = request.form['type']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            uploads_collection.insert_one({
                'filename': filename,
                'file_path': file_path,
                'description': description,
                'type': upload_type,
                'approved': False,
                'created_at': datetime.utcnow()
            })
            
            flash('Upload successful! Awaiting admin approval.', 'success')
            return redirect(url_for('upload'))
    
    return render_template('upload.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        course = request.form['course']
        
        orders_collection.insert_one({
            'name': name,
            'phone': phone,
            'address': address,
            'course': course,
            'status': 'pending',
            'created_at': datetime.utcnow()
        })
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order'))
    
    return render_template('order.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        admin = get_admin()
        if admin and admin['email'] == email and check_password_hash(admin['password'], password):
            user = Admin(admin['email'])
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    pending_uploads = list(uploads_collection.find({'approved': False}))
    orders = list(orders_collection.find())
    return render_template('admin_dashboard.html', pending_uploads=pending_uploads, orders=orders)

@app.route('/admin/approve_upload/<upload_id>')
@login_required
def approve_upload(upload_id):
    upload = uploads_collection.find_one({'_id': upload_id})
    if upload:
        if upload['type'] == 'notes':
            notes_collection.insert_one({
                'filename': upload['filename'],
                'file_path': upload['file_path'],
                'description': upload['description'],
                'created_at': datetime.utcnow()
            })
        elif upload['type'] == 'pyq':
            pyqs_collection.insert_one({
                'filename': upload['filename'],
                'file_path': upload['file_path'],
                'description': upload['description'],
                'created_at': datetime.utcnow()
            })
        
        uploads_collection.update_one({'_id': upload_id}, {'$set': {'approved': True}})
        flash('Upload approved successfully!', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_upload/<upload_id>')
@login_required
def reject_upload(upload_id):
    uploads_collection.delete_one({'_id': upload_id})
    flash('Upload rejected!', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        subject = request.form.get('subject', '')
        class_course = request.form.get('class_course', '')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            notes_collection.insert_one({
                'filename': filename,
                'file_path': file_path,
                'description': description,
                'subject': subject,
                'class_course': class_course,
                'created_at': datetime.utcnow()
            })
            
            flash('Note added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_note.html')

@app.route('/admin/add_pyq', methods=['GET', 'POST'])
@login_required
def add_pyq():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        university = request.form.get('university', '')
        course = request.form.get('course', '')
        year = request.form.get('year', '')
        exam_type = request.form.get('exam_type', '')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            pyqs_collection.insert_one({
                'filename': filename,
                'file_path': file_path,
                'description': description,
                'university': university,
                'course': course,
                'year': year,
                'exam_type': exam_type,
                'created_at': datetime.utcnow()
            })
            
            flash('PYQ added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_pyq.html')

@app.route('/admin/add_video', methods=['GET', 'POST'])
@login_required
def add_video():
    if request.method == 'POST':
        title = request.form['title']
        video_url = request.form['video_url']
        description = request.form['description']
        subject = request.form.get('subject', '')
        class_course = request.form.get('class_course', '')
        
        videos_collection.insert_one({
            'title': title,
            'video_url': video_url,
            'description': description,
            'subject': subject,
            'class_course': class_course,
            'created_at': datetime.utcnow()
        })
        
        flash('Video added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_video.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
