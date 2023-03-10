import serial
from tkinter import filedialog as dlg
import re
from tkinter import * 
import asyncio
from time import sleep
import XVM
import serial.tools.list_ports
from async_timeout import timeout




class Sender():
    def __init__(self):
        self.ids = []
        self.cs =[]
        self.dir()
        pass


    def dir(self):
        self.path =dlg.askopenfilename()
        with open(f'{self.path}') as f:
            self.tudo = f.read()
        self.comandos=(re.findall('(>.*<)', self.tudo))
        asyncio.run(self.function_asyc())




    async def conferencia(self):
        msg = XVM.generateXVM(self.id,str(1).zfill(4),f'>QEP_CFG<')
        self.ser.write(msg.encode())
        resp = self.ser.readline()
        print(resp)
        if re.findall(b'REP_CFG.*',resp) is not None:            
            self.resp_msg = resp.decode().split('_')[3]
            print(self.resp_msg)
            self.conf = self.resp_msg.split(' ')[0]
            print(self.conf)
            self.cs.append(self.conf)



    
    async def conexao(self,COM):
        teste = serial.Serial(COM, 19200, timeout=10)
        self.id = '-'
        try:
            for i in range(5):
                xvm = XVM.generateXVM('1234',str(i).zfill(4),'>QVR<')
                teste.write(xvm.encode())
                resposta = teste.readline().decode()
                self.id = resposta.split(';')[1][3::]
                if self.id != '1234':
                    print(self.id)
                    break
        except Exception:
            print('PORTA SEM COMUNICAÇÃO')
            pass
            

    async def function_asyc(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(p)
            print('estabelecendo conexao...')
            try:
                async with timeout(10):
                    await asyncio.create_task(self.conexao(p.device))
                    if self.id == '-':
                        Exception
            except Exception as error:
                print('error', error)
            else:
                self.ser = serial.Serial(f'{p.device}', 19200)
                if self.id != '-':	
                    for i in range(len(self.comandos)):
                        self.linha = str.encode(self.comandos[i])
                        print(self.comandos[i])
                        xvm = XVM.generateXVM(self.id,str(8000+i).zfill(4),self.comandos[i])
                        self.ser.write(xvm.encode())
                        sleep(0.1)
                        resposta = self.ser.readline().decode()
                        print(resposta)
                    self.ids.append(self.id)
                    print(self.ids)
                    await self.conferencia()    
                self.ser.close()

