
# Rotación de nube de puntos usando SPMD (MATLAB)

## Descripción

Este proyecto implementa un algoritmo de cómputo paralelo utilizando el modelo SPMD en MATLAB para aplicar una rotación en 3D a una nube de puntos.

## Metodología

* Generación de una nube de puntos (1M,8M2,27M,64M,125M)
* Definición de matrices de rotación en X, Y, Z
* Distribución de datos mediante modelo master-worker
* Procesamiento paralelo usando `spmd`, `spmdSend` y `spmdReceive`

## Resultados

Se comparó el desempeño del algoritmo paralelo y secuencial, obteniendo menor tiempo en secuencial que en paralelo.

## Archivos

* `aplicacion2.m`: implementación principal
* `cubo.png`: grafica del cubo normal y rotado
* `n_vs_tiempo.jpg`: grafica del número de puntos vs tiempo 
* `n_vs_speedup.jpg`: grafica del número de puntos vs el Speedup
* `n_vs_eficiencia.jpg`: grafica del número de puntos vs Eficiencia
 

## Autor

[Galicia Orihuela Johnny Michael]

