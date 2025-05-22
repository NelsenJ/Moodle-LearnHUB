"""empty message

Revision ID: b484ac1b5cc0
Revises: 1c9acc97afe8, remove_image_url
Create Date: 2025-05-21 19:35:57.661519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b484ac1b5cc0'
down_revision = ('1c9acc97afe8', 'remove_image_url')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
