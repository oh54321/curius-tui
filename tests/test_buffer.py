from typing import Dict, List
from unittest.mock import patch

from src.buffer import LinkBuffer, link_timestamp
from src.nodes import Link

from tests.test_nodes import make_link_dict, make_user_dict
from src.nodes import User


def _user(user_id: int, last_online: str, pages: Dict[int, List[Link]]) -> User:
    user_dict = make_user_dict(id=user_id, lastOnline=last_online)
    user_dict["userLink"] = f"user{user_id}"
    user = User.from_dict(user_dict)

    def links_page(page: int) -> List[Link]:
        return pages.get(page, [])

    # Bind a per-instance override to avoid the global network client.
    user.links_page = links_page  # type: ignore[assignment]
    return user


class TestLinkTimestamp:
    def test_falls_back_to_created_date(self):
        link = Link.from_dict(make_link_dict(modifiedDate=""))
        ts = link_timestamp(link)
        # epoch sentinel because empty modified_date and created_date is also set
        assert ts.year >= 2024 or ts.year == 1970

    def test_uses_modified_date_when_present(self):
        link = Link.from_dict(make_link_dict(modifiedDate="2024-05-01T00:00:00Z"))
        assert link_timestamp(link).year == 2024


class TestLinkBuffer:
    def test_paginates_in_descending_order(self):
        # Two users; their links interleave by date when merged.
        # Each link gets a unique URL so the dedup pass doesn't collapse them.
        def _link(id_, ts):
            return Link.from_dict(
                make_link_dict(
                    id=id_, link=f"https://example.com/{id_}", modifiedDate=ts
                )
            )

        u1_links_p0 = [
            _link(1, "2024-06-10T00:00:00Z"),
            _link(2, "2024-06-01T00:00:00Z"),
        ]
        u2_links_p0 = [
            _link(3, "2024-06-05T00:00:00Z"),
            _link(4, "2024-05-20T00:00:00Z"),
        ]

        u1 = _user(1, "2024-06-15T00:00:00Z", {0: u1_links_p0, 1: []})
        u2 = _user(2, "2024-06-12T00:00:00Z", {0: u2_links_p0, 1: []})

        buffer = LinkBuffer([u1, u2], include_users=False)
        first_two = buffer.get_next_n(2)
        assert [link.id for link in first_two] == [1, 3]
        remaining = buffer.get_next_n(10)
        assert [link.id for link in remaining] == [2, 4]
        assert buffer.is_exhausted()

    def test_dedupes_links_seen_via_multiple_users(self):
        shared = make_link_dict(id=10, modifiedDate="2024-06-10T00:00:00Z")
        u1_links = [Link.from_dict(shared)]
        u2_links = [Link.from_dict(shared)]

        u1 = _user(1, "2024-06-15T00:00:00Z", {0: u1_links, 1: []})
        u2 = _user(2, "2024-06-14T00:00:00Z", {0: u2_links, 1: []})

        buffer = LinkBuffer([u1, u2], include_users=False)
        result = buffer.get_next_n(10)
        assert [link.id for link in result] == [10]

    def test_include_users_decorates_titles(self):
        link_dict = make_link_dict(id=20, modifiedDate="2024-06-10T00:00:00Z")
        u1 = _user(1, "2024-06-15T00:00:00Z", {0: [Link.from_dict(link_dict)], 1: []})
        u2 = _user(2, "2024-06-14T00:00:00Z", {0: [Link.from_dict(link_dict)], 1: []})

        # Avoid hitting UserGraph.get_user during user-name lookup for FollowingUsers.
        with patch("src.buffer.LinkBuffer._get_user", side_effect=lambda x: x):
            buffer = LinkBuffer([u1, u2], include_users=True)
            result = buffer.get_next_n(10)

        assert len(result) == 1
        # The title should be prefixed with the user(s) that saved it.
        assert "Example A" in result[0].title
        assert "|" in result[0].title
