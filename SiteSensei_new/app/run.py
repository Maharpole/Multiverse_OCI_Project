#!/home/opc/usr/bin/python3.9

#above is a shebang line, please leave intact to direct the python interpreter in oci

from endpoints.routes import app

if __name__ == '__main__':
    app.run(debug=True)
