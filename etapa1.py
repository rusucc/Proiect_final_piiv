import csv
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
import socket
import time
import tkinter as tk
import threading
from queue import Queue

#functie care deschide 4 fisiere in care urmeaza sa scrie date, din fisierul cu date senzori
def splitCSVs(): 
    with open('date_senzori.csv', 'r', newline='') as file:
        with open('_Temperaturi.csv', 'w', newline='') as temp_file:
            with open('_Umiditate.csv', 'w', newline='') as umid_file:
                with open('_Viteza.csv', 'w', newline='') as vit_file:
                    with open('_Prezenta.csv', 'w', newline='') as prez_file:
                        #temp-0, umiditate-1, viteza-2, prezenta-3
                        wr_t = csv.writer(temp_file,delimiter=',',quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        wr_u = csv.writer(umid_file,delimiter=',',quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        wr_v = csv.writer(vit_file,delimiter=',',quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        wr_p = csv.writer(prez_file,delimiter=',',quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                        rd = csv.reader(file, delimiter=',', quotechar='|')
                        index = 0 #index pentru numarul citirii
                        for row in rd:
                            currentTime = datetime.now().strftime("%H:%M:%S")
                            wr_t.writerow([currentTime,index,row[0]])
                            wr_u.writerow([currentTime,index,row[1]])
                            wr_v.writerow([currentTime,index,row[2]])
                            wr_p.writerow([currentTime,index,row[3]])
                            index = index + 1

def graph(name): #functie care afiseaza un grafic cu datele dintr-un fisier si ii salveaza imaginea
    with open(name,'r', newline='') as file:
        rd = csv.reader(file, delimiter=',', quotechar='|')
        x = []
        y = []
        for row in rd:
            x.append(row[1])
            y.append(row[2])
    x = np.array(x)
    y = np.array(y)
    y = y.astype(np.float64)
    #convertim din string in float
    # https://stackoverflow.com/questions/51351817/python-matplotlib-scatterplot-plots-axis-with-inconsistent-numbers
    print(x,y)
    plt.scatter(x,y)
    title = name[1:-4] #eliminam '_' si '.csv'
    plt.title(title)
    plt.savefig('images/'+title+'.png')
    plt.show()
    plt.clf()
    #clear figure, fara el se suprapuneau toate graficele
def graphAll():
    csv_names = ['_Prezenta.csv','_Temperaturi.csv','_Viteza.csv','_Umiditate.csv']
    for csv_name in csv_names:
        graph(csv_name)
dataSendQueue = Queue()
def start_server(host='127.0.0.1', port=65432):
    # Creăm un socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    #server_socket.settimeout(5)  # Timeout after 5 seconds
    #server_socket.setblocking(False)
    
    
    # Așteptăm pachetele de inițializare a conexiunii de la client
    server_socket.listen()
    print(f"Serverul este gata și așteaptă conexiunea clientului la {host}:{port}")
    print("***************************************************************************************")
    
    # Acceptăm conexiunea clientului
    client_socket, client_address = server_socket.accept()
    print(f"Conexiune cu clientul {client_address} a fost stabilită.")
    global dataSendQueue
    try:
        while dataSendQueue.empty() is False:
            print('*')
            sendData = dataSendQueue.get()
            sendData = str(sendData)
            client_socket.sendall(sendData.encode("utf-8")) #Trimitem datele clientului
            print(f"SERVER: Date trimise: {sendData.strip()}") #Afișăm valoarea trimisă clientului
            time.sleep(0.2) #Pauză scurtă între trimiterea datelor
    except Exception as e:
        print(f"Eroare: {e}")

def start_client():
    # Definirea parametrilor pentru realizarea conexiunii la server
    host = '127.0.0.1'  # Adresa IP a serverului
    port = 65432        # Portul serverului
    
    # Crearea unui socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket.settimeout(5)  # Timeout after 5 seconds
    #client_socket.setblocking(False)


    
    try:
        # Conectarea la server
        client_socket.connect((host, port))
        print(f"Clientul s-a conectat la serverul cu ip-ul {host}:{port}")
        print("***************************************************************************************")
        
        # Variabile pentru stocarea datelor primite
        
        while True:
            # Citim datele primite și le stocăm în variabila date
            data = client_socket.recv(1024) #1024 bytes valoare maximă a unui mesaj
            decoded_data = data.decode("utf-8").strip()
            if data:
                print(f"CLIENT: Date primite: {decoded_data}")
            else:
                break
    except Exception as e:
        print(f"Eroare: {e}")
    finally:
        client_socket.close()
        print("Conexiunea a fost închisă.")


def startClientAndServer():
    server_thread = threading.Thread(target=start_server, name="serverTCP")
    client_thread = threading.Thread(target=start_client, name="clientTCP")

    server_thread.start()
    client_thread.start()
    
    server_thread.join() 
    client_thread.join()  

def TCPsendCSV():
    global dataSendQueue
    with open('date_senzori.csv','r', newline='') as file:
        rd = csv.reader(file, delimiter=',', quotechar='|')
        for row in rd:
            dataSendQueue.put(row)
    startClientAndServer()

if __name__ == '__main__':
    
    tk1 = tk.Tk()
    tk1.title('PIIV')

    button_split = tk.Button(tk1, text='Split CSVs', width=25, command=splitCSVs)
    button_split.pack(pady=20)

    button_graph = tk.Button(tk1, text='Graph All', width=25, command=graphAll)
    button_graph.pack(pady=20)

    button_send = tk.Button(tk1, text='Send data over TCP', width=25, command=TCPsendCSV)
    button_send.pack(pady=20)

    button_stop = tk.Button(tk1, text='Stop', width=25, command=tk1.destroy)
    button_stop.pack(pady=20)

    tk1.mainloop()