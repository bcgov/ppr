"""2024-10-01_rebase

Revision ID: ce62234b2378
Revises: 
Create Date: 2024-10-01 13:59:22.172259

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_extension import PGExtension
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_view import PGView
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Sequence, CreateSequence, DropSequence  # Added manually.

# revision identifiers, used by Alembic.
revision = 'ce62234b2378'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### Manually install extensions. ###
    # op.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")
    # op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    # op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")
    public_fuzzystrmatch = PGExtension(
        schema="public",
        signature="fuzzystrmatch"
    )
    op.create_entity(public_fuzzystrmatch)

    public_btree_gist = PGExtension(
        schema="public",
        signature="btree_gist"
    )
    op.create_entity(public_btree_gist)

    public_pg_trgm = PGExtension(
        schema="public",
        signature="pg_trgm"
    )
    op.create_entity(public_pg_trgm)

    # ### Manually create sequences and add them to pk columns. ###
    # PPR sequences
    op.execute(CreateSequence(Sequence('document_number_seq', start=100000, increment=1)))
    op.execute(CreateSequence(Sequence('registration_num_q_seq', start=100000, increment=1)))
    op.execute(CreateSequence(Sequence('account_bcol_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('address_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('code_branch_id_seq', start=7162, increment=1, minvalue=7162, maxvalue=8999)))
    op.execute(CreateSequence(Sequence('historical_head_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('court_order_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('draft_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('event_tracking_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('financing_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('general_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mail_report_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('party_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('registration_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('search_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('securities_act_notice_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('securities_act_order_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('test_search_batches_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('test_search_results_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('test_searches_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('trust_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('user_extra_registration_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('user_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('vehicle_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('verification_report_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('word_id_seq', start=55, increment=1)))
    op.execute(CreateSequence(Sequence('name_id_seq', start=100528, increment=1)))
    # MHR sequences
    op.execute(CreateSequence(Sequence('mhr_number_seq', start=150000, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_draft_number_seq', start=100000, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_doc_reg_seq', start=550000, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_doc_id_manufacturer_seq', start=80100000, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_doc_id_gov_seq', start=90050000, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_doc_id_qualified_seq', start=10200000, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_extra_registration_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_draft_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_registration_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_owner_group_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_party_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_registration_report_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_location_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_document_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_note_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_description_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_section_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_manufacturer_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_supplier_id_seq', start=1, increment=1)))
    op.execute(CreateSequence(Sequence('mhr_agreements_id_seq', start=1, increment=1)))

    # ### commands auto generated by Alembic - please adjust! ###
    # PPR type tables
    country_type = op.create_table('country_types',
    sa.Column('country_type', sa.String(length=2), nullable=False),
    sa.Column('country_desc', sa.String(length=75), nullable=False),
    sa.PrimaryKeyConstraint('country_type')
    )
    event_tracking_type = op.create_table('event_tracking_types',
    sa.Column('event_tracking_type', sa.String(length=20), nullable=False),
    sa.Column('event_tracking_desc', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('event_tracking_type')
    )
    party_type = op.create_table('party_types',
    sa.Column('party_type', sa.String(length=2), nullable=False),
    sa.Column('party_type_desc', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('party_type')
    )
    registration_type_class = op.create_table('registration_type_classes',
    sa.Column('registration_type_cl', sa.String(length=10), nullable=False),
    sa.Column('registration_desc', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('registration_type_cl')
    )
    search_type = op.create_table('search_types',
    sa.Column('search_type', sa.String(length=2), nullable=False),
    sa.Column('search_type_desc', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('search_type')
    )
    securities_act_type = op.create_table('securities_act_types',
    sa.Column('securities_act_type', postgresql.ENUM('LIEN', 'PROCEEDINGS', 'PRESERVATION', name='securities_act_type'), nullable=False),
    sa.Column('securities_act_type_desc', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('securities_act_type')
    )
    serial_type = op.create_table('serial_types',
    sa.Column('serial_type', sa.String(length=2), nullable=False),
    sa.Column('serial_type_desc', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('serial_type')
    )
    state_type = op.create_table('state_types',
    sa.Column('state_type', sa.String(length=3), nullable=False),
    sa.Column('state_type_desc', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('state_type')
    )
    province_type = op.create_table('province_types',
    sa.Column('province_type', sa.String(length=2), nullable=False),
    sa.Column('country_type', sa.String(length=2), nullable=False),
    sa.Column('province_desc', sa.String(length=75), nullable=False),
    sa.ForeignKeyConstraint(['country_type'], ['country_types.country_type'], ),
    sa.PrimaryKeyConstraint('province_type')
    )
    registration_type = op.create_table('registration_types',
    sa.Column('registration_type', sa.String(length=2), nullable=False),
    sa.Column('registration_type_cl', sa.String(length=10), nullable=False),
    sa.Column('registration_desc', sa.String(length=100), nullable=False),
    sa.Column('registration_act', sa.String(length=60), nullable=False),
    sa.ForeignKeyConstraint(['registration_type_cl'], ['registration_type_classes.registration_type_cl'], ),
    sa.PrimaryKeyConstraint('registration_type')
    )
    # MHR type tables
    mhr_document_type = op.create_table('mhr_document_types',
    sa.Column('document_type', postgresql.ENUM('REG_101', 'REG_102', 'REG_103', 'REG_103E', 'ABAN', 'ADDI', 'AFFE', 'ATTA', 'BANK', 'BCLC', 'CAU', 'CAUC', 'CAUE', 'COMP', 'CONF', 'CONV', 'COU', 'COUR', 'DEAT', 'DNCH', 'EXMN', 'EXNR', 'EXRE', 'EXRS', 'FORE', 'FZE', 'GENT', 'INTE', 'INTW', 'LETA', 'MAID', 'MAIL', 'MARR', 'MEAM', 'NAMV', 'NCAN', 'NCON', 'NPUB', 'NRED', 'PDEC', 'PUBA', 'REBU', 'REGC', 'REIV', 'REPV', 'REST', 'STAT', 'SZL', 'TAXN', 'TAXS', 'THAW', 'TRAN', 'VEST', 'WHAL', 'WILL', 'TRANS_LAND_TITLE', 'TRANS_FAMILY_ACT', 'TRANS_INFORMAL_SALE', 'TRANS_QUIT_CLAIM', 'TRANS_SEVER_GRANT', 'TRANS_RECEIVERSHIP', 'TRANS_WRIT_SEIZURE', 'AMEND_PERMIT', 'CANCEL_PERMIT', 'REGC_STAFF', 'REGC_CLIENT', 'REREGISTER_C', name='mhr_document_type'), nullable=False),
    sa.Column('document_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_fee_code', sa.String(length=6), nullable=True),
    sa.PrimaryKeyConstraint('document_type')
    )
    mhr_location_type = op.create_table('mhr_location_types',
    sa.Column('location_type', postgresql.ENUM('MANUFACTURER', 'MH_PARK', 'OTHER', 'RESERVE', 'STRATA', name='mhr_location_type'), nullable=False),
    sa.Column('location_type_desc', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('location_type')
    )
    mhr_note_status_type = op.create_table('mhr_note_status_types',
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'CANCELLED', 'EXPIRED', 'CORRECTED', 'COMPLETED', name='mhr_note_status_type'), nullable=False),
    sa.Column('status_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_status_type', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('status_type')
    )
    mhr_owner_status_type = op.create_table('mhr_owner_status_types',
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'EXEMPT', 'PREVIOUS', name='mhr_owner_status_type'), nullable=False),
    sa.Column('status_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_status_type', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('status_type')
    )
    mhr_party_type = op.create_table('mhr_party_types',
    sa.Column('party_type', postgresql.ENUM('OWNER_BUS', 'OWNER_IND', 'SUBMITTING', 'EXECUTOR', 'ADMINISTRATOR', 'TRUSTEE', 'TRUST', 'MANUFACTURER', 'CONTACT', name='mhr_party_type'), nullable=False),
    sa.Column('party_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_party_type', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('party_type')
    )
    mhr_registration_status_type = op.create_table('mhr_registration_status_types',
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'CANCELLED', 'DRAFT', 'EXEMPT', 'HISTORICAL', name='mhr_registration_status_type'), nullable=False),
    sa.Column('status_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_status_type', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('status_type')
    )
    mhr_registration_type = op.create_table('mhr_registration_types',
    sa.Column('registration_type', postgresql.ENUM('DECAL_REPLACE', 'MHREG', 'TRAND', 'TRANS', 'TRANS_AFFIDAVIT', 'TRANS_ADMIN', 'TRANS_WILL', 'EXEMPTION_RES', 'EXEMPTION_NON_RES', 'PERMIT', 'PERMIT_EXTENSION', 'MANUFACTURER', 'MHREG_CONVERSION', 'REG_STAFF_ADMIN', 'AMENDMENT', name='mhr_registration_type'), nullable=False),
    sa.Column('registration_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_registration_type', sa.String(length=4), nullable=False),
    sa.PrimaryKeyConstraint('registration_type')
    )
    mhr_status_type = op.create_table('mhr_status_types',
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'DRAFT', 'HISTORICAL', name='mhr_status_type'), nullable=False),
    sa.Column('status_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_status_type', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('status_type')
    )
    mhr_tenancy_type = op.create_table('mhr_tenancy_types',
    sa.Column('tenancy_type', postgresql.ENUM('COMMON', 'JOINT', 'NA', 'SOLE', name='mhr_tenancy_type'), nullable=False),
    sa.Column('tenancy_type_desc', sa.String(length=100), nullable=False),
    sa.Column('legacy_tenancy_type', sa.String(length=2), nullable=False),
    sa.PrimaryKeyConstraint('tenancy_type')
    )

    # PPR tables
    op.create_table('account_bcol_ids',
    sa.Column('id', sa.Integer(), sa.Sequence('account_bcol_id_seq'), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=False),
    sa.Column('bconline_account', sa.Integer(), nullable=False),
    sa.Column('crown_charge_ind', sa.String(length=1), nullable=True),
    sa.Column('securities_act_ind', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('account_bcol_ids', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_account_bcol_ids_account_id'), ['account_id'], unique=False)

    op.create_table('user_extra_registrations',
    sa.Column('id', sa.Integer(), sa.Sequence('user_extra_registration_seq'), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=False),
    sa.Column('registration_number', sa.String(length=10), nullable=False),
    sa.Column('removed_ind', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user_extra_registrations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_extra_registrations_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_extra_registrations_registration_number'), ['registration_number'], unique=False)

    op.create_table('users',
    sa.Column('id', sa.Integer(), sa.Sequence('user_id_seq'), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('username', sa.String(length=1000), nullable=False),
    sa.Column('sub', sa.String(length=36), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('firstname', sa.String(length=1000), nullable=True),
    sa.Column('lastname', sa.String(length=1000), nullable=True),
    sa.Column('email', sa.String(length=1024), nullable=True),
    sa.Column('iss', sa.String(length=1024), nullable=True),
    sa.Column('idp_userid', sa.String(length=256), nullable=True),
    sa.Column('login_source', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sub')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_idp_userid'), ['idp_userid'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=False)

    op.create_table('event_tracking',
    sa.Column('id', sa.Integer(), sa.Sequence('event_tracking_id_seq'), nullable=False),
    sa.Column('key_id', sa.Integer(), nullable=False),
    sa.Column('event_ts', sa.DateTime(), nullable=False),
    sa.Column('event_tracking_type', sa.String(length=20), nullable=False),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=2000), nullable=True),
    sa.Column('email_address', sa.String(length=250), nullable=True),
    sa.ForeignKeyConstraint(['event_tracking_type'], ['event_tracking_types.event_tracking_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('event_tracking', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_event_tracking_event_tracking_type'), ['event_tracking_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_tracking_event_ts'), ['event_ts'], unique=False)
        batch_op.create_index(batch_op.f('ix_event_tracking_key_id'), ['key_id'], unique=False)

    op.create_table('financing_statements',
    sa.Column('id', sa.Integer(), sa.Sequence('financing_id_seq'), nullable=False),
    sa.Column('state_type', sa.String(length=3), nullable=False),
    sa.Column('life', sa.Integer(), nullable=True),
    sa.Column('expire_date', sa.DateTime(), nullable=True),
    sa.Column('discharged', sa.String(length=1), nullable=True),
    sa.Column('renewed', sa.String(length=1), nullable=True),
    sa.Column('type_claim', sa.String(length=2), nullable=True),
    sa.Column('crown_charge_type', sa.String(length=2), nullable=True),
    sa.Column('crown_charge_other', sa.String(length=70), nullable=True),
    sa.ForeignKeyConstraint(['state_type'], ['state_types.state_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('search_requests',
    sa.Column('id', sa.Integer(), sa.Sequence('search_id_seq'), nullable=False),
    sa.Column('search_ts', sa.DateTime(), nullable=False),
    sa.Column('search_type', sa.String(length=2), nullable=False),
    sa.Column('api_criteria', sa.JSON(), nullable=False),
    sa.Column('search_response', sa.JSON(), nullable=True),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('client_reference_id', sa.String(length=50), nullable=True),
    sa.Column('total_results_size', sa.Integer(), nullable=True),
    sa.Column('returned_results_size', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.String(length=1000), nullable=True),
    sa.Column('updated_selection', sa.JSON(), nullable=True),
    sa.Column('pay_invoice_id', sa.Integer(), nullable=True),
    sa.Column('pay_path', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['search_type'], ['search_types.search_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('search_requests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_search_requests_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_search_requests_search_ts'), ['search_ts'], unique=False)

    op.create_table('user_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('payment_confirmation', sa.String(length=1), nullable=False),
    sa.Column('search_selection_confirmation', sa.String(length=1), nullable=False),
    sa.Column('default_drop_downs', sa.String(length=1), nullable=False),
    sa.Column('default_table_filters', sa.String(length=1), nullable=False),
    sa.Column('registrations_table', sa.JSON(), nullable=True),
    sa.Column('misc_preferences', sa.JSON(), nullable=True),
    sa.Column('service_agreements', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('addresses',
    sa.Column('id', sa.Integer(), sa.Sequence('address_id_seq'), nullable=False),
    sa.Column('street', sa.String(length=50), nullable=True),
    sa.Column('street_additional', sa.String(length=50), nullable=True),
    sa.Column('city', sa.String(length=40), nullable=True),
    sa.Column('region', sa.String(length=2), nullable=True),
    sa.Column('postal_code', sa.String(length=15), nullable=True),
    sa.Column('country', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['country'], ['country_types.country_type'], ),
    sa.ForeignKeyConstraint(['region'], ['province_types.province_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('drafts',
    sa.Column('id', sa.Integer(), sa.Sequence('draft_id_seq'), nullable=False),
    sa.Column('document_number', sa.String(length=10), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=False),
    sa.Column('create_ts', sa.DateTime(), nullable=False),
    sa.Column('draft', sa.JSON(), nullable=False),
    sa.Column('registration_number', sa.String(length=10), nullable=True),
    sa.Column('update_ts', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.String(length=1000), nullable=True),
    sa.Column('registration_type', sa.String(length=2), nullable=False),
    sa.Column('registration_type_cl', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['registration_type'], ['registration_types.registration_type'], ),
    sa.ForeignKeyConstraint(['registration_type_cl'], ['registration_type_classes.registration_type_cl'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('document_number')
    )
    with op.batch_alter_table('drafts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_drafts_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_drafts_create_ts'), ['create_ts'], unique=False)

    op.create_table('previous_financing_statements',
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('registration_type', sa.String(length=30), nullable=False),
    sa.Column('cb_date', sa.String(length=10), nullable=True),
    sa.Column('cb_number', sa.String(length=10), nullable=True),
    sa.Column('cr_date', sa.String(length=10), nullable=True),
    sa.Column('cr_number', sa.String(length=10), nullable=True),
    sa.Column('mhr_date', sa.String(length=10), nullable=True),
    sa.Column('mhr_number', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.PrimaryKeyConstraint('financing_id')
    )
    op.create_table('search_results',
    sa.Column('search_id', sa.Integer(), nullable=False),
    sa.Column('api_result', sa.JSON(), nullable=True),
    sa.Column('registrations', sa.JSON(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('exact_match_count', sa.Integer(), nullable=True),
    sa.Column('similar_match_count', sa.Integer(), nullable=True),
    sa.Column('callback_url', sa.String(length=1000), nullable=True),
    sa.Column('doc_storage_url', sa.String(length=1000), nullable=True),
    sa.Column('account_name', sa.String(length=1000), nullable=True),
    sa.ForeignKeyConstraint(['search_id'], ['search_requests.id'], ),
    sa.PrimaryKeyConstraint('search_id')
    )
    op.create_table('client_codes',
    sa.Column('id', sa.Integer(), sa.Sequence('code_branch_id_seq'), nullable=False),
    sa.Column('head_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('bconline_account', sa.Integer(), nullable=True),
    sa.Column('contact_name', sa.String(length=100), nullable=False),
    sa.Column('contact_area_cd', sa.String(length=3), nullable=True),
    sa.Column('contact_phone_number', sa.String(length=15), nullable=False),
    sa.Column('email_address', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.String(length=7), nullable=True),
    sa.Column('date_ts', sa.DateTime(), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=False),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client_codes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_codes_address_id'), ['address_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_head_id'), ['head_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_users_id'), ['users_id'], unique=False)

    op.create_table('registrations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('registration_ts', sa.DateTime(), nullable=False),
    sa.Column('registration_number', sa.String(length=10), nullable=False),
    sa.Column('base_reg_number', sa.String(length=10), nullable=True),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('client_reference_id', sa.String(length=50), nullable=True),
    sa.Column('life', sa.Integer(), nullable=True),
    sa.Column('lien_value', sa.String(length=15), nullable=True),
    sa.Column('surrender_date', sa.DateTime(), nullable=True),
    sa.Column('ver_bypassed', sa.String(length=1), nullable=True),
    sa.Column('pay_invoice_id', sa.Integer(), nullable=True),
    sa.Column('pay_path', sa.String(length=256), nullable=True),
    sa.Column('user_id', sa.String(length=1000), nullable=True),
    sa.Column('detail_description', sa.String(length=4000), nullable=True),
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('draft_id', sa.Integer(), nullable=False),
    sa.Column('registration_type', sa.String(length=2), nullable=False),
    sa.Column('registration_type_cl', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['draft_id'], ['drafts.id'], ),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.ForeignKeyConstraint(['registration_type'], ['registration_types.registration_type'], ),
    sa.ForeignKeyConstraint(['registration_type_cl'], ['registration_type_classes.registration_type_cl'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_registrations_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_registrations_base_reg_number'), ['base_reg_number'], unique=False)
        batch_op.create_index(batch_op.f('ix_registrations_draft_id'), ['draft_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_registrations_financing_id'), ['financing_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_registrations_registration_number'), ['registration_number'], unique=False)
        batch_op.create_index(batch_op.f('ix_registrations_registration_ts'), ['registration_ts'], unique=False)

    op.create_table('client_codes_historical',
    sa.Column('id', sa.Integer(), sa.Sequence('historical_head_id_seq'), nullable=False),
    sa.Column('head_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('historical_type', sa.String(length=1), nullable=False),
    sa.Column('bconline_account', sa.Integer(), nullable=True),
    sa.Column('contact_name', sa.String(length=100), nullable=False),
    sa.Column('contact_area_cd', sa.String(length=3), nullable=True),
    sa.Column('contact_phone_number', sa.String(length=15), nullable=False),
    sa.Column('email_addresss', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.String(length=7), nullable=True),
    sa.Column('date_ts', sa.DateTime(), nullable=True),
    sa.Column('branch_id', sa.Integer(), nullable=False),
    sa.Column('address_id', sa.Integer(), nullable=False),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['branch_id'], ['client_codes.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client_codes_historical', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_codes_historical_address_id'), ['address_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_historical_branch_id'), ['branch_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_historical_head_id'), ['head_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_historical_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_client_codes_historical_users_id'), ['users_id'], unique=False)

    op.create_table('court_orders',
    sa.Column('id', sa.Integer(), sa.Sequence('court_order_id_seq'), nullable=False),
    sa.Column('order_date', sa.DateTime(), nullable=False),
    sa.Column('court_name', sa.String(length=256), nullable=False),
    sa.Column('court_registry', sa.String(length=64), nullable=False),
    sa.Column('file_number', sa.String(length=20), nullable=False),
    sa.Column('effect_of_order', sa.String(length=512), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('court_orders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_court_orders_registration_id'), ['registration_id'], unique=False)

    op.create_table('general_collateral',
    sa.Column('id', sa.Integer(), sa.Sequence('general_id_seq'), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=1), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('general_collateral', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_general_collateral_financing_id'), ['financing_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_general_collateral_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_general_collateral_registration_id_end'), ['registration_id_end'], unique=False)

    op.create_table('general_collateral_legacy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=1), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('general_collateral_legacy', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_general_collateral_legacy_financing_id'), ['financing_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_general_collateral_legacy_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_general_collateral_legacy_registration_id_end'), ['registration_id_end'], unique=False)

    op.create_table('parties',
    sa.Column('id', sa.Integer(), sa.Sequence('party_id_seq'), nullable=False),
    sa.Column('party_type', sa.String(length=2), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('middle_initial', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('business_name', sa.String(length=150), nullable=True),
    sa.Column('birth_date', sa.DateTime(), nullable=True),
    sa.Column('email_address', sa.String(length=250), nullable=True),
    sa.Column('first_name_key', sa.String(length=100), nullable=True),
    sa.Column('last_name_key', sa.String(length=50), nullable=True),
    sa.Column('business_srch_key', sa.String(length=150), nullable=True),
    sa.Column('last_name_split1', sa.String(length=50), nullable=True),
    sa.Column('last_name_split2', sa.String(length=50), nullable=True),
    sa.Column('last_name_split3', sa.String(length=50), nullable=True),
    sa.Column('first_name_split1', sa.String(length=50), nullable=True),
    sa.Column('first_name_split2', sa.String(length=50), nullable=True),
    sa.Column('first_name_char1', sa.String(length=1), nullable=True),
    sa.Column('first_name_char2', sa.String(length=1), nullable=True),
    sa.Column('first_name_key_char1', sa.String(length=1), nullable=True),
    sa.Column('bus_name_base', sa.String(length=150), nullable=True),
    sa.Column('bus_name_key_char1', sa.String(length=1), nullable=True),
    sa.Column('previous_party_id', sa.Integer(), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('branch_id', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['branch_id'], ['client_codes.id'], ),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.ForeignKeyConstraint(['party_type'], ['party_types.party_type'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('parties', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_parties_address_id'), ['address_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_branch_id'), ['branch_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_business_name'), ['business_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_business_srch_key'), ['business_srch_key'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_financing_id'), ['financing_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_first_name_key'), ['first_name_key'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_first_name_split1'), ['first_name_split1'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_first_name_split2'), ['first_name_split2'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_last_name_key'), ['last_name_key'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_last_name_split1'), ['last_name_split1'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_last_name_split2'), ['last_name_split2'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_last_name_split3'), ['last_name_split3'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_middle_initial'), ['middle_initial'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_parties_registration_id_end'), ['registration_id_end'], unique=False)

    op.create_table('securities_act_notices',
    sa.Column('id', sa.Integer(), sa.Sequence('securities_act_notice_id_seq'), nullable=False),
    sa.Column('effective_ts', sa.DateTime(), nullable=False),
    sa.Column('detail_description', sa.String(length=4000), nullable=True),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('securities_act_type', postgresql.ENUM('LIEN', 'PROCEEDINGS', 'PRESERVATION', name='securities_act_type'), nullable=False),
    sa.Column('previous_notice_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.ForeignKeyConstraint(['securities_act_type'], ['securities_act_types.securities_act_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('securities_act_notices', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_securities_act_notices_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_securities_act_notices_registration_id_end'), ['registration_id_end'], unique=False)

    op.create_table('serial_collateral',
    sa.Column('id', sa.Integer(), sa.Sequence('vehicle_id_seq'), nullable=False),
    sa.Column('serial_type', sa.String(length=2), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('make', sa.String(length=60), nullable=True),
    sa.Column('model', sa.String(length=60), nullable=True),
    sa.Column('serial_number', sa.String(length=30), nullable=True),
    sa.Column('mhr_number', sa.String(length=6), nullable=True),
    sa.Column('srch_vin', sa.String(length=6), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.ForeignKeyConstraint(['serial_type'], ['serial_types.serial_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('serial_collateral', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_serial_collateral_financing_id'), ['financing_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_serial_collateral_mhr_number'), ['mhr_number'], unique=False)
        batch_op.create_index(batch_op.f('ix_serial_collateral_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_serial_collateral_registration_id_end'), ['registration_id_end'], unique=False)
        batch_op.create_index(batch_op.f('ix_serial_collateral_srch_vin'), ['srch_vin'], unique=False)

    op.create_table('trust_indentures',
    sa.Column('id', sa.Integer(), sa.Sequence('trust_id_seq'), nullable=False),
    sa.Column('trust_indenture', sa.String(length=1), nullable=False),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('financing_id', sa.Integer(), nullable=False),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['financing_id'], ['financing_statements.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('trust_indentures', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_trust_indentures_financing_id'), ['financing_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_trust_indentures_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_trust_indentures_registration_id_end'), ['registration_id_end'], unique=False)

    op.create_table('verification_reports',
    sa.Column('id', sa.Integer(), sa.Sequence('verification_report_id_seq'), nullable=False),
    sa.Column('create_ts', sa.DateTime(), nullable=False),
    sa.Column('report_data', sa.JSON(), nullable=False),
    sa.Column('report_type', sa.String(length=30), nullable=False),
    sa.Column('doc_storage_url', sa.String(length=1000), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('verification_reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_verification_reports_create_ts'), ['create_ts'], unique=False)
        batch_op.create_index(batch_op.f('ix_verification_reports_registration_id'), ['registration_id'], unique=False)

    op.create_table('mail_reports',
    sa.Column('id', sa.Integer(), sa.Sequence('mail_report_id_seq'), nullable=False),
    sa.Column('create_ts', sa.DateTime(), nullable=False),
    sa.Column('report_data', sa.JSON(), nullable=False),
    sa.Column('doc_storage_url', sa.String(length=1000), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=2000), nullable=True),
    sa.Column('batch_job_id', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('party_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mail_reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mail_reports_create_ts'), ['create_ts'], unique=False)
        batch_op.create_index(batch_op.f('ix_mail_reports_party_id'), ['party_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mail_reports_registration_id'), ['registration_id'], unique=False)

    op.create_table('securities_act_orders',
    sa.Column('id', sa.Integer(), sa.Sequence('securities_act_order_id_seq'), nullable=False),
    sa.Column('court_order_ind', sa.String(length=1), nullable=False),
    sa.Column('order_date', sa.DateTime(), nullable=True),
    sa.Column('court_name', sa.String(length=256), nullable=True),
    sa.Column('court_registry', sa.String(length=64), nullable=True),
    sa.Column('file_number', sa.String(length=20), nullable=True),
    sa.Column('effect_of_order', sa.String(length=512), nullable=True),
    sa.Column('registration_id_end', sa.Integer(), nullable=True),
    sa.Column('previous_order_id', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('securities_act_notice_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['registrations.id'], ),
    sa.ForeignKeyConstraint(['securities_act_notice_id'], ['securities_act_notices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('securities_act_orders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_securities_act_orders_registration_id'), ['registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_securities_act_orders_registration_id_end'), ['registration_id_end'], unique=False)
        batch_op.create_index(batch_op.f('ix_securities_act_orders_securities_act_notice_id'), ['securities_act_notice_id'], unique=False)

    op.create_table('test_search_batches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('search_type', sa.String(length=2), nullable=False),
    sa.Column('test_date', sa.DateTime(), nullable=False),
    sa.Column('sim_val_business', sa.Float(), nullable=True),
    sa.Column('sim_val_first_name', sa.Float(), nullable=True),
    sa.Column('sim_val_last_name', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['search_type'], ['search_types.search_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_searches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('search_criteria', sa.Text(), nullable=False),
    sa.Column('run_time', sa.Float(), nullable=False),
    sa.Column('batch_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['batch_id'], ['test_search_batches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_searches_batch_id'), 'test_searches', ['batch_id'], unique=False)
    op.create_table('test_search_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doc_id', sa.String(length=20), nullable=False),
    sa.Column('details', sa.Text(), nullable=False),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('match_type', sa.String(length=1), nullable=False),
    sa.Column('source', sa.String(length=10), nullable=False),
    sa.Column('search_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['search_id'], ['test_searches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_search_results_search_id'), 'test_search_results', ['search_id'], unique=False)

    nickname = op.create_table('nicknames',
    sa.Column('name_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=25), nullable=False),
    )
    op.create_index(op.f('ix_nickname_name_id'), 'nicknames', ['name_id'], unique=False)
    op.create_index(op.f('ix_nickname_name'), 'nicknames', ['name'], unique=False)

    # Manually added common_word, used by search.
    op.create_table('common_word',
    sa.Column('id', sa.Integer(), sa.Sequence('word_id_seq'), nullable=False),
    sa.Column('word', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_common_word_word'), 'common_word', ['word'], unique=False)

    # MHR tables
    op.create_table('mhr_drafts',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_draft_id_seq'), nullable=False),
    sa.Column('draft_number', sa.String(length=10), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=False),
    sa.Column('create_ts', sa.DateTime(), nullable=False),
    sa.Column('draft', sa.JSON(), nullable=False),
    sa.Column('mhr_number', sa.String(length=7), nullable=True),
    sa.Column('update_ts', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.String(length=1000), nullable=True),
    sa.Column('registration_type', postgresql.ENUM('DECAL_REPLACE', 'MHREG', 'TRAND', 'TRANS', 'TRANS_AFFIDAVIT', 'TRANS_ADMIN', 'TRANS_WILL', 'EXEMPTION_RES', 'EXEMPTION_NON_RES', 'PERMIT', 'PERMIT_EXTENSION', 'MANUFACTURER', 'MHREG_CONVERSION', 'REG_STAFF_ADMIN', 'AMENDMENT', name='mhr_registration_type'), nullable=False),
    sa.ForeignKeyConstraint(['registration_type'], ['mhr_registration_types.registration_type'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('draft_number')
    )
    with op.batch_alter_table('mhr_drafts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_drafts_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_drafts_create_ts'), ['create_ts'], unique=False)

    op.create_table('mhr_extra_registrations',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_extra_registration_seq'), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=False),
    sa.Column('mhr_number', sa.String(length=6), nullable=False),
    sa.Column('removed_ind', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_extra_registrations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_extra_registrations_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_extra_registrations_mhr_number'), ['mhr_number'], unique=False)

    op.create_table('mhr_service_agreements',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_agreements_id_seq'), nullable=False),
    sa.Column('agreement_type', sa.String(length=20), nullable=False),
    sa.Column('version', sa.String(length=10), nullable=False),
    sa.Column('create_ts', sa.DateTime(), nullable=False),
    sa.Column('doc_storage_url', sa.String(length=1000), nullable=False),
    sa.Column('current_version', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('mhr_registrations',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_registration_id_seq'), nullable=False),
    sa.Column('registration_ts', sa.DateTime(), nullable=False),
    sa.Column('mhr_number', sa.String(length=7), nullable=False),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('client_reference_id', sa.String(length=50), nullable=True),
    sa.Column('pay_invoice_id', sa.Integer(), nullable=True),
    sa.Column('pay_path', sa.String(length=256), nullable=True),
    sa.Column('user_id', sa.String(length=1000), nullable=True),
    sa.Column('draft_id', sa.Integer(), nullable=False),
    sa.Column('registration_type', postgresql.ENUM('DECAL_REPLACE', 'MHREG', 'TRAND', 'TRANS', 'TRANS_AFFIDAVIT', 'TRANS_ADMIN', 'TRANS_WILL', 'EXEMPTION_RES', 'EXEMPTION_NON_RES', 'PERMIT', 'PERMIT_EXTENSION', 'MANUFACTURER', 'MHREG_CONVERSION', 'REG_STAFF_ADMIN', 'AMENDMENT', name='mhr_registration_type'), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'CANCELLED', 'DRAFT', 'EXEMPT', 'HISTORICAL', name='mhr_registration_status_type'), nullable=False),
    sa.ForeignKeyConstraint(['draft_id'], ['mhr_drafts.id'], ),
    sa.ForeignKeyConstraint(['registration_type'], ['mhr_registration_types.registration_type'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_registration_status_types.status_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_registrations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_registrations_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_registrations_draft_id'), ['draft_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_registrations_mhr_number'), ['mhr_number'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_registrations_registration_ts'), ['registration_ts'], unique=False)

    op.create_table('mhr_descriptions',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_description_id_seq'), nullable=False),
    sa.Column('csa_number', sa.String(length=10), nullable=True),
    sa.Column('csa_standard', sa.String(length=4), nullable=True),
    sa.Column('number_of_sections', sa.Integer(), nullable=False),
    sa.Column('square_feet', sa.Integer(), nullable=True),
    sa.Column('year_made', sa.Integer(), nullable=True),
    sa.Column('circa', sa.String(length=1), nullable=True),
    sa.Column('engineer_date', sa.DateTime(), nullable=True),
    sa.Column('engineer_name', sa.String(length=150), nullable=True),
    sa.Column('manufacturer_name', sa.String(length=310), nullable=True),
    sa.Column('make', sa.String(length=60), nullable=True),
    sa.Column('model', sa.String(length=60), nullable=True),
    sa.Column('rebuilt_remarks', sa.String(length=300), nullable=True),
    sa.Column('other_remarks', sa.String(length=150), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'DRAFT', 'HISTORICAL', name='mhr_status_type'), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_status_types.status_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_descriptions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_descriptions_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_descriptions_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_documents',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_document_id_seq'), nullable=False),
    sa.Column('document_id', sa.String(length=8), nullable=False),
    sa.Column('document_registration_number', sa.String(length=8), nullable=False),
    sa.Column('attention_reference', sa.String(length=50), nullable=True),
    sa.Column('owner_x_reference', sa.String(length=5), nullable=True),
    sa.Column('declared_value', sa.Integer(), nullable=True),
    sa.Column('own_land', sa.String(length=1), nullable=True),
    sa.Column('consideration_value', sa.String(length=80), nullable=True),
    sa.Column('consent', sa.String(length=60), nullable=True),
    sa.Column('transfer_date', sa.DateTime(), nullable=True),
    sa.Column('affirm_by', sa.String(length=60), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('document_type', postgresql.ENUM('REG_101', 'REG_102', 'REG_103', 'REG_103E', 'ABAN', 'ADDI', 'AFFE', 'ATTA', 'BANK', 'BCLC', 'CAU', 'CAUC', 'CAUE', 'COMP', 'CONF', 'CONV', 'COU', 'COUR', 'DEAT', 'DNCH', 'EXMN', 'EXNR', 'EXRE', 'EXRS', 'FORE', 'FZE', 'GENT', 'INTE', 'INTW', 'LETA', 'MAID', 'MAIL', 'MARR', 'MEAM', 'NAMV', 'NCAN', 'NCON', 'NPUB', 'NRED', 'PDEC', 'PUBA', 'REBU', 'REGC', 'REIV', 'REPV', 'REST', 'STAT', 'SZL', 'TAXN', 'TAXS', 'THAW', 'TRAN', 'VEST', 'WHAL', 'WILL', 'TRANS_LAND_TITLE', 'TRANS_FAMILY_ACT', 'TRANS_INFORMAL_SALE', 'TRANS_QUIT_CLAIM', 'TRANS_SEVER_GRANT', 'TRANS_RECEIVERSHIP', 'TRANS_WRIT_SEIZURE', 'AMEND_PERMIT', 'CANCEL_PERMIT', 'REGC_STAFF', 'REGC_CLIENT', 'REREGISTER_C', name='mhr_document_type'), nullable=False),
    sa.ForeignKeyConstraint(['document_type'], ['mhr_document_types.document_type'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_documents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_documents_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_documents_document_id'), ['document_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_documents_document_registration_number'), ['document_registration_number'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_documents_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_locations',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_location_id_seq'), nullable=False),
    sa.Column('ltsa_description', sa.String(length=1000), nullable=True),
    sa.Column('additional_description', sa.String(length=250), nullable=True),
    sa.Column('dealer_name', sa.String(length=310), nullable=True),
    sa.Column('exception_plan', sa.String(length=150), nullable=True),
    sa.Column('leave_province', sa.String(length=1), nullable=True),
    sa.Column('tax_certification', sa.String(length=1), nullable=True),
    sa.Column('tax_certification_date', sa.DateTime(), nullable=True),
    sa.Column('park_name', sa.String(length=100), nullable=True),
    sa.Column('park_pad', sa.String(length=10), nullable=True),
    sa.Column('pid_number', sa.String(length=9), nullable=True),
    sa.Column('lot', sa.String(length=10), nullable=True),
    sa.Column('parcel', sa.String(length=10), nullable=True),
    sa.Column('block', sa.String(length=10), nullable=True),
    sa.Column('district_lot', sa.String(length=20), nullable=True),
    sa.Column('part_of', sa.String(length=10), nullable=True),
    sa.Column('section', sa.String(length=10), nullable=True),
    sa.Column('township', sa.String(length=10), nullable=True),
    sa.Column('range', sa.String(length=10), nullable=True),
    sa.Column('meridian', sa.String(length=10), nullable=True),
    sa.Column('land_district', sa.String(length=30), nullable=True),
    sa.Column('plan', sa.String(length=20), nullable=True),
    sa.Column('band_name', sa.String(length=150), nullable=True),
    sa.Column('reserve_number', sa.String(length=20), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('location_type', postgresql.ENUM('MANUFACTURER', 'MH_PARK', 'OTHER', 'RESERVE', 'STRATA', name='mhr_location_type'), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'DRAFT', 'HISTORICAL', name='mhr_status_type'), nullable=False),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['location_type'], ['mhr_location_types.location_type'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_status_types.status_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_locations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_locations_address_id'), ['address_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_locations_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_locations_exception_plan'), ['exception_plan'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_locations_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_owner_groups',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_owner_group_id_seq'), nullable=False),
    sa.Column('sequence_number', sa.Integer(), nullable=True),
    sa.Column('interest', sa.String(length=20), nullable=True),
    sa.Column('interest_numerator', sa.Integer(), nullable=True),
    sa.Column('interest_denominator', sa.Integer(), nullable=True),
    sa.Column('tenancy_specified', sa.String(length=1), nullable=False),
    sa.Column('group_sequence_number', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('tenancy_type', postgresql.ENUM('COMMON', 'JOINT', 'NA', 'SOLE', name='mhr_tenancy_type'), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'EXEMPT', 'PREVIOUS', name='mhr_owner_status_type'), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_owner_status_types.status_type'], ),
    sa.ForeignKeyConstraint(['tenancy_type'], ['mhr_tenancy_types.tenancy_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_owner_groups', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_owner_groups_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_owner_groups_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_qualified_suppliers',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_supplier_id_seq'), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('middle_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('business_name', sa.String(length=150), nullable=True),
    sa.Column('dba_name', sa.String(length=150), nullable=True),
    sa.Column('authorization_name', sa.String(length=150), nullable=True),
    sa.Column('account_id', sa.String(length=20), nullable=False),
    sa.Column('email_address', sa.String(length=250), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('phone_extension', sa.String(length=10), nullable=True),
    sa.Column('terms_accepted', sa.String(length=1), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('party_type', postgresql.ENUM('OWNER_BUS', 'OWNER_IND', 'SUBMITTING', 'EXECUTOR', 'ADMINISTRATOR', 'TRUSTEE', 'TRUST', 'MANUFACTURER', 'CONTACT', name='mhr_party_type'), nullable=False),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['party_type'], ['mhr_party_types.party_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_qualified_suppliers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_qualified_suppliers_address_id'), ['address_id'], unique=False)

    op.create_table('mhr_registration_reports',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_registration_report_id_seq'), nullable=False),
    sa.Column('create_ts', sa.DateTime(), nullable=False),
    sa.Column('report_data', sa.JSON(), nullable=False),
    sa.Column('report_type', sa.String(length=30), nullable=False),
    sa.Column('doc_storage_url', sa.String(length=1000), nullable=True),
    sa.Column('batch_storage_url', sa.String(length=1000), nullable=True),
    sa.Column('batch_report_data', sa.JSON(), nullable=True),
    sa.Column('batch_registration_data', sa.JSON(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_registration_reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_registration_reports_create_ts'), ['create_ts'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_registration_reports_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_sections',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_section_id_seq'), nullable=False),
    sa.Column('compressed_key', sa.String(length=6), nullable=False),
    sa.Column('serial_number', sa.String(length=20), nullable=False),
    sa.Column('length_feet', sa.Integer(), nullable=False),
    sa.Column('width_feet', sa.Integer(), nullable=False),
    sa.Column('length_inches', sa.Integer(), nullable=True),
    sa.Column('width_inches', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'DRAFT', 'HISTORICAL', name='mhr_status_type'), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_status_types.status_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_sections', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_sections_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_sections_compressed_key'), ['compressed_key'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_sections_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_notes',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_note_id_seq'), nullable=False),
    sa.Column('remarks', sa.String(length=500), nullable=True),
    sa.Column('destroyed', sa.String(length=1), nullable=True),
    sa.Column('expiry_date', sa.DateTime(), nullable=True),
    sa.Column('effective_ts', sa.DateTime(), nullable=True),
    sa.Column('non_residential_reason', postgresql.ENUM('BURNT', 'DISMANTLED', 'DILAPIDATED', 'OTHER', 'OFFICE', 'STORAGE_SHED', 'BUNKHOUSE', name='exnrreasontype'), nullable=True),
    sa.Column('non_residential_other', sa.String(length=125), nullable=True),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('document_type', postgresql.ENUM('REG_101', 'REG_102', 'REG_103', 'REG_103E', 'ABAN', 'ADDI', 'AFFE', 'ATTA', 'BANK', 'BCLC', 'CAU', 'CAUC', 'CAUE', 'COMP', 'CONF', 'CONV', 'COU', 'COUR', 'DEAT', 'DNCH', 'EXMN', 'EXNR', 'EXRE', 'EXRS', 'FORE', 'FZE', 'GENT', 'INTE', 'INTW', 'LETA', 'MAID', 'MAIL', 'MARR', 'MEAM', 'NAMV', 'NCAN', 'NCON', 'NPUB', 'NRED', 'PDEC', 'PUBA', 'REBU', 'REGC', 'REIV', 'REPV', 'REST', 'STAT', 'SZL', 'TAXN', 'TAXS', 'THAW', 'TRAN', 'VEST', 'WHAL', 'WILL', 'TRANS_LAND_TITLE', 'TRANS_FAMILY_ACT', 'TRANS_INFORMAL_SALE', 'TRANS_QUIT_CLAIM', 'TRANS_SEVER_GRANT', 'TRANS_RECEIVERSHIP', 'TRANS_WRIT_SEIZURE', 'AMEND_PERMIT', 'CANCEL_PERMIT', 'REGC_STAFF', 'REGC_CLIENT', 'REREGISTER_C', name='mhr_document_type'), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'CANCELLED', 'EXPIRED', 'CORRECTED', 'COMPLETED', name='mhr_note_status_type'), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['mhr_documents.id'], ),
    sa.ForeignKeyConstraint(['document_type'], ['mhr_document_types.document_type'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_note_status_types.status_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_notes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_notes_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_notes_document_id'), ['document_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_notes_effective_ts'), ['effective_ts'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_notes_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_parties',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_party_id_seq'), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('middle_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('business_name', sa.String(length=150), nullable=True),
    sa.Column('compressed_name', sa.String(length=30), nullable=False),
    sa.Column('email_address', sa.String(length=250), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('phone_extension', sa.String(length=10), nullable=True),
    sa.Column('suffix', sa.String(length=100), nullable=True),
    sa.Column('description', sa.String(length=150), nullable=True),
    sa.Column('death_cert_number', sa.String(length=20), nullable=True),
    sa.Column('death_ts', sa.DateTime(), nullable=True),
    sa.Column('corp_number', sa.String(length=20), nullable=True),
    sa.Column('death_corp_number', sa.String(length=20), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('change_registration_id', sa.Integer(), nullable=False),
    sa.Column('party_type', postgresql.ENUM('OWNER_BUS', 'OWNER_IND', 'SUBMITTING', 'EXECUTOR', 'ADMINISTRATOR', 'TRUSTEE', 'TRUST', 'MANUFACTURER', 'CONTACT', name='mhr_party_type'), nullable=False),
    sa.Column('status_type', postgresql.ENUM('ACTIVE', 'EXEMPT', 'PREVIOUS', name='mhr_owner_status_type'), nullable=False),
    sa.Column('owner_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['owner_group_id'], ['mhr_owner_groups.id'], ),
    sa.ForeignKeyConstraint(['party_type'], ['mhr_party_types.party_type'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['status_type'], ['mhr_owner_status_types.status_type'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_parties', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_parties_address_id'), ['address_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_parties_business_name'), ['business_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_parties_change_registration_id'), ['change_registration_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_parties_compressed_name'), ['compressed_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_parties_middle_name'), ['middle_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_mhr_parties_registration_id'), ['registration_id'], unique=False)

    op.create_table('mhr_manufacturers',
    sa.Column('id', sa.Integer(), sa.Sequence('mhr_manufacturer_id_seq'), nullable=False),
    sa.Column('manufacturer_name', sa.String(length=150), nullable=False),
    sa.Column('dba_name', sa.String(length=150), nullable=True),
    sa.Column('authorization_name', sa.String(length=150), nullable=True),
    sa.Column('account_id', sa.String(length=20), nullable=True),
    sa.Column('bcol_account', sa.String(length=8), nullable=True),
    sa.Column('terms_accepted', sa.String(length=1), nullable=True),
    sa.Column('registration_id', sa.Integer(), nullable=False),
    sa.Column('submitting_party_id', sa.Integer(), nullable=False),
    sa.Column('owner_party_id', sa.Integer(), nullable=False),
    sa.Column('dealer_party_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['dealer_party_id'], ['mhr_parties.id'], ),
    sa.ForeignKeyConstraint(['owner_party_id'], ['mhr_parties.id'], ),
    sa.ForeignKeyConstraint(['registration_id'], ['mhr_registrations.id'], ),
    sa.ForeignKeyConstraint(['submitting_party_id'], ['mhr_parties.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('mhr_manufacturers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_mhr_manufacturers_registration_id'), ['registration_id'], unique=False)

    # PPR functions
    public_business_name_strip_designation = PGFunction(
        schema="public",
        signature="business_name_strip_designation(actual_name character varying)",
        definition="RETURNS character varying\n LANGUAGE plpgsql\n AS $function$\n DECLARE\n v_base VARCHAR(150);\n BEGIN\n v_base := regexp_replace(regexp_replace(regexp_replace(actual_name,'[^\\w\\s]+','','gi'),'\\y(CORPORATION|INCORPORATED|INCORPOREE|LIMITED|LIMITEE|NON PERSONAL LIABILITY|CORP|INC|LTD|LTEE|NPL|ULC)\\y','','gi'),'\\s+', '', 'gi');\n RETURN TRIM(v_base);\n END\n ;\n  $function$"
    )
    op.create_entity(public_business_name_strip_designation)

    public_get_draft_document_number = PGFunction(
        schema="public",
        signature="get_draft_document_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    DECLARE\n      v_id INTEGER;\n      v_doc_num VARCHAR(10);\n    BEGIN\n      v_id := nextval('document_number_seq');\n      IF v_id >= 10000000 THEN\n        v_doc_num := 'D' || trim(to_char(nextval('document_number_seq'), '00000000'));\n      ELSE\n        v_doc_num := 'D' || trim(to_char(nextval('document_number_seq'), '0000000'));\n      END IF;\n      RETURN v_doc_num;\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_draft_document_number)

    public_get_registration_num = PGFunction(
        schema="public",
        signature="get_registration_num()",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    BEGIN\n        RETURN trim(to_char(nextval('registration_num_q_seq'), '000000')) || 'Q';\n    END\n    ; \n    $$"
    )
    op.create_entity(public_get_registration_num)

    public_searchkey_name_match = PGFunction(
        schema="public",
        signature="searchkey_name_match(search_key IN VARCHAR, name1 IN VARCHAR, name2 IN VARCHAR, name3 IN varchar)",
        definition="RETURNS int\n    LANGUAGE plpgsql\n    AS\n    $$\n    -- Cartesion cross-product on name\\: search key may have up to 3 names, an exact match on any name is a hit.\n    -- search_key is party.first_name_key to match on\\: may be 3 names separated by a space character.\n    -- name1, name2, name3 are names already parsed from the search criteria\\: name2 and name3 may be null. \n    DECLARE\n        v_name1 VARCHAR(50);\n        v_name2 VARCHAR(50);\n        v_name3 VARCHAR(50);\n        v_match_count integer;\n    BEGIN\n        v_match_count := 0;\n        v_name1 = split_part(search_key, ' ', 1);\n        v_name2 = split_part(search_key, ' ', 2);  -- May be null\n        v_name3 = split_part(search_key, ' ', 3);  -- May be null\n        IF (v_name1 = name1 OR (name2 IS NOT NULL AND v_name1 = name2) OR (name3 IS NOT NULL AND v_name1 = name3)) THEN\n        v_match_count := 1;\n        ELSIF (v_name2 IS NOT NULL AND v_name2 = name1 OR (name2 IS NOT NULL AND v_name2 = name2) OR (name3 IS NOT NULL AND v_name2 = name3)) THEN\n        v_match_count := 1;\n        ELSIF (v_name3 IS NOT NULL AND v_name3 = name1 OR (name2 IS NOT NULL AND v_name3 = name2) OR (name3 IS NOT NULL AND v_name3 = name3)) THEN\n        v_match_count := 1;\n        END IF;\n\n        RETURN v_match_count;\n    END\n    ; \n    $$"
    )
    op.create_entity(public_searchkey_name_match)

    public_searchkey_nickname_match = PGFunction(
        schema="public",
        signature="searchkey_nickname_match(search_key IN VARCHAR, name1 IN VARCHAR, name2 IN VARCHAR, name3 IN varchar)",
        definition="RETURNS int\n    LANGUAGE plpgsql\n    AS\n    $$\n    -- Cartesion cross-product on nickname\\: search key may have up to 3 names, a nickname match on any name is a hit.\n    -- search_key is party.first_name_key to match on\\: may be 3 names separated by a space character.\n    -- name1, name2, name3 are names already parsed from the search criteria\\: name2 and name3 may be null. \n    DECLARE\n        v_name1 VARCHAR(50);\n        v_name2 VARCHAR(50);\n        v_name3 VARCHAR(50);\n        v_match_count integer;\n    BEGIN\n        v_match_count := 0;\n        v_name1 = split_part(search_key, ' ', 1);\n        v_name2 = split_part(search_key, ' ', 2);  -- May be null\n        v_name3 = split_part(search_key, ' ', 3);  -- May be null\n        SELECT COUNT(name_id)\n        INTO v_match_count\n        FROM nicknames n1\n        WHERE (name = v_name1 AND \n                n1.name_id IN (SELECT n2.name_id \n                                FROM nicknames n2\n                                WHERE n2.name IN (name1, name2, name3))) OR\n            (v_name2 IS NOT NULL AND\n                name = v_name2 AND \n                n1.name_id IN (SELECT n2.name_id \n                                FROM nicknames n2\n                                WHERE n2.name IN (name1, name2, name3))) OR\n            (v_name3 IS NOT NULL AND\n                name = v_name3 AND \n                n1.name_id IN (SELECT n2.name_id \n                                FROM nicknames n2\n                                WHERE n2.name IN (name1, name2, name3)));\n\n        RETURN v_match_count;\n    END\n    ; \n    $$"
    )
    op.create_entity(public_searchkey_nickname_match)

    public_sim_number = PGFunction(
        schema="public",
        signature="sim_number(actual_name character varying)",
        definition="RETURNS numeric\n LANGUAGE plpgsql\nAS $function$\nDECLARE\n   v_name VARCHAR(60);\n   v_sim_number DECIMAL;\n  BEGIN\n     v_name := regexp_replace(actual_name, '(.)\\1{1,}', '\\1', 'g');\n\n     if length((SELECT public.searchkey_last_name(v_name))) <= 3 then\n\t v_sim_number := .65 ;\n\t else\n\t v_sim_number := .46 ;\n   end if;\n  return v_sim_number;\n  END\n    ; \n    $function$"
    )
    op.create_entity(public_sim_number)

    public_individual_split_1 = PGFunction(
        schema="public",
        signature="individual_split_1(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n  v_last_name VARCHAR(150);\n  v_split_1 VARCHAR(50);\n  BEGIN\n        -- Remove special characters last name\n    v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffix\n\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n       \t-- Split first name\n\tv_last_name := trim(v_last_name);\n    v_split_1 := split_part(v_last_name,' ',1);\n\t  RETURN UPPER(v_split_1);\n\n  END\n    ; \n    $function$"
    )
    op.create_entity(public_individual_split_1)

    public_individual_split_2 = PGFunction(
        schema="public",
        signature="individual_split_2(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n  v_last_name VARCHAR(150);\n  v_split_2 VARCHAR(50);\n    BEGIN\n        -- Remove special characters last name\n        v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Split second name\n         v_split_2 := split_part(v_last_name,' ',2);\n\t  RETURN UPPER(v_split_2);\n\n  END\n    ; \n    $function$"
    )
    op.create_entity(public_individual_split_2)

    public_individual_split_3 = PGFunction(
        schema="public",
        signature="individual_split_3(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n  v_last_name VARCHAR(150);\n  v_split_3 VARCHAR(50);\n    BEGIN\n        -- Remove special characters last name\n        v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Split second name\n         v_split_3 := split_part(v_last_name,' ',3);\n\t  RETURN UPPER(v_split_3);\n\n  END\n    ; \n    $function$"
    )
    op.create_entity(public_individual_split_3)

    public_searchkey_individual = PGFunction(
        schema="public",
        signature="searchkey_individual(last_name character varying, first_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n        v_ind_key VARCHAR(100);\n\t\tv_last_name VARCHAR(50);\n\t\tv_first_name VARCHAR(50);\n    BEGIN\n\t    -- Remove special characters last name\n        v_last_name := regexp_replace(LAST_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_last_name := regexp_replace(v_last_name, '(.)\\1{1,}', '\\1', 'g');\n\t\t-- Remove special characters first name\n        v_first_name := regexp_replace(first_name,'[^\\w]+',' ','gi');\n        -- Remove prefixes first name\n\t\tv_first_name := regexp_replace(v_first_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_first_name := trim(regexp_replace(v_first_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_first_name := regexp_replace(v_first_name, '(.)\\1{1,}', '\\1', 'g');\n\n\t\t-- join last first name\n\t\tv_ind_key := v_last_name||' '||v_first_name;\n\n     RETURN UPPER(v_ind_key);\n    END\n    ; \n    $function$"
    )
    op.create_entity(public_searchkey_individual)

    public_match_individual_name = PGFunction(
        schema="public",
        signature="match_individual_name(lastname character varying,firstname character varying,sq_last real,sq_first real,sq_def real)",
        definition="RETURNS integer[]\n  LANGUAGE plpgsql\n      AS $function$\nDECLARE\n    v_ids  INTEGER ARRAY;\n  BEGIN\n\n    SET pg_trgm.similarity_threshold = 0.29; -- assigning from variable does not work\n\n    WITH q AS (SELECT(SELECT public.searchkey_individual(lastname, firstname)) AS INDKEY,\n               (SELECT public.searchkey_last_name(lastname)) AS search_last_key,              \n              lastname AS LAST,\n              firstname AS FIRST,\n              LENGTH(lastname) AS LAST_LENGTH,\n              LENGTH(firstname) AS FIRST_LENGTH,\n              SUBSTR(firstname,1,1) AS FIRST_CHAR1,\n              SUBSTR(firstname,2,1) AS FIRST_CHAR2,\n              SUBSTR((SELECT(SELECT public.searchkey_individual(lastname, firstname))),1,1) AS INDKEY_CHAR1,\n              (SELECT public.sim_number(lastname)) as simnumber,\n              (SELECT public.individual_split_1(lastname)) AS SPLIT1,\n              (SELECT public.individual_split_2(lastname)) AS SPLIT2,\n              (SELECT public.individual_split_3(lastname)) AS SPLIT3,\n              (SELECT public.individual_split_1(firstname)) AS SPLIT4, \n              (SELECT public.individual_split_2(firstname)) AS SPLIT5\n              )\n    SELECT array_agg(p.id)\n      INTO v_ids\n  FROM PARTIES p,q\n WHERE (p.LAST_NAME_key = search_last_key OR \n        (first_name_key_char1 = INDKEY_CHAR1 AND\n         indkey <% p.FIRST_NAME_KEY AND \n         LEVENSHTEIN(p.FIRST_NAME_KEY,indkey) <= 2)) \n   AND p.PARTY_TYPE = 'DI'\n   AND p.REGISTRATION_ID_END IS NULL\n   AND (\n        (p.FIRST_NAME = FIRST OR p.MIDDLE_INITIAL= FIRST)\n    OR  (p.FIRST_NAME IN (SELECT NAME \n                            FROM public.NICKNAMES \n                           WHERE NAME_ID IN (SELECT NAME_ID \n                                               FROM public.NICKNAMES WHERE(FIRST) = NAME))\n        )\n    OR  (FIRST_LENGTH = 1 AND FIRST_CHAR1 = p.first_name_char1)\n    OR  (FIRST_LENGTH > 1 AND FIRST_CHAR1 = p.first_name_char1 AND p.first_name_char2 IS NOT NULL AND p.first_name_char2 = '-')\n    OR  (FIRST_LENGTH > 1 AND FIRST_CHAR2 IS NOT NULL AND FIRST_CHAR2 = '-' AND FIRST_CHAR1 = p.first_name_char1)\n    OR (p.first_name_char1 = FIRST_CHAR1 AND LENGTH(p.first_name) = 1)\n    OR (indkey <% p.FIRST_NAME_KEY AND\n        SIMILARITY(p.FIRST_NAME_KEY, indkey) >= SIMNUMBER AND \n        p.first_name_key_char1 = INDKEY_CHAR1 AND \n        ((FIRST <% p.first_name AND \n          SIMILARITY(p.FIRST_NAME,FIRST)>= sq_first AND \n          (LAST_LENGTH BETWEEN LENGTH(p.LAST_NAME)-3 AND LENGTH(p.LAST_NAME)+3 OR LAST_LENGTH >= 10)) OR\n          (p.first_name_char1 = FIRST_CHAR1 OR P.FIRST_NAME = FIRST_CHAR1))          \n       )\n    OR (FIRST <% p.first_name AND\n        SIMILARITY(p.FIRST_NAME,FIRST)>= sq_first AND \n        (p.last_name_split1 = SPLIT1 OR \n         p.last_name_split2 = SPLIT1 and p.last_name_split2 != '' OR\n         p.last_name_split3 = SPLIT1 and p.last_name_split3 != '' OR\n         p.last_name_split1 = SPLIT2 OR \n         p.last_name_split2 = SPLIT2 and p.last_name_split2 != '' OR\n         p.last_name_split3 = SPLIT2 and p.last_name_split3 != '' OR\n         p.last_name_split1 = SPLIT3 OR \n         p.last_name_split2 = SPLIT3 and p.last_name_split2 != '' OR\n         p.last_name_split3 = SPLIT3 and p.last_name_split3 != ''\n        )\n       )       \n    OR (LAST <% p.LAST_NAME AND\n        SIMILARITY(p.LAST_NAME,LAST)>= SIMNUMBER AND \n        (p.first_name_split1 = SPLIT4 OR\n         p.first_name_split2 = SPLIT4 and p.first_name_split2 != '' OR\n         p.first_name_split1 = SPLIT5 OR\n         p.first_name_split2 = SPLIT5 and p.first_name_split2 != ''\n        )\n       )\n    )\n    ;\n    RETURN v_ids;\n  END\n    ; \n    $function$"
    )
    op.create_entity(public_match_individual_name)

    public_searchkey_aircraft = PGFunction(
        schema="public",
        signature="searchkey_aircraft(aircraft_number IN VARCHAR)",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    DECLARE\n        v_search_key VARCHAR(25);\n    BEGIN\n        v_search_key := TRIM(REGEXP_REPLACE(aircraft_number,'\\s|-','','gi'));\n        IF (LENGTH(v_search_key) > 6) THEN\n        v_search_key := RIGHT(v_search_key, 6);\n        END IF;\n        RETURN v_search_key;\n    END\n    ; \n    $$"
    )
    op.create_entity(public_searchkey_aircraft)

    public_searchkey_business_name = PGFunction(
        schema="public",
        signature="searchkey_business_name(actual_name IN VARCHAR)",
        definition="RETURNS character varying\n LANGUAGE plpgsql\nAS $function$\nDECLARE\n    v_search_key VARCHAR(150);\n    v_name_2  VARCHAR(150);\n    v_name_3  VARCHAR(150);\n    v_name_4  VARCHAR(150);\n    v_name_5  VARCHAR(150);\n    v_word_1  VARCHAR(150);\n    v_word_2  VARCHAR(150);\n    v_word_3  VARCHAR(150);\n    v_word_4  VARCHAR(150);\n\t\nBEGIN\n    IF LENGTH(SPLIT_PART(REGEXP_REPLACE(actual_name,'[A-Z]+','','g'),' ',1))>=5 then\n        v_search_key := REGEXP_REPLACE(actual_name,'^0000|^000|^00|^0','','g');\n        v_search_key := REGEXP_REPLACE(SPLIT_PART(v_search_key,' ',1),'[A-Za-z]+','','g');\n        v_search_key := REGEXP_REPLACE(v_search_key,'[^\\w\\s]+','','gi');\n    END IF;\n\n    IF  array_length(string_to_array(v_search_key,''),1) is not null then\n        RETURN v_search_key;\n    ELSE\n        v_search_key := split_part(upper(actual_name), 'INC', 1);\n        v_search_key := split_part(upper(v_search_key), 'LTD', 1);\n        v_search_key := split_part(upper(v_search_key), 'LTEE', 1);\n        v_search_key := split_part(upper(v_search_key), 'LIMITED', 1);\n        v_search_key := split_part(upper(v_search_key), 'INCORPORATED', 1);\n        v_search_key := split_part(upper(v_search_key), 'INCORPORATEE', 1);\n        v_search_key := split_part(upper(v_search_key), 'INCORPORATION', 1);\n\t\tv_search_key := regexp_replace(v_search_key, '\\([^()]*\\)', '', 'gi');\n        v_search_key := regexp_replace(v_search_key,'^THE','','gi');\n        v_search_key := regexp_replace(v_search_key,'\\y(AND|DBA)\\y', '', 'g');\n        v_search_key := REGEXP_REPLACE(v_search_key,'[^\\w\\s]+',' ','gi');\n        v_search_key := TRIM(REGEXP_REPLACE(v_search_key, '\\s+', ' ', 'gi'));\n        v_search_key := REGEXP_REPLACE(v_search_key,'\\y( S$)\\y','','gi');\n    END IF;\n\n    IF SUBSTR(v_search_key,2,1)=' ' AND SUBSTR(v_search_key,4,1)=' ' AND SUBSTR(v_search_key,6,1)!=' ' THEN\n        v_search_key := TRIM(REGEXP_REPLACE(SUBSTR(v_search_key,1,3),'\\s+', '', 'gi'))||SUBSTR(v_search_key,4,146);\n    ELSIF SUBSTR(v_search_key,2,1)=' ' AND SUBSTR(v_search_key,4,1)=' ' AND SUBSTR(v_search_key,6,1)=' ' THEN \n        v_search_key := TRIM(REGEXP_REPLACE(SUBSTR(v_search_key,1,3),'\\s+', '', 'gi'))||SUBSTR(v_search_key,5,145);\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n\n    v_name_2 := SPLIT_PART(v_search_key,' ',2);\n    v_name_3 := SPLIT_PART(v_search_key,' ',3);\n    v_name_4 := SPLIT_PART(v_search_key,' ',4);\n    v_name_5 := SPLIT_PART(v_search_key,' ',5);\n    v_word_1 := (select word from common_word where word = v_name_2 );\n    v_word_2 := (select word from common_word where word = v_name_3 );\n    v_word_3 := (select word from common_word where word = v_name_4 );\n    v_word_4 := (select word from common_word where word = v_name_5 );\n\n   \n\n    IF v_word_2 is not null THEN\n        v_search_key := regexp_replace(v_search_key,v_word_2,'','ig');\n    ELSE    \n        v_search_key := v_search_key;\n    END IF;\n\n    IF v_word_3 is not null THEN\n    v_search_key := regexp_replace(v_search_key,v_word_3,'','ig');\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n\n    IF v_word_4 is not null THEN\n        v_search_key := regexp_replace(v_search_key,v_word_4,'','ig');\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n    \n    IF  v_search_key is null or LENGTH(TRIM(v_search_key)) = 0 THEN\n        v_search_key := actual_name;\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(BRITISH COLUMBIA|BRITISHCOLUMBIA)\\y','BC','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(LIMITED|PARTNERSHIP|GP|LLP|LP)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(SOCIETY|ASSOCIATION|TRUST|TRUSTEE|SOCIETE)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(INCORPORATED|INCORPOREE|INCORPORATION|INCORP|INC)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(COMPANY|CORPORATIONS|CORPORATION|CORPS|CORP|CO)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(LIMITEE|LTEE|LTD|ULC)\\y','','gi');\n\tv_search_key := regexp_replace(v_search_key,'\\y(AND)\\y','AN','gi');\n\tv_search_key := regexp_replace(v_search_key,'&','AN','gi');\n\tv_search_key := regexp_replace(v_search_key, '\\([^()]*\\)', '', 'gi');\n    v_search_key := regexp_replace(v_search_key,'^THE','','gi');\n    v_search_key := regexp_replace(v_search_key,'\\y(DBA)\\y', '', 'g');\n\tv_search_key := REGEXP_REPLACE(v_search_key,'[^\\w\\s]+','','gi');\n    v_search_key := trim(regexp_replace(v_search_key, '\\s+', '', 'gi'));\n\t\n    RETURN v_search_key;\n\nEND\n    ; \n$function$"
    )
    op.create_entity(public_searchkey_business_name)

    public_searchkey_first_name = PGFunction(
        schema="public",
        signature="searchkey_first_name(actual_name IN character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS\n    $$\nDECLARE\n        v_search_key VARCHAR(92);\n    BEGIN\n        -- Remove special characters first name\n        v_search_key := regexp_replace(actual_name,'[^\\w]+',' ','gi');\n        -- Remove prefixes first name\n\t\tv_search_key := regexp_replace(v_first_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_search_key := trim(regexp_replace(v_first_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_search_key := regexp_replace(v_first_name, '(.)\\1{1,}', '\\1', 'g');\n        RETURN UPPER(v_search_key);\n    END\n    ; \n    $$"
    )
    op.create_entity(public_searchkey_first_name)

    public_searchkey_last_name = PGFunction(
        schema="public",
        signature="searchkey_last_name(actual_name IN character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    COST 100\n    VOLATILE PARALLEL UNSAFE\n    AS\n    $$\nDECLARE\n        v_last_name VARCHAR(60);\n    BEGIN\n        -- Remove special characters last name\n        v_last_name := regexp_replace(actual_name,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_last_name := regexp_replace(v_last_name, '(.)\\1{1,}', '\\1', 'g');\n\t\t-- Remove special characters first name\n     RETURN UPPER(v_last_name);\n    END\n    ; \n    $$"
    )
    op.create_entity(public_searchkey_last_name)

    public_searchkey_mhr = PGFunction(
        schema="public",
        signature="searchkey_mhr(mhr_number IN VARCHAR)",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    DECLARE\n        v_search_key VARCHAR(6);\n    BEGIN\n        v_search_key := TRIM(REGEXP_REPLACE(mhr_number,'[^0-9A-Za-z]','','gi'));\n        v_search_key := LPAD(REGEXP_REPLACE(v_search_key,'[$A-Za-z]','0'),6,'0');\n        RETURN v_search_key;\n    END\n    ; \n    $$"
    )
    op.create_entity(public_searchkey_mhr)

    public_searchkey_vehicle = PGFunction(
        schema="public",
        signature="searchkey_vehicle(serial_number IN VARCHAR)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $$\n    DECLARE\n            v_search_key VARCHAR(25);\n            BEGIN\n            v_search_key := REGEXP_REPLACE(serial_number, '[^0-9A-Za-z]','','gi');\n            v_search_key := LPAD(SUBSTR(v_search_key, LENGTH(v_search_key) - 5, 6),6,'0');\n            v_search_key := REGEXP_REPLACE(\n                            REGEXP_REPLACE(\n                            REGEXP_REPLACE(\n                            REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                    REGEXP_REPLACE(\n                                    REGEXP_REPLACE(\n                                    REGEXP_REPLACE(v_search_key,'I','1','gi'),\n                                                    'L','1','gi'),\n                                                    'Z','2','gi'),\n                                                    'H','4','gi'),\n                                                    'Y','4','gi'),\n                                                    'S','5','gi'),\n                                                    'C','6','gi'),\n                                                    'G','6','gi'),\n                                                    'B','8','gi'),\n                                                    'O','0','gi'),\n                                                    '[^\\w]+|[A-Za-z]+','0','gi');\n                v_search_key := LPAD(v_search_key,6,'0');\t\t\t\t\t\t\t\t\t\t\t \n            RETURN v_search_key;\n        END\n        ;\n    $$"
    )
    op.create_entity(public_searchkey_vehicle)

    # MHR functions
    public_get_mhr_draft_number = PGFunction(
        schema="public",
        signature="get_mhr_draft_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_draft_number_seq'), '000000'));\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_mhr_draft_number)

    public_get_mhr_number = PGFunction(
        schema="public",
        signature="get_mhr_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_number_seq'), '000000'));\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_mhr_number)

    public_get_mhr_doc_reg_number = PGFunction(
        schema="public",
        signature="get_mhr_doc_reg_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_reg_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_mhr_doc_reg_number)

    public_get_mhr_doc_manufacturer_id = PGFunction(
        schema="public",
        signature="get_mhr_doc_manufacturer_id()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_id_manufacturer_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_mhr_doc_manufacturer_id)

    public_get_mhr_doc_qualified_id = PGFunction(
        schema="public",
        signature="get_mhr_doc_qualified_id()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_id_qualified_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_mhr_doc_qualified_id)

    public_get_mhr_doc_gov_agent_id = PGFunction(
        schema="public",
        signature="get_mhr_doc_gov_agent_id()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_id_gov_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.create_entity(public_get_mhr_doc_gov_agent_id)

    public_mhr_name_compressed_key = PGFunction(
        schema="public",
        signature="mhr_name_compressed_key(v_name character varying)",
        definition="RETURNS character varying\n  IMMUTABLE\n  LANGUAGE plpgsql\n  AS\n  $$\n    declare\n    v_key VARCHAR(250);\n    begin\n    v_key := upper(v_name);\n    if position(left(v_key, 1) in '&#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') < 1 then\n        v_key := substring(v_key, 2);\n    end if;\n    if left(v_key, 4) = 'THE ' then\n        v_key := substring(v_key, 5);\n    end if;\n    v_key := regexp_replace(v_key, '[^0-9A-Z&#]+', '', 'gi');\n    if left(v_key, 15) = 'BRITISHCOLUMBIA' then\n        v_key := 'BC' || substring(v_key, 16);\n    end if;\n    v_key := replace(v_key, '#', 'NUMBER');\n    v_key := replace(v_key, '&', 'AND');\n    v_key := replace(v_key, '0', 'ZERO');\n    v_key := replace(v_key, '1', 'ONE');\n    v_key := replace(v_key, '2', 'TWO');\n    v_key := replace(v_key, '3', 'THREE');\n    v_key := replace(v_key, '4', 'FOUR');\n    v_key := replace(v_key, '5', 'FIVE');\n    v_key := replace(v_key, '6', 'SIX');\n    v_key := replace(v_key, '7', 'SEVEN');\n    v_key := replace(v_key, '8', 'EIGHT');\n    v_key := replace(v_key, '9', 'NINE');\n    if length(v_key) > 30 then\n        v_key := substring(v_key, 1, 30);\n    end if;\n    return v_key;\n    end;\n  $$"
    )
    op.create_entity(public_mhr_name_compressed_key)

    public_mhr_serial_compressed_key = PGFunction(
        schema="public",
        signature="mhr_serial_compressed_key(v_serial character varying)",
        definition="RETURNS character varying\n  IMMUTABLE\n  LANGUAGE plpgsql\n  AS\n  $$\n    declare\n    v_key VARCHAR(40);\n    last_pos integer := 6;\n    i integer := 1;\n    begin\n    v_key := upper(v_serial);\n    v_key := REGEXP_REPLACE(v_key, '[^0-9A-Za-z]','','gi');\n    v_key := '000000' || v_key;\n    for i in 1 .. LENGTH(v_key)\n    loop\n        if POSITION(substring(v_key, i, 1) in '0123456789') > 0 then\n        last_pos := i;\n        end if;\n    end loop;\n    v_key := replace(v_key, 'B', '8');\n    v_key := replace(v_key, 'C', '6');\n    v_key := replace(v_key, 'G', '6');\n    v_key := replace(v_key, 'H', '4');\n    v_key := replace(v_key, 'I', '1');\n    v_key := replace(v_key, 'L', '1');\n    v_key := replace(v_key, 'S', '5');\n    v_key := replace(v_key, 'Y', '4');\n    v_key := replace(v_key, 'Z', '2');\n    v_key := REGEXP_REPLACE(v_key, '[^0-9]','0','gi');\n    v_key := substring(v_key, last_pos - 5, 6);\n    return v_key;\n    end;\n  $$"
    )
    op.create_entity(public_mhr_serial_compressed_key)

    # ### Manually add type table data ###

    # PPR type table inserts
    op.bulk_insert(party_type,
      [
        { 'party_type': 'DB', 'party_type_desc': 'BUSINESS DEBTOR' },
        { 'party_type': 'DI', 'party_type_desc': 'INDIVIDUAL DEBTOR' },
        { 'party_type': 'RG', 'party_type_desc': 'REGISTERING PARTY' },
        { 'party_type': 'SP', 'party_type_desc': 'SECURED PARTY' }
      ]
    )
    op.bulk_insert(search_type,
      [
        { 'search_type': 'AC', 'search_type_desc': 'AIRCRAFT AIRFRAME D.O.T. NUMBER' },
        { 'search_type': 'BS', 'search_type_desc': 'BUSINESS DEBTOR NAME' },
        { 'search_type': 'IS', 'search_type_desc': 'INDIVIDUAL DEBTOR NAME' },
        { 'search_type': 'MH', 'search_type_desc': 'MANUFACTURED HOME REGISTRATION NUMBER' },
        { 'search_type': 'RG', 'search_type_desc': 'REGISTRATION NUMBER' },
        { 'search_type': 'SS', 'search_type_desc': 'SERIAL NUMBER SEARCH' },
        { 'search_type': 'MI', 'search_type_desc': 'MHR search by owner name' },
        { 'search_type': 'MM', 'search_type_desc': 'MHR search by MHR number' },
        { 'search_type': 'MO', 'search_type_desc': 'MHR search by organization name' },
        { 'search_type': 'MS', 'search_type_desc': 'MHR search by serial number' }
      ]
    )
    op.bulk_insert(serial_type,
      [
        { 'serial_type': 'AC', 'serial_type_desc': 'AIRCRAFT' },
        { 'serial_type': 'AF', 'serial_type_desc': 'AIRCRAFT AIRFRAME' },
        { 'serial_type': 'AP', 'serial_type_desc': 'AIRPLANE' },
        { 'serial_type': 'BO', 'serial_type_desc': 'BOAT' },
        { 'serial_type': 'EV', 'serial_type_desc': 'ELECTRIC MOTOR VEHICLE' },
        { 'serial_type': 'MH', 'serial_type_desc': 'MANUFACTURED HOME' },
        { 'serial_type': 'MV', 'serial_type_desc': 'MOTOR VEHICLE' },
        { 'serial_type': 'OB', 'serial_type_desc': 'OUTBOARD BOAT MOTOR' },
        { 'serial_type': 'TR', 'serial_type_desc': 'TRAILER' }
      ]
    )
    op.bulk_insert(state_type,
      [
        { 'state_type': 'ACT', 'state_type_desc': 'ACTIVE' },
        { 'state_type': 'HEX', 'state_type_desc': 'REGISTRATION HAS EXPIRED' },
        { 'state_type': 'HDC', 'state_type_desc': 'REGISTRATION DISCHARGED' }
      ]
    )
    op.bulk_insert(event_tracking_type,
      [
        { 'event_tracking_type': 'SEARCH_REPORT', 'event_tracking_desc': 'Search Detail large report generation and storage.' },
        { 'event_tracking_type': 'API_NOTIFICATION', 'event_tracking_desc': 'Notification by API callback of successful event outcome.' },
        { 'event_tracking_type': 'EMAIL', 'event_tracking_desc': 'Email notification.' },
        { 'event_tracking_type': 'SURFACE_MAIL', 'event_tracking_desc': 'Surface mail delivery of report to service provider.' },
        { 'event_tracking_type': 'EMAIL_REPORT', 'event_tracking_desc': 'Email delivery of report.' },
        { 'event_tracking_type': 'REGISTRATION_REPORT', 'event_tracking_desc': 'Registration Verification Statement generation and storage.' },
        { 'event_tracking_type': 'MHR_REG_REPORT', 'event_tracking_desc': 'MHR registration report generation and storage.' },
        { 'event_tracking_type': 'REG_HIST_JOB', 'event_tracking_desc': 'Job to updated account IDs when registrations become historical.' }
      ]
    )
    op.bulk_insert(securities_act_type,
      [
        { 'securities_act_type': 'PRESERVATION', 'securities_act_type_desc': 'PRESERVATION ORDER' },
        { 'securities_act_type': 'LIEN', 'securities_act_type_desc': 'NOTICE OF LIEN AND CHARGE' },
        { 'securities_act_type': 'PROCEEDINGS', 'securities_act_type_desc': 'NOTICE OF ORDER OR PROCEEDINGS' }
      ]
    )
    op.bulk_insert(country_type,
      [
        {
          'country_type': 'AD',
          'country_desc': 'ANDORRA'
        },
        {
          'country_type': 'AE',
          'country_desc': 'UNITED ARAB EMIRATES'
        },
        {
          'country_type': 'AF',
          'country_desc': 'AFGHANISTAN'
        },
        {
          'country_type': 'AG',
          'country_desc': 'ANTIGUA AND BARBUDA'
        },
        {
          'country_type': 'AI',
          'country_desc': 'ANGUILLA'
        },
        {
          'country_type': 'AL',
          'country_desc': 'ALBANIA'
        },
        {
          'country_type': 'AM',
          'country_desc': 'ARMENIA'
        },
        {
          'country_type': 'AN',
          'country_desc': 'NETHERLANDS ANTILLES'
        },
        {
          'country_type': 'AO',
          'country_desc': 'ANGOLA'
        },
        {
          'country_type': 'AQ',
          'country_desc': 'ANTARCTICA'
        },
        {
          'country_type': 'AR',
          'country_desc': 'ARGENTINA'
        },
        {
          'country_type': 'AS',
          'country_desc': 'AMERICAN SAMOA'
        },
        {
          'country_type': 'AT',
          'country_desc': 'AUSTRIA'
        },
        {
          'country_type': 'AU',
          'country_desc': 'AUSTRALIA'
        },
        {
          'country_type': 'AW',
          'country_desc': 'ARUBA'
        },
        {
          'country_type': 'AX',
          'country_desc': 'ALAND ISLANDS'
        },
        {
          'country_type': 'AZ',
          'country_desc': 'AZERBAIJAN'
        },
        {
          'country_type': 'BA',
          'country_desc': 'BOSNIA AND HERZEGOVINA'
        },
        {
          'country_type': 'BB',
          'country_desc': 'BARBADOS'
        },
        {
          'country_type': 'BD',
          'country_desc': 'BANGLADESH'
        },
        {
          'country_type': 'BE',
          'country_desc': 'BELGIUM'
        },
        {
          'country_type': 'BF',
          'country_desc': 'BURKINA FASO'
        },
        {
          'country_type': 'BG',
          'country_desc': 'BULGARIA'
        },
        {
          'country_type': 'BH',
          'country_desc': 'BAHRAIN'
        },
        {
          'country_type': 'BI',
          'country_desc': 'BURUNDI'
        },
        {
          'country_type': 'BJ',
          'country_desc': 'BENIN'
        },
        {
          'country_type': 'BL',
          'country_desc': 'SAINT BARTHELEMY'
        },
        {
          'country_type': 'BM',
          'country_desc': 'BERMUDA'
        },
        {
          'country_type': 'BN',
          'country_desc': 'BRUNEI DARUSSALAM'
        },
        {
          'country_type': 'BO',
          'country_desc': 'BOLIVIA'
        },
        {
          'country_type': 'BQ',
          'country_desc': 'BONAIRE, ST EUSTATIUS AND SABA'
        },
        {
          'country_type': 'BR',
          'country_desc': 'BRAZIL'
        },
        {
          'country_type': 'BS',
          'country_desc': 'BAHAMAS'
        },
        {
          'country_type': 'BT',
          'country_desc': 'BHUTAN'
        },
        {
          'country_type': 'BV',
          'country_desc': 'BOUVET ISLAND'
        },
        {
          'country_type': 'BW',
          'country_desc': 'BOTSWANA'
        },
        {
          'country_type': 'BY',
          'country_desc': 'BELARUS'
        },
        {
          'country_type': 'BZ',
          'country_desc': 'BELIZE'
        },
        {
          'country_type': 'CA',
          'country_desc': 'CANADA'
        },
        {
          'country_type': 'CC',
          'country_desc': 'COCOS (KEELING) ISLANDS'
        },
        {
          'country_type': 'CD',
          'country_desc': 'CONGO, THE DEMOCRATIC REPUBLIC OF THE'
        },
        {
          'country_type': 'CF',
          'country_desc': 'CENTRAL AFRICAN REPUBLIC'
        },
        {
          'country_type': 'CG',
          'country_desc': 'CONGO'
        },
        {
          'country_type': 'CH',
          'country_desc': 'SWITZERLAND'
        },
        {
          'country_type': 'CI',
          'country_desc': 'COTE D''IVOIRE'
        },
        {
          'country_type': 'CK',
          'country_desc': 'COOK ISLANDS'
        },
        {
          'country_type': 'CL',
          'country_desc': 'CHILE'
        },
        {
          'country_type': 'CM',
          'country_desc': 'CAMEROON'
        },
        {
          'country_type': 'CN',
          'country_desc': 'CHINA'
        },
        {
          'country_type': 'CO',
          'country_desc': 'COLOMBIA'
        },
        {
          'country_type': 'CR',
          'country_desc': 'COSTA RICA'
        },
        {
          'country_type': 'CU',
          'country_desc': 'CUBA'
        },
        {
          'country_type': 'CV',
          'country_desc': 'CAPE VERDE'
        },
        {
          'country_type': 'CW',
          'country_desc': 'CURACAO'
        },
        {
          'country_type': 'CX',
          'country_desc': 'CHRISTMAS ISLAND'
        },
        {
          'country_type': 'CY',
          'country_desc': 'CYPRUS'
        },
        {
          'country_type': 'CZ',
          'country_desc': 'CZECH REPUBLIC'
        },
        {
          'country_type': 'DE',
          'country_desc': 'GERMANY'
        },
        {
          'country_type': 'DJ',
          'country_desc': 'DJIBOUTI'
        },
        {
          'country_type': 'DK',
          'country_desc': 'DENMARK'
        },
        {
          'country_type': 'DM',
          'country_desc': 'DOMINICA'
        },
        {
          'country_type': 'DO',
          'country_desc': 'DOMINICAN REPUBLIC'
        },
        {
          'country_type': 'DZ',
          'country_desc': 'ALGERIA'
        },
        {
          'country_type': 'EC',
          'country_desc': 'ECUADOR'
        },
        {
          'country_type': 'EE',
          'country_desc': 'ESTONIA'
        },
        {
          'country_type': 'EG',
          'country_desc': 'EGYPT'
        },
        {
          'country_type': 'EH',
          'country_desc': 'WESTERN SAHARA'
        },
        {
          'country_type': 'ER',
          'country_desc': 'ERITREA'
        },
        {
          'country_type': 'ES',
          'country_desc': 'SPAIN'
        },
        {
          'country_type': 'ET',
          'country_desc': 'ETHIOPIA'
        },
        {
          'country_type': 'FI',
          'country_desc': 'FINLAND'
        },
        {
          'country_type': 'FJ',
          'country_desc': 'FIJI'
        },
        {
          'country_type': 'FK',
          'country_desc': 'FALKLAND ISLANDS (MALVINAS)'
        },
        {
          'country_type': 'FM',
          'country_desc': 'MICRONESIA, FEDERATED STATES OF'
        },
        {
          'country_type': 'FO',
          'country_desc': 'FAROE ISLANDS'
        },
        {
          'country_type': 'FR',
          'country_desc': 'FRANCE'
        },
        {
          'country_type': 'FX',
          'country_desc': 'FRANCE, METROPOLITAN'
        },
        {
          'country_type': 'GA',
          'country_desc': 'GABON'
        },
        {
          'country_type': 'GB',
          'country_desc': 'UNITED KINGDOM'
        },
        {
          'country_type': 'GD',
          'country_desc': 'GRENADA'
        },
        {
          'country_type': 'GE',
          'country_desc': 'GEORGIA'
        },
        {
          'country_type': 'GF',
          'country_desc': 'FRENCH GUIANA'
        },
        {
          'country_type': 'GG',
          'country_desc': 'GUERNSEY'
        },
        {
          'country_type': 'GH',
          'country_desc': 'GHANA'
        },
        {
          'country_type': 'GI',
          'country_desc': 'GIBRALTAR'
        },
        {
          'country_type': 'GL',
          'country_desc': 'GREENLAND'
        },
        {
          'country_type': 'GM',
          'country_desc': 'GAMBIA'
        },
        {
          'country_type': 'GN',
          'country_desc': 'GUINEA'
        },
        {
          'country_type': 'GP',
          'country_desc': 'GUADELOUPE'
        },
        {
          'country_type': 'GQ',
          'country_desc': 'EQUATORIAL GUINEA'
        },
        {
          'country_type': 'GR',
          'country_desc': 'GREECE'
        },
        {
          'country_type': 'GS',
          'country_desc': 'SOUTH GEORGIA AND THE SOUTH SANDWICH ISL'
        },
        {
          'country_type': 'GT',
          'country_desc': 'GUATEMALA'
        },
        {
          'country_type': 'GU',
          'country_desc': 'GUAM'
        },
        {
          'country_type': 'GW',
          'country_desc': 'GUINEA-BISSAU'
        },
        {
          'country_type': 'GY',
          'country_desc': 'GUYANA'
        },
        {
          'country_type': 'HK',
          'country_desc': 'HONG KONG'
        },
        {
          'country_type': 'HM',
          'country_desc': 'HEARD ISLAND AND MCDONALD ISLANDS'
        },
        {
          'country_type': 'HN',
          'country_desc': 'HONDURAS'
        },
        {
          'country_type': 'HR',
          'country_desc': 'CROATIA'
        },
        {
          'country_type': 'HT',
          'country_desc': 'HAITI'
        },
        {
          'country_type': 'HU',
          'country_desc': 'HUNGARY'
        },
        {
          'country_type': 'ID',
          'country_desc': 'INDONESIA'
        },
        {
          'country_type': 'IE',
          'country_desc': 'IRELAND'
        },
        {
          'country_type': 'IL',
          'country_desc': 'ISRAEL'
        },
        {
          'country_type': 'IM',
          'country_desc': 'ISLE OF MAN'
        },
        {
          'country_type': 'IN',
          'country_desc': 'INDIA'
        },
        {
          'country_type': 'IO',
          'country_desc': 'BRITISH INDIAN OCEAN TERRITORY'
        },
        {
          'country_type': 'IQ',
          'country_desc': 'IRAQ'
        },
        {
          'country_type': 'IR',
          'country_desc': 'IRAN, ISLAMIC REPUBLIC OF'
        },
        {
          'country_type': 'IS',
          'country_desc': 'ICELAND'
        },
        {
          'country_type': 'IT',
          'country_desc': 'ITALY'
        },
        {
          'country_type': 'JE',
          'country_desc': 'JERSEY'
        },
        {
          'country_type': 'JM',
          'country_desc': 'JAMAICA'
        },
        {
          'country_type': 'JO',
          'country_desc': 'JORDAN'
        },
        {
          'country_type': 'JP',
          'country_desc': 'JAPAN'
        },
        {
          'country_type': 'KE',
          'country_desc': 'KENYA'
        },
        {
          'country_type': 'KG',
          'country_desc': 'KYRGYZSTAN'
        },
        {
          'country_type': 'KH',
          'country_desc': 'CAMBODIA'
        },
        {
          'country_type': 'KI',
          'country_desc': 'KIRIBATI'
        },
        {
          'country_type': 'KM',
          'country_desc': 'COMOROS'
        },
        {
          'country_type': 'KN',
          'country_desc': 'SAINT KITTS AND NEVIS'
        },
        {
          'country_type': 'KP',
          'country_desc': 'KOREA, DEMOCRATIC PEOPLE''S REPUBLIC OF'
        },
        {
          'country_type': 'KR',
          'country_desc': 'KOREA, REPUBLIC OF'
        },
        {
          'country_type': 'KW',
          'country_desc': 'KUWAIT'
        },
        {
          'country_type': 'KY',
          'country_desc': 'CAYMAN ISLANDS'
        },
        {
          'country_type': 'KZ',
          'country_desc': 'KAZAKHSTAN'
        },
        {
          'country_type': 'LA',
          'country_desc': 'LAO PEOPLE''S DEMOCRATIC REPUBLIC'
        },
        {
          'country_type': 'LB',
          'country_desc': 'LEBANON'
        },
        {
          'country_type': 'LC',
          'country_desc': 'SAINT LUCIA'
        },
        {
          'country_type': 'LI',
          'country_desc': 'LIECHTENSTEIN'
        },
        {
          'country_type': 'LK',
          'country_desc': 'SRI LANKA'
        },
        {
          'country_type': 'LR',
          'country_desc': 'LIBERIA'
        },
        {
          'country_type': 'LS',
          'country_desc': 'LESOTHO'
        },
        {
          'country_type': 'LT',
          'country_desc': 'LITHUANIA'
        },
        {
          'country_type': 'LU',
          'country_desc': 'LUXEMBOURG'
        },
        {
          'country_type': 'LV',
          'country_desc': 'LATVIA'
        },
        {
          'country_type': 'LY',
          'country_desc': 'LIBYA'
        },
        {
          'country_type': 'MA',
          'country_desc': 'MOROCCO'
        },
        {
          'country_type': 'MC',
          'country_desc': 'MONACO'
        },
        {
          'country_type': 'MD',
          'country_desc': 'MOLDOVA, REPUBLIC OF'
        },
        {
          'country_type': 'ME',
          'country_desc': 'MONTENEGRO'
        },
        {
          'country_type': 'MF',
          'country_desc': 'SAINT MARTIN(FRENCH PART)'
        },
        {
          'country_type': 'MG',
          'country_desc': 'MADAGASCAR'
        },
        {
          'country_type': 'MH',
          'country_desc': 'MARSHALL ISLANDS'
        },
        {
          'country_type': 'MK',
          'country_desc': 'MACEDONIA, THE FORMER YUGOSLAV REPUBLIC '
        },
        {
          'country_type': 'ML',
          'country_desc': 'MALI'
        },
        {
          'country_type': 'MM',
          'country_desc': 'MYANMAR'
        },
        {
          'country_type': 'MN',
          'country_desc': 'MONGOLIA'
        },
        {
          'country_type': 'MO',
          'country_desc': 'MACAO'
        },
        {
          'country_type': 'MP',
          'country_desc': 'NORTHERN MARIANA ISLANDS'
        },
        {
          'country_type': 'MQ',
          'country_desc': 'MARTINIQUE'
        },
        {
          'country_type': 'MR',
          'country_desc': 'MAURITANIA'
        },
        {
          'country_type': 'MS',
          'country_desc': 'MONTSERRAT'
        },
        {
          'country_type': 'MT',
          'country_desc': 'MALTA'
        },
        {
          'country_type': 'MU',
          'country_desc': 'MAURITIUS'
        },
        {
          'country_type': 'MV',
          'country_desc': 'MALDIVES'
        },
        {
          'country_type': 'MW',
          'country_desc': 'MALAWI'
        },
        {
          'country_type': 'MX',
          'country_desc': 'MEXICO'
        },
        {
          'country_type': 'MY',
          'country_desc': 'MALAYSIA'
        },
        {
          'country_type': 'MZ',
          'country_desc': 'MOZAMBIQUE'
        },
        {
          'country_type': 'NA',
          'country_desc': 'NAMIBIA'
        },
        {
          'country_type': 'NC',
          'country_desc': 'NEW CALEDONIA'
        },
        {
          'country_type': 'NE',
          'country_desc': 'NIGER'
        },
        {
          'country_type': 'NF',
          'country_desc': 'NORFOLK ISLAND'
        },
        {
          'country_type': 'NG',
          'country_desc': 'NIGERIA'
        },
        {
          'country_type': 'NI',
          'country_desc': 'NICARAGUA'
        },
        {
          'country_type': 'NL',
          'country_desc': 'NETHERLANDS'
        },
        {
          'country_type': 'NO',
          'country_desc': 'NORWAY'
        },
        {
          'country_type': 'NP',
          'country_desc': 'NEPAL'
        },
        {
          'country_type': 'NR',
          'country_desc': 'NAURU'
        },
        {
          'country_type': 'NU',
          'country_desc': 'NIUE'
        },
        {
          'country_type': 'NZ',
          'country_desc': 'NEW ZEALAND'
        },
        {
          'country_type': 'OM',
          'country_desc': 'OMAN'
        },
        {
          'country_type': 'PA',
          'country_desc': 'PANAMA'
        },
        {
          'country_type': 'PE',
          'country_desc': 'PERU'
        },
        {
          'country_type': 'PF',
          'country_desc': 'FRENCH POLYNESIA'
        },
        {
          'country_type': 'PG',
          'country_desc': 'PAPUA NEW GUINEA'
        },
        {
          'country_type': 'PH',
          'country_desc': 'PHILIPPINES'
        },
        {
          'country_type': 'PK',
          'country_desc': 'PAKISTAN'
        },
        {
          'country_type': 'PL',
          'country_desc': 'POLAND'
        },
        {
          'country_type': 'PM',
          'country_desc': 'SAINT PIERRE AND MIQUELON'
        },
        {
          'country_type': 'PN',
          'country_desc': 'PITCAIRN'
        },
        {
          'country_type': 'PR',
          'country_desc': 'PUERTO RICO'
        },
        {
          'country_type': 'PS',
          'country_desc': 'PALESTINIAN TERRITORY, OCCUPIED'
        },
        {
          'country_type': 'PT',
          'country_desc': 'PORTUGAL'
        },
        {
          'country_type': 'PW',
          'country_desc': 'PALAU'
        },
        {
          'country_type': 'PY',
          'country_desc': 'PARAGUAY'
        },
        {
          'country_type': 'QA',
          'country_desc': 'QATAR'
        },
        {
          'country_type': 'RE',
          'country_desc': 'REUNION'
        },
        {
          'country_type': 'RO',
          'country_desc': 'ROMANIA'
        },
        {
          'country_type': 'RS',
          'country_desc': 'SERBIA'
        },
        {
          'country_type': 'RU',
          'country_desc': 'RUSSIAN FEDERATION'
        },
        {
          'country_type': 'RW',
          'country_desc': 'RWANDA'
        },
        {
          'country_type': 'SA',
          'country_desc': 'SAUDI ARABIA'
        },
        {
          'country_type': 'SB',
          'country_desc': 'SOLOMON ISLANDS'
        },
        {
          'country_type': 'SC',
          'country_desc': 'SEYCHELLES'
        },
        {
          'country_type': 'SD',
          'country_desc': 'SUDAN'
        },
        {
          'country_type': 'SE',
          'country_desc': 'SWEDEN'
        },
        {
          'country_type': 'SG',
          'country_desc': 'SINGAPORE'
        },
        {
          'country_type': 'SH',
          'country_desc': 'SAINT HELENA'
        },
        {
          'country_type': 'SI',
          'country_desc': 'SLOVENIA'
        },
        {
          'country_type': 'SJ',
          'country_desc': 'SVALBARD AND JAN MAYEN'
        },
        {
          'country_type': 'SK',
          'country_desc': 'SLOVAKIA'
        },
        {
          'country_type': 'SL',
          'country_desc': 'SIERRA LEONE'
        },
        {
          'country_type': 'SM',
          'country_desc': 'SAN MARINO'
        },
        {
          'country_type': 'SN',
          'country_desc': 'SENEGAL'
        },
        {
          'country_type': 'SO',
          'country_desc': 'SOMALIA'
        },
        {
          'country_type': 'SR',
          'country_desc': 'SURINAME'
        },
        {
          'country_type': 'SS',
          'country_desc': 'SOUTH SUDAN'
        },
        {
          'country_type': 'ST',
          'country_desc': 'SAO TOME AND PRINCIPE'
        },
        {
          'country_type': 'SV',
          'country_desc': 'EL SALVADOR'
        },
        {
          'country_type': 'SX',
          'country_desc': 'SINT MAARTEN(DUTCH PART)'
        },
        {
          'country_type': 'SY',
          'country_desc': 'SYRIAN ARAB REPUBLIC'
        },
        {
          'country_type': 'SZ',
          'country_desc': 'SWAZILAND'
        },
        {
          'country_type': 'TA',
          'country_desc': 'TRISTAN DA CUNHA'
        },
        {
          'country_type': 'TC',
          'country_desc': 'TURKS AND CAICOS ISLANDS'
        },
        {
          'country_type': 'TD',
          'country_desc': 'CHAD'
        },
        {
          'country_type': 'TF',
          'country_desc': 'FRENCH SOUTHERN TERRITORIES'
        },
        {
          'country_type': 'TG',
          'country_desc': 'TOGO'
        },
        {
          'country_type': 'TH',
          'country_desc': 'THAILAND'
        },
        {
          'country_type': 'TJ',
          'country_desc': 'TAJIKISTAN'
        },
        {
          'country_type': 'TK',
          'country_desc': 'TOKELAU'
        },
        {
          'country_type': 'TL',
          'country_desc': 'TIMOR-LESTE'
        },
        {
          'country_type': 'TM',
          'country_desc': 'TURKMENISTAN'
        },
        {
          'country_type': 'TN',
          'country_desc': 'TUNISIA'
        },
        {
          'country_type': 'TO',
          'country_desc': 'TONGA'
        },
        {
          'country_type': 'TR',
          'country_desc': 'TURKEY'
        },
        {
          'country_type': 'TT',
          'country_desc': 'TRINIDAD AND TOBAGO'
        },
        {
          'country_type': 'TV',
          'country_desc': 'TUVALU'
        },
        {
          'country_type': 'TW',
          'country_desc': 'TAIWAN'
        },
        {
          'country_type': 'TZ',
          'country_desc': 'TANZANIA, UNITED REPUBLIC OF'
        },
        {
          'country_type': 'UA',
          'country_desc': 'UKRAINE'
        },
        {
          'country_type': 'UG',
          'country_desc': 'UGANDA'
        },
        {
          'country_type': 'UM',
          'country_desc': 'UNITED STATES MINOR OUTLYING ISLANDS'
        },
        {
          'country_type': 'US',
          'country_desc': 'UNITED STATES'
        },
        {
          'country_type': 'UY',
          'country_desc': 'URUGUAY'
        },
        {
          'country_type': 'UZ',
          'country_desc': 'UZBEKISTAN'
        },
        {
          'country_type': 'VA',
          'country_desc': 'HOLY SEE (VATICAN CITY STATE)'
        },
        {
          'country_type': 'VC',
          'country_desc': 'SAINT VINCENT AND THE GRENADINES'
        },
        {
          'country_type': 'VE',
          'country_desc': 'VENEZUELA'
        },
        {
          'country_type': 'VG',
          'country_desc': 'VIRGIN ISLANDS, BRITISH'
        },
        {
          'country_type': 'VI',
          'country_desc': 'VIRGIN ISLANDS, U.S.'
        },
        {
          'country_type': 'VN',
          'country_desc': 'VIET NAM'
        },
        {
          'country_type': 'VU',
          'country_desc': 'VANUATU'
        },
        {
          'country_type': 'WF',
          'country_desc': 'WALLIS AND FUTUNA'
        },
        {
          'country_type': 'WS',
          'country_desc': 'SAMOA'
        },
        {
          'country_type': 'XZ',
          'country_desc': 'KOSOVO'
        },
        {
          'country_type': 'YE',
          'country_desc': 'YEMEN'
        },
        {
          'country_type': 'YT',
          'country_desc': 'MAYOTTE'
        },
        {
          'country_type': 'YU',
          'country_desc': 'YUGOSLAVIA'
        },
        {
          'country_type': 'ZA',
          'country_desc': 'SOUTH AFRICA'
        },
        {
          'country_type': 'ZM',
          'country_desc': 'ZAMBIA'
        },
        {
          'country_type': 'ZW',
          'country_desc': 'ZIMBABWE'
        }
      ]
    )
    op.bulk_insert(province_type,
      [
        {
          'province_type': 'AB',
          'country_type': 'CA',
          'province_desc': 'ALBERTA'
        },
        {
          'province_type': 'BC',
          'country_type': 'CA',
          'province_desc': 'BRITISH COLUMBIA'
        },
        {
          'province_type': 'MB',
          'country_type': 'CA',
          'province_desc': 'MANITOBA'
        },
        {
          'province_type': 'NB',
          'country_type': 'CA',
          'province_desc': 'NEW BRUNSWICK'
        },
        {
          'province_type': 'NL',
          'country_type': 'CA',
          'province_desc': 'NEWFOUNDLAND AND LABRADOR'
        },
        {
          'province_type': 'NS',
          'country_type': 'CA',
          'province_desc': 'NOVA SCOTIA'
        },
        {
          'province_type': 'NT',
          'country_type': 'CA',
          'province_desc': 'NORTHWEST TERRITORIES'
        },
        {
          'province_type': 'NU',
          'country_type': 'CA',
          'province_desc': 'NUNAVUT'
        },
        {
          'province_type': 'ON',
          'country_type': 'CA',
          'province_desc': 'ONTARIO'
        },
        {
          'province_type': 'PE',
          'country_type': 'CA',
          'province_desc': 'PRINCE EDWARD ISLAND'
        },
        {
          'province_type': 'QC',
          'country_type': 'CA',
          'province_desc': 'QUEBEC'
        },
        {
          'province_type': 'SK',
          'country_type': 'CA',
          'province_desc': 'SASKATCHEWAN'
        },
        {
          'province_type': 'YT',
          'country_type': 'CA',
          'province_desc': 'YUKON TERRITORIES'
        },
        {
          'province_type': 'AA',
          'country_type': 'US',
          'province_desc': 'ARMED FORCES - AMERICAS'
        },
        {
          'province_type': 'AE',
          'country_type': 'US',
          'province_desc': 'ARMED FORCES - OTHER'
        },
        {
          'province_type': 'AK',
          'country_type': 'US',
          'province_desc': 'ALASKA'
        },
        {
          'province_type': 'AL',
          'country_type': 'US',
          'province_desc': 'ALABAMA'
        },
        {
          'province_type': 'AP',
          'country_type': 'US',
          'province_desc': 'ARMED FORCES - PACIFIC'
        },
        {
          'province_type': 'AR',
          'country_type': 'US',
          'province_desc': 'ARKANSAS'
        },
        {
          'province_type': 'AS',
          'country_type': 'US',
          'province_desc': 'AMERICAN SAMOA'
        },
        {
          'province_type': 'AZ',
          'country_type': 'US',
          'province_desc': 'ARIZONA'
        },
        {
          'province_type': 'CA',
          'country_type': 'US',
          'province_desc': 'CALIFORNIA'
        },
        {
          'province_type': 'CO',
          'country_type': 'US',
          'province_desc': 'COLORADO'
        },
        {
          'province_type': 'CT',
          'country_type': 'US',
          'province_desc': 'CONNECTICUT'
        },
        {
          'province_type': 'DC',
          'country_type': 'US',
          'province_desc': 'DISTRICT OF COLUMBIA'
        },
        {
          'province_type': 'DE',
          'country_type': 'US',
          'province_desc': 'DELAWARE'
        },
        {
          'province_type': 'FL',
          'country_type': 'US',
          'province_desc': 'FLORIDA'
        },
        {
          'province_type': 'FM',
          'country_type': 'US',
          'province_desc': 'FED. STATES'
        },
        {
          'province_type': 'GA',
          'country_type': 'US',
          'province_desc': 'GEORGIA'
        },
        {
          'province_type': 'GU',
          'country_type': 'US',
          'province_desc': 'GUAM'
        },
        {
          'province_type': 'HI',
          'country_type': 'US',
          'province_desc': 'HAWAII'
        },
        {
          'province_type': 'IA',
          'country_type': 'US',
          'province_desc': 'IOWA'
        },
        {
          'province_type': 'ID',
          'country_type': 'US',
          'province_desc': 'IDAHO'
        },
        {
          'province_type': 'IL',
          'country_type': 'US',
          'province_desc': 'ILLINOIS'
        },
        {
          'province_type': 'IN',
          'country_type': 'US',
          'province_desc': 'INDIANA'
        },
        {
          'province_type': 'KS',
          'country_type': 'US',
          'province_desc': 'KANSAS'
        },
        {
          'province_type': 'KY',
          'country_type': 'US',
          'province_desc': 'KENTUCKY'
        },
        {
          'province_type': 'LA',
          'country_type': 'US',
          'province_desc': 'LOUISIANA'
        },
        {
          'province_type': 'MA',
          'country_type': 'US',
          'province_desc': 'MASSACHUSETTS'
        },
        {
          'province_type': 'MD',
          'country_type': 'US',
          'province_desc': 'MARYLAND'
        },
        {
          'province_type': 'ME',
          'country_type': 'US',
          'province_desc': 'MAINE'
        },
        {
          'province_type': 'MH',
          'country_type': 'US',
          'province_desc': 'MARSHALL ISLANDS'
        },
        {
          'province_type': 'MI',
          'country_type': 'US',
          'province_desc': 'MICHIGAN'
        },
        {
          'province_type': 'MN',
          'country_type': 'US',
          'province_desc': 'MINNESOTA'
        },
        {
          'province_type': 'MO',
          'country_type': 'US',
          'province_desc': 'MISSOURI'
        },
        {
          'province_type': 'MP',
          'country_type': 'US',
          'province_desc': 'N. MARIANA ISLANDS'
        },
        {
          'province_type': 'MS',
          'country_type': 'US',
          'province_desc': 'MISSISSIPPI'
        },
        {
          'province_type': 'MT',
          'country_type': 'US',
          'province_desc': 'MONTANA'
        },
        {
          'province_type': 'NC',
          'country_type': 'US',
          'province_desc': 'NORTH CAROLINA'
        },
        {
          'province_type': 'ND',
          'country_type': 'US',
          'province_desc': 'NORTH DAKOTA'
        },
        {
          'province_type': 'NE',
          'country_type': 'US',
          'province_desc': 'NEBRASKA'
        },
        {
          'province_type': 'NH',
          'country_type': 'US',
          'province_desc': 'NEW HAMPSHIRE'
        },
        {
          'province_type': 'NJ',
          'country_type': 'US',
          'province_desc': 'NEW JERSEY'
        },
        {
          'province_type': 'NM',
          'country_type': 'US',
          'province_desc': 'NEW MEXICO'
        },
        {
          'province_type': 'NV',
          'country_type': 'US',
          'province_desc': 'NEVADA'
        },
        {
          'province_type': 'NY',
          'country_type': 'US',
          'province_desc': 'NEW YORK'
        },
        {
          'province_type': 'OH',
          'country_type': 'US',
          'province_desc': 'OHIO'
        },
        {
          'province_type': 'OK',
          'country_type': 'US',
          'province_desc': 'OKLAHOMA'
        },
        {
          'province_type': 'OR',
          'country_type': 'US',
          'province_desc': 'OREGON'
        },
        {
          'province_type': 'PA',
          'country_type': 'US',
          'province_desc': 'PENNSYLVANIA'
        },
        {
          'province_type': 'PR',
          'country_type': 'US',
          'province_desc': 'PUERTO RICO'
        },
        {
          'province_type': 'PW',
          'country_type': 'US',
          'province_desc': 'PALAU'
        },
        {
          'province_type': 'RI',
          'country_type': 'US',
          'province_desc': 'RHODE ISLAND'
        },
        {
          'province_type': 'SC',
          'country_type': 'US',
          'province_desc': 'SOUTH CAROLINA'
        },
        {
          'province_type': 'SD',
          'country_type': 'US',
          'province_desc': 'SOUTH DAKOTA'
        },
        {
          'province_type': 'TN',
          'country_type': 'US',
          'province_desc': 'TENNESSEE'
        },
        {
          'province_type': 'TX',
          'country_type': 'US',
          'province_desc': 'TEXAS'
        },
        {
          'province_type': 'UM',
          'country_type': 'US',
          'province_desc': 'U.S. MINOR ISLANDS'
        },
        {
          'province_type': 'UT',
          'country_type': 'US',
          'province_desc': 'UTAH'
        },
        {
          'province_type': 'VA',
          'country_type': 'US',
          'province_desc': 'VIRGINIA'
        },
        {
          'province_type': 'VI',
          'country_type': 'US',
          'province_desc': 'VIRGIN ISLANDS'
        },
        {
          'province_type': 'VT',
          'country_type': 'US',
          'province_desc': 'VERMONT'
        },
        {
          'province_type': 'WA',
          'country_type': 'US',
          'province_desc': 'WASHINGTON'
        },
        {
          'province_type': 'WI',
          'country_type': 'US',
          'province_desc': 'WISCONSIN'
        },
        {
          'province_type': 'WV',
          'country_type': 'US',
          'province_desc': 'WEST VIRGINIA'
        },
        {
          'province_type': 'WY',
          'country_type': 'US',
          'province_desc': 'WYOMING'
        }
      ]
    )
    op.bulk_insert(registration_type_class,
      [
        { 'registration_type_cl': 'PPSALIEN',
          'registration_desc': 'NEW REGISTRATION FILED UNDER THE PPSA SECURITY ACT' },
        { 'registration_type_cl': 'MISCLIEN',
          'registration_desc': 'NEW REGISTRATION FILED UNDER MISCELLANEOUS REGISTRATIONS ACT' },
        { 'registration_type_cl': 'CROWNLIEN',
          'registration_desc': 'NEW REGISTRATION FILED UNDER MISCELLANEOUS REGISTRATIONS ACT AS A CROWN CHARGE' },
        { 'registration_type_cl': 'AMENDMENT',
          'registration_desc': 'AMENDMENT REGISTRATION FILED UNDER THE PPSA SECURITY ACT' },
        { 'registration_type_cl': 'COURTORDER',
          'registration_desc': 'COURT ORDERED AMENDMENT FILED UNDER THE PPSA SECURITY ACT' },
        { 'registration_type_cl': 'CHANGE',
          'registration_desc': 'CHANGE REGISTRATION  FILED UNDER THE PPSA SECURITY ACT' },
        { 'registration_type_cl': 'RENEWAL',
          'registration_desc': 'RENEWAL REGISTRATION  FILED UNDER THE PPSA SECURITY ACT' },
        { 'registration_type_cl': 'DISCHARGE',
          'registration_desc': 'TOTAL DISCHARE REGISTRATION FILED UNDER THE PPSA SECURITY ACT' }
      ]
    )
    op.bulk_insert(registration_type,
      [
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'A1',
            'registration_act': 'SECURITIES ACT',
            'registration_desc': 'AMENDMENT - NOTICE ADDED'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'A2',
            'registration_act': 'SECURITIES ACT',
            'registration_desc': 'AMENDMENT - NOTICE REMOVED'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'A3',
            'registration_act': 'SECURITIES ACT',
            'registration_desc': 'AMENDMENT - NOTICE AMENDED'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AA',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'ADDITION OF COLLATERAL/PROCEEDS'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AD',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'DEBTOR TRANSFER'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AM',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'AMENDMENT/OTHER CHANGE'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AR',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'DEBTOR RELEASE'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AP',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'PARTIAL DISCHARGE'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AS',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'SECURED PARTY TRANSFER'
        },
        {
            'registration_type_cl': 'AMENDMENT',
            'registration_type': 'AU',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'SUBSTITUTION OF COLLATERAL'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'AC',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'ADDITION OF COLLATERAL/PROCEEDS'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'DR',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'DEBTOR RELEASE'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'DT',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'DEBTOR TRANSFER'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'PD',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'PARTIAL DISCHARGE'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'RC',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'REGISTRY CORRECTION'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'ST',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'SECURED PARTY TRANSFER'
        },
        {
            'registration_type_cl': 'CHANGE',
            'registration_type': 'SU',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'SUBSTITUTION OF COLLATERAL'
        },
        {
            'registration_type_cl': 'COURTORDER',
            'registration_type': 'CO',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'COURT ORDER'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'CC',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO CORPORATION CAPITAL TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'CT',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO CARBON TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'DP',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO CONSUMPTION, TRANSITION TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'ET',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO EXCISE TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'FO',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO FOREST ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'FT',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO MOTOR FUEL TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'HR',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO HOTEL ROOM TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'IP',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO INSURANCE PREMIUM TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'IT',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO INCOME TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'LO',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO LOGGING TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'MD',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO MINERAL LAND TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'MI',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO MINING TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'MR',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO MINERAL RESOURCE TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'OT',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'OTHER'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'PG',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO PETROLEUM and NATURAL GAS TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'PS',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO PROVINCIAL SALES TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'PT',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO PROPERTY TRANSFER TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'RA',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO TAXATION (RURAL AREA) ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'SC',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO SCHOOL ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'SS',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO SOCIAL SERVICE TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'SV',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO SPECULATION AND VACANCY TAX ACT'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'TL',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'TAX LIEN UNDER SOCIAL SERVICE OR HOTEL ROOM TAX ACTS'
        },
        {
            'registration_type_cl': 'CROWNLIEN',
            'registration_type': 'TO',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'CROWN CHARGE FILED PURSUANT TO TOBACCO TAX ACT'
        },
        {
            'registration_type_cl': 'DISCHARGE',
            'registration_type': 'DC',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'TOTAL DISCHARGE'
        },
        {
            'registration_type_cl': 'MISCLIEN',
            'registration_type': 'HN',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'HERITAGE CONSERVATION NOTICE'
        },
        {
            'registration_type_cl': 'MISCLIEN',
            'registration_type': 'ML',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'MAINTENANCE LIEN'
        },
        {
            'registration_type_cl': 'MISCLIEN',
            'registration_type': 'MN',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'MANUFACTURED HOME NOTICE'
        },
        {
            'registration_type_cl': 'MISCLIEN',
            'registration_type': 'PN',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'PROCEEDS OF CRIME NOTICE'
        },
        {
            'registration_type_cl': 'MISCLIEN',
            'registration_type': 'SE',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'SECURITIES ORDER OR PROCEEDING'
        },
        {
            'registration_type_cl': 'MISCLIEN',
            'registration_type': 'WL',
            'registration_act': 'MISCELLANEOUS REGISTRATIONS ACT',
            'registration_desc': 'LIEN FOR UNPAID WAGES'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'FA',
            'registration_act': 'FORESTRY SERVICE PROVIDERS PROTECTION ACT',
            'registration_desc': 'FORESTRY - CONTRACTOR CHARGE'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'FL',
            'registration_act': 'FORESTRY SERVICE PROVIDERS PROTECTION ACT',
            'registration_desc': 'FORESTRY - CONTRACTOR LIEN'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'FR',
            'registration_act': 'FAMILY LAW ACT',
            'registration_desc': 'MARRIAGE/SEPARATION AGREEMENT AFFECTING MANUFACTURED HOME'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'FS',
            'registration_act': 'FORESTRY SERVICE PROVIDERS PROTECTION ACT',
            'registration_desc': 'FORESTRY - SUB-CONTRACTOR CHARGE'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'LT',
            'registration_act': 'LAND TAX DEFERMENT ACT',
            'registration_desc': 'LAND TAX DEFERMENT LIEN ON A MANUFACTURED HOME'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'MH',
            'registration_act': 'MANUFACTURED HOME ACT, S.27/28',
            'registration_desc': 'TAX LIEN UNDER S.27/28 OF THE MANUFACTURED HOME ACT'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'RL',
            'registration_act': 'REPAIRERS LIEN ACT',
            'registration_desc': 'REPAIRER''S LIEN'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'SA',
            'registration_act': 'PERSONAL PROPERTY SECURITY ACT',
            'registration_desc': 'PPSA SECURITY AGREEMENT'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'SG',
            'registration_act': 'SALE OF GOODS ACT, S.30',
            'registration_desc': 'POSSESSION UNDER S.30 OF THE SALE OF GOODS ACT'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'TA',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'SECURITY AGREEMENT TRANSITION FINANCING STATEMENT'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'TF',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'PPSA TRANSITION FINANCING STATEMENT'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'TG',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'SALES OF GOODS TRANSITION FINANCING STATEMENT'
        },
        {
            'registration_type_cl': 'PPSALIEN',
            'registration_type': 'TM',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'M.H. TRANSITION FINANCING STATEMENT'
        },
        {
            'registration_type_cl': 'RENEWAL',
            'registration_type': 'RE',
            'registration_act': 'PPSA SECURITY ACT',
            'registration_desc': 'RENEWAL'
        }
      ]
    )

    # MHR type table inserts
    op.bulk_insert(mhr_location_type,
      [
        { 'location_type': 'MANUFACTURER', 'location_type_desc': "Dealer's/Manufacturer's lot" },
        { 'location_type': 'MH_PARK', 'location_type_desc': 'Manufacturer home park (other than a strata park)' },
        { 'location_type': 'RESERVE', 'location_type_desc': 'Indian Reserve' },
        { 'location_type': 'STRATA', 'location_type_desc': 'Strata' },
        { 'location_type': 'OTHER', 'location_type_desc': 'Other' }
      ]
    )
    op.bulk_insert(mhr_note_status_type,
      [
        {"status_type": "ACTIVE", "status_type_desc": "Active.", "legacy_status_type": "A"},
        {"status_type": "CANCELLED", "status_type_desc": "Cancelled.", "legacy_status_type": "C"},
        {"status_type": "EXPIRED", "status_type_desc": "Expired.", "legacy_status_type": "E"},
        {"status_type": "CORRECTED", "status_type_desc": "Corrected.", "legacy_status_type": "F"},
        {"status_type": "COMPLETED", "status_type_desc": "Completed.", "legacy_status_type": "C"}
      ]
    )
    op.bulk_insert(mhr_owner_status_type,
      [
        {"status_type": "ACTIVE", "status_type_desc": "Active.", "legacy_status_type": "3"},
        {"status_type": "EXEMPT", "status_type_desc": "Exempt.", "legacy_status_type": "5"},
        {"status_type": "PREVIOUS", "status_type_desc": "Previous.", "legacy_status_type": "6"}
      ]
    )
    op.bulk_insert(mhr_registration_status_type,
      [
        {"status_type": "ACTIVE", "status_type_desc": "Registered.", "legacy_status_type": "R"},
        {"status_type": "DRAFT", "status_type_desc": "In a draft state (drafted).", "legacy_status_type": "D"},
        {"status_type": "EXEMPT", "status_type_desc": "Exempted.", "legacy_status_type": "E"},
        {"status_type": "HISTORICAL", "status_type_desc": "Cancelled or replaced.", "legacy_status_type": "C"},
        {"status_type": "CANCELLED", "status_type_desc": "Cancelled.", "legacy_status_type": "C"}
      ]
    )
    op.bulk_insert(mhr_party_type,
      [
        {"party_type": "OWNER_IND", "party_type_desc": "Individual Owner"},
        {"party_type": "OWNER_BUS", "party_type_desc": "Business/Organization Owner"},
        {"party_type": "SUBMITTING", "party_type_desc": "Submitting Party"},
        {"party_type": "EXECUTOR", "party_type_desc": "Executor Owner"},
        {"party_type": "TRUSTEE", "party_type_desc": "Trustee Owner"},
        {"party_type": "ADMINISTRATOR", "party_type_desc": "Administrator Owner"},
        {"party_type": "TRUST", "party_type_desc": "Trust beneficiary company"},
        {"party_type": "MANUFACTURER", "party_type_desc": "Manufactured Home Manufacturer"},
        {"party_type": "CONTACT", "party_type_desc": "Registration Contact"}
      ]
    )
    op.bulk_insert(mhr_registration_type,
      [
        {"registration_type": "EXEMPTION_RES", "registration_type_desc": "RESIDENTIAL EXEMPTION", "legacy_registration_type": "EXRS"},
        {"registration_type": "EXEMPTION_NON_RES", "registration_type_desc": "NON-RESIDENTIAL EXEMPTION", "legacy_registration_type": "EXNR"},
        {"registration_type": "PERMIT", "registration_type_desc": "TRANSPORT PERMIT", "legacy_registration_type": "103"},
        {"registration_type": "DECAL_REPLACE", "registration_type_desc": "DECAL REPLACEMENT", "legacy_registration_type": "102 "},
        {"registration_type": "TRANS_WILL", "registration_type_desc": "TRANSFER TO EXECUTOR – GRANT OF PROBATE WITH WILL", "legacy_registration_type": "WILL"},
        {"registration_type": "TRANS", "registration_type_desc": "TRANSFER DUE TO SALE OR GIFT", "legacy_registration_type": "TRAN"},
        {"registration_type": "TRAND", "registration_type_desc": "TRANSFER TO SURVIVING JOINT TENANT(S)", "legacy_registration_type": "DEAT"},
        {"registration_type": "MHREG_CONVERSION", "registration_type_desc": "RECORD CONVERSION", "legacy_registration_type": "CONV"},
        {"registration_type": "REG_STAFF_ADMIN", "registration_type_desc": "REGISTRIES STAFF ADMIN", "legacy_registration_type": "*"},
        {"registration_type": "MHREG", "registration_type_desc": "MANUFACTURED HOME REGISTRATION", "legacy_registration_type": "101"},
        {"registration_type": "TRANS_ADMIN", "registration_type_desc": "TRANSFER TO ADMINISTRATOR – GRANT OF ADMINISTRATION", "legacy_registration_type": "LETA"},
        {"registration_type": "TRANS_AFFIDAVIT", "registration_type_desc": "TRANSFER TO EXECUTOR – ESTATE UNDER $25,000 WITH WILL", "legacy_registration_type": "AFFE"},
        {"registration_type": "MANUFACTURER", "registration_type_desc": "Create Manufacturer", "legacy_registration_type": "NA"},
        {"registration_type": "AMENDMENT", "registration_type_desc": "Amendment", "legacy_registration_type": "PUBA"},
        {"registration_type": "PERMIT_EXTENSION", "registration_type_desc": "TRANSPORT PERMIT - EXTENDED", "legacy_registration_type": "103E"}          
      ]
    )
    op.bulk_insert(mhr_status_type,
      [
        {"status_type": "ACTIVE", "status_type_desc": "Active.", "legacy_status_type": "A"},
        {"status_type": "DRAFT", "status_type_desc": "In a draft state.", "legacy_status_type": "D"},
        {"status_type": "HISTORICAL", "status_type_desc": "Historical or replaced.", "legacy_status_type": "H"}
      ]
    )
    op.bulk_insert(mhr_tenancy_type,
      [
        {"tenancy_type": "COMMON", "tenancy_type_desc": "Tenants in common.", "legacy_tenancy_type": "TC"},
        {"tenancy_type": "JOINT", "tenancy_type_desc": "Joint tenants.", "legacy_tenancy_type": "JT"},
        {"tenancy_type": "SOLE", "tenancy_type_desc": "Sole owner.", "legacy_tenancy_type": "SO"},
        {"tenancy_type": "NA", "tenancy_type_desc": "Not Applicable", "legacy_tenancy_type": ""}
      ]
    )
    op.bulk_insert(mhr_document_type,
      [
        {"document_type": "REG_102", "document_type_desc": "DECAL REPLACEMENT"},
        {"document_type": "REG_103", "document_type_desc": "TRANSPORT PERMIT"},
        {"document_type": "ADDI", "document_type_desc": "ADDITION"},
        {"document_type": "ATTA", "document_type_desc": "ATTACHMENT"},
        {"document_type": "BCLC", "document_type_desc": "BCAA LOCATION CHANGE"},
        {"document_type": "COMP", "document_type_desc": "CERTIFICATE OF COMPANIES"},
        {"document_type": "CONF", "document_type_desc": "CONFIRMATION"},
        {"document_type": "COUR", "document_type_desc": "COURT RESCIND ORDER"},
        {"document_type": "DNCH", "document_type_desc": "DECLARATION OF NAME CHANGE"},
        {"document_type": "EXMN", "document_type_desc": "MANUFACTURED EXEMPTION"},
        {"document_type": "EXNR", "document_type_desc": "NON-RESIDENTIAL EXEMPTION"},
        {"document_type": "EXRS", "document_type_desc": "RESIDENTIAL EXEMPTION"},
        {"document_type": "FZE", "document_type_desc": "REGISTRARS FREEZE"},
        {"document_type": "INTE", "document_type_desc": "EXTEND INTERIM"},
        {"document_type": "INTW", "document_type_desc": "WITHDRAW INTERIM"},
        {"document_type": "MAID", "document_type_desc": "MAIDEN NAME"},
        {"document_type": "MAIL", "document_type_desc": "MAILING ADDRESS"},
        {"document_type": "MARR", "document_type_desc": "MARRIAGE CERTIFICATE"},
        {"document_type": "MEAM", "document_type_desc": "CERTIFICATE OF MERGER/AMALGAMATION"},
        {"document_type": "NAMV", "document_type_desc": "CERTIFICATE OF VITAL STATS"},
        {"document_type": "NCAN", "document_type_desc": "CANCEL NOTE"},
        {"document_type": "NCON", "document_type_desc": "CONFIDENTIAL NOTE"},
        {"document_type": "NPUB", "document_type_desc": "PUBLIC NOTE"},
        {"document_type": "NRED", "document_type_desc": "NOTICE OF REDEMPTION"},
        {"document_type": "PDEC", "document_type_desc": "PRESOLD DECAL"},
        {"document_type": "PUBA", "document_type_desc": "PUBLIC AMENDMENT"},
        {"document_type": "REBU", "document_type_desc": "REBUILT"},
        {"document_type": "REST", "document_type_desc": "RESTRAINING ORDER"},
        {"document_type": "THAW", "document_type_desc": "REMOVE FREEZE"},
        {"document_type": "WHAL", "document_type_desc": "WAREHOUSEMAN LIEN"},
        {"document_type": "CONV", "document_type_desc": "RECORD CONVERSION"},
        {"document_type": "REGC_STAFF", "document_type_desc": "REGISTRY CORRECTION - STAFF ERROR OR OMISSION"},
        {"document_type": "TRAN", "document_type_desc": "TRANSFER DUE TO SALE OR GIFT"},
        {"document_type": "REGC_CLIENT", "document_type_desc": "REGISTRY CORRECTION - CLIENT ERROR OR OMISSION"},
        {"document_type": "DEAT", "document_type_desc": "TRANSFER TO SURVIVING JOINT TENANT(S)"},
        {"document_type": "REG_101", "document_type_desc": "MANUFACTURED HOME REGISTRATION"},
        {"document_type": "AFFE", "document_type_desc": "TRANSFER TO EXECUTOR – ESTATE UNDER $25,000 WITH WILL"},
        {"document_type": "CAU", "document_type_desc": "NOTICE OF CAUTION"},
        {"document_type": "CAUC", "document_type_desc": "CONTINUED NOTICE OF CAUTION"},
        {"document_type": "REREGISTER_C", "document_type_desc": "RE-REGISTER A CANCELLED HOME"},
        {"document_type": "TAXN", "document_type_desc": "NOTICE OF TAX SALE"},
        {"document_type": "CAUE", "document_type_desc": "EXTENSION TO NOTICE OF CAUTION"},
        {"document_type": "TRANS_WRIT_SEIZURE", "document_type_desc": "TRANSFER DUE TO WRIT OF SEIZURE AND SALE"},
        {"document_type": "TRANS_SEVER_GRANT", "document_type_desc": "TRANSFER DUE TO SEVERING JOINT TENANCY"},
        {"document_type": "TRANS_RECEIVERSHIP", "document_type_desc": "TRANSFER DUE TO RECEIVERSHIP"},
        {"document_type": "TRANS_LAND_TITLE", "document_type_desc": "TRANSFER DUE TO LAND TITLE"},
        {"document_type": "TRANS_FAMILY_ACT", "document_type_desc": "TRANSFER DUE TO FAMILY MAINTENANCE ACT"},
        {"document_type": "TRANS_QUIT_CLAIM", "document_type_desc": "TRANSFER DUE TO QUIT CLAIM"},
        {"document_type": "TRANS_INFORMAL_SALE", "document_type_desc": "TRANSFER WITH AN INFORMAL BILL OF SALE"},
        {"document_type": "ABAN", "document_type_desc": "TRANSFER DUE TO ABANDONMENT AND SALE"},
        {"document_type": "BANK", "document_type_desc": "TRANSFER DUE TO BANKRUPTCY"},
        {"document_type": "COU", "document_type_desc": "TRANSFER DUE TO COURT ORDER"},
        {"document_type": "FORE", "document_type_desc": "TRANSFER DUE TO FORECLOSURE ORDER"},
        {"document_type": "GENT", "document_type_desc": "TRANSFER DUE TO GENERAL TRANSMISSION"},
        {"document_type": "REIV", "document_type_desc": "TRANSFER DUE TO REPOSSESSION - INVOLUNTARY"},
        {"document_type": "REPV", "document_type_desc": "TRANSFER DUE TO REPOSSESSION - VOLUNTARY"},
        {"document_type": "SZL", "document_type_desc": "TRANSFER DUE TO SEIZURE UNDER LAND ACT"},
        {"document_type": "TAXS", "document_type_desc": "TRANSFER DUE TO TAX SALE"},
        {"document_type": "VEST", "document_type_desc": "TRANSFER DUE TO VESTING ORDER"},
        {"document_type": "WILL", "document_type_desc": "TRANSFER TO EXECUTOR - GRANT OF PROBATE WITH WILL"},
        {"document_type": "CANCEL_PERMIT", "document_type_desc": "TRANSPORT PERMIT - CANCELLED"},
        {"document_type": "REGC", "document_type_desc": "REGISTRAR'S CORRECTION"},
        {"document_type": "STAT", "document_type_desc": "REGISTERED LOCATION CHANGE"},
        {"document_type": "LETA", "document_type_desc": "TRANSFER TO ADMINISTRATOR - GRANT OF ADMINISTRATION"},
        {"document_type": "AMEND_PERMIT", "document_type_desc": "TRANSPORT PERMIT - AMENDED"},
        {"document_type": "EXRE", "document_type_desc": "MANUFACTURED HOME RE-REGISTRATION"},
        {"document_type": "REG_103E", "document_type_desc": "TRANSPORT PERMIT - EXTENDED"}
      ]
    )

    # ### Create views manually added - must be after tables. ###
    # PPR views
    public_account_draft_vw = PGView(
        schema="public",
        signature="account_draft_vw",
        definition="SELECT d.document_number,\n       d.create_ts,\n       d.registration_type,\n       d.registration_type_cl,\n       rt.registration_desc,\n       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN ''\n            ELSE d.registration_number END base_reg_num,\n       d.draft ->> 'type' AS draft_type,\n       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,\n       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN\n                 d.draft -> 'financingStatement' ->> 'clientReferenceId'\n            WHEN d.registration_type_cl = 'AMENDMENT' THEN d.draft -> 'amendmentStatement' ->> 'clientReferenceId'\n            WHEN d.registration_type_cl = 'CHANGE' THEN d.draft -> 'changeStatement' ->> 'clientReferenceId'\n            ELSE '' END client_reference_id,\n       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND\n                 d.draft -> 'financingStatement' -> 'registeringParty' IS NOT NULL THEN\n                 CASE WHEN d.draft -> 'financingStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN\n                           d.draft -> 'financingStatement' -> 'registeringParty' ->> 'businessName'\n                      WHEN d.draft -> 'financingStatement' -> 'registeringParty' ->> 'personName' IS NOT NULL THEN\n                      concat(d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',\n                             d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'last')\n                 END\n            WHEN d.registration_type_cl = 'AMENDMENT' AND\n                 (d.draft -> 'amendmentStatement' -> 'registeringParty') IS NOT NULL THEN\n                 CASE WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN\n                           d.draft -> 'amendmentStatement' -> 'registeringParty' ->> 'businessName'\n                      WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' IS NOT NULL THEN\n                        concat(d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',\n                               d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'last')\n                 END\n            ELSE '' END registering_party,\n      CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND\n                 d.draft -> 'financingStatement' -> 'securedParties' IS NOT NULL THEN\n                (SELECT string_agg((CASE WHEN (sp -> 'businessName') IS NOT NULL THEN\n                                             (sp ->> 'businessName')\n                                         WHEN sp -> 'personName' IS NOT NULL THEN\n                                            concat((sp -> 'personName' ->> 'first'), ' ',\n                                                   (sp -> 'personName' ->> 'last'))\n                                         END),\n                                   ',')\n                   FROM json_array_elements(d.draft -> 'financingStatement' -> 'securedParties') sp)\n          WHEN d.registration_type_cl = 'AMENDMENT' AND\n                 d.draft -> 'amendmentStatement' -> 'securedParties' IS NOT NULL THEN\n                (SELECT string_agg((CASE WHEN (sp2 -> 'businessName') IS NOT NULL THEN\n                                             (sp2 ->> 'businessName')\n                                         WHEN sp2 -> 'personName' IS NOT NULL THEN\n                                            concat((sp2 -> 'personName' ->> 'first'), ' ',\n                                                   (sp2 -> 'personName' ->> 'last'))\n                                         END),\n                                   ',')\n                   FROM json_array_elements(d.draft -> 'amendmentStatement' -> 'securedParties') sp2)\n            ELSE ' ' END secured_party,\n       (SELECT CASE WHEN d.user_id IS NULL THEN ''\n                    ELSE (SELECT u.firstname || ' ' || u.lastname\n                            FROM users u\n                           WHERE u.username = d.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n       d.account_id,\n       d.id, d.registration_number\n  FROM drafts d, registration_types rt\n WHERE d.registration_type = rt.registration_type"
    )
    op.create_entity(public_account_draft_vw)

    public_account_registration_count_vw = PGView(
        schema="public",
        signature="account_registration_count_vw",
        definition="SELECT r.id, r.account_id, r.registration_type_cl\n        FROM registrations r, registration_types rt, financing_statements fs\n        WHERE r.registration_type = rt.registration_type\n        AND fs.id = r.financing_id\n        AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n        AND NOT EXISTS (SELECT r3.id\n                            FROM registrations r3\n                            WHERE r3.financing_id = fs.id\n                            AND r3.registration_type_cl = 'DISCHARGE'\n                            AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))\n        AND NOT EXISTS (SELECT r2.financing_id\n                            FROM user_extra_registrations uer, registrations r2\n                        WHERE uer.registration_number = r2.registration_number\n                            AND r2.financing_id = r.financing_id\n                            AND uer.removed_ind = 'Y')\n        UNION (\n        SELECT r.id, uer.account_id, r.registration_type_cl\n        FROM registrations r, registration_types rt, financing_statements fs, user_extra_registrations uer\n        WHERE r.registration_type = rt.registration_type\n        AND fs.id = r.financing_id\n        AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n        AND (r.registration_number = uer.registration_number OR r.base_reg_number = uer.registration_number)\n        AND uer.removed_ind IS NULL\n        AND NOT EXISTS (SELECT r3.id\n                            FROM registrations r3\n                            WHERE r3.financing_id = fs.id\n                            AND r3.registration_type_cl = 'DISCHARGE'\n                            AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days')))"
    )
    op.create_entity(public_account_registration_count_vw)

    public_account_registration_vw = PGView(
        schema="public",
        signature="account_registration_vw",
        definition="WITH q AS (\n  SELECT (now() at time zone 'utc')\n      AS current_expire_ts\n)\nSELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, r.account_id,\n       rt.registration_desc, r.base_reg_number, r.id AS registration_id, fs.id AS financing_id,\n       CASE WHEN fs.state_type = 'ACT' AND fs.expire_date IS NOT NULL AND\n                 (fs.expire_date at time zone 'utc') < (now() at time zone 'utc') THEN 'HEX'\n            ELSE fs.state_type END AS state,\n       CASE WHEN fs.life = 99 THEN -99\n            ELSE CAST(EXTRACT(days from (fs.expire_date at time zone 'utc' - current_expire_ts)) AS INT) END expire_days,\n       (SELECT MAX(r2.registration_ts)\n          FROM registrations r2\n         WHERE r2.financing_id = r.financing_id) AS last_update_ts,\n       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                    WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                    ELSE p.first_name || ' ' || p.last_name END\n          FROM parties p\n         WHERE p.registration_id = r.id\n           AND p.party_type = 'RG') AS registering_party,\n       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                                WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                                ELSE p.first_name || ' ' || p.last_name END), ', ')\n          FROM parties p\n         WHERE p.financing_id = fs.id\n           AND p.registration_id_end IS NULL\n           AND p.party_type = 'SP') AS secured_party,\n       r.client_reference_id,\n       (SELECT CASE WHEN r.user_id IS NULL THEN ''\n                    ELSE (SELECT u.firstname || ' ' || u.lastname\n                            FROM users u\n                           WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n       r.account_id AS orig_account_id,\n       r2.account_id AS base_account_id,\n       (SELECT COUNT(vr.id)\n          FROM verification_reports vr\n         WHERE vr.registration_id = r.id\n           AND vr.doc_storage_url IS NULL) AS pending_count,\n       (SELECT COUNT(sc.id)\n         FROM serial_collateral sc\n        WHERE sc.financing_id = fs.id\n          AND (sc.registration_id = r.id OR \n               (sc.registration_id <= r.id AND (sc.registration_id_end IS NULL OR sc.registration_id_end > r.id)))) AS vehicle_count \n FROM registrations r, registration_types rt, financing_statements fs, registrations r2, q\n WHERE r.registration_type = rt.registration_type\n   AND fs.id = r.financing_id\n   AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n   AND NOT EXISTS (SELECT r3.id\n                     FROM registrations r3\n                    WHERE r3.financing_id = fs.id\n                      AND r3.registration_type_cl = 'DISCHARGE'\n                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))\n  AND NOT EXISTS (SELECT r2.financing_id\n                    FROM user_extra_registrations uer, registrations r2\n                   WHERE uer.registration_number = r2.registration_number\n                     AND r2.financing_id = r.financing_id\n                     AND uer.removed_ind = 'Y')\n  AND r2.financing_id = fs.id\n  AND r2.financing_id = r.financing_id\n  AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')\nUNION (\nSELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, uer.account_id,\n       rt.registration_desc, r.base_reg_number, r.id AS registration_id, fs.id AS financing_id,\n       CASE WHEN fs.state_type = 'ACT' AND fs.expire_date IS NOT NULL AND\n                 (fs.expire_date at time zone 'utc') < (now() at time zone 'utc') THEN 'HEX'\n            ELSE fs.state_type END AS state,\n       CASE WHEN fs.life = 99 THEN -99\n            ELSE CAST(EXTRACT(days from (fs.expire_date at time zone 'utc' - current_expire_ts)) AS INT) END expire_days,\n       (SELECT MAX(r2.registration_ts)\n          FROM registrations r2\n         WHERE r2.financing_id = r.financing_id) AS last_update_ts,\n       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                    WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                    ELSE p.first_name || ' ' || p.last_name END\n          FROM parties p\n         WHERE p.registration_id = r.id\n           AND p.party_type = 'RG') AS registering_party,\n       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                                WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                                ELSE p.first_name || ' ' || p.last_name END), ', ')\n          FROM parties p\n         WHERE p.financing_id = fs.id\n           AND p.registration_id_end IS NULL\n           AND p.party_type = 'SP') AS secured_party,\n       r.client_reference_id,\n       (SELECT CASE WHEN r.user_id IS NULL THEN ''\n                    ELSE (SELECT u.firstname || ' ' || u.lastname\n                            FROM users u\n                           WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n       r.account_id AS orig_account_id,\n       r2.account_id AS base_account_id,\n       (SELECT COUNT(vr.id)\n          FROM verification_reports vr\n         WHERE vr.registration_id = r.id\n           AND vr.doc_storage_url IS NULL) AS pending_count,\n       (SELECT COUNT(sc.id)\n         FROM serial_collateral sc\n        WHERE sc.financing_id = fs.id\n          AND (sc.registration_id = r.id OR \n               (sc.registration_id <= r.id AND (sc.registration_id_end IS NULL OR sc.registration_id_end > r.id)))) AS vehicle_count \n  FROM registrations r, registration_types rt, financing_statements fs, user_extra_registrations uer, registrations r2, q\n WHERE r.registration_type = rt.registration_type\n   AND fs.id = r.financing_id\n   AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n   AND (r.registration_number = uer.registration_number OR r.base_reg_number = uer.registration_number)\n   AND uer.removed_ind IS NULL\n   AND NOT EXISTS (SELECT r3.id\n                     FROM registrations r3\n                    WHERE r3.financing_id = fs.id\n                      AND r3.registration_type_cl = 'DISCHARGE'\n                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))\n  AND r2.financing_id = fs.id\n  AND r2.financing_id = r.financing_id\n  AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')\n)"
    )
    op.create_entity(public_account_registration_vw)

    # MHR views
    public_mhr_lien_check_vw = PGView(
        schema="public",
        signature="mhr_lien_check_vw",
        definition="SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')\n    AND r.registration_type NOT IN ('SA', 'TA', 'TM')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n  UNION (\n  SELECT sc.mhr_number, r.registration_type || '_TAX', r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl = 'PPSALIEN'\n    AND r.registration_type IN ('SA', 'TA', 'TM')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n    AND EXISTS (SELECT p.id\n                  FROM parties p, client_codes cc\n                  WHERE p.financing_id = fs.id\n                    AND p.party_type = 'SP'\n                    AND p.registration_id_end IS NULL\n                    AND p.branch_id IS NOT NULL\n                    AND p.branch_id = cc.id\n                    AND cc.name like '%TAX DEFERME%')\n  )\n  UNION (\n  SELECT sc.mhr_number, r.registration_type || '_GOV', r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl = 'PPSALIEN'\n    AND r.registration_type IN ('SA', 'TA', 'TM')\n    AND r.registration_ts <= TO_DATE('2004-03-31', 'YYYY-MM-DD')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n    AND EXISTS (SELECT p.id\n                  FROM parties p, client_codes cc\n                  WHERE p.financing_id = fs.id\n                    AND p.party_type = 'SP'\n                    AND p.registration_id_end IS NULL\n                    AND p.branch_id IS NOT NULL\n                    AND p.branch_id = cc.id\n                    AND cc.name like 'HER MAJESTY%')\n  )\n  UNION (\n  SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl = 'PPSALIEN'\n    AND r.registration_type IN ('SA', 'TA', 'TM')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n    AND NOT EXISTS (SELECT p.id\n                      FROM parties p, client_codes cc\n                      WHERE p.financing_id = fs.id\n                        AND p.party_type = 'SP'\n                        AND p.registration_id_end IS NULL\n                        AND p.branch_id IS NOT NULL\n                        AND p.branch_id = cc.id\n                        AND (cc.name like 'HER MAJESTY%' OR cc.name like '%TAX DEFERME%'))\n  )"
    )
    op.create_entity(public_mhr_lien_check_vw)

    public_mhr_search_mhr_number_vw = PGView(
        schema="public",
        signature="mhr_search_mhr_number_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          (SELECT s.serial_number\n               FROM mhr_registrations rs, mhr_sections s\n          WHERE rs.mhr_number = r.mhr_number \n               AND rs.id = s.registration_id\n               AND s.status_type = 'ACTIVE'\n          ORDER BY s.id\n          FETCH FIRST 1 ROWS ONLY) AS serial_number,\n          d.year_made,\n          d.make, d.model, r.id,\n          (SELECT CASE WHEN p.business_name IS NOT NULL THEN og.status_type || '|' || p.business_name\n                         WHEN p.middle_name IS NOT NULL THEN og.status_type || '|' || p.first_name || '|' || p.middle_name || '|' || p.last_name\n                         ELSE og.status_type || '|' || p.first_name || '|' || p.last_name\n                    END\n               FROM mhr_registrations ro, mhr_owner_groups og, mhr_parties p\n          WHERE ro.mhr_number = r.mhr_number \n               AND ro.id = og.registration_id\n               AND og.registration_id = p.registration_id\n               AND og.status_type IN ('ACTIVE', 'EXEMPT')\n               ORDER BY p.id DESC\n               FETCH FIRST 1 ROWS ONLY) AS owner_info\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'"
    )
    op.create_entity(public_mhr_search_mhr_number_vw)

    public_mhr_search_owner_bus_vw = PGView(
        schema="public",
        signature="mhr_search_owner_bus_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          (SELECT s.serial_number\n               FROM mhr_registrations rs, mhr_sections s\n          WHERE rs.mhr_number = r.mhr_number \n               AND rs.id = s.registration_id\n               AND s.status_type = 'ACTIVE'\n          ORDER BY s.id\n          FETCH FIRST 1 ROWS ONLY) AS serial_number,\n          d.year_made,\n          d.make, d.model, r.id,\n          p.business_name,\n          og.status_type AS owner_status_type,\n          p.compressed_name\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_registrations ro,\n          mhr_owner_groups og,\n          mhr_parties p,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND ro.mhr_number = r.mhr_number \n     AND ro.id = og.registration_id\n     AND og.registration_id = p.registration_id\n     AND p.owner_group_id = og.id\n     AND p.party_type = 'OWNER_BUS'\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'"
    )
    op.create_entity(public_mhr_search_owner_bus_vw)

    public_mhr_search_owner_ind_vw = PGView(
        schema="public",
        signature="mhr_search_owner_ind_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          (SELECT s.serial_number\n               FROM mhr_registrations rs, mhr_sections s\n          WHERE rs.mhr_number = r.mhr_number \n               AND rs.id = s.registration_id\n               AND s.status_type = 'ACTIVE'\n          ORDER BY s.id\n          FETCH FIRST 1 ROWS ONLY) AS serial_number,\n          d.year_made,\n          d.make, d.model, r.id,\n          p.last_name,\n          p.first_name,\n          p.middle_name,\n          og.status_type AS owner_status_type,\n          p.compressed_name\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_registrations ro,\n          mhr_owner_groups og,\n          mhr_parties p,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND ro.mhr_number = r.mhr_number \n     AND ro.id = og.registration_id\n     AND og.registration_id = p.registration_id\n     AND p.party_type = 'OWNER_IND'\n     AND p.owner_group_id = og.id\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'"
    )
    op.create_entity(public_mhr_search_owner_ind_vw)

    public_mhr_search_serial_vw = PGView(
        schema="public",
        signature="mhr_search_serial_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          s.serial_number,\n          s.compressed_key,\n          d.year_made,\n          d.make, d.model, r.id,\n          (SELECT CASE WHEN p.business_name IS NOT NULL THEN og.status_type || '|' || p.business_name\n                         WHEN p.middle_name IS NOT NULL THEN og.status_type || '|' || p.first_name || '|' || p.middle_name || '|' || p.last_name\n                         ELSE og.status_type || '|' || p.first_name || '|' || p.last_name\n                    END\n               FROM mhr_registrations ro, mhr_owner_groups og, mhr_parties p\n          WHERE ro.mhr_number = r.mhr_number \n               AND ro.id = og.registration_id\n               AND og.registration_id = p.registration_id\n               AND og.status_type IN ('ACTIVE', 'EXEMPT')\n               ORDER BY p.id DESC\n               FETCH FIRST 1 ROWS ONLY) AS owner_info,\n          s.id AS section_id\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d,\n          mhr_registrations rs,\n          mhr_sections s\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'\n     AND rs.mhr_number = r.mhr_number \n     AND rs.id = s.registration_id\n     AND s.status_type = 'ACTIVE'"
    )
    op.create_entity(public_mhr_search_serial_vw)

    public_mhr_account_reg_vw = PGView(
        schema="public",
        signature="mhr_account_reg_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts,\n        (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                      WHEN p.middle_name IS NOT NULL THEN p.first_name || ' ' || p.middle_name || ' ' || p.last_name\n                      ELSE p.first_name || ' ' || p.last_name\n                END\n            FROM mhr_parties p\n          WHERE p.registration_id = r.id \n            AND p.party_type = 'SUBMITTING') AS submitting_name,\n        r.client_reference_id,\n        r.registration_type,       \n        (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                                  WHEN p.middle_name IS NOT NULL THEN p.first_name || ' ' || p.middle_name || ' ' || p.last_name\n                                  ELSE p.first_name || ' ' || p.last_name END), '\\n')\n            FROM mhr_registrations r1, mhr_owner_groups og, mhr_parties p\n          WHERE r1.mhr_number = r.mhr_number \n            AND r1.id = og.registration_id\n            AND og.registration_id = p.registration_id\n            AND og.id = p.owner_group_id\n            AND r1.registration_ts = (SELECT MAX(r2.registration_ts)\n                                        FROM mhr_registrations r2, mhr_owner_groups og2\n                                        WHERE r2.mhr_number = r.mhr_number\n                                          AND og2.registration_id = r2.id\n                                          AND r2.id <= r.id)) AS owner_names,       \n        (SELECT CASE WHEN r.user_id IS NULL THEN ''\n                      ELSE (SELECT u.firstname || ' ' || u.lastname\n                              FROM users u\n                            WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n        d.document_id,\n        d.document_registration_number,\n        (SELECT d2.document_type\n            FROM mhr_documents d2\n          WHERE d2.id = (SELECT MAX(d3.id)\n                            FROM mhr_documents d3, mhr_registrations r2\n                          WHERE r2.id = d3.registration_id\n                            AND r2.mhr_number = r.mhr_number)) AS last_doc_type,\n        (SELECT n.status_type\n            FROM mhr_notes n\n          WHERE n.registration_id = r.id) AS note_status,\n        (SELECT n.expiry_date\n            FROM mhr_notes n\n          WHERE n.registration_id = r.id) AS note_expiry,\n        (CASE\n            WHEN d.document_type in ('NCAN', 'NRED') THEN\n              (SELECT n.document_type\n                FROM mhr_notes n\n                WHERE n.status_type != 'ACTIVE'\n                  AND n.change_registration_id = r.id\n                  AND n.document_type != 'CAUC'\n                  AND n.document_type != 'CAUE'\n              FETCH FIRST 1 ROWS ONLY)\n            ELSE NULL\n          END) AS cancel_doc_type,\n        (SELECT n.document_type\n            FROM mhr_notes n, mhr_registrations r2\n          WHERE r2.mhr_number = r.mhr_number\n            AND r2.id = n.registration_id\n            AND n.status_type = 'ACTIVE'\n            AND (n.document_type IN ('TAXN', 'NCON', 'REST') OR \n                  (n.document_type IN ('REG_103', 'REG_103E') AND \n                  n.expiry_date IS NOT NULL AND n.expiry_date > (now() at time zone 'UTC')))\n          FETCH FIRST 1 ROWS ONLY) AS frozen_doc_type,\n        r.account_id,\n        dt.document_type_desc,\n        (SELECT CASE WHEN r.registration_type NOT IN ('MHREG', 'MHREG_CONVERSION') THEN ''\n              ELSE (SELECT lcv.registration_type\n                      FROM mhr_lien_check_vw lcv\n                    WHERE lcv.mhr_number = r.mhr_number\n                  ORDER BY lcv.base_registration_ts\n                  FETCH FIRST 1 ROWS ONLY) END) AS ppr_lien_type,\n        d.document_type,\n        r.id AS registration_id,\n        (SELECT mrr.doc_storage_url\n            FROM mhr_registration_reports mrr\n          WHERE mrr.registration_id = r.id) AS doc_storage_url,\n        (SELECT l.location_type\n            FROM mhr_locations l, mhr_registrations r2\n          WHERE r2.mhr_number = r.mhr_number\n            AND r2.id = l.registration_id\n            AND l.status_type = 'ACTIVE') AS location_type,\n        d.affirm_by,\n        (SELECT COUNT(mrr.id)\n            FROM mhr_registration_reports mrr\n          WHERE mrr.registration_id = r.id) AS report_count\n    FROM mhr_registrations r, mhr_documents d, mhr_document_types dt\n  WHERE r.id = d.registration_id\n    AND d.document_type = dt.document_type"
    )
    op.create_entity(public_mhr_account_reg_vw)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    public_account_registration_vw = PGView(
        schema="public",
        signature="account_registration_vw",
        definition="WITH q AS (\n  SELECT (now() at time zone 'utc')\n      AS current_expire_ts\n)\nSELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, r.account_id,\n       rt.registration_desc, r.base_reg_number, r.id AS registration_id, fs.id AS financing_id,\n       CASE WHEN fs.state_type = 'ACT' AND fs.expire_date IS NOT NULL AND\n                 (fs.expire_date at time zone 'utc') < (now() at time zone 'utc') THEN 'HEX'\n            ELSE fs.state_type END AS state,\n       CASE WHEN fs.life = 99 THEN -99\n            ELSE CAST(EXTRACT(days from (fs.expire_date at time zone 'utc' - current_expire_ts)) AS INT) END expire_days,\n       (SELECT MAX(r2.registration_ts)\n          FROM registrations r2\n         WHERE r2.financing_id = r.financing_id) AS last_update_ts,\n       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                    WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                    ELSE p.first_name || ' ' || p.last_name END\n          FROM parties p\n         WHERE p.registration_id = r.id\n           AND p.party_type = 'RG') AS registering_party,\n       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                                WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                                ELSE p.first_name || ' ' || p.last_name END), ', ')\n          FROM parties p\n         WHERE p.financing_id = fs.id\n           AND p.registration_id_end IS NULL\n           AND p.party_type = 'SP') AS secured_party,\n       r.client_reference_id,\n       (SELECT CASE WHEN r.user_id IS NULL THEN ''\n                    ELSE (SELECT u.firstname || ' ' || u.lastname\n                            FROM users u\n                           WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n       r.account_id AS orig_account_id,\n       r2.account_id AS base_account_id,\n       (SELECT COUNT(vr.id)\n          FROM verification_reports vr\n         WHERE vr.registration_id = r.id\n           AND vr.doc_storage_url IS NULL) AS pending_count,\n       (SELECT COUNT(sc.id)\n         FROM serial_collateral sc\n        WHERE sc.financing_id = fs.id\n          AND (sc.registration_id = r.id OR \n               (sc.registration_id <= r.id AND (sc.registration_id_end IS NULL OR sc.registration_id_end > r.id)))) AS vehicle_count \n FROM registrations r, registration_types rt, financing_statements fs, registrations r2, q\n WHERE r.registration_type = rt.registration_type\n   AND fs.id = r.financing_id\n   AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n   AND NOT EXISTS (SELECT r3.id\n                     FROM registrations r3\n                    WHERE r3.financing_id = fs.id\n                      AND r3.registration_type_cl = 'DISCHARGE'\n                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))\n  AND NOT EXISTS (SELECT r2.financing_id\n                    FROM user_extra_registrations uer, registrations r2\n                   WHERE uer.registration_number = r2.registration_number\n                     AND r2.financing_id = r.financing_id\n                     AND uer.removed_ind = 'Y')\n  AND r2.financing_id = fs.id\n  AND r2.financing_id = r.financing_id\n  AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')\nUNION (\nSELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, uer.account_id,\n       rt.registration_desc, r.base_reg_number, r.id AS registration_id, fs.id AS financing_id,\n       CASE WHEN fs.state_type = 'ACT' AND fs.expire_date IS NOT NULL AND\n                 (fs.expire_date at time zone 'utc') < (now() at time zone 'utc') THEN 'HEX'\n            ELSE fs.state_type END AS state,\n       CASE WHEN fs.life = 99 THEN -99\n            ELSE CAST(EXTRACT(days from (fs.expire_date at time zone 'utc' - current_expire_ts)) AS INT) END expire_days,\n       (SELECT MAX(r2.registration_ts)\n          FROM registrations r2\n         WHERE r2.financing_id = r.financing_id) AS last_update_ts,\n       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                    WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                    ELSE p.first_name || ' ' || p.last_name END\n          FROM parties p\n         WHERE p.registration_id = r.id\n           AND p.party_type = 'RG') AS registering_party,\n       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)\n                                WHEN p.middle_initial IS NOT NULL THEN p.first_name || ' ' || p.middle_initial || ' ' || p.last_name\n                                ELSE p.first_name || ' ' || p.last_name END), ', ')\n          FROM parties p\n         WHERE p.financing_id = fs.id\n           AND p.registration_id_end IS NULL\n           AND p.party_type = 'SP') AS secured_party,\n       r.client_reference_id,\n       (SELECT CASE WHEN r.user_id IS NULL THEN ''\n                    ELSE (SELECT u.firstname || ' ' || u.lastname\n                            FROM users u\n                           WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n       r.account_id AS orig_account_id,\n       r2.account_id AS base_account_id,\n       (SELECT COUNT(vr.id)\n          FROM verification_reports vr\n         WHERE vr.registration_id = r.id\n           AND vr.doc_storage_url IS NULL) AS pending_count,\n       (SELECT COUNT(sc.id)\n         FROM serial_collateral sc\n        WHERE sc.financing_id = fs.id\n          AND (sc.registration_id = r.id OR \n               (sc.registration_id <= r.id AND (sc.registration_id_end IS NULL OR sc.registration_id_end > r.id)))) AS vehicle_count \n  FROM registrations r, registration_types rt, financing_statements fs, user_extra_registrations uer, registrations r2, q\n WHERE r.registration_type = rt.registration_type\n   AND fs.id = r.financing_id\n   AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n   AND (r.registration_number = uer.registration_number OR r.base_reg_number = uer.registration_number)\n   AND uer.removed_ind IS NULL\n   AND NOT EXISTS (SELECT r3.id\n                     FROM registrations r3\n                    WHERE r3.financing_id = fs.id\n                      AND r3.registration_type_cl = 'DISCHARGE'\n                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))\n  AND r2.financing_id = fs.id\n  AND r2.financing_id = r.financing_id\n  AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')\n)"
    )
    op.drop_entity(public_account_registration_vw)

    public_account_registration_count_vw = PGView(
        schema="public",
        signature="account_registration_count_vw",
        definition="SELECT r.id, r.account_id, r.registration_type_cl\n        FROM registrations r, registration_types rt, financing_statements fs\n        WHERE r.registration_type = rt.registration_type\n        AND fs.id = r.financing_id\n        AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n        AND NOT EXISTS (SELECT r3.id\n                            FROM registrations r3\n                            WHERE r3.financing_id = fs.id\n                            AND r3.registration_type_cl = 'DISCHARGE'\n                            AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))\n        AND NOT EXISTS (SELECT r2.financing_id\n                            FROM user_extra_registrations uer, registrations r2\n                        WHERE uer.registration_number = r2.registration_number\n                            AND r2.financing_id = r.financing_id\n                            AND uer.removed_ind = 'Y')\n        UNION (\n        SELECT r.id, uer.account_id, r.registration_type_cl\n        FROM registrations r, registration_types rt, financing_statements fs, user_extra_registrations uer\n        WHERE r.registration_type = rt.registration_type\n        AND fs.id = r.financing_id\n        AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))\n        AND (r.registration_number = uer.registration_number OR r.base_reg_number = uer.registration_number)\n        AND uer.removed_ind IS NULL\n        AND NOT EXISTS (SELECT r3.id\n                            FROM registrations r3\n                            WHERE r3.financing_id = fs.id\n                            AND r3.registration_type_cl = 'DISCHARGE'\n                            AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days')))"
    )
    op.drop_entity(public_account_registration_count_vw)

    public_account_draft_vw = PGView(
        schema="public",
        signature="account_draft_vw",
        definition="SELECT d.document_number,\n       d.create_ts,\n       d.registration_type,\n       d.registration_type_cl,\n       rt.registration_desc,\n       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN ''\n            ELSE d.registration_number END base_reg_num,\n       d.draft ->> 'type' AS draft_type,\n       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,\n       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN\n                 d.draft -> 'financingStatement' ->> 'clientReferenceId'\n            WHEN d.registration_type_cl = 'AMENDMENT' THEN d.draft -> 'amendmentStatement' ->> 'clientReferenceId'\n            WHEN d.registration_type_cl = 'CHANGE' THEN d.draft -> 'changeStatement' ->> 'clientReferenceId'\n            ELSE '' END client_reference_id,\n       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND\n                 d.draft -> 'financingStatement' -> 'registeringParty' IS NOT NULL THEN\n                 CASE WHEN d.draft -> 'financingStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN\n                           d.draft -> 'financingStatement' -> 'registeringParty' ->> 'businessName'\n                      WHEN d.draft -> 'financingStatement' -> 'registeringParty' ->> 'personName' IS NOT NULL THEN\n                      concat(d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',\n                             d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'last')\n                 END\n            WHEN d.registration_type_cl = 'AMENDMENT' AND\n                 (d.draft -> 'amendmentStatement' -> 'registeringParty') IS NOT NULL THEN\n                 CASE WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN\n                           d.draft -> 'amendmentStatement' -> 'registeringParty' ->> 'businessName'\n                      WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' IS NOT NULL THEN\n                        concat(d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',\n                               d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'last')\n                 END\n            ELSE '' END registering_party,\n      CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND\n                 d.draft -> 'financingStatement' -> 'securedParties' IS NOT NULL THEN\n                (SELECT string_agg((CASE WHEN (sp -> 'businessName') IS NOT NULL THEN\n                                             (sp ->> 'businessName')\n                                         WHEN sp -> 'personName' IS NOT NULL THEN\n                                            concat((sp -> 'personName' ->> 'first'), ' ',\n                                                   (sp -> 'personName' ->> 'last'))\n                                         END),\n                                   ',')\n                   FROM json_array_elements(d.draft -> 'financingStatement' -> 'securedParties') sp)\n          WHEN d.registration_type_cl = 'AMENDMENT' AND\n                 d.draft -> 'amendmentStatement' -> 'securedParties' IS NOT NULL THEN\n                (SELECT string_agg((CASE WHEN (sp2 -> 'businessName') IS NOT NULL THEN\n                                             (sp2 ->> 'businessName')\n                                         WHEN sp2 -> 'personName' IS NOT NULL THEN\n                                            concat((sp2 -> 'personName' ->> 'first'), ' ',\n                                                   (sp2 -> 'personName' ->> 'last'))\n                                         END),\n                                   ',')\n                   FROM json_array_elements(d.draft -> 'amendmentStatement' -> 'securedParties') sp2)\n            ELSE ' ' END secured_party,\n       (SELECT CASE WHEN d.user_id IS NULL THEN ''\n                    ELSE (SELECT u.firstname || ' ' || u.lastname\n                            FROM users u\n                           WHERE u.username = d.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n       d.account_id,\n       d.id, d.registration_number\n  FROM drafts d, registration_types rt\n WHERE d.registration_type = rt.registration_type"
    )
    op.drop_entity(public_account_draft_vw)

    public_searchkey_vehicle = PGFunction(
        schema="public",
        signature="searchkey_vehicle(serial_number IN VARCHAR)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $$\n    DECLARE\n            v_search_key VARCHAR(25);\n            BEGIN\n            v_search_key := REGEXP_REPLACE(serial_number, '[^0-9A-Za-z]','','gi');\n            v_search_key := LPAD(SUBSTR(v_search_key, LENGTH(v_search_key) - 5, 6),6,'0');\n            v_search_key := REGEXP_REPLACE(\n                            REGEXP_REPLACE(\n                            REGEXP_REPLACE(\n                            REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                REGEXP_REPLACE(\n                                    REGEXP_REPLACE(\n                                    REGEXP_REPLACE(\n                                    REGEXP_REPLACE(v_search_key,'I','1','gi'),\n                                                    'L','1','gi'),\n                                                    'Z','2','gi'),\n                                                    'H','4','gi'),\n                                                    'Y','4','gi'),\n                                                    'S','5','gi'),\n                                                    'C','6','gi'),\n                                                    'G','6','gi'),\n                                                    'B','8','gi'),\n                                                    'O','0','gi'),\n                                                    '[^\\w]+|[A-Za-z]+','0','gi');\n                v_search_key := LPAD(v_search_key,6,'0');\t\t\t\t\t\t\t\t\t\t\t \n            RETURN v_search_key;\n        END\n        ;\n    $$"
    )
    op.drop_entity(public_searchkey_vehicle)

    public_searchkey_mhr = PGFunction(
        schema="public",
        signature="searchkey_mhr(mhr_number IN VARCHAR)",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    DECLARE\n        v_search_key VARCHAR(6);\n    BEGIN\n        v_search_key := TRIM(REGEXP_REPLACE(mhr_number,'[^0-9A-Za-z]','','gi'));\n        v_search_key := LPAD(REGEXP_REPLACE(v_search_key,'[$A-Za-z]','0'),6,'0');\n        RETURN v_search_key;\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_searchkey_mhr)

    public_searchkey_last_name = PGFunction(
        schema="public",
        signature="searchkey_last_name(actual_name IN character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    COST 100\n    VOLATILE PARALLEL UNSAFE\n    AS\n    $$\nDECLARE\n        v_last_name VARCHAR(60);\n    BEGIN\n        -- Remove special characters last name\n        v_last_name := regexp_replace(actual_name,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_last_name := regexp_replace(v_last_name, '(.)\\1{1,}', '\\1', 'g');\n\t\t-- Remove special characters first name\n     RETURN UPPER(v_last_name);\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_searchkey_last_name)

    public_searchkey_first_name = PGFunction(
        schema="public",
        signature="searchkey_first_name(actual_name IN character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS\n    $$\nDECLARE\n        v_search_key VARCHAR(92);\n    BEGIN\n        -- Remove special characters first name\n        v_search_key := regexp_replace(actual_name,'[^\\w]+',' ','gi');\n        -- Remove prefixes first name\n\t\tv_search_key := regexp_replace(v_first_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_search_key := trim(regexp_replace(v_first_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_search_key := regexp_replace(v_first_name, '(.)\\1{1,}', '\\1', 'g');\n        RETURN UPPER(v_search_key);\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_searchkey_first_name)

    public_searchkey_business_name = PGFunction(
        schema="public",
        signature="searchkey_business_name(actual_name IN VARCHAR)",
        definition="RETURNS character varying\n LANGUAGE plpgsql\nAS $function$\nDECLARE\n    v_search_key VARCHAR(150);\n    v_name_2  VARCHAR(150);\n    v_name_3  VARCHAR(150);\n    v_name_4  VARCHAR(150);\n    v_name_5  VARCHAR(150);\n    v_word_1  VARCHAR(150);\n    v_word_2  VARCHAR(150);\n    v_word_3  VARCHAR(150);\n    v_word_4  VARCHAR(150);\n\t\nBEGIN\n    IF LENGTH(SPLIT_PART(REGEXP_REPLACE(actual_name,'[A-Z]+','','g'),' ',1))>=5 then\n        v_search_key := REGEXP_REPLACE(actual_name,'^0000|^000|^00|^0','','g');\n        v_search_key := REGEXP_REPLACE(SPLIT_PART(v_search_key,' ',1),'[A-Za-z]+','','g');\n        v_search_key := REGEXP_REPLACE(v_search_key,'[^\\w\\s]+','','gi');\n    END IF;\n\n    IF  array_length(string_to_array(v_search_key,''),1) is not null then\n        RETURN v_search_key;\n    ELSE\n        v_search_key := split_part(upper(actual_name), 'INC', 1);\n        v_search_key := split_part(upper(v_search_key), 'LTD', 1);\n        v_search_key := split_part(upper(v_search_key), 'LTEE', 1);\n        v_search_key := split_part(upper(v_search_key), 'LIMITED', 1);\n        v_search_key := split_part(upper(v_search_key), 'INCORPORATED', 1);\n        v_search_key := split_part(upper(v_search_key), 'INCORPORATEE', 1);\n        v_search_key := split_part(upper(v_search_key), 'INCORPORATION', 1);\n\t\tv_search_key := regexp_replace(v_search_key, '\\([^()]*\\)', '', 'gi');\n        v_search_key := regexp_replace(v_search_key,'^THE','','gi');\n        v_search_key := regexp_replace(v_search_key,'\\y(AND|DBA)\\y', '', 'g');\n        v_search_key := REGEXP_REPLACE(v_search_key,'[^\\w\\s]+',' ','gi');\n        v_search_key := TRIM(REGEXP_REPLACE(v_search_key, '\\s+', ' ', 'gi'));\n        v_search_key := REGEXP_REPLACE(v_search_key,'\\y( S$)\\y','','gi');\n    END IF;\n\n    IF SUBSTR(v_search_key,2,1)=' ' AND SUBSTR(v_search_key,4,1)=' ' AND SUBSTR(v_search_key,6,1)!=' ' THEN\n        v_search_key := TRIM(REGEXP_REPLACE(SUBSTR(v_search_key,1,3),'\\s+', '', 'gi'))||SUBSTR(v_search_key,4,146);\n    ELSIF SUBSTR(v_search_key,2,1)=' ' AND SUBSTR(v_search_key,4,1)=' ' AND SUBSTR(v_search_key,6,1)=' ' THEN \n        v_search_key := TRIM(REGEXP_REPLACE(SUBSTR(v_search_key,1,3),'\\s+', '', 'gi'))||SUBSTR(v_search_key,5,145);\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n\n    v_name_2 := SPLIT_PART(v_search_key,' ',2);\n    v_name_3 := SPLIT_PART(v_search_key,' ',3);\n    v_name_4 := SPLIT_PART(v_search_key,' ',4);\n    v_name_5 := SPLIT_PART(v_search_key,' ',5);\n    v_word_1 := (select word from common_word where word = v_name_2 );\n    v_word_2 := (select word from common_word where word = v_name_3 );\n    v_word_3 := (select word from common_word where word = v_name_4 );\n    v_word_4 := (select word from common_word where word = v_name_5 );\n\n   \n\n    IF v_word_2 is not null THEN\n        v_search_key := regexp_replace(v_search_key,v_word_2,'','ig');\n    ELSE    \n        v_search_key := v_search_key;\n    END IF;\n\n    IF v_word_3 is not null THEN\n    v_search_key := regexp_replace(v_search_key,v_word_3,'','ig');\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n\n    IF v_word_4 is not null THEN\n        v_search_key := regexp_replace(v_search_key,v_word_4,'','ig');\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n    \n    IF  v_search_key is null or LENGTH(TRIM(v_search_key)) = 0 THEN\n        v_search_key := actual_name;\n    ELSE\n        v_search_key := v_search_key;\n    END IF;\n\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(BRITISH COLUMBIA|BRITISHCOLUMBIA)\\y','BC','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(LIMITED|PARTNERSHIP|GP|LLP|LP)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(SOCIETY|ASSOCIATION|TRUST|TRUSTEE|SOCIETE)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(INCORPORATED|INCORPOREE|INCORPORATION|INCORP|INC)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(COMPANY|CORPORATIONS|CORPORATION|CORPS|CORP|CO)\\y','','gi');\n    v_search_key := REGEXP_REPLACE(v_search_key,'\\y(LIMITEE|LTEE|LTD|ULC)\\y','','gi');\n\tv_search_key := regexp_replace(v_search_key,'\\y(AND)\\y','AN','gi');\n\tv_search_key := regexp_replace(v_search_key,'&','AN','gi');\n\tv_search_key := regexp_replace(v_search_key, '\\([^()]*\\)', '', 'gi');\n    v_search_key := regexp_replace(v_search_key,'^THE','','gi');\n    v_search_key := regexp_replace(v_search_key,'\\y(DBA)\\y', '', 'g');\n\tv_search_key := REGEXP_REPLACE(v_search_key,'[^\\w\\s]+','','gi');\n    v_search_key := trim(regexp_replace(v_search_key, '\\s+', '', 'gi'));\n\t\n    RETURN v_search_key;\n\nEND\n    ; \n$function$"
    )
    op.drop_entity(public_searchkey_business_name)

    public_searchkey_aircraft = PGFunction(
        schema="public",
        signature="searchkey_aircraft(aircraft_number IN VARCHAR)",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    DECLARE\n        v_search_key VARCHAR(25);\n    BEGIN\n        v_search_key := TRIM(REGEXP_REPLACE(aircraft_number,'\\s|-','','gi'));\n        IF (LENGTH(v_search_key) > 6) THEN\n        v_search_key := RIGHT(v_search_key, 6);\n        END IF;\n        RETURN v_search_key;\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_searchkey_aircraft)

    public_match_individual_name = PGFunction(
        schema="public",
        signature="match_individual_name(lastname character varying,firstname character varying,sq_last real,sq_first real,sq_def real)",
        definition="RETURNS integer[]\n  LANGUAGE plpgsql\n      AS $function$\nDECLARE\n    v_ids  INTEGER ARRAY;\n  BEGIN\n\n    SET pg_trgm.similarity_threshold = 0.29; -- assigning from variable does not work\n\n    WITH q AS (SELECT(SELECT public.searchkey_individual(lastname, firstname)) AS INDKEY,\n               (SELECT public.searchkey_last_name(lastname)) AS search_last_key,              \n              lastname AS LAST,\n              firstname AS FIRST,\n              LENGTH(lastname) AS LAST_LENGTH,\n              LENGTH(firstname) AS FIRST_LENGTH,\n              SUBSTR(firstname,1,1) AS FIRST_CHAR1,\n              SUBSTR(firstname,2,1) AS FIRST_CHAR2,\n              SUBSTR((SELECT(SELECT public.searchkey_individual(lastname, firstname))),1,1) AS INDKEY_CHAR1,\n              (SELECT public.sim_number(lastname)) as simnumber,\n              (SELECT public.individual_split_1(lastname)) AS SPLIT1,\n              (SELECT public.individual_split_2(lastname)) AS SPLIT2,\n              (SELECT public.individual_split_3(lastname)) AS SPLIT3,\n              (SELECT public.individual_split_1(firstname)) AS SPLIT4, \n              (SELECT public.individual_split_2(firstname)) AS SPLIT5\n              )\n    SELECT array_agg(p.id)\n      INTO v_ids\n  FROM PARTIES p,q\n WHERE (p.LAST_NAME_key = search_last_key OR \n        (first_name_key_char1 = INDKEY_CHAR1 AND\n         indkey <% p.FIRST_NAME_KEY AND \n         LEVENSHTEIN(p.FIRST_NAME_KEY,indkey) <= 2)) \n   AND p.PARTY_TYPE = 'DI'\n   AND p.REGISTRATION_ID_END IS NULL\n   AND (\n        (p.FIRST_NAME = FIRST OR p.MIDDLE_INITIAL= FIRST)\n    OR  (p.FIRST_NAME IN (SELECT NAME \n                            FROM public.NICKNAMES \n                           WHERE NAME_ID IN (SELECT NAME_ID \n                                               FROM public.NICKNAMES WHERE(FIRST) = NAME))\n        )\n    OR  (FIRST_LENGTH = 1 AND FIRST_CHAR1 = p.first_name_char1)\n    OR  (FIRST_LENGTH > 1 AND FIRST_CHAR1 = p.first_name_char1 AND p.first_name_char2 IS NOT NULL AND p.first_name_char2 = '-')\n    OR  (FIRST_LENGTH > 1 AND FIRST_CHAR2 IS NOT NULL AND FIRST_CHAR2 = '-' AND FIRST_CHAR1 = p.first_name_char1)\n    OR (p.first_name_char1 = FIRST_CHAR1 AND LENGTH(p.first_name) = 1)\n    OR (indkey <% p.FIRST_NAME_KEY AND\n        SIMILARITY(p.FIRST_NAME_KEY, indkey) >= SIMNUMBER AND \n        p.first_name_key_char1 = INDKEY_CHAR1 AND \n        ((FIRST <% p.first_name AND \n          SIMILARITY(p.FIRST_NAME,FIRST)>= sq_first AND \n          (LAST_LENGTH BETWEEN LENGTH(p.LAST_NAME)-3 AND LENGTH(p.LAST_NAME)+3 OR LAST_LENGTH >= 10)) OR\n          (p.first_name_char1 = FIRST_CHAR1 OR P.FIRST_NAME = FIRST_CHAR1))          \n       )\n    OR (FIRST <% p.first_name AND\n        SIMILARITY(p.FIRST_NAME,FIRST)>= sq_first AND \n        (p.last_name_split1 = SPLIT1 OR \n         p.last_name_split2 = SPLIT1 and p.last_name_split2 != '' OR\n         p.last_name_split3 = SPLIT1 and p.last_name_split3 != '' OR\n         p.last_name_split1 = SPLIT2 OR \n         p.last_name_split2 = SPLIT2 and p.last_name_split2 != '' OR\n         p.last_name_split3 = SPLIT2 and p.last_name_split3 != '' OR\n         p.last_name_split1 = SPLIT3 OR \n         p.last_name_split2 = SPLIT3 and p.last_name_split2 != '' OR\n         p.last_name_split3 = SPLIT3 and p.last_name_split3 != ''\n        )\n       )       \n    OR (LAST <% p.LAST_NAME AND\n        SIMILARITY(p.LAST_NAME,LAST)>= SIMNUMBER AND \n        (p.first_name_split1 = SPLIT4 OR\n         p.first_name_split2 = SPLIT4 and p.first_name_split2 != '' OR\n         p.first_name_split1 = SPLIT5 OR\n         p.first_name_split2 = SPLIT5 and p.first_name_split2 != ''\n        )\n       )\n    )\n    ;\n    RETURN v_ids;\n  END\n    ; \n    $function$"
    )
    op.drop_entity(public_match_individual_name)

    public_searchkey_individual = PGFunction(
        schema="public",
        signature="searchkey_individual(last_name character varying, first_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n        v_ind_key VARCHAR(100);\n\t\tv_last_name VARCHAR(50);\n\t\tv_first_name VARCHAR(50);\n    BEGIN\n\t    -- Remove special characters last name\n        v_last_name := regexp_replace(LAST_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_last_name := regexp_replace(v_last_name, '(.)\\1{1,}', '\\1', 'g');\n\t\t-- Remove special characters first name\n        v_first_name := regexp_replace(first_name,'[^\\w]+',' ','gi');\n        -- Remove prefixes first name\n\t\tv_first_name := regexp_replace(v_first_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\t-- Remove extra spaces\n\t\tv_first_name := trim(regexp_replace(v_first_name, '\\s+', ' ', 'gi'));\n\t\t-- Remove repeating letters\n\t\tv_first_name := regexp_replace(v_first_name, '(.)\\1{1,}', '\\1', 'g');\n\n\t\t-- join last first name\n\t\tv_ind_key := v_last_name||' '||v_first_name;\n\n     RETURN UPPER(v_ind_key);\n    END\n    ; \n    $function$"
    )
    op.drop_entity(public_searchkey_individual)

    public_individual_split_3 = PGFunction(
        schema="public",
        signature="individual_split_3(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n  v_last_name VARCHAR(150);\n  v_split_3 VARCHAR(50);\n    BEGIN\n        -- Remove special characters last name\n        v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Split second name\n         v_split_3 := split_part(v_last_name,' ',3);\n\t  RETURN UPPER(v_split_3);\n\n  END\n    ; \n    $function$"
    )
    op.drop_entity(public_individual_split_3)

    public_individual_split_2 = PGFunction(
        schema="public",
        signature="individual_split_2(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n  v_last_name VARCHAR(150);\n  v_split_2 VARCHAR(50);\n    BEGIN\n        -- Remove special characters last name\n        v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffixes last name\n\t\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n\t\tv_last_name := trim(regexp_replace(v_last_name, '\\s+', ' ', 'gi'));\n\t\t-- Split second name\n         v_split_2 := split_part(v_last_name,' ',2);\n\t  RETURN UPPER(v_split_2);\n\n  END\n    ; \n    $function$"
    )
    op.drop_entity(public_individual_split_2)

    public_individual_split_1 = PGFunction(
        schema="public",
        signature="individual_split_1(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\nDECLARE\n  v_last_name VARCHAR(150);\n  v_split_1 VARCHAR(50);\n  BEGIN\n        -- Remove special characters last name\n    v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n        -- Remove prefixes suffix\n\tv_last_name := regexp_replace(v_last_name,'\\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\\y','','gi');\n       \t-- Split first name\n\tv_last_name := trim(v_last_name);\n    v_split_1 := split_part(v_last_name,' ',1);\n\t  RETURN UPPER(v_split_1);\n\n  END\n    ; \n    $function$"
    )
    op.drop_entity(public_individual_split_1)

    public_sim_number = PGFunction(
        schema="public",
        signature="sim_number(actual_name character varying)",
        definition="RETURNS numeric\n LANGUAGE plpgsql\nAS $function$\nDECLARE\n   v_name VARCHAR(60);\n   v_sim_number DECIMAL;\n  BEGIN\n     v_name := regexp_replace(actual_name, '(.)\\1{1,}', '\\1', 'g');\n\n     if length((SELECT public.searchkey_last_name(v_name))) <= 3 then\n\t v_sim_number := .65 ;\n\t else\n\t v_sim_number := .46 ;\n   end if;\n  return v_sim_number;\n  END\n    ; \n    $function$"
    )
    op.drop_entity(public_sim_number)

    public_searchkey_nickname_match = PGFunction(
        schema="public",
        signature="searchkey_nickname_match(search_key IN VARCHAR, name1 IN VARCHAR, name2 IN VARCHAR, name3 IN varchar)",
        definition="RETURNS int\n    LANGUAGE plpgsql\n    AS\n    $$\n    -- Cartesion cross-product on nickname\\: search key may have up to 3 names, a nickname match on any name is a hit.\n    -- search_key is party.first_name_key to match on\\: may be 3 names separated by a space character.\n    -- name1, name2, name3 are names already parsed from the search criteria\\: name2 and name3 may be null. \n    DECLARE\n        v_name1 VARCHAR(50);\n        v_name2 VARCHAR(50);\n        v_name3 VARCHAR(50);\n        v_match_count integer;\n    BEGIN\n        v_match_count := 0;\n        v_name1 = split_part(search_key, ' ', 1);\n        v_name2 = split_part(search_key, ' ', 2);  -- May be null\n        v_name3 = split_part(search_key, ' ', 3);  -- May be null\n        SELECT COUNT(name_id)\n        INTO v_match_count\n        FROM nicknames n1\n        WHERE (name = v_name1 AND \n                n1.name_id IN (SELECT n2.name_id \n                                FROM nicknames n2\n                                WHERE n2.name IN (name1, name2, name3))) OR\n            (v_name2 IS NOT NULL AND\n                name = v_name2 AND \n                n1.name_id IN (SELECT n2.name_id \n                                FROM nicknames n2\n                                WHERE n2.name IN (name1, name2, name3))) OR\n            (v_name3 IS NOT NULL AND\n                name = v_name3 AND \n                n1.name_id IN (SELECT n2.name_id \n                                FROM nicknames n2\n                                WHERE n2.name IN (name1, name2, name3)));\n\n        RETURN v_match_count;\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_searchkey_nickname_match)

    public_searchkey_name_match = PGFunction(
        schema="public",
        signature="searchkey_name_match(search_key IN VARCHAR, name1 IN VARCHAR, name2 IN VARCHAR, name3 IN varchar)",
        definition="RETURNS int\n    LANGUAGE plpgsql\n    AS\n    $$\n    -- Cartesion cross-product on name\\: search key may have up to 3 names, an exact match on any name is a hit.\n    -- search_key is party.first_name_key to match on\\: may be 3 names separated by a space character.\n    -- name1, name2, name3 are names already parsed from the search criteria\\: name2 and name3 may be null. \n    DECLARE\n        v_name1 VARCHAR(50);\n        v_name2 VARCHAR(50);\n        v_name3 VARCHAR(50);\n        v_match_count integer;\n    BEGIN\n        v_match_count := 0;\n        v_name1 = split_part(search_key, ' ', 1);\n        v_name2 = split_part(search_key, ' ', 2);  -- May be null\n        v_name3 = split_part(search_key, ' ', 3);  -- May be null\n        IF (v_name1 = name1 OR (name2 IS NOT NULL AND v_name1 = name2) OR (name3 IS NOT NULL AND v_name1 = name3)) THEN\n        v_match_count := 1;\n        ELSIF (v_name2 IS NOT NULL AND v_name2 = name1 OR (name2 IS NOT NULL AND v_name2 = name2) OR (name3 IS NOT NULL AND v_name2 = name3)) THEN\n        v_match_count := 1;\n        ELSIF (v_name3 IS NOT NULL AND v_name3 = name1 OR (name2 IS NOT NULL AND v_name3 = name2) OR (name3 IS NOT NULL AND v_name3 = name3)) THEN\n        v_match_count := 1;\n        END IF;\n\n        RETURN v_match_count;\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_searchkey_name_match)

    public_get_registration_num = PGFunction(
        schema="public",
        signature="get_registration_num()",
        definition="RETURNS VARCHAR\n    LANGUAGE plpgsql\n    AS\n    $$\n    BEGIN\n        RETURN trim(to_char(nextval('registration_num_q_seq'), '000000')) || 'Q';\n    END\n    ; \n    $$"
    )
    op.drop_entity(public_get_registration_num)

    public_get_draft_document_number = PGFunction(
        schema="public",
        signature="get_draft_document_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    DECLARE\n      v_id INTEGER;\n      v_doc_num VARCHAR(10);\n    BEGIN\n      v_id := nextval('document_number_seq');\n      IF v_id >= 10000000 THEN\n        v_doc_num := 'D' || trim(to_char(nextval('document_number_seq'), '00000000'));\n      ELSE\n        v_doc_num := 'D' || trim(to_char(nextval('document_number_seq'), '0000000'));\n      END IF;\n      RETURN v_doc_num;\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_draft_document_number)

    public_business_name_strip_designation = PGFunction(
        schema="public",
        signature="business_name_strip_designation(actual_name character varying)",
        definition="RETURNS character varying\n LANGUAGE plpgsql\n AS $function$\n DECLARE\n v_base VARCHAR(150);\n BEGIN\n v_base := regexp_replace(regexp_replace(regexp_replace(actual_name,'[^\\w\\s]+','','gi'),'\\y(CORPORATION|INCORPORATED|INCORPOREE|LIMITED|LIMITEE|NON PERSONAL LIABILITY|CORP|INC|LTD|LTEE|NPL|ULC)\\y','','gi'),'\\s+', '', 'gi');\n RETURN TRIM(v_base);\n END\n ;\n  $function$"
    )
    op.drop_entity(public_business_name_strip_designation)

    with op.batch_alter_table('securities_act_orders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_securities_act_orders_securities_act_notice_id'))
        batch_op.drop_index(batch_op.f('ix_securities_act_orders_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_securities_act_orders_registration_id'))

    op.drop_table('securities_act_orders')
    with op.batch_alter_table('mail_reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mail_reports_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mail_reports_party_id'))
        batch_op.drop_index(batch_op.f('ix_mail_reports_create_ts'))

    op.drop_table('mail_reports')
    with op.batch_alter_table('verification_reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_verification_reports_registration_id'))
        batch_op.drop_index(batch_op.f('ix_verification_reports_create_ts'))

    op.drop_table('verification_reports')
    with op.batch_alter_table('trust_indentures', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_trust_indentures_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_trust_indentures_registration_id'))
        batch_op.drop_index(batch_op.f('ix_trust_indentures_financing_id'))

    op.drop_table('trust_indentures')
    with op.batch_alter_table('serial_collateral', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_serial_collateral_srch_vin'))
        batch_op.drop_index(batch_op.f('ix_serial_collateral_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_serial_collateral_registration_id'))
        batch_op.drop_index(batch_op.f('ix_serial_collateral_mhr_number'))
        batch_op.drop_index(batch_op.f('ix_serial_collateral_financing_id'))

    op.drop_table('serial_collateral')
    with op.batch_alter_table('securities_act_notices', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_securities_act_notices_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_securities_act_notices_registration_id'))

    op.drop_table('securities_act_notices')
    with op.batch_alter_table('parties', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_parties_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_parties_registration_id'))
        batch_op.drop_index(batch_op.f('ix_parties_middle_initial'))
        batch_op.drop_index(batch_op.f('ix_parties_last_name_split3'))
        batch_op.drop_index(batch_op.f('ix_parties_last_name_split2'))
        batch_op.drop_index(batch_op.f('ix_parties_last_name_split1'))
        batch_op.drop_index(batch_op.f('ix_parties_last_name_key'))
        batch_op.drop_index(batch_op.f('ix_parties_first_name_split2'))
        batch_op.drop_index(batch_op.f('ix_parties_first_name_split1'))
        batch_op.drop_index(batch_op.f('ix_parties_first_name_key'))
        batch_op.drop_index(batch_op.f('ix_parties_financing_id'))
        batch_op.drop_index(batch_op.f('ix_parties_business_srch_key'))
        batch_op.drop_index(batch_op.f('ix_parties_business_name'))
        batch_op.drop_index(batch_op.f('ix_parties_branch_id'))
        batch_op.drop_index(batch_op.f('ix_parties_address_id'))

    op.drop_table('parties')
    with op.batch_alter_table('general_collateral_legacy', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_general_collateral_legacy_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_general_collateral_legacy_registration_id'))
        batch_op.drop_index(batch_op.f('ix_general_collateral_legacy_financing_id'))

    op.drop_table('general_collateral_legacy')
    with op.batch_alter_table('general_collateral', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_general_collateral_registration_id_end'))
        batch_op.drop_index(batch_op.f('ix_general_collateral_registration_id'))
        batch_op.drop_index(batch_op.f('ix_general_collateral_financing_id'))

    op.drop_table('general_collateral')
    with op.batch_alter_table('court_orders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_court_orders_registration_id'))

    op.drop_table('court_orders')
    with op.batch_alter_table('client_codes_historical', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_codes_historical_users_id'))
        batch_op.drop_index(batch_op.f('ix_client_codes_historical_name'))
        batch_op.drop_index(batch_op.f('ix_client_codes_historical_head_id'))
        batch_op.drop_index(batch_op.f('ix_client_codes_historical_branch_id'))
        batch_op.drop_index(batch_op.f('ix_client_codes_historical_address_id'))

    op.drop_table('client_codes_historical')
    with op.batch_alter_table('registrations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_registrations_registration_ts'))
        batch_op.drop_index(batch_op.f('ix_registrations_registration_number'))
        batch_op.drop_index(batch_op.f('ix_registrations_financing_id'))
        batch_op.drop_index(batch_op.f('ix_registrations_draft_id'))
        batch_op.drop_index(batch_op.f('ix_registrations_base_reg_number'))
        batch_op.drop_index(batch_op.f('ix_registrations_account_id'))

    op.drop_table('registrations')
    with op.batch_alter_table('client_codes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_codes_users_id'))
        batch_op.drop_index(batch_op.f('ix_client_codes_name'))
        batch_op.drop_index(batch_op.f('ix_client_codes_head_id'))
        batch_op.drop_index(batch_op.f('ix_client_codes_address_id'))

    op.drop_table('client_codes')
    op.drop_table('search_results')
    op.drop_table('previous_financing_statements')
    with op.batch_alter_table('drafts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_drafts_create_ts'))
        batch_op.drop_index(batch_op.f('ix_drafts_account_id'))

    op.drop_table('drafts')
    op.drop_table('addresses')
    op.drop_table('user_profiles')
    with op.batch_alter_table('search_requests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_search_requests_search_ts'))
        batch_op.drop_index(batch_op.f('ix_search_requests_account_id'))

    op.drop_table('search_requests')
    op.drop_table('registration_types')
    op.drop_table('province_types')
    op.drop_table('financing_statements')
    with op.batch_alter_table('event_tracking', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_event_tracking_key_id'))
        batch_op.drop_index(batch_op.f('ix_event_tracking_event_ts'))
        batch_op.drop_index(batch_op.f('ix_event_tracking_event_tracking_type'))

    op.drop_table('event_tracking')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_idp_userid'))

    op.drop_table('users')
    with op.batch_alter_table('user_extra_registrations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_extra_registrations_registration_number'))
        batch_op.drop_index(batch_op.f('ix_user_extra_registrations_account_id'))

    op.drop_table('user_extra_registrations')
    op.drop_table('state_types')
    op.drop_table('serial_types')
    op.drop_table('securities_act_types')
    op.drop_table('search_types')
    op.drop_table('registration_type_classes')
    op.drop_table('party_types')
    op.drop_table('event_tracking_types')
    op.drop_table('country_types')
    with op.batch_alter_table('account_bcol_ids', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_account_bcol_ids_account_id'))

    op.drop_table('account_bcol_ids')

    op.drop_index(op.f('ix_test_search_results_search_id'), table_name='test_search_results')
    op.drop_table('test_search_results')
    op.drop_index(op.f('ix_test_searches_batch_id'), table_name='test_searches')
    op.drop_table('test_searches')
    op.drop_table('test_search_batches')

    op.drop_index(op.f('ix_nickname_name_id'), table_name='nicknames')
    op.drop_index(op.f('ix_nickname_name'), table_name='nicknames')
    op.drop_table('nicknames')

    # Manually added common_word, used by search.
    op.drop_table('common_word')
    with op.batch_alter_table('common_word', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_common_word_word'))

    # Manually added drop sequence commands ###
    op.execute(DropSequence(Sequence('document_number_seq')))
    op.execute(DropSequence(Sequence('registration_num_q_seq')))
    op.execute(DropSequence(Sequence('account_bcol_id_seq')))
    op.execute(DropSequence(Sequence('address_id_seq')))
    op.execute(DropSequence(Sequence('code_branch_id_seq')))
    op.execute(DropSequence(Sequence('historical_head_id_seq')))
    op.execute(DropSequence(Sequence('court_order_id_seq')))
    op.execute(DropSequence(Sequence('draft_id_seq')))
    op.execute(DropSequence(Sequence('event_tracking_id_seq')))
    op.execute(DropSequence(Sequence('financing_id_seq')))
    op.execute(DropSequence(Sequence('general_id_seq')))
    op.execute(DropSequence(Sequence('mail_report_id_seq')))
    op.execute(DropSequence(Sequence('party_id_seq')))
    op.execute(DropSequence(Sequence('registration_id_seq')))
    op.execute(DropSequence(Sequence('search_id_seq')))
    op.execute(DropSequence(Sequence('securities_act_notice_id_seq')))
    op.execute(DropSequence(Sequence('securities_act_order_id_seq')))
    op.execute(DropSequence(Sequence('test_search_batches_id_seq')))
    op.execute(DropSequence(Sequence('test_search_results_id_seq')))
    op.execute(DropSequence(Sequence('test_searches_id_seq')))
    op.execute(DropSequence(Sequence('trust_id_seq')))
    op.execute(DropSequence(Sequence('user_extra_registration_seq')))
    op.execute(DropSequence(Sequence('user_id_seq')))
    op.execute(DropSequence(Sequence('vehicle_id_seq')))
    op.execute(DropSequence(Sequence('verification_report_id_seq')))
    op.execute(DropSequence(Sequence('word_id_seq')))
    op.execute(DropSequence(Sequence('name_id_seq')))

    # Manually added drop extensions
    public_pg_trgm = PGExtension(
        schema="public",
        signature="pg_trgm"
    )
    op.drop_entity(public_pg_trgm)

    public_btree_gist = PGExtension(
        schema="public",
        signature="btree_gist"
    )
    op.drop_entity(public_btree_gist)

    public_fuzzystrmatch = PGExtension(
        schema="public",
        signature="fuzzystrmatch"
    )
    op.drop_entity(public_fuzzystrmatch)

    public_mhr_account_reg_vw = PGView(
        schema="public",
        signature="mhr_account_reg_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts,\n        (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                      WHEN p.middle_name IS NOT NULL THEN p.first_name || ' ' || p.middle_name || ' ' || p.last_name\n                      ELSE p.first_name || ' ' || p.last_name\n                END\n            FROM mhr_parties p\n          WHERE p.registration_id = r.id \n            AND p.party_type = 'SUBMITTING') AS submitting_name,\n        r.client_reference_id,\n        r.registration_type,       \n        (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name\n                                  WHEN p.middle_name IS NOT NULL THEN p.first_name || ' ' || p.middle_name || ' ' || p.last_name\n                                  ELSE p.first_name || ' ' || p.last_name END), '\\n')\n            FROM mhr_registrations r1, mhr_owner_groups og, mhr_parties p\n          WHERE r1.mhr_number = r.mhr_number \n            AND r1.id = og.registration_id\n            AND og.registration_id = p.registration_id\n            AND og.id = p.owner_group_id\n            AND r1.registration_ts = (SELECT MAX(r2.registration_ts)\n                                        FROM mhr_registrations r2, mhr_owner_groups og2\n                                        WHERE r2.mhr_number = r.mhr_number\n                                          AND og2.registration_id = r2.id\n                                          AND r2.id <= r.id)) AS owner_names,       \n        (SELECT CASE WHEN r.user_id IS NULL THEN ''\n                      ELSE (SELECT u.firstname || ' ' || u.lastname\n                              FROM users u\n                            WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,\n        d.document_id,\n        d.document_registration_number,\n        (SELECT d2.document_type\n            FROM mhr_documents d2\n          WHERE d2.id = (SELECT MAX(d3.id)\n                            FROM mhr_documents d3, mhr_registrations r2\n                          WHERE r2.id = d3.registration_id\n                            AND r2.mhr_number = r.mhr_number)) AS last_doc_type,\n        (SELECT n.status_type\n            FROM mhr_notes n\n          WHERE n.registration_id = r.id) AS note_status,\n        (SELECT n.expiry_date\n            FROM mhr_notes n\n          WHERE n.registration_id = r.id) AS note_expiry,\n        (CASE\n            WHEN d.document_type in ('NCAN', 'NRED') THEN\n              (SELECT n.document_type\n                FROM mhr_notes n\n                WHERE n.status_type != 'ACTIVE'\n                  AND n.change_registration_id = r.id\n                  AND n.document_type != 'CAUC'\n                  AND n.document_type != 'CAUE'\n              FETCH FIRST 1 ROWS ONLY)\n            ELSE NULL\n          END) AS cancel_doc_type,\n        (SELECT n.document_type\n            FROM mhr_notes n, mhr_registrations r2\n          WHERE r2.mhr_number = r.mhr_number\n            AND r2.id = n.registration_id\n            AND n.status_type = 'ACTIVE'\n            AND (n.document_type IN ('TAXN', 'NCON', 'REST') OR \n                  (n.document_type IN ('REG_103', 'REG_103E') AND \n                  n.expiry_date IS NOT NULL AND n.expiry_date > (now() at time zone 'UTC')))\n          FETCH FIRST 1 ROWS ONLY) AS frozen_doc_type,\n        r.account_id,\n        dt.document_type_desc,\n        (SELECT CASE WHEN r.registration_type NOT IN ('MHREG', 'MHREG_CONVERSION') THEN ''\n              ELSE (SELECT lcv.registration_type\n                      FROM mhr_lien_check_vw lcv\n                    WHERE lcv.mhr_number = r.mhr_number\n                  ORDER BY lcv.base_registration_ts\n                  FETCH FIRST 1 ROWS ONLY) END) AS ppr_lien_type,\n        d.document_type,\n        r.id AS registration_id,\n        (SELECT mrr.doc_storage_url\n            FROM mhr_registration_reports mrr\n          WHERE mrr.registration_id = r.id) AS doc_storage_url,\n        (SELECT l.location_type\n            FROM mhr_locations l, mhr_registrations r2\n          WHERE r2.mhr_number = r.mhr_number\n            AND r2.id = l.registration_id\n            AND l.status_type = 'ACTIVE') AS location_type,\n        d.affirm_by,\n        (SELECT COUNT(mrr.id)\n            FROM mhr_registration_reports mrr\n          WHERE mrr.registration_id = r.id) AS report_count\n    FROM mhr_registrations r, mhr_documents d, mhr_document_types dt\n  WHERE r.id = d.registration_id\n    AND d.document_type = dt.document_type"
    )
    op.drop_entity(public_mhr_account_reg_vw)

    public_mhr_search_serial_vw = PGView(
        schema="public",
        signature="mhr_search_serial_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          s.serial_number,\n          s.compressed_key,\n          d.year_made,\n          d.make, d.model, r.id,\n          (SELECT CASE WHEN p.business_name IS NOT NULL THEN og.status_type || '|' || p.business_name\n                         WHEN p.middle_name IS NOT NULL THEN og.status_type || '|' || p.first_name || '|' || p.middle_name || '|' || p.last_name\n                         ELSE og.status_type || '|' || p.first_name || '|' || p.last_name\n                    END\n               FROM mhr_registrations ro, mhr_owner_groups og, mhr_parties p\n          WHERE ro.mhr_number = r.mhr_number \n               AND ro.id = og.registration_id\n               AND og.registration_id = p.registration_id\n               AND og.status_type IN ('ACTIVE', 'EXEMPT')\n               ORDER BY p.id DESC\n               FETCH FIRST 1 ROWS ONLY) AS owner_info,\n          s.id AS section_id\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d,\n          mhr_registrations rs,\n          mhr_sections s\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'\n     AND rs.mhr_number = r.mhr_number \n     AND rs.id = s.registration_id\n     AND s.status_type = 'ACTIVE'"
    )
    op.drop_entity(public_mhr_search_serial_vw)

    public_mhr_search_owner_ind_vw = PGView(
        schema="public",
        signature="mhr_search_owner_ind_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          (SELECT s.serial_number\n               FROM mhr_registrations rs, mhr_sections s\n          WHERE rs.mhr_number = r.mhr_number \n               AND rs.id = s.registration_id\n               AND s.status_type = 'ACTIVE'\n          ORDER BY s.id\n          FETCH FIRST 1 ROWS ONLY) AS serial_number,\n          d.year_made,\n          d.make, d.model, r.id,\n          p.last_name,\n          p.first_name,\n          p.middle_name,\n          og.status_type AS owner_status_type,\n          p.compressed_name\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_registrations ro,\n          mhr_owner_groups og,\n          mhr_parties p,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND ro.mhr_number = r.mhr_number \n     AND ro.id = og.registration_id\n     AND og.registration_id = p.registration_id\n     AND p.party_type = 'OWNER_IND'\n     AND p.owner_group_id = og.id\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'"
    )
    op.drop_entity(public_mhr_search_owner_ind_vw)

    public_mhr_search_owner_bus_vw = PGView(
        schema="public",
        signature="mhr_search_owner_bus_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          (SELECT s.serial_number\n               FROM mhr_registrations rs, mhr_sections s\n          WHERE rs.mhr_number = r.mhr_number \n               AND rs.id = s.registration_id\n               AND s.status_type = 'ACTIVE'\n          ORDER BY s.id\n          FETCH FIRST 1 ROWS ONLY) AS serial_number,\n          d.year_made,\n          d.make, d.model, r.id,\n          p.business_name,\n          og.status_type AS owner_status_type,\n          p.compressed_name\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_registrations ro,\n          mhr_owner_groups og,\n          mhr_parties p,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND ro.mhr_number = r.mhr_number \n     AND ro.id = og.registration_id\n     AND og.registration_id = p.registration_id\n     AND p.owner_group_id = og.id\n     AND p.party_type = 'OWNER_BUS'\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'"
    )
    op.drop_entity(public_mhr_search_owner_bus_vw)

    public_mhr_search_mhr_number_vw = PGView(
        schema="public",
        signature="mhr_search_mhr_number_vw",
        definition="SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,\n          (SELECT s.serial_number\n               FROM mhr_registrations rs, mhr_sections s\n          WHERE rs.mhr_number = r.mhr_number \n               AND rs.id = s.registration_id\n               AND s.status_type = 'ACTIVE'\n          ORDER BY s.id\n          FETCH FIRST 1 ROWS ONLY) AS serial_number,\n          d.year_made,\n          d.make, d.model, r.id,\n          (SELECT CASE WHEN p.business_name IS NOT NULL THEN og.status_type || '|' || p.business_name\n                         WHEN p.middle_name IS NOT NULL THEN og.status_type || '|' || p.first_name || '|' || p.middle_name || '|' || p.last_name\n                         ELSE og.status_type || '|' || p.first_name || '|' || p.last_name\n                    END\n               FROM mhr_registrations ro, mhr_owner_groups og, mhr_parties p\n          WHERE ro.mhr_number = r.mhr_number \n               AND ro.id = og.registration_id\n               AND og.registration_id = p.registration_id\n               AND og.status_type IN ('ACTIVE', 'EXEMPT')\n               ORDER BY p.id DESC\n               FETCH FIRST 1 ROWS ONLY) AS owner_info\n     FROM mhr_registrations r,\n          mhr_registrations rl,\n          mhr_registrations rd,\n          mhr_locations l, \n          addresses a, \n          mhr_descriptions d\n     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')\n     AND r.mhr_number = rl.mhr_number\n     AND r.mhr_number = rd.mhr_number\n     AND rl.id = l.registration_id\n     AND l.status_type = 'ACTIVE'\n     AND l.address_id = a.id\n     AND rd.id = d.registration_id\n     AND d.status_type = 'ACTIVE'"
    )
    op.drop_entity(public_mhr_search_mhr_number_vw)

    public_mhr_lien_check_vw = PGView(
        schema="public",
        signature="mhr_lien_check_vw",
        definition="SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')\n    AND r.registration_type NOT IN ('SA', 'TA', 'TM')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n  UNION (\n  SELECT sc.mhr_number, r.registration_type || '_TAX', r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl = 'PPSALIEN'\n    AND r.registration_type IN ('SA', 'TA', 'TM')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n    AND EXISTS (SELECT p.id\n                  FROM parties p, client_codes cc\n                  WHERE p.financing_id = fs.id\n                    AND p.party_type = 'SP'\n                    AND p.registration_id_end IS NULL\n                    AND p.branch_id IS NOT NULL\n                    AND p.branch_id = cc.id\n                    AND cc.name like '%TAX DEFERME%')\n  )\n  UNION (\n  SELECT sc.mhr_number, r.registration_type || '_GOV', r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl = 'PPSALIEN'\n    AND r.registration_type IN ('SA', 'TA', 'TM')\n    AND r.registration_ts <= TO_DATE('2004-03-31', 'YYYY-MM-DD')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n    AND EXISTS (SELECT p.id\n                  FROM parties p, client_codes cc\n                  WHERE p.financing_id = fs.id\n                    AND p.party_type = 'SP'\n                    AND p.registration_id_end IS NULL\n                    AND p.branch_id IS NOT NULL\n                    AND p.branch_id = cc.id\n                    AND cc.name like 'HER MAJESTY%')\n  )\n  UNION (\n  SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,\n        r.registration_number AS base_registration_num\n    FROM registrations r, financing_statements fs, serial_collateral sc\n  WHERE r.financing_id = fs.id\n    AND r.registration_type_cl = 'PPSALIEN'\n    AND r.registration_type IN ('SA', 'TA', 'TM')\n    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))\n    AND NOT EXISTS (SELECT r3.id \n                      FROM registrations r3\n                      WHERE r3.financing_id = fs.id\n                        AND r3.registration_type_cl = 'DISCHARGE'\n                        AND r3.registration_ts < (now() at time zone 'utc'))\n    AND sc.financing_id = fs.id\n    AND sc.registration_id_end IS NULL\n    AND sc.mhr_number IS NOT NULL\n    AND sc.mhr_number != 'NR'\n    AND NOT EXISTS (SELECT p.id\n                      FROM parties p, client_codes cc\n                      WHERE p.financing_id = fs.id\n                        AND p.party_type = 'SP'\n                        AND p.registration_id_end IS NULL\n                        AND p.branch_id IS NOT NULL\n                        AND p.branch_id = cc.id\n                        AND (cc.name like 'HER MAJESTY%' OR cc.name like '%TAX DEFERME%'))\n  )"
    )
    op.drop_entity(public_mhr_lien_check_vw)

    public_mhr_serial_compressed_key = PGFunction(
        schema="public",
        signature="mhr_serial_compressed_key(v_serial character varying)",
        definition="RETURNS character varying\n  IMMUTABLE\n  LANGUAGE plpgsql\n  AS\n  $$\n    declare\n    v_key VARCHAR(40);\n    last_pos integer := 6;\n    i integer := 1;\n    begin\n    v_key := upper(v_serial);\n    v_key := REGEXP_REPLACE(v_key, '[^0-9A-Za-z]','','gi');\n    v_key := '000000' || v_key;\n    for i in 1 .. LENGTH(v_key)\n    loop\n        if POSITION(substring(v_key, i, 1) in '0123456789') > 0 then\n        last_pos := i;\n        end if;\n    end loop;\n    v_key := replace(v_key, 'B', '8');\n    v_key := replace(v_key, 'C', '6');\n    v_key := replace(v_key, 'G', '6');\n    v_key := replace(v_key, 'H', '4');\n    v_key := replace(v_key, 'I', '1');\n    v_key := replace(v_key, 'L', '1');\n    v_key := replace(v_key, 'S', '5');\n    v_key := replace(v_key, 'Y', '4');\n    v_key := replace(v_key, 'Z', '2');\n    v_key := REGEXP_REPLACE(v_key, '[^0-9]','0','gi');\n    v_key := substring(v_key, last_pos - 5, 6);\n    return v_key;\n    end;\n  $$"
    )
    op.drop_entity(public_mhr_serial_compressed_key)

    public_mhr_name_compressed_key = PGFunction(
        schema="public",
        signature="mhr_name_compressed_key(v_name character varying)",
        definition="RETURNS character varying\n  IMMUTABLE\n  LANGUAGE plpgsql\n  AS\n  $$\n    declare\n    v_key VARCHAR(250);\n    begin\n    v_key := upper(v_name);\n    if position(left(v_key, 1) in '&#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') < 1 then\n        v_key := substring(v_key, 2);\n    end if;\n    if left(v_key, 4) = 'THE ' then\n        v_key := substring(v_key, 5);\n    end if;\n    v_key := regexp_replace(v_key, '[^0-9A-Z&#]+', '', 'gi');\n    if left(v_key, 15) = 'BRITISHCOLUMBIA' then\n        v_key := 'BC' || substring(v_key, 16);\n    end if;\n    v_key := replace(v_key, '#', 'NUMBER');\n    v_key := replace(v_key, '&', 'AND');\n    v_key := replace(v_key, '0', 'ZERO');\n    v_key := replace(v_key, '1', 'ONE');\n    v_key := replace(v_key, '2', 'TWO');\n    v_key := replace(v_key, '3', 'THREE');\n    v_key := replace(v_key, '4', 'FOUR');\n    v_key := replace(v_key, '5', 'FIVE');\n    v_key := replace(v_key, '6', 'SIX');\n    v_key := replace(v_key, '7', 'SEVEN');\n    v_key := replace(v_key, '8', 'EIGHT');\n    v_key := replace(v_key, '9', 'NINE');\n    if length(v_key) > 30 then\n        v_key := substring(v_key, 1, 30);\n    end if;\n    return v_key;\n    end;\n  $$"
    )
    op.drop_entity(public_mhr_name_compressed_key)

    public_get_mhr_doc_gov_agent_id = PGFunction(
        schema="public",
        signature="get_mhr_doc_gov_agent_id()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_id_gov_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_mhr_doc_gov_agent_id)

    public_get_mhr_doc_qualified_id = PGFunction(
        schema="public",
        signature="get_mhr_doc_qualified_id()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_id_qualified_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_mhr_doc_qualified_id)

    public_get_mhr_doc_manufacturer_id = PGFunction(
        schema="public",
        signature="get_mhr_doc_manufacturer_id()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_id_manufacturer_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_mhr_doc_manufacturer_id)

    public_get_mhr_doc_reg_number = PGFunction(
        schema="public",
        signature="get_mhr_doc_reg_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_doc_reg_seq'), '00000000'));\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_mhr_doc_reg_number)

    public_get_mhr_number = PGFunction(
        schema="public",
        signature="get_mhr_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_number_seq'), '000000'));\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_mhr_number)

    public_get_mhr_draft_number = PGFunction(
        schema="public",
        signature="get_mhr_draft_number()",
        definition="RETURNS VARCHAR\n  LANGUAGE plpgsql\n  AS\n  $$\n    BEGIN\n        RETURN trim(to_char(nextval('mhr_draft_number_seq'), '000000'));\n    END\n  ; \n  $$"
    )
    op.drop_entity(public_get_mhr_draft_number)

    with op.batch_alter_table('mhr_manufacturers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_manufacturers_registration_id'))
    op.drop_table('mhr_manufacturers')
    with op.batch_alter_table('mhr_sections', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_sections_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_sections_compressed_key'))
        batch_op.drop_index(batch_op.f('ix_mhr_sections_change_registration_id'))
    op.drop_table('mhr_sections')
    with op.batch_alter_table('mhr_registration_reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_registration_reports_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_registration_reports_create_ts'))
    op.drop_table('mhr_registration_reports')
    with op.batch_alter_table('mhr_qualified_suppliers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_qualified_suppliers_address_id'))
    op.drop_table('mhr_qualified_suppliers')
    with op.batch_alter_table('mhr_owner_groups', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_owner_groups_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_owner_groups_change_registration_id'))
    op.drop_table('mhr_owner_groups')
    with op.batch_alter_table('mhr_locations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_locations_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_locations_exception_plan'))
        batch_op.drop_index(batch_op.f('ix_mhr_locations_change_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_locations_address_id'))
    op.drop_table('mhr_locations')
    with op.batch_alter_table('mhr_documents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_documents_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_documents_document_registration_number'))
        batch_op.drop_index(batch_op.f('ix_mhr_documents_document_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_documents_change_registration_id'))
    op.drop_table('mhr_documents')
    with op.batch_alter_table('mhr_descriptions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_descriptions_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_descriptions_change_registration_id'))
    op.drop_table('mhr_descriptions')
    with op.batch_alter_table('mhr_registration_reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_registration_reports_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_registration_reports_create_ts'))
    op.drop_table('mhr_registration_reports')
    with op.batch_alter_table('mhr_qualified_suppliers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_qualified_suppliers_address_id'))
    op.drop_table('mhr_qualified_suppliers')
    with op.batch_alter_table('mhr_owner_groups', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_owner_groups_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_owner_groups_change_registration_id'))
    op.drop_table('mhr_owner_groups')
    with op.batch_alter_table('mhr_locations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_locations_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_locations_exception_plan'))
        batch_op.drop_index(batch_op.f('ix_mhr_locations_change_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_locations_address_id'))
    op.drop_table('mhr_locations')
    with op.batch_alter_table('mhr_documents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_documents_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_documents_document_registration_number'))
        batch_op.drop_index(batch_op.f('ix_mhr_documents_document_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_documents_change_registration_id'))
    op.drop_table('mhr_documents')
    with op.batch_alter_table('mhr_descriptions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_descriptions_registration_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_descriptions_change_registration_id'))
    op.drop_table('mhr_descriptions')
    with op.batch_alter_table('mhr_registrations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_registrations_registration_ts'))
        batch_op.drop_index(batch_op.f('ix_mhr_registrations_mhr_number'))
        batch_op.drop_index(batch_op.f('ix_mhr_registrations_draft_id'))
        batch_op.drop_index(batch_op.f('ix_mhr_registrations_account_id'))
    op.drop_table('mhr_registrations')
    with op.batch_alter_table('mhr_drafts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_drafts_create_ts'))
        batch_op.drop_index(batch_op.f('ix_mhr_drafts_account_id'))
    op.drop_table('mhr_drafts')
    op.drop_table('mhr_tenancy_types')
    op.drop_table('mhr_status_types')
    op.drop_table('mhr_service_agreements')
    op.drop_table('mhr_registration_types')
    op.drop_table('mhr_registration_status_types')
    op.drop_table('mhr_party_types')
    op.drop_table('mhr_owner_status_types')
    op.drop_table('mhr_note_status_types')
    op.drop_table('mhr_location_types')
    with op.batch_alter_table('mhr_extra_registrations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mhr_extra_registrations_mhr_number'))
        batch_op.drop_index(batch_op.f('ix_mhr_extra_registrations_account_id'))
    op.drop_table('mhr_extra_registrations')
    op.drop_table('mhr_document_types')
    # Manually added drop sequence commands ###
    op.execute(DropSequence(Sequence('mhr_number_seq')))
    op.execute(DropSequence(Sequence('mhr_draft_number_seq')))
    op.execute(DropSequence(Sequence('mhr_doc_reg_seq')))
    op.execute(DropSequence(Sequence('mhr_doc_id_manufacturer_seq')))
    op.execute(DropSequence(Sequence('mhr_doc_id_gov_seq')))
    op.execute(DropSequence(Sequence('mhr_doc_id_qualified_seq')))
    op.execute(DropSequence(Sequence('mhr_extra_registration_seq')))
    op.execute(DropSequence(Sequence('mhr_draft_id_seq')))
    op.execute(DropSequence(Sequence('mhr_registration_id_seq')))
    op.execute(DropSequence(Sequence('mhr_owner_group_id_seq')))
    op.execute(DropSequence(Sequence('mhr_party_id_seq')))
    op.execute(DropSequence(Sequence('mhr_registration_report_id_seq')))
    op.execute(DropSequence(Sequence('mhr_location_id_seq')))
    op.execute(DropSequence(Sequence('mhr_document_id_seq')))
    op.execute(DropSequence(Sequence('mhr_note_id_seq')))
    op.execute(DropSequence(Sequence('mhr_description_id_seq')))
    op.execute(DropSequence(Sequence('mhr_section_id_seq')))
    op.execute(DropSequence(Sequence('mhr_manufacturer_id_seq')))
    op.execute(DropSequence(Sequence('mhr_supplier_id_seq')))
    op.execute(DropSequence(Sequence('mhr_agreements_id_seq')))
    # ### end Alembic commands ###
