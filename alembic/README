Generic single-database configuration.

Set to install:
1. Install "alembic" in your local development
2. Run this command to create new versions based on schema changes
    ```bash
        alembic revision --autogenerate -m "<Your message>"
    ```
3. Use this command to upgrade or downgrade revision
    ```bash
        alembic upgrade head
    ```
    Or
    ```bash
        alembic downgrade base
    ```
4. [Optional] Using this command to check all revisions
    ``` bash
        alembic history
    ```
**Note**: If this is the first time you want to deploy your schema.
If you have some tables already in the database before and you supply
a new metadata or a None metadata as Terminal suggested in the comments,
you will see this behavior because alembic knows that based on that metadata,
those tables should not be in the database, so it will try to delete those.