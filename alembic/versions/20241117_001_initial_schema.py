"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-11-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create genres table
    op.create_table(
        'genres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_genres_id'), 'genres', ['id'], unique=False)
    op.create_index(op.f('ix_genres_slug'), 'genres', ['slug'], unique=True)

    # Create movies table
    op.create_table(
        'movies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('poster_url', sa.String(length=500), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movies_id'), 'movies', ['id'], unique=False)
    op.create_index(op.f('ix_movies_title'), 'movies', ['title'], unique=False)

    # Create movie_genres junction table
    op.create_table(
        'movie_genres',
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('genre_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('movie_id', 'genre_id')
    )

    # Create showtimes table
    op.create_table(
        'showtimes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('movie_id', sa.Integer(), nullable=False),
        sa.Column('screen_name', sa.String(length=100), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_seats', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_showtimes_id'), 'showtimes', ['id'], unique=False)
    op.create_index(op.f('ix_showtimes_movie_id'), 'showtimes', ['movie_id'], unique=False)
    op.create_index(op.f('ix_showtimes_start_time'), 'showtimes', ['start_time'], unique=False)

    # Create seats table
    op.create_table(
        'seats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('showtime_id', sa.Integer(), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('row_letter', sa.String(length=2), nullable=False),
        sa.Column('is_reserved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['showtime_id'], ['showtimes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seats_id'), 'seats', ['id'], unique=False)
    op.create_index(op.f('ix_seats_showtime_id'), 'seats', ['showtime_id'], unique=False)
    op.create_index(op.f('ix_seats_is_reserved'), 'seats', ['is_reserved'], unique=False)

    # Create reservations table
    op.create_table(
        'reservations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('showtime_id', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.Enum('confirmed', 'cancelled', name='reservationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['showtime_id'], ['showtimes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reservations_id'), 'reservations', ['id'], unique=False)
    op.create_index(op.f('ix_reservations_user_id'), 'reservations', ['user_id'], unique=False)
    op.create_index(op.f('ix_reservations_showtime_id'), 'reservations', ['showtime_id'], unique=False)
    op.create_index(op.f('ix_reservations_status'), 'reservations', ['status'], unique=False)

    # Create reservation_seats junction table
    op.create_table(
        'reservation_seats',
        sa.Column('reservation_id', sa.Integer(), nullable=False),
        sa.Column('seat_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['reservation_id'], ['reservations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seat_id'], ['seats.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('reservation_id', 'seat_id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('reservation_seats')
    op.drop_index(op.f('ix_reservations_status'), table_name='reservations')
    op.drop_index(op.f('ix_reservations_showtime_id'), table_name='reservations')
    op.drop_index(op.f('ix_reservations_user_id'), table_name='reservations')
    op.drop_index(op.f('ix_reservations_id'), table_name='reservations')
    op.drop_table('reservations')
    
    op.drop_index(op.f('ix_seats_is_reserved'), table_name='seats')
    op.drop_index(op.f('ix_seats_showtime_id'), table_name='seats')
    op.drop_index(op.f('ix_seats_id'), table_name='seats')
    op.drop_table('seats')
    
    op.drop_index(op.f('ix_showtimes_start_time'), table_name='showtimes')
    op.drop_index(op.f('ix_showtimes_movie_id'), table_name='showtimes')
    op.drop_index(op.f('ix_showtimes_id'), table_name='showtimes')
    op.drop_table('showtimes')
    
    op.drop_table('movie_genres')
    
    op.drop_index(op.f('ix_movies_title'), table_name='movies')
    op.drop_index(op.f('ix_movies_id'), table_name='movies')
    op.drop_table('movies')
    
    op.drop_index(op.f('ix_genres_slug'), table_name='genres')
    op.drop_index(op.f('ix_genres_id'), table_name='genres')
    op.drop_table('genres')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='reservationstatus').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())



