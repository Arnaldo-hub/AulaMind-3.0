/*
==========================================================
AulaMind Enterprise 3.0
Planning Engine V2
Parte 1 de 8
==========================================================
*/

"use strict";

/*=========================================================
CONFIGURACIÓN
=========================================================*/

const API = {

    courses: "/planning/api/curriculum/courses",

    subjects: "/planning/api/curriculum/subjects",

    units: "/planning/api/curriculum/units",

    objectives: "/planning/api/curriculum/objectives",

    generate: "/planning/generate"

};

/*=========================================================
ESTADO GLOBAL
=========================================================*/

const State = {

    courses: [],

    subjects: [],

    units: [],

    objectives: [],

    initialized: false

};

/*=========================================================
REFERENCIAS DOM
=========================================================*/

const DOM = {

    form: null,

    course: null,

    subject: null,

    unit: null,

    objectives: null,

    result: null,

    tema: null,

    duracion: null,

    tipo: null,

    recursos: null,

    observaciones: null,

    loader: null,

    toast: null,

    btnGenerar: null,

    btnLimpiar: null,

    btnCopiar: null,

    btnWord: null,

    btnPDF: null

};

/*=========================================================
INICIALIZACIÓN
=========================================================*/

async function initializePlanning(){

    console.clear();

    console.log("======================================");
    console.log("AulaMind Enterprise 3.0");
    console.log("Planning Engine V2");
    console.log("Inicializando...");
    console.log("======================================");

    bindDOM();

    validateDOM();

    registerEvents();

    await loadCourses();

    State.initialized = true;

    console.log("Planning Engine listo.");

}

/*=========================================================
DOM READY
=========================================================*/

if(document.readyState==="loading"){

    document.addEventListener("DOMContentLoaded",initializePlanning);

}else{

    initializePlanning();

}

/*=========================================================
REFERENCIAS DOM
=========================================================*/

function bindDOM(){

    DOM.form=document.getElementById("planningForm");

    DOM.course=document.getElementById("course");

    DOM.subject=document.getElementById("subject");

    DOM.unit=document.getElementById("unit");

    DOM.objectives=document.getElementById("learningObjectives");

    DOM.result=document.getElementById("resultado");

    DOM.tema=document.getElementById("tema");

    DOM.duracion=document.getElementById("duracion");

    DOM.tipo=document.getElementById("tipo");

    DOM.recursos=document.getElementById("recursos");

    DOM.observaciones=document.getElementById("observaciones");

    DOM.loader=document.getElementById("loader");

    DOM.toast=document.getElementById("toast");

    DOM.btnGenerar=document.getElementById("btnGenerar");

    DOM.btnLimpiar=document.getElementById("btnLimpiar");

    DOM.btnCopiar=document.getElementById("btnCopiar");

    DOM.btnWord=document.getElementById("btnWord");

    DOM.btnPDF=document.getElementById("btnPDF");

}

/*=========================================================
VALIDACIÓN DOM
=========================================================*/

function validateDOM(){

    const required=[

        "form",
        "course",
        "subject",
        "unit",
        "objectives",
        "result"

    ];

    for(const key of required){

        if(!DOM[key]){

            throw new Error("No existe elemento DOM: "+key);

        }

    }

}

/*=========================================================
FETCH JSON
=========================================================*/

async function fetchJSON(url){

    const response=await fetch(url,{

        credentials:"same-origin",

        headers:{
            "Accept":"application/json"
        }

    });

    if(!response.ok){

        throw new Error("HTTP "+response.status);

    }

    return await response.json();

}

/*=========================================================
UTILIDADES
=========================================================*/

function option(value,text){

    const o=document.createElement("option");

    o.value=value;

    o.textContent=text;

    return o;

}

function clearSelect(select,label){

    select.innerHTML="";

    select.appendChild(option("",label));

}

function enable(select){

    select.disabled=false;

}

function disable(select){

    select.disabled=true;

}

function toast(message,error=false){

    if(!DOM.toast){

        console.log(message);

        return;

    }

    DOM.toast.innerHTML=message;

    DOM.toast.className=error
        ? "toast error show"
        : "toast success show";

    setTimeout(()=>{

        DOM.toast.classList.remove("show");

    },3000);

}

function loader(show){

    if(!DOM.loader) return;

    DOM.loader.style.display=show
        ? "flex"
        : "none";

}

/*=========================================================
ORDEN CURRICULAR
=========================================================*/

function normalize(value){

    return String(value??"").trim();

}

function orderCourse(name){

    const txt=name.toLowerCase();

    const n=parseInt(txt.match(/\d+/)?.[0]||99);

    if(txt.includes("bás")||txt.includes("bas"))
        return n;

    if(txt.includes("medio"))
        return 8+n;

    return 99;

}

function sortCourses(list){

    return [...new Set(list)]

        .map(normalize)

        .filter(Boolean)

        .sort((a,b)=>{

            const oa=orderCourse(a);

            const ob=orderCourse(b);

            if(oa!==ob)
                return oa-ob;

            return a.localeCompare(

                b,

                "es",

                {

                    numeric:true,

                    sensitivity:"base"

                }

            );

        });

}

/*=========================================================
FIN PARTE 1
=========================================================*/
/*=========================================================
CARGAR CURSOS
=========================================================*/

async function loadCourses(){

    try{

        disable(DOM.course);

        clearSelect(
            DOM.course,
            "Cargando cursos..."
        );

        clearSelect(
            DOM.subject,
            "Seleccione un curso..."
        );

        clearSelect(
            DOM.unit,
            "Seleccione una asignatura..."
        );

        disable(DOM.subject);
        disable(DOM.unit);

        State.courses=[];

        const json=await fetchJSON(API.courses);

        if(!json.success){

            throw new Error(
                json.message ||
                json.error ||
                "No fue posible obtener los cursos."
            );

        }

        State.courses=sortCourses(json.courses||[]);

        clearSelect(
            DOM.course,
            "Seleccione un curso..."
        );

        State.courses.forEach(course=>{

            DOM.course.appendChild(
                option(course,course)
            );

        });

        enable(DOM.course);

        console.log(
            "Cursos:",
            State.courses
        );

    }
    catch(error){

        console.error(error);

        clearSelect(
            DOM.course,
            "Error cargando cursos"
        );

        toast(
            "Error cargando cursos",
            true
        );

    }

}

/*=========================================================
CARGAR ASIGNATURAS
=========================================================*/

async function loadSubjects(course){

    try{

        disable(DOM.subject);
        disable(DOM.unit);

        clearSelect(
            DOM.subject,
            "Cargando asignaturas..."
        );

        clearSelect(
            DOM.unit,
            "Seleccione una asignatura..."
        );

        clearObjectives();

        State.subjects=[];

        const json=await fetchJSON(

            API.subjects+
            "/"+
            encodeURIComponent(course)

        );

        if(!json.success){

            throw new Error(
                json.message ||
                json.error ||
                "Sin asignaturas."
            );

        }

        State.subjects=(json.subjects||[])
            .sort((a,b)=>

                a.localeCompare(

                    b,

                    "es",

                    {
                        numeric:true,
                        sensitivity:"base"
                    }

                )

            );

        clearSelect(

            DOM.subject,

            "Seleccione una asignatura..."

        );

        State.subjects.forEach(subject=>{

            DOM.subject.appendChild(

                option(subject,subject)

            );

        });

        enable(DOM.subject);

        console.log(
            "Asignaturas:",
            State.subjects
        );

    }
    catch(error){

        console.error(error);

        clearSelect(
            DOM.subject,
            "Sin asignaturas"
        );

        disable(DOM.subject);

        toast(
            "No fue posible cargar las asignaturas.",
            true
        );

    }

}

/*=========================================================
CARGAR UNIDADES
=========================================================*/

async function loadUnits(course,subject){

    try{

        disable(DOM.unit);

        clearSelect(

            DOM.unit,

            "Cargando unidades..."

        );

        clearObjectives();

        State.units=[];

        const json=await fetchJSON(

            API.units+
            "/"+
            encodeURIComponent(course)+
            "/"+
            encodeURIComponent(subject)

        );

        if(!json.success){

            throw new Error(

                json.message ||

                json.error ||

                "Sin unidades."

            );

        }

        State.units=(json.units||[])
            .sort((a,b)=>

                a.localeCompare(

                    b,

                    "es",

                    {
                        numeric:true,
                        sensitivity:"base"
                    }

                )

            );

        clearSelect(

            DOM.unit,

            "Seleccione una unidad..."

        );

        State.units.forEach(unit=>{

            DOM.unit.appendChild(

                option(unit,unit)

            );

        });

        enable(DOM.unit);

        console.log(
            "Unidades:",
            State.units
        );

    }
    catch(error){

        console.error(error);

        clearSelect(
            DOM.unit,
            "Sin unidades"
        );

        disable(DOM.unit);

        toast(
            "No fue posible cargar las unidades.",
            true
        );

    }

}

/*=========================================================
LIMPIAR PANEL OA
=========================================================*/

function clearObjectives(){

    State.objectives=[];

    DOM.objectives.innerHTML=`

        <div class="empty-state">

            <i class="fa-solid fa-book-open-reader"></i>

            <h4>
                Currículum Nacional
            </h4>

            <p>

                Seleccione una unidad para visualizar
                los Objetivos de Aprendizaje.

            </p>

        </div>

    `;

}

/*=========================================================
EVENTO CAMBIO CURSO
=========================================================*/

DOM.course.addEventListener(

    "change",

    async()=>{

        const course=DOM.course.value;

        clearSelect(
            DOM.subject,
            "Seleccione una asignatura..."
        );

        clearSelect(
            DOM.unit,
            "Seleccione una unidad..."
        );

        disable(DOM.subject);
        disable(DOM.unit);

        clearObjectives();

        if(!course){

            return;

        }

        await loadSubjects(course);

    }

);

/*=========================================================
EVENTO CAMBIO ASIGNATURA
=========================================================*/

DOM.subject.addEventListener(

    "change",

    async()=>{

        const course=DOM.course.value;

        const subject=DOM.subject.value;

        clearSelect(
            DOM.unit,
            "Seleccione una unidad..."
        );

        disable(DOM.unit);

        clearObjectives();

        if(!course || !subject){

            return;

        }

        await loadUnits(

            course,

            subject

        );

    }

);

/*=========================================================
FIN PARTE 2
PARTE 3:
- loadObjectives()
- renderObjectives()
- checkboxes OA
- selección múltiple
=========================================================*/
/*=========================================================
CARGAR OBJETIVOS DE APRENDIZAJE
=========================================================*/

async function loadObjectives(course,subject,unit){

    try{

        State.objectives=[];

        DOM.objectives.innerHTML=`

            <div class="empty-state">

                <i class="fa-solid fa-spinner fa-spin"></i>

                <h4>Cargando Objetivos de Aprendizaje...</h4>

            </div>

        `;

        const json=await fetchJSON(

            API.objectives+
            "/"+
            encodeURIComponent(course)+
            "/"+
            encodeURIComponent(subject)+
            "/"+
            encodeURIComponent(unit)

        );

        if(!json.success){

            throw new Error(

                json.message ||

                json.error ||

                "No existen objetivos."

            );

        }

        State.objectives=

            normalizeObjectives(json);

        renderObjectives();

        console.log(

            "Objetivos:",

            State.objectives

        );

    }
    catch(error){

        console.error(error);

        clearObjectives();

        toast(

            "No fue posible cargar los Objetivos.",

            true

        );

    }

}

/*=========================================================
NORMALIZAR RESPUESTA API
=========================================================*/

function normalizeObjectives(json){

    if(Array.isArray(json.objectives))
        return json.objectives;

    if(Array.isArray(json.objetivos))
        return json.objetivos;

    if(Array.isArray(json.data))
        return json.data;

    return [];

}

/*=========================================================
CÓDIGO OA
=========================================================*/

function getObjectiveCode(oa,index){

    if(typeof oa==="string"){

        const match=

            oa.match(/OA\s*\d+/i);

        return match
            ? match[0].toUpperCase()
            : "OA "+(index+1);

    }

    return String(

        oa.code ??

        oa.codigo ??

        oa.oa ??

        oa.id ??

        "OA "+(index+1)

    );

}

/*=========================================================
DESCRIPCIÓN OA
=========================================================*/

function getObjectiveDescription(oa){

    if(typeof oa==="string")
        return oa;

    return String(

        oa.description ??

        oa.descripcion ??

        oa.text ??

        oa.texto ??

        oa.objetivo ??

        oa.title ??

        oa.titulo ??

        ""

    );

}

/*=========================================================
ESCAPAR HTML
=========================================================*/

function escapeHTML(text){

    return String(text??"")

        .replace(/&/g,"&amp;")

        .replace(/</g,"&lt;")

        .replace(/>/g,"&gt;")

        .replace(/"/g,"&quot;")

        .replace(/'/g,"&#039;");

}

/*=========================================================
RENDER OBJETIVOS
=========================================================*/

function renderObjectives(){

    DOM.objectives.innerHTML="";

    if(State.objectives.length===0){

        clearObjectives();

        return;

    }

    const fragment=

        document.createDocumentFragment();

    State.objectives.forEach(

        (oa,index)=>{

            const code=

                getObjectiveCode(

                    oa,

                    index

                );

            const description=

                getObjectiveDescription(

                    oa

                );

            const label=

                document.createElement("label");

            label.className="oa-item";

            label.innerHTML=`

                <input
                    type="checkbox"
                    class="oa-checkbox"
                    data-index="${index}"
                    value="${escapeHTML(code)}"
                >

                <div class="oa-content">

                    <strong>

                        ${escapeHTML(code)}

                    </strong>

                    <p>

                        ${escapeHTML(description)}

                    </p>

                </div>

            `;

            fragment.appendChild(label);

        }

    );

    DOM.objectives.appendChild(fragment);

}

/*=========================================================
OBTENER OA SELECCIONADOS
=========================================================*/

function getSelectedObjectives(){

    const selected=[];

    document

        .querySelectorAll(

            ".oa-checkbox:checked"

        )

        .forEach(

            checkbox=>{

                const index=

                    Number(

                        checkbox.dataset.index

                    );

                const oa=

                    State.objectives[index];

                if(!oa)
                    return;

                selected.push({

                    code:

                        getObjectiveCode(

                            oa,

                            index

                        ),

                    description:

                        getObjectiveDescription(

                            oa

                        )

                });

            }

        );

    return selected;

}

/*=========================================================
EVENTO CAMBIO UNIDAD
=========================================================*/

DOM.unit.addEventListener(

    "change",

    async()=>{

        const course=

            DOM.course.value;

        const subject=

            DOM.subject.value;

        const unit=

            DOM.unit.value;

        clearObjectives();

        if(

            !course ||

            !subject ||

            !unit

        ){

            return;

        }

        await loadObjectives(

            course,

            subject,

            unit

        );

    }

);

/*=========================================================
ACTUALIZAR CONTADOR OA
=========================================================*/

document.addEventListener(

    "change",

    event=>{

        if(

            !event.target.classList.contains(

                "oa-checkbox"

            )

        ){

            return;

        }

        const total=

            getSelectedObjectives()

            .length;

        const info=

            document.getElementById(

                "infoOA"

            );

        if(info){

            info.textContent=total;

        }

    }

);

/*=========================================================
FIN PARTE 3
PARTE 4
- Validación del formulario
- Payload
- Generación IA
- Render resultado
=========================================================*/
/*=========================================================
VALIDAR FORMULARIO
=========================================================*/

function validateForm(){

    if(!DOM.course.value){

        toast("Debe seleccionar un curso.", true);
        DOM.course.focus();
        return false;

    }

    if(!DOM.subject.value){

        toast("Debe seleccionar una asignatura.", true);
        DOM.subject.focus();
        return false;

    }

    if(!DOM.unit.value){

        toast("Debe seleccionar una unidad.", true);
        DOM.unit.focus();
        return false;

    }

    const objectives=getSelectedObjectives();

    if(objectives.length===0){

        toast("Seleccione al menos un Objetivo de Aprendizaje.", true);
        return false;

    }

    return true;

}

/*=========================================================
CONSTRUIR PAYLOAD
=========================================================*/

function buildPayload(){

    return{

        course:DOM.course.value,

        subject:DOM.subject.value,

        unit:DOM.unit.value,

        objectives:getSelectedObjectives(),

        topic:DOM.tema?.value.trim() || "",

        duration:DOM.duracion?.value || "",

        lessonType:DOM.tipo?.value || "",

        resources:DOM.recursos?.value.trim() || "",

        observations:DOM.observaciones?.value.trim() || ""

    };

}

/*=========================================================
GENERAR PLANIFICACIÓN IA
=========================================================*/

async function generatePlanning(){

    if(!validateForm()){

        return;

    }

    loader(true);

    if(DOM.btnGenerar){

        DOM.btnGenerar.disabled=true;

    }

    DOM.result.innerHTML=`

        <div class="empty-state">

            <i class="fa-solid fa-spinner fa-spin"></i>

            <h4>Generando planificación...</h4>

            <p>La IA está construyendo el documento.</p>

        </div>

    `;

    try{

        const payload=buildPayload();

        const response=await fetch(API.generate,{

            method:"POST",

            credentials:"same-origin",

            headers:{

                "Content-Type":"application/json",

                "Accept":"application/json"

            },

            body:JSON.stringify(payload)

        });

        if(!response.ok){

            throw new Error("HTTP "+response.status);

        }

        const json=await response.json();

        if(!json.success){

            throw new Error(

                json.message ||

                json.error ||

                "No fue posible generar la planificación."

            );

        }

        renderPlanning(json);

        toast("Planificación generada correctamente.");

    }
    catch(error){

        console.error(error);

        DOM.result.innerHTML=`

            <div class="empty-state">

                <i class="fa-solid fa-circle-exclamation"></i>

                <h4>Error</h4>

                <p>${escapeHTML(error.message)}</p>

            </div>

        `;

        toast(error.message,true);

    }
    finally{

        loader(false);

        if(DOM.btnGenerar){

            DOM.btnGenerar.disabled=false;

        }

    }

}

/*=========================================================
RENDER PLANIFICACIÓN
=========================================================*/

function renderPlanning(json){

    const planning=

        json.planning ||

        json.planificacion ||

        json.result ||

        json.data ||

        "";

    const html=

        planning.replace(/\n/g,"<br>");

    DOM.result.innerHTML=`

        <div class="planning-output">

            ${html}

        </div>

    `;

}

/*=========================================================
EVENTO FORMULARIO
=========================================================*/

DOM.form.addEventListener(

    "submit",

    async function(e){

        e.preventDefault();

        await generatePlanning();

    }

);

/*=========================================================
EVENTO BOTÓN GENERAR
=========================================================*/

if(DOM.btnGenerar){

    DOM.btnGenerar.addEventListener(

        "click",

        async function(e){

            e.preventDefault();

            await generatePlanning();

        }

    );

}

/*=========================================================
FIN PARTE 4

PARTE 5
- Limpiar formulario
- Copiar resultado
- Exportar Word
- Exportar PDF
- Impresión
=========================================================*/
/*=========================================================
LIMPIAR FORMULARIO
=========================================================*/

function resetPlanning(){

    if(DOM.form){

        DOM.form.reset();

    }

    clearSelect(

        DOM.subject,

        "Seleccione una asignatura..."

    );

    clearSelect(

        DOM.unit,

        "Seleccione una unidad..."

    );

    disable(DOM.subject);

    disable(DOM.unit);

    clearObjectives();

    DOM.result.innerHTML=`

        <div class="empty-state">

            <i class="fa-solid fa-file-lines"></i>

            <h4>Planificación</h4>

            <p>

                La planificación generada por IA
                aparecerá aquí.

            </p>

        </div>

    `;

}

/*=========================================================
BOTÓN LIMPIAR
=========================================================*/

if(DOM.btnLimpiar){

    DOM.btnLimpiar.addEventListener(

        "click",

        function(e){

            e.preventDefault();

            resetPlanning();

        }

    );

}

/*=========================================================
OBTENER TEXTO RESULTADO
=========================================================*/

function getResultText(){

    if(!DOM.result){

        return "";

    }

    return DOM.result.innerText.trim();

}

/*=========================================================
COPIAR PORTAPAPELES
=========================================================*/

async function copyPlanning(){

    try{

        const text=getResultText();

        if(text===""){

            toast(

                "No existe planificación para copiar.",

                true

            );

            return;

        }

        await navigator.clipboard.writeText(text);

        toast(

            "Planificación copiada."

        );

    }
    catch(error){

        console.error(error);

        toast(

            "No fue posible copiar.",

            true

        );

    }

}

if(DOM.btnCopiar){

    DOM.btnCopiar.addEventListener(

        "click",

        copyPlanning

    );

}

/*=========================================================
EXPORTAR WORD
=========================================================*/

function exportWord(){

    const html=`

    <html>

    <head>

        <meta charset="utf-8">

    </head>

    <body>

        ${DOM.result.innerHTML}

    </body>

    </html>

    `;

    const blob=new Blob(

        [html],

        {

            type:"application/msword"

        }

    );

    const url=URL.createObjectURL(blob);

    const a=document.createElement("a");

    a.href=url;

    a.download="planificacion.doc";

    document.body.appendChild(a);

    a.click();

    a.remove();

    URL.revokeObjectURL(url);

    toast(

        "Documento Word generado."

    );

}

if(DOM.btnWord){

    DOM.btnWord.addEventListener(

        "click",

        exportWord

    );

}

/*=========================================================
EXPORTAR PDF
=========================================================*/

function exportPDF(){

    window.print();

}

if(DOM.btnPDF){

    DOM.btnPDF.addEventListener(

        "click",

        exportPDF

    );

}

/*=========================================================
IMPRIMIR
=========================================================*/

window.addEventListener(

    "beforeprint",

    ()=>{

        document.body.classList.add(

            "printing"

        );

    }

);

window.addEventListener(

    "afterprint",

    ()=>{

        document.body.classList.remove(

            "printing"

        );

    }

);

/*=========================================================
GUARDAR PLANIFICACIÓN
=========================================================*/

function saveLocal(){

    const planning={

        date:new Date().toISOString(),

        payload:buildPayload(),

        result:DOM.result.innerHTML

    };

    localStorage.setItem(

        "aulamind_last_planning",

        JSON.stringify(planning)

    );

}

/*=========================================================
RECUPERAR PLANIFICACIÓN
=========================================================*/

function restoreLocal(){

    const raw=localStorage.getItem(

        "aulamind_last_planning"

    );

    if(!raw){

        return;

    }

    try{

        const planning=

            JSON.parse(raw);

        if(planning.result){

            DOM.result.innerHTML=

                planning.result;

        }

    }
    catch(error){

        console.error(error);

    }

}

/*=========================================================
GUARDAR AUTOMÁTICAMENTE
=========================================================*/

const observer=new MutationObserver(

    ()=>{

        if(

            DOM.result.innerText.trim()

            !==""

        ){

            saveLocal();

        }

    }

);

observer.observe(

    DOM.result,

    {

        childList:true,

        subtree:true,

        characterData:true

    }

);

restoreLocal();

/*=========================================================
FIN PARTE 5

PARTE 6
- Utilidades generales
- Manejo de errores
- Accesibilidad
- Atajos de teclado
- Autoajuste de interfaz
=========================================================*/
/*=========================================================
PARTE 6
UTILIDADES
ACCESIBILIDAD
ATAJOS
MANEJO DE ERRORES
=========================================================*/

/*=========================================================
AUTOAJUSTE TEXTAREA
=========================================================*/

function autoResize(textarea){

    if(!textarea) return;

    textarea.style.height="auto";

    textarea.style.height=textarea.scrollHeight+"px";

}

[
    DOM.tema,
    DOM.recursos,
    DOM.observaciones
].forEach(control=>{

    if(!control) return;

    control.addEventListener("input",()=>{

        autoResize(control);

    });

});

/*=========================================================
INDICADOR DE CONEXIÓN
=========================================================*/

function updateConnectionStatus(){

    const badge=document.getElementById("connectionStatus");

    if(!badge) return;

    if(navigator.onLine){

        badge.className="status online";

        badge.innerHTML="🟢 En línea";

    }else{

        badge.className="status offline";

        badge.innerHTML="🔴 Sin conexión";

    }

}

window.addEventListener(

    "online",

    updateConnectionStatus

);

window.addEventListener(

    "offline",

    updateConnectionStatus

);

updateConnectionStatus();

/*=========================================================
CONFIRMAR SALIDA
=========================================================*/

window.addEventListener(

    "beforeunload",

    function(e){

        const text=getResultText();

        if(text.length===0){

            return;

        }

        e.preventDefault();

        e.returnValue="";

    }

);

/*=========================================================
SCROLL RESULTADO
=========================================================*/

function scrollResult(){

    if(!DOM.result) return;

    DOM.result.scrollIntoView({

        behavior:"smooth",

        block:"start"

    });

}

/*=========================================================
ENFOCAR PRIMER ERROR
=========================================================*/

function focusFirstInvalid(){

    if(!DOM.course.value){

        DOM.course.focus();

        return;

    }

    if(!DOM.subject.value){

        DOM.subject.focus();

        return;

    }

    if(!DOM.unit.value){

        DOM.unit.focus();

        return;

    }

}

/*=========================================================
ATAJOS DE TECLADO
=========================================================*/

document.addEventListener(

    "keydown",

    function(event){

        const ctrl=event.ctrlKey;

        const key=event.key.toLowerCase();

        // CTRL+ENTER

        if(ctrl && key==="enter"){

            event.preventDefault();

            generatePlanning();

        }

        // CTRL+L

        if(ctrl && key==="l"){

            event.preventDefault();

            resetPlanning();

        }

        // CTRL+C

        if(ctrl && key==="c"){

            if(document.activeElement!==document.body){

                return;

            }

            event.preventDefault();

            copyPlanning();

        }

        // CTRL+P

        if(ctrl && key==="p"){

            event.preventDefault();

            exportPDF();

        }

    }

);

/*=========================================================
ANIMACIÓN BOTÓN
=========================================================*/

function pulseButton(button){

    if(!button) return;

    button.classList.add("pulse");

    setTimeout(()=>{

        button.classList.remove("pulse");

    },500);

}

/*=========================================================
ESTADO BOTÓN GENERAR
=========================================================*/

function updateGenerateButton(){

    if(!DOM.btnGenerar) return;

    const enabled=

        DOM.course.value &&
        DOM.subject.value &&
        DOM.unit.value;

    DOM.btnGenerar.disabled=!enabled;

}

[
    DOM.course,
    DOM.subject,
    DOM.unit
].forEach(control=>{

    if(!control) return;

    control.addEventListener(

        "change",

        updateGenerateButton

    );

});

updateGenerateButton();

/*=========================================================
PROGRESO
=========================================================*/

function updateProgress(){

    const progress=document.getElementById("planningProgress");

    if(!progress) return;

    let total=0;

    if(DOM.course.value) total++;
    if(DOM.subject.value) total++;
    if(DOM.unit.value) total++;

    const oa=getSelectedObjectives().length;

    if(oa>0) total++;

    progress.value=total;

}

/*=========================================================
ACTUALIZAR PROGRESO
=========================================================*/

document.addEventListener(

    "change",

    function(){

        updateProgress();

    }

);

/*=========================================================
RESALTAR RESULTADO
=========================================================*/

function flashResult(){

    if(!DOM.result) return;

    DOM.result.classList.add("highlight");

    setTimeout(()=>{

        DOM.result.classList.remove(

            "highlight"

        );

    },1200);

}

/*=========================================================
ENVOLVER GENERATE
=========================================================*/

const originalRenderPlanning=renderPlanning;

renderPlanning=function(json){

    originalRenderPlanning(json);

    flashResult();

    scrollResult();

    saveLocal();

};

/*=========================================================
MANEJO GLOBAL DE ERRORES
=========================================================*/

window.addEventListener(

    "error",

    function(event){

        console.error(

            "Planning Engine:",

            event.error

        );

    }

);

window.addEventListener(

    "unhandledrejection",

    function(event){

        console.error(

            "Promise:",

            event.reason

        );

    }

);

/*=========================================================
DIAGNÓSTICO
=========================================================*/

console.log(

    "%cPlanning Engine V2",

    "color:#0066cc;font-size:18px;font-weight:bold"

);

console.log(

    "Parte 6 cargada correctamente."

);

/*=========================================================
FIN PARTE 6

PARTE 7
- Exportación avanzada
- Historial
- Favoritos
- Restauración automática
- Funciones auxiliares finales
=========================================================*/
/*=========================================================
PARTE 7
HISTORIAL
AUTOGUARDADO
EXPORTACIÓN
FAVORITOS
=========================================================*/

/*=========================================================
CONFIGURACIÓN
=========================================================*/

const STORAGE_KEYS={

    LAST:"aulamind_last_planning",

    HISTORY:"aulamind_history",

    FAVORITES:"aulamind_favorites"

};

/*=========================================================
HISTORIAL
=========================================================*/

function getHistory(){

    try{

        return JSON.parse(

            localStorage.getItem(

                STORAGE_KEYS.HISTORY

            ) || "[]"

        );

    }catch(e){

        return [];

    }

}

function saveHistory(record){

    let history=getHistory();

    history.unshift(record);

    if(history.length>20){

        history=history.slice(0,20);

    }

    localStorage.setItem(

        STORAGE_KEYS.HISTORY,

        JSON.stringify(history)

    );

}

/*=========================================================
REGISTRO
=========================================================*/

function createHistoryRecord(){

    return{

        date:new Date().toLocaleString(),

        payload:buildPayload(),

        html:DOM.result.innerHTML,

        text:getResultText()

    };

}

/*=========================================================
GUARDAR HISTORIAL
=========================================================*/

function savePlanningHistory(){

    if(getResultText()===""){

        return;

    }

    saveHistory(

        createHistoryRecord()

    );

}

/*=========================================================
RESTAURAR ÚLTIMO DOCUMENTO
=========================================================*/

function restoreLastPlanning(){

    try{

        const raw=localStorage.getItem(

            STORAGE_KEYS.LAST

        );

        if(!raw) return;

        const data=JSON.parse(raw);

        if(data.result){

            DOM.result.innerHTML=data.result;

        }

    }catch(e){

        console.error(e);

    }

}

/*=========================================================
FAVORITOS
=========================================================*/

function getFavorites(){

    try{

        return JSON.parse(

            localStorage.getItem(

                STORAGE_KEYS.FAVORITES

            ) || "[]"

        );

    }catch(e){

        return [];

    }

}

function saveFavorite(){

    if(getResultText()===""){

        toast(

            "No existe planificación.",

            true

        );

        return;

    }

    const list=getFavorites();

    list.unshift({

        title:

            DOM.tema?.value ||

            "Planificación",

        date:new Date().toLocaleString(),

        html:DOM.result.innerHTML

    });

    localStorage.setItem(

        STORAGE_KEYS.FAVORITES,

        JSON.stringify(list)

    );

    toast(

        "Agregada a favoritos."

    );

}

/*=========================================================
BOTÓN FAVORITO
=========================================================*/

const btnFavorite=

document.getElementById(

    "btnFavorito"

);

if(btnFavorite){

    btnFavorite.addEventListener(

        "click",

        saveFavorite

    );

}

/*=========================================================
EXPORTAR HTML
=========================================================*/

function exportHTML(){

    const blob=new Blob(

        [

            `
<!DOCTYPE html>

<html lang="es">

<head>

<meta charset="utf-8">

<title>Planificación AulaMind</title>

<style>

body{

font-family:Arial;

margin:40px;

line-height:1.6;

}

</style>

</head>

<body>

${DOM.result.innerHTML}

</body>

</html>

`

        ],

        {

            type:"text/html"

        }

    );

    const url=

        URL.createObjectURL(blob);

    const a=

        document.createElement("a");

    a.href=url;

    a.download="planificacion.html";

    a.click();

    URL.revokeObjectURL(url);

}

/*=========================================================
EXPORTAR TEXTO
=========================================================*/

function exportTXT(){

    const blob=new Blob(

        [

            getResultText()

        ],

        {

            type:"text/plain"

        }

    );

    const url=

        URL.createObjectURL(blob);

    const a=

        document.createElement("a");

    a.href=url;

    a.download="planificacion.txt";

    a.click();

    URL.revokeObjectURL(url);

}

/*=========================================================
ATAJOS EXPORTACIÓN
=========================================================*/

document.addEventListener(

    "keydown",

    function(e){

        if(

            e.ctrlKey &&

            e.shiftKey &&

            e.key==="H"

        ){

            e.preventDefault();

            exportHTML();

        }

        if(

            e.ctrlKey &&

            e.shiftKey &&

            e.key==="T"

        ){

            e.preventDefault();

            exportTXT();

        }

    }

);

/*=========================================================
AUTO GUARDADO
=========================================================*/

function autoSave(){

    if(getResultText()===""){

        return;

    }

    saveLocal();

}

setInterval(

    autoSave,

    30000

);

/*=========================================================
ACTUALIZAR renderPlanning
=========================================================*/

const previousRender=

renderPlanning;

renderPlanning=function(json){

    previousRender(json);

    savePlanningHistory();

    saveLocal();

};

/*=========================================================
RESTAURAR AL INICIO
=========================================================*/

restoreLastPlanning();

/*=========================================================
LOG
=========================================================*/

console.log(

    "Planning Engine V2 - Parte 7 cargada"

);

/*=========================================================
FIN PARTE 7

PARTE 8
- Inicialización final
- Verificaciones
- Compatibilidad
- Limpieza
- Funciones finales
- Cierre del archivo planning.js
=========================================================*/
/*=========================================================
PARTE 8
PLANNING ENGINE V2
FINALIZACIÓN DEL SISTEMA
=========================================================*/

/*=========================================================
VALIDACIÓN FINAL
=========================================================*/

function finalValidation(){

    console.group("Planning Engine V2");

    console.log("Curso:",!!DOM.course);
    console.log("Asignatura:",!!DOM.subject);
    console.log("Unidad:",!!DOM.unit);
    console.log("Objetivos:",!!DOM.objectives);
    console.log("Formulario:",!!DOM.form);
    console.log("Resultado:",!!DOM.result);

    console.groupEnd();

}

/*=========================================================
RESTAURAR ÚLTIMO ESTADO
=========================================================*/

function restoreSelections(){

    try{

        const raw=localStorage.getItem("aulamind_last_planning");

        if(!raw){

            return;

        }

        const data=JSON.parse(raw);

        if(!data.payload){

            return;

        }

        if(DOM.tema)
            DOM.tema.value=data.payload.topic||"";

        if(DOM.duracion)
            DOM.duracion.value=data.payload.duration||"";

        if(DOM.tipo)
            DOM.tipo.value=data.payload.lessonType||"";

        if(DOM.recursos)
            DOM.recursos.value=data.payload.resources||"";

        if(DOM.observaciones)
            DOM.observaciones.value=data.payload.observations||"";

    }
    catch(error){

        console.error(error);

    }

}

/*=========================================================
VERSIÓN
=========================================================*/

const PlanningEngine={

    name:"Planning Engine",

    version:"2.0.0",

    build:"Enterprise",

    release:"2026",

    author:"AulaMind Enterprise"

};

/*=========================================================
API PÚBLICA
=========================================================*/

window.PlanningEngine={

    version:PlanningEngine.version,

    state:State,

    generate:generatePlanning,

    reset:resetPlanning,

    copy:copyPlanning,

    exportWord:exportWord,

    exportPDF:exportPDF,

    exportHTML:exportHTML,

    exportTXT:exportTXT,

    history:getHistory,

    favorites:getFavorites

};

/*=========================================================
INICIALIZACIÓN FINAL
=========================================================*/

window.addEventListener(

    "load",

    function(){

        finalValidation();

        restoreSelections();

        updateGenerateButton();

        updateConnectionStatus();

        updateProgress();

        console.log(
            "Planning Engine listo."
        );

    }

);

/*=========================================================
LIMPIEZA
=========================================================*/

window.addEventListener(

    "unload",

    function(){

        if(observer){

            observer.disconnect();

        }

    }

);

/*=========================================================
COMPATIBILIDAD
=========================================================*/

if(!window.fetch){

    alert(

        "Su navegador no soporta la API Fetch."

    );

}

if(!window.Promise){

    alert(

        "Su navegador no soporta Promises."

    );

}

/*=========================================================
INFORMACIÓN
=========================================================*/

console.log(

`

========================================================

        AulaMind Enterprise 3.0

        Planning Engine V2

        Versión : ${PlanningEngine.version}

        Build   : ${PlanningEngine.build}

        Release : ${PlanningEngine.release}

========================================================

Módulos cargados

✓ Configuración

✓ Estado global

✓ DOM

✓ API

✓ Cursos

✓ Asignaturas

✓ Unidades

✓ Objetivos de Aprendizaje

✓ IA

✓ Historial

✓ Exportación

✓ Favoritos

✓ Autoguardado

✓ Accesibilidad

✓ Utilidades

========================================================

Sistema iniciado correctamente.

========================================================

`

);

/*=========================================================
FIN DEL ARCHIVO
planning.js
=========================================================*/
