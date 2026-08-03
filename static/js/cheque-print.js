
document.addEventListener("DOMContentLoaded", () => {
    const amountWords = document.getElementById("amountWords");
    PrintService.splitAmountWords(amountWords);
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            window.print();
        });
    }); 
    window.onafterprint = () => window.close();
});