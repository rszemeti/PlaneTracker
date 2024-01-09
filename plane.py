import csv
import pyproj
from datetime import datetime
from math import radians, degrees, sin, cos, asin, acos, sqrt, atan2

    
my_location = ( 52.388137, -2.304576, 67.0) # lat, lon, height (metres)

debug = True

planes = {}

class Target:
    def __init__(self,id,az,dist,ele):
        self.id=id
        self.azimuth=az
        self.distance = dist
        self.elevation = ele

class Plane:
    geod = pyproj.Geod(ellps='WGS84')
    
    def __init__(self, csv_string):
        fields = csv_string.strip().split(',')

        # Assigning fields to the class attributes
        self.message_type = fields[0] if len(fields) > 0 else None
        self.transmission_type = fields[1] if len(fields) > 1 else None
        self.session_id = fields[2] if len(fields) > 2 else None
        self.aircraft_id = fields[3] if len(fields) > 3 else None
        self.hex_id = fields[4] if len(fields) > 4 else None
        self.flight_id = fields[5] if len(fields) > 5 else None
        self.generated_date = fields[6] if len(fields) > 6 else None
        self.generated_time = fields[7] if len(fields) > 7 else None
        self.logged_date = fields[8] if len(fields) > 8 else None
        self.logged_time = fields[9] if len(fields) > 9 else None
        self.callsign = fields[10] if len(fields) > 10 else None
        self.altitude = int(fields[11]) if len(fields) > 11 and fields[11] else None
        self.ground_speed = int(fields[12]) if len(fields) > 12 and fields[12] else None
        self.track = int(fields[13]) if len(fields) > 13 and fields[13] else None
        self.latitude = float(fields[14]) if len(fields) > 14 and fields[14] else None
        self.longitude = float(fields[15]) if len(fields) > 15 and fields[15] else None
        self.vertical_rate = int(fields[16]) if len(fields) > 16 and fields[16] else None
        self.squawk = fields[17] if len(fields) > 17 else None
        self.alert = fields[18] if len(fields) > 18 else None
        self.emergency = fields[19] if len(fields) > 19 else None
        self.spi = fields[20] if len(fields) > 20 else None
        self.is_on_ground = fields[21] if len(fields) > 21 else None
        self.position_time = None

    def update(self, new_message):
        position_updated = False
        for key, value in new_message.__dict__.items():
            if value is not None:
                setattr(self, key, value)
                if key in ['latitude', 'longitude']:
                    position_updated = True
        
        if position_updated:
            self.position_time = datetime.now()

    from math import radians, degrees, sin, cos, asin, acos, sqrt

    def get_position(self):
        
        delta = datetime.now() - self.position_time
        elapsed_time = int(delta.total_seconds())
        eleapsed_time = 0

        # Convert track and speed into radians and nautical miles
        track_rad = radians(float(self.track))
        distance = float(self.ground_speed) * (elapsed_time / 3600)  # Distance in nautical miles

        # Radius of the Earth in nautical miles
        radius_earth = 3440.065

        # Convert latitude to radians
        lat_rad = radians(float(self.latitude))

        # New latitude in radians
        new_lat_rad = asin(sin(lat_rad) * cos(distance / radius_earth) +
                           cos(lat_rad) * sin(distance / radius_earth) * cos(track_rad))

        # New longitude in radians
        new_lon_rad = float(self.longitude) + degrees(acos((sin(new_lat_rad) - sin(lat_rad) * sin(lat_rad)) /
                                         (cos(lat_rad) * cos(new_lat_rad))) * 
                                   (-1 if sin(track_rad) < 0 else 1))

        # Convert new latitude and longitude to degrees
        new_lat = degrees(new_lat_rad)
        new_lon = degrees(new_lon_rad)
        print(self.latitude, self.longitude, new_lat, new_lon)

        return new_lat, new_lon, float(self.altitude) * 0.3048

    def get_target(self, my_position):
        try:
            estimated_position = self.get_position()  # (latitude, longitude, altitude)  
            # Correct the order of longitude and latitude
            print(my_position[1], my_position[0], estimated_position[1], estimated_position[0])
            fwd_azimuth, back_azimuth, distance = self.geod.inv(my_position[1], my_position[0], estimated_position[1], estimated_position[0])
            altitude_difference = estimated_position[2] - my_position[2]  # Ensure both are in the same unit
            los_distance = (distance**2 + altitude_difference**2)**0.5
            elevation_angle = degrees(atan2(altitude_difference, distance))
            return Target(self.hex_id, fwd_azimuth, int(distance / 1000), elevation_angle)
        
        except Exception as e:
            print("Not enough data yet")
            print(e)
            return None


    def __str__(self):
        return f"ADSBMessage({self.callsign}, Type: {self.transmission_type}, Hex: {self.hex_id},  Altitude: {self.altitude}, Speed: {self.ground_speed}, Track: {self.track}, Lat: {self.latitude}, Long: {self.longitude})"

# Test function
def test():
    plane= Plane("")
    plane.track="180.0"
    plane.ground_speed="0.0"
    plane.latitude="60.0"
    plane.longitude="0.0"
    plane.altitude="10000"
    plane.position_time = datetime.now()
    plane.get_position()
    

# This part ensures that the following code runs only when the script is executed directly
if __name__ == "__main__":
    test()
