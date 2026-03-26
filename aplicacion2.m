[X,Y,Z] = ndgrid(1:100, 1:100, 1:100); %creamos nube de puntos representando un cubo

puntos = [X(:), Y(:), Z(:)]; %guardamos esa nube de puntos en una mamtriz de 1,000,000 x 3 

% Rotacion 
theta = deg2rad(60); %definimos el angulo de rotacion 
Rx = [1 0 0;
      0 cos(theta) -sin(theta);
      0 sin(theta)  cos(theta)]; %matriz de rotacion x

Ry = [ cos(theta) 0 sin(theta);
       0          1 0;
      -sin(theta) 0 cos(theta)]; % matriz de rotacion y

Rz = [cos(theta) -sin(theta) 0;
      sin(theta)  cos(theta) 0;
      0           0          1]; %matriz de rotacion z

R = Rz * Ry * Rx; %rotacion general, primero sobre x luego sobre y al ultimo sobre z

tic %comenzamos la medicion del tiempo 

spmd % trabajamos sobre spmd 

    if spmdIndex == 1 %elegimos a nuestro master, en este caso el procesador 1
        
        n = size(puntos,1); % numero total de puntos 
        bloque = floor(n / spmdSize); %deterinamos la cantidad de elementos con los que va a trabajar cada worker 
        partes = cell(1, spmdSize); %creamos un arreglo vacio para cada worker incluido del master (spmdSize=4)(matriz 1x4)
        
        inicio = 1;
        %el siguiente ciclo permite divir los elementos de la matriz en los bloques asignados para cada worker
        for i = 1:spmdSize %ciclo de 1-4
            if i == spmdSize 
                fin = n; % el ultimo worker recibe los puntos restantes si la division no fue equitativa 
            else  
                fin = inicio + bloque - 1; % los workers reciben su seccion de puntos 
            end
            partes{i} = puntos(inicio:fin, :); % se guarda cada seccion de "bloque" creada
                                                                                        
            inicio = fin + 1; %seguimos con el siguiente bloque
        end

        for destino = 2:spmdSize
            spmdSend(partes{destino}, destino); %enviamos cada parte creada a su destino comenzamos en 2 porque 1 esta reservado para el master                                           
        end
        parte_local = partes{1}; %el master ya tiene su propia parte de "bloque" 
        resultado_local = (R * parte_local')'; %master procesa su parte 

        resultados = cell(1, spmdSize); % juntamos los resultados de todos los workers
        resultados{1} = resultado_local; % master guarda su propio trabajo

        for fuente = 2:spmdSize
            resultados{fuente} = spmdReceive(fuente); %master recibe el resultado de todos los workers 
        end

        puntos_rotados = vertcat(resultados{:}); % jutamos el resultados de todos una detras de otro de forma vertical , recreamos la matriz de 1,000,000 x 3

    else
        
        parte_local = spmdReceive(1); %cada worker recibe su bloque de puntos 
        resultado_local = (R * parte_local')'; % procesa sus datos(aplica la rotacion)
        spmdSend(resultado_local, 1); %envia el resultado al master 
        
        puntos_rotados = []; %los workers nos acumulan resultados; solo el master
        
    end

end %terminamos smpd
tiempo_paralelo = toc;%detenemos el tiempo 

puntos_rotados = puntos_rotados{1}; %extraemos el resultado del master para poder graficar 

fprintf('Tiempo Paralelo: %.6f s\n', tiempo_paralelo); %impriminos el tiempo que se tardo el envio/procesamiento/devolucion 
%graficamos
figure;

subplot(1,2,1)
scatter3(puntos(:,1), puntos(:,2), puntos(:,3), 'filled')
title('Original')
grid on
axis equal

subplot(1,2,2)
scatter3(puntos_rotados(:,1), puntos_rotados(:,2), puntos_rotados(:,3), 'filled')
title('Rotado 60°')
grid on
axis equal