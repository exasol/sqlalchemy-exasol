from sqlalchemy import (
    delete,
    insert,
    join,
    select,
    update,
)

from examples.config import ENGINE
from examples.features.non_orm._0_create_tables import (
    email_address_table,
    user_table,
)

# 1. Clean tables and Insert
with ENGINE.begin() as conn:
    # a. clean tables
    conn.execute(delete(email_address_table))
    conn.execute(delete(user_table))

    # b. Insert user
    conn.execute(insert(user_table).values(first_name="Jax", last_name="Doe"))

    # c. Use a SELECT statement to get the user ID
    select_stmt = select(user_table.c.id).where(
        user_table.c.first_name == "Jax", user_table.c.last_name == "Doe"
    )
    user_id = conn.execute(select_stmt).scalar()

    # d. Insert email_address
    conn.execute(
        insert(email_address_table).values(
            user_id=user_id, email_address="jax.doe@example.com"
        )
    )


# 2. Select with a join
def select_all_entries():
    with ENGINE.connect() as conn:
        j = join(
            user_table,
            email_address_table,
            user_table.c.id == email_address_table.c.user_id,
            isouter=True,
        )
        stmt = select(user_table, email_address_table.c.email_address).select_from(j)

        for row in conn.execute(stmt):
            print(f"{row.id} {row.first_name} {row.last_name} [{row.email_address}]")


select_all_entries()

# 3. Update the entry
with ENGINE.begin() as conn:
    # a. Update User
    conn.execute(
        update(user_table)
        .where(user_table.c.first_name == "Jax")
        .values(first_name="Paris")
    )
    # b. Update EmailAddress
    conn.execute(
        update(email_address_table)
        .where(email_address_table.c.email_address == "jax.doe@example.com")
        .values(email_address="paris.doe@example.com")
    )

# 4. Delete the entry
with ENGINE.begin() as conn:
    # a. Get the IDs of the users you want to delete
    user_ids_stmt = select(user_table.c.id).where(user_table.c.first_name == "Paris")
    user_ids = conn.execute(user_ids_stmt).scalars().all()

    if user_ids:
        # b. Delete related emails first
        conn.execute(
            delete(email_address_table).where(
                email_address_table.c.user_id.in_(user_ids)
            )
        )

        # c. Delete the user
        conn.execute(delete(user_table).where(user_table.c.id.in_(user_ids)))
