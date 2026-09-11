// ================================
// DARK MODE
// ================================

const themeToggle = document.getElementById("themeToggle");

if (themeToggle) {

    // Load saved theme
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.textContent = "☀️";
    }

    // Toggle theme
    themeToggle.addEventListener("click", function () {

        document.body.classList.toggle("dark-mode");

        const isDark =
            document.body.classList.contains("dark-mode");

        if (isDark) {
            themeToggle.textContent = "☀️";
            localStorage.setItem("theme", "dark");
        } else {
            themeToggle.textContent = "🌙";
            localStorage.setItem("theme", "light");
        }

    });

}


// ================================
// RESEARCH ELEMENTS
// ================================

const researchButton =
    document.getElementById("researchButton");

const topicInput =
    document.getElementById("topic");

const loading =
    document.getElementById("loading");

const results =
    document.getElementById("results");

const errorBox =
    document.getElementById("error");

const report =
    document.getElementById("report");

const feedback =
    document.getElementById("feedback");

const sources =
    document.getElementById("sources");

const progressTitle =
    document.getElementById("progressTitle");

const progressMessage =
    document.getElementById("progressMessage");

const progressPercent =
    document.getElementById("progressPercent");

const progressFill =
    document.getElementById("progressFill");

const liveResearchData =
    document.getElementById("liveResearchData");


// ================================
// EVENT LISTENERS
// ================================

researchButton.addEventListener(
    "click",
    runResearch
);


topicInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {
            runResearch();
        }

    }
);


// ================================
// RUN RESEARCH
// ================================

async function runResearch() {

    const topic =
        topicInput.value.trim();

    if (!topic) {

        showError(
            "Please enter a research topic."
        );

        return;
    }


    // Reset UI

    results.classList.add("hidden");

    errorBox.classList.add("hidden");

    loading.classList.remove("hidden");

    researchButton.disabled = true;

    resetProgress();


    try {

        const response =
            await fetch("/api/research", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    topic: topic
                })

            });


        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                errorText || "Server error"
            );

        }


        const reader =
            response.body.getReader();

        const decoder =
            new TextDecoder();

        let buffer = "";


        while (true) {

            const {
                value,
                done
            } = await reader.read();


            if (done) {
                break;
            }


            buffer += decoder.decode(
                value,
                {
                    stream: true
                }
            );


            const events =
                buffer.split("\n\n");

            buffer =
                events.pop();


            for (const eventText of events) {

                if (!eventText.trim()) {
                    continue;
                }


                const dataLine =
                    eventText
                        .split("\n")
                        .find(
                            line =>
                                line.startsWith("data:")
                        );


                if (!dataLine) {
                    continue;
                }


                const jsonData =
                    dataLine.replace(
                        /^data:\s*/,
                        ""
                    );


                const event =
                    JSON.parse(jsonData);


                handleServerEvent(event);

            }

        }


    } catch (error) {

        console.error(
            "Research error:",
            error
        );


        showError(
            error.message ||
            "Something went wrong. Please try again."
        );


    } finally {

        loading.classList.add("hidden");

        researchButton.disabled = false;

    }

}


// ================================
// HANDLE SERVER EVENTS
// ================================

function handleServerEvent(event) {

    // -----------------------------
    // Progress event
    // -----------------------------

    if (event.type === "progress") {

        updateProgress(
            event.stage,
            event.message,
            event.percent,
            event.data
        );

        return;
    }


    // -----------------------------
    // Final result
    // -----------------------------

    if (event.type === "result") {

        const data =
            event.data;


        report.textContent =
            data.report;


        feedback.textContent =
            data.feedback;


        sources.innerHTML =
            formatSources(
                data.sources
            );


        results.classList.remove(
            "hidden"
        );


        return;
    }


    // -----------------------------
    // Error
    // -----------------------------

    if (event.type === "error") {

        throw new Error(
            event.message ||
            "Research failed."
        );

    }

}


// ================================
// UPDATE PROGRESS
// ================================

function updateProgress(
    stage,
    message,
    percent,
    data
) {

    progressMessage.textContent =
        message;


    progressPercent.textContent =
        `${percent}%`;


    progressFill.style.width =
        `${percent}%`;


    updateStep(stage);


    // -----------------------------
    // Show live research sources
    // -----------------------------

    if (
        data &&
        data.sources &&
        data.sources.length
    ) {

        liveResearchData.innerHTML = `

            <strong>
                Sources discovered:
                ${data.sources.length}
            </strong>

            <div class="live-sources">

                ${data.sources
                    .slice(0, 5)
                    .map(url => `

                        <div>
                            ${escapeHtml(
                                getHostname(url)
                            )}
                        </div>

                    `)
                    .join("")
                }

            </div>

        `;

    }


    // -----------------------------
    // Show critic score
    // -----------------------------

    if (
        data &&
        typeof data.score === "number"
    ) {

        liveResearchData.innerHTML = `

            <strong>
                Quality score:
                ${data.score}/10
            </strong>

        `;

    }

}


// ================================
// UPDATE PROGRESS STEPS
// ================================

function updateStep(currentStage) {

    // Handle retry stages
    let normalizedStage =
        currentStage;


    if (
        currentStage === "additional_search"
    ) {

        normalizedStage =
            "search";

    }


    if (
        currentStage === "rewrite"
    ) {

        normalizedStage =
            "writer";

    }


    const steps =
        document.querySelectorAll(
            ".progress-step"
        );


    const order = [
        "search",
        "reader",
        "writer",
        "critic"
    ];


    const currentIndex =
        order.indexOf(
            normalizedStage
        );


    steps.forEach(step => {

        const stage =
            step.dataset.stage;


        const stageIndex =
            order.indexOf(stage);


        const icon =
            step.querySelector(
                ".step-icon"
            );


        if (stageIndex < currentIndex) {

            icon.textContent =
                "✓";


            step.classList.add(
                "completed"
            );


            step.classList.remove(
                "active"
            );

        }

        else if (
            stageIndex === currentIndex
        ) {

            icon.textContent =
                "◉";


            step.classList.add(
                "active"
            );


            step.classList.remove(
                "completed"
            );

        }

        else {

            icon.textContent =
                "○";


            step.classList.remove(
                "active",
                "completed"
            );

        }

    });

}


// ================================
// RESET PROGRESS
// ================================

function resetProgress() {

    progressTitle.textContent =
        "Researching your topic...";


    progressMessage.textContent =
        "Preparing research...";


    progressPercent.textContent =
        "0%";


    progressFill.style.width =
        "0%";


    liveResearchData.innerHTML =
        "";


    document
        .querySelectorAll(
            ".progress-step"
        )
        .forEach(step => {

            step.classList.remove(
                "active",
                "completed"
            );


            step.querySelector(
                ".step-icon"
            ).textContent =
                "○";

        });

}


// ================================
// GET HOSTNAME
// ================================

function getHostname(url) {

    try {

        return new URL(url).hostname;

    }

    catch (error) {

        return url;

    }

}


// ================================
// FORMAT SOURCES
// ================================

function formatSources(sourceList) {

    if (
        !sourceList ||
        sourceList.length === 0
    ) {

        return "<p>No sources found.</p>";

    }


    return sourceList
        .map(
            (url, index) => {

                const cleanUrl =
                    url.replace(
                        /[),.;]+$/,
                        ""
                    );


                let hostname =
                    cleanUrl;


                try {

                    hostname =
                        new URL(
                            cleanUrl
                        ).hostname;

                }

                catch (error) {

                    // Keep original URL

                }


                return `

                    <div class="source-item">

                        <div class="source-number">
                            ${index + 1}
                        </div>

                        <div class="source-info">

                            <div class="source-title">
                                ${escapeHtml(
                                    hostname
                                )}
                            </div>

                            <a
                                href="${encodeURI(
                                    cleanUrl
                                )}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Open source →
                            </a>

                        </div>

                    </div>

                `;

            }
        )
        .join("");

}


// ================================
// ESCAPE HTML
// ================================

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text;


    return div.innerHTML;

}


// ================================
// SHOW ERROR
// ================================

function showError(message) {

    errorBox.textContent =
        message;


    errorBox.classList.remove(
        "hidden"
    );

}