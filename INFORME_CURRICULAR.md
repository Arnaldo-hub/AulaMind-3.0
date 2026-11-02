# Informe de actualización curricular integral — AulaMind 3.0

**Fecha:** 3 de noviembre de 2026  
**Alcance:** programas oficiales entregados por el usuario, unidades, OA/AE y selector de objetivos de la pantalla `/mineduc`.

## Resultado

- **129 JSON curriculares actualizados:** 110 modificados y 19 nuevos.
- **518 unidades** y **2.669 apariciones de OA/AE** en el lote: 2.640 OA y 29 AE.
- La carpeta curricular pasa de **565 a 584 JSON**; los 19 adicionales son exactamente los nuevos respaldados.
- Se actualiza `templates/mineduc.html` para mostrar códigos en el selector y conservar la descripción completa en el valor seleccionado.
- **Total de archivos de aplicación entregados: 130.** No se modifican controladores, servicios Python, base de datos, usuarios, planes, variables de entorno ni otras plantillas.

## Correcciones principales

- Descripciones completas contrastadas con programas oficiales; se retiraron restos de encabezados, pies de página, indicadores, actitudes y duraciones ajenas identificados documentalmente.
- Se conservaron textos oficiales breves y variantes por unidad; no se seleccionaron textos por una regla automática de mayor o menor longitud.
- Inglés: reconstrucción de tablas anuales y variantes por unidad, incluidas las continuaciones omitidas en 6° básico OA 12.
- Ciencias Naturales 2° medio: 12 unidades según la organización principal por ejes y OA 1–18.
- Colla 6°: 14 OA, con distribución oficial **4/3/3/4**.
- Mapuzugun 7° y Quechua 8°: se conservan **AE**, con 16 y 13 objetivos respectivamente; se eliminaron metadatos heredados que duplicaban unidades vacías.
- Educación Física: catálogos oficiales integrados y 4° básico OA 10 completado con su continuación documental.
- Historia: correcciones puntuales en 3°–6° y numeración romana de 8°; se verificó nuevamente la distribución de 5°–8°.
- Matemática 7°/8°: fórmulas restauradas en OA 9 y OA 8 respectivamente.
- Aymara 2°, Mundo Global y Teatro: artefactos y truncamientos puntuales sustituidos por texto oficial completo.
- Ciencias para la Ciudadanía: se conservaron módulos y habilidades; solo se corrigió el OA documentado de Ambiente y Sostenibilidad.
- No se rellenaron electivos de profundización con documentos de Formación General ni se reutilizaron programas entre asignaturas, pueblos o niveles.

## Validaciones ejecutadas

| Validación | Resultado |
|---|---:|
| Sintaxis de los 584 JSON | 584 correctos; 11 inventarios son listas y 573 documentos son objetos |
| Escritura del lote | 129/129 idénticos al lote preparado |
| Metadatos, unidades, códigos y descripciones del lote | Sin campos vacíos ni códigos duplicados dentro de una unidad |
| Auditoría de contaminación y cierres incompletos | 0 errores en los 129 destinos |
| Distribuciones LCPOA contrastadas | 071, 103, 104, 105, 106, 119, 073 y 072 correctas |
| Carga con `CurriculumService` | 584 JSON, 573 documentos, 16 cursos, 719 unidades indexadas y 3.768 OA/AE únicos |
| Igualdad JSON ↔ servicio | 2.669/2.669 apariciones del lote verificadas, sin faltantes ni diferencias |
| Selector OA/AE | Código visible; descripción completa en `value` y `title`; prueba funcional correcta |
| Repositorio curricular de la app | Inicialización y estadísticas correctas |

El validador histórico incluido en el repositorio pasó de 541 a 560 documentos analizados, de 205 a 225 documentos `VALID` y de 37,89 % a 40,18 % de cobertura. Mantiene **0 `STRUCTURAL`** y **0 `SCHEMA_ERROR`**. Aún informa observaciones heredadas en documentos fuera del alcance documental —por ejemplo, Religion sin unidades, duplicados LCPOA por pueblo y esquemas antiguos—; no se alteraron sin fuentes ni se presentan como errores introducidos por este lote.

## Archivos nuevos (19)

- `aymara/lcpoa_aymara_4_basico.json`
- `colla/lcpoa_colla_6_basico.json`
- `educacion_fisica/educaci_n_f_sica_y_salud_2_3_medio.json`
- `educacion_fisica/educaci_n_f_sica_y_salud_2_4_medio.json`
- `historia_geografia_cs/hist_4_basico.json`
- `ingles/ingles_1_basico.json`
- `ingles/ingles_2_basico.json`
- `ingles/ingles_3_basico.json`
- `ingles/ingles_4_basico.json`
- `interculturalidad/lcpoa_interculturalidad_5_basico.json`
- `kawesqar/lcpoa_kawesqar_3_basico.json`
- `medio_hc/chile_y_la_region_latinoamericana_3_medio.json`
- `medio_hc/chile_y_la_region_latinoamericana_4_medio.json`
- `medio_hc/danza_3_medio.json`
- `medio_hc/danza_4_medio.json`
- `medio_hc/mundo_global_3_medio.json`
- `medio_hc/mundo_global_4_medio.json`
- `medio_hc/teatro_3_medio.json`
- `medio_hc/teatro_4_medio.json`

## Detalle de los 129 JSON

“Antes” y “después” indican unidades/apariciones de OA o AE. En los archivos nuevos no existe valor anterior.

| Estado | Archivo | Fuente oficial | Antes | Después |
|---|---|---|---:|---:|
| modificado | `artes_visuales/artes_1_basico.json` | Programa Artes Visuales.pdf | 4/5 | 4/19 |
| modificado | `artes_visuales/artes_1_medio.json` | Programa Artes Visuales(6).pdf | 4/19 | 4/14 |
| modificado | `artes_visuales/artes_2_basico.json` | Programa Artes Visuales(1).pdf | 4/5 | 4/17 |
| modificado | `artes_visuales/artes_2_medio.json` | Programa Artes Visuales(7).pdf | 4/13 | 4/11 |
| modificado | `artes_visuales/artes_3_basico.json` | Programa Artes Visuales(2).pdf | 4/5 | 4/17 |
| modificado | `artes_visuales/artes_4_basico.json` | Art. Visuales 4.pdf | 4/17 | 4/18 |
| modificado | `artes_visuales/artes_5_basico.json` | Programa de estudio Artes.pdf | 4/5 | 4/17 |
| modificado | `artes_visuales/artes_6_basico.json` | Programa Artes Visuales(3).pdf | 4/16 | 4/18 |
| modificado | `artes_visuales/artes_7_basico.json` | Programa Artes Visuales(4).pdf | 4/17 | 4/16 |
| modificado | `artes_visuales/artes_8_basico.json` | Programa Artes Visuales(5).pdf | 4/17 | 4/14 |
| modificado | `artes_visuales/artes_visuales_3_medio.json` | Artes Visuales 3° y 4°.pdf | 4/19 | 4/11 |
| modificado | `artes_visuales/artes_visuales_4_medio.json` | Artes Visuales 3° y 4°.pdf | 4/19 | 4/11 |
| modificado | `aymara/lcpoa_aymara_2_basico.json` | Programa Pueblos originarios.pdf | 4/17 | 4/27 |
| nuevo | `aymara/lcpoa_aymara_4_basico.json` | Propuesta Pueblos Originarios.pdf | — | 4/18 |
| modificado | `ciencias_naturales/ciencias_1_basico.json` | Programa Ciencias Naturales.pdf | 4/12 | 4/12 |
| modificado | `ciencias_naturales/ciencias_1_medio.json` | Programa Ciencias Naturales(8).pdf | 4/31 | 4/12 |
| modificado | `ciencias_naturales/ciencias_2_basico.json` | Programa Ciencias Naturales(1).pdf | 4/14 | 4/14 |
| modificado | `ciencias_naturales/ciencias_2_medio.json` | Ciencias Naturales.pdf | 11/18 | 12/18 |
| modificado | `ciencias_naturales/ciencias_3_basico.json` | Programa Ciencias Naturales(2).pdf | 4/13 | 4/13 |
| modificado | `ciencias_naturales/ciencias_4_basico.json` | Programa Ciencias Naturales(3).pdf | 4/17 | 4/17 |
| modificado | `ciencias_naturales/ciencias_5_basico.json` | Programa Ciencias Naturales(4).pdf | 4/14 | 4/14 |
| modificado | `ciencias_naturales/ciencias_6_bas.json` | Programa Ciencias Naturales(5).pdf | 4/18 | 4/18 |
| modificado | `ciencias_naturales/ciencias_7_bas.json` | Programa Ciencias Naturales(6).pdf | 4/47 | 4/15 |
| modificado | `ciencias_naturales/ciencias_8_basico.json` | Programa Ciencias Naturales(7).pdf | 4/15 | 4/15 |
| nuevo | `colla/lcpoa_colla_6_basico.json` | Programa Pueblos Originarios(2).pdf | — | 4/14 |
| modificado | `diaguita/lcpoa_diaguita_1_basico.json` | Programa Pueblos Originarios.pdf | 4/16 | 4/18 |
| nuevo | `educacion_fisica/educaci_n_f_sica_y_salud_2_3_medio.json` | Educación Física y Salud Electivo 3° y 4°.pdf | — | 4/8 |
| nuevo | `educacion_fisica/educaci_n_f_sica_y_salud_2_4_medio.json` | Educación Física y Salud Electivo 3° y 4°.pdf | — | 4/8 |
| modificado | `educacion_fisica/educaci_n_f_sica_y_salud_3_medio.json` | Ed Fisica y Salud 1- 3°4°M.pdf | 4/6 | 4/8 |
| modificado | `educacion_fisica/educaci_n_f_sica_y_salud_4_medio.json` | Ed Fisica y Salud 1- 3°4°M.pdf | 4/6 | 4/8 |
| modificado | `educacion_fisica/efi_1_basico.json` | Programa Educación Física y Salud.pdf | 4/11 | 4/14 |
| modificado | `educacion_fisica/efi_1_medio.json` | Educ. Física y Salud 1M.pdf | 4/8 | 4/5 |
| modificado | `educacion_fisica/efi_2_basico.json` | Educ. Física y Salud 2.pdf | 4/12 | 4/13 |
| modificado | `educacion_fisica/efi_2_medio.json` | Programa Ed. Física y salud.pdf | 4/5 | 4/5 |
| modificado | `educacion_fisica/efi_3_basico.json` | Educ. Física 3.pdf | 4/11 | 4/13 |
| modificado | `educacion_fisica/efi_4_basico.json` | Programa Educación Física y Salud(1).pdf | 4/11 | 4/13 |
| modificado | `educacion_fisica/efi_5_basico.json` | Programa de Ed. Física y salud.pdf | 4/11 | 4/12 |
| modificado | `educacion_fisica/efi_6_basico.json` | Programa de Educación Física y Salud.pdf | 4/11 | 4/12 |
| modificado | `educacion_fisica/efi_7_basico.json` | Programa Ed. Física y Salud.pdf | 4/7 | 4/6 |
| modificado | `educacion_fisica/efi_8_basico.json` | Programa Ed.Física y Salud.pdf | 4/8 | 4/6 |
| modificado | `historia_geografia_cs/hist_1_basico.json` | Programa Historia, Geografía.pdf | 4/32 | 4/23 |
| modificado | `historia_geografia_cs/hist_1_medio.json` | Programa  Historia 1° Medio.pdf | 4/25 | 4/20 |
| modificado | `historia_geografia_cs/hist_2_basico.json` | Programa Historia GCS.pdf | 4/12 | 4/22 |
| modificado | `historia_geografia_cs/hist_2_medio.json` | Programa Historia GCS 6 2M (Decreto).pdf | 4/15 | 4/19 |
| modificado | `historia_geografia_cs/hist_3_basico.json` | Programa Historia GCS 3.pdf | 4/13 | 4/28 |
| nuevo | `historia_geografia_cs/hist_4_basico.json` | Programa Historia GCS(1).pdf | — | 4/23 |
| modificado | `historia_geografia_cs/hist_5_basico.json` | Programa Historia.pdf | 4/26 | 4/23 |
| modificado | `historia_geografia_cs/hist_6_basico.json` | Programa de Historia, Geografía y Ciencias Sociales.pdf | 4/31 | 4/28 |
| modificado | `historia_geografia_cs/hist_8_basico.json` | Programa Historia GCS(3).pdf | 4/22 | 4/19 |
| modificado | `historia_geografia_cs/hist_bas.json` | Programa Historia GCS(2).pdf | 4/24 | 4/20 |
| nuevo | `ingles/ingles_1_basico.json` | Propuesta Curricular Inglés.pdf | — | 4/56 |
| modificado | `ingles/ingles_1medio.json` | Inglés 1M.pdf | 4/65 | 4/64 |
| nuevo | `ingles/ingles_2_basico.json` | Propuesta curricular Inglés 2° básico.pdf | — | 4/56 |
| modificado | `ingles/ingles_2medio.json` | Inglés 2M Modificado.pdf | 4/69 | 4/64 |
| nuevo | `ingles/ingles_3_basico.json` | Propuesta Inglés.pdf | — | 4/60 |
| nuevo | `ingles/ingles_4_basico.json` | Propuesta curricular Inglés 4° básico.pdf | — | 4/60 |
| modificado | `ingles/ingles_5_basico.json` | Programa Inglés (Propuesta).pdf | 4/64 | 4/60 |
| modificado | `ingles/ingles_6_basico.json` | Programa Inglés (formal).pdf | 4/64 | 4/64 |
| modificado | `ingles/ingles_7_basico.json` | Propuesta curricular Inglés.pdf | 4/45 | 4/52 |
| modificado | `ingles/ingles_8_basico.json` | Programa Propuesta Inglés.pdf | 4/42 | 4/52 |
| nuevo | `interculturalidad/lcpoa_interculturalidad_5_basico.json` | Programa INTERCULTURALIDAD_5ºBásico.pdf | — | 4/18 |
| nuevo | `kawesqar/lcpoa_kawesqar_3_basico.json` | Programa Pueblos Originarios(1).pdf | — | 4/14 |
| modificado | `lenguaje_literatura/leng_1_basico.json` | Programa Lenguaje y Comunicación.pdf | 4/44 | 4/35 |
| modificado | `lenguaje_literatura/leng_1_medio.json` | Programa lenguaje y Literatura.pdf | 4/31 | 4/31 |
| modificado | `lenguaje_literatura/leng_2_basico.json` | Programa Lenguaje.pdf | 4/47 | 4/32 |
| modificado | `lenguaje_literatura/leng_2_medio.json` | Programa lengua y Literatura.pdf | 4/42 | 4/42 |
| modificado | `lenguaje_literatura/leng_3_basico.json` | Lenguaje 3.pdf | 4/45 | 4/27 |
| modificado | `lenguaje_literatura/leng_4_basico.json` | Programa Lenguaje y Comunicación(1).pdf | 4/48 | 4/28 |
| modificado | `lenguaje_literatura/leng_5_basico.json` | Lenguaje 5.pdf | 4/47 | 4/25 |
| modificado | `lenguaje_literatura/leng_6_basico.json` | Programa Lenguaje y Comunicación(2).pdf | 4/50 | 4/28 |
| modificado | `lenguaje_literatura/leng_7_basico.json` | Programa lenguaje.pdf | 7/90 | 7/90 |
| modificado | `lenguaje_literatura/leng_8_basico.json` | Programa Lengua y Literatura.pdf | 7/98 | 7/98 |
| modificado | `matematica/mat_1_basico.json` | Programa Matemática.pdf | 4/36 | 4/28 |
| modificado | `matematica/mat_1_medio.json` | Programa Matemática(4).pdf | 4/19 | 4/15 |
| modificado | `matematica/mat_2_basico.json` | Programa Matemática(1).pdf | 4/36 | 4/29 |
| modificado | `matematica/mat_2_medio.json` | Matemática 2M.pdf | 4/15 | 4/12 |
| modificado | `matematica/mat_3_basico.json` | Matemática 3.pdf | 4/36 | 4/29 |
| modificado | `matematica/mat_4_basico.json` | Programa Matemática(2).pdf | 4/34 | 4/27 |
| modificado | `matematica/mat_5_basico.json` | Programa 5° matemática.pdf | 4/35 | 4/27 |
| modificado | `matematica/mat_6_basico.json` | Programa Matemáticas.pdf | 4/32 | 4/24 |
| modificado | `matematica/mat_7_basico.json` | Matemática 7.pdf | 4/21 | 4/19 |
| modificado | `matematica/mat_8_basico.json` | Programa Matemática(3).pdf | 4/20 | 4/17 |
| nuevo | `medio_hc/chile_y_la_region_latinoamericana_3_medio.json` | Programa Electivo Chile y Región Latinoamericana.pdf | — | 4/12 |
| nuevo | `medio_hc/chile_y_la_region_latinoamericana_4_medio.json` | Programa Electivo Chile y Región Latinoamericana.pdf | — | 4/12 |
| modificado | `medio_hc/ciencias_para_la_ciudadan_a_3_medio.json` | Ambiente y Sostenibilidad.pdf | 5/21 | 5/21 |
| modificado | `medio_hc/ciencias_para_la_ciudadan_a_4_medio.json` | Ambiente y Sostenibilidad.pdf | 5/21 | 5/21 |
| nuevo | `medio_hc/danza_3_medio.json` | Danza  3° y 4° Electivo.pdf | — | 4/11 |
| nuevo | `medio_hc/danza_4_medio.json` | Danza  3° y 4° Electivo.pdf | — | 4/11 |
| modificado | `medio_hc/educaci_n_ciudadana_3_medio.json` | Programa Educación Ciudadana 3°.pdf | 1/8 | 4/10 |
| modificado | `medio_hc/filosof_a_3_medio.json` | Programa Filosofía 3° y 4°.pdf | 5/16 | 2/10 |
| modificado | `medio_hc/filosof_a_4_medio.json` | Programa Filosofía 3° y 4°.pdf | 5/15 | 2/9 |
| nuevo | `medio_hc/mundo_global_3_medio.json` | Mundo global Electivo 3° y 4°.pdf | — | 4/11 |
| nuevo | `medio_hc/mundo_global_4_medio.json` | Mundo global Electivo 3° y 4°.pdf | — | 4/11 |
| nuevo | `medio_hc/teatro_3_medio.json` | Teatro 3° y 4° Electivo.pdf | — | 4/8 |
| nuevo | `medio_hc/teatro_4_medio.json` | Teatro 3° y 4° Electivo.pdf | — | 4/8 |
| modificado | `musica/m_sica_3_medio.json` | Música 3° y 4° Electivo.pdf | 4/21 | 4/14 |
| modificado | `musica/m_sica_4_medio.json` | Música 3° y 4° Electivo.pdf | 4/21 | 4/14 |
| modificado | `musica/musica_1_basico.json` | Programa Música.pdf | 4/6 | 4/23 |
| modificado | `musica/musica_1_medio.json` | Programa música.pdf | 4/23 | 4/17 |
| modificado | `musica/musica_2_basico.json` | Programa Música(1).pdf | 4/6 | 4/23 |
| modificado | `musica/musica_2_medio.json` | Programa Música(4).pdf | 4/20 | 4/18 |
| modificado | `musica/musica_3_basico.json` | Música 3.pdf | 4/23 | 4/23 |
| modificado | `musica/musica_4_basico.json` | Música 4.pdf | 4/8 | 4/22 |
| modificado | `musica/musica_5_basico.json` | Programa de Música.pdf | 4/8 | 4/21 |
| modificado | `musica/musica_6_basico.json` | Programa Música(2).pdf | 4/7 | 4/20 |
| modificado | `musica/musica_7_basico.json` | Programa Música(3).pdf | 4/23 | 4/18 |
| modificado | `musica/musica_8_basico.json` | Música 8.pdf | 4/23 | 4/18 |
| modificado | `orientacion/orient_1_medio.json` | Programa orientación.pdf | 4/10 | 5/10 |
| modificado | `orientacion/orient_2_bas.json` | Programa Orientación.pdf | 4/8 | 2/11 |
| modificado | `orientacion/orient_2_medio.json` | Programa orientación(1).pdf | 4/10 | 5/10 |
| modificado | `orientacion/orient_3_bas.json` | Programa Orientación(1).pdf | 4/8 | 2/12 |
| modificado | `orientacion/orient_4_bas.json` | Programa Orientación(2).pdf | 4/9 | 2/13 |
| modificado | `orientacion/orient_5_basi.json` | Programa de Orientación.pdf | 4/9 | 4/6 |
| modificado | `orientacion/orient_6_bas.json` | Programa Orientación(3).pdf | 4/9 | 4/6 |
| modificado | `orientacion/orient_7_bas.json` | Programa Orientación(4).pdf | 4/12 | 4/8 |
| modificado | `orientacion/orient_8_bas.json` | Programa Orientación(5).pdf | 4/13 | 4/8 |
| modificado | `orientacion/orientacion_1_bas.json` | Orientación 1.pdf | 4/8 | 2/11 |
| modificado | `pueblos-originarios/mapuzugun_programa_7_basico.json` | Programa lengua Indígena.pdf | 0/0 | 4/16 |
| modificado | `pueblos-originarios/programa_lengua_indigena_8_basico_-_lengua_indigena_quechua_0.json` | Programa Lengua Indígena 8° Básico - Lengua Indígena Quechua_0.pdf | 0/0 | 4/13 |
| modificado | `tecnologia/tecnol_1_basico.json` | Programa Tecnología.pdf | 4/11 | 4/10 |
| modificado | `tecnologia/tecnol_2_basico.json` | Programa Tecnología(1).pdf | 4/12 | 4/11 |
| modificado | `tecnologia/tecnol_2_medio.json` | Programa tecnología.pdf | 4/12 | 2/6 |
| modificado | `tecnologia/tecnol_4_basico.json` | Programa Tecnología(2).pdf | 4/15 | 4/11 |
| modificado | `tecnologia/tecnol_5_basico.json` | Programa Tecnología(3).pdf | 4/14 | 4/11 |
| modificado | `tecnologia/tecnol_7_basico.json` | Programa Tecnología(4).pdf | 4/6 | 4/17 |
| modificado | `tecnologia/tecnol_8_basico.json` | Programa Tecnología(5).pdf | 4/6 | 4/18 |
| modificado | `tecnologia/tecnologia_1medio.json` | Tecnología 1M.pdf | 4/14 | 2/6 |
| modificado | `tecnologia/tecnologia_3_basico.json` | Tecnología 3.pdf | 4/13 | 4/11 |
| modificado | `tecnologia/tecnologia_6_basico.json` | Tecnología 6.pdf | 4/13 | 4/11 |

## Revisión y despliegue

La entrega está preparada para revisión local y posterior carga a GitHub. **No se ha modificado GitHub, Render ni producción desde esta fase.** Después de copiar los archivos y revisar la app, el usuario puede confirmar el commit y desplegar el commit correspondiente en Render.

Las instrucciones operativas y los casos de revisión visual están en `LEEME.txt`.
