"""Flask application for a minimalist, Markdown-based blog.

Articles live as folders under posts/<slug>/, each with an index.md file
(Markdown + YAML frontmatter) and an optional imgs/ subfolder. Standalone
pages (e.g. an "About" page) follow the same pattern under pages/<slug>/,
served at the site root (/<slug>) instead of under /post/. There is no
database: everything is read from disk on each request.
"""

import math
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import frontmatter
import markdown
from flask import Flask, Response, abort, render_template, request, send_from_directory, url_for

app = Flask(__name__)
# Reload Jinja templates from disk on every request, independent of the
# Werkzeug debugger (which stays off unless FLASK_DEBUG=1, see bottom of file).
app.config["TEMPLATES_AUTO_RELOAD"] = True

POSTS_DIR = Path(__file__).parent / "posts"
PAGES_DIR = Path(__file__).parent / "pages"
SITE_NAME = "Journal"
SITE_TAGLINE = "Notes sur le design, le code et les idées."
POSTS_PER_PAGE = 6

# Single reusable Markdown converter (reset before each use, see get_post).
md = markdown.Markdown(extensions=["fenced_code", "codehilite", "tables", "extra"])

MONTHS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


@app.template_filter("french_date")
def french_date(value):
    """Format a date as "D month YYYY" in French (e.g. "3 juillet 2026").

    Avoids relying on the system locale for month names, since Python's
    strftime('%B') requires a French locale to be installed on the host.
    """
    return f"{value.day} {MONTHS_FR[value.month - 1]} {value.year}"


def _words_per_minute(text: str) -> int:
    """Estimate reading time in minutes, at 200 words per minute, minimum 1."""
    words = len(text.split())
    return max(1, round(words / 200))


def slugify(value: str) -> str:
    """Turn an arbitrary string (e.g. a category name) into a URL-safe slug."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def _relative_to_imgs(path: str) -> str:
    """Normalize an author-provided image path to be relative to a post's imgs/ folder.

    Authors may write either "imgs/photo.jpg" (mirroring the folder they see
    on disk) or just "photo.jpg". Both must resolve to the same served URL,
    so a leading "imgs/" (or "/") is stripped here before building the route.
    """
    path = path.lstrip("/")
    return path[len("imgs/") :] if path.startswith("imgs/") else path


def _resolve_image_field(image, endpoint, slug):
    """Resolve a frontmatter `image` value to an absolute URL, or None if unset.

    Absolute URLs are returned as-is; relative ones are served through the
    given imgs-serving endpoint ("post_image" or "page_image") so each
    article/page's assets stay inside its own folder rather than static/.
    """
    if not image:
        return None
    if image.startswith("http"):
        return image
    return url_for(endpoint, slug=slug, filename=_relative_to_imgs(image), _external=True)


def load_posts():
    """Read every article from posts/<slug>/index.md into a list of dicts.

    Returns posts sorted by date, most recent first. Each dict merges the
    YAML frontmatter with a few derived fields (slug, category_slug, reading
    time, resolved image URL) consumed directly by the templates.
    """
    posts = []
    for folder in POSTS_DIR.iterdir():
        md_path = folder / "index.md"
        if not folder.is_dir() or not md_path.exists():
            continue
        post = frontmatter.load(md_path)
        slug = post.get("slug") or folder.name
        date = post.get("date")
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        category = post.get("category", "Général")
        summary = post.get("summary", "")
        posts.append(
            {
                "slug": slug,
                "title": post.get("title", slug),
                "summary": summary,
                "date": date,
                "year": date.year,
                "category": category,
                "category_slug": slugify(category),
                "content": post.content,
                "reading_time": _words_per_minute(post.content),
                "meta_description": post.get("meta_description") or summary,
                "keywords": post.get("keywords", ""),
                "image": _resolve_image_field(post.get("image"), "post_image", slug),
            }
        )
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def load_pages():
    """Read every standalone page from pages/<slug>/index.md into a list of dicts.

    Unlike posts, pages have no date/category/reading time — they're for
    static content (e.g. "About") rather than chronological articles.
    """
    if not PAGES_DIR.exists():
        return []
    pages = []
    for folder in PAGES_DIR.iterdir():
        md_path = folder / "index.md"
        if not folder.is_dir() or not md_path.exists():
            continue
        page = frontmatter.load(md_path)
        slug = page.get("slug") or folder.name
        pages.append(
            {
                "slug": slug,
                "title": page.get("title", slug),
                "content": page.content,
                "meta_description": page.get("meta_description", ""),
                "keywords": page.get("keywords", ""),
                "image": _resolve_image_field(page.get("image"), "page_image", slug),
            }
        )
    return pages


# Matches a whole <img ...> tag, then a src="..." attribute within it, so
# image paths written in Markdown can be rewritten to the post_image/page_image route.
IMG_TAG_RE = re.compile(r"<img\s[^>]*>")
SRC_ATTR_RE = re.compile(r'src="([^"]+)"')


def _resolve_content_images(html, endpoint, slug):
    """Rewrite relative <img src="..."> paths in rendered HTML to an imgs-serving route.

    Absolute URLs (http/https) and root-relative paths ("/...") are left
    untouched, since those are assumed to already point somewhere valid.
    """

    def rewrite_tag(tag_match):
        def rewrite_src(src_match):
            path = src_match.group(1)
            if path.startswith(("http://", "https://", "/")):
                return src_match.group(0)
            filename = _relative_to_imgs(path)
            return f'src="{url_for(endpoint, slug=slug, filename=filename)}"'

        return SRC_ATTR_RE.sub(rewrite_src, tag_match.group(0))

    return IMG_TAG_RE.sub(rewrite_tag, html)


def get_post(slug):
    """Return a single post dict (with rendered HTML) for the given slug, or None."""
    for post in load_posts():
        if post["slug"] == slug:
            html = md.reset().convert(post["content"])
            post["html"] = _resolve_content_images(html, "post_image", slug)
            return post
    return None


def get_page(slug):
    """Return a single standalone page dict (with rendered HTML), or None."""
    for page in load_pages():
        if page["slug"] == slug:
            html = md.reset().convert(page["content"])
            page["html"] = _resolve_content_images(html, "page_image", slug)
            return page
    return None


def paginate(posts, page):
    """Slice a list of posts into one page, clamping page to a valid range.

    Returns (posts_for_this_page, clamped_page_number, total_pages).
    """
    total_pages = max(1, math.ceil(len(posts) / POSTS_PER_PAGE))
    page = max(1, min(page, total_pages))
    start = (page - 1) * POSTS_PER_PAGE
    return posts[start : start + POSTS_PER_PAGE], page, total_pages


def get_categories():
    """Return every category in use, with its slug and article count, sorted by name."""
    counts = {}
    for post in load_posts():
        entry = counts.setdefault(
            post["category"], {"name": post["category"], "slug": post["category_slug"], "count": 0}
        )
        entry["count"] += 1
    return sorted(counts.values(), key=lambda c: c["name"])


@app.context_processor
def inject_site():
    """Make site-wide constants available in every template without passing them explicitly."""
    return {"site_name": SITE_NAME, "site_tagline": SITE_TAGLINE}


@app.route("/")
def index():
    """Homepage: paginated list of all articles, grouped by year in the template."""
    all_posts = load_posts()
    categories = get_categories()
    page = request.args.get("page", 1, type=int)
    posts, page, total_pages = paginate(all_posts, page)
    # Keep paginated URLs (page=2, etc.) out of the canonical URL for page 1,
    # so /?page=1 and / aren't treated as separate pages by search engines.
    page_kwargs = {"page": page} if page > 1 else {}
    return render_template(
        "index.html",
        posts=posts,
        categories=categories,
        active_category=None,
        page=page,
        total_pages=total_pages,
        pagination_endpoint="index",
        pagination_kwargs={},
        meta_description=SITE_TAGLINE,
        canonical_url=url_for("index", _external=True, **page_kwargs),
    )


@app.route("/categorie/<slug>")
def category(slug):
    """Paginated list of articles filtered to a single category."""
    all_posts = [p for p in load_posts() if p["category_slug"] == slug]
    if not all_posts:
        abort(404)
    categories = get_categories()
    page = request.args.get("page", 1, type=int)
    posts, page, total_pages = paginate(all_posts, page)
    category_name = all_posts[0]["category"]
    page_kwargs = {"page": page} if page > 1 else {}
    return render_template(
        "index.html",
        posts=posts,
        categories=categories,
        active_category=slug,
        category_name=category_name,
        page=page,
        total_pages=total_pages,
        pagination_endpoint="category",
        pagination_kwargs={"slug": slug},
        meta_description=f"Articles classés dans la catégorie {category_name}.",
        canonical_url=url_for("category", slug=slug, _external=True, **page_kwargs),
    )


@app.route("/post/<slug>/imgs/<path:filename>")
def post_image(slug, filename):
    """Serve an image from a single post's imgs/ folder.

    The resolved directory is checked against POSTS_DIR to reject any slug
    that tries to escape the posts/ tree (e.g. via ".." segments), before
    handing off to send_from_directory (which itself guards `filename`).
    """
    directory = (POSTS_DIR / slug / "imgs").resolve()
    if POSTS_DIR.resolve() not in directory.parents:
        abort(404)
    return send_from_directory(directory, filename)


@app.route("/post/<slug>")
def post(slug):
    """Article page: rendered content, SEO metadata, and schema.org JSON-LD."""
    post = get_post(slug)
    if post is None:
        abort(404)
    canonical_url = url_for("post", slug=slug, _external=True)
    structured_data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["meta_description"],
        "datePublished": post["date"].isoformat(),
        "mainEntityOfPage": canonical_url,
        "author": {"@type": "Person", "name": SITE_NAME},
    }
    if post["image"]:
        structured_data["image"] = post["image"]
    return render_template(
        "post.html",
        post=post,
        canonical_url=canonical_url,
        structured_data=structured_data,
        meta_description=post["meta_description"],
    )


@app.route("/sitemap.xml")
def sitemap():
    """XML sitemap listing the homepage, every category, article, and standalone page."""
    all_posts = load_posts()
    urls = [{"loc": url_for("index", _external=True), "lastmod": None}]
    urls += [
        {"loc": url_for("category", slug=cat["slug"], _external=True), "lastmod": None}
        for cat in get_categories()
    ]
    urls += [
        {"loc": url_for("post", slug=p["slug"], _external=True), "lastmod": p["date"].isoformat()}
        for p in all_posts
    ]
    urls += [
        {"loc": url_for("page", slug=p["slug"], _external=True), "lastmod": None}
        for p in load_pages()
    ]
    xml = render_template("sitemap.xml", pages=urls)
    return Response(xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    """Plain-text robots.txt allowing all crawlers and pointing to the sitemap."""
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {url_for('sitemap', _external=True)}",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


@app.route("/<slug>/imgs/<path:filename>")
def page_image(slug, filename):
    """Serve an image from a single standalone page's imgs/ folder.

    Same path-traversal guard as post_image, scoped to PAGES_DIR instead.
    """
    directory = (PAGES_DIR / slug / "imgs").resolve()
    if PAGES_DIR.resolve() not in directory.parents:
        abort(404)
    return send_from_directory(directory, filename)


@app.route("/<slug>")
def page(slug):
    """Standalone page (e.g. /about): rendered content and SEO metadata.

    Registered last and matched only if no more specific rule applies —
    Werkzeug always prefers a literal/static route (like /sitemap.xml or
    /post/<slug>) over this single-segment catch-all, regardless of
    definition order, so this can't shadow the routes above it.
    """
    page = get_page(slug)
    if page is None:
        abort(404)
    return render_template(
        "page.html",
        page=page,
        canonical_url=url_for("page", slug=slug, _external=True),
        meta_description=page["meta_description"] or SITE_TAGLINE,
    )


@app.errorhandler(404)
def not_found(_error):
    """Render a branded 404 page instead of Flask's default error page."""
    return render_template("404.html"), 404


if __name__ == "__main__":
    import os

    # The interactive debugger allows arbitrary code execution when reachable,
    # so it's opt-in only (FLASK_DEBUG=1) rather than the default.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=int(os.environ.get("PORT", 5000)))
