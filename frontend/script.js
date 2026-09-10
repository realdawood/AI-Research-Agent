const researchButton = document.getElementById("researchButton");
const topicInput = document.getElementById("topic");

const loading = document.getElementById("loading");
const results = document.getElementById("results");
const errorBox = document.getElementById("error");

const report = document.getElementById("report");
const feedback = document.getElementById("feedback");
const sources = document.getElementById("sources");


researchButton.addEventListener("click", runResearch);


topicInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {
        runResearch();
    }

});


async function runResearch() {

    const topic = topicInput.value.trim();

    if (!topic) {
        showError("Please enter a research topic.");
        return;
    }


    // Hide previous results/errors
    results.classList.add("hidden");
    errorBox.classList.add("hidden");


    // Show loading
    loading.classList.remove("hidden");

    researchButton.disabled = true;


    try {

        const response = await fetch("/api/research", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                topic: topic
            })

        });


        const text = await response.text();

        console.log("Server response:", text);


        if (!response.ok) {
            throw new Error(text || "Server error");
        }


        const data = JSON.parse(text);


        if (data.error) {
            throw new Error(data.error);
        }


        // Display results
        report.textContent = data.report;

        feedback.textContent = data.feedback;

        sources.innerHTML = formatSources(data.sources);


        // Show results
        results.classList.remove("hidden");


    } catch (error) {

        console.error("Research error:", error);

        showError(
            error.message ||
            "Something went wrong. Please try again."
        );

    } finally {

        loading.classList.add("hidden");

        researchButton.disabled = false;

    }

}


function showError(message) {

    errorBox.textContent = message;

    errorBox.classList.remove("hidden");

}

function formatSources(sourceList) {

    if (!sourceList || sourceList.length === 0) {
        return "<p>No sources found.</p>";
    }

    return sourceList.map((url, index) => {

        const cleanUrl = url.replace(/[),.;]+$/, "");

        let hostname = cleanUrl;

        try {
            hostname = new URL(cleanUrl).hostname;
        } catch (error) {
            // Keep URL if hostname cannot be parsed
        }

        return `
            <div class="source-item">

                <div class="source-number">
                    ${index + 1}
                </div>

                <div class="source-info">

                    <div class="source-title">
                        ${escapeHtml(hostname)}
                    </div>

                    <a
                        href="${encodeURI(cleanUrl)}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Open source →
                    </a>

                </div>

            </div>
        `;

    }).join("");
}

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}