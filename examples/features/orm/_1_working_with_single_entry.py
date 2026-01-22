from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from examples.config import (
    ENGINE,
)
from examples.features.orm._0_create_tables import (
    EmailAddress,
    User,
)

# 0. Clean tables
with Session(ENGINE) as session:
    session.execute(delete(EmailAddress))
    session.execute(delete(User))
    session.commit()

# 1. Insert an entry
with Session(ENGINE) as session:
    # a. Create a new instance
    new_user = User(
        # id is auto-incremented by the database; it is initially set to None.
        first_name="Jax",
        last_name="Doe",
    )

    # b. Add to be inserted
    session.add(new_user)

    # c. Send the pending change to the session WITHOUT committing it yet;
    # this updates the User with a numerical id value.
    session.flush()

    new_email = EmailAddress(
        user_id=new_user.id,
        email_address="jax.doe@example.com",
    )

    # b. Add the user and email address to the session
    session.add(new_email)

    # c. Commit the transaction to persist the changes
    session.commit()


# 2. Select to see the results
def select_all_entries():
    with Session(ENGINE) as session:
        stmt = select(User).options(joinedload(User.email_addresses))  # type: ignore
        # .unique() is required for the 1-to-Many `joinedload` to deduplicate parent objects
        results = session.scalars(stmt).unique().all()

    for result in results:
        emails = [e.email_address for e in result.email_addresses]
        print(f"{result.id} {result.first_name} {result.last_name} {emails}")


select_all_entries()

# 3. Update the entry
with Session(ENGINE) as session:
    # a. Query the user by their identifying information
    user_to_update = (
        session.query(User).filter_by(first_name="Jax", last_name="Doe").first()
    )

    # b. check that an entry was found and update it
    if user_to_update:
        user_to_update.first_name = "Paris"

        if user_to_update.email_addresses:
            user_to_update.email_addresses[0].email_address = "paris.doe@example.com"

        session.commit()
        print("\n--User 'Jax Doe' has been updated to 'Paris Doe'.--")

select_all_entries()

# 4. Delete the entry
with Session(ENGINE) as session:
    # a. Query the user by their identifying information
    user_to_delete = (
        session.query(User).filter_by(first_name="Paris", last_name="Doe").first()
    )

    if user_to_delete:
        # b. Delete the user
        session.delete(user_to_delete)

        # c. Commit the changes to persist the deletion
        session.commit()
        print("\n--User 'Paris Doe' has been deleted from the database.--")

select_all_entries()
