document.addEventListener("DOMContentLoaded", () => {

    const dateInput = document.getElementById("date");

    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split("T")[0];
    }    

    const form = document.getElementById("chequeForm");

    if (!form) {
        return;
    }


    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        try {

            await PrintService.print(form);

        } catch (error) {

            alert(error.message);

        }

    });

});

