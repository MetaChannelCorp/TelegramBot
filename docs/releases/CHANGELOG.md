# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Company pre-selection in template mode — before filling in the template, the user searches for and selects the company to assign to all contacts in the batch.
- Option to create a new company directly from the search result if no match is found, both in guided mode and template mode.

### Changed

- Project modularized into separate files: `main.py`, `config.py`, `odoo_client.py`, `helpers.py`, `handlers/comandos.py`, and `handlers/conversacion.py`.

### Deprecated

- ...

### Removed

- ...

### Fixed

- `OdooClient.crear_empresa` now checks for an existing company with the exact same name before creating a new one, preventing duplicate entries in Odoo.

### Security

- ...

## [0.2.0] - 2026/04/10

### Added

- Guided mode to add contacts and companies to Odoo CRM field by field via conversation flow.
- Template mode to add one or multiple contacts at once using a structured text format.
- Automatic company lookup when adding a contact — if the company does not exist, the user is prompted to create it on the spot.
- `/nuevo` command with three options: guided contact, guided company, and template mode.
- `/recientes` command that lists the last 5 contacts added to the CRM.
- `/estado` command that checks the Odoo connection and returns the URL, database and user.
- `/cancelar` command to cancel any ongoing operation.
- `OdooClient` class handling XML-RPC authentication and all CRM operations.

## [0.1.3] - 2026/03/27

### Added

- The `requirements.txt` file is missing in the release workflow.

## [0.1.2] - 2026/03/27

### Added

- Command that checks the Odoo connection, returns the URL, database and user.

## [0.0.2] - 2026/03/27

### Added

- Python venv (virtual environment).

### Fixed

- The `.env.example` file is missing in the release workflow.

## [0.0.1] - 2026/03/27

### Added

- Initial files.

[unreleased]: https://github.com/MetaChannelCorp/TelegramBot/compare/0.2.0...HEAD
[0.2.0]: https://github.com/MetaChannelCorp/TelegramBot/releases/tag/0.2.0
[0.1.3]: https://github.com/MetaChannelCorp/TelegramBot/releases/tag/0.1.3
[0.1.2]: https://github.com/MetaChannelCorp/TelegramBot/releases/tag/0.1.2
[0.0.2]: https://github.com/MetaChannelCorp/TelegramBot/releases/tag/0.0.2
[0.0.1]: https://github.com/MetaChannelCorp/TelegramBot/releases/tag/0.0.1
