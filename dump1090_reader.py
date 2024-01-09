import socket
import csv
import asyncio
from plane import Plane
    
my_location = ( 52.388137, -2.304576, 67.0) # lat, lon, height (metres)

debug = True

planes = {}

async def connect_to_dump1090(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer

    
async def update_planes(reader, writer):
    try:
        while True:
            data = await reader.read(1024)
            message = data.decode('utf-8')
            if message:
                new_plane = Plane(message)
                if(debug):
                    print(new_plane)
                hex_id = new_plane.hex_id

                if hex_id in planes:
                    planes[hex_id].update(new_plane)
                else:
                    planes[hex_id] = new_plane
    except KeyboardInterrupt:
        print("Disconnected.")
    finally:
        writer.close()
        await writer.wait_closed()

async def track_planes():
    while True:
        for hex_id, plane in planes.items():
            if plane.latitude is not None:
                target = plane.get_target(my_location)
                if(target):
                    print(f"Plane {target.id} is at {target.azimuth} degrees azimuth at a distance of {target.distance}km and an elevation angle of {target.elevation} degrees.")
        print("##")
        await asyncio.sleep(5)  # Wait for 5 seconds before the next update

async def main():
    reader, writer = await connect_to_dump1090('localhost', 30003)
    await asyncio.gather(
        update_planes(reader, writer),
        track_planes()
    )

asyncio.run(main())

