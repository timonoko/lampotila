import network,time,machine,sys
import  onewire, ds18x20
from machine import WDT
wdt=WDT(timeout=30000)


import socket

Ledi = machine.Pin(2, machine.Pin.OUT)
Ledi.value(0)

dat14 = machine.Pin(14)
ds = ds18x20.DS18X20(onewire.OneWire(dat14))
roms = ds.scan()
print('found devices:', roms)
dat12 = machine.Pin(12)
ds2 = ds18x20.DS18X20(onewire.OneWire(dat12))
roms2 = ds2.scan()
print('found devices:', roms2)
dat13 = machine.Pin(13)
ds3 = ds18x20.DS18X20(onewire.OneWire(dat13))
roms3 = ds3.scan()
print('found devices:', roms3)



def web_page():
  menu="""
    <h1>LAMPOTILA</h1>
    <p>ULKO: """+str(temps['155'])+""" <p>
    <p>TYO : """+str(temps['100'])+""" <p>
    <p>OLO : """+str(temps['160'])+""" <p>
    <p>PAT : """+str(temps['47'])+""" <p>
<p>  
    <p> LED <a href="/led/on"> <button class="button">ON</button></a>
     <a href="/led/off"> <button class="button button2">OFF</button></a> </p>
    """
  html = """
     <html><head>
     <meta http-equiv="refresh" content="3"> 
     <title>LAMPOTILA</title>
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <link rel="icon" href="data:,">
     <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style>
     </head>
      <body>
     """ + menu + """
     </body>
   </html>"""
  return html



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
s.setblocking(False)

while True:
    wdt.feed()
    s.settimeout(0.2)
    temps={}
    try:
        ds.convert_temp()
        ds2.convert_temp()
        ds3.convert_temp()
        time.sleep_ms(750)
        for rom in roms: temps.update({str(rom[2]):ds.read_temp(rom)})
        for rom in roms2: temps.update({str(rom[2]):ds2.read_temp(rom)})
        for rom in roms3: temps.update({str(rom[2]):ds3.read_temp(rom)})
    except:
        temps={'155': -40, '162': -40, '100': -40, '47': -40}
    print(temps)
    print(web_page())
    try:
        print('venaa')
        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)
        if request.find('/led/on') == 6:
            print('ledi on')
            Ledi.value(1)
        if request.find('/led/off') == 6:
            Ledi.value(0)
        if request.find('/reset') == 6:
            machine.reset()
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    except (OSError): # Catch the specific non-blocking error
        print('no connection to handle') # Or simply `pass` to do nothing
    except:
        print('an error occurred')

