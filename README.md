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
    participant AppMovil as 📱 App Móvil
    participant Clientes as Módulo Clientes
    participant Cargas as Módulo Cargas
    participant Pagos as Módulo Pagos

    AppMovil->>Clientes: POST /clientes/registrar
    Clientes->>Clientes: guarda Cliente en BD
    Clientes-->>Cargas: 🔔 ClienteRegistradoEvent
    Clientes-->>Pagos: 🔔 ClienteRegistradoEvent
    Cargas->>Cargas: guarda ClienteCarga local
    Pagos->>Pagos: guarda ClientePago local

    AppMovil->>Clientes: POST /clientes/{cedula}/medioPago
    Clientes->>Clientes: guarda MedioPago en BD
    Clientes-->>Pagos: 🔔 MedioPagoAgregadoEvent
    Pagos->>Pagos: guarda MedioPagoPago local

    AppMovil->>Cargas: POST /cargas/iniciar
    Cargas->>Cargas: verifica ClienteCarga local
    Cargas->>Cargas: ocupa Cargador
    Cargas->>Cargas: crea Carga ACTIVA

    Note over AppMovil,Cargas: el cliente carga su vehículo...

    AppMovil->>Cargas: POST /cargas/finalizar
    Cargas->>Cargas: finaliza Carga, calcula importe
    Cargas->>Cargas: libera Cargador
    Cargas-->>Pagos: 🔔 EventoCargaFinalizada
    Pagos->>Pagos: busca ClientePago local
    Pagos->>Pagos: busca MedioPagoPago local
    Pagos->>Pagos: cobra con TarjetaMock o FacturaUTEMock
    Pagos->>Pagos: guarda Pago EXITOSO o FALLIDO
```

---

## Estructura de paquetes

```mermaid
graph TD
    src["src/main/java/org/tallerjava"]

    src --> MC["ModuloCliente/"]
    src --> MCA["ModuloCarga/"]
    src --> MP["ModuloPago/"]
    src --> INF["infraestructura/\nconfiguracion/\nApplicationConfig.java"]

    MC --> MC_AP["aplicacion/\nServicioClientes.java\nimpl/ServicioClientesImpl.java"]
    MC --> MC_DO["dominio/\nCliente.java\nClienteComun.java\nClienteProfesional.java\nMedioPago.java\nTarjeta.java\nCuentaUTE.java\nReclamo.java\nrepositorios/"]
    MC --> MC_IN["infraestructura/\npersistencia/\nClienteRepositorioImpl.java"]
    MC --> MC_IF["Interface/\nevento/out/\nClienteRegistradoEvent.java\nPublicadorEventoCliente.java\nMedioPagoAgregadoEvent.java\nPublicadorEventoMedioPago.java\nremota/rest/\nClienteAPI.java\ndto/\nlocal/\nInterfaceLocalCliente.java"]

    MCA --> MCA_AP["aplicacion/\nServicioCarga.java\nimpl/ServicioCargaImpl.java"]
    MCA --> MCA_DO["dominio/\nCarga.java\nCargador.java\nEstacionCarga.java\nClienteCarga.java\nrepositorios/"]
    MCA --> MCA_IN["infraestructura/\npersistencia/\nCargaRepositorioImpl.java\nCargadorRepositorioImpl.java\nEstacionRepositorioImpl.java\nClienteCargaRepositorioImpl.java"]
    MCA --> MCA_IF["Interface/\nevento/in/\nObserverClienteRegistrado.java\nevento/out/\nEventoCargaFinalizada.java\nPublicadorEventoCarga.java\nremota/rest/\nCargaAPI.java\ndto/\nlocal/\nInterfaceLocalCarga.java"]

    MP --> MP_AP["aplicacion/\nServicioPago.java\nimpl/ServicioPagoImpl.java"]
    MP --> MP_DO["dominio/\nPago.java\nEstadoPago.java\nClientePago.java\nMedioPagoPago.java\nrepositorios/"]
    MP --> MP_IN["infraestructura/\npersistencia/\nPagoRepositorioImpl.java\nClientePagoRepositorioImpl.java\nMedioPagoPagoRepositorioImpl.java\nexternos/\nTarjetaMock.java\nFacturaUTEMock.java"]
    MP --> MP_IF["Interface/\nevento/in/\nObserverClienteRegistrado.java\nObserverMedioPagoAgregado.java\nObserverCargaFinalizada.java\nremota/rest/\nPagoAPI.java\ndto/\nlocal/\nInterfaceLocalPago.java"]
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

## Tablas en base de datos — Módulo Clientes

```mermaid
erDiagram
    clientes {
        string cedula PK
        string nombre_completo
        string telefono
        string contrasena
        string tipo_cliente
        string tipo_profesional
        double porcentaje_descuento
    }

    medios_pago {
        long id PK
        string tipo_medio_pago
        boolean predeterminado
        string cedula_cliente FK
        string numero
        string titular
        date fecha_vencimiento
        string digito_verificacion
        string tipo_tarjeta
        string numero_cuenta
    }

    reclamos {
        long id PK
        string comentario
        datetime fecha
        string cedula_cliente FK
    }

    clientes ||--o{ medios_pago : "tiene"
    clientes ||--o{ reclamos : "realiza"
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

