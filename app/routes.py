from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Game, Review  
from app.games import get_games_list, get_game_details
# Define a blueprint for routes
routes = Blueprint('routes', __name__)

# Home route
@routes.route('/')
@routes.route('/home')
def home():
    return render_template('home.html')

# Registration route
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Create new user object and password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)

        # Adding user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user in after the registration
        login_user(new_user)

        flash('Registration successful!', 'success')
        return redirect(url_for('routes.profile'))  # Redirect to profile page after successful registration

    return render_template('register.html')

# Login route
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('routes.profile'))  # Redirect to profile page after successful login

        flash('Login failed. Check your credentials and try again.', 'danger')

    return render_template('login.html')

# Logout route
@routes.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.home'))

# Profile route (can only be accessible by logged-in users)
@routes.route('/profile')
@login_required
def profile():
    # Get all reviews by the current user goes by the newest to oldest
    user_reviews = Review.query.filter_by(user_id=current_user.id)\
        .order_by(Review.created_at.desc()).all()
    
    # Get the game details for each review
    reviews_with_games = []
    for review in user_reviews:
        game = Game.query.get(review.game_id)
        if game:
            reviews_with_games.append({
                'review': review,
                'game': game
            })
    
    return render_template('profile.html', 
                         user=current_user,
                         reviews=reviews_with_games)

@routes.route('/game/<int:game_id>')
def game_detail(game_id):
    game_data = get_game_details(game_id)
    if not game_data:
        flash('Game not found.', 'danger')
        return redirect(url_for('routes.games'))
    
    # Get the game from our database
    game_record = Game.query.filter_by(rawg_id=game_id).first()
    
    user_rating = None
    average_rating = None
    total_ratings = 0
    reviews = []
    
    if game_record:
        # Get all reviews for this game
        reviews = Review.query.filter_by(game_id=game_record.id)\
            .order_by(Review.created_at.desc()).all()
        total_ratings = len(reviews)
        
        if total_ratings > 0:
            # Calculate average rating
            average_rating = sum(r.rating for r in reviews) / total_ratings
        
        # Get user's rating
        if current_user.is_authenticated:
            user_rating = Review.query.filter_by(
                user_id=current_user.id,
                game_id=game_record.id
            ).first()
    
    return render_template('game_detail.html', 
                         game=game_data,
                         user_rating=user_rating,
                         average_rating=average_rating,
                         total_ratings=total_ratings,
                         reviews=reviews)

@routes.route('/game/<int:game_id>/rate', methods=['POST'])
@login_required
def rate_game(game_id):
    rating_value = request.form.get('rating')
    review_text = request.form.get('review_text')

    if not rating_value:
        flash('Please select a rating.', 'danger')
        return redirect(url_for('routes.game_detail', game_id=game_id))
    
    # Convert rating to integer
    rating_value = int(rating_value)
    if not 1 <= rating_value <= 5:
        flash('Invalid rating value.', 'danger')
        return redirect(url_for('routes.game_detail', game_id=game_id))
    
    # Check if game exists in our database
    game = Game.query.filter_by(rawg_id=game_id).first()
    if not game:
       
        game_data = get_game_details(game_id)
        if not game_data:
            flash('Game not found.', 'danger')
            return redirect(url_for('routes.games'))
        
        game = Game(
            rawg_id=game_id,
            title=game_data['name'],
            description=game_data.get('description_raw', ''),
            image_url=game_data.get('background_image', ''),
            release_date=game_data.get('released', '')
        )
        db.session.add(game)
        db.session.commit()
    
    # Check if user has already rated this game
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        game_id=game.id
    ).first()
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating_value
        existing_review.comment = review_text
        flash('Your review has been updated!', 'success')
    else:
        # Create new review
        new_review = Review(
            user_id=current_user.id,
            game_id=game.id,
            rating=rating_value,
            comment=review_text
        )
        db.session.add(new_review)
        flash('Your review has been saved!', 'success')
    
    db.session.commit()
    return redirect(url_for('routes.game_detail', game_id=game_id))

@routes.route('/games')
def games():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    games_data = get_games_list(page=page, search_query=search_query)
    
    if games_data:
        return render_template('games.html', 
                             games=games_data['results'],
                             next_page=games_data['next'] is not None,
                             prev_page=games_data['previous'] is not None,
                             current_page=page,
                             search_query=search_query)
    
    flash('Unable to load games at this time.', 'danger')
    return render_template('games.html', games=[])