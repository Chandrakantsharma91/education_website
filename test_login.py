import requests
from bs4 import BeautifulSoup

# Get the login page
response = requests.get('http://127.0.0.1:5000/admin/login')
soup = BeautifulSoup(response.text, 'html.parser')

# Find CSRF token
csrf_input = soup.find('input', {'name': 'csrf_token'})
if csrf_input:
    csrf_token = csrf_input.get('value')
    print('Found CSRF token:', csrf_token)

    # Try login with CSRF token
    login_data = {
        'email': 'pkh99314930@gmail.com',
        'password': 'pk88488848',
        'csrf_token': csrf_token
    }
    login_response = requests.post('http://127.0.0.1:5000/admin/login', data=login_data, allow_redirects=False)
    print('Login status:', login_response.status_code)
    print('Location:', login_response.headers.get('Location', 'No redirect'))
    if login_response.status_code == 302:
        print('Login successful - redirect to dashboard')
    else:
        print('Login response:', login_response.text[:500])
else:
    print('CSRF token not found')