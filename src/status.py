import asyncio

server = {'running': True,
          'softboot': False}
frontend = {'connected': False}
grapevine = {'connected': True,
             'authenticated': False}

server_shutdown = asyncio.Queue()
