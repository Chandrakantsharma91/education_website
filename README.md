# EduHub - University Education Website

A complete, beginner-friendly but professional education website for university students built with Python Flask, HTML, CSS, and JavaScript.

## Features

### 📚 Main Features
- **Previous Year Questions (PYQs)** - University-wise, course-wise, and year-wise question papers
- **Expert Notes** - Chapter-wise comprehensive study materials
- **Handwritten Notes** - Beautifully handwritten notes with personal touch
- **Video Solutions** - Topic-wise video explanations and problem-solving sessions
- **Hard Copy Notes Order** - Simple order form for physical note delivery
- **Student Upload Section** - Students can upload PDFs (question papers, syllabus, notes)
- **WhatsApp Support** - Floating WhatsApp chat button

### 🔐 Admin Panel
- Secure admin login with authentication
- Protected admin routes
- **Full Dashboard Control** - Complete management of all content
- Upload/edit/delete notes, PYQs, videos, and handwritten notes
- Approve or reject student uploads
- Manage hard copy orders
- View and manage downloads
- **Storage Management** - Delete uploaded data to manage storage space

## Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MongoDB (Atlas)
- **File Uploads**: PDF support
- **Authentication**: Admin login only
- **Hosting**: Localhost

## Database Configuration

**MongoDB Atlas Connection:**
- Username: `pk88488848_db_user`
- Password: `A9cbseJTvXToA2N0`
- Connection String: `mongodb+srv://pk88488848_db_user:A9cbseJTvXToA2N0@cluster0.yik8h02.mongodb.net/`

## Admin Details

- **Admin Name**: PK.Hindustani
- **Admin Email**: pkh99314930@gmail.com
- **Default Password**: `pk88488848` (Change this after first login)

## WhatsApp Support

- **WhatsApp Number**: +91 8882767568
- Floating WhatsApp button available on all pages

## Project Structure

```
education_website/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── home.html           # Home page
│   ├── notes.html          # Notes listing page
│   ├── pyqs.html           # PYQs listing page
│   ├── videos.html         # Videos listing page
│   ├── upload.html         # Student upload page
│   ├── order.html          # Hard copy order page
│   ├── admin_login.html    # Admin login page
│   ├── admin_dashboard.html # Admin dashboard
│   ├── add_note.html       # Add notes form
│   ├── add_pyq.html        # Add PYQs form
│   └── add_video.html      # Add videos form
├── static/                 # Static files
│   └── style.css          # Custom CSS styles
└── uploads/               # File upload directory
```

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account access
- Internet connection for dependencies

### 2. Clone and Setup
```bash
# Navigate to project directory
cd education_website

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
The application is configured to connect to MongoDB Atlas using the provided credentials. No additional environment setup is required.

### 4. Run the Application
```bash
# Start the Flask development server
python app.py
```

### 5. Access the Website
Open your browser and navigate to:
- **Localhost**: http://localhost:5000
- **Network**: http://0.0.0.0:5000 (accessible from other devices on the same network)

## Usage

### For Students
1. **Browse Content**: Visit the Notes, PYQs, or Videos pages to access educational materials
2. **Upload Content**: Use the Upload page to submit question papers, syllabus, or notes (requires admin approval)
3. **Order Notes**: Use the Order page to request hard copy notes
4. **Contact Support**: Use the floating WhatsApp button for support

### For Admins
1. **Login**: Navigate to `/admin/login` and use the admin credentials
2. **Dashboard**: View pending uploads and orders in the admin dashboard
3. **Content Management**: Add new notes, PYQs, and videos
4. **Approval System**: Review and approve/reject student uploads
5. **Order Management**: View and manage hard copy orders

## Security Features

- **Admin Authentication**: Secure login system with password hashing
- **Protected Routes**: Admin routes require authentication
- **File Validation**: Only PDF files are allowed for uploads
- **Input Validation**: All forms include proper validation
- **Session Management**: Secure session-based authentication

## Customization

### Changing Admin Password
1. Access the MongoDB Atlas database
2. Navigate to the `admins` collection
3. Update the password field with a new hashed password using `generate_password_hash()`

### Adding Custom Content
- Upload files directly through the admin panel
- Add video links from YouTube or other video platforms
- Customize the website text and banners through the admin interface

### Styling
- Modify `static/style.css` for custom CSS changes
- The base template includes Bootstrap 5.3.0 for responsive design
- Font Awesome 6.4.0 provides icons

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Check internet connection
   - Verify MongoDB Atlas credentials
   - Ensure the IP address is whitelisted in MongoDB Atlas

2. **File Upload Issues**
   - Ensure the `uploads/` directory exists and is writable
   - Check file size limits (currently set to reasonable defaults)
   - Verify file type restrictions (PDF only)

3. **Admin Login Issues**
   - Check admin credentials
   - Verify the admin user exists in the database
   - Reset password if needed

### Getting Help
- Contact: pkh99314930@gmail.com
- WhatsApp: +91 8882767568

## Development Notes

- The application uses Flask-Login for session management
- MongoDB is used for all data storage including files
- File uploads are stored in the `uploads/` directory
- All routes are protected with appropriate security measures
- The application is designed to be beginner-friendly with clear code structure

## License

This project is created for educational purposes and is not licensed for commercial use.

## Support

For technical support or questions:
- Email: pkh99314930@gmail.com
- WhatsApp: +91 8882767568

---

**EduHub** - Your complete university companion for academic success! 🎓
