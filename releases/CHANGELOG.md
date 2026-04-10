# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- ...

### Changed

- ...

### Deprecated

- ...

### Removed

- ...

### Fixed

- ...

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

[unreleased]: https://github.com/FJrodafo/MetaBot/compare/0.2.0...HEAD
[0.2.0]: https://github.com/FJrodafo/MetaBot/releases/tag/0.2.0
[0.1.3]: https://github.com/FJrodafo/MetaBot/releases/tag/0.1.3
[0.1.2]: https://github.com/FJrodafo/MetaBot/releases/tag/0.1.2
[0.0.2]: https://github.com/FJrodafo/MetaBot/releases/tag/0.0.2
[0.0.1]: https://github.com/FJrodafo/MetaBot/releases/tag/0.0.1
