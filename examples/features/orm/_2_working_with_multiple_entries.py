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

from examples.config import ENGINE
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
    {
        "first_name": "Amity",
        "last_name": "Blight",
        "email_addresses": ["amity.blight@hexside.com"],
    },
    {
        "first_name": "Willow",
        "last_name": "Park",
        "email_addresses": ["willow.park@hexside.com"],
    },
]

with Session(ENGINE) as session:
    # a. Add more entries using a dictionary
    session.execute(insert(User), data)

    # b. Send the pending changes to the session WITHOUT committing it yet;
    # this updates Users with id values.
    session.flush()

    # c. Retrieve user ids
    stmt = select(User.id, User.first_name, User.last_name)
    user_map = {(u.first_name, u.last_name): u.id for u in session.execute(stmt)}

    # d. Insert email for each user in the dictionary
    email_payload = []
    for entry in data:
        user_id = user_map.get((entry["first_name"], entry["last_name"]))
        for email in entry["email_addresses"]:
            email_payload.append({"user_id": user_id, "email_address": email})
    session.execute(insert(EmailAddress), email_payload)

    # e. Commit all changes
    session.commit()


# 2. Display the results
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
    # a. Fetch the users by their old last names
    raine = session.query(User).filter_by(last_name="Whispers").first()
    eda = session.query(User).filter_by(last_name="Clawthorne").first()

    if raine and eda:
        # b. Update Users last_name
        raine.last_name = "Clawthorne-Whispers"
        eda.last_name = "Clawthorne-Whispers"

        # c. Update EmailAddress
        eda_email = session.query(EmailAddress).filter_by(user_id=eda.id).first()
        if eda_email:
            eda_email.email_address = "eda.clawthorne-whispers@owlhouse.com"  # type: ignore

        session.commit()
        print(f"\n--Users {eda.id} & {raine.id} have been updated.--")

select_all_entries()

# 4. Delete multiple entries
with Session(ENGINE) as session:
    # a. Get the User.id for affected Users
    targets = [("Amity", "Blight"), ("Willow", "Park"), ("Lux", "Noceda")]
    stmt = select(User.id).filter(tuple_(User.first_name, User.last_name).in_(targets))
    user_ids = session.scalars(stmt).all()

    # b. Delete EmailAddresses associated with these Users, as they graduated
    for user_id in user_ids:
        session.query(EmailAddress).filter(EmailAddress.user_id == user_id).delete(
            synchronize_session=False
        )

    session.commit()
    print(f"\n--EmailAddress for Users {user_ids} have been deleted.--")

select_all_entries()
