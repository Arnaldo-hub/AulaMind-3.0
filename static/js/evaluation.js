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

    let exportInfo = {

        word : null,
        pdf  : null

    };

    /**********************************************************************
     * UTILIDADES
     **********************************************************************/

    function showLoading(){

        if(loadingModal){

            loadingModal.style.display = "flex";

        }

    }

    function hideLoading(){

        if(loadingModal){

            loadingModal.style.display = "none";

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

    function showResult(content){

        if(result){

            result.textContent = content || "";

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

        exportInfo.word = null;

        exportInfo.pdf = null;

        if(result){

            result.textContent="";

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
                            class="btn-open"
                            data-id="${document.id}">
                            Abrir
                        </button>

                        <button
                            class="btn-word"
                            data-id="${document.id}">
                            Word
                        </button>

                        <button
                            class="btn-pdf"
                            data-id="${document.id}">
                            PDF
                        </button>

                        <button
                            class="btn-delete"
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

        const text=result.textContent.trim();

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