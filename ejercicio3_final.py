from math import sqrt, pow, inf

import pyhop


def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
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


def load_car_op(state, ):
    x = state.location
    for car in state.cars.keys():
        if state.cars[car]['location'] == x and car in state.cars_available:
            state.carloaded = True
            state.car_driving = car
            state.car_driving_location = state.cars[car]['location']
            state.car_driving_fuel = state.cars[car]['fuel']
            return state
    else:
        return False


def unload_car_op(state):
    if state.carloaded == True:
        state.carloaded = False
        state.location = state.car_driving_location
        state.cars[state.car_driving]['location'] = state.car_driving_location
        state.cars[state.car_driving]['fuel'] = state.car_driving_fuel
        return state
    else:
        return False
    
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


def travel_by_car(state, goal):
    x = state.location
    y = goal.final
    if x != y:
        return [('load_car_op',), ('travel_to_city', goal), ('unload_car_op',), ('travel', goal)]
    return False

def change_car(state, goal):
    x = state.location
    y = goal.final
    if x != y and state.cars_available:
        state.cars_available.pop(0)
        return [('travel', goal)]
    return False

def final(state, goal):
    if state.location == goal.final:
        return []
    return False
pyhop.declare_methods('travel', travel_by_car, change_car, final)
print()
pyhop.print_methods()

# INITIAL STATE

state1 = pyhop.State('state1')
state1.coordinates = {'Huelva': {'X': 25, 'Y': 275}, 'Cadiz': {'X': 200, 'Y': 50}, 'Sevilla': {'X': 250, 'Y': 325},
                      'Cordoba': {'X': 475, 'Y': 450}, 'Malaga': {'X': 550, 'Y': 100}, 'Jaen': {'X': 750, 'Y': 425},
                      'Granada': {'X': 800, 'Y': 250}, 'Almeria': {'X': 1000, 'Y': 150}}
state1.connection = {'Huelva': {'Sevilla'}, 'Sevilla': {'Cadiz', 'Huelva', 'Cordoba', 'Malaga'},
                     'Cadiz': {'Sevilla', 'Malaga'}, 'Cordoba': {'Sevilla', 'Malaga', 'Jaen'},
                     'Malaga': {'Cadiz', 'Huelva', 'Cordoba', 'Sevilla', 'Granada', 'Almeria'},
                     'Jaen': {'Cordoba', 'Granada'}, 'Granada': {'Jaen', 'Malaga', 'Almeria'},
                     'Almeria': {'Granada', 'Malaga'}}
state1.location = 'Huelva'
state1.carloaded = False
state1.car_driving = None
state1.car_driving_location = None
state1.car_driving_fuel = 0
state1.path = ['Huelva']
state1.cost = 0
state1.cars = {'c0':{'fuel':100, 'location':'Huelva'},'c1':{'fuel':500, 'location':'Huelva'}, 'c2':{'fuel':2000, 'location':'Huelva'}}
state1.cars_available = ['c0', 'c1', 'c2']
# GOAL
goal1 = pyhop.Goal('goal1')
goal1.final = 'Almeria'

# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('travel', goal1)], verbose=3)
