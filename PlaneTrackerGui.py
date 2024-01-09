import PySimpleGUI as sg
import asyncio
import threading


# Define the data structure for the table
header_list = ['Hex ID', 'Latitude', 'Longitude', 'Azimuth', 'Distance', 'Elevation']
data = []

# Create the layout
layout = [
    [sg.Table(values=data, headings=header_list, max_col_width=25,
              auto_size_columns=True,
              display_row_numbers=True,
              justification='right',
              num_rows=20,
              key='-TABLE-',
              row_height=35)],
]

# Create the window
window = sg.Window('Plane Tracker', layout)

def update_gui():
    global planes
    while True:
        # Update the table in the GUI
        try:
            window.write_event_value('-UPDATE-', planes)
            asyncio.sleep(5)  # Update every 5 seconds
        except:
            break

# Launch the GUI update in a separate thread
threading.Thread(target=update_gui, daemon=True).start()

# Event loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '-UPDATE-':
        # Update table data
        updated_data = []
        for hex_id, plane in planes.items():
            target = plane.get_target(my_location)
            if target:
                updated_data.append([target.id, plane.latitude, plane.longitude,
                                     target.azimuth, target.distance, target.elevation])
        window['-TABLE-'].update(values=updated_data)

window.close()
