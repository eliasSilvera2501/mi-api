# Taller Java — Iteración 1
## Sistema de Gestión de Movilidad Eléctrica

---

## Introducción

Sistema de gestión de movilidad eléctrica desarrollado con Jakarta EE 10, JPA/Hibernate y MariaDB.
Permite gestionar clientes, estaciones de carga, cargas de vehículos eléctricos y pagos,
siguiendo una arquitectura modular con bajo acoplamiento entre módulos.

---

## Decisiones de diseño

- **Modularización**: el sistema se divide en tres módulos principales — Clientes, Cargas y Pagos.
  Cada módulo es una separación lógica independiente dentro de la aplicación.

- **Bajo acoplamiento entre módulos**: los módulos se comunican exclusivamente mediante eventos CDI.
  Ningún módulo importa clases de dominio de otro módulo.
  Cada módulo tiene sus propias clases de dominio y su propio conjunto de tablas en la base de datos.

- **Separación en capas**: cada módulo sigue una arquitectura limpia con capas bien definidas —
  dominio, aplicación, interfaz e infraestructura.

- **Priorización de lógica de negocio**: la capa de dominio es el centro de la arquitectura.
  No conoce ninguna capa externa — ni eventos, ni HTTP, ni base de datos.
  Solo contiene reglas de negocio.

- **Persistencia**: MariaDB con JPA/Hibernate. Cada módulo gestiona sus propias tablas.

- **Inyección de dependencias**: CDI (Contexts and Dependency Injection) de Jakarta EE.
  El contenedor resuelve las dependencias en tiempo de ejecución.

---

## Arquitectura general

```mermaid
graph TD
    AppMovil["📱 App Móvil"]
    GestorWeb["🖥️ Gestor Web"]
    Cargador["⚡ Cargador Físico"]

    subgraph Sistema
        subgraph ModuloClientes["Módulo Clientes"]
            ClienteAPI["ClienteAPI (REST)"]
            ServicioClientes["ServicioClientesImpl"]
            DominioClientes["Dominio\nCliente / MedioPago / Reclamo"]
            DBClientes[("MariaDB\nclientes\nmedios_pago\nreclamos")]
        end

        subgraph ModuloCargas["Módulo Cargas"]
            CargaAPI["CargaAPI (REST)"]
            ServicioCargas["ServicioCargaImpl"]
            DominioCargas["Dominio\nCarga / Cargador / EstacionCarga"]
            DBCargas[("MariaDB\ncargas\ncargadores\nestaciones_carga\ncargas_clientes")]
        end

        subgraph ModuloPagos["Módulo Pagos"]
            PagoAPI["PagoAPI (REST)"]
            ServicioPagos["ServicioPagoImpl"]
            DominioPagos["Dominio\nPago / ClientePago / MedioPagoPago"]
            DBPagos[("MariaDB\npagos\npagos_clientes\npagos_medios_pago")]
        end
    end

    AppMovil --> ClienteAPI
    AppMovil --> CargaAPI
    GestorWeb --> ClienteAPI
    GestorWeb --> CargaAPI
    Cargador --> CargaAPI
    GestorWeb --> PagoAPI

    ClienteAPI --> ServicioClientes
    ServicioClientes --> DominioClientes
    DominioClientes --> DBClientes

    CargaAPI --> ServicioCargas
    ServicioCargas --> DominioCargas
    DominioCargas --> DBCargas

    PagoAPI --> ServicioPagos
    ServicioPagos --> DominioPagos
    DominioPagos --> DBPagos
```

---

## Comunicación entre módulos — Eventos CDI

Los módulos no se llaman directamente. Se comunican mediante eventos CDI.
Cada módulo guarda una copia local de los datos que necesita de otros módulos.

```mermaid
sequenceDiagram
    participant AppMovil as  App Móvil
    participant Clientes as Módulo Clientes
    participant Cargas as Módulo Cargas
    participant Pagos as Módulo Pagos

    AppMovil->>Clientes: POST /clientes/registrar
    Clientes->>Clientes: guarda Cliente en BD
    Clientes-->>Cargas:  ClienteRegistradoEvent
    Clientes-->>Pagos:  ClienteRegistradoEvent
    Cargas->>Cargas: guarda ClienteCarga local
    Pagos->>Pagos: guarda ClientePago local

    AppMovil->>Clientes: POST /clientes/{cedula}/medioPago
    Clientes->>Clientes: guarda MedioPago en BD
    Clientes-->>Pagos:  MedioPagoAgregadoEvent
    Pagos->>Pagos: guarda MedioPagoPago local

    
```

---


## Módulo Clientes

### Modelo de dominio

```mermaid
classDiagram
    class Cliente {
        <<abstract>>
        -String cedula
        -String nombreCompleto
        -String telefono
        -String contrasena
        +agregarMedioPago(MedioPago)
        +obtenerMedioPagoPredeterminado() MedioPago
        +aplicarDescuento(double) double
    }

    class ClienteComun {
        +aplicarDescuento(double) double
    }

    class ClienteProfesional {
        -TipoProfesional tipoProfesional
        -double porcentajeDescuento
        +aplicarDescuento(double) double
    }

    class TipoProfesional {
        <<enum>>
        TAXI
        UBER
        CABIFY
    }

    class MedioPago {
        <<abstract>>
        -Long id
        -boolean predeterminado
        +describir() String
    }

    class Tarjeta {
        -String numero
        -String titular
        -LocalDate fechaVencimiento
        -String digitoVerificacion
        -TipoTarjeta tipoTarjeta
        +estaVigente() boolean
        +ultimosCuatroDigitos() String
    }

    class CuentaUTE {
        -String numeroCuenta
    }

    class TipoTarjeta {
        <<enum>>
        VISA
        MASTERCARD
        OCA
        AMEX
    }

    class Reclamo {
        -Long id
        -String comentario
        -LocalDateTime fecha
        -String cedulaCliente
    }

    Cliente <|-- ClienteComun
    Cliente <|-- ClienteProfesional
    ClienteProfesional --> TipoProfesional
    Cliente "1" --> "0..*" MedioPago
    MedioPago <|-- Tarjeta
    MedioPago <|-- CuentaUTE
    Tarjeta --> TipoTarjeta
```

### Casos de uso

| Caso de uso | Consumidor | Descripción |
|-------------|------------|-------------|
| `registrarCliente` | App móvil | Registra un nuevo cliente. Hashea la contraseña con BCrypt. Dispara `ClienteRegistradoEvent` |
| `altaMedioPago` | App móvil | Agrega un medio de pago al cliente. El primero queda como predeterminado. Dispara `MedioPagoAgregadoEvent` |
| `obtenerClientes` | Gestor web | Devuelve todos los clientes registrados |
| `realizarReclamo` | App móvil | Registra un reclamo del cliente con comentario y fecha |

### Cómo se resolvieron

**registrarCliente**
- La API recibe un `ClienteDTO` con los datos del cliente y el tipo (COMUN o PROFESIONAL)
- El DTO es responsable de decidir qué subclase de `Cliente` construir con `build()` — 
  si el tipo es PROFESIONAL crea un `ClienteProfesional` con su porcentaje de descuento,
  si es COMUN crea un `ClienteComun`. Esta lógica vive en el DTO y no contamina el servicio.
- El servicio valida que la cédula no esté ya registrada antes de persistir — 
  si existe lanza `IllegalStateException` y la API devuelve `409 CONFLICT`
- La contraseña se hashea con BCrypt antes de guardar — 
  nunca se almacena en texto plano en la base de datos
- Al finalizar se dispara `ClienteRegistradoEvent` con primitivos (cedula, nombre, tipo) —
  sin objetos de dominio — para que Cargas y Pagos guarden su copia local del cliente

**altaMedioPago**
- La API recibe un `MedioPagoDTO` con el tipo (TARJETA o UTE) y sus datos
- El DTO construye la subclase correcta con `build()` — `Tarjeta` o `CuentaUTE`
- La lógica de predeterminado vive en el dominio — `Cliente.agregarMedioPago()` 
  marca automáticamente el primer medio de pago como predeterminado sin que el 
  servicio ni la API intervengan
- Por seguridad, en la respuesta el número de tarjeta nunca se expone completo —
  `MedioPagoDTO.desde()` enmascara el número mostrando solo los últimos 4 dígitos
  usando `tarjeta.ultimosCuatroDigitos()`
- El dígito de verificación nunca se devuelve en ninguna respuesta
- Se dispara `MedioPagoAgregadoEvent` con el id técnico del medio de pago —
  nunca con el número de tarjeta — para que Pagos guarde su copia local

**obtenerClientes**
- Consumido por el gestor web para administración del sistema
- El servicio devuelve objetos de dominio `Cliente` pero la API los convierte 
  a `ClienteDTO` antes de responder — así la contraseña hasheada nunca sale 
  en la respuesta HTTP aunque esté en el objeto de dominio
- La conversión se hace con `ClienteDTO.desde(cliente)` que excluye 
  explícitamente el campo contraseña

**realizarReclamo**
- El cliente envía únicamente un comentario de texto libre
- La fecha y hora las asigna el sistema automáticamente en el constructor 
  de `Reclamo` con `LocalDateTime.now()` — el cliente no puede manipularla
- El reclamo se asocia al cliente por cédula
- El servicio verifica que el cliente existe antes de registrar el reclamo —
  si no existe devuelve `400 BAD REQUEST`

### Eventos que produce

```mermaid
graph LR
    ServicioClientes["ServicioClientesImpl"]

    ServicioClientes -->|"dispara"| E1["🔔 ClienteRegistradoEvent\ncedula, nombre, tipo"]
    ServicioClientes -->|"dispara"| E2["🔔 MedioPagoAgregadoEvent\ncedulaCliente, idMedioPago\ntipoMedioPago, predeterminado"]

    E1 -->|"@Observes"| OC["ObserverClienteRegistrado\n(ModuloCargas)\n→ guarda ClienteCarga"]
    E1 -->|"@Observes"| OP["ObserverClienteRegistrado\n(ModuloPagos)\n→ guarda ClientePago"]
    E2 -->|"@Observes"| OM["ObserverMedioPagoAgregado\n(ModuloPagos)\n→ guarda MedioPagoPago"]
```

### Endpoints REST

| Método | URL | Body | Respuesta |
|--------|-----|------|-----------|
| `POST` | `/api/clientes/registrar` | `ClienteDTO` | `201` id del cliente |
| `POST` | `/api/clientes/{cedula}/medioPago` | `MedioPagoDTO` | `200` ok |
| `GET` | `/api/clientes` | — | `200` lista de clientes |
| `POST` | `/api/clientes/{cedula}/reclamos` | String comentario | `201` id del reclamo |

### Ejemplos curl

**Registrar cliente común:**
```bash
curl -X POST http://localhost:8080/TallerJavaEquipo6/api/clientes/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "cedula": "12345678",
    "nombreCompleto": "Juan Perez",
    "telefono": "099123456",
    "contrasena": "clave123",
    "tipo": "COMUN"
  }'
```

**Registrar cliente profesional:**
```bash
curl -X POST http://localhost:8080/TallerJavaEquipo6/api/clientes/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "cedula": "98765432",
    "nombreCompleto": "Maria Garcia",
    "telefono": "098456789",
    "contrasena": "clave456",
    "tipo": "PROFESIONAL",
    "tipoProfesional": "TAXI",
    "porcentajeDescuento": 15.0
  }'
```

**Agregar tarjeta:**
```bash
curl -X POST http://localhost:8080/TallerJavaEquipo6/api/clientes/12345678/medioPago \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "TARJETA",
    "numero": "4111111111111111",
    "titular": "Juan Perez",
    "fechaVencimiento": "2027-12-01",
    "digitoVerificacion": "123",
    "tipoTarjeta": "VISA"
  }'
```

**Agregar cuenta UTE:**
```bash
curl -X POST http://localhost:8080/TallerJavaEquipo6/api/clientes/12345678/medioPago \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "UTE",
    "numeroCuenta": "UTE-987654"
  }'
```

**Realizar reclamo:**
```bash
curl -X POST http://localhost:8080/TallerJavaEquipo6/api/clientes/12345678/reclamos \
  -H "Content-Type: application/json" \
  -d '"El cargador no funciona"'
```

**Obtener todos los clientes:**
```bash
curl http://localhost:8080/TallerJavaEquipo6/api/clientes
```

---



## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Jakarta EE | 10 | Plataforma base |
| WildFly | 27 | Servidor de aplicaciones |
| JPA / Hibernate | 6 | Persistencia |
| MariaDB | — | Base de datos |
| CDI | 4 | Inyección de dependencias y eventos |
| JAX-RS | 3.1 | API REST |
| BCrypt | — | Hash de contraseñas |
| JUnit | 5 | Tests |

---

## Cómo ejecutar

```bash
# Levantar el servidor en modo desarrollo
mvn clean package wildfly:dev

# El servidor queda disponible en
http://localhost:8080/TallerJavaEquipo6
```

