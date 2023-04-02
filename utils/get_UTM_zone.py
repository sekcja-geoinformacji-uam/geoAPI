import math

def get_UTM_zone(bounds):
        if math.ceil((bounds[2] + 180) / 6) - math.ceil((bounds[0] + 180) / 6) > 1:
            return 3857
        else:
            zone = math.ceil(((bounds[2] + bounds[0]) / 2 + 180) / 6)
            if bounds[3] >= 0:
                crs = int("326" + str(zone))
            else:
                crs = int("327" + str(zone))
            return crs