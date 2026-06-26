# PokeApp — Pokédex Web

Proyecto final de Aplicaciones de Internet Ricas (RIA) 2026 — Grupo 7

Es una Pokédex web hecha con Angular donde se puede explorar Pokémon, armar un equipo, guardar favoritos y manejar el perfil de usuario.

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

- Permite explorar más de 1000 Pokémon, con búsqueda, paginación y filtros por tipo
- Muestra el detalle de cada Pokémon: sus stats, habilidades, su versión shiny y un gráfico con sus estadísticas
- Reproduce el sonido (cry) de cada Pokémon
- Permite guardar Pokémon como favoritos y armar un equipo de hasta 6
- Permite editar el perfil de usuario (nombre y ciudad)
- Tiene un modo oscuro que se puede activar desde cualquier pantalla
- Cuenta con un panel de administración para los usuarios con rol admin

---

## Con qué está hecho

| Tecnología | Versión | Para qué se usa |
|---|---|---|
| Angular | 21.2.0 | Es el framework principal de la app (páginas, rutas, formularios, etc.) |
| TypeScript | 5.9.2 | El lenguaje en el que está escrito el código |
| Bootstrap + SCSS | 5.3.8 | Para los estilos y que todo se vea ordenado |
| Animate.css | 4.1.1 | Para las animaciones cuando aparecen las tarjetas y páginas |
| SweetAlert2 | 11.26.25 | Para los popups de confirmación y de error |
| Chart.js | 4.5.1 | Para el gráfico con las estadísticas de cada Pokémon |
| PokéAPI v2 | pública | De ahí se obtiene toda la información de los Pokémon |
| LocalStorage | — | Ahí se guardan los favoritos, el equipo y las preferencias del usuario |
| Keycloak JS | 26.2.4 | Se encarga del login, los tokens y los roles de usuario |

---

## Cómo correrlo en local

**Requisitos previos:**
- Tener Node.js instalado (compatible con Angular 21)
- Tener npm (se desarrolló con la versión 11.13.0)
- Conexión a internet, porque la app consulta la PokéAPI y Keycloak constantemente

**Pasos:**

```bash
# 1. Clonar el repositorio
git clone https://github.com/RamosMariano/pokedex-app.git
cd pokedex-app

# 2. Instalar las dependencias
npm install

# 3. Levantar el servidor
npm start
```

La app queda disponible en `http://localhost:4200`

---

## Compilar y desplegar

### Compilación

Para generar la versión final (la que se sube a un servidor) se ejecuta:

```bash
ng build
```

Esto deja todos los archivos listos en `dist/pokedex-app/browser/`. Básicamente junta todo en archivos de HTML, CSS y JS que ya no necesitan Node ni Angular para funcionar, y se pueden alojar en cualquier servidor.

En el archivo `angular.json` se tuvieron que subir un poco los límites de tamaño permitido, porque con todas las librerías que se usan (Keycloak, Chart.js, SweetAlert2, etc.) la app pesa más de lo que Angular deja pasar por defecto:

```json
"budgets": [
  { "type": "initial", "maximumWarning": "2mb", "maximumError": "4mb" },
  { "type": "anyComponentStyle", "maximumWarning": "4kB", "maximumError": "8kB" }
]
```

Si al compilar aparecen warnings en amarillo no hay problema, no impiden que la app se pueda desplegar.

### Despliegue

Para llenar

**URL de la app:** Para llenar

**Pasos para volver a desplegar:**

Para llenar

---

## Rutas de la aplicación

| Ruta | Acceso | Descripción |
|---|---|---|
| `/home` | Público | La Pokédex principal |
| `/detail/:id` | Público | El detalle de un Pokémon |
| `/login` | Público | Inicio de sesión |
| `/register` | Público | Registro (redirige a Keycloak) |
| `/favorites` | Requiere sesión | Los favoritos del usuario |
| `/myteam` | Requiere sesión | El equipo del usuario |
| `/profile` | Requiere sesión | El perfil del usuario |
| `/resources` | Requiere sesión | Referencias y librerías usadas |
| `/admin` | Solo administradores | El panel de administración |

Las rutas protegidas usan un guard que revisa si hay un token guardado, y la ruta de admin además revisa que el usuario tenga el rol correspondiente.

---

## Dónde se guardan los datos

Como la app no tiene un backend propio, los datos de cada usuario se guardan en el LocalStorage del navegador:

| Clave | Contenido |
|---|---|
| `kc_token` | El token de la sesión activa |
| `kc_refresh_token` | El token para renovar la sesión |
| `kc_user` | Los datos del usuario (nombre de usuario, rol, nombre visible, ciudad) |
| `pokemonFavoritos_{username}` | La lista de favoritos del usuario |
| `pokeweb_equipo_{username}` | El equipo del usuario (hasta 6 Pokémon) |
| `pokeweb_tema` | Si tiene activado el modo oscuro o no |

---

## API utilizada

**PokéAPI v2** — `https://pokeapi.co/api/v2/`

Es una API pública y gratuita, no hace falta registrarse ni tener una API key.

Endpoints usados:
- `/pokemon?limit=1025` — para el listado completo
- `/pokemon/{id}` — para los datos de detalle
- `/pokemon-species/{id}` — para los datos de la especie
- `/type/{tipo}` — para filtrar por tipo

Documentación oficial: https://pokeapi.co/docs/v2

---

## Autenticación

El login y el registro se manejan con un servidor de **Keycloak** alojado en `auth.fabriq.uy`. La app nunca guarda contraseñas: Keycloak se encarga de validar las credenciales y devuelve un token firmado. Ahí mismo viene también el rol del usuario (si es admin o no).

Documentación oficial: https://www.keycloak.org/documentation

---

## Repositorio

[github.com/RamosMariano/pokedex-app](https://github.com/RamosMariano/pokedex-app)

Docente: José Luis Brito Rodríguez  
Entrega: 26 de junio de 2026 — `jose.brito@utec.edu.uy`
