from sqlalchemy import (
    and_,
    delete,
    insert,
    or_,
    select,
    update,
)

from examples.config import ENGINE

# Import the Table objects (not classes) from your metadata
from examples.features.non_orm._0_create_tables import (
    email_address_table,
    user_table,
)

# 0. Clean tables
with ENGINE.begin() as conn:
    conn.execute(delete(email_address_table))
    conn.execute(delete(user_table))

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

with ENGINE.begin() as conn:
    # a. Insert Users
    user_payload = [
        {"first_name": d["first_name"], "last_name": d["last_name"]} for d in data
    ]
    conn.execute(insert(user_table), user_payload)

    # b. Retrieve user ids
    stmt = select(user_table.c.id, user_table.c.first_name, user_table.c.last_name)
    user_map = {(row.first_name, row.last_name): row.id for row in conn.execute(stmt)}

    # c. Insert EmailAddresses
    email_payload = []
    for entry in data:
        u_id = user_map.get((entry["first_name"], entry["last_name"]))
        for email in entry["email_addresses"]:
            email_payload.append({"user_id": u_id, "email_address": email})
    conn.execute(insert(email_address_table), email_payload)


# 2. Display results
def select_all_entries():
    with ENGINE.connect() as conn:
        # Join user_table and email_address_table explicitly
        stmt = select(
            user_table.c.id,
            user_table.c.first_name,
            user_table.c.last_name,
            email_address_table.c.email_address,
        ).select_from(user_table.join(email_address_table, isouter=True))
        results = conn.execute(stmt).fetchall()

        # Grouping manually since Core doesn't have ORM's unique().all() object deduplication
        grouped = {}
        for row in results:
            key = (row.id, row.first_name, row.last_name)
            if key not in grouped:
                grouped[key] = []
            if row.email_address:
                grouped[key].append(row.email_address)

        for (u_id, f_name, l_name), emails in grouped.items():
            print(f"{u_id} {f_name} {l_name} {emails}")


select_all_entries()

# 3. Update multiple entries
with ENGINE.begin() as conn:
    # a. Update the last_name of Users
    new_last_name = "Clawthorne-Whispers"
    conn.execute(
        update(user_table)
        .where(user_table.c.last_name.in_(["Whispers", "Clawthorne"]))
        .values(last_name=new_last_name)
    )

    # b. Update the EmailAddress
    eda_id_subq = (
        select(user_table.c.id)
        .where(user_table.c.first_name == "Eda")
        .scalar_subquery()
    )
    conn.execute(
        update(email_address_table)
        .where(email_address_table.c.user_id == eda_id_subq)
        .values(email_address="eda.clawthorne-whispers@owlhouse.com")
    )

# 4. Delete multiple entries
with ENGINE.begin() as conn:
    # a. Define the selection criteria for the users you want to target
    target_criteria = or_(
        and_(user_table.c.first_name == "Amity", user_table.c.last_name == "Blight"),
        and_(user_table.c.first_name == "Willow", user_table.c.last_name == "Park"),
        and_(user_table.c.first_name == "Lux", user_table.c.last_name == "Noceda"),
    )
    stmt = select(user_table.c.id).where(target_criteria)
    users_ids = conn.execute(stmt).scalars().all()

    # b. Delete EmailAddresses associated with these Users, as they graduated
    for uid in users_ids:
        email_delete_stmt = delete(email_address_table).where(
            email_address_table.c.user_id == uid
        )
        conn.execute(email_delete_stmt)

select_all_entries()
