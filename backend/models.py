from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    role = db.Column(db.Enum('admin', 'sponsor', 'influencer'), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    flagged = db.Column(db.Boolean, default=False)


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = relationship('User', backref=db.backref('admin', uselist=False))

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100))
    budget = db.Column(db.Float)
    user = relationship('User', backref=db.backref('sponsor', uselist=False))
    campaigns = relationship('Campaign', back_populates='sponsor')

class Influencer(db.Model):
    __tablename__ = 'influencers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    niche = db.Column(db.String(100))
    reach = db.Column(db.Integer)
    user = relationship('User', backref=db.backref('influencer', uselist=False))
    ad_requests = relationship('AdRequest', back_populates='influencer')


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.Enum('public', 'private'), nullable=False)
    goals = db.Column(db.Text)
    sponsor = relationship('Sponsor', back_populates='campaigns')
    ad_requests = relationship('AdRequest', back_populates='campaign')


class AdRequest(db.Model):
    __tablename__ = 'ad_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.id'), nullable=False)
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', 'negotiating','requested'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaign = relationship('Campaign', back_populates='ad_requests')
    influencer = relationship('Influencer', back_populates='ad_requests')
    proposed_amount = db.Column(db.Float)  
    last_updated_by = db.Column(db.Enum('sponsor', 'influencer'))  


