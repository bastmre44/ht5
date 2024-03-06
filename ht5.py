import simpy
import random
import matplotlib.pyplot as plt

# Definición de las variables y parámetros
Random_seed = 42
Memory_capacity = 100
Process_interval = 200
CPU_speed = 5
simulation_time = 1000

random.seed(Random_seed)

# Lista para almacenar el estado de la memoria durante la simulación
memory_usage = []

# Clase Process para representar el proceso de la simulación
class Process:
    def __init__(self, env, am, memory, instructions):
        self.env = env
        self.am = am
        self.memory = memory
        self.instructions = instructions
        # Crear un proceso en el entorno de simulación
        self.action = env.process(self.run())

    def run(self):
        # Para solicitar memoria
        with self.am.get(self.memory) as req:
            yield req
            # Proceso estado ready
            print(f'Proceso listo para ejecutar - Memoria solicitada: {self.memory}')
            
            # Proceso estado running
            while self.instructions > 0:
                # Se ejecutan las instrucciones
                instructions_to_execute = min(self.instructions, CPU_speed)
                print(f'Ejecutando {instructions_to_execute} instrucciones')
                yield self.env.timeout(1)
                self.instructions -= instructions_to_execute
                # Se guarda el estado de la memoria
                memory_usage.append(Memory_capacity - self.am.level)  

            # Para verificar si el proceso ha terminado
            if self.instructions == 0:
                print('Proceso terminado')

                # Para verificar si el proceso tiene que volver o esperar a la cola ready
                wait_decision = random.randint(1, 2)
                if wait_decision == 1:
                    print('Esperando por operaciones de I/O')
                    yield self.env.timeout(random.randint(1, 2))
                    print("Operaciones de I/O finalizadas, regresando a ready")
                else:
                    print('Regresando a la cola de ready')

            # Para proceso en estado terminated/waiting/ready
            if self.instructions == 0:
                print('Proceso terminado y liberando memoria utilizada.')
            else:
                print('Proceso en espera o listo para volver a ejecutar.')

            # Se libera la memoria que se estaba utilizando
            yield self.am.put(self.memory)

# Generador de procesos
def generate_processes(env, am):
    while True:
        process_memory = random.randint(1, 10)
        process_instructions = random.randint(1, 10)
        # Crear un proceso
        p = Process(env, am, process_memory, process_instructions)
        # Esperar un tiempo aleatorio para generar otro proceso
        yield env.timeout(random.expovariate(1.0 / Process_interval))

# Instancia Environment y se define la RAM como un contenedor
env = simpy.Environment()
am = simpy.Container(env, init=Memory_capacity, capacity=Memory_capacity)

# Generar procesos para ejecutar la simulación
env.process(generate_processes(env, am))

# Ejecutar la simulación hasta que alcance el tiempo de simulación especificado
env.run(until=simulation_time)

# Gráfico de la capacidad de memoria utilizada en función del tiempo
plt.plot(memory_usage)
plt.xlabel('Tiempo')
plt.ylabel('Capacidad de memoria utilizada')
plt.title('Uso de memoria durante la simulación')
plt.show()
