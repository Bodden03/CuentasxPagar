from re import S
from flask import Flask, render_template, request, redirect, url_for, flash,session,Response
from flask_mysqldb import MySQL
import bcrypt
import io as tio
import xlwt
import pymysql
from datetime import date
import requests
import json

app = Flask(__name__)
# Conexion a la Base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'picapollo2'
app.config['MYSQL_DB'] = 'INTEGRACION_2DO_PARCIAL'
mysql = MySQL(app)
# FIN

# Seccion
app.secret_key='mysecretkey'
# FIN


#semilla para encriptamiento
semilla = bcrypt.gensalt()


# Index

@app.route('/')
def index():
    if 'usuario' in session: 
        nombre_user = ['usuario']
        return render_template('index.html')
    else:
        return render_template('login.html')


#------------------FIN--------------------------------

# Concepto_pago

@app.route('/conpago')
def conpago():
    if 'usuario' in session: 
        nombre_user = ['usuario']

        cur=mysql.connection.cursor()
        cur.execute('Select * from t_Concepto_pago')
        data = cur.fetchall()
        return render_template('Concepto_pago/Concepto_pago.html', conpago= data)
    else:
        return render_template('login.html')
    

@app.route('/guardar_conpago', methods=['POST'])
def guardar_conpago():
    if request.method=='POST':
        descripcion = request.form['Descripcion']
        cur=mysql.connection.cursor()
        cur.execute('insert into t_Concepto_pago (descripcion) VALUES (%s)', {descripcion})
        mysql.connection.commit()
        flash('Concepto Pago Agregado')
        return redirect(url_for('conpago'))


@app.route('/editarconpago/<id>')
def editconpago(id):
    cur=mysql.connection.cursor()
    cur.execute('select * from t_Concepto_pago  where id = {0}'.format(id))
    data=cur.fetchall()
    print(data[0])  
    return render_template('Concepto_pago/Editar_conpago.html', conpago= data[0])

@app.route('/update_conpago/<id>', methods=['POST'])
def update_conpago(id):
    if request.method=='POST':
        descripcion=request.form['Descripcion']
        cur=mysql.connection.cursor()
        cur.execute("""
        update t_Concepto_pago
        set descripcion = %s
        where id = %s
        """, (descripcion,id)) 
        mysql.connection.commit()
        return redirect(url_for('conpago'))

@app.route('/eliminarconpago/<string:id>')
def eliminarconpago(id):    
    cur=mysql.connection.cursor()
    cur.execute('Delete from t_Concepto_pago where id = {0}'. format(id))
    mysql.connection.commit()
    flash('concepto pago Eliminado')
    return redirect(url_for('conpago'))



#Proveedores

@app.route('/proveedores')
def proveedores():

    cur=mysql.connection.cursor()
    cur.execute("""
Select
Nombre,
tipo_persona,
Rnc, 
Balance, 
t_proveedores.Estado
from t_proveedores
     """)
    data = cur.fetchall()
    return render_template('Proveedores/Proveedores.html')


# Insert to proveedores
@app.route('/guardar_proveedor', methods=['POST'])
def guardar_proveedor():
    if request.method=='POST':
        name = request.form['nombre']
        tipo_persona = request.form['tipo_persona']
        cedula = request.form['cedula']
        balance = request.form['balance']
        estado = request.form['estado']
        cur = mysql.connection.cursor()
        cur.execute("""
        Insert into t_proveedores 
        (nombre, tipo_persona, rnc, balance, estado)
        Values (%s,%s,%s,%s,%s)""", (name, tipo_persona, cedula, balance, estado))
        mysql.connection.commit()
        flash('Proveedor Agregado')
        return redirect(url_for('conproveedores'))
        
        
# Editar Proveedor

@app.route('/editarproveedor/<id>')
def editproveedor(id):
    cur=mysql.connection.cursor()
    cur.execute('select * from t_proveedores  where ID_PROVEEDOR = {0}'.format(id))
    data=cur.fetchall()
    print(data[0])  
    return render_template('proveedores/Editar_proveedor.html', proveedores= data[0])

@app.route('/update_proveedor/<id>', methods=['POST'])
def update_proveedor(id):
    if request.method=='POST':
        name = request.form['nombre']
        tipo_persona = request.form['tipo_persona']
        cedula = request.form['cedula']
        balance = request.form['balance']
        estado = request.form['estado']
        cur=mysql.connection.cursor()
        cur.execute("""
        update t_proveedores
        set nombre = %s,
        tipo_persona =%s,
        rnc= %s,
        balance = %s, 
        estado = %s
        where ID_PROVEEDOR = %s
        """, (name,tipo_persona,cedula,balance,estado,id)) 
        mysql.connection.commit()
        return redirect(url_for('conproveedores'))


    # Eliminar proveedor


@app.route('/eliminarproveedor/<string:id>')
def eliminarproveedor(id):    
    cur=mysql.connection.cursor()
    cur.execute('Delete from t_Proveedores where ID_PROVEEDOR = {0}'. format(id))
    mysql.connection.commit()
    flash('Proveedor Eliminado')
    return redirect(url_for('conproveedores'))





# Consulta Proveedores

@app.route('/conproveedores')
def conproveedores():
    if 'usuario' in session: 
        nombre_user = ['usuario']

        cur = mysql.connection.cursor()
        cur.execute("""
 Select
ID_PROVEEDOR,
Nombre,
tipo_persona.descripcion as tipo_persona,
Rnc, 
Balance, 
t_proveedores.Estado
from t_proveedores
join tipo_persona on (t_proveedores.tipo_persona=tipo_persona.id)
group by  ID_PROVEEDOR     
        """)
        data = cur.fetchall()


    
        return render_template('proveedores/Consulta_proveedores.html', proveedores=data )
    else:
        return render_template('login.html')



# ======================================================================================================

#          Documentos

@app.route('/documento')
def documento():
    if 'usuario' in session: 
        nombre_user = ['usuario']
    

       #proveedor  to listbox
        cur=mysql.connection.cursor()
        cur.execute('select ID_PROVEEDOR, nombre from t_proveedores')
        data=cur.fetchall()

        #Conceptopago to listbox
        cur2=mysql.connection.cursor()
        cur2.execute('select ID, Descripcion from T_CONCEPTO_PAGO')
        data2=cur2.fetchall()


       #Grid Documentos

        cur3 = mysql.connection.cursor()
        cur3.execute("""
select 
d.ID_DOCUMENTO,
p.nombre,
p.RNC,
cp.Descripcion,
d.Numero_factura,
d.Numero_documento,
d.Fecha_documento,
d.Fecha_registro,
d.monto,
bpd.Balance
from T_DOCUMENTO d 
join T_PROVEEDORES p  on (d.ID_PROVEEDOR = p.ID_PROVEEDOR)
join T_CONCEPTO_PAGO cp on (d.ID_PAGO = cp.id)
left join Balance_Proveedor_documento bpd on (d.ID_DOCUMENTO=bpd.ID_Documento)
group by ID_DOCUMENTO
        
        """)
        data3 = cur3.fetchall()


        return render_template('Documentos/documento.html', proveedor=data, cuenta=data2, documento=data3)
    else:
        return render_template('login.html')


@app.route('/webservice')
def webservice():
    
    cur3 = mysql.connection.cursor()
    cur3.execute("""
select 
d.ID_DOCUMENTO,
p.nombre,
p.RNC,
cp.Descripcion,
d.Numero_factura,
d.Numero_documento,
d.Fecha_documento,
d.Fecha_registro,
d.monto,
bpd.Balance
from T_DOCUMENTO d 
join T_PROVEEDORES p  on (d.ID_PROVEEDOR = p.ID_PROVEEDOR)
join T_CONCEPTO_PAGO cp on (d.ID_PAGO = cp.id)
left join Balance_Proveedor_documento bpd on (d.ID_DOCUMENTO=bpd.ID_Documento)
where Numero_documento is null group by ID_DOCUMENTO
        
        """)
    data3 = cur3.fetchall()
    url = 'https://accountingaccountapi20211205021409.azurewebsites.net/api/AccountingSeat/Register'
    
    for resultado in data3:

        test = json.dumps( {
  "description": resultado[3],
  "auxiliar": 6,
  "currencyCode": 1,
  "detail": {
    "cuentaCR": "4",
    "cuentaDB": "82",
    "amountCR": resultado[8],
    "amountDB": resultado[8]
  }
})





        cabe = {'Content-Type': 'application/json'}
    #response = requests.post(url, data=json.dumps(test), headers=cabe)
        response = requests.post(url, data=test, json=test, headers=cabe)

        print(response.url)
    #if response.status_code == 200: 
        dataresult = response.json()
        print(dataresult['id'])
        flash(dataresult['id'])
        cur=mysql.connection.cursor()
        cur.execute("""
        update T_DOCUMENTO
        set Numero_documento = %s
        where Numero_documento is null and ID_DOCUMENTO = %s
        """, (dataresult['id'],resultado[0])) 
        mysql.connection.commit()
        flash(response.content)
    return redirect(url_for('documento'))

# Insert to Documentos
@app.route('/guardar_documento', methods=['POST'])
def guardar_documento():
    if request.method=='POST':
        proveedor = request.form['proveedor']
        pago = request.form['pago']
        factura = request.form['factura']
        fecha = request.form['fecha']
        monto = request.form['monto']
        cur = mysql.connection.cursor()
        cur.execute("""
        Insert into t_documento 
        (ID_PROVEEDOR, ID_PAGO,
          Numero_factura,
          Fecha_documento,Monto)
        Values (%s,%s,%s,%s,%s)""", (proveedor, pago, factura, fecha,monto))
        mysql.connection.commit()
        flash('Documento Agregado')
        return redirect(url_for('documento'))


        # Consulta Documentos

@app.route('/condocumento')
def condocumento():

    if 'usuario' in session: 
        nombre_user = ['usuario']


        cur = mysql.connection.cursor()
        cur.execute("""
 Select
ID_PROVEEDOR,
Nombre,
tipo_persona.descripcion as tipo_persona,
Rnc, 
Balance, 
t_proveedores.Estado
from t_proveedores
join tipo_persona on (t_proveedores.tipo_persona=tipo_persona.id)
        
        """)
        data = cur.fetchall()
        return render_template('proveedores/Consulta_proveedores.html', proveedores=data)
    else:

        return render_template('login.html')


@app.route('/eliminardocumento/<string:id>')
def eliminardocumento(id):    
    cur=mysql.connection.cursor()
    cur.execute('Delete from t_documento where ID_DOCUMENTO = {0}'. format(id))
    mysql.connection.commit()
    flash('Documento Eliminado')
    return redirect(url_for('documento'))



# ----------------------------------------------


#======================================LOGIN=============================================================

# Seccion
app.secret_key='mysecretkey'
# FIN


#Login 

@app.route('/login')
def login():
    return render_template('/login.html')


#Valida Login

@app.route('/logearse', methods=['GET','POST'])
def logearse():


    if(request.method=='GET'):
        if 'usuario' in session:

            return redirect(url_for('/'))
        else: return redirect(url_for('login'))
    else:
        nombre = request.form['user']
        passw= request.form['contra']
        passwe = passw.encode("utf-8")
        #contraE = bcrypt.hashpw(passwe, semilla)
        
        cur = mysql.connection.cursor()
        sQuery = 'select UserName , password from user where password = %s and Username = %s'
        cur.execute(sQuery,[passw,nombre])
        usuario = cur.fetchone()
        cur.close()


        if (usuario != None): 
            

            session['usuario'] =usuario[0]
            session['pass'] =usuario[1]
            return render_template('index.html')


        else: 
            flash('Usuario/contraseña incorrectos', "alert-warning")
            return redirect(url_for('login'))

        

    return 'hola'



    #-==========================================================================
    #==================================Reportes CSV==============================

#Listados de Candidatos
@app.route('/reporteProveedor', methods=['POST'])
def reporteProveedor():
    if request.method == 'POST': 
        fechad= request.form['fechan']
        fechah= request.form['fechafin']
        cur = mysql.connection.cursor()
        cur.execute("""
    
    Select 
    T_PROVEEDORES.ID_PROVEEDOR,
    Nombre,
    tp.descripcion,
    RNC, 
    T_PROVEEDORES.Balance, 
    Max(bpd.balance),
    max(T_DOCUMENTO.Fecha_documento),
    T_PROVEEDORES.Estado
    from T_PROVEEDORES 
    join tipo_persona  tp on (T_PROVEEDORES.Tipo_Persona = tp.id) 
    left join T_DOCUMENTO on  (T_PROVEEDORES.ID_PROVEEDOR = T_DOCUMENTO.ID_PROVEEDOR)
    left join  Balance_Proveedor_documento bpd on (T_PROVEEDORES.ID_PROVEEDOR = bpd.ID_PROVEEDOR)
     where DATE(T_PROVEEDORES.fechacrea) between  '{0}' and '{1}'""".format(fechad, fechah) .format(fechah))
        result = cur.fetchall()
        print(result)
        output = tio.BytesIO()
        workbook = xlwt.Workbook()
        sh  = workbook.add_sheet('Candidatos')

        sh.write(0, 0, 'Id proveedor')
        sh.write(0, 1, 'Nombre')
        sh.write(0, 2, 'Tipo Persona')
        sh.write(0, 3, 'RNC/Cedula')
        sh.write(0, 4, 'Balance inicial')
        sh.write(0, 5, 'Balance ult Transaccion')
        sh.write(0, 6, 'Fecha Ult Transaccion')
        sh.write(0, 7, 'Estado')

        idx = 0
        for now in result:
            sh.write(idx+1, 0, int(now[0]))
            sh.write(idx+1, 1, now[1])
            sh.write(idx+1, 2, now[2])
            sh.write(idx+1, 3, now[3])
            sh.write(idx+1, 4, now[4])
            sh.write(idx+1, 5, str(now[5]))
            sh.write(idx+1, 6, now[6])
            sh.write(idx+1, 7, now[7])

            idx +=1

        workbook.save(output)
        output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})

#---------------------------------------------------------------------------------------------------------------------------------------------

#Listados de proveedores
@app.route('/reportedocumento', methods=['POST'])
def reportedocumento():
    if request.method == 'POST': 
        fechad= request.form['fechan']
        fechah= request.form['fechafin']
        cur = mysql.connection.cursor()
        cur.execute("""
    
    Select 
    T_PROVEEDORES.ID_PROVEEDOR,
    Nombre,
    tp.descripcion,
    RNC, 
    T_PROVEEDORES.Balance, 
    Max(bpd.balance),
    max(T_DOCUMENTO.Fecha_documento),
    T_PROVEEDORES.Estado
    from T_PROVEEDORES 
    join tipo_persona  tp on (T_PROVEEDORES.Tipo_Persona = tp.id) 
    left join T_DOCUMENTO on  (T_PROVEEDORES.ID_PROVEEDOR = T_DOCUMENTO.ID_PROVEEDOR)
    left join  Balance_Proveedor_documento bpd on (T_PROVEEDORES.ID_PROVEEDOR = bpd.ID_PROVEEDOR)
     where DATE(T_PROVEEDORES.fechacrea) between  '{0}' and '{1}'""".format(fechad, fechah) .format(fechah))
        result = cur.fetchall()
        print(result)
        output = tio.BytesIO()
        workbook = xlwt.Workbook()
        sh  = workbook.add_sheet('Candidatos')

        sh.write(0, 0, 'Id proveedor')
        sh.write(0, 1, 'Nombre')
        sh.write(0, 2, 'Tipo Persona')
        sh.write(0, 3, 'RNC/Cedula')
        sh.write(0, 4, 'Balance inicial')
        sh.write(0, 5, 'Balance ult Transaccion')
        sh.write(0, 6, 'Fecha Ult Transaccion')
        sh.write(0, 7, 'Estado')

        idx = 0
        for now in result:
            sh.write(idx+1, 0, int(now[0]))
            sh.write(idx+1, 1, now[1])
            sh.write(idx+1, 2, now[2])
            sh.write(idx+1, 3, now[3])
            sh.write(idx+1, 4, now[4])
            sh.write(idx+1, 5, str(now[5]))
            sh.write(idx+1, 6, now[6])
            sh.write(idx+1, 7, now[7])

            idx +=1

        workbook.save(output)
        output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=employee_report.xls"})


#---------------------------------------------------------------------------------------------------------------------------------------------



@app.route('/salir')
def salir(): 
    session.clear()
    return redirect(url_for('login'))



if __name__=='__main__':
    app.run(port=3000, debug = True)