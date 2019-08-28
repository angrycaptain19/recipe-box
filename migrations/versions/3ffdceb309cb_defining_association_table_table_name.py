"""defining association table table name

Revision ID: 3ffdceb309cb
Revises: cb64ba9f42a4
Create Date: 2019-08-28 15:13:46.257664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ffdceb309cb'
down_revision = 'cb64ba9f42a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe-ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=True),
    sa.Column('ingredient_id', sa.Integer(), nullable=True),
    sa.Column('ingredientAmount', sa.Float(), nullable=True),
    sa.Column('ingredientUnit', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('recipe_ingredients')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe_ingredients',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('recipe_id', sa.INTEGER(), nullable=True),
    sa.Column('ingredient_id', sa.INTEGER(), nullable=True),
    sa.Column('ingredientAmount', sa.FLOAT(), nullable=True),
    sa.Column('ingredientUnit', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('recipe-ingredients')
    # ### end Alembic commands ###
