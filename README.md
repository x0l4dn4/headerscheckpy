Script en Python que realiza dos funciones:

1. Consulta una URL y comprueba la presencia de cabeceras de seguridad HTTP.
2. Levanta un servidor HTTP local que registra el encabezado `User-Agent` de cada peticion recibida.

Los resultados del analisis se guardan en `security_headers.json` y las peticiones capturadas en `user_agents.jsonl`.

## Requisitos

- Python 3.8 o superior.
- No requiere librerias externas: usa solo la libreria estandar de Python.

## Uso basico

```bash
python3 headers.py https://example.com --port 8080
```

El script:

1. Hace una peticion HTTPS a `https://example.com`.
2. Comprueba cabeceras como `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, entre otras.
3. Guarda el informe en `security_headers.json`.
4. Inicia un servidor HTTP en el puerto `8080`.
5. Registra cada peticion entrante en `user_agents.jsonl`.

## Sintaxis

```bash
python3 headers.py [URL] [--host HOST] [--port PUERTO] [--timeout SEGUNDOS]
```

### Argumentos

| Argumento | Valor por defecto | Descripcion |
|---|---:|---|
| `URL` | `https://example.com` | Sitio web cuya cabecera de seguridad se analizara |
| `--host` | `0.0.0.0` | Interfaz de red donde escucha el servidor |
| `--port` | `8080` | Puerto TCP del servidor HTTP |
| `--timeout` | `10` | Tiempo maximo, en segundos, para la peticion de analisis |

## Ejemplos

### Analizar example.com y levantar el servidor en el puerto 8080

```bash
python3 headers.py https://example.com --port 8080
```

### Analizar otro sitio web

```bash
python3 headers.py https://www.mozilla.org --port 8080
```

### Usar otro puerto

```bash
python3 headers.py https://example.com --port 9000
```

El servidor quedara disponible en:

```text
http://localhost:9000
```

### Escuchar solo en localhost

Por seguridad, si solo quieres probarlo en tu propio equipo:

```bash
python3 headers.py https://example.com --host 127.0.0.1 --port 8080
```

### Aumentar el timeout

Util si la web tarda en responder:

```bash
python3 headers.py https://example.com --timeout 20
```

### Probar la captura de User-Agent con curl

Con el servidor en ejecucion, abre otra terminal y ejecuta:

```bash
curl -A "Mozilla/5.0 (TestAgent)" http://localhost:8080/prueba
```

Tambien puedes probar con una peticion POST:

```bash
curl -X POST -A "MiAgenteDePruebas/1.0" http://localhost:8080/formulario
```

O abrir en el navegador:

```text
http://localhost:8080/
```

Cada peticion quedara registrada en `user_agents.jsonl`.

## Archivos generados

### security_headers.json

Contiene el resultado del analisis de la URL indicada.

Ejemplo simplificado:

```json
{
  "url": "https://example.com/",
  "status": 200,
  "checked_at": "2026-10-14T18:53:00+00:00",
  "headers": {
    "Content-Security-Policy": null,
    "Strict-Transport-Security": null,
    "X-Content-Type-Options": null,
    "X-Frame-Options": null,
    "Referrer-Policy": null,
    "Permissions-Policy": null,
    "Cross-Origin-Opener-Policy": null,
    "Cross-Origin-Resource-Policy": null,
    "Cross-Origin-Embedder-Policy": null
  }
}
```

Un valor `null` significa que la cabecera no fue devuelta por el servidor analizado.

### user_agents.jsonl

Contiene una linea JSON por cada peticion recibida por el servidor local.

Ejemplo:

```json
{"time": "2026-10-14T18:53:10+00:00", "method": "GET", "path": "/prueba", "client": "127.0.0.1", "user_agent": "Mozilla/5.0 (TestAgent)", "headers": {"Host": "localhost:8080", "User-Agent": "Mozilla/5.0 (TestAgent)", "Accept": "*/*"}}
```

## Cabeceras comprobadas

| Cabecera | Funcion principal |
|---|---|
| `Content-Security-Policy` | Reduce el riesgo de XSS y controla los recursos que puede cargar la pagina |
| `Strict-Transport-Security` | Obliga al navegador a usar HTTPS |
| `X-Content-Type-Options` | Evita el sniffing de tipos MIME |
| `X-Frame-Options` | Ayuda a prevenir clickjacking mediante iframes |
| `Referrer-Policy` | Controla la informacion de referencia enviada a otros sitios |
| `Permissions-Policy` | Restringe APIs del navegador como camara, microfono o geolocalizacion |
| `Cross-Origin-Opener-Policy` | Aisla el contexto de navegacion entre ventanas |
| `Cross-Origin-Resource-Policy` | Controla quien puede incrustar los recursos del sitio |
| `Cross-Origin-Embedder-Policy` | Aisla documentos embebidos de origen cruzado |

## Detener el servidor

Pulsa:

```text
Ctrl + C
```

El script mostrara:

```text
[*] Servidor detenido
```

## Solucion de problemas

### `Address already in use`

El puerto esta ocupado. Usa otro:

```bash
python3 headers.py https://example.com --port 9000
```

Tambien puedes comprobar que proceso usa el puerto:

```bash
sudo ss -ltnp | grep 8080
```

### `No se pudo analizar https://...`

Puede deberse a:

- Falta de conexion a Internet.
- Certificado TLS invalido.
- DNS que no resuelve el dominio.
- Firewall o proxy bloqueando la peticion.
- Timeout insuficiente.

Prueba con otro sitio o aumenta el timeout:

```bash
python3 headers.py https://example.com --timeout 30
```

### No puedo acceder desde otro dispositivo

Comprueba que:

- El servidor esta escuchando en `0.0.0.0`.
- Usas la IP local del equipo, por ejemplo `http://192.168.1.50:8080`.
- El firewall permite conexiones entrantes al puerto elegido.
