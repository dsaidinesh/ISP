# Influencer Engagement and Sponsorship Coordination Platform

## Project Overview
This project is designed to create a platform that connects **Sponsors** and **Influencers**, enabling sponsors to advertise their services and influencers to monetize their reach. Sponsors can create multiple campaigns and ad requests, assigning them to various influencers. Simultaneously, influencers can search for campaigns, monitor their earnings, and more. This platform serves as a bridge between influencers and sponsors.

## Architecture and Features
- **MVC Architecture**:
  - **Controllers**: Handle all logic and routing.
  - **Templates**: Contain models.
  - **Static Files**: Include CSS and JavaScript.

- **Key Features**:
  - Separate registration pages for Sponsors and Influencers to maintain clean data.
  - A single login button for all users (admin, sponsor, or influencer).
  - Admin privileges to view all platform data and flag specific users if misconduct is detected.
  - Dedicated dashboards for both sponsors and influencers.
  - Negotiation feature enabling influencers and sponsors to discuss ad pricing.

## Database Schema Design
The database design consists of five main tables:
1. **User**: `id`, `username`, `email`, `password`, `role`
2. **Admin**: `id`, `user_id`
3. **Sponsor**: `id`, `user_id`, `company_name`, `industry`, `budget`
4. **Influencer**: `id`, `user_id`, `name`, `category`, `niche`, `reach`
5. **Campaign**: `name`, `description`, `budget`, `date`, `visibility`, `goals`
6. **AdRequest**: `messages`, `requirements`, `payment_amount`, `status`

For a comprehensive understanding of the database and table relationships, please refer to the [ER diagram](https://drive.google.com/file/d/1aj3L2x1OKauZW_8yCLcW98tjg8HRaZ_l/view?usp=sharing).

## Technologies and Libraries Used
- **Flask**: Backend framework for building the web application.
- **SQLAlchemy**: ORM (Object-Relational Mapping) tool for database interactions.
- **SQLite**: Database management system for storing application data.
- **HTML, Bootstrap, JavaScript**: Frontend technologies for user interface design and interactivity.
- **Flask-Login**: Extension for managing user sessions and authentication.
- **Datetime**: Python library for handling date and time operations.
- **Jinja2**: Template engine for rendering dynamic HTML content.

## Challenges Faced
- **Database Relationships**: Establishing proper relationships between database tables required significant time and effort.
- **Negotiation Functionality**: Implementing the negotiation functionality between sponsors and influencers required schema adjustments.

## Future Improvements
- Add a project status feature for influencers to update campaign progress and notify sponsors.
- Implement a dummy payment page to simulate transactions between sponsors and influencers.
- Enhance the overall styling of the platform to improve user experience and visual appeal.
- Explore additional features to expand the platform's capabilities and user engagement.

## Conclusion
The Influencer Engagement and Sponsor Coordination Platform serves as a functional tool for both sponsors and influencers to accomplish their respective tasks. Sponsors can create multiple campaigns, make ad requests, and assign them to specific influencers based on their needs. Influencers can request to participate in public campaigns and track their income effectively.

