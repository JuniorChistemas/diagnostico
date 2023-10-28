from flask import Flask
from flask import render_template, request, redirect, Response, url_for, session
from flask_mysqldb import MySQL,MySQLdb # pip install Flask-MySQLdb

app = Flask(__name__,template_folder='views')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '19151423' #agregue mi contraseña
app.config['MYSQL_DB'] = 'proyectorn'
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


#----------------------------------

if __name__ == '__main__':
    app.secret_key = "pinchellave"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
