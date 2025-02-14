from math import sqrt, pow, inf

import pyhop

#Function to calculate the distance between two points
def distance(p1, p2):
    x = pow(p1['X'] - p2['X'], 2)
    y = pow(p1['Y'] - p2['Y'], 2)
    return sqrt(x + y)


def select_new_city(state, y):  # evaluation function
    x = state.car_driving_location
    best = inf  # big float
    for c in state.connection.keys():
        if c not in state.path and c in state.connection[x]:
            g = state.cost
            h = distance(state.coordinates[c], state.coordinates[y])
            if g + h < best:
                best_city = c
                best = g + h
    return best_city


def gather_samples(state,target):
    x = state.rover_location

    if x in state.optimal_recharge_points:
        if x in state.sample_points[target] and state.rover_carrying_samples == False and state.rover_carrying_data == False and state.rover_battery >= 50:
            state.rover_gathered_points.append(x)
            state.rover_carrying_samples = True
            state.rover_battery -= 50
            state.rover_current_mission_route=[]
            return state
        else:
            return False
                
    else:
        if x in state.sample_points[target] and state.rover_carrying_samples == False and state.rover_carrying_data == False and state.rover_battery >= 150:
            state.rover_gathered_points.append(x)
            state.rover_carrying_samples = True

            state.rover_battery -= 50
            state.rover_current_mission_route=[]
            return state
        else:
            return False


def analyse_samples(state):
    x = state.rover_location
    if x in state.optimal_recharge_points:
        if state.rover_carrying_samples == True and state.rover_battery >= 50:
            state.rover_carrying_samples = False
            state.rover_carrying_data = True
            state.rover_battery -= 50
            return state
        else:
            return False
    else:
        if state.rover_carrying_samples == True and state.rover_battery >= 150:
            state.rover_carrying_samples = False
            state.rover_carrying_data = True
            state.rover_battery -= 50
            return state
        else:
            return False

def transfer_data(state):
    if state.rover_carrying_data == True and state.rover_battery >= 150:
        state.rover_carrying_data = False
        state.rover_mission_list.pop(0)
        state.rover_battery -= 50
        return state
    else:
        return False

# I WAS HERE

def travel_op(state, y):
    x = state.car_driving_location
    d = distance(state.coordinates[x], state.coordinates[y])
    if y in state.connection[x] and state.carloaded == True and state.car_driving_fuel >= d:
        state.car_driving_location = y
        state.path.append(y)
        state.cost += d
        state.car_driving_fuel -= d
        return state
    else:
        return False

pyhop.declare_operators(travel_op,load_car_op,unload_car_op)
print()
pyhop.print_operators()


def travel_m(state, goal):
    x = state.car_driving_location
    y = goal.final
    if x != y:
        z = select_new_city(state, y)
        g = pyhop.Goal('g')
        g.final = y
        return [('travel_op', z), ('travel_to_city', g)]
    return False


def already_there(state, goal):
    x = state.car_driving_location
    y = goal.final
    if x == y:
        return []
    return False


pyhop.declare_methods('travel_to_city', travel_m, already_there)


def do_mission(state, goal):
    x = state.rover_mision_list
    y = goal.final
    if x != y:
        return [('gather_samples',x[0]),('analyse_samples',),('transfer_data',),('navigate', goal), ('explore', goal)]
    return False

def final(state, goal):
    if state.rover_mision_list == goal.final:
        return []
    return False
pyhop.declare_methods('explore', do_mission, final)
print()
pyhop.print_methods()

# INITIAL STATE

state1 = pyhop.State('state1')
state1.coordinates = {'A': {'X': 100, 'Y': 200}, 'B': {'X': 200, 'Y': 200}, 'C': {'X': 300, 'Y': 300},
                      'D': {'X': 300, 'Y': 100}, 'E': {'X': 400, 'Y': 200}, 'F': {'X': 400, 'Y': 400},
                      'G': {'X': 400, 'Y': 0}, 'H': {'X': 500, 'Y': 300}, 'I': {'X': 500, 'Y': 100}, 'J': {'X': 600, 'Y': 200}, 'K': {'X': 700, 'Y': 200}}
state1.connection = {'A': {'B'}, 'B': {'A', 'C', 'D'},
                     'C': {'B', 'F'}, 'D': {'B', 'G'},
                     'E': {'F', 'G'},
                     'F': {'C', 'E', 'H'}, 'G': {'D', 'E', 'I'},
                     'H': {'F', 'J'}, 'I': {'G', 'J'}, 
                     'J': {'H', 'I', 'K'}, 'K': {'J'}}

state1.sample_points = {'soil': {'B', 'H', 'I'}, 'rock': {'D', 'C', 'F'}, 'ice': {'E', 'G', 'J'}, 'plant': {'K'}}

state1.optimal_recharge_points = ['A', 'B', 'E', 'F', 'G', 'J', 'K'] 
state1.optimal_transfer_points = ['C', 'D', 'H', 'I']
state1.rover_location = 'A'

state1.rover_current_mission_route = ['A']

state1.rover_gathered_points = []

state1.rover_battery = 500


state1.rover_mission_list = ['rock', 'ice', 'soil', 'plant', 'rock', 'ice', 'soil']

state1.rover_carrying_samples = False
state1.rover_carrying_data = False
# GOAL
goal1 = pyhop.Goal('goal1')
goal1.final = []

# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('explore', goal1)], verbose=3)
