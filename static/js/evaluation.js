/******************************************************************************
 * AulaMind Enterprise 3.0
 * Archivo : static/js/evaluation.js
 * Módulo  : Evaluaciones IA
 * Autor   : Biotecno Chile
 * Versión : 3.0
 ******************************************************************************/

document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    /**********************************************************************
     * CONFIGURACIÓN
     **********************************************************************/

    const CONFIG = window.EVALUATION_CONFIG || {};

    // Token CSRF: Flask-WTF exige X-CSRFToken en todos los POST
    const CSRF_TOKEN =
        (document.getElementById("csrf_token") || {}).value || "";

    const URLS = {

        generate : CONFIG.generateUrl,
        history  : CONFIG.historyUrl,

        document(id){
            return `/evaluation/${id}`;
        },

        exportLinks(id){
            return `/evaluation/export-links/${id}`;
        }

    };

    /**********************************************************************
     * ELEMENTOS DEL DOM
     **********************************************************************/

    const form = document.getElementById("evaluationForm");

    const resultSection = document.getElementById("resultSection");

    const result = document.getElementById("evaluationResult");

    const historyBody = document.getElementById("historyBody");

    const loadingModal = document.getElementById("loadingModal");

    const copyButton = document.getElementById("copyEvaluation");

    const wordButton = document.getElementById("downloadWord");

    const pdfButton = document.getElementById("downloadPdf");

    const toast = document.getElementById("toast");

    /**********************************************************************
     * VARIABLES
     **********************************************************************/

    let currentDocument = null;

    let lastGeneratedMarkdown = "";

    let exportInfo = {

        word : null,
        pdf  : null

    };

    /**********************************************************************
     * UTILIDADES
     **********************************************************************/

    function showLoading(){

        if(loadingModal){

            loadingModal.classList.add("active");

        }

    }

    function hideLoading(){

        if(loadingModal){

            loadingModal.classList.remove("active");

        }

    }

    function showToast(message,type="success"){

        if(!toast){

            console.log(message);

            return;

        }

        toast.innerText = message;

        toast.className = "";

        toast.classList.add("show");

        toast.classList.add(type);

        setTimeout(()=>{

            toast.classList.remove("show");

            toast.classList.remove(type);

        },3000);

    }

    function renderMarkdown(text){

        const source = String(text ?? "");

        if(
            window.marked &&
            typeof window.marked.parse === "function"
        ){

            try{

                return window.marked.parse(source);

            }

            catch(error){

                console.error(
                    "Error renderizando markdown:",
                    error
                );

            }

        }

        return source
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br>");

    }

    function showResult(content){

        lastGeneratedMarkdown = content || "";

        if(result){

            result.innerHTML = renderMarkdown(lastGeneratedMarkdown);

        }

        if(resultSection){

            resultSection.style.display="block";

            resultSection.scrollIntoView({

                behavior:"smooth",

                block:"start"

            });

        }

    }

    function clearResult(){

        currentDocument = null;

        lastGeneratedMarkdown = "";

        exportInfo.word = null;

        exportInfo.pdf = null;

        if(result){

            result.innerHTML="";

        }

    }

    async function request(url,options={}){

        options.headers = Object.assign(
            { "X-CSRFToken": CSRF_TOKEN },
            options.headers || {}
        );

        const response = await fetch(url,options);

        const data = await response.json();

        if(!response.ok){

            throw new Error(

                data.error ||

                "Error del servidor."

            );

        }

        if(data.success===false){

            throw new Error(

                data.error ||

                "Operación falló."

            );

        }

        return data;

    }

    /**********************************************************************
     * CARGA EN CASCADA DEL CURRÍCULO
     **********************************************************************/

    const API_BASE = "/planning/api/curriculum";

    async function populateSelect(url, selectId, placeholder){

        const select = document.getElementById(selectId);

        if(!select){

            return;

        }

        try{

            const response = await fetch(url);

            const data = await response.json();

            if(!data.success){

                throw new Error(data.message || "Error API");

            }

            select.innerHTML =
                `<option value="">${placeholder}</option>`;

            const key =
                selectId === "curso"      ? "courses"    :
                selectId === "asignatura" ? "subjects"   :
                selectId === "unidad"     ? "units"      :
                "objectives";

            const items = data[key];

            if(!items || items.length === 0){

                select.innerHTML =
                    "<option value=\"\">No hay datos disponibles</option>";

                select.disabled = true;

                return;

            }

            items.forEach((item)=>{

                const opt = document.createElement("option");

                if(typeof item === "object" && item !== null){

                    if(item.code){

                        opt.value = item.code;
                        opt.textContent =
                            item.code + " - " + (item.description || "");
                        opt.title = item.description || item.code;

                    }

                    else if(item.id){

                        opt.value = item.id;
                        opt.textContent = item.name || item.id;

                    }

                    else if(item.name){

                        opt.value = item.name;
                        opt.textContent = item.name;

                    }

                    else{

                        opt.value = JSON.stringify(item);
                        opt.textContent =
                            item.name || item.id || JSON.stringify(item);

                    }

                }

                else{

                    opt.value = item;
                    opt.textContent = item;

                }

                select.appendChild(opt);

            });

            select.disabled = false;

        }

        catch(error){

            console.error(
                "Error cargando " + selectId + ":",
                error
            );

            select.innerHTML =
                "<option value=\"\">Error cargando datos</option>";

            select.disabled = true;

        }

    }

    (async()=>{

        await populateSelect(
            API_BASE + "/courses",
            "curso",
            "Selecciona un curso..."
        );

    })();

    const cursoSelect = document.getElementById("curso");

    if(cursoSelect){

        cursoSelect.addEventListener("change", async function(){

            const course = this.value;

            const asignatura = document.getElementById("asignatura");
            const unidad = document.getElementById("unidad");
            const objetivo = document.getElementById("objetivo");

            asignatura.innerHTML =
                "<option value=\"\">Selecciona una asignatura...</option>";
            unidad.innerHTML =
                "<option value=\"\">Selecciona una unidad...</option>";
            objetivo.innerHTML =
                "<option value=\"\">Selecciona un OA...</option>";

            asignatura.disabled = !course;
            unidad.disabled = true;
            objetivo.disabled = true;

            if(!course){

                return;

            }

            await populateSelect(
                API_BASE + "/subjects/" + encodeURIComponent(course),
                "asignatura",
                "Selecciona una asignatura..."
            );

        });

    }

    const asignaturaSelect = document.getElementById("asignatura");

    if(asignaturaSelect){

        asignaturaSelect.addEventListener("change", async function(){

            const course = document.getElementById("curso").value;
            const subject = this.value;

            const unidad = document.getElementById("unidad");
            const objetivo = document.getElementById("objetivo");

            unidad.innerHTML =
                "<option value=\"\">Selecciona una unidad...</option>";
            objetivo.innerHTML =
                "<option value=\"\">Selecciona un OA...</option>";

            unidad.disabled = !subject;
            objetivo.disabled = true;

            if(!subject){

                return;

            }

            await populateSelect(
                API_BASE + "/units/" +
                    encodeURIComponent(course) + "/" +
                    encodeURIComponent(subject),
                "unidad",
                "Selecciona una unidad..."
            );

        });

    }

    const unidadSelect = document.getElementById("unidad");

    if(unidadSelect){

        unidadSelect.addEventListener("change", async function(){

            const course = document.getElementById("curso").value;
            const subject = document.getElementById("asignatura").value;
            const unit = this.value;

            const objetivo = document.getElementById("objetivo");

            objetivo.innerHTML =
                "<option value=\"\">Selecciona un OA...</option>";

            objetivo.disabled = !unit;

            if(!unit){

                return;

            }

            await populateSelect(
                API_BASE + "/objectives/" +
                    encodeURIComponent(course) + "/" +
                    encodeURIComponent(subject) + "/" +
                    encodeURIComponent(unit),
                "objetivo",
                "Selecciona un OA..."
            );

        });

    }

    /**********************************************************************
     * GENERAR EVALUACIÓN
     **********************************************************************/

    async function generateEvaluation(){

        const payload = Object.fromEntries(

            new FormData(form).entries()

        );

        showLoading();

        try{

            const response = await request(

                URLS.generate,

                {

                    method:"POST",

                    headers:{

                        "Content-Type":"application/json"

                    },

                    body:JSON.stringify(payload)

                }

            );

            currentDocument = response.document_id;

            showResult(

                response.content

            );

            showToast(

                "Evaluación generada correctamente."

            );

            await loadExportLinks();

            await loadHistory();

        }

        catch(error){

            showResult(

                "ERROR\n\n"+error.message

            );

            showToast(

                error.message,

                "error"

            );

        }

        finally{

            hideLoading();

        }

    }
        /**********************************************************************
     * CARGAR HISTORIAL
     **********************************************************************/

    async function loadHistory(){

        if(!historyBody){

            return;

        }

        historyBody.innerHTML = "";

        try{

            const response = await request(

                URLS.history

            );

            if(!response.items){

                return;

            }

            if(response.items.length===0){

                historyBody.innerHTML=`
                    <tr>
                        <td colspan="4" style="text-align:center">
                            No existen evaluaciones.
                        </td>
                    </tr>
                `;

                return;

            }

            response.items.forEach(document=>{

                const tr=document.createElement("tr");

                const created=document.created_at
                    ? new Date(document.created_at).toLocaleString()
                    : "";

                tr.innerHTML=`

                    <td>${created}</td>

                    <td>${document.course || ""}</td>

                    <td>${document.subject || ""}</td>

                    <td>

                        <button
                            class="btn-action btn-open"
                            data-id="${document.id}">
                            Abrir
                        </button>

                        <button
                            class="btn-action btn-word"
                            data-id="${document.id}">
                            Word
                        </button>

                        <button
                            class="btn-action btn-pdf"
                            data-id="${document.id}">
                            PDF
                        </button>

                        <button
                            class="btn-action delete btn-delete"
                            data-id="${document.id}">
                            Eliminar
                        </button>

                    </td>

                `;

                historyBody.appendChild(tr);

            });

        }

        catch(error){

            console.error(error);

            historyBody.innerHTML=`

                <tr>

                    <td colspan="4">

                        Error cargando historial

                    </td>

                </tr>

            `;

        }

    }

    /**********************************************************************
     * ABRIR DOCUMENTO
     **********************************************************************/

    async function openDocument(documentId){

        showLoading();

        try{

            const response = await request(

                URLS.document(documentId)

            );

            currentDocument=documentId;

            showResult(

                response.document.content

            );

            await loadExportLinks();

            showToast(

                "Documento cargado."

            );

        }

        catch(error){

            showToast(

                error.message,

                "error"

            );

        }

        finally{

            hideLoading();

        }

    }

    /**********************************************************************
     * ELIMINAR DOCUMENTO
     **********************************************************************/

    async function deleteDocument(documentId){

        const confirmDelete=confirm(

            "¿Desea eliminar esta evaluación?"

        );

        if(!confirmDelete){

            return;

        }

        showLoading();

        try{

            await request(

                URLS.document(documentId),

                {

                    method:"DELETE"

                }

            );

            if(currentDocument===documentId){

                clearResult();

            }

            await loadHistory();

            showToast(

                "Evaluación eliminada."

            );

        }

        catch(error){

            showToast(

                error.message,

                "error"

            );

        }

        finally{

            hideLoading();

        }

    }

    /**********************************************************************
     * EXPORTACIONES
     **********************************************************************/

    async function loadExportLinks(){

        if(!currentDocument){

            return;

        }

        try{

            const response=await request(

                URLS.exportLinks(

                    currentDocument

                )

            );

            exportInfo.word=response.word;

            exportInfo.pdf=response.pdf;

        }

        catch(error){

            console.error(error);

        }

    }
        /**********************************************************************
     * BOTÓN COPIAR
     **********************************************************************/

    async function copyEvaluation(){

        if(!result){

            return;

        }

        const text=(lastGeneratedMarkdown || result.textContent || "").trim();

        if(text===""){

            showToast(

                "No existe contenido para copiar.",

                "error"

            );

            return;

        }

        try{

            await navigator.clipboard.writeText(text);

            showToast(

                "Evaluación copiada al portapapeles."

            );

        }

        catch(error){

            console.error(error);

            showToast(

                "No fue posible copiar.",

                "error"

            );

        }

    }

    /**********************************************************************
     * EXPORTAR WORD
     **********************************************************************/

    function exportWord(){

        if(!exportInfo.word){

            showToast(

                "Debe generar o abrir una evaluación.",

                "error"

            );

            return;

        }

        window.location.href=exportInfo.word;

    }

    /**********************************************************************
     * EXPORTAR PDF
     **********************************************************************/

    function exportPdf(){

        if(!exportInfo.pdf){

            showToast(

                "Debe generar o abrir una evaluación.",

                "error"

            );

            return;

        }

        window.location.href=exportInfo.pdf;

    }

    /**********************************************************************
     * EVENTOS DEL FORMULARIO
     **********************************************************************/

    if(form){

        form.addEventListener(

            "submit",

            async(event)=>{

                event.preventDefault();

                await generateEvaluation();

            }

        );

    }

    /**********************************************************************
     * BOTONES PRINCIPALES
     **********************************************************************/

    if(copyButton){

        copyButton.addEventListener(

            "click",

            copyEvaluation

        );

    }

    if(wordButton){

        wordButton.addEventListener(

            "click",

            exportWord

        );

    }

    if(pdfButton){

        pdfButton.addEventListener(

            "click",

            exportPdf

        );

    }

    /**********************************************************************
     * EVENTOS DEL HISTORIAL
     **********************************************************************/

    if(historyBody){

        historyBody.addEventListener(

            "click",

            async(event)=>{

                const button=event.target.closest("button");

                if(!button){

                    return;

                }

                const documentId=parseInt(

                    button.dataset.id

                );

                if(

                    button.classList.contains(

                        "btn-open"

                    )

                ){

                    await openDocument(

                        documentId

                    );

                    return;

                }

                if(

                    button.classList.contains(

                        "btn-delete"

                    )

                ){

                    await deleteDocument(

                        documentId

                    );

                    return;

                }

                if(

                    button.classList.contains(

                        "btn-word"

                    )

                ){

                    currentDocument=documentId;

                    await loadExportLinks();

                    exportWord();

                    return;

                }

                if(

                    button.classList.contains(

                        "btn-pdf"

                    )

                ){

                    currentDocument=documentId;

                    await loadExportLinks();

                    exportPdf();

                    return;

                }

            }

        );

    }

    /**********************************************************************
     * INICIALIZACIÓN
     **********************************************************************/

    (async()=>{

        try{

            await loadHistory();

        }

        catch(error){

            console.error(error);

        }

    })();

});