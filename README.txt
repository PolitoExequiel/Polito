DUX TICKET - PELLEGRINI v0.2 (58 mm)
===================================
Configuración: Windows 10/11 x64, Chrome, USB, Hasar 181 (modelo por verificar), 58 mm, 1 copia.
Objetivo final: impresión automática al abrir el PDF de egreso de Dux.

ESTADO DE ESTA VERSIÓN
- Prototipo MANUAL: abre un PDF de egreso, lee datos, muestra ticket y envía a la impresora de Windows sin diálogo.
- Bloquea envíos duplicados por huella del PDF y exige confirmación para reimprimir.
- NO detecta todavía la apertura de una pestaña PDF en Chrome.
- NO es instalador EXE ni fue probado físicamente en la Hasar.
- La compatibilidad del driver con 58 mm debe verificarse.

INSTALACIÓN EN WINDOWS 10/11 x64
1. Descomprimir ZIP.
2. Instalar Python 3.11 o 3.12 x64 (con Tkinter).
3. Abrir CMD en la carpeta descomprimida.
4. Ejecutar: py -m pip install -r requirements.txt
5. Ejecutar: py app.py
6. Abrir PDF de Dux, elegir impresora y probar.

SEGURIDAD
- No modifica Dux ni envía información a servidores.
- Enviado a cola de Windows no significa impreso físicamente.
- El PDF de ejemplo disponible es de Lisandro, no Pellegrini.
- No inventa destinatario ni identificador ausentes en el PDF.
- Para la captura automática desde Chrome hay que verificar el URL real del PDF y su acceso.
