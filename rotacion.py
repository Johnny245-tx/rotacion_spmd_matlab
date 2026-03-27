import time
import numpy as np
from mpi4py import MPI
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
 
#Inicio mpi 
comm = MPI.COMM_WORLD          # Comunicador global 
rank = comm.Get_rank()         
size = comm.Get_size()  

# creamos nube de puntos representando un cubo 
coords = np.arange(0,100)
X, Y, Z = np.meshgrid(coords, coords, coords, indexing='ij')
puntos = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
# guardamos esa nube de puntos en una matriz de 1,000,000x3
 
#angulo de rotacion 
theta = np.deg2rad(60)       
 
# rotacion alrededor del eje X
Rx = np.array([[1,              0,             0],
               [0,  np.cos(theta), -np.sin(theta)],
               [0,  np.sin(theta),  np.cos(theta)]])
 
# rotacion alrededor del eje Y
Ry = np.array([[ np.cos(theta), 0, np.sin(theta)],
               [             0, 1,             0],
               [-np.sin(theta), 0, np.cos(theta)]])
 
# rotacion alrededor del eje Z
Rz = np.array([[np.cos(theta), -np.sin(theta), 0],
               [np.sin(theta),  np.cos(theta), 0],
               [            0,              0, 1]])
 
# rotacion compuesta, primero sobre x luego sobre y, al final sobre z
R = Rz @ Ry @ Rx
tic = time.perf_counter()
# definimos al master 
if rank == 0:
    n = puntos.shape[0] #numero total de puntos
    bloque = n // size  # puntos con los que va a trabajar cada worker
    partes = [] #creamos una lista vacia para cada worker
    
    inicio = 0
    # en el siguiente ciclo vamos a dividir los elementos de la matriz en los bloques asignados a cada worker
    for i in range(size): 
        if i == size - 1:
            fin = n #el ultimo worker recibe los puntos restantes si la division no es entera
        else: 
            fin= inicio + bloque  # los workers reciben su seccion de puntos 
        partes.append(puntos[inicio:fin, :]) # se guarda cada seccion de "bloque" creada
        inicio = fin #se define el nuevo inicio desde el utimo valor que se agrego en el ultimo bloque
 
    #enviamos cadabloque a su destino, comenzamos en 1 porque el worker no se manda a el mismo
    for destino in range(1, size):
        comm.Send(partes[destino], dest=destino, tag=0)  # tag=0 identifica el mensaje
 
    parte_local = partes[0] # el master procesa su propio bloque
 
else:
    # Para recibir con comm.Recv necesitamos un buffer pre-reservado.
    # El master envio puntos float64, entonces reservamos ese dtype.

    status = MPI.Status() #primero recibimos el status para saber cuantas filas vienen 
    comm.Probe(source=0, tag=0, status=status) #inspeccionamos los bloques sin consumir memoria 
    count  = status.Get_count(MPI.DOUBLE) // 3 # reconocemos que vienen numeros de floatx64 y que son 3 columnas 
    parte_local = np.empty((count, 3), dtype=np.float64)
    comm.Recv(parte_local, source=0, tag=0) #recibimos el bloque real
 
#todos los procesos rotan su parte local 
resultado_local = (R @ parte_local.T).T

# los workers envian su trabajo al master 
if rank == 0: #detectamos al master 
    resultados = [resultado_local] #el master ya tiene su resultado
 
    for fuente in range(1, size):
        # reservamos buffer del mismo tamaño que envio ese worker
        n_fuente = len(partes[fuente])
        buf = np.empty((n_fuente, 3), dtype=np.float64)
        comm.Recv(buf, source=fuente, tag=1)   # tag=1 para los resultados
        resultados.append(buf)
 
    # concatenamos todos los resultados (equivale a vertcat en MATLAB)
    puntos_rotados = np.vstack(resultados)
    tiempo_paralelo = time.perf_counter() - tic

    print(f"Tiempo paralelo ({size} procesos): {tiempo_paralelo:.6f} s")
    print(f"Forma final de puntos_rotados: {puntos_rotados.shape}")
else:
    comm.Send(resultado_local, dest=0, tag=1)  # Devolvemos resultado al master