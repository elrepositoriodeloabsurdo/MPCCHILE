# 🚀 VibeCodingChile MCP en Vercel

Tu repositorio está **listo para desplegar en Vercel**. Aquí está todo lo que necesitas:

## ✅ Qué hemos hecho

### 1. **API REST Completa** (`/pages/api/`)
- ✨ `/api/search` - Buscar conceptos por término
- ✨ `/api/concept` - Obtener detalle de un concepto
- ✨ `/api/stats` - Estadísticas de la ontología
- ✨ `/api/branches` - Listar ramas de la taxonomía
- ✨ `/api/health` - Health check

### 2. **Interfaz Web Interactiva** (`/pages/index.tsx`)
- 🎨 Diseño responsivo y moderno
- 🔍 Búsqueda en tiempo real
- 📋 Panel de detalle de conceptos
- 📊 Estadísticas integradas
- 🔗 Enlaces a endpoints API

### 3. **Configuración Vercel Optimizada**
- `vercel.json` - Config de framework y funciones serverless
- `.vercelignore` - Excluye archivos Python innecesarios
- `next.config.js` - Optimizaciones para Vercel
- `package.json` - Dependencias limpias (solo Next + React)

### 4. **Exclusiones Automáticas**
- ❌ Python (server.py, data_loader.py) no se sube a Vercel
- ❌ Dependencias PyPI no se instalan
- ✅ Solo JavaScript/Node.js

## 🚀 Cómo desplegar

### **Opción 1: Dashboard de Vercel (Recomendado)**

1. Ve a https://vercel.com
2. Click en **"Add New"** → **"Project"**
3. Selecciona **"Import Git Repository"**
4. Elige este repositorio (`elrepositoriodeloabsurdo/MPCCHILE`)
5. Vercel detectará Next.js automáticamente
6. Click en **"Deploy"**

### **Opción 2: CLI de Vercel**

```bash
npm install -g vercel
vercel --prod
```

### **Opción 3: GitHub Auto-Deploy**

1. Conecta el repo a Vercel desde el dashboard
2. Cada push a `main` se deployará automáticamente

## 🎯 Resultados después del deploy

Tu aplicación estará disponible en:
```
https://<tu-dominio>.vercel.app/
```

Y los endpoints API en:
```
https://<tu-dominio>.vercel.app/api/search?q=base+de+licitud
https://<tu-dominio>.vercel.app/api/concept?id=base_licitud
https://<tu-dominio>.vercel.app/api/stats
https://<tu-dominio>.vercel.app/api/branches
https://<tu-dominio>.vercel.app/api/health
```

## 🧪 Probar localmente antes de desplegar

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Abrir http://localhost:3000
```

## 📡 Usar la API programáticamente

```javascript
// Buscar conceptos
const res = await fetch('https://<tu-dominio>.vercel.app/api/search?q=riesgo');
const data = await res.json();
console.log(data.results);

// Obtener concepto específico
const res2 = await fetch('https://<tu-dominio>.vercel.app/api/concept?id=base_licitud');
const concept = await res2.json();
console.log(concept);
```

## 🐛 Si algo sale mal

**Error: "Build failed"**
- Verifica que `ontology.json` y `relations.json` existan en la raíz
- Revisa los logs en Vercel Dashboard

**Error: "Cannot find module 'ontology.json'"**
- Asegúrate que los archivos JSON están en `/` (raíz del repo)
- Limpia `.next` y vuelve a buildear: `rm -rf .next && npm run build`

**CORS error**
- Headers CORS están configurados en todos los endpoints
- Verifica que el endpoint está siendo llamado correctamente

## 📚 Estructura del proyecto

```
MPCCHILE/
├── pages/
│   ├── api/
│   │   ├── search.js        # 🔍 Búsqueda de conceptos
│   │   ├── concept.js       # 📋 Detalle de concepto
│   │   ├── stats.js         # 📊 Estadísticas
│   │   ├── branches.js      # 🌳 Ramas
│   │   └── health.js        # ❤️ Health check
│   └── index.tsx            # 🎨 UI Principal
├── styles/
│   └── globals.css          # 🎨 Estilos globales
├── public/                  # 📁 Assets estáticos
├── ontology.json            # 📖 Datos de ontología
├── relations.json           # 🔗 Relaciones
├── package.json             # 📦 Dependencias
├── next.config.js           # ⚙️ Config Next.js
├── vercel.json              # 🚀 Config Vercel
├── .vercelignore            # 🚫 Excluir de Vercel
└── README.md                # 📖 Esta documentación
```

## 🔄 Variables de ambiente (si las necesitas)

Puedes configurar en Vercel Dashboard → Project Settings → Environment Variables:

```
# Ejemplo (opcional)
NEXT_PUBLIC_API_URL=https://<tu-dominio>.vercel.app
```

## 💡 Tips

- La ontología (JSON) se carga al iniciar el servidor
- No hay base de datos ni llamadas externas, todo es en memoria
- Escalable globalmente gracias a Vercel
- Puedes integrar esta API en cualquier app (React, Vue, Python, etc.)

## 🎓 Próximos pasos (opcionales)

1. **Agregar autenticación** si quieres limitar acceso
2. **Caché de Vercel** para mejorar rendimiento
3. **Webhooks** para sincronizar cambios en la ontología
4. **Base de datos** para persistencia (si necesitas guardar logs de búsquedas)

---

**¡Tu repositorio está 100% listo para Vercel! 🎉**

Cualquier duda, revisa la [documentación de Vercel](https://vercel.com/docs) o el [README original del MCP](./README.md).
