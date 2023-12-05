from flask import Flask
from flask import render_template, request, redirect, Response, url_for, session
from flask_mysqldb import MySQL,MySQLdb # pip install Flask-MySQLdb
import numpy as np
#from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model


# Ruta al modelo descargado en tu entorno local
ruta_modelo_local = 'modelo_enfermedades_regresion.h5'

app = Flask(__name__,template_folder='views')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '19151423' #agregue mi contraseña
app.config['MYSQL_DB'] = 'proyectorn2'
app.config['MYSQL_PORT'] = 3306  # Añade esta línea @@@JUNIOR: CAMBIE DE PUERTO 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def home():
    session['id_rol']=0
    return render_template('index.html')   

@app.route('/admin')
def admin():
    return render_template('Admin/admin.html')   

@app.route('/perfil')
def perfil():
    return render_template('User/perfil.html')  

@app.route('/reportes')
def reporte():
    return render_template('User/reportes.html')  

# ACCESO---LOGIN
@app.route('/acceso-login', methods= ["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password,))
        account = cur.fetchone()
        if account:
            session['logueado'] = True
            session['id'] = account['id']
            session['id_rol']=account['id_rol']
            
            if session['id_rol']==1:
                return render_template("Admin/admin.html")
            elif session ['id_rol']==2:
                return render_template("User/usuario.html")
        else:
            return render_template('index.html',mensaje="Usuario O Contraseña Incorrectas")

#registro---
@app.route('/registro')
def registro():
    return render_template('registro.html')  

@app.route('/crear-registro', methods= ["GET", "POST"])
def crear_registro(): 
    
    correo=request.form['txtCorreo']
    password=request.form['txtPassword']
    
    cur = mysql.connection.cursor()
    cur.execute(" INSERT INTO usuarios (correo, password, id_rol) VALUES (%s, %s, '2')",(correo,password))
    mysql.connection.commit()
    
    return render_template("index.html",mensaje="Usuario Registrado Exitosamente")
#-----------------------------------

#Registro-diagnostico
@app.route('/registrodiagnostico')
def registrodiag():
    return render_template('User/diagnostico.html')  

@app.route('/crear-registro2', methods= ["GET", "POST"])
def crear_registro_diag(): 
    
    paciente=request.form['txtpaciente']
    usuario=request.form['txtusuario']
    fecha=request.form['txtfecha']
    diagnostico=request.form['txtdiagnostico']
    cur = mysql.connection.cursor()
    cur.execute(" INSERT INTO historia_clinica (id_paciente, id_usuario, fecha_atencion, Diagnostico) VALUES (%s, %s, %s, %s)",(paciente,usuario,fecha,diagnostico))
    mysql.connection.commit()
    
    return render_template("User/diagnostico.html",mensaje="Diagnostico Registrado Exitosamente")

#Registro-pacientes
@app.route('/registropacientes')
def registropaciente():
    return render_template('User/paciente.html')  

@app.route('/registro-paciente', methods=["GET", "POST"])
def crear_registro_paciente():
    nombre = request.form['txtnombre']
    apellido = request.form['txtapellido']
    dni = request.form['txtdni']
    cel = request.form['txtcel']
    direccion = request.form['txtdireccion']

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO paciente (nombre, apellido, DNI, cel, direccion) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, apellido, dni, cel, direccion))
        mysql.connection.commit()
        registro_exitoso = True  # Registro exitoso
        mensaje = "Paciente Registrado Exitosamente"
    except Exception as e:
        mysql.connection.rollback()
        registro_exitoso = False  # Error en el registro
        mensaje = "Error al registrar paciente: " + str(e)
    finally:
        cur.close()
    return render_template("registropaciente.html", mensaje=mensaje, registro_exitoso=registro_exitoso)
# funcion para predicir con la red neuronal

@app.route('/predict', methods=['GET'])
def predict():
    #cargamos el modelo desarrollado en google colad
    sintoma_1 = float(request.args.get('sintoma_1', 0.0))
    sintoma_2 = float(request.args.get('sintoma_2', 0.0))
    sintoma_3 = float(request.args.get('sintoma_3', 0.0))
    sintoma_4 = float(request.args.get('sintoma_4', 0.0))
    sintoma_5 = float(request.args.get('sintoma_5', 0.0))
    sintoma_6 = float(request.args.get('sintoma_6', 0.0))
    sintoma_7 = float(request.args.get('sintoma_7', 0.0))
    sintoma_8 = float(request.args.get('sintoma_8', 0.0))
    sintoma_9 = float(request.args.get('sintoma_9', 0.0))
    sintoma_10 = float(request.args.get('sintoma_10', 0.0))
    sintoma_11 = float(request.args.get('sintoma_11', 0.0))
    sintoma_12 = float(request.args.get('sintoma_12', 0.0))
    sintoma_13 = float(request.args.get('sintoma_13', 0.0))
    sintoma_14 = float(request.args.get('sintoma_14', 0.0))
    sintoma_15 = float(request.args.get('sintoma_15', 0.0))
    model = load_model(ruta_modelo_local)
    # Crear un array con los datos de entrada
    input_data = np.array([[sintoma_1,sintoma_2,sintoma_3,sintoma_4,sintoma_5,sintoma_6,sintoma_7,sintoma_8,sintoma_9,sintoma_10,sintoma_11,sintoma_12,sintoma_13,sintoma_14,sintoma_15]])
    # Realizar la predicción
    prediction = model.predict(input_data)

    # Si has normalizado los datos de salida, deshaz la normalización
    # En este caso, supongo que tus datos de salida están en el rango de 0 a 10
    prediction_original_scale = prediction * 10.0
    prediction_as_int = int(prediction_original_scale[0])
    resultado_mapa = {
        0: 'Resfriado común',
        1: 'Gripe (Influenza)',
        2: 'Asma',
        3: 'Enfermedad pulmonar obstructiva crónica ',
        4: 'Neumonía',
        5: 'Bronquitis aguda',
        6: 'Tuberculosis',
        7: 'Fibrosis pulmonar',
        8: 'Apnea del sueño',
        9: 'Rinitis alérgica',
    }
    resultado_correspondiente = resultado_mapa.get(prediction_as_int, 'Resultado no definido')
    # Puedes devolver el resultado como parte de la respuesta
    return f'Resultado correspondiente: {resultado_correspondiente}'



#-----LISTAR USUARIOS-------------
@app.route('/listar', methods= ["GET", "POST"])
def listar(): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    
    return render_template("Admin/listar_usuarios.html",usuarios=usuarios)

#-----LISTAR PACIENTES-------------
@app.route('/listarpacientes', methods= ["GET", "POST"])
def listarpacientes(): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM paciente")
    paciente = cur.fetchall()
    cur.close()
    
    return render_template("Admin/listar_pacientes.html",paciente=paciente)
#-----GENERAR RECETA-------------
@app.route('/Receta', methods=["GET", "POST"])
def GenerarReceta():
    receta = None
    
    if request.method == "POST":
        dni = request.form.get("dni")
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT concat_ws(' ', p.nombre, p.apellido) AS Paciente, p.DNI, p.cel, p.direccion, 
                   d.fecha_atencion, e.nomEnfermedad AS Enfermedad, t.nomTratamiento AS Tratamiento, 
                   t.receta, u.nombre as Doctor 
            FROM paciente p  
            INNER JOIN diagnostico d ON p.id = d.id 
            INNER JOIN enfermedad e ON e.idEnfermedad = d.id_Enfermedad 
            INNER JOIN tratamiento t ON t.idTratamiendo = e.id_Tratamiento 
            INNER JOIN usuarios u ON u.id = d.id_usuario 
            WHERE p.DNI = %s
        """, (dni,))
        
        receta = cur.fetchall()
        cur.close()
    # Si es una solicitud GET o POST, simplemente renderiza la plantilla
    return render_template("User/reportes.html", receta=receta)

#------------------------------------
if __name__ == '__main__':
    app.secret_key = "pinchellave"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
