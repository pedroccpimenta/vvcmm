from flask import Flask, render_template, request, redirect, url_for, session
import json
import openpyxl
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Hardcoded login credentials


import socket
hostname=socket.gethostname()
print ("hostname:", hostname)

if (hostname=="DESKTOP-O5TUSN4") :
    servfile='./etc/secrets/staleciurlac-efa9f27b99af.json'
    servfile='./etc/secrets/d4maia-gcells2mysql-062d106bc40f.json'
    othu='https://staleciurlac.onrender.com/'
    with open('./etc/secrets/vvcm_key.json', 'r') as fh:
        LOGIN_KEYWORD = json.loads(fh.read())['key']

    #servfile='./etc/secrets/knot-433216-030beb26e003.json'
else:
    servfile='/etc/secrets/staleciurlac-efa9f27b99af.json'
    servfile='/etc/secrets/d4maia-gcells2mysql-062d106bc40f.json'
    othu='http://127.0.0.1:5000/'
    with open('/etc/secrets/vvcm_key.json', 'r') as fh:
        LOGIN_KEYWORD = json.loads(fh.read())['key']

print ('LOGIN_KEYWORD', LOGIN_KEYWORD)


"""
Logbook: https://docs.google.com/document/d/1RIQ4LQFTd3fj13Boa7eXlJf1Krh9P9gpjHwVfd84eAs
"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("keyword") == LOGIN_KEYWORD:
            session["logged_in"] = True
            return redirect(url_for("map"))
        else:
            return render_template("login.html", error="Chave inválida.")
    return render_template("login.html")

@app.route("/map")
def map():
    if not session.get("logged_in"):
        return redirect(url_for("login"))


    def dms_to_decimal(dms):
        """
        Converts coordinates in DMS (Degrees, Minutes) format to decimal degrees.
        :param dms: A string with coordinates (e.g., 'N 46° 13.282’ E 012° 52.536’')
        :return: Tuple with decimal latitude and longitude
        """
        dms = dms.replace('°', '').replace('’', '').split()
        print (dms)
        
        lat_direction = dms[0]
        lat_degrees = float(dms[1])
        lat_minutes = float(dms[2])
        
        lon_direction = dms[3]
        lon_degrees = float(dms[4])
        lon_minutes = float(dms[5])
        
        # Convert to decimal degrees
        latitude = lat_degrees + lat_minutes / 60
        longitude = lon_degrees + lon_minutes / 60
        
        # Apply negative sign for S and W
        if lat_direction == 'S':
            latitude = -latitude
        if lon_direction == 'W':
            longitude = -longitude
        
        return latitude, longitude

    points = [
        {"name": "Point 1", "lat": 37.7749, "lng": -122.4194},  # San Francisco
        {"name": "Point 2", "lat": 34.0522, "lng": -118.2437},  # Los Angeles
    ]

    import pygsheets

    gc = pygsheets.authorize(service_file=servfile)

    sheet_id = '1g70Tsb-nQpxrZCuCoTz-fnM01IA8u6x_cVuRx7h7e5k'  # Replace with the actual file ID
    
    try:
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet[0]  # Indexing starts at 0
        data = worksheet.get_all_values()
    except Exception as err:
        print (f"Err: |{str(err)}|.")
        if str(err)=='Unable to find the server at oauth2.googleapis.com':
            pass    
        else:
            exit(-1)


    points=[]
    print("Data:--------------------------------------------------------")
    print(data)
    ns=0
     
    for l in data:  
        agora = str(datetime.datetime.now())[0:16]
        if (ns>0) and l[0]!=None:
            print(f"NS: {ns}:",l[0], l[1]+ l[2])
            if l[0]!="":
                nome=l[0]
                latlon = l[4]
                #print ("latlon:", latlon)

                [latitude, longitude] = latlon.split(",")
                latitude = float(latitude)
                longitude = float(longitude)
                if type(l[3])==type(None):
                    fotourl=""
                else:
                    fotourl=l[3].replace('?usp=drive_link', '')
    
                fotourl=fotourl.replace('/view', '/preview')
                #print(fotourl)
                if fotourl=="":
                    fotourl='images/vespaasiatica.jpg'
                fotourl='./images/vespaasiatica.jpg'

                points.append( {"name": nome, "lat": latitude, "lng": longitude, 'foto':fotourl, 'tipo':l[10], 'id':l[0],
                    'address':l[3], 'suporte':l[5], 'altura':l[8], 'tamanho':l[9], 'reportado':l[11], 'contacto':l[12], 
                    'reportado':l[11], 'tstamp':agora, 'notifica':l[14], 'interv':l[16], 'método':l[18] })
                ns=ns+1

            else:
                break
        else:
            ns=ns+1
            pass

    # https://iconduck.com/icons/65479/ruins


    poly=[]
    with open ('./static/limconc.geojson') as fh:
        poly=json.loads(fh.read())


    return render_template("map.html", points=points, polys=poly)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
