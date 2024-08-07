from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import *
from flask import current_app as app
from datetime import timedelta
from sqlalchemy.sql import func

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register/influencer", methods=["GET", "POST"])
def influencer_registration():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        category = request.form.get("category")
        niche = request.form.get("niche")
        reach = request.form.get("reach")

        existing_user = User.query.filter_by(username=username).first()
        existing_mail = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("influencer_registration"))
        if existing_mail:
            flash("Email already exists. Please try to sign in instead.")
            return redirect(url_for("influencer_registration"))

        new_user = User(username=username, email=email, role="influencer", password=password)
        db.session.add(new_user)
        db.session.commit()
        new_influencer = Influencer(user_id=new_user.id, name=name, category=category, niche=niche, reach=reach)
        db.session.add(new_influencer)
        db.session.commit()

        flash("Influencer registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register_influencer.html")

@app.route("/register/sponsor", methods=["GET", "POST"])
def sponsor_registration():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        industry = request.form.get("industry")
        budget = request.form.get("budget")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("sponsor_registration"))

        new_user = User(username=username, email=email, role="sponsor", password=password)
        db.session.add(new_user)
        db.session.commit()
        new_sponsor = Sponsor(user_id=new_user.id, company_name=company_name, industry=industry, budget=budget)
        db.session.add(new_sponsor)
        db.session.commit()

        flash("Sponsor registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register_sponsor.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            if user.flagged:
                flash("Your account has been flagged. Please contact support.")
                return redirect(url_for("login"))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome, {user.username}!")
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "sponsor":
                return redirect(url_for("sponsor_dashboard"))
            elif user.role == "influencer":
                return redirect(url_for("influencer_dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("home"))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied.")
        return redirect(url_for("home"))
    
    users = User.query.all()
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    
    active_users = User.query.filter(User.last_login > (datetime.utcnow() - timedelta(days=30))).count()
    public_campaigns = Campaign.query.filter_by(visibility="public").count()
    private_campaigns = Campaign.query.filter_by(visibility="private").count()
    pending_ad_requests = AdRequest.query.filter_by(status="pending").count()
    flagged_users = User.query.filter_by(flagged=True).count()
    
    total_sponsors = Sponsor.query.count()
    total_influencers = Influencer.query.count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequest.query.count()
    
    avg_campaign_budget = db.session.query(func.avg(Campaign.budget)).scalar()
    avg_campaign_budget = round(avg_campaign_budget, 2) if avg_campaign_budget else 0
    
    avg_influencer_reach = db.session.query(func.avg(Influencer.reach)).scalar()
    avg_influencer_reach = int(avg_influencer_reach) if avg_influencer_reach else 0
    
    campaign_success_rate = (AdRequest.query.filter_by(status="accepted").count() / total_ad_requests) * 100 if total_ad_requests > 0 else 0
    campaign_success_rate = round(campaign_success_rate, 2)

    return render_template(
        "admin_dashboard.html",
        users=users,
        campaigns=campaigns,
        ad_requests=ad_requests,
        active_users=active_users,
        public_campaigns=public_campaigns,
        private_campaigns=private_campaigns,
        pending_ad_requests=pending_ad_requests,
        flagged_users=flagged_users,
        total_sponsors=total_sponsors,
        total_influencers=total_influencers,
        total_campaigns=total_campaigns,
        total_ad_requests=total_ad_requests,
        avg_campaign_budget=avg_campaign_budget,
        avg_influencer_reach=avg_influencer_reach,
        campaign_success_rate=campaign_success_rate
    )

@app.route("/flag_user/<int:user_id>", methods=["POST"])
@login_required
def flag_user(user_id):
    if current_user.role != "admin":
        flash("Access denied.")
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    user.flagged = not user.flagged
    db.session.commit()
    
    flash(f"User {user.username} has been {'flagged' if user.flagged else 'unflagged'}.")
    return redirect(url_for('admin_dashboard') + '#users')

@app.route("/sponsor/dashboard")
@login_required
def sponsor_dashboard():
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))
    
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    campaign_ids = [campaign.id for campaign in campaigns]
    ad_requests = AdRequest.query.filter(AdRequest.campaign_id.in_(campaign_ids)).all()
    requested_ads = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id, AdRequest.status == 'requested').all()

    return render_template("sponsor_dashboard.html", sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests,requested_ads=requested_ads)

@app.route("/sponsor/create_campaign", methods=["GET", "POST"])
@login_required
def create_campaign():
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        budget = float(request.form.get("budget"))
        visibility = request.form.get("visibility")
        goals = request.form.get("goals")

        sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
        new_campaign = Campaign(sponsor_id=sponsor.id, name=name, description=description,
                                start_date=start_date, end_date=end_date, budget=budget,
                                visibility=visibility, goals=goals)
        db.session.add(new_campaign)
        db.session.commit()

        flash("Campaign created successfully.")
        return redirect(url_for("sponsor_dashboard"))

    return render_template("create_campaign.html")

@app.route("/sponsor/edit_campaign/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def edit_campaign(campaign_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != Sponsor.query.filter_by(user_id=current_user.id).first().id:
        flash("Access denied.")
        return redirect(url_for("sponsor_dashboard"))

    if request.method == "POST":
        campaign.name = request.form.get("name")
        campaign.description = request.form.get("description")
        campaign.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        campaign.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        campaign.budget = float(request.form.get("budget"))
        campaign.visibility = request.form.get("visibility")
        campaign.goals = request.form.get("goals")

        db.session.commit()
        flash("Campaign updated successfully.")
        return redirect(url_for("sponsor_dashboard"))

    return render_template("edit_campaign.html", campaign=campaign)

@app.route("/sponsor/delete_campaign/<int:campaign_id>", methods=["POST"])
@login_required
def delete_campaign(campaign_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != Sponsor.query.filter_by(user_id=current_user.id).first().id:
        flash("Access denied.")
        return redirect(url_for("sponsor_dashboard"))

    try:
        AdRequest.query.filter_by(campaign_id=campaign_id).delete()
        CampaignRequest.query.filter_by(campaign_id=campaign_id).delete()
        
        db.session.delete(campaign)
        
        db.session.commit()
        flash("Campaign and associated requests deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the campaign: {str(e)}")

    return redirect(url_for("sponsor_dashboard"))

@app.route("/sponsor/create_ad_request/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def create_ad_request(campaign_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    campaign = Campaign.query.get_or_404(campaign_id)
    influencer_id = request.args.get('influencer_id')

    if request.method == "POST":
        influencer_id = request.form.get("influencer_id")
        messages = request.form.get("messages")
        requirements = request.form.get("requirements")
        payment_amount = float(request.form.get("payment_amount"))

        new_ad_request = AdRequest(campaign_id=campaign_id, influencer_id=influencer_id,
                                   messages=messages, requirements=requirements,
                                   payment_amount=payment_amount, status="pending")
        db.session.add(new_ad_request)
        db.session.commit()

        flash("Ad request created successfully.")
        return redirect(url_for("sponsor_dashboard"))

    influencers = Influencer.query.all()
    return render_template("create_ad_request.html", campaign=campaign, influencers=influencers, influencer_id=influencer_id)

@app.route("/sponsor/edit_ad_request/<int:ad_request_id>", methods=["GET", "POST"])
@login_required
def edit_ad_request(ad_request_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.campaign.sponsor_id != Sponsor.query.filter_by(user_id=current_user.id).first().id:
        flash("Access denied.")
        return redirect(url_for("sponsor_dashboard"))

    if request.method == "POST":
        ad_request.influencer_id = request.form.get("influencer_id")
        ad_request.messages = request.form.get("messages")
        ad_request.requirements = request.form.get("requirements")
        ad_request.payment_amount = float(request.form.get("payment_amount"))
        ad_request.status = request.form.get("status")

        db.session.commit()
        flash("Ad request updated successfully.")
        return redirect(url_for("sponsor_dashboard"))

    influencers = Influencer.query.all()
    return render_template("edit_ad_request.html", ad_request=ad_request, influencers=influencers)

@app.route("/sponsor/delete_ad_request/<int:ad_request_id>", methods=["POST"])
@login_required
def delete_ad_request(ad_request_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.campaign.sponsor_id != Sponsor.query.filter_by(user_id=current_user.id).first().id:
        flash("Access denied.")
        return redirect(url_for("sponsor_dashboard"))

    db.session.delete(ad_request)
    db.session.commit()
    flash("Ad request deleted successfully.")
    return redirect(url_for("sponsor_dashboard"))

@app.route("/influencer/dashboard")
@login_required
def influencer_dashboard():
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))

    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
    pending_campaigns = Campaign.query.join(AdRequest).filter(
        AdRequest.influencer_id == influencer.id,
        AdRequest.status == 'pending'
    ).distinct()

    query = request.args.get("query")
    industry = request.args.get("industry")
    min_budget = request.args.get("min_budget")
    
    if query:
        pending_campaigns = pending_campaigns.filter(Campaign.name.ilike(f"%{query}%"))
    if industry:
        pending_campaigns = pending_campaigns.join(Sponsor).filter(Sponsor.industry == industry)
    if min_budget:
        pending_campaigns = pending_campaigns.filter(Campaign.budget >= float(min_budget))
    
    pending_campaigns = pending_campaigns.all()

    accepted_requests = sum(1 for r in ad_requests if r.status == 'accepted')
    rejected_requests = sum(1 for r in ad_requests if r.status == 'rejected')
    pending_requests = sum(1 for r in ad_requests if r.status == 'pending')
    total_requests = len(ad_requests)
    acceptance_rate = (accepted_requests / total_requests * 100) if total_requests > 0 else 0

    total_earnings = sum(r.payment_amount for r in ad_requests if r.status == 'accepted')
    avg_earnings_per_campaign = total_earnings / accepted_requests if accepted_requests > 0 else 0
    highest_paid_campaign = max((r.payment_amount for r in ad_requests if r.status == 'accepted'), default=0)

    latest_ad_request = AdRequest.query.filter_by(influencer_id=influencer.id).order_by(AdRequest.created_at.desc()).first()

    return render_template(
        "influencer_dashboard.html",
        influencer=influencer,
        ad_requests=ad_requests,
        pending_campaigns=pending_campaigns,
        accepted_requests=accepted_requests,
        rejected_requests=rejected_requests,
        pending_requests=pending_requests,
        acceptance_rate=round(acceptance_rate, 2),
        total_earnings=round(total_earnings, 2),
        avg_earnings_per_campaign=round(avg_earnings_per_campaign, 2),
        highest_paid_campaign=round(highest_paid_campaign, 2),
        latest_ad_request=latest_ad_request,
    )


@app.route("/influencer/respond_ad_request/<int:ad_request_id>", methods=["POST"])
@login_required
def respond_ad_request(ad_request_id):
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    action = request.form.get("action")

    if action == "accept":
        if ad_request.status == "negotiating":
            ad_request.payment_amount = ad_request.proposed_amount
        ad_request.status = "accepted"
        flash("Ad request accepted.")
    elif action == "reject":
        ad_request.status = "rejected"
        flash("Ad request rejected.")
    elif action == "negotiate":
        new_amount = float(request.form.get("new_amount"))
        ad_request.proposed_amount = new_amount
        ad_request.status = "negotiating"
        ad_request.last_updated_by = "influencer"
        flash("Negotiation proposal sent.")
    else:
        flash("Invalid action.")

    db.session.commit()
    return redirect(url_for('influencer_dashboard') + '#ad-requests')

@app.route("/search_influencers")
@login_required
def search_influencers():
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    query = request.args.get("query")
    category = request.args.get("category")
    min_reach = request.args.get("min_reach")
    campaign_id = request.args.get("campaign_id")
    
    influencers = Influencer.query
    
    if query:
        influencers = influencers.filter(Influencer.name.ilike(f"%{query}%"))
    if category:
        influencers = influencers.filter_by(niche = category  )
    if min_reach:
        influencers = influencers.filter(Influencer.reach >= int(min_reach))
    
    influencers = influencers.all()
    campaign = None
    if campaign_id:
        campaign = Campaign.query.get(campaign_id)
    
    return render_template("search_influencers.html", influencers=influencers, campaign=campaign)


@app.route("/search_campaigns")
@login_required
def search_campaigns():
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))

    query = request.args.get("query")
    industry = request.args.get("industry")
    min_budget = request.args.get("min_budget")
    
    campaigns = Campaign.query.filter_by(visibility="public")
    if query:
        campaigns = campaigns.filter(Campaign.name.ilike(f"%{query}%"))
    if industry:
        campaigns = campaigns.join(Sponsor).filter(Sponsor.industry == industry)
    if min_budget:
        campaigns = campaigns.filter(Campaign.budget >= float(min_budget))
    
    campaigns = campaigns.all()
    return redirect(url_for("influencer_dashboard")+'#find-campaigns')

@app.route("/view_campaign/<int:campaign_id>")
@login_required
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id, status='pending').all()
    return render_template("view_campaign.html", campaign=campaign, ad_requests=ad_requests)


@app.route("/request_ad/<int:ad_request_id>", methods=["POST"])
@login_required
def request_ad(ad_request_id):
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))
    
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    
    if ad_request.status != 'pending':
        flash("This ad request is no longer available.")
        return redirect(url_for("view_campaign", campaign_id=ad_request.campaign_id))
    
    ad_request.influencer_id = influencer.id
    ad_request.status = 'requested'
    db.session.commit()
    
    flash("Ad request submitted successfully.")
    return redirect(url_for("view_campaign", campaign_id=ad_request.campaign_id))

    


@app.route("/sponsor/handle_ad_request/<int:ad_request_id>", methods=["POST"])
@login_required
def handle_ad_request(ad_request_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    action = request.form.get("action")

    if action == "accept":
        ad_request.status = "accepted"
        flash("Ad request accepted.")
    elif action == "reject":
        ad_request.status = "rejected"
        flash("Ad request rejected.")
    else:
        flash("Invalid action.")

    db.session.commit()
    return redirect(url_for('sponsor_dashboard') + '#campaign-requests')

@app.route("/request_campaign/<int:campaign_id>", methods=["POST"])
@login_required
def request_campaign(campaign_id):
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    
    existing_request = CampaignRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer.id).first()
    if existing_request:
        flash("You have already requested this campaign.")
    else:
        new_request = CampaignRequest(campaign_id=campaign_id, influencer_id=influencer.id)
        db.session.add(new_request)
        db.session.commit()
        flash("Campaign request sent successfully.")
    
    return redirect(url_for("view_campaign", campaign_id=campaign_id))

@app.route("/influencer/negotiate/<int:ad_request_id>", methods=["POST"])
@login_required
def negotiate_ad_request(ad_request_id):
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    proposed_amount = float(request.form.get("proposed_amount"))

    ad_request.proposed_amount = proposed_amount
    ad_request.status = "negotiating"
    ad_request.last_updated_by = "influencer"
    db.session.commit()

    flash("Negotiation proposal sent to sponsor.")
    return redirect(url_for("view_ad_requests"))

@app.route("/sponsor/respond_negotiation/<int:ad_request_id>", methods=["POST"])
@login_required
def respond_negotiation(ad_request_id):
    if current_user.role != "sponsor":
        flash("Access denied.")
        return redirect(url_for("home"))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    action = request.form.get("action")

    if action == "accept":
        ad_request.payment_amount = ad_request.proposed_amount
        ad_request.status = "accepted"
        flash("Negotiation accepted.")
    elif action == "reject":
        ad_request.status = "rejected"
        flash("Negotiation rejected.")
    elif action == "counter":
        counter_amount = float(request.form.get("counter_amount"))
        ad_request.proposed_amount = counter_amount
        ad_request.status = "negotiating"
        ad_request.last_updated_by = "sponsor"
        flash("Counter-offer sent to influencer.")

    db.session.commit()
    return redirect(url_for("sponsor_dashboard")+"##ad-requests")

@app.route("/update_influencer_profile", methods=["POST"])
@login_required
def update_influencer_profile():
    if current_user.role != "influencer":
        flash("Access denied.")
        return redirect(url_for("home"))
    
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    if not influencer:
        flash("Influencer profile not found.")
        return redirect(url_for("influencer_dashboard"))
    
    influencer.name = request.form.get("name")
    influencer.category = request.form.get("category")
    influencer.niche = request.form.get("niche")
    influencer.reach = request.form.get("reach")
    
    db.session.commit()
    flash("Profile updated successfully.")
    return redirect(url_for('influencer_dashboard') + '#profile')
