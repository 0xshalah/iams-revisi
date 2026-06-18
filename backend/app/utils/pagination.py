"""Simple cursor-free pagination helper."""
from flask import request


def paginate(query, max_per_page=100):
    """Apply page/per_page pagination to a SQLAlchemy query.

    Expects query params ``page`` (default 1) and ``per_page`` (default 25,
    capped at ``max_per_page``).  Returns a dict with:
        data       -> list[dict]
        page       -> int
        per_page   -> int
        total      -> int
        pages      -> int
    """
    try:
        page = int(request.args.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    if page < 1:
        page = 1

    try:
        per_page = int(request.args.get('per_page', 25))
    except (ValueError, TypeError):
        per_page = 25
    if per_page < 1:
        per_page = 1
    per_page = min(per_page, max_per_page)

    # Count total rows via a subquery to avoid ordering/limit conflicts
    total = query.order_by(None).count()
    pages = max(1, -(-total // per_page))  # ceiling division
    if page > pages:
        page = pages

    rows = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        'data': [r.to_dict() for r in rows],
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': pages,
    }
