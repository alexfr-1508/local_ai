# zammad_client.py

import requests
from collections import Counter
from datetime import datetime, timedelta, timezone
from zammad.zammad_render import ZammadRenderer

class ZammadClient:
    def __init__(self, base_url: str, token: str):
        self.renderer = ZammadRenderer()

        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token token={token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        self._group_map = None
        self.state_map = None

        self._group_map = self.get_group_map()
        self.state_map = self.get_state_map()

        self.open_states = {
            "new",
            "open",
        }
        self.closed_states = {
            "closed",
            "merged",
            "pending close",
            "Warten auf Kunde"
        } # expand as needed

    def _ticket_summary(self, ticket: dict) -> dict:
        state = self.state_map.get(
            ticket["state_id"],
            f"Unknown ({ticket['state_id']})"
        )
        group = self._group_map.get(
            ticket["group_id"],
            f"Unknown ({ticket['group_id']})"
        )

        return {
            "id": ticket["id"],
            "number": ticket["number"],
            "title": ticket["title"],
            "state": state,
            "priority_id": ticket["priority_id"],
            "owner_id": ticket["owner_id"],
            "customer_id": ticket["customer_id"],
            "group": group,
            "article_count": ticket["article_count"],
            "created_at": ticket["created_at"],
            "updated_at": ticket["updated_at"],
        }
    
    def list_states(self):
        response = self.session.get(
            f"{self.base_url}/api/v1/ticket_states"
        )

        response.raise_for_status()
        return response.json()


    def get_state_map(self):
        states = self.list_states()

        return {
            state["id"]: state["name"]
            for state in states
        }

    def list_groups(self):
        response = self.session.get(
            f"{self.base_url}/api/v1/groups"
        )

        response.raise_for_status()
        return response.json()
    
    def get_group_map(self):
        if self._group_map is None:
            groups = self.list_groups()

            self._group_map = {
                group["id"]: group["name"]
                for group in groups
            }

        return self._group_map

    def list_organizations(self):
        response = self.session.get(
            f"{self.base_url}/api/v1/organizations"
        )

        response.raise_for_status()
        return response.json()
    
    def get_ticket(self, ticket_id: int):
        response = self.session.get(
            f"{self.base_url}/api/v1/tickets/{ticket_id}"
        )

        response.raise_for_status()
        return response.json()

    def list_tickets(self, page: int = 1, per_page: int = 25):
        response = self.session.get(
            f"{self.base_url}/api/v1/tickets",
            params={
                "page": page,
                "per_page": per_page,
            },
        )

        response.raise_for_status()
        tickets = response.json()

        return [self._ticket_summary(ticket) for ticket in tickets]
    
    def search_tickets(self, query: str, per_page: int = 200): # max Zammad search limit is 200
        tickets = []
        page = 1

        while True:
            response = self.session.get(
                f"{self.base_url}/api/v1/tickets/search",
                params={
                    "query": query,
                    "page": page,
                    "per_page": per_page,
                },
            )

            response.raise_for_status()
            batch = response.json()

            if not batch:
                break
            tickets.extend(
                self._ticket_summary(ticket)
                for ticket in batch
            )

            page += 1

        return tickets
    
    def tickets_between(self, start: datetime, end: datetime, per_page: int = 200):
        query = f"created_at:[{start.strftime('%Y-%m-%d')} TO {(end - timedelta(days=1)).strftime('%Y-%m-%d')}]"
        return self.search_tickets(query, per_page=per_page)
    
    def tickets_for_month(self, year: int, month: int, per_page: int = 200):
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        start = datetime(year, month, 1, tzinfo=timezone.utc)

        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        return self.tickets_between(start, end, per_page=per_page)
    
    def tickets_for_year(self, year: int, per_page: int = 200):
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

        return self.tickets_between(start, end, per_page=per_page)
    
    def tickets_past_days(self, days: int, per_page: int = 200):
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        return self.tickets_between(start, end, per_page)
    
    def _state_grouping(self, tickets: list, start: datetime, end: datetime):
        opened = len(tickets)
        closed = sum(
            1 for ticket in tickets
            if ticket["state"] in self.closed_states
        )

        by_group = {}

        for ticket in tickets:
            group = ticket["group"]

            if group not in by_group:
                by_group[group] = {
                    "opened": 0,
                    "closed": 0,
                    "still_open": 0,
                }

            by_group[group]["opened"] += 1

            if ticket["state"] in self.closed_states:
                by_group[group]["closed"] += 1
            else:
                by_group[group]["still_open"] += 1

        return {
            "period": {
                "from": start.isoformat(),
                "to": end.isoformat(),
                "timezone": "UTC",
            },
            "per_group": by_group,
            "total": {
                "opened": opened,
                "closed": closed,
                "still_open": opened - closed,
            },
        }
    
    def summary_month(self, year: int, month: int):
        start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        return self._state_grouping(self.tickets_for_month(year, month), start, end)
    
    def summary_year(self, year: int):
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

        return self._state_grouping(self.tickets_for_year(year), start, end)

    def _summary_since(self, days: int):
        now = datetime.now(timezone.utc)
        since = now - timedelta(days=days)

        return self._summary_between(since, now)
    
    def summary_past_days(self, days):
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        return self._state_grouping(self.tickets_past_days(days), start, end)
    
    def summary_last_week(self):
        return self.summary_past_days(7)
        
    
    def summary_last_month(self):
        return self.summary_past_days(30)
    
    def list_all_tickets(self):
        tickets = []
        page = 1
        per_page = 100

        while True:
            batch = self.list_tickets(page=page, per_page=per_page,)
            if not batch:
                break

            tickets.extend(batch)

            if len(batch) < per_page:
                break

            page += 1

        return tickets
    
    def summary_open(self):
        tickets = self.list_all_tickets()
        grouped_tickets = self.open_grouping(tickets)
        return grouped_tickets
    
    def open_grouping(self, tickets):
        states = {}
        for ticket in tickets:
            states[ticket["state"]] = states.get(ticket["state"], 0) + 1

        groups = {}
        groups["total"] = 0

        for ticket in tickets:
            if ticket["state"] in self.closed_states:
                continue

            groups["total"] += 1
            group = ticket["group"]
            if group not in groups:
                groups[group] = 0

            groups[group] += 1

        return groups
    
    def summary(self):
        last_7_days = self.summary_last_week()
        last_30_days = self.summary_last_month()
        current_open = self.summary_open()

        categories = current_open.keys()

        return {
            "summary": {
                "current_open": current_open["total"],
                "last_7_days": last_7_days["total"],
                "last_30_days": last_30_days["total"],
            },
            "categories": {
               category: {
                   "current_open": current_open[category],
                   "last_7_days": last_7_days["per_group"].get(
                       category,
                       {
                           "opened": 0,
                           "closed": 0,
                           "still_open": 0,
                       }
                   ),

                   "last_30_days": last_30_days["per_group"].get(
                       category,
                       {
                           "opened": 0,
                           "closed": 0,
                           "still_open": 0,
                       }
                   ),
               }
               for category in categories if category != "total"
            },
            "periods": {
                "last_7_days": last_7_days["period"],
                "last_30_days": last_30_days["period"]
            }
        }
    def summary_html(self):
        report = self.summary()
        content = ""
        content += self.renderer.render_header("Ticketübersicht", 1)
        content += self.renderer.render_periods(report["periods"])
        content += self.renderer.render_table("Gesamtübersicht", 2, report["summary"]) 
        content += self.renderer.render_header("Kategorien", 2)
        content += self.renderer.render_categories(report["categories"])

        return content


    def get_current_user(self):
        response = self.session.get(
	        f"{self.base_url}/api/v1/users/me"
        )
        response.raise_for_status()
        return response.json()
    
    def test(self):
        response = self.session.get(
            f"{self.base_url}/api/v1/tickets/search",
            params={
                "query": f"created_at:[2024-01-01 TO 2026-01-01]",
                "only_total_count": True,
            },
        )

        return response.json()


    # Tags
    def get_ticket_tags(self, ticket_id: int):
        response = self.session.get(
                f"{self.base_url}/api/v1/tags?object=Ticket&o_id={ticket_id}"
            )
    
        response.raise_for_status()
        return response.json()["tags"]

    

    def tag_statistics(self, tickets):
        counter = Counter()

        for ticket in tickets:
            tags = self.get_ticket_tags(ticket["id"])
            counter.update(tags)

        return {
            "tag_counts": counter.most_common()
        }
