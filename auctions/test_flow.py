from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment


class FlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", "o@x.com", "pass12345")
        self.bidder = User.objects.create_user("bidder", "b@x.com", "pass12345")
        self.cat = Category.objects.create(name="Cars")

    def test_full_flow(self):
        self.client.force_login(self.owner)
        r = self.client.post(reverse("create"), {
            "title": "BMW", "description": "Nice car", "starting_bid": "100",
            "image_url": "", "category": self.cat.id})
        self.assertEqual(r.status_code, 302)
        listing = Listing.objects.get(title="BMW")
        self.assertEqual(listing.current_price(), Decimal("100.00"))
        self.assertEqual(r.url, reverse("listing", args=[listing.id]))

        # bidder bids
        self.client.force_login(self.bidder)
        self.client.post(reverse("listing", args=[listing.id]), {"action": "bid", "amount": "150"})
        listing.refresh_from_db()
        self.assertEqual(listing.current_price(), Decimal("150.00"))

        # low bid rejected
        self.client.post(reverse("listing", args=[listing.id]), {"action": "bid", "amount": "120"})
        self.assertEqual(Bid.objects.count(), 1)
        page = self.client.get(reverse("listing", args=[listing.id]))
        self.assertIn("must be higher", page.content.decode())

        # watchlist toggle
        self.client.post(reverse("listing", args=[listing.id]), {"action": "watch"})
        self.assertEqual(self.bidder.watchlist.count(), 1)
        self.assertContains(self.client.get(reverse("watchlist")), "BMW")
        self.client.post(reverse("listing", args=[listing.id]), {"action": "unwatch"})
        self.assertEqual(self.bidder.watchlist.count(), 0)

        # comment
        self.client.post(reverse("listing", args=[listing.id]), {"action": "comment", "content": "Great!"})
        self.assertEqual(Comment.objects.count(), 1)

        # bidder cannot close
        self.client.post(reverse("listing", args=[listing.id]), {"action": "close"})
        listing.refresh_from_db()
        self.assertTrue(listing.is_active)

        # owner closes -> winner
        self.client.force_login(self.owner)
        self.client.post(reverse("listing", args=[listing.id]), {"action": "close"})
        listing.refresh_from_db()
        self.assertFalse(listing.is_active)
        self.assertEqual(listing.winner(), self.bidder)
        self.assertNotContains(self.client.get(reverse("index")), "BMW")

        # category page
        r = self.client.get(reverse("category", args=[self.cat.id]))
        self.assertEqual(r.status_code, 200)
