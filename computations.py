
import json
import matplotlib.pyplot as plt


def get_frames(objectsData, obj_descriptions): #DONE
    """ Returns a dictionary {'frames' : [{'time': 0, 'left': , ...} {} {} ...]}
        Takes objectsData and combines all frames for all object descriptions in the array obj_descriptions (selected by user)
        Ex: get_frames(objectsData from track_objects_gcs_all, ['ball', 'basketball', 'fruits']) """

    frameData = {"frames": []}
    for obj in obj_descriptions:
        if obj in objectsData:
            frameData['frames'] += objectsData[obj]
    frameData['frames'] = sorted(frameData['frames'], key = lambda i: i['time'])
    return frameData


def getJSON(jsonString): #DONE
    dict = json.loads(json.dumps(jsonString))
    return dict

def calculate(objectsData, obj_descriptions, ref_list): 
#ref_list contains info for SCALING (coordinate1, coordinate2, physical distance betweent the two corrdinates)
    time = []

    ref_constant = getScaleConstant(ref_list[0], ref_list[1], ref_list[2]) #DONE

    coordinates = []
    total_distance = []
    distance_per_frame = []
    displacement = [] #NOT USED
    velocity = []
    acceleration = []

    jsonData = getJSON(get_frames(objectsData, obj_descriptions)) #jsonData shoild be an array of dictionarys

    normalized_velocity = []
    normalized_acce = []

    findDataPoints(time, coordinates, jsonData)
    findDistance(coordinates, distance_per_frame, total_distance, ref_constant)
    findVelocity(distance_per_frame, velocity, time)

    findMovingAverageVelocity(normalized_velocity, velocity)
    findAcceleration(distance_per_frame, acceleration, normalized_velocity, time) # Do we want to use normalized velocity for calculations of acceleration - makes normalized acceleration even smoother

    findMovingAverageAcce(normalized_acce, acceleration) # Do we want to use normalized velocity for calculations of acceleration - makes normalized acceleration even smoother

    return {"time": time,
            "coordinates": coordinates,
            "total_distance": total_distance,
            "distance_per_frame": distance_per_frame,
            "displacement": displacement, #NOT USED
            "velocity": velocity,
            "acceleration": acceleration,
            "normalized_velocity": normalized_velocity,
            "normalized_acce": normalized_acce}


def findDataPoints(time, coordinates, jsonData): #DONE
    for frame in jsonData.get("frames"):
        time.append(frame.get("time"))
        x = (frame.get("right") + frame.get("left"))/2
        y = (frame.get("bottom") + frame.get("top"))/2
        coordinates.append([x, y])

def getScaleConstant(ref_one, ref_two, ref_dist): #DONE
    return ref_dist / getCoordinateScale(ref_one, ref_two)

def getCoordinateScale(coordinate_one,coordinate_two): #DONE
    return pow(pow((coordinate_one[0] - coordinate_two[0]), 2) + pow((coordinate_one[1] - coordinate_two[1]), 2), 0.5)

def findDistance(coordinates, distance_per_frame, total_distance, ref_constant): #WARNING: run findDistance 1 time only
#DONE
    for i in range(len(coordinates)):
        if i == 0:
            distance_per_frame.append(0)
            total_distance.append(0)
        else:
            #EDITED HERE
            frame_distance = ref_constant * getCoordinateScale(coordinates[i - 1], coordinates[i])
            #distance_per_frame.append(frame_distance)
            # if self.coordinates[i][1] < self.coordinates[i-1][1]:
            #     print("true")
            #     frame_distance = -1 * self.ref_constant * self.getCoordinateScale(self.coordinates[i - 1], self.coordinates[i])
            # else:
            #frame_distance = self.ref_constant * self.getCoordinateScale(self.coordinates[i - 1], self.coordinates[i])


            distance_per_frame.append(frame_distance)
            total_distance.append(frame_distance + total_distance[i - 1])

def findVelocity(distance_per_frame, velocity, time): #DONE
    for i in range(len(distance_per_frame)):
        if i == 0:
            velocity.append(0) #Velocity might not be zero at the start
        else:
            if time[i] == time[i-1]: #HACKY FIX TO PREVENT DIVISION BY 0
                velocity.append(velocity[-1])
            else:
                velocity.append(distance_per_frame[i] / (time[i] - time[i - 1]))

def findAcceleration(distance_per_frame, acceleration, velocity, time): #NEED TO SEE IF WE WANNA USE NORMALIZED VELOCITY TO CALCULATE ACCELERATION
    for i in range(len(distance_per_frame)):
        if i == 0:
            acceleration.append(0) #Velocity might not be zero at the start
        else:
            if time[i] == time[i-1]: #HACKY FIX TO PREVENT DIVISION BY 0
                acceleration.append(acceleration[-1])
            else:
                acceleration.append((velocity[i] - velocity[i - 1]) / pow((time[i] - time[i - 1]), 2))

def findMovingAverageVelocity(normalized_velocity, velocity): #DONE
    x = 100
    # for i in range(x + 1):
    #     athena = sum(self.vel)
    #     self.normalized_velocity.append(self.velocity[i])
    # for i in range(x + 1, len(self.velocity) - x):
    #     anjali = sum([self.velocity[val] for val in range(i-x, i+x+1)]) / (2 * x + 1)
    #     print(anjali)
    #     self.normalized_velocity.append(anjali)
    # for i in range(len(self.velocity) - x, len(self.velocity)):
    #     self.normalized_velocity.append(self.velocity[i])
    #normalized_velocity.append(velocity[0])
    for i in range(0 , len(velocity)):
        front = max(0, i-x) 
        back = min(len(velocity), i+x)
        delta = min(i-front, back-i)
        anjali = sum([velocity[val] for val in range(i - delta, i + delta)]) / (2*delta + 1)
        normalized_velocity.append(anjali)

def findMovingAverageAcce(normalized_acce, acceleration): #NEED TO SEE IF WE WANNA USE NORMALIZED VELOCITY TO CALCULATE ACCELERATION
    x = 5
    # for i in range(x + 1):
    #     athena = sum(self.vel)
    #     self.normalized_velocity.append(self.velocity[i])
    # for i in range(x + 1, len(self.velocity) - x):
    #     anjali = sum([self.velocity[val] for val in range(i-x, i+x+1)]) / (2 * x + 1)
    #     print(anjali)
    #     self.normalized_velocity.append(anjali)
    # for i in range(len(self.velocity) - x, len(self.velocity)):
    #     self.normalized_velocity.append(self.velocity[i])
    for i in range(0 , len(acceleration)):
        front = max(0, i-x) 
        back = min(len(acceleration), i+x)
        delta = min(i-front, back-i)
        anjali = sum([acceleration[val] for val in range(i - delta, i + delta)]) / (2*delta + 1)
        normalized_acce.append(anjali)






ref_list = [[0.121, 0.215], [0.9645, 0.446], 0.60]
with open('objectsData.json') as json_file:
    data = json.load(json_file)
print(data.keys())
test = calculate(data, ['ball', 'basketball', 'orange', 'fruit', 'lemon', 'food'], ref_list)
#test = DataUtils(json_string, ref_list)

plt.plot(test['time'], test['normalized_velocity'])

#print(test.velocity)
plt.show()
