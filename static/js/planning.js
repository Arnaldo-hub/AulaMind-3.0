/*
===========================================================
AulaMind Enterprise 3.0
Planning Engine
static/js/planning.js

VERSIÓN CORREGIDA
PARTE 1 DE 4

Incluye:
- Inicialización única
- Configuración API
- Referencias DOM
- Estado
- Utilidades
- Orden correcto de cursos
- Normalización de respuestas
- Toast
- Loader
- Fetch JSON
===========================================================
*/

async function startPlanning() {
    await initializePlanning();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startPlanning);
} else {
    startPlanning();
}

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

    const form =
        document.getElementById("planningForm");

    const course =
        document.getElementById("course");

    const subject =
        document.getElementById("subject");

    const unit =
        document.getElementById("unit");

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

    const btnCopiar =
        document.getElementById("btnCopiar");

    const btnWord =
        document.getElementById("btnWord");

    const btnPDF =
        document.getElementById("btnPDF");

    const loader =
        document.getElementById("loader");

    const toast =
        document.getElementById("toast");


    //=========================================================
    // VALIDACIÓN DE ELEMENTOS PRINCIPALES
    //=========================================================

    if (!form) {

        console.error(
            "AulaMind: no se encontró #planningForm"
        );

        return;

    }

    if (!course || !subject || !unit) {

        console.error(
            "AulaMind: faltan selectores curriculares."
        );

        return;

    }

    if (!learningObjectives) {

        console.error(
            "AulaMind: no se encontró #learningObjectives"
        );

        return;

    }


    //=========================================================
    // ESTADO DEL MÓDULO
    //=========================================================

    let currentCourses = [];

    let currentSubjects = [];

    let currentUnits = [];

    let currentObjectives = [];


    //=========================================================
    // CREAR OPTION
    //=========================================================

    function createOption(value, text) {

        const option =
            document.createElement("option");

        option.value = value;

        option.textContent = text;

        return option;

    }


    //=========================================================
    // LIMPIAR SELECT
    //=========================================================

    function clearSelect(select, label) {

        if (!select) return;

        select.innerHTML = "";

        select.appendChild(

            createOption("", label)

        );

    }


    //=========================================================
    // ACTIVAR / DESACTIVAR SELECT
    //=========================================================

    function enableSelect(select) {

        if (select) {

            select.disabled = false;

        }

    }


    function disableSelect(select) {

        if (select) {

            select.disabled = true;

        }

    }


    //=========================================================
    // EXTRAER TEXTO DE RESPUESTAS API
    //=========================================================

    function extractText(item) {

        if (typeof item === "string") {

            return item.trim();

        }

        if (!item || typeof item !== "object") {

            return "";

        }

        return String(

            item.name ??

            item.nombre ??

            item.course ??

            item.curso ??

            item.subject ??

            item.asignatura ??

            item.unit ??

            item.unidad ??

            item.title ??

            item.titulo ??

            ""

        ).trim();

    }


    //=========================================================
    // ELIMINAR DUPLICADOS
    //=========================================================

    function uniqueStrings(items) {

        const values = Array.isArray(items)

            ? items

            : [];

        const normalized = values

            .map(extractText)

            .filter(Boolean);

        return [...new Set(normalized)];

    }


    //=========================================================
    // ORDEN CURRICULAR DE CURSOS
    //=========================================================

    function courseOrder(courseName) {

        const text =
            String(courseName).toLowerCase();

        const match =
            text.match(/\d+/);

        const number =
            match ? parseInt(match[0], 10) : 99;


        // 1° Básico a 8° Básico

        if (

            text.includes("bás") ||

            text.includes("bas")

        ) {

            return number;

        }


        // 1° Medio a 4° Medio

        if (text.includes("medio")) {

            return 8 + number;

        }


        return 99;

    }


    //=========================================================
    // ORDENAR CURSOS
    //=========================================================

    function sortCourses(items) {

        return uniqueStrings(items).sort(

            (a, b) => {

                const orderA =
                    courseOrder(a);

                const orderB =
                    courseOrder(b);

                if (orderA !== orderB) {

                    return orderA - orderB;

                }

                return a.localeCompare(

                    b,

                    "es",

                    {

                        numeric: true,

                        sensitivity: "base"

                    }

                );

            }

        );

    }


    //=========================================================
    // ORDEN ALFABÉTICO
    //=========================================================

    function sortAlphabetically(items) {

        return uniqueStrings(items).sort(

            (a, b) =>

                a.localeCompare(

                    b,

                    "es",

                    {

                        numeric: true,

                        sensitivity: "base"

                    }

                )

        );

    }


    //=========================================================
    // ORDENAR UNIDADES
    //=========================================================

    function sortUnits(items) {

        return uniqueStrings(items).sort(

            (a, b) =>

                a.localeCompare(

                    b,

                    "es",

                    {

                        numeric: true,

                        sensitivity: "base"

                    }

                )

        );

    }


    //=========================================================
    // ESCAPAR HTML
    //=========================================================

    function escapeHTML(value) {

        return String(value ?? "")

            .replace(/&/g, "&amp;")

            .replace(/</g, "&lt;")

            .replace(/>/g, "&gt;")

            .replace(/"/g, "&quot;")

            .replace(/'/g, "&#039;");

    }


    //=========================================================
    // CONFIGURACIÓN PANEL OA COMPACTO
    //=========================================================

    learningObjectives.style.maxHeight =
        "360px";

    learningObjectives.style.overflowY =
        "auto";

    learningObjectives.style.paddingRight =
        "8px";

    learningObjectives.style.scrollBehavior =
        "smooth";


    //=========================================================
    // TOAST
    //=========================================================

    function showToast(message, success = true) {

        if (!toast) {

            console.log(message);

            return;

        }

        toast.textContent = message;

        toast.className = success

            ? "toast success show"

            : "toast error show";


        setTimeout(() => {

            toast.classList.remove("show");

        }, 3000);

    }


    //=========================================================
    // LOADER
    //=========================================================

    function openLoader() {

        if (loader) {

            loader.style.display = "flex";

        }

        if (btnGenerar) {

            btnGenerar.disabled = true;

        }

    }


    function closeLoader() {

        if (loader) {

            loader.style.display = "none";

        }

        if (btnGenerar) {

            btnGenerar.disabled = false;

        }

    }


    //=========================================================
    // FETCH JSON
    //=========================================================

    async function fetchJSON(url) {

        const response = await fetch(url, {
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
         throw new Error(`HTTP ${response.status} en ${url}`);
        }

        return await response.json();
    }

    //=========================================================
    // LIMPIAR OBJETIVOS DE APRENDIZAJE
    //=========================================================

    function clearObjectives() {

        currentObjectives = [];

        learningObjectives.innerHTML = `

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


    //=========================================================
    // PLACEHOLDER RESULTADO
    //=========================================================

    function resetResult() {

        if (!resultado) return;

        resultado.innerHTML = `

            <div class="placeholder">

                <i class="fa-solid fa-robot"></i>

                <h2>
                    AulaMind IA está listo
                </h2>

                <p>

                    Complete la información curricular
                    y presione

                    <strong>
                        Generar Planificación IA
                    </strong>

                </p>

            </div>

        `;

    }


    //=========================================================
    // FIN PARTE 1 DE 4
    // CONTINUAR INMEDIATAMENTE CON PARTE 2
    //=========================================================
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


            const json =
                await fetchJSON(API.courses);


            if (!json.success) {

                throw new Error(
                    json.message ||
                    json.error ||
                    "No fue posible cargar los cursos."
                );

            }


            currentCourses =
                sortCourses(json.courses || []);


            clearSelect(
                course,
                "Seleccione un curso..."
            );


            currentCourses.forEach(courseName => {

                course.appendChild(

                    createOption(
                        courseName,
                        courseName
                    )

                );

            });


            enableSelect(course);


            console.log(
                "Cursos cargados:",
                currentCourses
            );

        }

        catch (error) {

            console.error(
                "Error loadCourses:",
                error
            );


            clearSelect(
                course,
                "Error cargando cursos"
            );


            showToast(
                "Error cargando cursos.",
                false
            );

        }

    }


    //=========================================================
    // CARGAR ASIGNATURAS SEGÚN CURSO
    //=========================================================

    async function loadSubjects(courseName) {

        try {

            currentSubjects = [];

            currentUnits = [];

            currentObjectives = [];


            disableSelect(subject);

            clearSelect(
                subject,
                "Cargando asignaturas..."
            );


            disableSelect(unit);

            clearSelect(
                unit,
                "Seleccione una asignatura..."
            );


            clearObjectives();


            const url =

                `${API.subjects}/${encodeURIComponent(courseName)}`;


            console.log(
                "Consultando asignaturas:",
                url
            );


            const json =
                await fetchJSON(url);


            if (!json.success) {

                throw new Error(
                    json.message ||
                    json.error ||
                    "No existen asignaturas para este curso."
                );

            }


            currentSubjects =
                sortAlphabetically(
                    json.subjects || []
                );


            clearSelect(
                subject,
                "Seleccione una asignatura..."
            );


            currentSubjects.forEach(subjectName => {

                subject.appendChild(

                    createOption(
                        subjectName,
                        subjectName
                    )

                );

            });


            if (currentSubjects.length > 0) {

                enableSelect(subject);

            }


            console.log(
                `Asignaturas de ${courseName}:`,
                currentSubjects
            );

        }

        catch (error) {

            console.error(
                "Error loadSubjects:",
                error
            );


            clearSelect(
                subject,
                "Sin asignaturas disponibles"
            );


            disableSelect(subject);


            showToast(
                "No fue posible cargar las asignaturas.",
                false
            );

        }

    }


    //=========================================================
    // CARGAR UNIDADES SEGÚN CURSO Y ASIGNATURA
    //=========================================================

    async function loadUnits(
        courseName,
        subjectName
    ) {

        try {

            currentUnits = [];

            currentObjectives = [];


            disableSelect(unit);

            clearSelect(
                unit,
                "Cargando unidades..."
            );


            clearObjectives();


            const url =

                `${API.units}/${encodeURIComponent(courseName)}/${encodeURIComponent(subjectName)}`;


            console.log(
                "Consultando unidades:",
                url
            );


            const json =
                await fetchJSON(url);


            if (!json.success) {

                throw new Error(
                    json.message ||
                    json.error ||
                    "No existen unidades para esta selección."
                );

            }


            currentUnits =
                sortUnits(
                    json.units || []
                );


            clearSelect(
                unit,
                "Seleccione una unidad..."
            );


            currentUnits.forEach(unitName => {

                unit.appendChild(

                    createOption(
                        unitName,
                        unitName
                    )

                );

            });


            if (currentUnits.length > 0) {

                enableSelect(unit);

            }


            console.log(
                `Unidades de ${courseName} / ${subjectName}:`,
                currentUnits
            );

        }

        catch (error) {

            console.error(
                "Error loadUnits:",
                error
            );


            clearSelect(
                unit,
                "Sin unidades disponibles"
            );


            disableSelect(unit);


            showToast(
                "No fue posible cargar las unidades.",
                false
            );

        }

    }


    //=========================================================
    // NORMALIZAR RESPUESTA DE OBJETIVOS
    //=========================================================

    function normalizeObjectives(json) {

        if (Array.isArray(json.objectives)) {

            return json.objectives;

        }


        if (Array.isArray(json.objetivos)) {

            return json.objetivos;

        }


        if (Array.isArray(json.data)) {

            return json.data;

        }


        return [];

    }


    //=========================================================
    // CARGAR OBJETIVOS DE APRENDIZAJE
    //=========================================================

    async function loadObjectives(
        courseName,
        subjectName,
        unitName
    ) {

        try {

            currentObjectives = [];


            learningObjectives.innerHTML = `

                <div class="empty-state">

                    <i class="fa-solid fa-spinner fa-spin"></i>

                    <h4>
                        Cargando Objetivos de Aprendizaje...
                    </h4>

                </div>

            `;


            const url =

                `${API.objectives}/${encodeURIComponent(courseName)}/${encodeURIComponent(subjectName)}/${encodeURIComponent(unitName)}`;


            console.log(
                "Consultando OA:",
                url
            );


            const json =
                await fetchJSON(url);


            if (!json.success) {

                throw new Error(
                    json.message ||
                    json.error ||
                    "No existen Objetivos de Aprendizaje."
                );

            }


            currentObjectives =
                normalizeObjectives(json);


            console.log(
                `OA de ${courseName} / ${subjectName} / ${unitName}:`,
                currentObjectives
            );


            renderObjectives();

        }

        catch (error) {

            console.error(
                "Error loadObjectives:",
                error
            );


            showToast(
                "No fue posible cargar los Objetivos de Aprendizaje.",
                false
            );


            clearObjectives();

        }

    }


    //=========================================================
    // OBTENER CÓDIGO DEL OA
    //=========================================================

    function getObjectiveCode(oa, index) {

        if (!oa) {

            return `OA ${index + 1}`;

        }


        if (typeof oa === "string") {

            const match =
                oa.match(/OA\s*\d+/i);


            return match

                ? match[0].toUpperCase()

                : `OA ${index + 1}`;

        }


        return String(

            oa.code ??

            oa.codigo ??

            oa.oa ??

            oa.id ??

            `OA ${index + 1}`

        ).trim();

    }


    //=========================================================
    // OBTENER DESCRIPCIÓN DEL OA
    //=========================================================

    function getObjectiveDescription(oa) {

        if (!oa) {

            return "";

        }


        if (typeof oa === "string") {

            return oa.trim();

        }


        return String(

            oa.description ??

            oa.descripcion ??

            oa.text ??

            oa.texto ??

            oa.objetivo ??

            oa.title ??

            oa.titulo ??

            ""

        ).trim();

    }


    //=========================================================
    // RENDERIZAR OA EN PANEL COMPACTO
    //=========================================================

    function renderObjectives() {

        learningObjectives.innerHTML = "";


        if (currentObjectives.length === 0) {

            learningObjectives.innerHTML = `

                <div class="empty-state">

                    <i class="fa-solid fa-circle-info"></i>

                    <h4>
                        Esta unidad no posee Objetivos de Aprendizaje.
                    </h4>

                </div>

            `;

            return;

        }


        const fragment =
            document.createDocumentFragment();


        currentObjectives.forEach(
            (oa, index) => {


                const codigo =
                    getObjectiveCode(oa, index);


                const descripcion =
                    getObjectiveDescription(oa);


                const item =
                    document.createElement("label");


                item.className =
                    "oa-item";


                item.style.display =
                    "flex";

                item.style.alignItems =
                    "flex-start";

                item.style.gap =
                    "10px";

                item.style.padding =
                    "12px";

                item.style.marginBottom =
                    "8px";

                item.style.border =
                    "1px solid #e5e7eb";

                item.style.borderRadius =
                    "10px";

                item.style.cursor =
                    "pointer";

                item.style.background =
                    "#ffffff";


                item.innerHTML = `

                    <input
                        type="checkbox"
                        class="oa-checkbox"
                        value="${escapeHTML(codigo)}"
                        data-index="${index}"
                        id="oa_${index}"
                        style="margin-top: 4px;"
                    >

                    <div style="min-width: 0;">

                        <strong>
                            ${escapeHTML(codigo)}
                        </strong>

                        <p style="
                            margin: 4px 0 0 0;
                            line-height: 1.45;
                        ">
                            ${escapeHTML(descripcion)}
                        </p>

                    </div>

                `;


                fragment.appendChild(item);

            }

        );


        learningObjectives.appendChild(fragment);


        learningObjectives.scrollTop = 0;

    }


    //=========================================================
    // EVENTO CAMBIO DE CURSO
    //=========================================================

    course.addEventListener(
        "change",
        async function () {


            const selectedCourse =
                course.value;


            currentSubjects = [];

            currentUnits = [];

            currentObjectives = [];


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


            if (selectedCourse === "") {

                return;

            }


            await loadSubjects(
                selectedCourse
            );

        }

    );


    //=========================================================
    // EVENTO CAMBIO DE ASIGNATURA
    //=========================================================

    subject.addEventListener(
        "change",
        async function () {


            const selectedSubject =
                subject.value;


            currentUnits = [];

            currentObjectives = [];


            clearSelect(
                unit,
                "Seleccione una unidad..."
            );


            disableSelect(unit);


            clearObjectives();


            if (

                course.value === "" ||

                selectedSubject === ""

            ) {

                return;

            }


            await loadUnits(

                course.value,

                selectedSubject

            );

        }

    );


    //=========================================================
    // EVENTO CAMBIO DE UNIDAD
    //=========================================================

    unit.addEventListener(
        "change",
        async function () {


            const selectedUnit =
                unit.value;


            currentObjectives = [];


            clearObjectives();


            if (

                course.value === "" ||

                subject.value === "" ||

                selectedUnit === ""

            ) {

                return;

            }


            await loadObjectives(

                course.value,

                subject.value,

                selectedUnit

            );

        }

    );


    //=========================================================
    // FIN PARTE 2 DE 4
    // CONTINUAR INMEDIATAMENTE CON PARTE 3
    //=========================================================
        //=========================================================
    // OBTENER OA SELECCIONADOS
    //=========================================================

    function getSelectedObjectives() {

        const selected = [];

        document
            .querySelectorAll(".oa-checkbox:checked")
            .forEach(checkbox => {

                const index =
                    Number(checkbox.dataset.index);


                const objective =
                    currentObjectives[index];


                if (!objective) {

                    return;

                }


                selected.push({

                    code:
                        getObjectiveCode(
                            objective,
                            index
                        ),

                    description:
                        getObjectiveDescription(
                            objective
                        )

                });

            });


        return selected;

    }


    //=========================================================
    // VALIDAR FORMULARIO
    //=========================================================

    function validatePlanning() {

        if (course.value === "") {

            showToast(
                "Seleccione un curso.",
                false
            );

            course.focus();

            return false;

        }


        if (subject.value === "") {

            showToast(
                "Seleccione una asignatura.",
                false
            );

            subject.focus();

            return false;

        }


        if (unit.value === "") {

            showToast(
                "Seleccione una unidad.",
                false
            );

            unit.focus();

            return false;

        }


        const selectedObjectives =
            getSelectedObjectives();


        if (selectedObjectives.length === 0) {

            showToast(
                "Debe seleccionar al menos un Objetivo de Aprendizaje.",
                false
            );

            learningObjectives.scrollIntoView({

                behavior: "smooth",

                block: "center"

            });

            return false;

        }


        if (

            !tema ||

            tema.value.trim() === ""

        ) {

            showToast(
                "Debe ingresar el tema de la clase.",
                false
            );


            if (tema) {

                tema.focus();

            }


            return false;

        }


        return true;

    }


    //=========================================================
    // CONSTRUIR PAYLOAD
    //=========================================================

    function buildPayload() {

        return {

            curso:
                course.value,

            asignatura:
                subject.value,

            unidad:
                unit.value,

            objetivos:
                getSelectedObjectives(),

            tema:
                tema
                    ? tema.value.trim()
                    : "",

            duracion:
                duracion
                    ? duracion.value
                    : "",

            tipo:
                tipo
                    ? tipo.value
                    : "",

            metodologia:
                "Aprendizaje Activo",

            evaluacion:
                "Formativa",

            recursos:
                recursos
                    ? recursos.value.trim()
                    : "",

            observaciones:
                observaciones
                    ? observaciones.value.trim()
                    : ""

        };

    }


    //=========================================================
    // MOSTRAR PLANIFICACIÓN
    //=========================================================

    function renderPlanning(content) {

        if (!resultado) {

            return;

        }


        if (

            content === undefined ||

            content === null ||

            String(content).trim() === ""

        ) {

            renderError(
                "La IA respondió sin contenido."
            );

            return;

        }


        resultado.innerHTML = `

            <div class="planning-response">

                ${String(content)
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/\n/g, "<br>")}

            </div>

        `;


        resultado.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }


    //=========================================================
    // MOSTRAR ERROR
    //=========================================================

    function renderError(message) {

        if (!resultado) {

            return;

        }


        resultado.innerHTML = `

            <div class="planning-error">

                <i class="fa-solid fa-circle-exclamation"></i>

                <h3>
                    Error
                </h3>

                <p>
                    ${escapeHTML(
                        message ||
                        "Error desconocido."
                    )}
                </p>

            </div>

        `;


        resultado.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }


    //=========================================================
    // LEER RESPUESTA DEL SERVIDOR
    //=========================================================

    async function readServerResponse(response) {

        const contentType =
            response.headers.get("content-type") || "";


        if (

            contentType.includes(
                "application/json"
            )

        ) {

            return await response.json();

        }


        const text =
            await response.text();


        throw new Error(

            text ||

            `Respuesta HTTP ${response.status}`

        );

    }


    //=========================================================
    // GENERAR PLANIFICACIÓN IA
    //=========================================================

    async function generatePlanning() {

        if (!validatePlanning()) {

            return;

        }


        openLoader();


        try {

            const payload =
                buildPayload();


            console.log(
                "Payload enviado a AulaMind IA:",
                payload
            );


            const response =
                await fetch(

                    API.generate,

                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify(payload)

                    }

                );


            const json =
                await readServerResponse(response);


            console.log(
                "Respuesta del servidor:",
                json
            );


            if (

                !response.ok ||

                !json.success

            ) {

                const serverMessage =

                    json.error ||

                    json.message ||

                    "No fue posible generar la planificación.";


                renderError(
                    serverMessage
                );


                showToast(
                    serverMessage,
                    false
                );


                return;

            }


            const content =

                json.content ??

                json.planificacion ??

                json.result ??

                json.data ??

                "";


            renderPlanning(content);


            showToast(
                "Planificación generada correctamente."
            );

        }

        catch (error) {

            console.error(
                "Error generatePlanning:",
                error
            );


            renderError(
                error.message ||
                "Error de conexión con el servidor."
            );


            showToast(
                "Error generando la planificación.",
                false
            );

        }

        finally {

            closeLoader();

        }

    }


    //=========================================================
    // SUBMIT DEL FORMULARIO
    //=========================================================

    form.addEventListener(

        "submit",

        async function (event) {

            event.preventDefault();

            await generatePlanning();

        }

    );


    //=========================================================
    // EVITAR DOBLE GENERACIÓN
    //=========================================================
    //
    // El botón btnGenerar está dentro del formulario.
    // Por eso la generación se controla solamente mediante
    // el evento submit anterior.
    //
    // No agregamos un segundo listener click al botón porque
    // eso podría provocar dos peticiones POST /generate.
    //=========================================================


    //=========================================================
    // LIMPIAR FORMULARIO
    //=========================================================

    function clearPlanningForm() {

        form.reset();


        currentSubjects = [];

        currentUnits = [];

        currentObjectives = [];


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


        showToast(
            "Formulario limpiado."
        );

    }


    //=========================================================
    // COPIAR PLANIFICACIÓN
    //=========================================================

    async function copyPlanning() {

        try {

            if (!resultado) {

                return;

            }


            const texto =
                resultado.innerText.trim();


            if (

                texto === "" ||

                texto.includes(
                    "AulaMind IA está listo"
                )

            ) {

                showToast(
                    "No existe una planificación para copiar.",
                    false
                );

                return;

            }


            await navigator.clipboard.writeText(
                texto
            );


            showToast(
                "Planificación copiada al portapapeles."
            );

        }

        catch (error) {

            console.error(
                "Error copyPlanning:",
                error
            );


            showToast(
                "No fue posible copiar la planificación.",
                false
            );

        }

    }


    //=========================================================
    // EXPORTAR WORD
    //=========================================================

    function exportWord() {

        showToast(
            "La exportación Word se mantendrá para su módulo correspondiente.",
            false
        );

    }


    //=========================================================
    // EXPORTAR PDF
    //=========================================================

    function exportPDF() {

        showToast(
            "La exportación PDF se mantendrá para su módulo correspondiente.",
            false
        );

    }


    //=========================================================
    // FIN PARTE 3 DE 4
    // CONTINUAR INMEDIATAMENTE CON PARTE 4
    //=========================================================
        //=========================================================
    // EVENTO BOTÓN LIMPIAR
    //=========================================================

    if (btnLimpiar) {

        btnLimpiar.addEventListener(

            "click",

            function (event) {

                event.preventDefault();

                clearPlanningForm();

            }

        );

    }


    //=========================================================
    // EVENTO BOTÓN COPIAR
    //=========================================================

    if (btnCopiar) {

        btnCopiar.addEventListener(

            "click",

            async function (event) {

                event.preventDefault();

                await copyPlanning();

            }

        );

    }


    //=========================================================
    // EVENTO BOTÓN WORD
    //=========================================================

    if (btnWord) {

        btnWord.addEventListener(

            "click",

            function (event) {

                event.preventDefault();

                exportWord();

            }

        );

    }


    //=========================================================
    // EVENTO BOTÓN PDF
    //=========================================================

    if (btnPDF) {

        btnPDF.addEventListener(

            "click",

            function (event) {

                event.preventDefault();

                exportPDF();

            }

        );

    }


    //=========================================================
    // ATAJO CTRL + ENTER
    //=========================================================

    document.addEventListener(

        "keydown",

        async function (event) {

            if (

                event.ctrlKey &&

                event.key === "Enter"

            ) {

                event.preventDefault();

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
    // INICIALIZACIÓN ÚNICA
    //=========================================================

    async function initializePlanning() {

        console.log(
            "========================================"
        );

        console.log(
            "AulaMind Enterprise 3.0"
        );

        console.log(
            "Planning Engine"
        );

        console.log(
            "Inicializando módulo curricular..."
        );

        console.log(
            "========================================"
        );


        // Estado inicial del formulario

        clearSelect(
            course,
            "Seleccione un curso..."
        );


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


        // Cargar cursos una sola vez

        await loadCourses();


        console.log(
            "========================================"
        );

        console.log(
            "Planning Engine inicializado correctamente"
        );

        console.log(
            "========================================"
        );

    }


 //=========================================================
// EJECUTAR INICIALIZACIÓN
//=========================================================

console.log("ANTES initializePlanning");

initializePlanning()
    .then(() => console.log("initializePlanning OK"))
    .catch(err => console.error("initializePlanning ERROR", err));

//=============================================================
// FIN planning.js
// (el cierre DOMContentLoaded era un remanente del armado
// por partes y rompía toda la sintaxis del archivo)
//=============================================================