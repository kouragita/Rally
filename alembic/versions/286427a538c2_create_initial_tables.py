"""Create initial tables

Revision ID: 286427a538c2
Revises: 
Create Date: 2025-08-30 01:09:54.902747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '286427a538c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('ecosystems',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('aquatic', 'terrestrial', name='ecosystem_type_enum'), nullable=False),
    sa.Column('subtype', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ecosystems_id'), 'ecosystems', ['id'], unique=False)
    op.create_index(op.f('ix_ecosystems_name'), 'ecosystems', ['name'], unique=False)
    
    op.create_table('species',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scientific_name', sa.String(), nullable=False),
    sa.Column('common_name', sa.String(), nullable=True),
    sa.Column('conservation_status', sa.String(), nullable=True),
    sa.Column('ecosystem_dependencies', sa.JSON(), nullable=True),
    sa.Column('climate_sensitivity', sa.Numeric(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_species_id'), 'species', ['id'], unique=False)
    op.create_index(op.f('ix_species_scientific_name'), 'species', ['scientific_name'], unique=True)
    
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('report_type', sa.String(), nullable=True),
    sa.Column('query_parameters', sa.JSON(), nullable=True),
    sa.Column('analysis_results', sa.JSON(), nullable=True),
    sa.Column('predictions', sa.JSON(), nullable=True),
    sa.Column('citations', sa.JSON(), nullable=True),
    sa.Column('confidence_scores', sa.JSON(), nullable=True),
    sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('ai_model_version', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    
    op.create_table('climate_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ecosystem_id', sa.Integer(), nullable=True),
    sa.Column('data_source', sa.String(), nullable=True),
    sa.Column('measurement_type', sa.String(), nullable=True),
    sa.Column('value', sa.Numeric(), nullable=True),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('date_recorded', sa.Date(), nullable=True),
    sa.Column('location_lat', sa.Numeric(), nullable=True),
    sa.Column('location_lon', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['ecosystem_id'], ['ecosystems.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_climate_data_id'), 'climate_data', ['id'], unique=False)
    
    op.create_table('wildlife_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('species_id', sa.Integer(), nullable=True),
    sa.Column('ecosystem_id', sa.Integer(), nullable=True),
    sa.Column('population_count', sa.Integer(), nullable=True),
    sa.Column('habitat_quality_score', sa.Numeric(), nullable=True),
    sa.Column('migration_pattern', sa.JSON(), nullable=True),
    sa.Column('date_recorded', sa.Date(), nullable=True),
    sa.Column('location_lat', sa.Numeric(), nullable=True),
    sa.Column('location_lon', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['ecosystem_id'], ['ecosystems.id'], ),
    sa.ForeignKeyConstraint(['species_id'], ['species.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wildlife_data_id'), 'wildlife_data', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_wildlife_data_id'), table_name='wildlife_data')
    op.drop_table('wildlife_data')
    op.drop_index(op.f('ix_climate_data_id'), table_name='climate_data')
    op.drop_table('climate_data')
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_table('reports')
    op.drop_index(op.f('ix_species_scientific_name'), table_name='species')
    op.drop_index(op.f('ix_species_id'), table_name='species')
    op.drop_table('species')
    op.drop_index(op.f('ix_ecosystems_name'), table_name='ecosystems')
    op.drop_index(op.f('ix_ecosystems_id'), table_name='ecosystems')
    op.drop_table('ecosystems')