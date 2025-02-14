"""
The "travel from home to the park" example from Dana Nau lectures.
Author: Dana Nau <nau@cs.umd.edu>, May 31, 2013
This file should work correctly in both Python 2.7 and Python 3.2.

Modified: Antonio Garrido
Recursive version with multiple goal
"""

import pyhop


# Funcion auxiliar

def taxi_rate(dist):
    return 1.5 + 0.5 * dist


# Operadores: devuelven el estado (si las conds se cumplen) o False (si las conds no se cumplen)
# Importante: los operadores NO se pueden descomponer

def walk(state, a, x, y):
    if state.loc[a] == x:
        state.loc[a] = y
        return state
    else:
        return False


def call_taxi(state, a, x):
    if state.wants_taxi[a]:
        state.phoned_times[a] += 1
        state.loc['taxi'] = x
        return state
    else:
        return False


def wait_taxi(state, a):
    state.waiting_time[a] += 10
    return state


def read_book(state, a):
    state.read_book[a] = True
    return state


def ride_taxi(state, a, x, y):
    if state.loc['taxi'] == x and state.loc[a] == x:
        state.loc['taxi'] = y
        state.loc[a] = y
        state.owe[a] = taxi_rate(state.dist[x][y])
        return state
    else:
        return False


def pay_driver(state, a):
    if state.cash[a] >= state.owe[a]:
        state.cash[a] = state.cash[a] - state.owe[a]
        state.owe[a] = 0
        return state
    else:
        return False


# Declaración de los operadores. NO BASTA con definirlos con "def" sino que
# también hay que indicárselo a pyhop.
# Importante: se deben declarar TODOS los operadores en un ÚNICO "declare_operators"

pyhop.declare_operators(walk, call_taxi, wait_taxi, read_book, ride_taxi, pay_driver)
print()
pyhop.print_operators()


# Definición de dos metodos para "read_if_necessary_book". Solo uno de ellos se ejecutará
# como máximo. Deben devolver un conjunto de operadores/tareas (aunque sea vacío) o False
# si no se puede aplicar

def do_read(state, a, x, y):
    if not state.read_book[a]:
        return [('read_book', a)]
    return False


def dont_read(state, a, x, y):
    if state.read_book[a]:
        return []
    return False


# Indicamos cual es la descomposición de "read_if_necessary_book"

pyhop.declare_methods('read_if_necessary_book', do_read, dont_read)


# Definición de dos métodos para "travel". Solo uno de ellos se ejecutará como máximo

def travel_by_foot(state, a, x, y):
    if state.dist[x][y] <= 2:
        return [('walk', a, x, y)]
    return False


def travel_by_taxi(state, a, x, y):
    if state.cash[a] >= taxi_rate(state.dist[x][y]):
        return [('call_taxi', a, x), ('wait_taxi', a), ('read_if_necessary_book', a, x, y), ('ride_taxi', a, x, y),
                ('pay_driver', a)]
    return False


pyhop.declare_methods('travel_method', travel_by_foot, travel_by_taxi)


def travel_recursive(state, goal):
    if len(goal.loc) > 0:
        # solo nos interesa el primer goal
        for who in goal.loc.keys():
            x = state.loc[who]
            y = goal.loc.pop(who)  # extraemos (se elimina) el goal del diccionario
            break
        return [('travel_method', who, x, y), ('travel', goal)]
    return []  # caso base: si len(goal.loc) == 0


# Indicamos cuál es la descomposición de "travel"

pyhop.declare_methods('travel', travel_recursive)
print()
pyhop.print_methods()

# Definicion del estado

state1 = pyhop.State('state1')

# Datos para "me" y "you"

state1.loc = {'me': 'home', 'you': 'home'}  # the location of "me"
state1.cash = {'me': 20, 'you': 40}  # the money "me" has
state1.owe = {'me': 0, 'you': 0}  # the money "me" owes
state1.phoned_times = {'me': 0, 'you': 0}  # how many times "me" has phoned
state1.wants_taxi = {'me': True, 'you': True}  # does "me" want a taxi?
state1.waiting_time = {'me': 0, 'you': 0}  # waiting time for a taxi of "me"
state1.read_book = {'me': False, 'you': True}  # has "me" read the book?

# Distribución de las distancias

state1.dist = {'home': {'park': 8, 'university': 10}, 'park': {'home': 8, 'university': 6},
               'university': {'home': 10, 'park': 6}}

# Definición del objetivo

goal1 = pyhop.Goal('goal1')
goal1.loc = {'me': 'park', 'you': 'university'}

print("""
****************************************************************************************
Call pyhop.pyhop(state1,[('travel','me','home','park')]) with different verbosity levels
****************************************************************************************
""")

# Buscamos un plan a partir de un estado inicial para que "me" viaje de "home" a "park"

# pyhop.pyhop(state1, [('travel','me','home','park')], verbose=1)
pyhop.pyhop(state1, [('travel', goal1)], verbose=3)

"""
Importante para depurar:

Necesitamos: import pdb

Ponemos la instruccion "pdb.set_trace()" donde queramos en nuestro codigo y se detendra la ejecucion
Luego simplemente escribimos la letra 'n' desde el shell que ejecutara la siguiente sentencia y podemos ir
viendo el valor de las variables
"""
