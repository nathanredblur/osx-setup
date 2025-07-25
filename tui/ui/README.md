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

### Tema Nativo Tokyo Night

- Usa `self.theme = "tokyo-night"` en lugar de CSS personalizado
- Textual maneja automáticamente colores, tipografía y efectos
- Solo se definen estilos estructurales necesarios

### Estilos Globales (`styles.py`)

- Solo layout y estructura
- Sin colores (manejados por el tema)

### Estilos por Componente

Cada componente tiene su propio `DEFAULT_CSS` solo con estructura:

#### `CategoryList` (`category_list.py`)

- Estructura de ListView para categorías
- Layout y dimensiones
- Sidebar container (`#category-sidebar`)

#### `ItemButtonList` (`item_list.py`)

- Estructura de ListView para items
- Layout y espaciado
- Container de tabla (`#item-table`)

#### `ItemDetailPanel` (`item_detail.py`)

- Estructura del panel de detalles
- Container (`#item-detail`)
- Layout de contenido

#### `ActionButtons` (`action_buttons.py`)

- Estructura del panel de control (`#control-panel`)
- Layout horizontal (`#action-buttons`)
- Dimensiones de botones

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

1. **Tema nativo**: Usar `self.theme = "tokyo-night"` para colores automáticos
2. **Solo estructura**: Definir únicamente layout en `DEFAULT_CSS`
3. **IDs únicos**: Usar selectores de ID para containers específicos
4. **Clases descriptivas**: Nombres de clase claros y específicos
5. **Responsive**: Usar unidades `fr` y porcentajes
