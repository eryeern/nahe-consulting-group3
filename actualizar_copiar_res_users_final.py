#!/usr/bin/python
# CUIDADO elegir bin del python correcto
# modificar la primer linea con which python.
# si está en un enviroment de pyhton usar la primer linea 
# Este script se testeo del 9 al 11 y anduvo. Tambien del 10 al 11 anduvo. Tambien anda desde odoo 8 a 11
import sys
import xmlrpc.client
import ssl

user_o = 'completar' #el usuario de odoo origen
user_d = 'completar' #el usuario de odoo destino
pwd_o = 'completar' # contrasenia de usuario odoo origen
pwd_d = 'completar' # contrasenia de usuario destino
dbname_o = 'completar'  # nombre de base de datos origen
dbname_d = 'completar' # nombre de base de datos destino
web_o = 'completar' # ip o dir web del origen
web_d = 'completar' # ip o dir web del destino
# datos de los modelos y campos
model_o = 'res.users' # nombre del modelo de origen
model_d = 'res.users' #nombre del modelo del destino
idant_o = 'x_id_anterior' # TO DO  generar el x_id_anterior nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa. (tiene que ser un campo existente en el modelo model_d)
#este campo hay que crearlo en el modelo 
# Es necesario crear el campo x_id_anterior en el model_d para usarlo en la variable idant_o
condi1_o = [('active','=','true'),('id', '>', '1')]
campos = ['id', 'active', 'name', 'login', 'company_id', 'partner_id', 'in_group_1', 'password_crypt']

# esto genera el contexto para que se conecte
gcontext = ssl._create_unverified_context()

# Get the uid origen de los datos. modificar weborigen por ip:puerto
sock_common_o = xmlrpc.client.ServerProxy ('http://www2.electronicajck.com/xmlrpc/common',context=gcontext)
uid_o = sock_common_o.login(dbname_o, user_o, pwd_o)

# Get the uid destino de los datos
sock_common_d = xmlrpc.client.ServerProxy ('http://127.0.0.1:8068/xmlrpc/common',context=gcontext)
uid_d = sock_common_d.login(dbname_d, user_d, pwd_d)

#reemplazar el valor de la ip o url del servidor de origen con su puerto
sock_o = xmlrpc.client.ServerProxy('http://www2.electronicajck.com/xmlrpc/object',context=gcontext)

#reemplazar el valor de la ip o url del servidor de destino con su puerto
sock_d = xmlrpc.client.ServerProxy('http://127.0.0.1:8068/xmlrpc/object',context=gcontext)


print("===========================================")
print("Se van a importar los siguientes registros:")
print("Web de origen..: ",web_o)
print("Modelo a migrar: ",model_o)
print("Condicion regis: ",condi1_o)
print("-------------------------------------------")
print("Se van a actualizar/crear los siguientes registros:")
print("Web de destino.: ",web_d)
print("Modelo migrado.: ",model_d)
print("Campo id anter.: ",idant_o)
print("===========================================")

# Busqueda en el odoo del origen solo las companias primero y luego los individuos 
# Busqueda en el odoo del origen los registros que cumplan con la condicion condi1_o todas las en este caso []
# las buscamos en el destino, si existren le actualizamos los valores_update
# si no existen en el destino las creamos, con los valores_update despues del else.
registro_ids_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'search',condi1_o)
print ("Cantidad de", model_o," con la condicion: ", condi1_o, " leidos desde el origen:",len(registro_ids_o))

# Iniciar los contadores
x=0
j=0
ec=0
ea=0

for i in registro_ids_o:
       # Leemos la info de los registros en la base origen 
    print(" cada registro de origen lo llamamos i, contiene lo siguiente: ", i)
    print ("Verificando en el origen el modelo: ",model_o," el objeto con id: ", i)
    registro_data_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'read',i,campos)
    print ("Registro  Obtenido: ", registro_data_o)
    #obteniendo la ID original para buscar en el destino
    clave=registro_data_o['id']
    nombre_o=registro_data_o['name']
    respartner_anterior=registro_data_o['partner_id']
    print("el partner_id anterior es la variable respartner_anterior valor: ",respartner_anterior)
    #Busqueda por id_anterior en el destino para ver si existe y se actualiza o hay que crearlo.
    # si el ODOO DE DESTINO tiene mas campos requeridos puede fallar, pero se agregan en la variable campos. 
    # conviene importar antes de seguir instalando muchos modulos.
    # BUSCAMOS EN EL DESTINO SI EXISTE un res.users con el valor de idant_o (tiene que existir ente valor en el modelo) igual a clave
    registro_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',[(idant_o,'=',clave)])
    #vamos a usar el campo ref pero hay que usar en un futuro x_id_anterior de res.partner
    nuevo_respartner_id = sock_d.execute(dbname_d,uid_d,pwd_d,'res.partner','search',[('ref','=',respartner_anterior[0])])
    if nuevo_respartner_id:
        print("el valor de nuevo_respartner_id es: ",nuevo_respartner_id)
        grabar_nuevo_partner_id=nuevo_respartner_id.pop(0)
        print("el valor de grabar_nuevo_partner_id es: ",grabar_nuevo_partner_id)
    else:
        print("no encontado nuevo_respartner_id")
        grabar_nuevo_partner_id=41
    # si se econtro el registro se actualiza
    if registro_id_d:
        print ("Encontrado en el nuevo servidor", clave, "con nombre", nombre_o,"lo vamos a actualizar") 
        #aca nombramos variables para luego llamarlas dentro de valores_update, en especial las que devuelven un diccionario. 
        valores_update = {
            'active': registro_data_o['active'],
            'name': registro_data_o['name'],
            'login': registro_data_o['login'],
            'password_crypt': registro_data_o['password_crypt'],
            #'company_id': registro_data_o['company_id'], creo que no es necesario ahora vemos. 
            'partner_id':  grabar_nuevo_partner_id,
            'in_group_10': registro_data_o['in_group_1'],
            idant_o: registro_data_o['id']
            }
        #esta linea es la encargada de actualizar en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'write',registro_id_d,valores_update)
            print (return_id,"exito al actualizar user ",nombre_o)
        except:
            print("Ha ocurrido un error al intentar actualizar el user: ",nombre_o)
            ea+=1
        x+=1
    # si no se econtro el registro en el destino se crea
    else:
        print ("No se encontro en el destino: ",nombre_o," vamos a crearlo.")
        valores_update = {
            'active': registro_data_o['active'],
            'name': registro_data_o['name'],
            'login': registro_data_o['login'],
            'password_crypt': registro_data_o['password_crypt'],
            #'company_id': registro_data_o['company_id'], creo que no es necesario ahora vemos. 
            #'partner_id': registro_data_d['partner_id'],
            'in_group_10': registro_data_o['in_group_1'],#los in group es algo de los permisos para grupos de usuarios revisar mas a fondo luego
            idant_o: registro_data_o['id']
            }
        #esta linea es la encargada de crear en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'create',valores_update)
            print (return_id,"exito al crear ",nombre_o)
        except:
            print("Ha ocurrido un error al intentar crear el user: ",nombre_o ) 
            ec+=1
        #print (registro_data_d)
        j+=1
print ("Cantidad de registros actualizados: ",x)
print ("Cantidad de actualizados con error: ",ea)
print ("Cantidad de registros creados: ",j)
print (" Cantidad de errores al crear: ",ec)