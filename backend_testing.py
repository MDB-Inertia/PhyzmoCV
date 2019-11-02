
import json

class DataUtils:

    def  __init__(self, jsonString, ref_list): #ref_list contains info for SCALING (coordinate1, coordinate2, physical distance betweent the two corrdinates)
        # ref_list - [[x1, y1], [x2, y2], distance]
        self.time = []

        self.ref_constant = self.getScaleConstant(ref_list[0], ref_list[1], ref_list[2])

        self.coordinates = []
        self.total_distance = []
        self.distance_per_frame = []
        self.velocity = []
        self.acceleration = []
        self.jsonData = self.getJSON(jsonString) #jsonData shoild be an array of dictionarys


    def getJSON(self, jsonString):
        dict = json.loads(json.dumps(jsonString))
        return dict

    def findDataPoints(self):
        for frame in self.jsonData.get("frames"):
            self.time.append(frame.get("time"))
            x = (frame.get("right") + frame.get("left"))/2
            y = (frame.get("bottom") + frame.get("top"))/2
            self.coordinates.append([x, y])

    def getScaleConstant(self, ref_one, ref_two, ref_dist):
        return ref_dist / self.getCoordinateScale(ref_one, ref_two)

    def getCoordinateScale(self, coordinate_one,coordinate_two):
        return pow(pow((coordinate_one[0] - coordinate_two[0]), 2) + pow((coordinate_one[1] - coordinate_two[1]), 2), 0.5)


    def findDistance(self): #WARNING: run find distance 1 time only.
        for i in range(len(self.coordinates)):
            if i == 0:
                self.distance_per_frame.append(0)
                self.total_distance.append(0)
            else:
                frame_distance = self.ref_constant * self.getCoordinateScale(self.coordinates[i - 1], self.coordinates[i])
                self.distance_per_frame.append(frame_distance)
                self.total_distance.append(frame_distance + self.total_distance[i - 1])

    def findVelocity(self):
        for i in range(len(self.distance_per_frame)):
            if i == 0:
                self.velocity.append(0) #Velocity might not be zero at the start
            else:
                self.velocity.append(self.distance_per_frame[i] / (self.time[i] - self.time[i - 1]))

    def findAcceleration(self):
        for i in range(len(self.distance_per_frame)):
            if i == 0:
                self.acceleration.append(0) #Velocity might not be zero at the start
            else:
                self.acceleration.append(self.distance_per_frame[i] / pow((self.time[i] - self.time[i - 1]), 2))





    #def getVelocity(arrayList coordinates):
        #AL = getDistance(coordinates)
        #divide all distance by time
        #rtn

    #def getAcceleration(arrayList coordinates):
        #AL = getVelocity(coordinates)
        #divide all velocities by time
        #rtn
