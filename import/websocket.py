# websocket.py

async def websocket_application(scope, receive, send):
     while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            await send({
                'type': 'websocket.accept'
            })

        if event['type'] == 'websocket.disconnect':
            break

        if event['type'] == 'websocket.receive':
  
            await send({
                'type': 'websocket.send',
                'text': event['text']
            })