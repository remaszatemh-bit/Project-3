def watchlist_count(request):
    """Expose the number of items in the current user's watchlist to every template."""
    if not request.user.is_authenticated:
        return {"watchlist_count": 0}
    return {"watchlist_count": request.user.watchlist.count()}
