# Architecture

Project Structure

apps/
    cheque/

core/

static/

templates/

docker/

docs/

Responsibilities

apps/
Contains all business modules.

Example

apps/
    cheque/
    invoice/
    receipt/

core/
Application initialization.

Blueprint registration.

Configuration.

static/

css/

js/

images/

templates/

base.html

Shared Layout

Every page extends

base.html

All common navigation, layout and assets are defined there.

JavaScript

Each page has

page.js

Business logic lives inside

Service classes

Example

PrintService

InvoiceService

ChequeService

Routes

Routes should

- validate
- call services
- render

Routes should NOT contain business logic.