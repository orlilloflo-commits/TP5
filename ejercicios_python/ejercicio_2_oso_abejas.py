"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# TODO PARA EL ESTUDIANTE:
# 1. Define los mecanismos de sincronización necesarios:
# - Un cerrojo (Lock) o semáforo binario para exclusión mutua en el tarro.
# - Un semáforo para despertar al oso cuando el tarro esté lleno.
# - Un semáforo para que las abejas esperen si el tarro está lleno o el oso está comiendo.
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)

def abeja(id_abeja):
    global tarro_miel, simulacion_activa
    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))
        
        # 1. Esperar a que el tarro esté disponible
        sem_tarro_disponible.acquire()
        
        # 2. Entrar en exclusión mutua con el tarro
        with mutex:
            # 3. Depositar una porción de miel
            tarro_miel += 1
            print(f"[Abeja {id_abeja}] Puso 1 porción. Total en tarro: {tarro_miel}/{M}")
            
            # 4. Si tarro_miel == M, avisar/despertar al oso dormido
            if tarro_miel == M:
                print(f"[Abeja {id_abeja}] ¡Tarro lleno! Despertando al oso 🐻")
                sem_oso.release()
            else:
                # 5. Si no está lleno, permitir que otras abejas sigan produciendo
                sem_tarro_disponible.release()

def oso(max_tarros=2):
    global tarro_miel, simulacion_activa
    tarros_comidos = 0
    while tarros_comidos < max_tarros and simulacion_activa:
        # 1. Esperar pasivamente hasta que una abeja señale que el tarro está lleno
        sem_oso.acquire()
        
        # 2. Comerse toda la miel (en exclusión mutua)
        with mutex:
            print(f"🐻 [Oso] ¡Desperté! Comiendo toda la miel del tarro (estaba lleno con {tarro_miel} porciones).")
            # 3. Reiniciar el tarro e incrementar tarros comidos
            tarro_miel = 0
            tarros_comidos += 1
            
            # 4. Avisar a las abejas que el tarro está vacío y disponible de nuevo
            sem_tarro_disponible.release()
        
    simulacion_activa = False

if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)
    # Crear e iniciar el hilo del oso
    hilo_oso = threading.Thread(target=oso, args=(2,))
    hilo_oso.start()

    # Crear e iniciar los hilos de las abejas
    hilos_abejas = []
    for i in range(1, NUM_ABEJAS + 1):
        h = threading.Thread(target=abeja, args=(i,))
        hilos_abejas.append(h)
        h.start()

    # Esperar a que termine el oso
    hilo_oso.join()
    print("\n✅ Simulación finalizada con éxito.")

