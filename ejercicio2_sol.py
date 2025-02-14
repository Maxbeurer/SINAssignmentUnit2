from math import sqrt, pow, inf

import pyhop


def distance(c1, c2):
    x = pow(c1['X'] - c2['X'], 2)
    y = pow(c1['Y'] - c2['Y'], 2)
    return sqrt(x + y)


def select_new_city(state, y):  # evaluation function
    x = state.location_car
    best = inf  # big float
    for c in state.connection.keys():
        if c not in state.path and c in state.connection[x]:
            g = state.cost
            h = distance(state.coordinates[c], state.coordinates[y])
            if g + h < best:
                best_city = c
                best = g + h
    return best_city


def travel_op(state, y):
    x = state.location_car
    if state.location == 'in_car' and y in state.connection[x]:
        state.location_car = y
        state.path.append(y)
        state.cost += distance(state.coordinates[x], state.coordinates[y])
        return state
    else:
        return False


def load_car_op(state):
    if state.location == state.location_car:
        state.location = 'in_car'
        return state
    else:
        return False


def unload_car_op(state):
    if state.location == 'in_car':
        state.location = state.location_car
        return state
    else:
        return False


pyhop.declare_operators(travel_op, load_car_op, unload_car_op)
print()
pyhop.print_operators()


def travel_m(state, goal):
    x = state.location_car
    y = goal.final
    if x != y:
        z = select_new_city(state, y)
        g = pyhop.Goal('g')
        g.final = y
        return [('travel_op', z), ('travel_to_city', g)]  # method solved by travel_op, and new travel_to_city task
    return False


def already_there(state, goal):
    x = state.location_car
    y = goal.final
    if x == y:
        return []
    return False


pyhop.declare_methods('travel_to_city', travel_m, already_there)  # task travel_to_city solvable by two methods


def travel_by_car(state, goal):
    x = state.location
    y = goal.final
    if x != y:
        return [('load_car_op',), ('travel_to_city', goal), ('unload_car_op',)]  # load/unload ops, task travel_to_city
    return False


pyhop.declare_methods('travel', travel_by_car)  # travel is the top most task that we use to specify the goal
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
state1.location_car = 'Huelva'
state1.path = ['Huelva']
state1.cost = 0

# GOAL
goal1 = pyhop.Goal('goal1')
goal1.final = 'Almeria'

# print('- If verbose=3, Pyhop also prints the intermediate states:')

result = pyhop.pyhop(state1, [('travel', goal1)], verbose=3)
