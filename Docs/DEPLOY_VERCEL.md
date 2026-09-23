# Guía Operativa: Despliegue de Frontend Angular en Vercel

Esta guía detalla el procedimiento paso a paso para desplegar la aplicación web (**CodeLab Stock**) desarrollada en **Angular 19/21** en la plataforma **Vercel** con certificado HTTPS automático y red de entrega de contenido (CDN) global.

---

## 📋 Requisitos Previos

1. Cuenta registrada en [Vercel](https://vercel.com/) (recomendado vincular con la cuenta de GitHub).
2. Backend Django desplegado y operativo en Alwaysdata según [Docs/DEPLOY_ALWAYSDATA.md](DEPLOY_ALWAYSDATA.md).
3. Acceso al repositorio del proyecto: `https://github.com/ISPC-WEB-2025/CodeLab.git`.

---

## 🚀 Paso 1: Importar el Repositorio en Vercel

1. Ingresá a tu panel de control en [Vercel Dashboard](https://vercel.com/dashboard).
2. Hacé clic en el botón **"Add New..."** (arriba a la derecha) y seleccioná **"Project"**.
3. En la lista de repositorios de GitHub, buscá `CodeLab` (o `TodoStock`) y hacé clic en **Import**.

---

## ⚙️ Paso 2: Configuración del Proyecto (Monorepo)

En la pantalla **"Configure Project"**, completá los siguientes campos:

### A. Root Directory (Paso Crítico)
Dado que el repositorio contiene tanto `Backend/` como `Frontend/`, debemos indicarle a Vercel la subcarpeta exacta:
* Junto a **Root Directory**, hacé clic en **Edit**.
* Seleccioná la carpeta:
  ```text
  Frontend/app-stock
  ```
* Hacé clic en **Continue**.

### B. Build and Output Settings
Vercel detectará automáticamente el preset de Angular. Verificá que los valores coincidan:
* **Framework Preset:** `Angular`
* **Build Command:** `npm run build` (o `ng build`)
* **Output Directory:** `dist/app-stock/browser`
* **Install Command:** `npm install`

---

## 🌐 Paso 3: Enrutamiento SPA y Archivo `vercel.json`

El repositorio ya incluye en `Frontend/app-stock/vercel.json` la regla de reescritura necesaria:

```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**¿Por qué es indispensable?**  
Al ser una *Single Page Application* (SPA), las rutas directas como `/dashboard`, `/login` o `/vendedor` son gestionadas por el enrutador en el navegador. Esta directiva garantiza que al recargar la página (F5) o ingresar mediante un enlace directo, Vercel no devuelva un error HTTP 404 y sirva siempre el archivo `/index.html`.

---

## 🔗 Paso 4: Desplegar y Probar

1. Hacé clic en el botón azul **"Deploy"**.
2. Vercel ejecutará la compilación de producción (`npm run build`) y en aproximadamente 1 minuto la aplicación estará en línea.
3. Al finalizar, Vercel te asignará una URL pública con HTTPS automático (ej: `https://codelab-stock.vercel.app`).
4. Abrí el enlace y realizá las siguientes comprobaciones:
   * **Navegación:** Ingresá a `/login`, recargá el navegador y confirmá que no aparezca error 404.
   * **Conectividad:** Iniciá sesión con el usuario administrador para comprobar la comunicación con la API de Alwaysdata.

---

## 🔄 Despliegues Automáticos (CI/CD)

Vercel queda vinculado directamente con GitHub:
* Cada vez que se realice un merge a la rama `develop` o `main`, Vercel detectará el cambio y desplegará automáticamente la nueva versión en segundos.
