from database import db
from datetime import date, datetime
from flask_login import UserMixin

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Boolean, default='User')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def formatted_date(self):
        return self.date_posted.strftime("%B %Y")

    def formatted_date_with_day(self):
        return self.date_posted.strftime("%d %B %Y")

    def formatted_time(self):
        return self.date_posted.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_posted
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=True)
    last_name = db.Column(db.String(), nullable=True)
    middle_name = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    password_hash = db.Column(db.String())

    # Foreignkey Integration
    roles = db.relationship('Roles', backref='poster', lazy=True, cascade='all, delete-orphan')

    def formatted_date(self):
        return self.date_added.strftime("%B %Y")

    def formatted_date_with_day(self):
        return self.date_added.strftime("%d %B %Y")

    def formatted_time(self):
        return self.date_added.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_added
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"
    
    @property
    def password(self):
        raise AttributeError(' Password Not A Readable Attribute !!! ')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(self):
        return '<Name %r>' % self.name
