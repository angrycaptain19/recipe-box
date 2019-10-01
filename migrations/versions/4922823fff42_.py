"""empty message

Revision ID: 4922823fff42
Revises: fc8e6c312659
Create Date: 2019-09-28 18:52:27.831798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4922823fff42'
down_revision = 'fc8e6c312659'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe2',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipeURL', sa.String(), nullable=True),
    sa.Column('recipeName', sa.String(length=128), nullable=True),
    sa.Column('ratingCount', sa.Integer(), nullable=True),
    sa.Column('ratingValue', sa.Float(), nullable=True),
    sa.Column('image_url', sa.String(length=256), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('keywords', sa.String(), nullable=True),
    sa.Column('recipeCategory', sa.String(), nullable=True),
    sa.Column('recipeCuisine', sa.String(), nullable=True),
    sa.Column('recipeYield', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recipe2_recipeName'), 'recipe2', ['recipeName'], unique=False)
    op.create_index(op.f('ix_recipe2_recipeURL'), 'recipe2', ['recipeURL'], unique=False)
    op.create_index(op.f('ix_recipe2_timestamp'), 'recipe2', ['timestamp'], unique=False)
    op.create_table('recipeIngredients2',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe2_id', sa.Integer(), nullable=True),
    sa.Column('ingredient', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['recipe2_id'], ['recipe2.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipe__steps2',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.Column('directions', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe2.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe__steps2')
    op.drop_table('recipeIngredients2')
    op.drop_index(op.f('ix_recipe2_timestamp'), table_name='recipe2')
    op.drop_index(op.f('ix_recipe2_recipeURL'), table_name='recipe2')
    op.drop_index(op.f('ix_recipe2_recipeName'), table_name='recipe2')
    op.drop_table('recipe2')
    # ### end Alembic commands ###