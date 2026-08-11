document.addEventListener("DOMContentLoaded", () => {

    lucide.createIcons();

    const modules = document.querySelectorAll(
        ".z-module-card-disabled"
    );

    const dialog = document.getElementById(
        "comingSoonDialog"
    );

    const message = document.getElementById(
        "comingSoonMessage"
    );

    const closeButton = document.getElementById(
        "comingSoonClose"
    );


    modules.forEach((module) => {

        module.addEventListener("click", (event) => {

            event.preventDefault();

            const moduleName =
                module.dataset.module;

            message.textContent =
                `${moduleName} is coming soon.`;

            dialog.hidden = false;

            closeButton.focus();

        });

    });


    closeButton.addEventListener(
        "click",
        () => {
            dialog.hidden = true;
        }
    );


    dialog.addEventListener(
        "click",
        (event) => {

            if (event.target === dialog) {
                dialog.hidden = true;
            }

        }
    );


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                !dialog.hidden
            ) {
                dialog.hidden = true;
            }

        }
    );

});