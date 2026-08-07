document.getElementById("analyzeBtn").addEventListener("click", async () => {

    const username = document.getElementById("username").value.trim();

    if (username === "") {
        alert("Please enter a username");
        return;
    }

    try {

        const response = await fetch("https://fake-influencer-api.onrender.com/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username
            })
        });

        const data = await response.json();

        // ---------- NOT FOUND ----------
        if (data.prediction === "NOT FOUND") {

            document.getElementById("result").innerHTML = `
                <h3>
                    <span class="notfound-badge">⚪ Not Found</span>
                </h3>

                <p>
                    <img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png"
                    width="20"
                    style="vertical-align:middle;margin-right:8px;">

                    <b>${data.username}</b>
                </p>

                <p style="color:#ff6b6b;font-weight:bold;">
                    Username not found in our dataset.
                </p>
            `;

        }

        // ---------- GENUINE ----------
        else if (data.prediction === "Genuine Influencer") {

            document.getElementById("result").innerHTML = `
                <h3>
                    <span class="genuine-badge">🟢 Genuine</span>
                </h3>

                <p>
                    <img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png"
                    width="20"
                    style="vertical-align:middle;margin-right:8px;">

                    <b>${data.username}</b>
                </p>

                <p><b>Followers:</b> ${data.followers}</p>

                <p><b>Posts:</b> ${data.posts}</p>

                <p><b>Average Likes:</b> ${data.avg_likes}</p>
            `;

        }

        // ---------- FAKE ----------
        else {

            document.getElementById("result").innerHTML = `
                <h3>
                    <span class="fake-badge">🔴 Fake</span>
                </h3>

                <p>
                    <img src="https://cdn-icons-png.flaticon.com/512/2111/2111463.png"
                    width="20"
                    style="vertical-align:middle;margin-right:8px;">

                    <b>${data.username}</b>
                </p>

                <p><b>Followers:</b> ${data.followers}</p>

                <p><b>Posts:</b> ${data.posts}</p>

                <p><b>Average Likes:</b> ${data.avg_likes}</p>
            `;

        }

    } catch (error) {

        document.getElementById("result").innerHTML =
            `<p style="color:red;">Error: ${error.message}</p>`;

    }

});