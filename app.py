from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import hashlib
import requests
import json
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
THINGSPEAK_URL, app.secret_key = 'https://thingspeak.mathworks.com/channels/3000780/field/1.json','https://thingspeak.mathworks.com/channels/3000780/field/1.json'  # Cambia esto por una clave secreta segura

# Credenciales de usuario (en producción, usa una base de datos)
USERS = {
    'admin': 'admin123',  # En producción, usa hashes de contraseñas
    'user': 'password123'
}

def hash_password(password):
    """Función para hashear contraseñas (opcional, para mayor seguridad)"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorador para requerir login en rutas protegidas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    """Landing page principal"""
    # Si quieres redirigir al dashboard si ya está logueado, descomenta la siguiente línea:
    # if 'logged_in' in session and session['logged_in']:
    #     return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        # Manejar login AJAX
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            
            # Validar credenciales
            if username in USERS and USERS[username] == password:
                session['logged_in'] = True
                session['username'] = username
                return jsonify({'success': True, 'message': 'Login exitoso'})
            else:
                return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401
        
        # Manejar login tradicional (formulario)
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas', 'error')
    
    # Si ya está logueado, redirigir al dashboard
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Página principal con los datos (anteriormente index)"""
    data = get_thingspeak_data()
   
    if not data:
        flash("Error al cargar los datos de ThingSpeak", "error")
        return render_template('dashboard.html', error=True)
   
    # Procesar los datos para la vista
    channel_info = data.get('channel', {})
    feeds = data.get('feeds', [])
   
    # Preparar datos para el gráfico
    chart_data = []
    for feed in feeds:
        if feed.get('field1'):
            chart_data.append({
                'timestamp': feed['created_at'],
                'value': float(feed['field1']),
                'formatted_time': format_timestamp(feed['created_at'])
            })
   
    # Estadísticas básicas
    values = [item['value'] for item in chart_data]
    stats = {
        'count': len(values),
        'min': min(values) if values else 0,
        'max': max(values) if values else 0,
        'avg': sum(values) / len(values) if values else 0,
        'latest': values[-1] if values else 0
    }
   
    return render_template('dashboard.html',
                         channel_info=channel_info,
                         chart_data=chart_data,
                         stats=stats,
                         username=session.get('username'))

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/check_auth')
def check_auth():
    """Endpoint para verificar si el usuario está autenticado (para AJAX)"""
    return jsonify({
        'authenticated': 'logged_in' in session and session['logged_in'],
        'username': session.get('username', '')
    })

def get_thingspeak_data():
    """Obtiene los datos de ThingSpeak"""
    try:
        response = requests.get(THINGSPEAK_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return None

def format_timestamp(timestamp_str):
    """Convierte timestamp UTC a formato legible"""
    try:
        utc_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Convertir a zona horaria local (puedes cambiar esto)
        local_tz = pytz.timezone('America/Santo_Domingo')  # Ajusta según tu zona horaria
        local_time = utc_time.astimezone(local_tz)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

@app.route('/water-level')
@login_required
def water_level():
    """Página de monitoreo de nivel de agua"""
    return render_template('water-level.html', username=session.get('username'))

@app.route('/history')
@login_required
def history():
    """Página de historial"""
    return render_template('history.html', username=session.get('username'))

@app.route('/config')
@login_required
def config():
    """Página de configuración de usuario"""
    return render_template('config.html', username=session.get('username'))

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Actualizar perfil de usuario"""
    # En una aplicación real, aquí guardarías los datos en una base de datos
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    # Simulamos una actualización exitosa
    flash('Perfil actualizado correctamente', 'success')
    return redirect(url_for('config'))



@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    """Cambiar contraseña de usuario"""
    username = session.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Verificar que la contraseña actual sea correcta
    if username not in USERS or USERS[username] != current_password:
        flash('La contraseña actual es incorrecta', 'error')
        return redirect(url_for('config'))
    
    # Verificar que las nuevas contraseñas coincidan
    if new_password != confirm_password:
        flash('Las nuevas contraseñas no coinciden', 'error')
        return redirect(url_for('config'))
    
    # En una aplicación real, aquí actualizarías la contraseña en la base de datos
    # Por ahora, actualizamos el diccionario de usuarios (solo para demo)
    USERS[username] = new_password
    
    flash('Contraseña actualizada correctamente', 'success')
    return redirect(url_for('config'))

# Envio de correos
@app.route('/send_email', methods=['POST'])
def send_email():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Configuración del servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'contactofloppy@gmail.com'
    smtp_password = 'floppy123'

    # Crear el mensaje de correo
    msg = MIMEText(message)
    msg['Subject'] = 'Nuevo mensaje de contacto'
    msg['From'] = email
    msg['To'] = smtp_username

    # Enviar el correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        flash('Correo enviado correctamente', 'success')
    except Exception as e:
        flash(f'Error al enviar el correo: {str(e)}', 'error')
        return redirect(url_for('landing'))

    return redirect(url_for('landing'))


if __name__ == '__main__':
    app.run(debug=True)