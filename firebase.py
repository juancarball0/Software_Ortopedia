import firebase_admin
from firebase_admin import credentials, db

# Inicializar la aplicación de Firebase
cred = credentials.Certificate('ruta/a/tu/archivo/clave.json')  # Reemplaza con la ruta de tu archivo JSON
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://<tu-database-name>.firebaseio.com/'  # Reemplaza con tu databaseURL
})

# Ahora puedes usar la base de datos
ref = db.reference('tu_referencia')  # Reemplaza 'tu_referencia' con la referencia deseada
