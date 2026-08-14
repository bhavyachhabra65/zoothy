Basic code: For sample:

Cheque.html

{% extends "base.html" %}

{% block title %}Print Cheque{% endblock %}

{% block styles %}
<link rel="stylesheet"
      href="{{ url_for('static', filename='css/cheque.css') }}">
{% endblock %}

{% block content %}

<div class="z-page-heading">

    <h1 class="z-page-heading-title">
        Print Cheque
    </h1>

</div>

<form class="z-form" id="chequeForm" method="POST" action="{{ url_for('cheque.print_cheque') }}">

    <div class="z-row">

        <div class="z-form-group z-col-2">

            <label class="z-label">

                Bank

            </label>

        <select class="z-input" name="bank" required>

            <option value="">Select Bank</option>

            <option value="sbi">State Bank of India</option>
            <option value="hdfc">HDFC Bank</option>
            <option value="icici">ICICI Bank</option>
            <option value="axis">Axis Bank</option>
            <option value="kotak">Kotak Mahindra Bank</option>
            <option value="pnb">Punjab National Bank</option>
            <option value="bob">Bank of Baroda</option>
            <option value="boi">Bank of India</option>
            <option value="union">Union Bank</option>
            <option value="federal">Federal Bank</option>
            <option value="indusind">IndusInd Bank</option>
            <option value="bandhan">Bandhan Bank</option>
            <option value="ausmallfinance">AU Small Finance Bank</option>
            <option value="uco">UCO Bank</option>

        </select>
            

        </div>

        <div class="z-form-group z-col-1">

            <label class="z-label">

                Date

            </label>

            <input
                type="date"
                id="date"
                class="z-input"
                name="date"
                min="1900-01-01"
                max="2099-12-31"
                required>

        </div>

    </div>

    <div class="z-form-group z-field-full">

        <label class="z-label">
            Pay To
        </label>

        <input
            type="text"
            maxlength="100"
            class="z-input"
            name="pay_to"
            autocomplete="off"
            required>

    </div>

    <div class="z-row z-row-bottom">

        <div class="z-form-group z-field-medium">

            <label class="z-label">
                Amount
            </label>

            <input
                type="number"
                id="amount"
                class="z-input"
                name="amount"
                step="0.01"
                min="0.01"
                max="999999999.99"
                autocomplete="off"
                required>

        </div>

        <div class="z-form-group z-checkbox-group">

            <label class="z-label">
                &nbsp;
            </label>

            <label class="z-checkbox">

                <input
                    type="checkbox"
                    id="acPayee"
                    name="ac_payee_only">

                <span>A/C Payee Only</span>

            </label>

        </div>

    </div>

    <div class="z-actions">

        <button
            type="submit"
            id="printButton"
            class="z-button">

            Print

        </button>

    </div>

</form>

{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/print-service.js') }}"></script>
<script src="{{ url_for('static', filename='js/cheque.js') }}"></script>
{% endblock %}



Cheque.css
*{
    box-sizing:border-box;
}

body{

    margin:0;

    background:white;

    font-family:Arial,sans-serif;

}

.cheque{

    position:relative;

    width:190mm;

    height:80mm;

    margin:auto;

}

.field{

    position:absolute;

    white-space:nowrap;

    font-size:12pt;

}

.amount{

    font-weight:bold;

}

@page{

    margin:0;

}

.ac-payee-box {
    width: 25mm;
    text-align: center;
    font-size: 10px;
    font-weight: 600;
}

.ac-payee-box .line {
    border-top: 1px solid #000;
    margin: 2px 0;
}



@media print{

    body{

        margin:0;

    }

}


#amountWords > div + div {
    margin-top: 3mm;
    margin-left: -17mm;
}

@media (min-width: 460px) {
    .z-checkbox-group {
    margin-bottom: 13px;
    display: flex;
    flex-direction: column;
    }

}

@media (max-width: 460px) {

    .z-container {
        padding: var(--z-space-4);
    }

    .z-row {
        flex-direction: column;
        align-items: stretch;
        gap: var(--z-space-4);
    }

    .z-col-1,
    .z-col-2,
    .z-col-3,
    .z-field-small,
    .z-field-medium,
    .z-field-large,
    .z-field-full {
        width: 100%;
        max-width: 100%;
        flex: none;
    }

    .z-actions .z-button {
        width: 100%;
    }

}


Components.css:
/* ==========================================================
   HEADER
========================================================== */

.z-page-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: var(--z-space-6);

    margin-bottom: var(--z-space-7);

}

/* ==========================================================
   PAGE HEADING
========================================================== */

.z-page-heading {

    display: flex;

    align-items: center;

    gap: var(--z-space-4);

    margin-bottom: var(--z-space-7);

}

.z-page-heading::before {

    content: "";

    width: 5px;

    height: 56px;

    flex: 0 0 5px;

    background: linear-gradient(
        to bottom,
        var(--z-primary),
        #4F8CFF
    );

    border-radius: 999px;

    box-shadow:
        0 2px 8px rgba(37, 99, 235, 0.18);

}

.z-page-heading-title {

    margin: 0;

    font-size: var(--z-font-title-size);

    font-weight: var(--z-font-title-weight);

    line-height: var(--z-line-height-title);

    color: var(--z-text);

}


/* ==========================================================
   BRAND
========================================================== */

.z-brand {

    position: relative;

    display: flex;

    flex-direction: column;

    justify-content: center;

    padding-left: var(--z-space-5);

}


/* ==========================================================
   BRAND ACCENT LINE
========================================================== */

.z-brand::before {

    content: "";

    position: absolute;

    left: 0;
    top: 50%;

    width: 5px;
    height: 56px;

    transform: translateY(-50%);

    background: linear-gradient(
        to bottom,
        var(--z-primary),
        #4F8CFF
    );

    border-radius: 999px;

    box-shadow:
        0 2px 8px rgba(37, 99, 235, 0.18);

}


/* ==========================================================
   BRAND NAME
========================================================== */

.z-brand-name {

    display: inline-block;

    color: var(--z-text);

    font-size: 32px;

    font-weight: 700;

    line-height: 1.1;

    text-decoration: none;

    transition: color var(--z-transition);

}

.z-brand-name:hover {

    color: var(--z-primary);

}


/* ==========================================================
   BRAND TAGLINE
========================================================== */

.z-brand-tagline {

    margin-top: var(--z-space-2);

    font-size: 18px;

    line-height: 1.4;

    color: var(--z-text-secondary);

}


/* ==========================================================
   HEADER NAVIGATION
========================================================== */

.z-page-header-nav {

    display: flex;

    align-items: center;

    gap: var(--z-space-6);

}

.z-page-header-nav a {

    color: var(--z-text-secondary);

    font-size: var(--z-font-body-size);

    font-weight: 500;

    text-decoration: none;

    transition: color var(--z-transition);

}

.z-page-header-nav a:hover {

    color: var(--z-primary);

}


/* ==========================================================
   TITLE
========================================================== */

/* .z-title {

    font-size: var(--z-font-title-size);

    font-weight: var(--z-font-title-weight);

    line-height: var(--z-line-height-title);

    margin-bottom: 36px;

} */


/* ==========================================================
   FORM
========================================================== */

.z-form {

    display: flex;

    flex-direction: column;

    gap: var(--z-field-gap);

}


/* ==========================================================
   FORM GROUP
========================================================== */

.z-form-group {

    display: flex;

    flex-direction: column;

    gap: var(--z-label-gap);

}


/* ==========================================================
   LABEL
========================================================== */

.z-label {

    font-size: var(--z-font-label-size);

    font-weight: var(--z-font-label-weight);

}


/* ==========================================================
   INPUT
========================================================== */

.z-input {

    width: 100%;

    height: var(--z-input-height);

    padding: 0 var(--z-space-3);

    border: var(--z-border-width) solid var(--z-border);

    border-radius: var(--z-radius-md);

    background: var(--z-surface);

    font-size: var(--z-font-body-size);

    transition: var(--z-transition);

}

.z-input:hover {

    border-color: #D1D5DB;

}

.z-input:focus {

    border-color: var(--z-primary);

}


/* ==========================================================
   CHECKBOX
========================================================== */

.z-checkbox {

    display: flex;

    align-items: center;

    gap: var(--z-space-2);

    cursor: pointer;

    width: fit-content;

}

.z-checkbox input[type="checkbox"] {

    appearance: auto;
    -webkit-appearance: checkbox;

    width: 18px;
    height: 18px;

    accent-color: var(--z-primary);

    cursor: pointer;

}

.z-checkbox-label {

    font-size: var(--z-font-body-size);

    user-select: none;

}


/* ==========================================================
   BUTTON
========================================================== */

.z-button {

    min-width: 190px;

    height: var(--z-button-height);

    padding: 0 var(--z-space-5);

    background: var(--z-primary);

    color: white;

    border-radius: var(--z-radius-md);

    transition: var(--z-transition);

}

.z-button:hover {

    background: var(--z-primary-hover);

}


/* ==========================================================
   ACTIONS
========================================================== */

.z-actions {

    margin-top: var(--z-space-4);

}


/* ==========================================================
   MODULE CARD
========================================================== */

.z-module-card {

    width: 220px;
    height: 180px;

    display: flex;

    flex-direction: column;

    justify-content: center;

    align-items: center;

    gap: var(--z-space-4);

    background: var(--z-surface);

    border: var(--z-border-width) solid var(--z-border);

    border-radius: var(--z-radius-lg);

    cursor: pointer;

    transition:
        transform var(--z-transition),
        box-shadow var(--z-transition),
        border-color var(--z-transition),
        background var(--z-transition);

}

.z-module-card:hover {

    transform: translateY(-2px);

    border-color: var(--z-primary);

    box-shadow: var(--z-shadow-md);

}

.z-module-card:active {

    transform: translateY(0);

}


/* ==========================================================
   MODULE ICON
========================================================== */

.z-module-icon {

    width: 56px;
    height: 56px;

    display: flex;

    align-items: center;
    justify-content: center;

    color: var(--z-primary);

}

.z-module-icon svg {

    width: 40px;
    height: 40px;

}


/* ==========================================================
   MODULE TITLE
========================================================== */

.z-module-title {

    font-size: 18px;

    font-weight: 600;

    color: var(--z-text);

    text-align: center;

}


/* ==========================================================
   MODULE GRID
========================================================== */

.z-module-grid {

    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));

    gap: var(--z-space-4);

    justify-items: center;

}


/* ==========================================================
   RESPONSIVE — TABLET
========================================================== */

@media (max-width: 900px) {

    .z-page-header {

        gap: var(--z-space-5);

    }

    .z-page-header-nav {

        gap: var(--z-space-4);

    }

}


/* ==========================================================
   RESPONSIVE — MOBILE
========================================================== */

@media (max-width: 680px) {

    .z-page-header {

        align-items: flex-start;

        flex-direction: column;

        gap: var(--z-space-5);

    }

    .z-page-header-nav {

        width: 100%;

        margin-left: 0;

        gap: var(--z-space-5);

    }

}


/* ==========================================================
   RESPONSIVE — SMALL MOBILE
========================================================== */

@media (max-width: 440px) {

    .z-brand-name {

        font-size: 30px;

    }

    .z-brand-tagline {

        font-size: 17px;

    }

    .z-page-header-nav {

        gap: var(--z-space-4);

    }

}


variable.css
/* ==========================================================
   Zoothy Design Tokens v1.0
   ----------------------------------------------------------
   DO NOT USE HARD-CODED VALUES IN CSS.
   Always use these variables.
========================================================== */

:root {

   --z-page-max-width-wide: 1280px;

    /* ======================================================
       COLORS
    ====================================================== */

    --z-primary: #2563EB;
    --z-primary-hover: #1D4ED8;

    --z-background: #FCFCFD;
    --z-surface: #FFFFFF;

    --z-text: #111827;
    --z-text-secondary: #6B7280;

    --z-border: #E5E7EB;

    --z-success: #16A34A;
    --z-warning: #D97706;
    --z-danger: #DC2626;


    /* ======================================================
       TYPOGRAPHY
    ====================================================== */

    --z-font-family: "Inter", sans-serif;

    /* Page Title */
    --z-font-title-size: 32px;
    --z-font-title-weight: 700;

    /* Labels */
    --z-font-label-size: 14px;
    --z-font-label-weight: 600;

    /* Body / Inputs / Buttons */
    --z-font-body-size: 16px;
    --z-font-body-weight: 400;

    /* Line Heights */
    --z-line-height-title: 1.2;
    --z-line-height-body: 1.6;


    /* ======================================================
       FIELD WIDTHS
    ====================================================== */

    --z-field-small: 180px;
    --z-field-medium: 320px;
    --z-field-large: 480px;
    --z-field-full: 100%;


    /* ======================================================
       COMPONENT HEIGHTS
    ====================================================== */

    --z-input-height: 48px;
    --z-button-height: 48px;


    /* ======================================================
       SPACING (8px Grid)
    ====================================================== */

    --z-space-1: 4px;
    --z-space-2: 8px;
    --z-space-3: 16px;
    --z-space-4: 24px;
    --z-space-5: 32px;
    --z-space-6: 40px;
    --z-space-7: 48px;
    --z-space-8: 64px;
    --z-space-9: 80px;


    /* ======================================================
       LAYOUT
    ====================================================== */

    --z-page-max-width: 960px;

    --z-label-gap: 8px;

    --z-field-gap: 16px;

    --z-section-gap: 48px;


    /* ======================================================
       BORDER RADIUS
    ====================================================== */

    --z-radius-sm: 6px;
    --z-radius-md: 10px;
    --z-radius-lg: 14px;


    /* ======================================================
       BORDERS
    ====================================================== */

    --z-border-width: 1px;


    /* ======================================================
       SHADOWS
    ====================================================== */

    --z-shadow-sm: 0 2px 6px rgba(15, 23, 42, 0.04);

    --z-shadow-md: 0 8px 20px rgba(15, 23, 42, 0.06);


    /* ======================================================
       ANIMATION
    ====================================================== */

    --z-transition-fast: 150ms ease;

    --z-transition: 180ms ease;

    --z-transition-slow: 250ms ease;

}