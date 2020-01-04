# identity

Print study sample, participant and bag labels

## Demographics Web Service

This application uses the NHS Digital Patient Demographics Service (PDS).  See
the `pds` directory in the `documentation` directory for details.

The web services that this application utilises is maintained by Joss Markham (Joss.Markham@orionhealth.com)

## Installation and Running

1. Download the code from github

```bash
git clone git@github.com:LCBRU/identity.git
```

2. Install the requirements

Go to the `identity` directory and type the command:

```bash
sudo apt-get install libldap2-dev
sudo apt-get install libsasl2-dev

pip install -r requirements.txt
```

3. Create the database using

Staying in the `identity` directory and type the command:

```bash
./manage_dev.py version_control
./manage_dev.py upgrade
```

4. Run the application

Staying in the `identity` directory and type the command:

```bash
./dev.py
```

5. Start Celery Worker

This application uses Celery to run background tasks.
To start Celery run the following command from the `identity`
directory:

```
celery -A celery_worker.celery worker
```

5. Start Celery Beat

This application uses Celery to run background tasks.
To start Celery run the following command from the `identity`
directory:

```
celery -A celery_worker.celery beat
```

## Development

### Testing

To test the application, run the following command from the project folder:

```bash
pytest
```

### Database Schema Amendments

#### Create Migration

To create a migration run the command

```bash
./manage.py script "{Description of change}"
```

You will then need to change the newly-created script created in the
`migrations` directory to make the necessary upgrade and downgrade
changes.

#### Installation

To initialise the database run the commands:

```bash
manage.py version_control
manage.py upgrade
```

#### Upgrade

To upgrade the database to the current version, run the command:

```bash
manage.py upgrade
```
