const doctorSelect =
    document.getElementById("doctor");

const dateInput =
    document.getElementById("appointment-date");

const slotSelect =
    document.getElementById("slot");

const message =
    document.getElementById("message");


async function loadSlots() {

    const doctorId = doctorSelect.value;
    const date = dateInput.value;

    if (!doctorId || !date) {
        return;
    }

    slotSelect.innerHTML =
        "<option>Loading...</option>";

    const response = await fetch(
        `/appointments/slots?doctor_id=${doctorId}&date=${date}`
    );

    const data = await response.json();

    slotSelect.innerHTML = "";

    if (!data.available) {

        slotSelect.innerHTML =
            "<option>Doctor is on leave</option>";

        return;
    }

    if (data.slots.length === 0) {

        slotSelect.innerHTML =
            "<option>No slots available</option>";

        return;
    }

    data.slots.forEach(slot => {

        const option =
            document.createElement("option");

        option.value =
            `${slot.start}|${slot.end}`;

        option.textContent =
            `${slot.start} - ${slot.end}`;

        slotSelect.appendChild(option);

    });
}


doctorSelect.addEventListener(
    "change",
    loadSlots
);

dateInput.addEventListener(
    "change",
    loadSlots
);


async function bookAppointment() {

    const doctorId =
        document.getElementById("doctor").value;

    const date =
        document.getElementById("appointment-date").value;

    const slot =
        document.getElementById("slot").value;

    const symptoms =
        document.getElementById("symptoms").value.trim();

    const message =
        document.getElementById("message");


    // -----------------------------------------
    // VALIDATION
    // -----------------------------------------

    if (!doctorId) {

        message.textContent =
            "Please select a doctor.";

        message.className =
            "booking-message error";

        return;
    }


    if (!date) {

        message.textContent =
            "Please select an appointment date.";

        message.className =
            "booking-message error";

        return;
    }


    if (!slot || slot.includes("Select") ||
        slot.includes("No slots") ||
        slot.includes("leave")) {

        message.textContent =
            "Please select an available time slot.";

        message.className =
            "booking-message error";

        return;
    }


    if (!symptoms) {

        message.textContent =
            "Please enter your symptoms.";

        message.className =
            "booking-message error";

        return;
    }


    const [
        startTime,
        endTime
    ] = slot.split("|");


    // -----------------------------------------
    // SHOW LOADING
    // -----------------------------------------

    message.textContent =
        "Booking appointment...";

    message.className =
        "booking-message";


    try {

        const response =
            await fetch(
                "/appointments/book",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        doctor_id: doctorId,

                        appointment_date: date,

                        start_time: startTime,

                        end_time: endTime,

                        symptoms: symptoms

                    })
                }
            );


        const data =
            await response.json();


        // -----------------------------------------
        // SUCCESS
        // -----------------------------------------

        if (response.ok && data.success) {

            message.textContent =
                "✓ Booking confirmed successfully.";

            message.className =
                "booking-message success";


            // Refresh available slots
            await loadSlots();


            // Clear symptoms
            document.getElementById(
                "symptoms"
            ).value = "";

            return;
        }


        // -----------------------------------------
        // DOCTOR ON LEAVE
        // -----------------------------------------

        if (data.status === "rejected") {

            message.textContent =
                "✕ Booking rejected. " +
                "The doctor is on leave on this date.";

            message.className =
                "booking-message error";

            return;
        }


        // -----------------------------------------
        // SLOT ALREADY BOOKED
        // -----------------------------------------

        message.textContent =
            data.message ||
            data.error ||
            "Unable to book appointment.";

        message.className =
            "booking-message error";

    }

    catch (error) {

        console.error(
            "BOOKING ERROR:",
            error
        );

        message.textContent =
            "Something went wrong while booking the appointment.";

        message.className =
            "booking-message error";
    }
}