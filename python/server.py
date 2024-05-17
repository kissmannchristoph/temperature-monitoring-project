import socketio
from aiohttp import web
import time
import paho.mqtt.client as mqtt
import requests 
import json

temp: float = 0.0
water: int = 0
room: str = ""
timestamp: float = 0.0

saveTimeout: int = 30

# create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')

# wrap with a WSGI application
app = web.Application()

dataFileName = "data.json"

savedData = None

def loadFile() -> dict[room: str, temp: float, water: int, timestamp: float]:
    f = open(dataFileName)
    return json.load(f)

def saveFile(data):
    with open(dataFileName, 'w') as f:
        json.dump(data, f)

def getSavedData():
    global savedData
    if savedData is None:
        savedData = loadFile()

    return savedData

def getLastSavedElement():
    data = getSavedData()

    if len(data) == 0:
        return None

    return data[len(data) - 1]

async def handleRoot(request):
    return web.FileResponse("public/index.html")

async def handleData(request):
    return web.json_response(status=200, data={ 'temp': temp, 'rain': water == 0 })

async def handleGraph(request):
    return web.json_response(status=200, data=getSavedData())

async def test():
    r = requests.get("http://127.0.0.1:8080/triggerGraph")

async def handleTrigger(request):
    await sio.emit('updateData', { 'temp': temp, 'rain': water == 0 }) # type: ignore
    return web.json_response(status=200, data={ 'temp': temp, 'rain': water == 0 })

async def handleTriggerGraph(request):
    await sio.emit('updateChart', {}) # type: ignore
    return web.json_response(status=200, data={ 'temp': temp, 'rain': water == 0 })

app.add_routes([
    # vue frontend
    web.get('/', handleRoot),
    
    # current data
    web.get('/data', handleData),
    
    # trigger websocket update
    web.get('/trigger', handleTrigger),

    # trigger websocket update for graph
    web.get('/triggerGraph', handleTriggerGraph),
    
    # load saved data
    web.get('/graph', handleGraph)
])

app.add_routes([web.static('/assets', "public/assets")])

sio.attach(app)

@sio.event
async def connect(sid, environ, auth):
    await sio.emit('updateData', { 'temp': temp, 'rain': water == 0 }, to=sid) # type: ignore
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

  # callback for incoming MQTT Messages
def messageReceived(client, userdata, message):
    data = message.payload.decode("utf-8")
    # "id|data"

    id = data.split("|")[0]

    if id == 'temp':
        global temp
        temp = float(data.split("|")[1])
    elif id == 'water':
        global water
        water = float(data.split("|")[1])
    
    if (time.time() - getLastSavedElement()['timestamp']) > saveTimeout:
        newData = getSavedData()
        newData.append({
            "room": room, 
            "timestamp": time.time(),
            "temp": temp,
            "water": water
        })

        saveFile(newData)

        print("data saved")

        r = requests.get("http://127.0.0.1:8080/triggerGraph")
    r = requests.get("http://127.0.0.1:8080/trigger")
    #main_event_loop = asyncio.get_event_loop()
    #main_event_loop.run_until_complete(sio.emit("updateData", "asd"))
    #asyncio.run(updateData())

async def refreshDataFromBroker():
        # start the program
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # create new instance
    
    client.connect("127.0.0.1")  # connect to broker
    client.subscribe("sensorclient/data")
            # start loop für  MQTT client
    client.loop_start()  # start the loop

            # callback for incoming MQTT Messages
    client.on_message = messageReceived
    print("Connected to MQTT Server")
   

async def init_app():
    sio.start_background_task(refreshDataFromBroker)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), port=8080)

        