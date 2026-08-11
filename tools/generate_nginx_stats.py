#!/usr/bin/env python3
import argparse
import html
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import unquote, urlsplit


LOG_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+) '
    r'"(?P<referer>[^"]*)" "(?P<ua>[^"]*)"'
)

TIME_FORMAT = '%d/%b/%Y:%H:%M:%S %z'
ASSET_EXTENSIONS = (
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.webp', '.avif', '.woff', '.woff2', '.ttf', '.map'
)


def parse_args():
    parser = argparse.ArgumentParser(description='Generate a private static traffic report from an Nginx access log.')
    parser.add_argument('--log', required=True, help='Nginx access log path')
    parser.add_argument('--output-dir', required=True, help='Directory to write index.html into')
    parser.add_argument('--site-name', default='LadderHelper', help='Site name shown in the report')
    parser.add_argument('--days', type=int, default=30, help='Only include recent N days')
    parser.add_argument('--top', type=int, default=20, help='Top rows per table')
    return parser.parse_args()


def is_page_view(path):
    clean_path = urlsplit(path).path
    if clean_path.startswith('/assets/'):
        return False
    if clean_path.endswith(ASSET_EXTENSIONS):
        return False
    if clean_path in ('/favicon.ico', '/robots.txt'):
        return False
    return True


def normalize_path(path):
    clean_path = urlsplit(path).path or '/'
    try:
        clean_path = unquote(clean_path)
    except UnicodeDecodeError:
        pass
    if clean_path.endswith('/index.html'):
        clean_path = clean_path[:-10] or '/'
    if clean_path.endswith('.html'):
        clean_path = clean_path[:-5]
    return clean_path


def parse_log(log_path, days):
    now = datetime.now().astimezone()
    cutoff = now - timedelta(days=days)
    records = []

    with Path(log_path).open('r', encoding='utf-8', errors='replace') as handle:
        for line in handle:
            match = LOG_RE.match(line.strip())
            if not match:
                continue

            data = match.groupdict()
            try:
                seen_at = datetime.strptime(data['time'], TIME_FORMAT)
            except ValueError:
                continue

            if seen_at < cutoff:
                continue

            path = data['path']
            if not is_page_view(path):
                continue

            status = int(data['status'])
            if status >= 500:
                continue

            records.append({
                'ip': data['ip'],
                'time': seen_at,
                'date': seen_at.date().isoformat(),
                'method': data['method'],
                'path': normalize_path(path),
                'status': status,
                'referer': data['referer'],
                'ua': data['ua'],
            })

    return records, now


def summarize(records, now, top):
    today = now.date().isoformat()
    yesterday = (now - timedelta(days=1)).date().isoformat()
    last_7_cutoff = now - timedelta(days=7)

    today_records = [item for item in records if item['date'] == today]
    yesterday_records = [item for item in records if item['date'] == yesterday]
    last_7_records = [item for item in records if item['time'] >= last_7_cutoff]

    by_day = Counter(item['date'] for item in records)
    by_page = Counter(item['path'] for item in records)
    by_status = Counter(str(item['status']) for item in records)
    by_referer = Counter(item['referer'] for item in records if item['referer'] and item['referer'] != '-')

    ip_stats = defaultdict(lambda: {
        'views': 0,
        'pages': Counter(),
        'first': None,
        'last': None,
        'ua': Counter(),
    })
    for item in records:
        stat = ip_stats[item['ip']]
        stat['views'] += 1
        stat['pages'][item['path']] += 1
        stat['ua'][item['ua']] += 1
        stat['first'] = item['time'] if stat['first'] is None else min(stat['first'], item['time'])
        stat['last'] = item['time'] if stat['last'] is None else max(stat['last'], item['time'])

    top_ips = []
    for ip, stat in ip_stats.items():
        top_ips.append({
            'ip': ip,
            'views': stat['views'],
            'pages': len(stat['pages']),
            'first': stat['first'],
            'last': stat['last'],
            'ua': stat['ua'].most_common(1)[0][0] if stat['ua'] else '',
        })
    top_ips.sort(key=lambda row: row['views'], reverse=True)

    return {
        'page_views': len(records),
        'unique_ips': len({item['ip'] for item in records}),
        'today_views': len(today_records),
        'today_ips': len({item['ip'] for item in today_records}),
        'yesterday_views': len(yesterday_records),
        'last_7_views': len(last_7_records),
        'last_7_ips': len({item['ip'] for item in last_7_records}),
        'by_day': by_day.most_common(top),
        'by_page': by_page.most_common(top),
        'by_status': by_status.most_common(top),
        'by_referer': by_referer.most_common(top),
        'top_ips': top_ips[:top],
    }


def esc(value):
    return html.escape(str(value), quote=True)


def fmt_time(value):
    if value is None:
        return '-'
    return value.strftime('%Y-%m-%d %H:%M:%S %z')


def table(headers, rows):
    head = ''.join(f'<th>{esc(item)}</th>' for item in headers)
    body = []
    for row in rows:
        body.append('<tr>' + ''.join(f'<td>{item}</td>' for item in row) + '</tr>')
    if not body:
        body.append(f'<tr><td colspan="{len(headers)}" class="empty">暂无数据</td></tr>')
    return f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def render(site_name, records, summary, now, days):
    day_rows = [
        [esc(day), esc(count), esc(len({item['ip'] for item in records if item['date'] == day}))]
        for day, count in summary['by_day']
    ]
    page_rows = [[esc(path), esc(count)] for path, count in summary['by_page']]
    status_rows = [[esc(status), esc(count)] for status, count in summary['by_status']]
    referer_rows = [[esc(referer), esc(count)] for referer, count in summary['by_referer']]
    ip_rows = [
        [
            esc(row['ip']),
            esc(row['views']),
            esc(row['pages']),
            esc(fmt_time(row['first'])),
            esc(fmt_time(row['last'])),
            esc(row['ua'][:160]),
        ]
        for row in summary['top_ips']
    ]

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>{esc(site_name)} 访问统计</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f8fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #667085;
      --line: #e4e7ec;
      --blue: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 32px auto 56px;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-end;
      margin-bottom: 20px;
    }}
    h1 {{ margin: 0 0 6px; font-size: 30px; }}
    h2 {{ margin: 0 0 14px; font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    .updated {{ text-align: right; font-size: 14px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }}
    .card, section {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: 0 8px 24px rgba(16, 24, 40, .04);
    }}
    .card {{ padding: 18px; }}
    .label {{ color: var(--muted); font-size: 14px; }}
    .value {{ margin-top: 6px; font-size: 30px; font-weight: 750; color: var(--blue); }}
    section {{ padding: 20px; margin-top: 16px; overflow: hidden; }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      word-break: break-word;
    }}
    th {{
      color: #344054;
      background: #f8fafc;
      font-weight: 700;
    }}
    .empty {{ color: var(--muted); text-align: center; }}
    .note {{
      margin-top: 16px;
      padding: 12px 14px;
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      background: #eff6ff;
      color: #1e3a8a;
      font-size: 14px;
    }}
    @media (max-width: 860px) {{
      header {{ display: block; }}
      .updated {{ text-align: left; margin-top: 10px; }}
      .cards, .grid {{ grid-template-columns: 1fr; }}
      main {{ width: min(100% - 20px, 1180px); margin-top: 20px; }}
      table {{ font-size: 13px; }}
      th, td {{ padding: 8px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>{esc(site_name)} 访问统计</h1>
        <p>基于服务器访问日志生成，统计最近 {esc(days)} 天的页面访问。</p>
      </div>
      <p class="updated">更新时间<br>{esc(fmt_time(now))}</p>
    </header>

    <div class="cards">
      <div class="card"><div class="label">总访问次数</div><div class="value">{esc(summary['page_views'])}</div></div>
      <div class="card"><div class="label">独立 IP</div><div class="value">{esc(summary['unique_ips'])}</div></div>
      <div class="card"><div class="label">今日访问 / IP</div><div class="value">{esc(summary['today_views'])} / {esc(summary['today_ips'])}</div></div>
      <div class="card"><div class="label">最近 7 天访问 / IP</div><div class="value">{esc(summary['last_7_views'])} / {esc(summary['last_7_ips'])}</div></div>
    </div>

    <section>
      <h2>访问 IP 排行</h2>
      {table(['IP', '访问次数', '访问页面数', '首次访问', '最近访问', '主要浏览器'], ip_rows)}
      <div class="note">这里展示的是原始访问 IP。请只用于自己的网站运维和排错，不建议截图公开。</div>
    </section>

    <div class="grid">
      <section>
        <h2>每日访问</h2>
        {table(['日期', '访问次数', '独立 IP'], day_rows)}
      </section>
      <section>
        <h2>热门页面</h2>
        {table(['页面', '访问次数'], page_rows)}
      </section>
    </div>

    <div class="grid">
      <section>
        <h2>来源页面</h2>
        {table(['来源', '次数'], referer_rows)}
      </section>
      <section>
        <h2>状态码</h2>
        {table(['状态码', '次数'], status_rows)}
      </section>
    </div>
  </main>
</body>
</html>
'''


def main():
    args = parse_args()
    records, now = parse_log(args.log, args.days)
    summary = summarize(records, now, args.top)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'index.html').write_text(
        render(args.site_name, records, summary, now, args.days),
        encoding='utf-8'
    )


if __name__ == '__main__':
    main()
