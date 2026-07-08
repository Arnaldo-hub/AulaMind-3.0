/*
===========================================================
AulaMind Enterprise 3.0
Planning Engine

MÓDULO PLANIFICACIÓN IA
PARTE 1

Autor:
Biotecno Chile
===========================================================
*/

document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    //=========================================================
    // CONFIGURACIÓN API
    //=========================================================

    const API = {

        courses: "/planning/api/curriculum/courses",

        subjects: "/planning/api/curriculum/subjects",

        units: "/planning/api/curriculum/units",

        objectives: "/planning/api/curriculum/objectives",

        generate: "/planning/generate"

    };

    //=========================================================
    // REFERENCIAS DOM
    //=========================================================

    const form = document.getElementById("planningForm");

    const course = document.getElementById("course");

    const subject = document.getElementById("subject");

    const unit = document.getElementById("unit");

    const learningObjectives =
        document.getElementById("learningObjectives");

    const tema =
        document.getElementById("tema");

    const duracion =
        document.getElementById("duracion");

    const tipo =
        document.getElementById("tipo");

    const recursos =
        document.getElementById("recursos");

    const observaciones =
        document.getElementById("observaciones");

    const resultado =
        document.getElementById("resultado");

    const btnGenerar =
        document.getElementById("btnGenerar");

    const btnLimpiar =
        document.getElementById("btnLimpiar");

    const loader =
        document.getElementById("loader");

    const toast =
        document.getElementById("toast");

    //=========================================================
    // ESTADO
    //=========================================================

    let currentCourses = [];

    let currentSubjects = [];

    let currentUnits = [];

    let currentObjectives = [];

    //=========================================================
    // TOAST
    //=========================================================

    function showToast(message, success = true){

        if(!toast) return;

        toast.innerHTML = message;

        toast.className = success
            ? "toast success show"
            : "toast error show";

        setTimeout(()=>{

            toast.classList.remove("show");

        },3000);

    }

    //=========================================================
    // LOADER
    //=========================================================

    function openLoader(){

        if(loader){

            loader.style.display="flex";

        }

        if(btnGenerar){

            btnGenerar.disabled=true;

        }

    }

    function closeLoader(){

        if(loader){

            loader.style.display="none";

        }

        if(btnGenerar){

            btnGenerar.disabled=false;

        }

    }

    //=========================================================
    // FETCH JSON
    //=========================================================

    async function fetchJSON(url){

        const response = await fetch(url);

        if(!response.ok){

            throw new Error(

                `HTTP ${response.status}`

            );

        }

        return await response.json();

    }

    //=========================================================
    // OPTION
    //=========================================================

    function createOption(value,text){

        const option =
            document.createElement("option");

        option.value=value;

        option.textContent=text;

        return option;

    }

    //=========================================================
    // LIMPIAR SELECT
    //=========================================================

    function clearSelect(select,label){

        select.innerHTML="";

        select.appendChild(

            createOption("",label)

        );

    }

    function disableSelect(select){

        select.disabled=true;

    }

    function enableSelect(select){

        select.disabled=false;

    }

    //=========================================================
    // LIMPIAR OA
    //=========================================================

    function clearObjectives(){

        learningObjectives.innerHTML=`

            <div class="empty-oa">

                Seleccione una unidad.

            </div>

        `;

    }

    //=========================================================
    // PLACEHOLDER RESULTADO
    //=========================================================

    function resetResult(){

        resultado.innerHTML=`

            <div class="placeholder">

                <i class="fa-solid fa-robot"></i>

                <h3>

                    AulaMind IA listo.

                </h3>

                <p>

                    Seleccione Curso,
                    Asignatura,
                    Unidad y Objetivos
                    para generar la planificación.

                </p>

            </div>

        `;

    }

    resetResult();
        //=========================================================
    // CARGAR CURSOS
    //=========================================================

    async function loadCourses() {

        try {

            disableSelect(course);

            clearSelect(
                course,
                "Cargando cursos..."
            );

            const json = await fetchJSON(API.courses);

            if (!json.success) {

                throw new Error(
                    "No fue posible cargar los cursos."
                );

            }

            currentCourses = json.courses || [];

            clearSelect(
                course,
                "Seleccione un curso..."
            );

            currentCourses.forEach(item => {

                course.appendChild(

                    createOption(item, item)

                );

            });

            enableSelect(course);

        }

        catch (error) {

            console.error(error);

            showToast(

                "Error cargando cursos.",

                false

            );

        }

    }

    //=========================================================
    // CARGAR ASIGNATURAS
    //=========================================================

    async function loadSubjects(courseName) {

        try {

            disableSelect(subject);

            clearSelect(

                subject,

                "Cargando asignaturas..."

            );

            const json = await fetchJSON(

                `${API.subjects}/${encodeURIComponent(courseName)}`

            );

            if (!json.success) {

                throw new Error(

                    "No existen asignaturas."

                );

            }

            currentSubjects = json.subjects || [];

            clearSelect(

                subject,

                "Seleccione una asignatura..."

            );

            currentSubjects.forEach(item => {

                subject.appendChild(

                    createOption(item, item)

                );

            });

            enableSelect(subject);

        }

        catch (error) {

            console.error(error);

            showToast(

                "No fue posible cargar asignaturas.",

                false

            );

        }

    }

    //=========================================================
    // CARGAR UNIDADES
    //=========================================================

    async function loadUnits(courseName, subjectName) {

        try {

            disableSelect(unit);

            clearSelect(

                unit,

                "Cargando unidades..."

            );

            const json = await fetchJSON(

                `${API.units}/${encodeURIComponent(courseName)}/${encodeURIComponent(subjectName)}`

            );

            if (!json.success) {

                throw new Error(

                    "No existen unidades."

                );

            }

            currentUnits = json.units || [];

            clearSelect(

                unit,

                "Seleccione una unidad..."

            );

            currentUnits.forEach(item => {

                unit.appendChild(

                    createOption(item, item)

                );

            });

            enableSelect(unit);

        }

        catch(error){

            console.error(error);

            showToast(

                "No fue posible cargar unidades.",

                false

            );

        }

    }

    //=========================================================
    // CARGAR OBJETIVOS
    //=========================================================

    async function loadObjectives(courseName, subjectName, unitName){

        try{

            learningObjectives.innerHTML=`

                <div class="loading-oa">

                    Cargando Objetivos...

                </div>

            `;

            const json = await fetchJSON(

                `${API.objectives}/${encodeURIComponent(courseName)}/${encodeURIComponent(subjectName)}/${encodeURIComponent(unitName)}`

            );

            if(!json.success){

                throw new Error(

                    "No existen objetivos."

                );

            }

            currentObjectives = json.objectives || [];

            renderObjectives();

        }

        catch(error){

            console.error(error);

            showToast(

                "No fue posible cargar los OA.",

                false

            );

            clearObjectives();

        }

    }

    //=========================================================
    // RENDER OA
    //=========================================================

    function renderObjectives(){

        learningObjectives.innerHTML="";

        if(currentObjectives.length===0){

            learningObjectives.innerHTML=`

                <div class="empty-oa">

                    Esta unidad no posee Objetivos de Aprendizaje.

                </div>

            `;

            return;

        }

        currentObjectives.forEach((oa,index)=>{

            const code =

                oa.code ||

                oa.codigo ||

                "";

            const description =

                oa.description ||

                oa.descripcion ||

                "";

            const card=document.createElement("label");

            card.className="oa-item";

            card.innerHTML=`

                <input

                    type="checkbox"

                    class="oa-checkbox"

                    id="oa_${index}"

                    value="${code}"

                >

                <div>

                    <strong>${code}</strong>

                    <br>

                    ${description}

                </div>

            `;

            learningObjectives.appendChild(card);

        });

    }

    //=========================================================
    // CAMBIOS DE CURRÍCULUM
    //=========================================================

    course.addEventListener("change", async ()=>{

        clearSelect(unit,"Seleccione una unidad...");

        disableSelect(unit);

        clearObjectives();

        if(course.value===""){

            clearSelect(subject,"Seleccione una asignatura...");

            disableSelect(subject);

            return;

        }

        await loadSubjects(course.value);

    });

    subject.addEventListener("change", async ()=>{

        clearObjectives();

        if(subject.value===""){

            clearSelect(unit,"Seleccione una unidad...");

            disableSelect(unit);

            return;

        }

        await loadUnits(

            course.value,

            subject.value

        );

    });

    unit.addEventListener("change", async ()=>{

        if(unit.value===""){

            clearObjectives();

            return;

        }

        await loadObjectives(

            course.value,

            subject.value,

            unit.value

        );

    });

    //=========================================================
    // INICIALIZAR CURRÍCULUM
    //=========================================================

    clearSelect(course,"Seleccione un curso...");

    clearSelect(subject,"Seleccione una asignatura...");

    clearSelect(unit,"Seleccione una unidad...");

    disableSelect(subject);

    disableSelect(unit);

    clearObjectives();

    loadCourses();
        //=========================================================
    // OBTENER OA SELECCIONADOS
    //=========================================================

    function getSelectedObjectives(){

        const selected = [];

        document
            .querySelectorAll(".oa-checkbox:checked")
            .forEach(item=>{

                const objective = currentObjectives.find(obj=>{

                    return (

                        obj.code === item.value ||

                        obj.codigo === item.value

                    );

                });

                if(objective){

                    selected.push(objective);

                }

            });

        return selected;

    }

    //=========================================================
    // VALIDAR
    //=========================================================

    function validatePlanning(){

        if(course.value===""){

            showToast(

                "Seleccione un curso.",

                false

            );

            course.focus();

            return false;

        }

        if(subject.value===""){

            showToast(

                "Seleccione una asignatura.",

                false

            );

            subject.focus();

            return false;

        }

        if(unit.value===""){

            showToast(

                "Seleccione una unidad.",

                false

            );

            unit.focus();

            return false;

        }

        if(getSelectedObjectives().length===0){

            showToast(

                "Seleccione al menos un Objetivo de Aprendizaje.",

                false

            );

            return false;

        }

        if(tema.value.trim()===""){

            showToast(

                "Debe ingresar el tema.",

                false

            );

            tema.focus();

            return false;

        }

        return true;

    }

    //=========================================================
    // PAYLOAD
    //=========================================================

    function buildPayload(){

        return{

            curso: course.value,

            asignatura: subject.value,

            unidad: unit.value,

            objetivos: getSelectedObjectives(),

            tema: tema.value.trim(),

            duracion: duracion.value,

            tipo: tipo.value,

            metodologia: "Aprendizaje Activo",

            evaluacion: "Formativa",

            recursos: recursos.value,

            observaciones: observaciones.value

        };

    }

    //=========================================================
    // MOSTRAR RESULTADO
    //=========================================================

    function renderPlanning(content){

        resultado.innerHTML=`

            <div class="planning-result">

                ${content.replace(/\n/g,"<br>")}

            </div>

        `;

    }

    //=========================================================
    // MOSTRAR ERROR
    //=========================================================

    function renderError(message){

        resultado.innerHTML=`

            <div class="error-box">

                <h3>Error</h3>

                <p>${message}</p>

            </div>

        `;

    }

    //=========================================================
    // GENERAR PLANIFICACIÓN
    //=========================================================

    async function generatePlanning(){

        if(!validatePlanning()){

            return;

        }

        openLoader();

        try{

            const payload = buildPayload();

            const response = await fetch(

                API.generate,

                {

                    method:"POST",

                    headers:{

                        "Content-Type":"application/json"

                    },

                    body:JSON.stringify(payload)

                }

            );

            const json = await response.json();

            closeLoader();

            if(!json.success){

                renderError(

                    json.error ||

                    "No fue posible generar la planificación."

                );

                showToast(

                    "La IA devolvió un error.",

                    false

                );

                return;

            }

            renderPlanning(

                json.content

            );

            showToast(

                "Planificación generada correctamente."

            );

        }

        catch(error){

            console.error(error);

            closeLoader();

            renderError(

                error.message

            );

            showToast(

                "Error de conexión.",

                false

            );

        }

    }

    //=========================================================
    // SUBMIT
    //=========================================================

    form.addEventListener(

        "submit",

        async function(e){

            e.preventDefault();

            await generatePlanning();

        }

    );

    //=========================================================
    // BOTÓN GENERAR
    //=========================================================

    btnGenerar.addEventListener(

        "click",

        async function(e){

            e.preventDefault();

            await generatePlanning();

        }

    );
        //=========================================================
    // LIMPIAR FORMULARIO
    //=========================================================

    function clearPlanningForm(){

        form.reset();

        clearSelect(

            subject,

            "Seleccione una asignatura..."

        );

        clearSelect(

            unit,

            "Seleccione una unidad..."

        );

        disableSelect(subject);

        disableSelect(unit);

        clearObjectives();

        resetResult();

        loadCourses();

    }

    //=========================================================
    // BOTÓN LIMPIAR
    //=========================================================

    btnLimpiar.addEventListener(

        "click",

        function(e){

            e.preventDefault();

            clearPlanningForm();

            showToast(

                "Formulario limpiado."

            );

        }

    );

    //=========================================================
    // COPIAR PLANIFICACIÓN
    //=========================================================

    if(btnCopiar){

        btnCopiar.addEventListener(

            "click",

            async function(){

                try{

                    const texto =

                        resultado.innerText.trim();

                    if(texto===""){

                        showToast(

                            "No existe una planificación.",

                            false

                        );

                        return;

                    }

                    await navigator.clipboard.writeText(

                        texto

                    );

                    showToast(

                        "Planificación copiada."

                    );

                }

                catch(error){

                    console.error(error);

                    showToast(

                        "No fue posible copiar.",

                        false

                    );

                }

            }

        );

    }

    //=========================================================
    // CTRL + ENTER
    //=========================================================

    document.addEventListener(

        "keydown",

        async function(e){

            if(

                e.ctrlKey &&

                e.key==="Enter"

            ){

                e.preventDefault();

                await generatePlanning();

            }

        }

    );

    //=========================================================
    // FUNCIONES GLOBALES
    //=========================================================

    window.generatePlanning =

        generatePlanning;

    window.clearPlanningForm =

        clearPlanningForm;

    //=========================================================
    // INICIALIZACIÓN
    //=========================================================

    console.log(

        "===================================="

    );

    console.log(

        "AulaMind Enterprise 3.0"

    );

    console.log(

        "Planning Engine Inicializado"

    );

    console.log(

        "===================================="

    );

    resetResult();

    loadCourses();

});
