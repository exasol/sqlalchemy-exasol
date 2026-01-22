from sqlalchemy import (
    delete,
)
from sqlalchemy.orm import (
    Session,
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

# 1. Perform a simple insert
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
