import serial
from tkinter import filedialog as dlg
import re
from tkinter import * 
from tkinter import ttk
import asyncio
from time import sleep
import XVM
import serial.tools.list_ports
from async_timeout import timeout
import class_EnvioXVM as cXVM
import SFB
import customtkinter
import SFB2

customtkinter.set_appearance_mode("Dark")
master = customtkinter.CTk() 
master.geometry("320x80")
master.title("Configurador")
master.resizable(FALSE,FALSE)



class app():
    def __init__(self):
        self.ids = []
        self.cs =[]
        self.SFBids = []
        self.Fdir = []
        self.label=customtkinter.CTkLabel(master, text= 'ESCOLHER ARQUIVO')
        self.label.place(x=20)
        self.bttn=customtkinter.CTkButton(master, text='Escolher',command=self.enviaComandos)
        self.bttn.place(x=10,y=30)
        self.label2=customtkinter.CTkLabel(master, text= 'ESCOLHER VOZ')
        self.label2.place(x=190)
        self.bttn2=customtkinter.CTkButton(master, text='Escolher',command=self.exibeVoz)
        self.bttn2.place(x=165,y=30)


    def enviaComandos(self):
        self.comand = cXVM.Sender()
        if self.comand.ids:
            self.OpenWindow2()
        else:
            pass


    def exibeVoz(self):
        self.voz = SFB2.SFB()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            id = asyncio.run(self.voz.Id(p.device))            
            self.SFBids.append(id)
        asyncio.run(self.main())
        for p in ports:
            for i in self.SFBids:
                fdir = asyncio.run(SFB2.SFB().Get_fdir(p.device,i))
                print(fdir)
                self.Fdir.append(fdir)
        # if self.voz.SFBids:
        self.OpenWindow()
        # else:
            # pass
        # name = getattr(nome.resp, 'resp')
        # print(nome.resp)
        # self.label_dinamica.set(nome.resp)

    async def main(self):
        path = dlg.askopenfilenames()
        if path != '':
            ports = serial.tools.list_ports.comports()
            for p in ports:
                task = asyncio.create_task(SFB2.SFB().arquivos(p.device,path))
            await task

            # for p in ports:
            #     fdir = asyncio.run(SFB2.SFB().finalização(p.device))
            #     print(fdir)

            


            
    def OpenWindow(self):
        customtkinter.set_appearance_mode("Dark")
        self.newWindow = customtkinter.CTkToplevel(master) 
        self.newWindow.title("Envio Vozes") 
        self.newWindow.geometry("280x300")
        self.newWindow.resizable(FALSE,FALSE)
        customtkinter.CTkLabel(self.newWindow, text ="IDS CONFIGURADOS!!").pack()
        
        for i in range(len(self.SFBids)):
    #         print(i, len(self.ids),self.cs)
            customtkinter.CTkLabel(self.newWindow, text=f'{self.SFBids[i]}').place(x=40, y=(i+1)*20)
            customtkinter.CTkLabel(self.newWindow, text=f'{self.Fdir[i]}').place(x=120, y=(i+1)*20)
    #         Label(self.newWindow, text='-----------',background="#dde", foreground="#009").grid(row=i+2,column=1,padx=15)
    #         Label(self.newWindow, text=f'{self.cs[i]}',background="#dde", foreground="#009").grid(row=i+2,column=2)


    def OpenWindow2(self):
        customtkinter.set_appearance_mode("Dark")
        self.newWindow2 = customtkinter.CTkToplevel(master) 
        self.newWindow2.title("Envio Comandos") 
        self.newWindow2.geometry("280x300")
        self.newWindow2.resizable(FALSE,FALSE)
        customtkinter.CTkLabel(self.newWindow2, text ="IDS CONFIGURADOS!!").pack()
        for i in range(len(self.comand.ids)):
            customtkinter.CTkLabel(self.newWindow2, text=f'{self.comand.ids[i]}').place(x=20, y=(i+1)*20)
            customtkinter.CTkLabel(self.newWindow2, text=f'{self.comand.cs[i]}').place(x=200 , y=(1+i)*20)
        pass

if __name__ == '__main__':
    app()
    master.mainloop()



