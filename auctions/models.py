from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to="listings/", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="listings")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)
    watchers = models.ManyToManyField(
        User, blank=True, related_name="watchlist")

    def current_price(self):
        highest = self.bids.order_by("-amount").first()
        return highest.amount if highest else self.starting_bid
    def image_src(self):
        # Uploaded file wins; otherwise fall back to the external URL.
        if self.image_file:
            return self.image_file.url
        return self.image_url or ""

    def winner(self):
        if not self.is_active:
            highest = self.bids.order_by("-amount").first()
            return highest.bidder if highest else None
        return None

    def __str__(self):
        return self.title


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder} bid ${self.amount} on {self.listing}"


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} on {self.listing}"
