from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from decimal import Decimal

from .models import User, Category, Listing, Bid, Comment


def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def categories(request):
    from django.db.models import Count, Q
    cats = Category.objects.annotate(
        active_count=Count("listings", filter=Q(listings__is_active=True))
    )
    return render(request, "auctions/categories.html", {
        "categories": cats
    })


def category(request, category_id):
    cat = get_object_or_404(Category, pk=category_id)
    return render(request, "auctions/category.html", {
        "category": cat,
        "listings": cat.listings.filter(is_active=True)
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = (request.POST.get("image_url") or "").strip()
        image_file = request.FILES.get("image_file")
        category_id = request.POST.get("category")

        cat = Category.objects.filter(pk=category_id).first() if category_id else None
        listing_obj = Listing.objects.create(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url or None,
            image_file=image_file,
            category=cat,
            owner=request.user
        )
        return redirect("listing", listing_obj.id)
    return render(request, "auctions/create.html", {
        "categories": Category.objects.all()
    })


@login_required
def delete_listing(request, listing_id):
    # Delete an auction, but only the owner may do it.
    lst = get_object_or_404(Listing, pk=listing_id)

    if lst.owner != request.user:
        return HttpResponseForbidden("You can only delete listings you created.")

    if request.method == "POST":
        if lst.image_file:
            lst.image_file.delete(save=False)
        lst.delete()
        return redirect("index")

    return render(request, "auctions/delete_listing.html", {"listing": lst})


def listing(request, listing_id):
    lst = get_object_or_404(Listing, pk=listing_id)
    in_watchlist = request.user in lst.watchers.all() if request.user.is_authenticated else False

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        action = request.POST.get("action")

        if action == "watch":
            lst.watchers.add(request.user)
        elif action == "unwatch":
            lst.watchers.remove(request.user)
        elif action == "bid":
            try:
                amount = Decimal(request.POST["amount"])
            except Exception:
                request.session["bid_error"] = "Enter a valid bid amount."
            else:
                if amount <= lst.current_price():
                    request.session["bid_error"] = f"Your bid must be higher than the current price (${lst.current_price()})."
                else:
                    Bid.objects.create(amount=amount, bidder=request.user, listing=lst)
                    request.session["bid_message"] = "Your bid was placed successfully!"
        elif action == "close":
            if request.user == lst.owner:
                lst.is_active = False
                lst.save()
        elif action == "comment":
            content = request.POST.get("content", "").strip()
            if content:
                Comment.objects.create(content=content, author=request.user, listing=lst)

        return redirect("listing", lst.id)

    message = request.session.pop("bid_message", None)
    error = request.session.pop("bid_error", None)

    return render(request, "auctions/listing.html", {
        "listing": lst,
        "in_watchlist": in_watchlist,
        "message": message,
        "error": error,
        "is_owner": request.user == lst.owner,
    })


@login_required
def watchlist(request):
    if request.method == "POST":
        # Quick remove from the watchlist cards.
        if request.POST.get("action") == "unwatch":
            listing_obj = Listing.objects.filter(pk=request.POST.get("listing_id")).first()
            if listing_obj is not None:
                listing_obj.watchers.remove(request.user)
        return redirect("watchlist")

    listings = request.user.watchlist.filter(is_active=True)
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "show_remove": True,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
