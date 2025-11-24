let CURRENT_SCORE_DATA = null;
let CURRENT_TRANSCRIPT = "";

async function sendForScoring() {
    const text = document.getElementById("inputText").value.trim();
    CURRENT_TRANSCRIPT = text;

    const btn = document.getElementById("scoreBtn");
    const loader = document.getElementById("loader");

    // Show loader + disable button
    btn.disabled = true;
    loader.classList.remove("hidden");
    document.getElementById("output").innerHTML = "";
    document.getElementById("downloadBtn").classList.add("hidden");

    try {
        const response = await fetch("http://127.0.0.1:5000/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript: text })
        });

        const data = await response.json();
        CURRENT_SCORE_DATA = data;

        let html = `<h2>Final Score: ${data.final_score.toFixed(2)}</h2>`;
        html += `<h3>Score Breakdown:</h3>`;

        data.details.forEach(item => {
            html += `
                <div class="box">
                    <strong>${item.metric}</strong><br>
                    Score: ${item.score.toFixed(2)}<br>
                    Weight: ${item.weight}<br>
                    Feedback: ${item.feedback}
                </div>
            `;
        });

        document.getElementById("output").innerHTML = html;

        // Show PDF button
        document.getElementById("downloadBtn").classList.remove("hidden");

    } catch (err) {
        document.getElementById("output").innerHTML =
            `<p style='color:red;'>Error connecting to backend.</p>`;
    }

    // Hide loader + enable button
    loader.classList.add("hidden");
    btn.disabled = false;
}


// ================================
// DOWNLOAD PDF FUNCTION
// ================================

function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    let y = 15;

    // Title
    doc.setFontSize(20);
    doc.text("Nirmaan AI Scoring Report", 10, y);
    y += 10;

    // Timestamp
    const date = new Date().toLocaleString();
    doc.setFontSize(10);
    doc.text(`Generated on: ${date}`, 10, y);
    y += 10;

    // Transcript
    doc.setFontSize(14);
    doc.text("Original Transcript:", 10, y);
    y += 8;

    doc.setFontSize(11);
    const lines = doc.splitTextToSize(CURRENT_TRANSCRIPT, 180);
    lines.forEach(line => {
        if (y > 275) { doc.addPage(); y = 15; }
        doc.text(line, 10, y);
        y += 6;
    });

    y += 8;

    // Final Score
    if (y > 265) { doc.addPage(); y = 15; }
    doc.setFontSize(14);
    doc.text(`Final Score: ${CURRENT_SCORE_DATA.final_score.toFixed(2)}`, 10, y);
    y += 10;

    // Breakdown
    doc.setFontSize(13);
    doc.text("Score Breakdown:", 10, y);
    y += 8;

    doc.setFontSize(11);

    CURRENT_SCORE_DATA.details.forEach(detail => {
        if (y > 265) { doc.addPage(); y = 15; }

        doc.text(`Metric: ${detail.metric}`, 10, y); y += 6;
        doc.text(`Score: ${detail.score.toFixed(2)} | Weight: ${detail.weight}`, 10, y); y += 6;

        const wrapped = doc.splitTextToSize(`Feedback: ${detail.feedback}`, 180);
        wrapped.forEach(line => {
            if (y > 270) { doc.addPage(); y = 15; }
            doc.text(line, 10, y);
            y += 6;
        });

        y += 6;
    });

    doc.save("Nirmaan_AI_Score_Report.pdf");
}
