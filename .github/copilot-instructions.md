# AI Agent Instructions for Identity Codebase

## Project Overview

**Identity** is a Flask-based web application for managing study sample participant data, participant ID generation, and label printing for biomedical research studies. It integrates with multiple external systems: NHS Digital PDS (Patient Demographics Service), PMI database, CiviCRM, and REDCap for data collection.

## Architecture & Key Components

### Core Technology Stack
- **Framework**: Flask with SQLAlchemy ORM, Celery for async tasks
- **Security**: LDAP-integrated using `lbrc-flask` (shared library)
- **Databases**: Main SQLite DB (local dev) + external bindings to PMI, CiviCRM, ETL systems
- **Async Processing**: Celery workers with RabbitMQ broker (see `identity/celery.py`)

### Major Subsystems

#### 1. **Demographics Processing Pipeline** (`identity/demographics/`)
Multi-stage request workflow with state transitions tracked by datetime flags:
- **Stages**: Upload → Extract → Pre-PMI Lookup → Spine Lookup → Post-PMI Lookup → Create Results → Download
- **State Model**: Located in `identity/demographics/model.py`; requests have `*_datetime` fields marking completion of each stage
- **Task Scheduling**: `schedule_lookup_tasks()` in `identity/demographics/__init__.py` orchestrates Celery tasks based on current state
- **Key Pattern**: State machine driven by presence/absence of datetime fields (e.g., if `data_extracted_datetime` is None, request needs extraction)

#### 2. **ID Generation System** (`identity/model/id.py`)
Multiple provider types (polymorphic SQLAlchemy models):
- **SequentialIdProvider**: Auto-incrementing with configurable prefix + zero-fill
- **LegacyIdProvider**: Random 6-digit IDs with collision checking
- **BioresourceIdProvider** / **PseudoRandomIdProvider**: Study-specific specialized generators
- **Key Pattern**: All inherit from `IdProvider` base; implement `allocate_id()` / `allocate_ids()` methods

#### 3. **Label Printing** (`identity/printing/`)
ZPL (Zebra Programming Language) code generation for label printers:
- **Classes**: `Label`, `SampleLabel`, `SampleBagLabel`, `MedicalNotesLabel`, `AliquotLabel`
- **Printer Config**: Environment vars define printer names (PRINTER_DEV, PRINTER_CVRC_LAB_SAMPLE, etc.)
- **Pattern**: Labels generate ZPL command strings via `get_code()` method, sent to physical printers via socket

#### 4. **Blinding System** (`identity/model/blinding.py`)
Maps study-specific unblind IDs to pseudo-random blind IDs:
- **Models**: `BlindingType` (per-study config) → `Blinding` (individual mappings)
- **Allocation**: `BlindingType.get_blind_id()` allocates new pseudo-random ID on first access

#### 5. **REST API** (`identity/api/`)
- **Auth**: Query-parameter API key validation via `decorators.assert_api_key()`
- **Views**: `identity/api/views/id.py` for ID creation endpoints
- **Validation**: JSON schema validation decorator `validate_json()`

### External System Integrations
- **SMSP**: NHS Patient Demographics Service (SOAP-based via `zeep`); called from `identity/demographics/smsp.py`
- **PMI Database**: Accessed via raw SQL connections in `identity/services/pmi.py`
- **CiviCRM**: External DB bindings at `CIVICRM_DB_URI`
- **REDCap**: Scheduled imports via Celery Beat (cron-like tasks)

## Developer Workflows

### Testing
```bash
pytest                              # Run all tests
pytest -m "not slow"               # Skip slow tests
pytest tests/demographics/         # Test specific subsystem
```
**Test Structure**: `tests/` mirrors source; fixtures in `tests/conftest.py` + custom providers in `tests/faker.py`
**Mocking Pattern**: Use `mock_*` fixtures from `tests/mocks.py` for Celery task mocking (e.g., `mock_schedule_lookup_tasks`)

### Database Migrations
```bash
./manage.py script "Description"   # Create new migration
./manage.py upgrade                # Apply pending migrations
./manage.py version_control        # Initialize DB version control
```
Migrations stored in `alembic/versions/`; use Alembic syntax

### Running the Application
```bash
./app.py                           # Start Flask dev server (port 8000)
celery -A celery_worker.celery worker    # Start background task worker
celery -A celery_worker.celery beat      # Start scheduled task scheduler
```

### Environment Configuration
- Copy `example.env` to `.env` and set required vars
- Critical vars: database URIs, printer addresses, SMSP credentials, Celery broker URL
- **Config Classes**: `identity/config.py` defines `Config` (prod), `TestConfig`, `TestConfigCRSF`

## Code Patterns & Conventions

### Database Models
- Use `from lbrc_flask.database import db` for all model definitions
- Soft-delete pattern: check `deleted_datetime` rather than removing records
- Polymorphic inheritance via `__mapper_args__` (e.g., ID providers, DemographicsRequest subclasses)
- Timestamps: `created_datetime`, `last_updated_datetime` defaults to `datetime.utcnow`

### Celery Tasks
- Define with `@celery.task()` decorator in `identity/demographics/__init__.py`
- Tasks called via `.delay()` for async execution
- Must receive Flask app context: handled via `ContextTask` class in `identity/celery.py`
- **Pattern**: Scheduler task (`schedule_lookup_tasks`) checks state; dispatcher task (`do_lookup_tasks`) schedules work tasks

### Error Handling
- Use `from lbrc_flask.logging import log_exception` for centralized error logging
- Demographics errors save to `dr.error_message` and set `dr.error_datetime`
- SMSP/PMI exceptions caught; requests moved to error state with message

### Templates & UI
- HTML templates in `identity/ui/templates/` and `identity/templates/`
- Flask-Admin integration in `identity/admin.py` for CRUD interfaces
- Email templates in `identity/templates/email/` (rendered via `render_template()`)

### Security
- Extended from `lbrc_flask.security` (LDAP-backed)
- User model in `identity/model/security.py`; users linked to studies via `users_studies` join table
- Role-based access in `identity/admin.py` view classes

## Critical Integration Points

### Study Association
- Users belong to studies via `User.studies` relationship
- All label/blinding operations scoped to studies
- Study ID in configuration maps to external EDGE system

### Request State Transitions
- Always check current state (datetime fields) before scheduling next stage
- Requests can be paused/deleted/errored—always guard against these in task runners
- Use `DemographicsRequest.query.get(id)` then check status before processing

### File Handling
- Uploaded demographics files stored in `FILE_UPLOAD_DIRECTORY`
- Path construction: `identity/demographics/model.py` → `filepath` property handles secure_filename wrapping
- Results saved alongside originals with `_result_` prefix

## Common Tasks for Agents

### Adding a New ID Provider Type
1. Create new class inheriting from `IdProvider` in `identity/model/id.py`
2. Set `__mapper_args__` with unique `polymorphic_identity`
3. Implement `allocate_id()` method
4. Register in admin view (`identity/admin.py`)

### Adding Demographics Processing Stage
1. Add new `*_datetime` field to `DemographicsRequest` in `identity/demographics/model.py`
2. Create Celery task function in `identity/demographics/__init__.py`
3. Add scheduling logic to `schedule_lookup_tasks()` dispatcher
4. Write tests in `tests/demographics/test_scheduling.py`

### Creating API Endpoints
1. Add view function to `identity/api/views/id.py`
2. Decorate with `@assert_api_key()` and `@validate_json(schema)` if needed
3. Register in `identity/api/__init__.py` blueprint
4. Write integration tests using `client` fixture with API key in query params

## Test Fixtures & Helpers

- **`client`**: Flask test client with app context
- **`faker`**: Faker generator with custom providers for Identity-specific data
- **`login(client, faker)`**: Helper that creates user + logs in (from `lbrc_flask.pytest.helpers`)
- **`DemographicsTestHelper`**: Builds complete request workflows with mock data (in `tests/demographics/__init__.py`)
- **Mock fixtures**: `mock_schedule_lookup_tasks`, `mock_extract_data`, etc. prevent actual Celery execution

## References

- **lbrc-flask**: Shared library providing Flask extensions (security, admin, database utilities)
- **Config inheritance**: `BaseConfig` from lbrc-flask; override in `identity/config.py`
- **External docs**: PDS/SMSP details in `documentation/pds/`
- **Requirements**: Pin versions in `requirements.txt` (compiled from `requirements.in`)
