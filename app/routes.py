from app import db
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Tweet
from app.forms import LoginForm, RegistrationForm, UpdateProfileForm, TweetForm
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/') 
@login_required
def home():
    """
    Home page route.

    Returns:
        Rendered home page template.
    """
    tweets = current_user.followed_tweets()
    form = TweetForm()
    return render_template('home.html', tweets=tweets, form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register page route.
    
    Returns:
        Rendered register page template.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page route.

    Returns:
        Rendered login page template.
    """
    
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('User not found.')
            return redirect(url_for('main.login'))
        if user.check_password(form.password.data) is False:
            flash('Wrong password.')
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.home'))
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    """
    Logout route.
    
    Returns:
        Redirect to home page.
    """
    logout_user()
    return redirect(url_for('main.home'))


@main.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """
    Delete account route.

    Returns:
        Redirect to home page.
    """
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.')
        return redirect(url_for('main.home'))
    return render_template('delete_account.html')

@main.route('/user/<username>')
@login_required
def profile(username):
    """
    Profile page route.

    Args:
        username: User's username.

    Returns:
        Rendered profile page template.
    """
    user = User.query.filter_by(username=username).first_or_404()
    tweets = user.tweets.order_by(Tweet.timestamp.desc())
    return render_template('profile.html', user=user, tweets=tweets)

@main.route('/user/<username>/update', methods=['GET', 'POST'])
@login_required
def update_profile(username):
    """
    Update profile page route.

    Args:
        username: User's username.

    Returns:
        Rendered update profile page template.
    """
    user = User.query.filter_by(username=username).first_or_404()
    form = UpdateProfileForm(
        original_username=user.username,
    )
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.profile', username=user.username))
    elif request.method == 'GET':
        form.username.data = user.username
        form.about_me.data = user.about_me
    return render_template('update_profile.html', form=form)

@main.route('/tweet', methods=['GET', 'POST'])
@login_required
def tweet():
    """
    Tweet page route.

    Returns:
        Rendered tweet page template.
    """
    form = TweetForm()
    if form.validate_on_submit():
        tweet = Tweet(body=form.content.data, author=current_user)
        db.session.add(tweet)
        db.session.commit()
        flash('Your tweet is now live!')
        return redirect(url_for('main.home'))
    return render_template('tweet.html', form=form)


@main.route('/tweet/<tweet_id>', methods=['GET', 'POST'])
@login_required
def tweet_detail(tweet_id):
    """
    Tweet detail page route.

    Args:
        tweet_id: Tweet's id.

    Returns:
        Rendered tweet detail page template.
    """
    tweet = Tweet.query.get(tweet_id)
    if tweet is None:
        return redirect(url_for('main.home'))
    return render_template('tweet.html', tweet=tweet)


@main.route('/tweet/<tweet_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_tweet(tweet_id):
    """
    Delete tweet route.

    Args:
        tweet_id: Tweet's id.

    Returns:
        Redirect to previous page.
    """
    before_page = request.referrer
    tweet = Tweet.query.get(tweet_id)
    if tweet is None:
        return redirect(url_for('main.home'))
    if tweet.author != current_user:
        flash('You cannot delete this tweet.')
        return redirect(url_for('main.home'))
    db.session.delete(tweet)
    db.session.commit()
    flash('Your tweet has been deleted.')

    return redirect(before_page)



@main.route('/like/<tweet_id>', methods=['POST'])
@login_required
def like(tweet_id):
    """
    Like tweet route.

    Args:
        tweet_id: Tweet's id.

    Returns:
        Redirect to previous page.
    """
    before_page = request.referrer
    tweet = Tweet.query.get(tweet_id)
    if tweet is None:
        flash('Tweet not found.')
        return redirect(url_for('main.home'))
    if tweet.is_liked_by(current_user):
        current_user.unlike_tweet(tweet)
    else:
        current_user.like_tweet(tweet)
    db.session.commit()

    return redirect(before_page)


@main.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """
    Follow user route.

    Args:
        username: User's username.

    Returns:
        Redirect to previous page.
    """
    before_page = request.referrer
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(before_page)
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(before_page)
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username))
    return redirect(before_page)


@main.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """
    Unfollow user route.

    Args:
        username: User's username.

    Returns:
        Redirect to previous page.
    """
    before_page = request.referrer
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(before_page)
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(before_page)
    current_user.unfollow(user)
    db.session.commit()
    flash('You have unfollowed {}.'.format(username))
    return redirect(before_page)


@main.route('/search')
@login_required
def search():
    """
    Search page route.

    q: Search term.

    Returns:
        Rendered search page template.
    """
    q = request.args.get('q')

    if q == '':
        flash('Please enter a search term.')
        return redirect(url_for('main.home'))
    
    lower_username = func.lower(User.username)
    filter_users = lower_username.ilike('%{}%'.format(q.lower()))
    users = User.query.filter(filter_users).all()

    lower_body = func.lower(Tweet.body)
    filter_tweets = lower_body.ilike('%{}%'.format(q.lower()))
    tweets = Tweet.query.filter(filter_tweets).all()

    return render_template('search.html', q=q,users=users, tweets=tweets)


# 404 error handler
@main.app_errorhandler(404)
def page_not_found(e):
    """
    404 error handler.

    Args:
        e: Error.

    Returns:
        Rendered 404 page template.
    """
    return render_template('404.html'), 404

    # 500 error handler
@main.app_errorhandler(500)
def internal_error(e):
    """
    500 error handler.

    Args:
        e: Error.

    Returns:
        Rendered 500 page template.
    """
    return render_template('500.html'), 500