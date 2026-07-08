document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("evaluationForm");
    const modal = document.getElementById("loadingModal");
    const target = document.getElementById("evaluationResult");
    const section = document.getElementById("resultSection");
    const toast = document.getElementById("toast");
    const copyButton = document.getElementById("copyEvaluation");

    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());

        if (modal) modal.style.display = "flex";
        if (target) target.textContent = "";

        try {
            const response = await fetch(window.EVALUATION_CONFIG.generateUrl, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "No fue posible generar la evaluación.");
            }

            if (target) target.textContent = data.content || "";
            if (section) {
                section.style.display = "block";
                section.scrollIntoView({behavior: "smooth", block: "start"});
            }

            if (toast) {
                toast.classList.add("show");
                setTimeout(() => toast.classList.remove("show"), 3000);
            }
        } catch (error) {
            if (target) target.textContent = "Error: " + error.message;
            if (section) {
                section.style.display = "block";
                section.scrollIntoView({behavior: "smooth", block: "start"});
            }
            console.error("Evaluation request failed:", error);
        } finally {
            if (modal) modal.style.display = "none";
        }
    });

    if (copyButton) {
        copyButton.addEventListener("click", async () => {
            const text = target ? target.textContent : "";
            if (text) await navigator.clipboard.writeText(text);
        });
    }
});
