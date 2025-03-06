"""
Dominio de transporte para el planificador pyhop.
Este dominio modela camiones, conductores y paquetes que necesitan ser transportados entre ciudades.
"""

import pyhop

# Funciones auxiliares
def can_walk(state, location1, location2):
    """Comprobar si un conductor puede caminar desde location1 hasta location2."""
    return location2 in state.walking_paths.get(location1, [])

def can_drive(state, location1, location2):
    """Comprobar si un camión puede ser conducido desde location1 hasta location2."""
    return location2 in state.driving_paths.get(location1, [])

def bus_cost(location1, location2):
    """Calcular el coste de tomar un autobús entre ubicaciones."""
    # Modelo de coste simple: coste fijo de 5 unidades
    return 5

# Operadores

def walk(state, driver, location1, location2):
    """El conductor camina desde location1 hasta location2."""
    if (state.driver_loc[driver] == location1 and 
        can_walk(state, location1, location2)):
        state.driver_loc[driver] = location2
        return state
    else:
        return False

def take_bus(state, driver, location1, location2):
    """El conductor toma un autobús desde location1 hasta location2."""
    if (state.driver_loc[driver] == location1 and 
        can_walk(state, location1, location2) and  # Los autobuses siguen las rutas peatonales
        state.driver_money[driver] >= bus_cost(location1, location2)):
        state.driver_loc[driver] = location2
        state.driver_money[driver] -= bus_cost(location1, location2)
        return state
    else:
        return False

def load_driver(state, driver, truck, location):
    """El conductor sube al camión en la ubicación indicada."""
    # Comprobar si el conductor ya está conduciendo otro camión
    for t in state.trucks:
        if state.truck_driver[t] == driver:
            print(f"DEBUG: El conductor {driver} ya está conduciendo el camión {t}")
            return False
    
    if (state.driver_loc[driver] == location and 
        state.truck_loc[truck] == location and 
        state.truck_driver[truck] is None):
        state.truck_driver[truck] = driver
        # Actualizar la ubicación del conductor para que coincida con la del camión
        # Esto es importante para rastrear la ubicación real del conductor
        state.driver_loc[driver] = location
        return state
    else:
        return False

def unload_driver(state, driver, truck, location):
    """El conductor baja del camión en la ubicación indicada."""
    if (state.truck_loc[truck] == location and 
        state.truck_driver[truck] == driver):
        state.truck_driver[truck] = None
        state.driver_loc[driver] = location
        return state
    else:
        return False

def drive_truck(state, driver, truck, location1, location2):
    """El conductor conduce el camión desde location1 hasta location2."""
    if (state.truck_loc[truck] == location1 and 
        state.truck_driver[truck] == driver and 
        can_drive(state, location1, location2)):
        state.truck_loc[truck] = location2
        # Actualizar la ubicación del conductor para que coincida con la del camión
        state.driver_loc[driver] = location2
        # Imprimir información de depuración
        print(f"DEBUG: Conduciendo camión {truck} desde {location1} hasta {location2}")
        return state
    else:
        # Imprimir información de depuración para el fallo
        print(f"DEBUG: No se pudo conducir el camión {truck} desde {location1} hasta {location2}")
        print(f"  Ubicación del camión: {state.truck_loc.get(truck)}")
        print(f"  Conductor del camión: {state.truck_driver.get(truck)}")
        print(f"  Se puede conducir: {can_drive(state, location1, location2)}")
        return False

def load_package(state, package, truck, location):
    """Cargar paquete en el camión en la ubicación indicada."""
    if (state.package_loc[package] == location and 
        state.truck_loc[truck] == location):
        state.package_loc[package] = truck
        return state
    else:
        return False

def unload_package(state, package, truck, location):
    """Descargar paquete del camión en la ubicación indicada."""
    if (state.package_loc[package] == truck and 
        state.truck_loc[truck] == location):
        state.package_loc[package] = location
        return state
    else:
        return False

# Declare operators
pyhop.declare_operators(walk, take_bus, load_driver, unload_driver, 
                        drive_truck, load_package, unload_package)
print()
pyhop.print_operators()

# Métodos

def deliver_package_already_there(state, package, goal_loc):
    """El paquete ya está en su ubicación objetivo."""
    if state.package_loc[package] == goal_loc:
        return []
    return False

def find_path(state, start, end, path_type='driving'):
    """Encontrar una ruta desde start hasta end usando BFS.
    path_type puede ser 'driving' o 'walking'."""
    if path_type == 'driving':
        paths = state.driving_paths
    else:  # walking
        paths = state.walking_paths
    
    # BFS para encontrar la ruta más corta
    queue = [[start]]
    visited = set([start])
    
    while queue:
        path = queue.pop(0)
        node = path[-1]
        
        if node == end:
            return path
        
        for neighbor in paths.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    
    return None  # No se encontró ninguna ruta

def deliver_package_in_truck(state, package, goal_loc):
    """El paquete está en un camión, necesita conducir hasta el objetivo y descargar."""
    truck = state.package_loc[package]
    if truck in state.truck_loc:  # Comprobar si el paquete está en un camión
        current_loc = state.truck_loc[truck]
        driver = state.truck_driver[truck]
        
        # Si el camión tiene un conductor, conducir hasta el objetivo y descargar
        if driver is not None:
            # Encontrar una ruta hasta el objetivo
            path = find_path(state, current_loc, goal_loc, 'driving')
            
            if path and len(path) > 1:
                # Crear un plan para conducir a través de cada paso en la ruta
                plan = []
                for i in range(len(path) - 1):
                    plan.append(('drive_truck', driver, truck, path[i], path[i+1]))
                
                # Añadir la acción de descargar al final
                plan.append(('unload_package', package, truck, goal_loc))
                return plan
            elif can_drive(state, current_loc, goal_loc):
                # Conducción directa
                return [('drive_truck', driver, truck, current_loc, goal_loc),
                        ('unload_package', package, truck, goal_loc)]
            else:
                print(f"DEBUG: No hay ruta de conducción desde {current_loc} hasta {goal_loc}")
                return False
        else:
            # Encontrar un conductor para conducir el camión
            for d in state.driver_loc:
                if state.driver_loc[d] == current_loc:
                    return [('load_driver', d, truck, current_loc),
                            ('deliver_package', package, goal_loc)]
            
            # No hay conductor en la ubicación del camión, necesita traer uno allí
            for d in state.driver_loc:
                return [('move_driver', d, current_loc),
                        ('deliver_package', package, goal_loc)]
    return False

def deliver_package_at_location(state, package, goal_loc):
    """El paquete está en una ubicación, necesita cargarse en un camión y entregarse."""
    current_loc = state.package_loc[package]
    
    # Encontrar un camión en la ubicación actual
    for truck in state.truck_loc:
        if state.truck_loc[truck] == current_loc:
            # Si el camión tiene un conductor, cargar paquete y entregar
            if state.truck_driver[truck] is not None:
                return [('load_package', package, truck, current_loc),
                        ('deliver_package', package, goal_loc)]
            else:
                # Encontrar un conductor para conducir el camión
                for d in state.driver_loc:
                    if state.driver_loc[d] == current_loc:
                        return [('load_driver', d, truck, current_loc),
                                ('load_package', package, truck, current_loc),
                                ('deliver_package', package, goal_loc)]
                
                # No hay conductor en la ubicación del camión, necesita traer uno allí
                for d in state.driver_loc:
                    return [('move_driver', d, current_loc),
                            ('deliver_package', package, goal_loc)]
    
    # No hay camión en la ubicación actual, necesita traer uno allí
    for truck in state.truck_loc:
        truck_loc = state.truck_loc[truck]
        if state.truck_driver[truck] is not None:
            driver = state.truck_driver[truck]
            return [('drive_truck', driver, truck, truck_loc, current_loc),
                    ('deliver_package', package, goal_loc)]
        else:
            # Encontrar un conductor para conducir el camión
            for d in state.driver_loc:
                if state.driver_loc[d] == truck_loc:
                    return [('load_driver', d, truck, truck_loc),
                            ('drive_truck', d, truck, truck_loc, current_loc),
                            ('deliver_package', package, goal_loc)]
                else:
                    return [('move_driver', d, truck_loc),
                            ('deliver_package', package, goal_loc)]
    
    return False

pyhop.declare_methods('deliver_package', 
                      deliver_package_already_there,
                      deliver_package_in_truck,
                      deliver_package_at_location)

def move_driver_already_there(state, driver, goal_loc):
    """El conductor ya está en la ubicación objetivo."""
    if state.driver_loc[driver] == goal_loc:
        return []
    return False

def move_driver_in_truck(state, driver, goal_loc):
    """El conductor está en un camión, necesita conducir hasta el objetivo y bajarse."""
    for truck in state.truck_loc:
        if state.truck_driver[truck] == driver:
            current_loc = state.truck_loc[truck]
            
            # Encontrar una ruta hasta el objetivo
            path = find_path(state, current_loc, goal_loc, 'driving')
            
            if path and len(path) > 1:
                # Crear un plan para conducir a través de cada paso en la ruta
                plan = []
                for i in range(len(path) - 1):
                    plan.append(('drive_truck', driver, truck, path[i], path[i+1]))
                
                # Añadir la acción de bajar al final
                plan.append(('unload_driver', driver, truck, goal_loc))
                return plan
            elif can_drive(state, current_loc, goal_loc):
                # Conducción directa
                return [('drive_truck', driver, truck, current_loc, goal_loc),
                        ('unload_driver', driver, truck, goal_loc)]
            else:
                print(f"DEBUG: No hay ruta de conducción desde {current_loc} hasta {goal_loc}")
                return False
    return False

def move_driver_walk(state, driver, goal_loc):
    """El conductor camina hasta la ubicación objetivo si es posible."""
    current_loc = state.driver_loc[driver]
    if can_walk(state, current_loc, goal_loc):
        return [('walk', driver, current_loc, goal_loc)]
    return False

def move_driver_bus(state, driver, goal_loc):
    """El conductor toma un autobús hasta la ubicación objetivo si es posible."""
    current_loc = state.driver_loc[driver]
    if (can_walk(state, current_loc, goal_loc) and  # Los autobuses siguen las rutas peatonales
        state.driver_money[driver] >= bus_cost(current_loc, goal_loc)):
        return [('take_bus', driver, current_loc, goal_loc)]
    return False

def move_driver_multi_step(state, driver, goal_loc):
    """El conductor se mueve a través de ubicaciones intermedias para llegar al objetivo."""
    current_loc = state.driver_loc[driver]
    
    # Encontrar una ruta hasta el objetivo
    path = find_path(state, current_loc, goal_loc, 'walking')
    
    if path and len(path) > 1:
        # Crear un plan para caminar a través de cada paso en la ruta
        plan = []
        for i in range(len(path) - 1):
            plan.append(('walk', driver, path[i], path[i+1]))
        return plan
    
    return False

pyhop.declare_methods('move_driver',
                      move_driver_already_there,
                      move_driver_in_truck,
                      move_driver_walk,
                      move_driver_bus,
                      move_driver_multi_step)

def move_truck_already_there(state, truck, goal_loc):
    """El camión ya está en la ubicación objetivo."""
    if state.truck_loc[truck] == goal_loc:
        return []
    return False

def move_truck_with_driver(state, truck, goal_loc):
    """El camión tiene un conductor, conducir hasta la ubicación objetivo."""
    driver = state.truck_driver[truck]
    current_loc = state.truck_loc[truck]
    if driver is not None and can_drive(state, current_loc, goal_loc):
        return [('drive_truck', driver, truck, current_loc, goal_loc)]
    return False

def move_truck_need_driver(state, truck, goal_loc):
    """El camión necesita un conductor para moverse a la ubicación objetivo."""
    current_loc = state.truck_loc[truck]
    
    # Encontrar un conductor en la ubicación actual
    for driver in state.driver_loc:
        if state.driver_loc[driver] == current_loc:
            return [('load_driver', driver, truck, current_loc),
                    ('move_truck', truck, goal_loc)]
    
    # No hay conductor en la ubicación del camión, necesita traer uno allí
    for driver in state.driver_loc:
        return [('move_driver', driver, current_loc),
                ('move_truck', truck, goal_loc)]
    
    return False

def move_truck_multi_step(state, truck, goal_loc):
    """El camión se mueve a través de ubicaciones intermedias para llegar al objetivo."""
    current_loc = state.truck_loc[truck]
    driver = state.truck_driver[truck]
    
    # Si el camión no tiene conductor, no podemos moverlo
    if driver is None:
        return False
    
    # Encontrar una ruta hasta el objetivo
    path = find_path(state, current_loc, goal_loc, 'driving')
    
    if path and len(path) > 1:
        # Crear un plan para conducir a través de cada paso en la ruta
        plan = []
        for i in range(len(path) - 1):
            plan.append(('drive_truck', driver, truck, path[i], path[i+1]))
        return plan
    
    return False

pyhop.declare_methods('move_truck',
                      move_truck_already_there,
                      move_truck_with_driver,
                      move_truck_need_driver,
                      move_truck_multi_step)

def achieve_goals_recursive(state, goal):
    """Lograr recursivamente todos los objetivos en el estado objetivo."""
    # Manejar objetivos de paquetes
    for package in goal.package_goals:
        if package not in state.achieved_package_goals:
            goal_loc = goal.package_goals[package]
            if state.package_loc[package] != goal_loc:
                state.achieved_package_goals.append(package)
                return [('deliver_package', package, goal_loc), 
                        ('achieve_goals', goal)]
    
    # Manejar objetivos de conductores
    for driver in goal.driver_goals:
        if driver not in state.achieved_driver_goals:
            goal_loc = goal.driver_goals[driver]
            if state.driver_loc[driver] != goal_loc:
                state.achieved_driver_goals.append(driver)
                return [('move_driver', driver, goal_loc), 
                        ('achieve_goals', goal)]
    
    # Manejar objetivos de camiones
    for truck in goal.truck_goals:
        if truck not in state.achieved_truck_goals:
            goal_loc = goal.truck_goals[truck]
            if state.truck_loc[truck] != goal_loc:
                state.achieved_truck_goals.append(truck)
                return [('move_truck', truck, goal_loc), 
                        ('achieve_goals', goal)]
    
    # Todos los objetivos logrados
    return []

pyhop.declare_methods('achieve_goals', achieve_goals_recursive)

# Define the initial state
state = pyhop.State('state')

state.locations = [
    'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao', 'Zaragoza',  # Ciudades
    'Path_Madrid_Barcelona', 'Path_Madrid_Valencia', 'Path_Barcelona_Sevilla', 
    'Path_Barcelona_Bilbao', 'Path_Valencia_Sevilla', 'Path_Valencia_Zaragoza', 
    'Path_Sevilla_Bilbao', 'Path_Bilbao_Zaragoza'  # Puntos de conexión
]

# Conexiones peatonales
state.walking_paths = {
    # Madrid
    'Madrid': ['Path_Madrid_Barcelona', 'Path_Madrid_Valencia'],
    'Path_Madrid_Barcelona': ['Madrid', 'Barcelona'],
    'Path_Madrid_Valencia': ['Madrid', 'Valencia'],
    
    # Barcelona
    'Barcelona': ['Path_Madrid_Barcelona', 'Path_Barcelona_Sevilla', 'Path_Barcelona_Bilbao'],
    'Path_Barcelona_Sevilla': ['Barcelona', 'Sevilla'],
    'Path_Barcelona_Bilbao': ['Barcelona', 'Bilbao'],
    
    # Valencia
    'Valencia': ['Path_Madrid_Valencia', 'Path_Valencia_Sevilla', 'Path_Valencia_Zaragoza'],
    'Path_Valencia_Sevilla': ['Valencia', 'Sevilla'],
    'Path_Valencia_Zaragoza': ['Valencia', 'Zaragoza'],
    
    # Sevilla
    'Sevilla': ['Path_Barcelona_Sevilla', 'Path_Valencia_Sevilla', 'Path_Sevilla_Bilbao'],
    'Path_Sevilla_Bilbao': ['Sevilla', 'Bilbao'],
    
    # Bilbao
    'Bilbao': ['Path_Barcelona_Bilbao', 'Path_Sevilla_Bilbao', 'Path_Bilbao_Zaragoza'],
    'Path_Bilbao_Zaragoza': ['Bilbao', 'Zaragoza'],
    
    # Zaragoza
    'Zaragoza': ['Path_Valencia_Zaragoza', 'Path_Bilbao_Zaragoza']
}

# Conexiones de conducción
state.driving_paths = {
    'Madrid': ['Barcelona', 'Valencia', 'Sevilla'],           # Madrid
    'Barcelona': ['Madrid', 'Valencia', 'Sevilla', 'Bilbao'], # Barcelona
    'Valencia': ['Madrid', 'Barcelona', 'Sevilla', 'Zaragoza'], # Valencia
    'Sevilla': ['Madrid', 'Barcelona', 'Valencia', 'Bilbao', 'Zaragoza'], # Sevilla
    'Bilbao': ['Barcelona', 'Sevilla', 'Zaragoza', 'Valencia'], # Bilbao
    'Zaragoza': ['Valencia', 'Sevilla', 'Bilbao']             # Zaragoza
}

# Printear ubicaciones para depuración
print("\nDriving paths:")
for loc in state.driving_paths:
    print(f"  From {loc} to: {state.driving_paths[loc]}")

# Conductores
state.drivers = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6']
state.driver_loc = {
    'D1': 'Barcelona', 'D2': 'Valencia', 'D3': 'Madrid',
    'D4': 'Sevilla', 'D5': 'Bilbao', 'D6': 'Zaragoza'
}
state.driver_money = {
    'D1': 10, 'D2': 15, 'D3': 20,
    'D4': 12, 'D5': 18, 'D6': 25
}

# Camiones
state.trucks = ['T1', 'T2', 'T3', 'T4']
state.truck_loc = {'T1': 'Barcelona', 'T2': 'Valencia', 'T3': 'Sevilla', 'T4': 'Bilbao'}
state.truck_driver = {'T1': None, 'T2': None, 'T3': None, 'T4': None}

# Paquetes
state.packages = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
state.package_loc = {
    'P1': 'Madrid', 'P2': 'Madrid', 'P3': 'Barcelona',
    'P4': 'Valencia', 'P5': 'Sevilla', 'P6': 'Bilbao'
}

# Goales logrados
state.achieved_package_goals = []
state.achieved_driver_goals = []
state.achieved_truck_goals = []

# Definir el goal state
goal = pyhop.Goal('goal')
goal.package_goals = {
    'P1': 'Barcelona', 'P2': 'Valencia', 'P3': 'Madrid',
    'P4': 'Zaragoza', 'P5': 'Bilbao', 'P6': 'Sevilla'
}
goal.driver_goals = {'D1': 'Madrid', 'D4': 'Zaragoza'}
goal.truck_goals = {'T1': 'Madrid', 'T3': 'Zaragoza'}

# Printear Initial state y Goal
print("\nInitial state:")
pyhop.print_state(state)

print("\nGoal:")
pyhop.print_goal(goal)

print("\nSolving transportation problem...")
result = pyhop.pyhop(state, [('achieve_goals', goal)], verbose=3)

if result:
    print("\nPlan found:")
    for action in result[0]:
        print(f"  {action}")
else:
    print("\nNo plan found.")

print("\nFinal state:")
if result and len(result) > 1:
    pyhop.print_state(result[1])
else:
    print("No final state available.")
