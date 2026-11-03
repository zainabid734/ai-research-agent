let currentMode = "research";

marked.setOptions({
    breaks: true,
    gfm: true,
});

function setMode(mode) {
    currentMode = mode;
    document.getElementById("researchBtn").classList.toggle("active", mode === "research");
    document.getElementById("debateBtn").classList.toggle("active", mode === "debate");
    document.getElementById("debateSection").classList.toggle("hidden", mode === "research");
    document.getElementById("btnText").textContent = mode === "research" ? "Research" : "Challenge Me";
    document.getElementById("researchResults").classList.add("hidden");
    document.getElementById("debateResults").classList.add("hidden");
    document.getElementById("topicInput").focus();
}

function setLoading(isLoading, step) {
    const loading = document.getElementById("loading");
    const submitBtn = document.getElementById("submitBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    if (isLoading) {
        loading.classList.remove("hidden");
        submitBtn.disabled = true;
        btnText.textContent = "Processing...";
        btnLoader.classList.remove("hidden");

        ["step1", "step2", "step3"].forEach((id, i) => {
            const el = document.getElementById(id);
            el.classList.remove("active", "done");
            if (i + 1 < step) el.classList.add("done");
            else if (i + 1 === step) el.classList.add("active");
        });
    } else {
        loading.classList.add("hidden");
        submitBtn.disabled = false;
        btnText.textContent = currentMode === "research" ? "Research" : "Challenge Me";
        btnLoader.classList.add("hidden");
        ["step1", "step2", "step3"].forEach((id) => {
            document.getElementById(id).classList.remove("active", "done");
        });
    }
}

function showError(msg) {
    document.getElementById("errorText").textContent = msg;
    document.getElementById("error").classList.remove("hidden");
}

function hideError() {
    document.getElementById("error").classList.add("hidden");
}

function animateSteps() {
    let step = 1;
    const interval = setInterval(() => {
        if (step >= 3) { clearInterval(interval); return; }
        setLoading(true, ++step);
    }, 2500);
    return interval;
}

function handleSubmit() {
    const topic = document.getElementById("topicInput").value.trim();
    if (!topic) {
        document.getElementById("topicInput").focus();
        return;
    }

    const pov = document.getElementById("povInput").value.trim();
    if (currentMode === "debate" && !pov) {
        document.getElementById("povInput").focus();
        return;
    }

    hideError();
    document.getElementById("researchResults").classList.add("hidden");
    document.getElementById("debateResults").classList.add("hidden");
    setLoading(true, 1);

    const stepAnim = animateSteps();

    const endpoint = currentMode === "research" ? "/api/research" : "/api/debate";
    const body = currentMode === "research" ? { topic } : { topic, pov };

    fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    })
        .then(async (res) => {
            let data;
            try {
                data = await res.json();
            } catch (e) {
                throw new Error("Unable to parse server response.");
            }
            if (!res.ok) {
                if (res.status === 429) {
                    throw new Error(data.error || "Rate limit exceeded. Please try again later.");
                }
                throw new Error(data.error || `Request failed with status ${res.status}`);
            }
            return data;
        })
        .then((data) => {
            clearInterval(stepAnim);
            setLoading(false);
            showResults(data);
        })
        .catch((err) => {
            clearInterval(stepAnim);
            setLoading(false);
            showError(err.message || "Something went wrong. Please try again.");
        });
}

function renderSources(container, countEl, sources) {
    container.innerHTML = "";
    if (!sources || sources.length === 0) {
        countEl.textContent = "";
        return;
    }
    countEl.textContent = `${sources.length} sources`;
    sources.forEach((src) => {
        const item = document.createElement("div");
        item.className = "source-item";
        const snippet = src.snippet ? `<div class="source-snippet">${escapeHtml(src.snippet)}</div>` : "";
        item.innerHTML = `
            <div class="source-num">${src.id}</div>
            <div class="source-info">
                <div class="source-title"><a href="${escapeHtml(src.url)}" target="_blank" rel="noopener">${escapeHtml(src.title)}</a></div>
                <div class="source-url">${escapeHtml(src.url)}</div>
                ${snippet}
            </div>
        `;
        container.appendChild(item);
    });
}

function showResults(data) {
    let resultsEl, answerEl, sourcesEl, sourceCountEl;

    if (currentMode === "debate") {
        resultsEl = document.getElementById("debateResults");
        answerEl = document.getElementById("debateAnswer");
        sourcesEl = document.getElementById("debateSources");
        sourceCountEl = document.getElementById("debateSourceCount");
        answerEl.innerHTML = marked.parse(data.challenge);
    } else {
        resultsEl = document.getElementById("researchResults");
        answerEl = document.getElementById("researchAnswer");
        sourcesEl = document.getElementById("researchSources");
        sourceCountEl = document.getElementById("researchSourceCount");
        answerEl.innerHTML = marked.parse(data.answer);
        const badge = document.getElementById("researchConfidence");
        if (data.confidence) {
            badge.className = `badge badge-${data.confidence}`;
            badge.textContent = data.confidence;
        } else {
            badge.className = "badge hidden";
        }
    }

    renderSources(sourcesEl, sourceCountEl, data.sources);

    resultsEl.classList.remove("hidden");
    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Char counters
document.getElementById("topicInput").addEventListener("input", function () {
    document.getElementById("topicCount").textContent = this.value.length;
});

document.getElementById("povInput").addEventListener("input", function () {
    document.getElementById("povCount").textContent = this.value.length;
});

// Enter to submit
document.getElementById("topicInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSubmit();
});

document.getElementById("povInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
    }
});
