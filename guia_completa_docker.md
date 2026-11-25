# Guía Completa de Docker: Todo lo que Debes Saber

Esta guía reúne los conceptos fundamentales, arquitectura, archivos de configuración, redes, almacenamiento y comandos esenciales para dominar **Docker** y **Docker Compose**, incluyendo ejemplos aplicados a entornos de laboratorio y desarrollo.

---

## 1. ¿Qué es Docker y para qué sirve?

**Docker** es una plataforma de código abierto que permite empaquetar una aplicación junto con todas sus dependencias (código, librerías, variables de entorno y herramientas del sistema) dentro de unidades estandarizadas y aisladas llamadas **contenedores**.

### ¿Qué problema resuelve?
* **Portabilidad total:** Elimina el clásico *"en mi ordenador funciona, pero en el tuyo falla"*. Si un contenedor funciona en tu portátil, funcionará igual en cualquier servidor Linux, Windows o nube.
* **Aislamiento:** Cada contenedor tiene su propio sistema de archivos, procesos y tarjeta de red virtual, sin interferir con tu sistema operativo anfitrión ni con otros contenedores.
* **Rapidez y ligereza:** A diferencia de una máquina virtual tradicional, un contenedor no necesita instalar un sistema operativo completo desde cero.

### Contenedores vs. Máquinas Virtuales (VM)

| Característica | Máquina Virtual (VirtualBox / VMware) | Contenedor Docker |
| :--- | :--- | :--- |
| **Arquitectura** | Virtualiza el hardware completo e incluye un SO invitado entero. | Virtualiza a nivel de sistema operativo; comparte el kernel del host. |
| **Tamaño en disco** | Muy pesado (decenas de GB por cada máquina). | Muy ligero (desde unos pocos MB hasta cientos de MB). |
| **Tiempo de arranque** | Minutos. | Milisegundos o pocos segundos. |
| **Rendimiento** | Mayor consumo de RAM y CPU por sobrecarga del hipervisor. | Rendimiento casi nativo. |

---

## 2. Conceptos Fundamentales (La Arquitectura)

Para entender Docker basta con dominar cuatro piezas clave:

1. **Imagen (`Image`):** Es una plantilla o "molde" de solo lectura que contiene el sistema base, el código de la aplicación y sus dependencias. Se construye por capas.
2. **Contenedor (`Container`):** Es una instancia viva y en ejecución de una imagen. Puedes crear, encender, pausar o borrar tantos contenedores como quieras a partir de una misma imagen.
3. **Registro (`Registry` / Docker Hub):** Es el repositorio en la nube (como GitHub, pero para imágenes) donde se almacenan y descargan imágenes oficiales (`python`, `ubuntu`, `nginx`, `postgres`, etc.).
4. **Docker Engine (Daemon + CLI):** Es el motor que corre en segundo plano gestionando los contenedores y la interfaz de línea de comandos (`docker ...`) con la que le das órdenes.

---

## 3. El `Dockerfile`: Cómo crear tus propias imágenes

Un **`Dockerfile`** es un archivo de texto sin extensión que funciona como receta paso a paso para construir una imagen personalizada.

### Instrucciones principales de un `Dockerfile`

| Instrucción | Qué hace | Ejemplo |
| :--- | :--- | :--- |
| **`FROM`** | Define la imagen base sobre la que se construye todo (siempre va primero). | `FROM python:3.12-slim` |
| **`WORKDIR`** | Crea y establece la carpeta de trabajo dentro del contenedor. | `WORKDIR /app` |
| **`COPY`** | Copia archivos o carpetas desde tu ordenador al interior de la imagen. | `COPY requirements.txt .` |
| **`RUN`** | Ejecuta comandos durante la **construcción** de la imagen (instalar paquetes). | `RUN pip install -r requirements.txt` |
| **`ENV`** | Define variables de entorno dentro del contenedor. | `ENV PYTHONUNBUFFERED=1` |
| **`EXPOSE`** | Documenta qué puerto escucha la aplicación dentro del contenedor. | `EXPOSE 80` |
| **`CMD`** | Define el comando por defecto que se ejecuta cuando **arranca** el contenedor. | `CMD ["python", "app.py"]` |

### Ejemplo práctico de `Dockerfile`
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends tcpdump iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "plc_server.py"]
```

---

## 4. Redes y Puertos en Docker

Por defecto, los contenedores viven aislados. Para comunicarlos con el exterior o entre sí existen dos mecanismos:

### Mapeo de Puertos (`-p`)
Conecta un puerto de tu ordenador anfitrión (`host`) con un puerto interno del contenedor:
* **Sintaxis:** `-p <puerto_host>:<puerto_contenedor>`
* **Ejemplo:** `docker run -d -p 8080:80 nginx`
  * Si abres `http://localhost:8080` en tu navegador, Docker redirige la petición al puerto `80` del contenedor.

### Redes Virtuales (`Networks`)
Permiten conectar varios contenedores en una red privada aislada:
* **`bridge` (por defecto):** Crea una red virtual interna (ej. `172.28.0.0/24`). Los contenedores conectados a la misma red bridge pueden comunicarse usando directamente el **nombre del servicio** como si fuera un dominio (DNS interno automático).
* **`host`:** El contenedor comparte directamente la tarjeta de red de tu máquina sin aislamiento.
* **`none`:** Aísla completamente al contenedor sin acceso a ninguna red.

---

## 5. Persistencia de Datos (Volúmenes y Bind Mounts)

**Regla de oro:** Los datos creados dentro de un contenedor son **efímeros**. Si eliminas el contenedor (`docker rm`), los cambios realizados dentro de su sistema de archivos desaparecen.

Para guardar datos de forma permanente o compartir archivos con tu equipo:

1. **Bind Mounts (Montaje de carpetas locales):** Vincula una carpeta real de tu PC con una carpeta dentro del contenedor. Cualquier cambio se sincroniza en tiempo real en ambos sentidos.
   * *Ejemplo:* `-v ./captures:/captures` (lo que el contenedor guarde en `/captures` aparece al instante en tu carpeta local `./captures`).
2. **Volúmenes gestionados (`Volumes`):** Espacios administrados directamente por Docker en su directorio interno del sistema, ideales para bases de datos en producción.

---

## 6. Docker Compose: Orquestación Multicontenedor

Cuando una aplicación o laboratorio necesita varios contenedores trabajando juntos (por ejemplo: un servidor, una base de datos y un cliente), usar comandos `docker run` largos uno por uno es incómodo.

**Docker Compose** permite definir toda la infraestructura en un único archivo YAML llamado **`docker-compose.yml`** y levantarla o apagarla con un solo comando.

### Estructura básica de un `docker-compose.yml`
```yaml
name: mi-laboratorio

services:
  servidor:
    build: .
    container_name: nodo-servidor
    command: python server.py
    volumes:
      - ./:/app
    networks:
      red_interna:
        ipv4_address: 172.28.0.10

  cliente:
    build: .
    container_name: nodo-cliente
    command: python client.py --host servidor
    depends_on:
      - servidor
    networks:
      red_interna:
        ipv4_address: 172.28.0.11

networks:
  red_interna:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/24
```

---

## 7. Chuleta de Comandos Esenciales (Cheat Sheet)

### Gestión de Contenedores
```bash
docker ps                                  # Lista contenedores activos
docker ps -a                               # Lista TODOS los contenedores (activos y detenidos)
docker run -d --name web -p 8080:80 nginx  # Crea y arranca un contenedor en segundo plano (-d)
docker stop <nombre_o_id>                  # Detiene un contenedor de forma ordenada
docker start <nombre_o_id>                 # Vuelve a arrancar un contenedor detenido
docker restart <nombre_o_id>               # Reinicia un contenedor
docker rm -f <nombre_o_id>                 # Detiene y elimina un contenedor a la fuerza
```

### Inspección y Depuración (Dentro del contenedor)
```bash
docker exec -it <nombre> bash              # Abre una terminal interactiva dentro del contenedor
docker exec -it <nombre> sh                # Alternativa si la imagen es ligera (Alpine) y no tiene bash
docker logs <nombre>                       # Muestra la salida/errores del contenedor
docker logs -f <nombre>                    # Muestra los logs en tiempo real (Ctrl + C para salir)
docker inspect <nombre>                    # Muestra configuración detallada en JSON (IPs, rutas, etc.)
docker stats                               # Monitor en tiempo real de uso de CPU, RAM y red
```

### Gestión de Imágenes
```bash
docker images                              # Lista las imágenes guardadas en tu equipo
docker build -t mi-imagen:1.0 .            # Construye una imagen desde el Dockerfile local
docker pull ubuntu:22.04                   # Descarga una imagen de Docker Hub sin arrancarla
docker rmi <nombre_o_id>                   # Elimina una imagen del disco duro
```

### Comandos de Docker Compose
*(Ejecutar dentro de la carpeta donde reside `docker-compose.yml`)*
```bash
docker compose up -d                       # Levanta todos los servicios en segundo plano
docker compose up -d --build               # Reconstruye imágenes (si hubo cambios) y levanta todo
docker compose down                        # Detiene y elimina contenedores y redes del proyecto
docker compose ps                          # Muestra el estado de los servicios de este proyecto
docker compose logs -f                     # Sigue los logs de todos los servicios a la vez
docker compose exec <servicio> bash        # Entra en la terminal de un servicio concreto
```

### Limpieza y Mantenimiento del Sistema
```bash
docker network ls                          # Lista las redes virtuales creadas
docker volume ls                           # Lista los volúmenes de datos persistentes
docker system df                           # Muestra cuánto espacio en disco ocupa Docker
docker system prune                        # Elimina contenedores parados, redes sin uso e imágenes huérfanas
```

---

## 8. Consejos y Buenas Prácticas

* **Evita usar `sudo` cada vez (en Linux/WSL):** Añade tu usuario al grupo de Docker con `sudo usermod -aG docker $USER` y cierra y vuelve a abrir la terminal.
* **Usa imágenes ligeras:** Siempre que sea posible, elige etiquetas como `-slim` o `-alpine` (ej. `python:3.12-slim`) para reducir el tamaño de descarga y la superficie de ataque.
* **Usa `.dockerignore`:** Crea un archivo `.dockerignore` en tu proyecto para evitar copiar archivos innecesarios (como `.git`, carpetas temporales o entornos virtuales locales) dentro de la imagen.
* **No guardes contraseñas en el `Dockerfile`:** Utiliza archivos `.env` o variables de entorno pasadas en tiempo de ejecución.
* **Apaga tus laboratorios al terminar:** Usa `docker compose down` cuando acabes de trabajar para liberar memoria RAM y evitar procesos innecesarios en segundo plano.
