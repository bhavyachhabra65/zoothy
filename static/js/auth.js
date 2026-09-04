function togglePassword(inputId, button) {

    const input = document.getElementById(
        inputId
    );

    if (!input) {
        return;
    }

    const isPassword =
        input.type === "password";

    input.type =
        isPassword
            ? "text"
            : "password";

    button.setAttribute(
        "aria-label",
        isPassword
            ? "Hide password"
            : "Show password"
    );
}