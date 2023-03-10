import asyncio
# import serial_asyncio
import serial
import serial.tools.list_ports
import XVM
import aioserial
import time
from tkinter import filedialog as dlg
import re
from pprint import pprint
from tkinter import * 
import sys



class SFB():
    def __init__(self) -> None:
        # self.SFBids = []
        pass

    async def Id(self,com):
        aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200,timeout=2)
        self.id = '1234'
        tries = 0
        while self.id == '1234':
            xvm = XVM.generateXVM(self.id,str(8000).zfill(4),'>QVR<')
            await aioserial_instance.write_async(xvm.encode())
            raw_data: bytes = await aioserial_instance.readline_async()
            tries += 1
            print('RAW DATA:',raw_data)
            if raw_data != b'':
                self.id = raw_data.decode().split(';')[1][3::]
                if self.id != '1234':
                    print('ID: ',self.id)
                    aioserial_instance.close()
                    # if self.id not in self.SFBids:
                        # self.SFBids.append(self.id)
                        # print('ids: ',self.SFBids)
                    return self.id
            if tries == 5:
                sys.exit()
                
                
    async def PegarSN(self,com):
        await self.Id(com)
        aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200, timeout=2)
        rsn = None
        while rsn is None:
            try:
                xvm = XVM.generateXVM(self.id,str(8000).zfill(4),'>QSN<')
                await aioserial_instance.write_async(xvm.encode())
                result = await aioserial_instance.readline_async()
                # print('result',result)
                result = re.search(b'>RSN.*',result)
                # print(f'result {id}:',result)
                if result is not None:
                    rsn = result.group()
                    # if re.search(b'>RSN',rsn) is not None:
                    # print(rsn)
                    rsn = rsn.decode().split('_')[0].split('>RSN')[1]
                    aioserial_instance.close()
                    return rsn
            except:
                pass
        raise Exception(' deu ruim pegando o SN')

    async def arquivos(self,com,path):
            self.path = path
            cabeçalho =  'BINAVSFB'
            bloc =''
            bloco =[]
            lista = path
            await self.noCarrier(com)
            sn =  await self.PegarSN(com)
            print('SN: ',sn)
            await self.crb(com)
            await self.vspg(com)
            aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200,timeout=1)
            for files in lista:
                f=open(f'{files}','rb')
                conteudo = f.read()
                separar = [conteudo[i:i+520]for i in range(0,len(conteudo),520)]
                print('\n',files,'\n')
                msg = '80000000'
                # resp = b''
                await asyncio.sleep(0.5)
                for i in range(len(separar)):
                    resp = b''
                    tentativas = 1
                    bloco = cabeçalho.encode().hex()+separar[i].hex()+sn.encode().hex()
                    sep = re.findall('........',bloco)
                    sep.append(msg)
                    cs = await self.crc(sep)
                    bloc = bloco+msg+cs
                    msg = int(msg,16)+1
                    msg = format(msg,'X')
                    b = bytes.fromhex(bloc)
                    b=b.replace(b'\xdb',b'\xdb\xdd')
                    b=b.replace(b'\xc0',b'\xdb\xdc')
                    b = b+b'\xc0'
                    while resp == b'':
                        try:
                            await aioserial_instance.write_async(b)
                            resp = await aioserial_instance.read_until_async(b'\xc0')
                            print(f'tentativa {tentativas} resp: ',resp)
                            tentativas +=1
                            if re.search(b'.*NAK',resp):
                                print('ERRO NAK')
                                # break
                            if re.search(b'>MESSAGE',resp):
                                print('erro msg')
                                # break
                            if tentativas == 5:
                                print('muitas tentativas!')
                                resp = None
                                break                                
                        except:
                            continue
            print(f'{self.id}=', await aioserial_instance.read_async(200))
            aioserial_instance.close()
            await asyncio.sleep(0.2)
            await self.finalização(com)
            # return self.id
            # if self.id not in self.SFBids:
            #     self.SFBids.append(self.id)
            # print(self.SFBids)            


    async def finalização(self,com):
        await self.noCarrier(com)
        aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200,timeout=2)
        tries = 0
        while tries<15:
            try:
                xvm = XVM.generateXVM(self.id,str(8005+tries).zfill(4),'>VSPG00000000<')
                # print(xvm)
                await aioserial_instance.write_async(xvm.encode())
                resposta_vspg = await aioserial_instance.read_until_async(b'<\r\n')
                print('final:',resposta_vspg)
                match = re.search(b'>VRPG.*',resposta_vspg)
                # print(next(match))
                tries+=1
                if match is not None:
                    match = match.group()
                    if match != b'':
                        break
                if tries%5 == 0:
                    await self.noCarrier(com)
                    xvm = XVM.generateXVM(self.id,str(8005+tries).zfill(4),'>QVR<')
                    print(xvm)
                    await aioserial_instance.write_async(xvm.encode())
                    resposta_vspg = await aioserial_instance.read_until_async(b'<\r\n')
            except:
                pass
        await asyncio.sleep(0.2)
        tries = 0
        while tries<15:
            try:
                xvm = XVM.generateXVM(self.id,str(8010+tries).zfill(4),'>FDIR<')
                # print(xvm)
                await aioserial_instance.write_async(xvm.encode())
                self.resposta_fdir = await aioserial_instance.read_until_async(b'_EOL')
                print('\nFDIR:',self.resposta_fdir)
                self.fdirr = re.search(b'FDIR.*files:\d',self.resposta_fdir)
                fdir = re.search(b'>ACK.*', self.resposta_fdir)
                tries+=1
                if fdir is not None:
                    fdir = fdir.group()
                    if fdir != b'':
                        return self.fdirr
                # if tries == 5:
                #     break
            except:
                pass
        aioserial_instance.close()
        await self.reenvio(com)


    async def reenvio(self,com):
        lista_path =[]
        lista_reenvio = list(self.path)
        lista = re.findall('\d{8}.MP3', self.resposta_fdir.decode())
        for i in range(len(lista)):
            lista[i]=(''.join(lista[i]).split('.')[0])
        # print('LISTA FDIR: ',lista, len(lista))
        for i in range(len(self.path)):
            lista_path.append(self.path[i].split('/')[4].split('_')[0])
        # print('lista_path', lista_path, len(lista_path))
        # print(list(path), " type: ",type(path)) 
        for i in lista:
            for files in lista_path:
                if i == files:
                    lista_reenvio.pop(lista_path.index(f'{files}'))
                    lista_path.remove(files)
                else:
                    continue
        print("path removido",lista_path)
        print(lista_reenvio)
        if len(lista_reenvio) != 0:
            await self.arquivos(com,lista_reenvio)
        else:
            pass

    async def noCarrier(self,com):
        result = None
        tries = 0
        aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200,timeout=0.2)
        print('Limpando Serial...')
        while result is None:
            try:
                await aioserial_instance.write_async(b'NO CARRIER')
                # await asyncio.sleep(0.1)
                resp = await aioserial_instance.read_until_async(b'NAK')
                tries += 1
                # print(tries,time.time()-timeout)
                # print(resp)
                if resp != b'':
                    result = resp
                    print('Pronto!')
                    break
                if tries == 5:
                    print('Pronto!')
                    break
            except:
                pass

    async def crb(self,com):
            aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200)
            for i in range(5):
                xvm = XVM.generateXVM(self.id,str(i).zfill(4),'>CRB<')
                print(xvm)
                await aioserial_instance.write_async(xvm.encode())
                crb = await aioserial_instance.readline_async()
                if re.search('CRB_ACK', crb.decode()) is not None:
                    print(crb)
                    aioserial_instance.close()
                    break
                else:
                    continue

    async def vspg(self,com):
            aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200)
            for i in range(5):
                xvm = XVM.generateXVM(self.id,str(i).zfill(4),'>VSPG00500300<')
                print(xvm)
                await aioserial_instance.write_async(xvm.encode())
                vrpg = await aioserial_instance.readline_async()
                if re.search('VRPG',vrpg.decode()):
                    print(vrpg)
                    aioserial_instance.close()
                    break
                else:
                    continue

    async def crc(self,x):
        cs_int = 0
        sep = x
        for i in range(len(sep)):
            cs_int ^= (int(sep[i],16)) 
        hexcs = hex(cs_int).replace('0x','')
        return hexcs


    

    async def Get_fdir(self,com,id):
        self.id = id
        aioserial_instance = aioserial.AioSerial(port=com, baudrate=19200,timeout=2)
        xvm = XVM.generateXVM(self.id,str(8010).zfill(4),'>FDIR<')
        await aioserial_instance.write_async(xvm.encode())
        self.resposta_fdir = await aioserial_instance.read_until_async(b'_EOL')
        self.fdirr = re.search(b'FDIR.*files:\d',self.resposta_fdir)
        if self.fdirr is not None:
            fdirr = self.fdirr.group()
            if fdirr != b'':
                return self.fdirr.group()



# async def main():
#     path = dlg.askopenfilenames()
#     if path != '':
#         ports = serial.tools.list_ports.comports()
#         for p in ports:
#             task = asyncio.create_task(SFB().arquivos(p.device,path))
#         await task

# if __name__ == '__main__':
#     synctempo = time.time()
#     asyncio.run(main())
#     print('\ntempo total:', time.time()-synctempo)

