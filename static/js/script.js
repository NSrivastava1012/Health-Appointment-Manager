async function regenerateSummary(
    appointmentId,
    event
) {

    const button =
        event.currentTarget;

    button.disabled = true;

    button.textContent =
        "Generating...";

    try {

        const response = await fetch(
            `/appointments/${appointmentId}/regenerate-summary`,
            {
                method: "POST"
            }
        );

        const data =
            await response.json();

        if (response.ok) {

            button.textContent =
                "✓ Summary Regenerated";

            setTimeout(() => {
                location.reload();
            }, 800);

        } else {

            alert(
                data.error ||
                "Unable to regenerate summary"
            );

            button.disabled = false;

            button.textContent =
                "↻ Regenerate AI Summary";
        }

    } catch (error) {

        console.error(error);

        alert(
            "Something went wrong while regenerating the summary."
        );

        button.disabled = false;

        button.textContent =
            "↻ Regenerate AI Summary";
    }
}