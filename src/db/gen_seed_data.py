"""
dummy_data_generator.py

Generate generic, schema-aligned dummy data for seeding the database.

Provides generators for:
- accounts
- credentials
- addresses
- accommodations
- images
- (stubs) calendar, payments, bookings, reviews, conversations, messages, payouts

Assumptions:
- seed parameters and word lists live in src.db.data_lists as `seeds`
- timestamps are generated in a uniform window [start_timestamp, stop_timestamp]
- number of rows is controlled by seeds.num_gen_dummydata
"""

# ---------------------------------------------------------------------------
# Stdlib imports
# ---------------------------------------------------------------------------
import random
import datetime
from pathlib import Path
import sys
from psycopg2 import sql

# ---------------------------------------------------------------------------
# Third-party / extra imports
# ---------------------------------------------------------------------------
import rstr

# ---------------------------------------------------------------------------
# Path/bootstrap
# Go two levels up if needed (src/db → project root). Keep logic unchanged.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
import src.db.data_lists as seeds
from src.db.connection import db_connection  # kept although not used in current funcs
import src.db.sql_repo as sqlrepo
from src.db.utils.db_helpers import get_tbl_contents_as_str
from src.utils.logger import logger

# ---------------------------------------------------------------------------
# ACCOUNTS
# ---------------------------------------------------------------------------
def gen_dummydata_accounts():
    """
    Fill dummy data for accounts table.

    Returns:
        email_addresses, first_names, last_names, roles, timestamps
    """
    # first names
    first_names = []
    for _ in range(seeds.num_gen_dummydata):
        name = ""
        syllable_ammount = random.randint(seeds.fn_min_sylls, seeds.fn_max_sylls)
        for _ in range(syllable_ammount):
            name += random.choice(seeds.first_name_syllables)
        first_names.append(name)

    # last names
    last_names = []
    for _ in range(seeds.num_gen_dummydata):
        name = ""
        syllable_ammount = random.randint(seeds.ln_min_sylls, seeds.ln_max_sylls)
        for _ in range(syllable_ammount):
            name += random.choice(seeds.last_name_syllables)
        last_names.append(name)

    # email addresses
    emails = []
    counter = 0
    while counter < seeds.num_gen_dummydata:
        email_address = (
            first_names[counter]
            + "."
            + last_names[counter]
            + "@"
            + random.choice(seeds.email_domains)
        )
        if email_address not in emails:
            emails.append(email_address)
            counter += 1
        else:
            continue

    # timestamps
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    timestamps = []
    for _ in range(seeds.num_gen_dummydata):
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        timestamps.append(random_timestamp)

    # roles
    roles = []
    for _ in range(seeds.num_gen_dummydata - seeds.admin_count):
        roles.append(random.choice(["guest", "host"]))
    for _ in range(seeds.admin_count):
        roles.append("admin")

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accounts'))
    cur.execute(query)
    data = zip(emails, first_names, last_names, roles, timestamps)
    cur.executemany(sqlrepo.INSERT_ACCOUNTS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into accounts table:")
    logger.info(get_tbl_contents_as_str('accounts'))

    # Return for later use
    return emails, first_names, last_names, roles, timestamps

# ---------------------------------------------------------------------------
# CREDENTIALS
# ---------------------------------------------------------------------------
def gen_dummydata_credentials():
    """
    Fill dummy data for credentials table.

    Returns:
        password_hash, password_updated_at
    """
    password_hash = []
    for _ in range(seeds.num_gen_dummydata):
        password = "".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()",
                k=seeds.pwd_hash_length,
            )
        )
        password_hash.append(password)

    # timestamps
    password_updated_at = []
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    timestamps = []
    for _ in range(seeds.num_gen_dummydata):
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        timestamps.append(random_timestamp)
        password_updated_at.append(random_timestamp)


    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('credentials'))
    cur.execute(query)
    
    # Get Id column name
    cur.execute(sqlrepo.FETCH_ID_COLUMN_NAME, ('accounts',))
    id_column_name = cur.fetchall()
    id_column_name = id_column_name[0][0] # Unpack list of tuples

    # Get ID's with ID colum name
    query = sql.SQL(sqlrepo.FETCH_IDS).format(
    col=sql.Identifier(f'{id_column_name}'),
    tbl=sql.Identifier('accounts')
    )
    cur.execute(query)
    account_ids = cur.fetchall()
    account_ids = [item[0] for item in account_ids]  # Unpack list of tuples
    data = zip(account_ids, password_hash, password_updated_at)
    cur.executemany(sqlrepo.INSERT_CREDENTIALS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into credentials table:")
    logger.info(get_tbl_contents_as_str('credentials'))

    return password_hash, password_updated_at


# ---------------------------------------------------------------------------
# ADDRESSES
# ---------------------------------------------------------------------------
def gen_dummydata_addresses():
    """
    Fill dummy data for addresses table.

    Returns:
        line1, line2, city, postal_code, country
    """
    line1 = []
    line2 = []
    cities = []
    postal_code = []
    countries = []

    for _ in range(seeds.num_gen_dummydata):
        city, postal = random.choice(list(seeds.city_postal.items()))
        country_name = seeds.city_country[city]
        street = random.choice(seeds.city_streets[city])
        house_number = str(random.randint(1, 200))

        # line1
        line1.append(f"{street} {house_number}")

        # optional line2
        if city in seeds.city_address_terms.keys():
            term1, term2 = seeds.city_address_terms[city]
            building_number = str(random.randint(1, 10))
            unit_number = str(random.randint(1, 50))
            line2.append(f"{term1} {building_number}, {term2} {unit_number}")

        cities.append(city)
        postal_code.append(postal)
        countries.append(country_name)

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('addresses'))
    cur.execute(query)
    data = zip(line1, line2, cities, postal_code, countries)
    cur.executemany(sqlrepo.INSERT_ADDRESSES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into addresses table:")
    logger.info(get_tbl_contents_as_str('addresses'))

    return line1, line2, cities, postal_code, countries


# ---------------------------------------------------------------------------
# ACCOMMODATIONS
# ---------------------------------------------------------------------------
def gen_dummydata_accommodations():
    """
    Fill dummy data for accommodations table.

    Returns:
        titles, price_cents, is_active, created_at
    """
    titles = []
    price_cents = []
    is_active = []
    created_at = []

    # host_account_id
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accommodations'))
    cur.execute(query)
    
    # Get Id column name from accounts table
    cur.execute(sqlrepo.FETCH_ID_COLUMN_NAME, ('accounts',))
    id_column_name = cur.fetchall()
    id_column_name = id_column_name[0][0] # Unpack list of tuples

    # Get ID's with ID colum name
    query = sql.SQL(sqlrepo.FETCH_HOST_IDS).format(
    col=sql.Identifier(f'{id_column_name}'),
    tbl=sql.Identifier('accounts')
    )
    cur.execute(query)
    host_account_ids = cur.fetchall()
    host_account_ids = [item[0] for item in host_account_ids]  # Unpack list of tuples

    # Select a randwom host account id list matching num_gen_dummydata
    host_account_ids = [random.choice(host_account_ids) for _ in range(seeds.num_gen_dummydata)]

    # titles
    for _ in range(seeds.num_gen_dummydata):
        title = [
            random.choice(seeds.accomodation_title_words_dict["adjectives_general"]),
            random.choice(seeds.accomodation_title_words_dict["accommodation_nouns"]),
            random.choice(seeds.accomodation_title_words_dict["location_connectors"]),
            random.choice(seeds.accomodation_title_words_dict["adjectives_location"]),
            random.choice(seeds.accomodation_title_words_dict["place_names"]),
        ]
        titles.append(" ".join(title))
        print(title)
    
    # address_id
    # Get Id column name from accounts table
    cur.execute(sqlrepo.FETCH_ID_COLUMN_NAME, ('addresses',))
    id_column_name = cur.fetchall()
    id_column_name = id_column_name[0][0] # Unpack list of tuples

    # Get ID's with ID colum name
    query = sql.SQL(sqlrepo.FETCH_IDS).format(
    col=sql.Identifier(f'{id_column_name}'),
    tbl=sql.Identifier('addresses')
    )
    cur.execute(query)
    address_ids = cur.fetchall()
    address_ids = [item[0] for item in address_ids]  # Unpack list of tuples

    # prices
    for _ in range(seeds.num_gen_dummydata):
        price = random.randint(50, 500) * 100
        price_cents.append(price)

    # activity flags
    for _ in range(seeds.num_gen_dummydata):
        is_active.append(random.choice([True, False]))

    # created_at
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    for _ in range(seeds.num_gen_dummydata):
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        created_at.append(random_timestamp)

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accommodations'))
    cur.execute(query)
    data = zip(host_account_ids, titles, address_ids, price_cents, is_active, created_at)
    cur.executemany(sqlrepo.INSERT_ACCOMMODATIONS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into accommodations table:")
    logger.info(get_tbl_contents_as_str('accommodations'))

    return titles, price_cents, is_active, created_at


# ---------------------------------------------------------------------------
# IMAGES
# ---------------------------------------------------------------------------
def gen_dummydata_images():
    """
    Fill dummy data for images table.

    Returns:
        mimes, storage_keys, created_at
    """
    mimes = []
    storage_keys = []
    created_at = []

    for _ in range(seeds.num_gen_dummydata*4):  # More images than other tables
        # mime
        mime = random.choice(seeds.image_mimes)
        mimes.append(mime)

        # timestamp
        time_delta = seeds.stop_timestamp - seeds.start_timestamp
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        created_at.append(random_timestamp)

        # storage key
        storage_key = "images/"
        storage_key += rstr.xeger(
            r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        )
        storage_key += f".{mime.split('/')[1]}"
        storage_keys.append(storage_key)

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('images'))
    cur.execute(query)
    data = zip(mimes, storage_keys, created_at)
    cur.executemany(sqlrepo.INSERT_IMAGES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into images table:")
    logger.info(get_tbl_contents_as_str('images'))

    return mimes, storage_keys, created_at


# ---------------------------------------------------------------------------
# STUBS FOR REMAINING TABLES
# Keep stubs to preserve structure. Implement later.
# ---------------------------------------------------------------------------
def gen_dummydata_accommodation_calendar():
    """
    Fill dummy data for accommodation_calendar table.

    Returns:
        day, is_blocked, price_cents, min_nights
    """
    days = []
    is_blocked = []
    price_cents = []
    min_nights = []

    return days, is_blocked, price_cents, min_nights


def gen_dummydata_payments():
    """
    Fill dummy data for payments table.
    """
    pass


def gen_dummydata_bookings():
    """
    Fill dummy data for bookings table.
    """
    pass


def gen_dummydata_reviews():
    """
    Fill dummy data for reviews table.
    """
    pass


def gen_dummydata_review_images():
    """
    Fill dummy data for review_images table.
    """
    pass


def gen_dummydata_conversations():
    """
    Fill dummy data for conversations table.
    """
    pass


def gen_dummydata_messages():
    """
    Fill dummy data for messages table.
    """
    pass


def gen_dummydata_payment_methods():
    """
    Fill dummy data for payment_methods table.
    """
    pass


def gen_dummydata_credit_cards():
    """
    Fill dummy data for credit_cards table.
    """
    pass


def gen_dummydata_paypal():
    """
    Fill dummy data for paypal table.
    """
    pass


def gen_dummydata_payout_accounts():
    """
    Fill dummy data for payout_accounts table.
    """
    pass


def gen_dummydata_payouts():
    """
    Fill dummy data for payouts table.
    """
    pass


def gen_dummydata_notifications():
    """
    Fill dummy data for notifications table.
    """
    pass




#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=



gen_dummydata_accounts()
gen_dummydata_credentials()
gen_dummydata_addresses()
gen_dummydata_accommodations()
gen_dummydata_images()

get_tbl_contents_as_str('accounts')
get_tbl_contents_as_str('credentials')
get_tbl_contents_as_str('addresses')
get_tbl_contents_as_str('accommodations')
get_tbl_contents_as_str('images')