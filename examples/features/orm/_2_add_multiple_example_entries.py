from sqlalchemy import (
    delete,
    insert,
    select,
    tuple_,
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

# 1. Perform a bulk insert
bulk_data = [
    {
        "first_name": "Lux",
        "last_name": "Noceda",
        "email_addresses": ["fantasy4l!fe@hotmail.com", "lux.noceda@hexside.com"],
    },
    {
        "first_name": "Eda",
        "last_name": "Clawthorne",
        "email_addresses": ["eda.clawthorne@owlhouse.com"],
    },
    {
        "first_name": "Raine",
        "last_name": "Whispers",
        "email_addresses": ["bard.coven@community.com"],
    },
]
with Session(ENGINE) as session:
    # a. We do NOT use options that implicitly rely on RETURNING, as the Exasol dialect
    # doesn't support RETURNING. For more details, see the `Inserting Multiple Entries`
    # page.
    session.execute(insert(User), bulk_data)
    # Flush to make the rows available for querying in this transaction
    session.flush()

    # b. Select back the IDs by matching first/last name to get the newly created IDs
    names = [(d["first_name"], d["last_name"]) for d in bulk_data]
    stmt = select(User.id, User.first_name, User.last_name).where(
        tuple_(User.first_name, User.last_name).in_(names)
    )
    user_map = {(u.first_name, u.last_name): u.id for u in session.execute(stmt)}

    # c. Build and insert to EmailAddress
    email_payload = []
    for entry in bulk_data:
        user_id = user_map.get((entry["first_name"], entry["last_name"]))
        for email in entry["email_addresses"]:
            email_payload.append({"user_id": user_id, "email_address": email})

    session.execute(insert(EmailAddress), email_payload)

    # d. Commit everything at once
    session.commit()

# 2. Check to see what data was added
with Session(ENGINE) as session:
    stmt = select(User).options(joinedload(User.email_addresses))  # type: ignore
    # .unique() is required for the 1-to-Many `joinedload` to deduplicate parent objects
    results = session.scalars(stmt).unique().all()

for result in results:
    emails = [e.email_address for e in result.email_addresses]
    print(f"{result.id} {result.first_name} {result.last_name} {emails}")
