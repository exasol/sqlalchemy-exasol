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

# 1. Insert multiple entries
data = [
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
    # a. Create new instances
    # Note: We do NOT use options that implicitly rely on RETURNING, as the Exasol dialect
    # doesn't support RETURNING. For more details, see:
    #    https://exasol.github.io/sqlalchemy-exasol/master/user_guide/examples/orm/insert_multiple_entries.html
    user_1 = User(first_name="Amity", last_name="Blight")
    user_2 = User(first_name="Willow", last_name="Park")

    # b. Adds multiple entries to be inserted
    session.add_all([user_1, user_2])

    # c. Add more entries using a dictionary
    session.execute(insert(User), data)

    # d. Sends the pending changes to the session WITHOUT committing it yet;
    # this updates Users with id values.
    session.flush()

    # e. Retrieve user ids
    names = [(d["first_name"], d["last_name"]) for d in data]
    stmt = select(User.id, User.first_name, User.last_name).where(
        tuple_(User.first_name, User.last_name).in_(names)
    )
    user_map = {(u.first_name, u.last_name): u.id for u in session.execute(stmt)}

    # f. Insert emails for dictionary-based data
    email_payload = []
    for entry in data:
        user_id = user_map.get((entry["first_name"], entry["last_name"]))
        for email in entry["email_addresses"]:
            email_payload.append({"user_id": user_id, "email_address": email})
    session.execute(insert(EmailAddress), email_payload)

    # g. Insert emails for individual entries
    email_address_1 = EmailAddress(
        email_address="amity.blight@hexside.com", user_id=user_1.id
    )
    email_address_2 = EmailAddress(
        email_address="willow.park@hexside.com", user_id=user_2.id
    )
    session.add_all([email_address_1, email_address_2])

    # h. Commit everything at once
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

# 3. Update multiple entries
with Session(ENGINE) as session:
    # Fetch the users by their old last names
    raine = session.query(User).filter_by(last_name="Whispers").first()
    eda = session.query(User).filter_by(last_name="Clawthorne").first()

    if raine and eda:
        raine.last_name = "Clawthorne-Whispers"
        eda.last_name = "Clawthorne-Whispers"

        eda_email = session.query(EmailAddress).filter_by(user_id=eda.id).first()
        if eda_email:
            eda_email.email_address = "eda.clawthorne-whispers@owlhouse.com"  # type: ignore

        session.commit()
        print(f"\n--Users {eda.id} & {raine.id} have been updated.--")

select_all_entries()

# 4. Delete multiple entries
with Session(ENGINE) as session:
    amity = (
        session.query(User).filter_by(first_name="Amity", last_name="Blight").first()
    )
    willow = (
        session.query(User).filter_by(first_name="Willow", last_name="Park").first()
    )
    lux = session.query(User).filter_by(first_name="Lux", last_name="Noceda").first()

    if amity and willow and lux:
        user_ids = [user.id for user in [amity, willow, lux] if user]

        # Delete email addresses associated with these users, as they graduated
        for user_id in user_ids:
            session.query(EmailAddress).filter(EmailAddress.user_id == user_id).delete(
                synchronize_session=False
            )

        session.commit()
        print(
            f"\n--EmailAddress for User {amity.id}, {willow.id}, {lux.id} have been deleted.--"
        )

select_all_entries()
