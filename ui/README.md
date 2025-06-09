# MacSnap UI Components

Esta carpeta contiene la interfaz de usuario modular de MacSnap, organizada en componentes independientes y reutilizables.

## 📁 Estructura de Archivos

```
ui/
├── __init__.py          # Exportaciones principales
├── styles.py            # Estilos globales y de layout
├── category_list.py     # Lista de categorías + estilos específicos
├── item_list.py         # Lista de items + estilos específicos
├── item_detail.py       # Panel de detalles + estilos específicos
├── action_buttons.py    # Botones de acción + estilos específicos
├── layout.py           # Layout principal y MacSnapApp
└── README.md           # Esta documentación
```

## 🎨 Distribución de Estilos CSS

### Estilos Globales (`styles.py`)

- Tema Tokyo Night base
- Layout de Screen y contenedores principales
- Header y Footer
- Modales y DataTable (compatibilidad)

### Estilos por Componente

Cada componente tiene su propio `DEFAULT_CSS` con estilos específicos:

#### `CategoryList` (`category_list.py`)

- Estilos de ListView para categorías
- Highlighting y hover states
- Sidebar container (`#category-sidebar`)

#### `ItemButtonList` (`item_list.py`)

- ListView para items con iconos
- Estados de selección y status
- Container de tabla (`#item-table`)
- Colores de status (installed, failed, etc.)

#### `ItemDetailPanel` (`item_detail.py`)

- Panel de detalles con texto enriquecido
- Container (`#item-detail`)
- Clases para nombre, status y descripción

#### `ActionButtons` (`action_buttons.py`)

- Panel de control (`#control-panel`)
- Container horizontal (`#action-buttons`)
- Estilos de botones (primary, error, default)
- Estados hover y focus

## 🔧 Ventajas de la Separación

### ✅ **Modularidad**

- Cada componente es completamente independiente
- CSS específico está junto al código del componente
- Fácil mantenimiento y debugging

### ✅ **Reutilización**

- Componentes pueden usarse en otras aplicaciones
- Estilos no se filtran entre componentes
- Configuración independiente

### ✅ **Escalabilidad**

- Agregar nuevos componentes es trivial
- Modificar estilos no afecta otros componentes
- Testing individual por componente

### ✅ **Claridad**

- CSS específico fácil de encontrar
- Estilos globales claramente separados
- Documentación embebida en el código

## 🚀 Uso

### Importar Componentes

```python
from ui import CategoryList, ItemButtonList, ItemDetailPanel, ActionButtons
```

### Usar en App Principal

```python
from ui.layout import MacSnapApp, run_macsnap_ui

# Ejecutar aplicación
run_macsnap_ui(verbose=True)
```

### Crear Nuevos Componentes

1. Crear archivo en `ui/`
2. Definir clase con `DEFAULT_CSS`
3. Exportar en `__init__.py`
4. Usar en `layout.py`

## 🎯 Arquitectura de Mensajes

Los componentes se comunican usando mensajes de Textual:

- `CategorySelected`: Categoría seleccionada
- `ItemSelected`: Item seleccionado/enfocado
- `ItemToggled`: Item seleccionado/deseleccionado
- `FocusItemTable`: Enfocar tabla de items
- `FocusCategoryList`: Enfocar lista de categorías

## 💡 Mejores Prácticas

1. **Estilos específicos**: Siempre usar `DEFAULT_CSS` en componentes
2. **IDs únicos**: Usar selectores de ID para containers específicos
3. **Clases descriptivas**: Nombres de clase claros y específicos
4. **Colores consistentes**: Usar paleta Tokyo Night
5. **Responsive**: Usar unidades `fr` y porcentajes
