"""add SpectralWorkflow.pluginVersion (A3 provenance)

Revision ID: f0ac79b33dde
Revises: 7200faf1d770
Create Date: 2026-07-19 18:14:05.654818
"""
from alembic import op
import sqlalchemy as sa


revision = 'f0ac79b33dde'
down_revision = '7200faf1d770'
branch_labels = None
depends_on = None


# A3 provenance (SPEC_plugin_distribution.md §8, F-a3-3). Autogenerate's body was DISCARDED: Alembic's
# target_metadata (via AllEntities) does not import the SpectralWorkflow graph — that graph lives under
# model.spectral (registered on DbBaseEntity.metadata only at app runtime), so autogenerate wrongly saw the
# workflow tables as "in DB, not in model" and proposed dropping them. The real, intended change is a single
# column. Hand-written to that. (Both DatabaseInitializer paths are covered: case 1 fresh installs build the
# column via create_all + stamp head and never run this; case 2 existing DBs upgrade head and run it.)
def upgrade():
    with op.batch_alter_table('spectral_workflow', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pluginVersion', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('spectral_workflow', schema=None) as batch_op:
        batch_op.drop_column('pluginVersion')
