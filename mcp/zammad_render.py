from datetime import datetime, timedelta, timezone

class ZammadRenderer:
    def render_table(self, title, heading_size, data):
        return f"""
        {self.render_header(title, heading_size)}

        <table>
            <tr>
                <th>Zeitraum</th>
                <th class="number">Eröffnet</th>
                <th class="number">Geschlossen</th>
                <th class="number">Offen</th>
            </tr>

            <tr>
                <td>Letzte 7 Tage</td>
                <td class="number">{data["last_7_days"]["opened"]}</td>
                <td class="number">{data["last_7_days"]["closed"]}</td>
                <td class="number">{data["last_7_days"]["still_open"]}</td>
            </tr>

            <tr>
                <td>Letzte 30 Tage</td>
                <td class="number">{data["last_30_days"]["opened"]}</td>
                <td class="number">{data["last_30_days"]["closed"]}</td>
                <td class="number">{data["last_30_days"]["still_open"]}</td>
            </tr>
        </table>

        <p class="summary-box">
            Aktuell offene Tickets:
            <strong>{data["current_open"]}</strong>
        </p>
        """
    
    def render_header(self, content, size):
        return f"<h{size}>{content}</h{size}>"
    
    def render_categories(self, categories):
        html = ""
        for name, data in categories.items():
            html += self.render_table(name, 3, data)

        return html
    
    def format_datetime(self, value):
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d.%m.%Y %H:%M")

    def render_periods(self, periods):
        week_from = self.format_datetime(periods["last_7_days"]["from"])
        week_to = self.format_datetime(periods["last_7_days"]["to"])

        month_from = self.format_datetime(periods["last_30_days"]["from"])
        month_to = self.format_datetime(periods["last_30_days"]["to"])

        return f"""
        {self.render_header("Berichtszeiträume", 2)}

        <table>
            <tr>
                <th>Zeitraum</th>
                <th>Von</th>
                <th>Bis</th>
            </tr>

            <tr>
                <td>Letzte 7 Tage</td>
                <td>{week_from}</td>
                <td>{week_to}</td>
            </tr>

            <tr>
                <td>Letzte 30 Tage</td>
                <td>{month_from}</td>
                <td>{month_to}</td>
            </tr>
        </table>
        """

    def render_css(self):
        return """
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #333333;
                font-size: 14px;
            }

            h1 {
                color: #1f4e79;
                font-size: 22px;
                margin-bottom: 12px;
            }

            h2, h3 {
                color: #2f75b5;
                border-bottom: 1px solid #dddddd;
                padding-bottom: 4px;
            }

            h2 {
                font-size: 16px;
                margin-top: 20px;
                margin-bottom: 8px;
            }

            h3 {
                font-size: 14px;
                margin-top: 14px;
                margin-bottom: 6px;
            }

            table {
                border-collapse: collapse;
                width: 100%;
                margin: 8px 0 16px;
                font-size: 13px;
            }

            th {
                background-color: #f2f2f2;
                text-align: left;
                padding: 4px 6px;
                border: 1px solid #ddd;
            }

            td {
                padding: 4px 6px;
                border: 1px solid #ddd;
            }

            .number {
                text-align: right;
            }

            .summary-box {
                margin-bottom: 20px;
            }
            .ai-summary {
                border-left: 4px solid #2f75b5;
                background: #f7f9fc;
                padding: 10px 12px;
                margin: 16px 0 20px;
            }
        </style>
        """
    
    def render_document(self, report_html: str, ai_summary_html: str = ""):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {self.render_css()}
        </head>

        <body>
            <h1>Supportbericht</h1>

            <div class="ai-summary">
                {ai_summary_html}
            </div>

            {report_html}
        </body>
        </html>
        """