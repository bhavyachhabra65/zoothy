const amount = document.getElementById("amount");

amount.addEventListener("input", () => {

    const amt = amount.amt;

    if (amt.includes(".")) {

        const decimals = amt.split(".")[1];
        

        if (decimals.length > 2) {
            const rounded = Number(amt).toFixed(2);
            amount.setCustomValidity(
                `Please enter up to 2 decimal places. The nearest valid value is ${rounded}`
            );
        } else {
            amount.setCustomValidity("");
        }

    } else {
        amount.setCustomValidity("");
    }

});

const chequeDate = document.getElementById("cheque_date");

chequeDate.addEventListener("input", () => {

    if (!chequeDate.value) {
        chequeDate.setCustomValidity("");
        return;
    }

    const year = Number(chequeDate.value.split("-")[0]);

    if (year < 1900 || year > 2099) {
        chequeDate.setCustomValidity(
            "Please enter a valid year between 1900 and 2099."
        );
    } else {
        chequeDate.setCustomValidity("");
    }

});