from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import re
import json
import sqlite3

conn = sqlite3.connect('mydb.db')


def send_data(self, status_code, message):
    self.send_response(status_code)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    if status_code != 200:
        di = {"Status code:": status_code, "Message:": message}
        self.wfile.write(json.dumps(di).encode("utf-8"))
    else:
        self.wfile.write(json.dumps(message).encode("utf-8"))


class Handling(BaseHTTPRequestHandler):
    def do_GET(self):
        di = dict()

        if self.path == '/cars':

            cursor = conn.execute(
                "SELECT ProductId, Marca, Model, Caroserie, Carburant, Putere, Cilindri, Pret, Sasiu from carshop")

            for data in cursor:
                datadict = dict()
                datadict['Marca'] = data[1]
                datadict['Model'] = data[2]
                datadict['Caroserie'] = data[3]
                datadict['Carburant'] = data[4]
                datadict['Putere(Cai)'] = data[5]
                datadict['Cilindri'] = data[6]
                datadict['Pret'] = data[7]
                datadict['Sasiu'] = data[8]
                di[data[0]] = datadict

            if len(di) != 0:
                send_data(self, 200, di)
            else:
                send_data(self, 404, "Nu exista masini in baza de date!")

        elif re.match('/cars/\d+', self.path):
            text = str(self.path).split("/cars/")

            cursor = conn.execute(
                "SELECT ProductId, Marca, Model, Caroserie, Carburant, Putere, Cilindri, Pret, Sasiu from carshop where ProductId = ?",
                [text[1]])
            for data in cursor:
                datadict = dict()
                datadict['Marca'] = data[1]
                datadict['Model'] = data[2]
                datadict['Caroserie'] = data[3]
                datadict['Carburant'] = data[4]
                datadict['Putere'] = data[5]
                datadict['Cilindri'] = data[6]
                datadict['Pret'] = data[7]
                di[data[0]] = datadict

            if len(di) != 0:
                send_data(self, 200, di)
            else:
                send_data(self, 404, "Masina cu ID-ul precizat nu se afla in baza de date.")

        else:
            send_data(self, 404, "Nu puteti face GET pe aceast URL")

    def do_POST(self):
        if self.path == '/cars':
            content_length = int(self.headers['Content-Length'])
            if content_length != 0:
                try:
                    body = json.loads(self.rfile.read(int(content_length)))
                    if body.keys() >= {"Sasiu", "Marca", "Model", "Caroserie", "Carburant", "Putere", "Cilindri",
                                       "Pret"}:
                        elements = [body['Sasiu'], body['Marca'], body['Model'], body['Caroserie'], body['Carburant'],
                                    body['Putere'], body['Cilindri'], body['Pret']]

                        try:
                            conn.execute(
                                "INSERT INTO carshop(Sasiu, Marca, Model, Caroserie, Carburant, Putere, Cilindri, Pret) VALUES (?,?,?,?,?,?,?,?)",
                                elements)
                            conn.commit()
                            send_data(self, 201, "Created!")
                        except sqlite3.Error as err:
                            send_data(self, 409, "Sasiul trebuie sa fie unic!")
                    else:
                        send_data(self, 400, "Elementele din body sunt incorecte!")
                except:
                    send_data(self, 400, "Elementele din body sunt incorecte!")

            else:
                send_data(self, 400, "Nu puteti face POST cu un Body gol")
        else:
            send_data(self, 404, "Nu puteti face POST pe acest URL")

    def do_PUT(self):
        if self.path == '/cars/all':
            send_data(self, 405,
                      "(Method Not Allowed), unless you want to update or replace the whole collection not often desirable.")
        elif re.match('/cars/\d+', self.path):
            datadict = dict()
            text = str(self.path).split("/cars/")
            cursor = conn.execute("SELECT count(*), Marca, Model, Caroserie, Carburant, Putere, Cilindri, Pret from carshop where ProductId=?", [text[1]])
            data = cursor.fetchone()
            if int(data[0]) == 1:
                datadict['Marca'] = data[1]
                datadict['Model'] = data[2]
                datadict['Caroserie'] = data[3]
                datadict['Carburant'] = data[4]
                datadict['Putere'] = data[5]
                datadict['Cilindri'] = data[6]
                datadict['Pret'] = data[7]
                print(datadict)
                content_length = int(self.headers['Content-Length'])
                if content_length != 0:
                    try:
                        body = json.loads(self.rfile.read(int(content_length)))
                        for index in ["Marca", "Model", "Caroserie", "Carburant", "Putere", "Cilindri", "Pret"]:
                            if index in body.keys():
                                datadict[index] = body[index]
                        try:
                            sql = ''' UPDATE carshop SET Marca = ? , Model = ? ,
                                    Caroserie = ? , Carburant = ? , Putere = ? , Cilindri = ? , Pret = ? WHERE ProductId = ?'''
                            exe = conn.cursor()
                            li = list(datadict.values())
                            li.append(int(text[1]))
                            exe.execute(sql, li)
                            conn.commit()
                            send_data(self, 200, {"Status code:": 200, "Message:": "Updated!"})
                        except sqlite3.Error as err:
                            send_data(self, 409, str(err))
                    except ValueError as e:
                        send_data(self, 404, str(e))

                else:
                    send_data(self, 400, "Nu puteti face PUT cu un Body gol")
            else:
                send_data(self, 404, "Nu exista in baza de date")
        else:
            send_data(self, 404, "Nu puteti face PUT pe acest URL")

    def do_DELETE(self):

        if self.path == '/cars/all':
            send_data(self, 405,
                      "(Method Not Allowed), unless you want to delete the whole collection not often desirable.")

        elif re.match('/cars/\d+', self.path):
            text = str(self.path).split("/cars/")
            cursor = conn.execute("SELECT count(*) from carshop where ProductId=?",[text[1]])
            if int(cursor.fetchone()[0]) == 1:
                try:
                    conn.execute("DELETE FROM carshop WHERE ProductId=?", [text[1]])
                    conn.commit()
                    send_data(self, 200, {"Status code:": 200, "Message:": "Deleted"})

                except sqlite3.Error as err:
                    send_data(self, 409, str(err))
            else:
                send_data(self, 404, "Nu exista id-ul in baza de date")
        else:
            send_data(self, 404, "Nu puteti face DELETE pe acest URL")


httpd = HTTPServer(('127.0.0.1', 5000), Handling)
httpd.serve_forever()
