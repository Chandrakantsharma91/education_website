from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, abort
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Mock collections for fallback when MongoDB is unavailable
class MockCollection:
    def __init__(self):
        self.data = []
    
    def find(self, query=None):
        try:
            if query is None:
                return MockCursor(self.data.copy())
            else:
                filtered_data = [item for item in self.data if all(item.get(k) == v for k, v in query.items())]
                return MockCursor(filtered_data)
        except Exception as e:
            logger.error(f"Error in MockCollection.find: {e}")
            return MockCursor([])
    
    def find_one(self, query):
        try:
            for item in self.data:
                # Handle both string and ObjectId comparisons
                match = True
                for k, v in query.items():
                    item_value = item.get(k)
                    if item_value != v:
                        # Try string comparison if direct comparison fails
                        if str(item_value) != str(v):
                            match = False
                            break
                if match:
                    return item
            return None
        except Exception as e:
            logger.error(f"Error in MockCollection.find_one: {e}")
            return None
    
    def insert_one(self, document):
        try:
            if not isinstance(document, dict):
                document = {}
            document['_id'] = str(uuid.uuid4())
            document['created_at'] = datetime.utcnow()
            self.data.append(document)
            return document
        except Exception as e:
            logger.error(f"Error in MockCollection.insert_one: {e}")
            return None
    
    def update_one(self, filter_query, update_query):
        try:
            for item in self.data:
                if all(item.get(k) == v for k, v in filter_query.items()):
                    if '$set' in update_query:
                        item.update(update_query['$set'])
                    return True
            return False
        except Exception as e:
            logger.error(f"Error in MockCollection.update_one: {e}")
            return False
    
    def delete_one(self, query):
        try:
            for i, item in enumerate(self.data):
                # Handle both string and ObjectId comparisons
                match = True
                for k, v in query.items():
                    item_value = item.get(k)
                    if item_value != v:
                        # Try string comparison if ObjectId comparison fails
                        if str(item_value) != str(v):
                            match = False
                            break
                if match:
                    self.data.pop(i)
                    return type('Result', (), {'deleted_count': 1})()
            return type('Result', (), {'deleted_count': 0})()
        except Exception as e:
            logger.error(f"Error in MockCollection.delete_one: {e}")
            return type('Result', (), {'deleted_count': 0})()

class MockCursor:
    def __init__(self, data):
        self.data = data if data is not None else []
    
    def sort(self, field, direction=1):
        try:
            self.data.sort(key=lambda x: x.get(field, '') if isinstance(x, dict) else '', reverse=(direction == -1))
            return self
        except Exception as e:
            logger.error(f"Error in MockCursor.sort: {e}")
            return self
    
    def __iter__(self):
        return iter(self.data)
    
    def __len__(self):
        return len(self.data)

# MongoDB Configuration with improved error handling
# db = None
# try:
#     MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://pk88488848_db_user:A9cbseJTvXToA2N0@cluster0.yik8h02.mongodb.net/')
#     if MONGODB_URI:
#         client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
#         # Test the connection
#         client.admin.command('ping')
#         db = client['education_website']
#         logger.info("MongoDB connected successfully")
#     else:
#         logger.warning("MongoDB URI not configured, using in-memory storage")
#         db = None
# except Exception as e:
#     logger.error(f"MongoDB connection failed: {e}")
#     db = None
#     logger.info("Using in-memory storage as fallback")



# =========================
# MongoDB Atlas Connection
# =========================

from pymongo.errors import ServerSelectionTimeoutError

db = None
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    logger.warning("MONGODB_URI not set. Using in-memory storage.")
else:
    try:
        client = MongoClient(
            MONGODB_URI,
            tls=True,                       # REQUIRED for Atlas
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )

        # Force actual connection
        client.admin.command("ping")

        db = client["education_website"]
        logger.info("MongoDB connected successfully")

    except ServerSelectionTimeoutError as e:
        logger.error(f"MongoDB connection timeout: {e}")
        db = None

    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        db = None


# Initialize collections based on database availability
# if db is not None:
#     try:
#         notes_collection = db['notes']
#         pyqs_collection = db['pyqs']
#         videos_collection = db['videos']
#         orders_collection = db['orders']
#         uploads_collection = db['uploads']
#         handwritten_notes_collection = db['handwritten_notes']
#         logger.info("MongoDB collections initialized successfully")
#     except Exception as e:
#         logger.error(f"Error initializing MongoDB collections: {e}")
#         db = None
#         # Fallback to mock collections
#         notes_collection = MockCollection()
#         pyqs_collection = MockCollection()
#         videos_collection = MockCollection()
#         orders_collection = MockCollection()
#         uploads_collection = MockCollection()
#         handwritten_notes_collection = MockCollection()
#         logger.info("Fallback to in-memory collections due to MongoDB error")
# else:
#     # Fallback mock collections
#     notes_collection = MockCollection()
#     pyqs_collection = MockCollection()
#     videos_collection = MockCollection()
#     orders_collection = MockCollection()
#     uploads_collection = MockCollection()
#     handwritten_notes_collection = MockCollection()
#     logger.info("Using in-memory storage as configured")


if db is not None:
    notes_collection = db.notes
    pyqs_collection = db.pyqs
    videos_collection = db.videos
    orders_collection = db.orders
    uploads_collection = db.uploads
    handwritten_notes_collection = db.handwritten_notes
    logger.info("MongoDB collections initialized")
else:
    notes_collection = MockCollection()
    pyqs_collection = MockCollection()
    videos_collection = MockCollection()
    orders_collection = MockCollection()
    uploads_collection = MockCollection()
    handwritten_notes_collection = MockCollection()
    logger.info("Using in-memory mock collections")


# Admin credentials from environment variables
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'pkh99314930@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'pk88488848')

admin_data = {
    'email': ADMIN_EMAIL,
    'password': generate_password_hash(ADMIN_PASSWORD),
    'name': 'PK.Hindustani'  # Keep admin name as is
}

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
    try:
        notes = list(notes_collection.find().sort('created_at', -1))
        return render_template('notes.html', notes=notes)
    except Exception as e:
        logger.error(f"Error in notes route: {e}")
        flash('Unable to load notes. Please try again later.', 'error')
        return redirect(url_for('home'))

@app.route('/pyqs')
def pyqs():
    try:
        pyqs = list(pyqs_collection.find().sort('created_at', -1))
        return render_template('pyqs.html', pyqs=pyqs)
    except Exception as e:
        logger.error(f"Error in pyqs route: {e}")
        flash('Unable to load PYQs. Please try again later.', 'error')
        return redirect(url_for('home'))

@app.route('/videos')
def videos():
    try:
        videos = list(videos_collection.find().sort('created_at', -1))
        return render_template('videos.html', videos=videos)
    except Exception as e:
        logger.error(f"Error in videos route: {e}")
        flash('Unable to load videos. Please try again later.', 'error')
        return redirect(url_for('home'))

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
        logger.info(f"Admin login attempt: email={email}, admin_data={admin}")
        
        if admin and admin['email'] == email and check_password_hash(admin['password'], password):
            user = Admin(admin['email'])
            login_user(user)
            flash('Login successful!', 'success')
            logger.info(f"Admin login successful for {email}")
            return redirect(url_for('admin_dashboard'))
        else:
            logger.warning(f"Admin login failed for {email}")
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        logger.info("Admin dashboard route accessed")
        
        # Load all collections with proper error handling
        pending_uploads = list(uploads_collection.find({'approved': False}).sort('created_at', -1))
        orders = list(orders_collection.find().sort('created_at', -1))
        notes = list(notes_collection.find().sort('created_at', -1))
        pyqs = list(pyqs_collection.find().sort('created_at', -1))
        videos = list(videos_collection.find().sort('created_at', -1))
        handwritten_notes = list(handwritten_notes_collection.find().sort('created_at', -1))
        
        # Calculate statistics
        stats = {
            'pending_uploads_count': len(pending_uploads),
            'orders_count': len(orders),
            'notes_count': len(notes),
            'pyqs_count': len(pyqs),
            'videos_count': len(videos),
            'handwritten_notes_count': len(handwritten_notes),
            'total_content': len(notes) + len(pyqs) + len(videos) + len(handwritten_notes)
        }
        
        logger.info(f"Admin dashboard loaded successfully. Stats: {stats}")
        
        return render_template('admin_dashboard.html', 
                             pending_uploads=pending_uploads, 
                             orders=orders,
                             notes=notes,
                             pyqs=pyqs,
                             videos=videos,
                             handwritten_notes=handwritten_notes,
                             stats=stats)
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash('An error occurred loading the dashboard. Please try again.', 'error')
        return redirect(url_for('home'))

@app.route('/admin/approve_upload/<upload_id>')
@login_required
def approve_upload(upload_id):
    try:
        # Handle both ObjectId (MongoDB) and string (MockCollection) IDs
        query = {'_id': upload_id}
        if db is not None:  # MongoDB
            try:
                from bson import ObjectId
                query = {'_id': ObjectId(upload_id)}
            except:
                pass  # Keep as string if conversion fails
        
        upload = uploads_collection.find_one(query)
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
            
            uploads_collection.update_one(query, {'$set': {'approved': True}})
            logger.info(f"Upload approved successfully: {upload_id}")
            flash('Upload approved successfully!', 'success')
        else:
            logger.warning(f"Upload not found for approval: {upload_id}")
            flash('Upload not found.', 'warning')
    except Exception as e:
        logger.error(f"Error approving upload {upload_id}: {e}")
        flash('Error approving upload. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_upload/<upload_id>')
@login_required
def reject_upload(upload_id):
    try:
        # Handle both ObjectId (MongoDB) and string (MockCollection) IDs
        query = {'_id': upload_id}
        if db is not None:  # MongoDB
            try:
                from bson import ObjectId
                query = {'_id': ObjectId(upload_id)}
            except:
                pass  # Keep as string if conversion fails
        
        upload = uploads_collection.find_one(query)
        if upload and 'file_path' in upload:
            try:
                if os.path.exists(upload['file_path']):
                    os.remove(upload['file_path'])
                    logger.info(f"Deleted rejected upload file: {upload['file_path']}")
            except Exception as e:
                logger.error(f"Error deleting rejected upload file {upload['file_path']}: {e}")
        
        result = uploads_collection.delete_one(query)
        if result.deleted_count > 0:
            logger.info(f"Upload rejected successfully: {upload_id}")
            flash('Upload rejected!', 'info')
        else:
            logger.warning(f"Upload not found for rejection: {upload_id}")
            flash('Upload not found or already processed.', 'warning')
    except Exception as e:
        logger.error(f"Error rejecting upload {upload_id}: {e}")
        flash('Error rejecting upload. Please try again.', 'error')
    
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

@app.route('/handwritten-notes')
def handwritten_notes():
    try:
        notes = list(handwritten_notes_collection.find().sort('created_at', -1))
        return render_template('handwritten_notes.html', notes=notes)
    except Exception as e:
        logger.error(f"Error in handwritten_notes route: {e}")
        flash('Unable to load handwritten notes. Please try again later.', 'error')
        return redirect(url_for('home'))

@app.route('/admin/add_handwritten_note', methods=['GET', 'POST'])
@login_required
def add_handwritten_note():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        subject = request.form.get('subject', '')
        class_course = request.form.get('class_course', '')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            handwritten_notes_collection.insert_one({
                'filename': filename,
                'file_path': file_path,
                'description': description,
                'subject': subject,
                'class_course': class_course,
                'created_at': datetime.utcnow()
            })
            
            flash('Handwritten note added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_handwritten_note.html')

@app.route('/admin/add_video', methods=['GET', 'POST'])
@login_required
def add_video():
    if request.method == 'POST':
        file = request.files.get('file')
        title = request.form.get('title', '')
        subject = request.form.get('subject', '')
        video_url = request.form.get('video_url', '')
        description = request.form['description']
        
        # For video URLs, we don't need file upload, just store the URL
        if video_url:
            videos_collection.insert_one({
                'title': title,
                'subject': subject,
                'video_url': video_url,
                'description': description,
                'created_at': datetime.utcnow()
            })
            
            flash('Video added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Video URL is required!', 'error')
    
    return render_template('add_video.html')

@app.route('/admin/delete_note/<note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    try:
        logger.info(f"Delete note request for ID: {note_id}")
        
        # Handle both ObjectId (MongoDB) and string (MockCollection) IDs
        query = {'_id': note_id}
        if db is not None:  # MongoDB
            try:
                from bson import ObjectId
                # Try to convert to ObjectId, but handle cases where it's already a string
                if isinstance(note_id, str) and len(note_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in note_id):
                    query = {'_id': ObjectId(note_id)}
                    logger.info(f"Converted {note_id} to ObjectId")
                else:
                    logger.info(f"Using string ID: {note_id}")
            except ImportError:
                logger.warning("bson.ObjectId not available, using string ID")
            except Exception as e:
                logger.warning(f"Could not convert to ObjectId: {e}, using string ID")
        
        note = notes_collection.find_one(query)
        if note:
            logger.info(f"Found note to delete: {note.get('filename', 'unknown')}")
            
            # Delete associated file if it exists
            if 'file_path' in note and note['file_path']:
                try:
                    if os.path.exists(note['file_path']):
                        os.remove(note['file_path'])
                        logger.info(f"Deleted file: {note['file_path']}")
                    else:
                        logger.warning(f"File not found: {note['file_path']}")
                except Exception as e:
                    logger.error(f"Error deleting file {note['file_path']}: {e}")
            
            # Delete from database
            result = notes_collection.delete_one(query)
            if result.deleted_count > 0:
                logger.info(f"Note deleted successfully: {note_id}")
                flash('Note deleted successfully!', 'success')
            else:
                logger.warning(f"Database delete returned 0 for note: {note_id}")
                flash('Note not found or already deleted.', 'warning')
        else:
            logger.warning(f"Note not found in database: {note_id}")
            flash('Note not found.', 'warning')
            
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash('Error deleting note. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_pyq/<pyq_id>', methods=['POST'])
@login_required
def delete_pyq(pyq_id):
    try:
        # Handle both ObjectId (MongoDB) and string (MockCollection) IDs
        query = {'_id': pyq_id}
        if db is not None:  # MongoDB
            try:
                from bson import ObjectId
                query = {'_id': ObjectId(pyq_id)}
            except:
                pass  # Keep as string if conversion fails
        
        pyq = pyqs_collection.find_one(query)
        if pyq and 'file_path' in pyq:
            try:
                if os.path.exists(pyq['file_path']):
                    os.remove(pyq['file_path'])
                    logger.info(f"Deleted file: {pyq['file_path']}")
            except Exception as e:
                logger.error(f"Error deleting file {pyq['file_path']}: {e}")
        
        result = pyqs_collection.delete_one(query)
        if result.deleted_count > 0:
            logger.info(f"PYQ deleted successfully: {pyq_id}")
            flash('PYQ deleted successfully!', 'success')
        else:
            logger.warning(f"PYQ not found for deletion: {pyq_id}")
            flash('PYQ not found or already deleted.', 'warning')
    except Exception as e:
        logger.error(f"Error deleting PYQ {pyq_id}: {e}")
        flash('Error deleting PYQ. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_video/<video_id>', methods=['POST'])
@login_required
def delete_video(video_id):
    try:
        # Handle both ObjectId (MongoDB) and string (MockCollection) IDs
        query = {'_id': video_id}
        if db is not None:  # MongoDB
            try:
                from bson import ObjectId
                query = {'_id': ObjectId(video_id)}
            except:
                pass  # Keep as string if conversion fails
        
        result = videos_collection.delete_one(query)
        if result.deleted_count > 0:
            logger.info(f"Video deleted successfully: {video_id}")
            flash('Video deleted successfully!', 'success')
        else:
            logger.warning(f"Video not found for deletion: {video_id}")
            flash('Video not found or already deleted.', 'warning')
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {e}")
        flash('Error deleting video. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_handwritten_note/<note_id>', methods=['POST'])
@login_required
def delete_handwritten_note(note_id):
    try:
        # Handle both ObjectId (MongoDB) and string (MockCollection) IDs
        query = {'_id': note_id}
        if db is not None:  # MongoDB
            try:
                from bson import ObjectId
                query = {'_id': ObjectId(note_id)}
            except:
                pass  # Keep as string if conversion fails
        
        note = handwritten_notes_collection.find_one(query)
        if note and 'file_path' in note:
            try:
                if os.path.exists(note['file_path']):
                    os.remove(note['file_path'])
                    logger.info(f"Deleted file: {note['file_path']}")
            except Exception as e:
                logger.error(f"Error deleting file {note['file_path']}: {e}")
        
        result = handwritten_notes_collection.delete_one(query)
        if result.deleted_count > 0:
            logger.info(f"Handwritten note deleted successfully: {note_id}")
            flash('Handwritten note deleted successfully!', 'success')
        else:
            logger.warning(f"Handwritten note not found for deletion: {note_id}")
            flash('Handwritten note not found or already deleted.', 'warning')
    except Exception as e:
        logger.error(f"Error deleting handwritten note {note_id}: {e}")
        flash('Error deleting handwritten note. Please try again.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/system_info')
@login_required
def system_info():
    try:
        import platform
        
        system_info = {
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'mongodb_connected': db is not None,
            'database_type': 'MongoDB Atlas' if db is not None else 'In-Memory Mock',
            'total_collections': 6,
            'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'upload_folder_path': app.config['UPLOAD_FOLDER'],
            'server_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'debug_mode': app.config['DEBUG'],
            'environment': app.config['ENV']
        }
        
        return render_template('system_info.html', system_info=system_info)
    except Exception as e:
        logger.error(f"Error in system_info: {e}")
        flash('Unable to load system information.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/clear_test_data')
@login_required
def clear_test_data():
    try:
        # Only clear data if using mock collections (development mode)
        if db is None:
            notes_collection.data.clear()
            pyqs_collection.data.clear()
            videos_collection.data.clear()
            orders_collection.data.clear()
            uploads_collection.data.clear()
            handwritten_notes_collection.data.clear()
            flash('Test data cleared successfully!', 'success')
        else:
            flash('Cannot clear data in production mode!', 'warning')
    except Exception as e:
        logger.error(f"Error clearing test data: {e}")
        flash('Error clearing test data.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Request expired. Please refresh and try again.', 'error')
    return redirect(request.referrer or url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        abort(404)

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
