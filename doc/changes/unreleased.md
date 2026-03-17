# Unreleased

## Summary

This update fixes a bug that specifically impacted ORM sessions when flushing values to
pass IDs between linked SQLAlchemy tables. We discovered that the internal
`get_lastrowid` function has been off by one since the dialect’s inception (2015)
before Exasol's direct involvement, a bug that previously went unnoticed due to a gap
in test coverage. If you were affected, this discrepancy caused incorrect ID referencing
during data inserts, potentially breaking relational integrity in your sessions. We have
now fixed the logic to ensure the returned IDs are accurate and implemented new tests
that specifically validate row ID retrieval during ORM flushes.

The error would have only happened for ORM sessions like this example:
```python
with Session(ENGINE) as session:
    new_user = User(first_name="Jax", last_name="Doe")

    session.add(new_user)
    session.flush()

    # Here, we use the ID from the post-flush SQLAlchemy object. Before this update,
    # this value was off by 1 (ID - 1). Now, this has been corrected (ID).
    new_email = EmailAddress(
        user_id=new_user.id,
        email_address="jax.doe@example.com",
    )

    session.add(new_email)
    session.commit()
```

While this method ensures accurate ID retrieval, it is not the most performant way to
insert data in SQLAlchemy-Exasol. For high-volume inserts, consider using more
efficient bulk processing methods.

## Refactoring

* #724: Updated to `exasol-toolbox` 6.0.0

## Bugfix

* #709: Fixed ORM session usage so that session IDs when flushed are not off by one
