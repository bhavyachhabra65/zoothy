class PrintService {

    static AMOUNT_WORDS_MAX_CHARS = 54;

    static splitAmountWords(element) {

        if (!element) {
            return;
        }

        const text = element.textContent
            .trim()
            .replace(/\s+/g, " ");

        if (text.length <= this.AMOUNT_WORDS_MAX_CHARS) {
            return;
        }

        let splitIndex = text.lastIndexOf(" ", this.AMOUNT_WORDS_MAX_CHARS);

        if (splitIndex === -1) {
            splitIndex = this.AMOUNT_WORDS_MAX_CHARS;
        }

        const line1 = text.substring(0, splitIndex).trim();
        const line2 = text.substring(splitIndex).trim();

        element.innerHTML = `
            <div>${line1}</div>
            <div>${line2}</div>
        `;
    }


    static async print(form) {

        const response = await fetch(form.action, {
            method: form.method,
            body: new FormData(form)
        });

        if (!response.ok) {
            throw await response.json();
        }

        const html = await response.text();

        const printWindow = window.open("", "_blank");

        printWindow.document.open();
        printWindow.document.write(html);
        printWindow.document.close();
    }

}