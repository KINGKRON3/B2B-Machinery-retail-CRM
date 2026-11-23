from database import init_db, load_demo_data


def seed(force=False):
    """Make sure the demo data exists.

    init_db() already loads the demo data automatically when the database is
    empty (see load_demo_data() in database.py). Pass force=True to wipe all
    data and restore the original demo state.
    """
    init_db()
    if force:
        load_demo_data(force=True)


if __name__ == "__main__":
    seed(force=True)
    print("Demo data loaded successfully!")
