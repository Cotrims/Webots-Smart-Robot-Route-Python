# Giovanna Pavani Martelli - 19173
# Maria Luiza Sperancin Mancebo - 19186
# Vinicius Martins Cotrim - 19040
# MATERIA - TI502: ROBO SEGUIDOR DE LINHA DESVIADOR DE OBSTACULO E MANDADOR DE FOTO
from controller import Robot
import math
import socket
import struct
import sys
import _thread
import base64 #imports de bibliotecas a serem utilizadas

TIME_STEP = 64

def servidor(a,b): #metodo de conectar o servidor 
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    c.bind((a, b))
    c.listen(1)

    while True:
        csock, caddr = c.accept() 
        cfile = csock.makefile('rw')
        line = cfile.readline().strip() 
        data_uri = base64.b64encode(open('imagem/imagem.jpeg', 'rb').read()).decode('utf-8')
        cfile.write('HTTP/1.0 200 OK\n\n') 
        cfile.write((r'<html><head><title> Robo </title></head><body><img style="width:80%" src="data:image/png;base64,{0}"></body></html>').format(data_uri)) 
        cfile.close() 
        csock.close()
        

class MeuRobot:
    def __init__(self, robo):   #inicializacao dos componentes do robo (sensores, rodas, etc) 
        self.robo = robo
   
        self.direita = self.robo.getDevice("ds_right")
        self.direita.enable(TIME_STEP)
        
        self.esquerda = self.robo.getDevice("ds_left")
        self.esquerda.enable(TIME_STEP)
        
        self.direita_t = self.robo.getDevice("ds_right_tras")
        self.direita_t.enable(TIME_STEP)
        
        self.esquerda_t = self.robo.getDevice("ds_left_tras")
        self.esquerda_t.enable(TIME_STEP)
        
        self.camera = self.robo.getDevice("camera")
        self.camera.enable(TIME_STEP)
        
        self.baixo_e = self.robo.getDevice("baixo esquerda")
        self.baixo_e.enable(TIME_STEP)
        
        self.baixo_d = self.robo.getDevice("baixo direita")
        self.baixo_d.enable(TIME_STEP)
        
        self.baixo_m = self.robo.getDevice("baixo meio")
        self.baixo_m.enable(TIME_STEP)
        
        self.rodas = []
        self.nomesRodas = ['frenteesquerda', 'frentedireita', 'trasesquerda', 'trasdireita']
        for i in range(4):
            self.rodas.append(self.robo.getDevice(self.nomesRodas[i]))
            self.rodas[i].setPosition(float('inf'))
            self.rodas[i].setVelocity(0.0)
       
        #declaracao de variaveis a serem utilizadas     
        self.segundo = 0
        self.obstaculo = 0
        self.contador = 0
        self.dir = False
        self.esq = False
        self.img = self.camera.getImage()
        self.cor1_m = self.baixo_m.getValue()
        self.cor1_d = self.baixo_d.getValue()
        self.cor1_e = self.baixo_e.getValue()
        self.velEsq = 1.0
        self.velDir = 1.0
        
class TI502(MeuRobot):   #classe do robo
    def run(self):        #metodo de controle do robo
        while self.robo.step(TIME_STEP) != -1:
            self.camera.saveImage('imagem\imagem.jpeg', 100)  #salva imagem tirada com a camera
            self.rodas[0].setVelocity(self.velEsq) #setta as velocidades atravez de variaveis que serao mudadas durante o codigo
            self.rodas[1].setVelocity(self.velDir)
            self.rodas[2].setVelocity(self.velEsq)
            self.rodas[3].setVelocity(self.velDir)	
            if self.contador > 0: #contador serve para o robo voltar do desvio de um obstaculo
                    if(self.cor2_e == 0.0 or self.cor2_d == 0.0 or self.cor2_m == 0.0 ):
                        self.contador = 0
                    self.contador -= 7
                    if self.dir == True: #se o desvio foi para direita, ele volta para esquerda
                        self.velEsq = 1.0
                        self.velDir = -1.0
                        self.dir = False
                    if self.esq == True: #se o desvio foi para esquerda, ele volta para direita
                        self.velEsq = -1.0
                        self.velDir = 1.0
                        self.esq = False
                    self.segundo = 0
            else: # estou na linha
                if self.obstaculo > 0:  #encontrou um obstaculo
                    self.obstaculo -= 7
                    if self.segundo == 1:
                        self.velEsq = -1.0
                        self.velDir = 1.0
                    if self.segundo == 2:
                        self.velEsq = 1.0
                        self.velDir = -1.0
                if self.obstaculo <= 0: #nao encontrou um obstaculo ainda
                        if  self.direita.getValue() < 300.0 and self.obstaculo <= 0: #viu um obstaculo esta na direita
                            self.obstaculo = 120
                            self.segundo = 1
                        elif  self.esquerda.getValue() < 300.0 and self.obstaculo <= 0: #viu um obstaculo esta na esquerda
                            self.obstaculo = 120
                            self.segundo = 2
                            
                        if self.segundo == 2: #se foi pra direita (obstaculo estava na esquerda), volta para esquerda
                            if self.esquerda_t.getValue() < 500.0:
                                self.contador = 350
                                self.esq = True
                        if self.segundo == 1: #se foi pra esquerda (obstaculo estava na direita), volta para direita
                            if self.direita_t.getValue() < 500.0:
                                self.contador = 350
                                self.dir = True
                                   
                        self.velEsq = 1.0
                        self.velDir = 1.0
                        self.cor2_m = self.baixo_m.getValue()
                        self.cor2_d = self.baixo_d.getValue()
                        self.cor2_e = self.baixo_e.getValue()
                        
                        if self.cor1_m != self.cor2_m: #verifica se a cor registrada antes eh a mesma de agora
                            if self.cor1_d != 0.0 and self.cor2_e == 0.0: #se a da direita for diferente e a esquerda for preta, vira para direita
                                self.velEsq = -1.0
                                self.velDir = 1.0
                                self.cor1_m = self.cor2_m
                                self.cor1_d = self.cor2_d
                            elif self.cor1_e != 0.0 and self.cor2_d == 0.0:  #se a da esquerda for diferente e a direita for preta, vira para esquerda
                                self.velEsq = 1.0
                                self.velDir = -1.0
                                self.cor1_m = self.cor2_m
                                self.cor1_e = self.cor2_e
             
robo = Robot() #cria o robo
robot_controler = TI502(robo) #instancia o robo
_thread.start_new_thread(servidor, ('localhost',8080)) #chama a thread com o servidor
robot_controler.run() #roda o robo            
