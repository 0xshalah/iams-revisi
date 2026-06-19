"""Flask application factory."""
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from app.extensions import db, limiter, migrate
from app.utils.audit import get_client_ip, log_audit


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS: explicit origin only, credentials allowed
    CORS(
        app,
        resources={r'/api/*': {'origins': [app.config['FRONTEND_ORIGIN']]}},
        supports_credentials=True,
        allow_headers=['Content-Type', 'X-CSRF-Token'],
        methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    )

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    # Generic error handlers: never leak internal details
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(429)
    def rate_limited(_):
        log_audit('RATE_LIMIT', 'api', status='failure',
                  metadata={'ip': get_client_ip(), 'path': request.path})
        return jsonify({'error': 'Too many requests'}), 429

    @app.errorhandler(Exception)
    def handle_exception(exc):
        app.logger.exception('Unhandled exception')
        return jsonify({'error': 'Internal server error'}), 500

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.users import bp as users_bp
    from app.routes.roles import bp as roles_bp
    from app.routes.master import bp as master_bp
    from app.routes.assets import bp as assets_bp
    from app.routes.incidents import bp as incidents_bp
    from app.routes.problems import bp as problems_bp
    from app.routes.audit_logs import bp as audit_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.health import bp as health_bp
    from app.routes.requests import bp as requests_bp
    from app.routes.changes import bp as changes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(master_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(problems_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(changes_bp)

    from app.commands import seed_command
    app.cli.add_command(seed_command)

    return app
