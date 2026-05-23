import pandas as pd

from src.nodes import FollowingUser, Highlight, Link, Network, User


def make_user_dict(**overrides):
    data = {
        "id": 1,
        "firstName": "Ada",
        "lastName": "Lovelace",
        "userLink": "ada",
        "major": "Maths",
        "interests": "engines",
        "expertise": "analytical",
        "school": "London",
        "github": None,
        "twitter": None,
        "website": None,
        "createdDate": "2024-01-01T00:00:00Z",
        "modifiedDate": "2024-01-02T00:00:00Z",
        "lastOnline": "2024-06-01T00:00:00Z",
        "lastCheckedNotifications": "2024-06-01T00:00:00Z",
        "views": 10,
        "numFollowers": 5,
        "followed": False,
        "followingMe": False,
        "recentUsers": [],
        "followingUsers": [
            {
                "id": 2,
                "firstName": "Grace",
                "lastName": "Hopper",
                "userLink": "grace",
                "lastOnline": "2024-05-01T00:00:00Z",
            }
        ],
    }
    data.update(overrides)
    return data


def make_link_dict(**overrides):
    data = {
        "id": 100,
        "link": "https://example.com/a",
        "title": "Example A",
        "favorite": False,
        "snippet": "snippet",
        "toRead": False,
        "createdBy": 1,
        "metadata": None,
        "createdDate": "2024-03-01T00:00:00Z",
        "modifiedDate": "2024-03-02T00:00:00Z",
        "lastCrawled": None,
        "trails": [],
        "comments": [],
        "mentions": [],
        "topics": [],
        "highlights": [],
        "userIds": [1, 2],
    }
    data.update(overrides)
    return data


class TestUser:
    def test_from_dict(self):
        user = User.from_dict(make_user_dict())
        assert user.id == 1
        assert user.name == "Ada Lovelace"
        assert len(user.following_users) == 1
        assert isinstance(user.following_users[0], FollowingUser)
        assert user.following_users[0].user_link == "grace"

    def test_name_omits_empty_last_name(self):
        user = User.from_dict(make_user_dict(lastName=""))
        assert user.name == "Ada"

    def test_is_expanded_reflects_set_expanded(self):
        # Regression: is_expanded was @cached_property and silently froze
        # the first observed value, so set_expanded was a no-op afterwards.
        user = User.from_dict(make_user_dict())
        assert user.is_expanded is False
        _ = user.is_expanded  # would cache under the old bug
        user._is_expanded = True
        assert user.is_expanded is True


class TestLink:
    def test_from_dict(self):
        link = Link.from_dict(make_link_dict())
        assert link.id == 100
        assert link.url == "https://example.com/a"
        assert link.title == "Example A"
        assert link.user_ids == [1, 2]

    def test_timestamp_uses_modified_date(self):
        link = Link.from_dict(make_link_dict())
        assert link.timestamp == pd.Timestamp("2024-03-02T00:00:00Z")

    def test_ordering_by_modified_date(self):
        old = Link.from_dict(make_link_dict(modifiedDate="2024-01-01T00:00:00Z"))
        new = Link.from_dict(make_link_dict(modifiedDate="2024-12-01T00:00:00Z"))
        assert old < new

    def test_set_title_preserves_original(self):
        link = Link.from_dict(make_link_dict())
        original = link.title
        link.set_title("Decorated | " + original)
        assert link.title == "Decorated | Example A"
        # set_title remembers the very first override target
        link.set_title("Other | " + original)
        assert link._title == "Decorated | " + original


class TestHighlight:
    def test_from_dict(self):
        data = {
            "id": 7,
            "userId": 1,
            "linkId": 100,
            "highlight": "the most important sentence",
            "createdDate": "2024-04-01T00:00:00Z",
            "leftContext": "before ",
            "rightContext": " after",
            "rawHighlight": "<b>the most important sentence</b>",
            "commentIds": [9],
            "comment": "great point",
        }
        hl = Highlight.from_dict(data)
        assert hl.id == 7
        assert hl.user_id == 1
        assert hl.link_id == 100
        assert hl.comment_ids == [9]


class TestNetwork:
    def test_from_payload_minimal(self):
        payload = {
            "networkInfo": {
                "id": 100,
                "link": "https://example.com/a",
                "title": "Example A",
                "users": [
                    {"id": 1, "userLink": "ada", "savedDate": "2024-03-02"},
                    {"id": 2, "userLink": "grace", "savedDate": "2024-03-03"},
                ],
                "highlights": [[], []],
                "readCount": 2,
                "userIds": [1, 2],
            }
        }
        net = Network.from_payload(payload)
        assert net.link.id == 100
        assert net.user_links == ["ada", "grace"]
        assert net.read_count == 2
        assert net.user_saved_dates == {1: "2024-03-02", 2: "2024-03-03"}

    def test_from_payload_missing_link_raises(self):
        import pytest

        with pytest.raises(ValueError):
            Network.from_payload({"networkInfo": {"users": []}})
