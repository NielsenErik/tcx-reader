import pandas as pd
import datetime
from lxml import etree, objectify


from printCalls import info, error, warning, debugging

class TCXreader:
    def __init__(self, tcx_file):
        self.path = tcx_file
        self.tree = objectify.parse(tcx_file)
        self.root = self.tree.getroot()
        self.activity = self.root.Activities.Activity
        self.tracking = {}
        self.tracking_list = []
              
        self.namespace = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
        self.namespace2 = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"
        self.laps_number = self.get_laps_number()
        self.df_lap_list = [0]*self.laps_number
        self.df = self.get_dataframe_all()

    def get_laps_number(self):
        return len(self.activity.Lap)
    
    def get_all_positions(self):
        tracking_list = []
        for lap in self.activity.Lap:
            for trackpoint in lap.Track.Trackpoint:
                if trackpoint.Position is not None:
                    tracking_list.append([trackpoint.Position.LatitudeDegrees, trackpoint.Position.LongitudeDegrees])
        return tracking_list

    def get_all_altitudes(self):
        tracking_list = []
        for lap in self.activity.Lap:
            for trackpoint in lap.Track.Trackpoint:
                if trackpoint.AltitudeMeters is not None:
                    tracking_list.append(trackpoint.AltitudeMeters)
        return tracking_list
    
    def get_all_times(self):
        tracking_list = []
        for lap in self.activity.Lap:
            for trackpoint in lap.Track.Trackpoint:
                if trackpoint.Time is not None:
                    time = datetime.datetime.fromisoformat(str(trackpoint.Time).replace('Z',''))
                    tracking_list.append(time)
        return tracking_list
    
    def get_all_distances(self):
        tracking_list = []
        for lap in self.activity.Lap:
            for trackpoint in lap.Track.Trackpoint:
                if trackpoint.DistanceMeters is not None:
                    tracking_list.append(trackpoint.DistanceMeters)
        return tracking_list
    
    def get_all_heart_rates(self):
        tracking_list = []
        for lap in self.activity.Lap:
            for trackpoint in lap.Track.Trackpoint:
                if trackpoint.HeartRateBpm is not None:
                    tracking_list.append(trackpoint.HeartRateBpm.Value)
        return tracking_list
    
    def get_all_speeds(self):
        tracking_list = []
        if self.activity.Lap.Track.Trackpoint.Extensions is not None:
            for speeds in self.root.xpath(
                "//ns1:TPX/ns1:Speed", namespaces={"ns0": self.namespace, "ns1": self.namespace2}
            ):
                tracking_list.append(speeds)
        return tracking_list
    
    def get_all_cadences(self): 
        tracking_list = []
        if self.activity.Lap.Track.Trackpoint.Extensions is not None:
            for cadences in self.root.xpath(
                "//ns0:Trackpoint/ns0:Extensions/ns1:TPX/ns1:RunCadence", namespaces={"ns0": self.namespace, "ns1": self.namespace2}
            ):                    
                tracking_list.append(cadences)
        return tracking_list
    
    def get_dataframe_all(self):
        position = self.get_all_positions()
        altitude = self.get_all_altitudes()
        time = self.get_all_times()
        distance = self.get_all_distances()
        heart_rate = self.get_all_heart_rates()
        speed = self.get_all_speeds()
        cadence = self.get_all_cadences()
        df = pd.DataFrame()        
        df = pd.concat([pd.DataFrame(position), pd.DataFrame(altitude), pd.DataFrame(time), pd.DataFrame(distance), pd.DataFrame(heart_rate), pd.DataFrame(speed), pd.DataFrame(cadence)], axis=1)
        columns = ['latitude', 'longitude', 'altitude', 'time', 'distance', 'heart_rate', 'speed', 'cadence']
        df.columns = columns
        df = df.astype({'latitude': 'float64', 'longitude': 'float64', 'altitude': 'float64', 'distance': 'float64', 'heart_rate': 'float64', 'speed': 'float64', 'cadence': 'float64'})
        return df
    
    def get_lap_positions(self, lap_number):
        tracking_list = []
        for trackpoint in self.activity.Lap[lap_number].Track.Trackpoint:
            if trackpoint.Position is not None:
                tracking_list.append([trackpoint.Position.LatitudeDegrees, trackpoint.Position.LongitudeDegrees])
        return tracking_list
    
    def get_lap_altitudes(self, lap_number):
        tracking_list = []
        for trackpoint in self.activity.Lap[lap_number].Track.Trackpoint:
            if trackpoint.AltitudeMeters is not None:
                tracking_list.append(trackpoint.AltitudeMeters)
        return tracking_list
    
    def get_lap_times(self, lap_number):
        tracking_list = []
        for trackpoint in self.activity.Lap[lap_number].Track.Trackpoint:
            if trackpoint.Time is not None:
                time = datetime.datetime.fromisoformat(str(trackpoint.Time).replace('Z',''))
                tracking_list.append(time)
        return tracking_list
    
    def get_lap_distances(self, lap_number):
        tracking_list = []
        for trackpoint in self.activity.Lap[lap_number].Track.Trackpoint:
            if trackpoint.DistanceMeters is not None:
                tracking_list.append(trackpoint.DistanceMeters)
        return tracking_list    
    
    def get_lap_heart_rates(self, lap_number): 
        tracking_list = []
        for trackpoint in self.activity.Lap[lap_number].Track.Trackpoint:
            if trackpoint.HeartRateBpm is not None:
                tracking_list.append(trackpoint.HeartRateBpm.Value)
        return tracking_list
    
    # def get_lap_speeds(self, lap_number):
    #     tracking_list = []
    #     if self.activity.Lap[lap_number].Track.Trackpoint.Extensions is not None:
    #         for speeds in self.activity.Lap[lap_number].Track.Trackpoint:
    #             speed = speeds.xpath("//ns0:Extensions/ns1:TPX/ns1:Speed", namespaces={"ns0": self.namespace, "ns1": self.namespace2})
    #             tracking_list.append(speed)
    #     return tracking_list
    
    # def get_lap_cadences(self, lap_number):
    #     tracking_list = []
    #     if self.activity.Lap[lap_number].Track.Trackpoint.Extensions is not None:
    #         for cadences in self.activity.Lap[lap_number].Track.Trackpoint.Extensions:
    #             print(cadences.getchildren())
    #             tpx = objectify.SubElement(cadences, "{http://www.garmin.com/xmlschemas/ActivityExtension/v2}TPX")
    #             print(tpx.tag)
    #             cadence = objectify.SubElement(tpx,"{http://www.garmin.com/xmlschemas/ActivityExtension/v2}RunCadence")
    #             cadence = cadence.text
    #             print(cadence)
    #     return tracking_list
    
    def get_dataframe_lap(self, lap_number):
        if lap_number > self.laps_number:
            error("Lap number is higher than the number of laps in the activity")
            return
        position = self.get_lap_positions(lap_number)
        altitude = self.get_lap_altitudes(lap_number)
        time = self.get_lap_times(lap_number)
        distance = self.get_lap_distances(lap_number)
        heart_rate = self.get_lap_heart_rates(lap_number)
        # speed = self.get_lap_speeds(lap_number)
        # cadence = self.get_lap_cadences(lap_number)
        speed = [0]*len(position)
        cadence = [0]*len(position)
        info(str(len(heart_rate)) + " heart rates")
        info(str(len(speed)) + " speeds")
        info(str(len(cadence)) + " cadences")
        df = pd.DataFrame()
        df = pd.concat([pd.DataFrame(position), pd.DataFrame(altitude), pd.DataFrame(time), pd.DataFrame(distance), pd.DataFrame(heart_rate), pd.DataFrame(speed), pd.DataFrame(cadence)], axis=1)
        columns = ['latitude', 'longitude', 'altitude', 'time', 'distance', 'heart_rate', 'speed', 'cadence']
        df.columns = columns
        df = df.astype({'latitude': 'float64', 'longitude': 'float64', 'altitude': 'float64', 'distance': 'float64', 'heart_rate': 'float64', 'speed': 'float64', 'cadence': 'float64'})
        return df
    
# test
if __name__ == "__main__":
    test = TCXreader('data/personal_tcx/reps.tcx')
    df = test.df
    print(df)
    l = []
    for t in range(5, test.laps_number-1):
        l.append(test.get_dataframe_lap(t))
    print(l[7])






'''
TCX files store data in a tree structure. The root is the TrainingCenterDatabase element.
the leaves are composed in the following order:
    - Activities
        - Activity (id, sport)
            - Id (date)
            - Lap (StartTime, TotalTimeSeconds, DistanceMeters, MaximumSpeed, Calories, AverageHeartRateBpm, MaximumHeartRateBpm, Intensity, Cadence, TriggerMethod, Track)
                - TotalTimeSeconds
                - DistanceMeters
                - MaximumSpeed
                - Calories
                - AverageHeartRateBpm
                - MaximumHeartRateBpm
                - Intensity
                - Cadence
                - TriggerMethod
                - Track
                    - Trackpoint 
                        - Time
                        - Position
                            - LatitudeDegrees
                            - LongitudeDegrees
                        - AltitudeMeters
                        - DistanceMeters
                        - HeartRateBpm
                            - Value
                        - Extensions
                            - TPX
                                - Speed
                                - RunCadence
                                - Watts
                                - Value
'''