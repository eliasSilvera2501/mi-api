# PokeApp — Pokédex Web

Proyecto final de Aplicaciones de Internet Ricas (RIA) 2026 — Grupo 7

Una Pokédex web desarrollada con Angular 21 que permite explorar Pokémon, armar tu equipo, guardar favoritos y gestionar tu perfil de usuario.

---

## Integrantes

| Nombre | Cédula |
|---|---|
| Facundo Navarro | 5.453.703-9 |
| Gerardo Navarro | 5.453.380-1 |
| Mariano Ramos | 4.334.927-5 |
| Francisco Blazevic | 4.691.399-8 |
| Elías Silvera | 5.311.325-4 |

---

## ¿Qué hace la app?

- Explorar más de 1000 Pokémon con paginación, búsqueda y filtros por tipo
- Ver el detalle de cada Pokémon: estadísticas, habilidades, imagen shiny y gráfico radar
- Reproducir el sonido (cry) de cada Pokémon
- Guardar Pokémon como favoritos y armar un equipo de hasta 6
- Editar el perfil de usuario (nombre y ciudad)
- Modo oscuro activable desde cualquier pantalla
- Panel de administración para usuarios con rol admin

---

## Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Angular | 21.2.0 | Framework principal (SPA, rutas, guards, formularios) |
| TypeScript | 5.9.2 | Lenguaje base del proyecto |
| Bootstrap + SCSS | 5.3.8 | Estilos, grillas y componentes visuales |
| Animate.css | 4.1.1 | Animaciones de entrada en tarjetas y páginas |
| SweetAlert2 | 11.26.25 | Popups de confirmación y errores |
| Chart.js | 4.5.1 | Gráfico radar con las estadísticas del Pokémon |
| PokéAPI v2 | pública | Fuente de todos los datos de Pokémon |
| LocalStorage | Web API | Favoritos, equipo y preferencias del usuario |
| Keycloak JS | 26.2.4 | Autenticación, tokens JWT y roles |

---

## Correr el proyecto en local

**Requisitos previos:**
- Node.js (compatible con Angular 21)
- npm (el proyecto fue desarrollado con npm 11.13.0)
- Conexión a internet (se consume PokéAPI y Keycloak en tiempo real)

**Pasos:**

```bash
# 1. Clonar el repositorio
git clone https://github.com/RamosMariano/pokedex-app.git
cd pokedex-app

# 2. Instalar dependencias
npm install

# 3. Levantar el servidor de desarrollo
npm start
```

La app queda disponible en `http://localhost:4200`

---

## Compilar y desplegar

### Compilación

Para generar el build de producción se ejecuta:

```bash
ng build
```

Los archivos compilados quedan en `dist/pokedex-app/browser/`. Este comando empaqueta toda la app en archivos estáticos (HTML, CSS, JS) que no necesitan Node ni Angular para funcionar.

El proyecto tiene los límites de bundle ajustados en `angular.json` para evitar errores de compilación dado el tamaño de las dependencias (Keycloak, Chart.js, SweetAlert2, etc.):

```json
"budgets": [
  { "type": "initial", "maximumWarning": "2mb", "maximumError": "4mb" },
  { "type": "anyComponentStyle", "maximumWarning": "4kB", "maximumError": "8kB" }
]
```

Si aparecen warnings amarillos durante el build, no impiden el despliegue.

### Despliegue en Netlify

La app está desplegada en **Netlify**, una plataforma de hosting gratuita para sitios estáticos. Se eligió por ser gratuita, no requerir configuración de servidor y permitir despliegue manual arrastrando una carpeta.

**URL de la app:** https://pokedex-grupo7.netlify.app

**Pasos para redesplegar:**

1. Ejecutar `ng build` para generar la carpeta `dist/pokedex-app/browser/`

2. Crear un archivo llamado `_redirects` (sin extensión) dentro de `dist/pokedex-app/browser/` con el siguiente contenido:
```
/*    /index.html    200
```
Este archivo es necesario para que Netlify redirija todas las rutas al `index.html` y Angular pueda manejarlas. Sin él, al ingresar directamente a cualquier ruta como `/home` o `/detail/1` aparece un error 404.

3. Ingresar a [netlify.com](https://netlify.com), ir al proyecto **pokedex-grupo7** y arrastrar la carpeta `dist/pokedex-app/browser/` a la zona de despliegue del dashboard.

---

## Rutas de la aplicación

| Ruta | Acceso | Descripción |
|---|---|---|
| `/home` | Público | Pokédex principal |
| `/detail/:id` | Público | Detalle de un Pokémon |
| `/login` | Público | Inicio de sesión |
| `/register` | Público | Registro (redirige a Keycloak) |
| `/favorites` | Requiere sesión | Favoritos del usuario |
| `/myteam` | Requiere sesión | Equipo del usuario |
| `/profile` | Requiere sesión | Perfil del usuario |
| `/resources` | Requiere sesión | Referencias y librerías |
| `/admin` | Solo administradores | Panel de administración |

Las rutas protegidas usan `authGuard` (verifica token en LocalStorage) y `adminGuard` (verifica rol admin).

---

## Persistencia de datos

Como la app no tiene backend propio, los datos de cada usuario se guardan en el LocalStorage del navegador:

| Clave | Contenido |
|---|---|
| `kc_token` | Token JWT de la sesión activa |
| `kc_refresh_token` | Refresh token de Keycloak |
| `kc_user` | Datos del usuario (username, rol, nombre visible, ciudad) |
| `pokemonFavoritos_{username}` | Lista de favoritos del usuario |
| `pokeweb_equipo_{username}` | Equipo del usuario (máx. 6) |
| `pokeweb_tema` | Preferencia de modo oscuro |

---

## API utilizada

**PokéAPI v2** — `https://pokeapi.co/api/v2/`

API pública y gratuita, no requiere registro ni API key.

Endpoints usados:
- `/pokemon?limit=1025` — listado completo
- `/pokemon/{id}` — datos de detalle
- `/pokemon-species/{id}` — datos de especie
- `/type/{tipo}` — filtro por tipo elemental

Documentación oficial: https://pokeapi.co/docs/v2

---

## Autenticación

El login y registro se manejan a través de un servidor **Keycloak** alojado en `auth.fabriq.uy`. La app nunca almacena contraseñas: Keycloak valida las credenciales y devuelve un token JWT firmado. Los roles (usuario / admin) también vienen dentro del token.

Documentación oficial: https://www.keycloak.org/documentation

---

## Capturas de pantalla

| | |
|---|---|
| ![Login](capturas/login.png) | ![Registro](capturas/registro.png) |
| Login | Registro |
| ![Home](capturas/home.png) | ![Detalle](capturas/detalle.png) |
| Pokédex principal | Detalle del Pokémon |
| ![Favoritos](capturas/favoritos.png) | ![Perfil](capturas/perfil.png) |
| Favoritos | Perfil de usuario |

---

## Repositorio

[github.com/RamosMariano/pokedex-app](https://github.com/RamosMariano/pokedex-app)

Docente: José Luis Brito Rodríguez  
Entrega: 26 de junio de 2026 — `jose.brito@utec.edu.uy`
