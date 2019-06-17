import re
import time

import click
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

WIKI_ROOT = 'https://en.wikipedia.org'
WIKI_URL = WIKI_ROOT + '/wiki/Special:Random'
REQUEST_TIMEOUT = 1
REQUEST_DELAY = 0.5

EARLY_STOPS = set(['Science', 'Geography', 'Knowledge', 'Fact', 'Switzerland',
                    'Country', 'Christianity', 'Language', 'Politics', 'Information', 'Physics', 'Continent'])

VALID_CHILDREN_TAGS = set(['p', 'ul', 'li'])


class InvalidResponse(Exception):
    def __init__(self, resp):
        self.message = "Request returned non-200: %s\n%s" % (resp.status_code, resp.text[:100])

def remove_parentheses(string):
    i = 0
    s = 0
    level = 0
    clean = ""
    while i < len(string):
        if string[i] == '(':
            level += 1
            if level == 1:
                # the parenthesis starts, so save up to this point
                clean += string[s:i]

        elif string[i] == ')':
            level -= 1
            # we got out of the top parenthesis level
            if level == 0:
                # start of the out-of-parenthesis string
                s = i+1

            if level < 0:
                print("Unexpected closing parenthesis, skipping...")
                level = 0
                clean += string[s:i]
                s = i+1

        i += 1

    clean += string[s:]

    if level != 0:
        print("Unbalanced parenthesis in text, removing the rest with regex")
        clean = re.sub(r"\(|\)", "", clean)

    return clean

def is_valid_content_child(tag):
    if type(tag) is not Tag:
        return False

    no_class = not tag.has_attr('class')
    no_style = not tag.has_attr('style')
    valid_tag = tag.name in VALID_CHILDREN_TAGS
    return no_class and no_style and valid_tag

def find_first_link(doc):
    main_text = doc.find(class_='mw-parser-output')
    if not main_text:
        title = doc.title.text.replace(" - Wikipedia", "")
        raise Exception("Could not find element 'mw-parser-output' with main text in %s" % title)

    return find_first_link_in_children(main_text)

def find_first_link_in_children(tag):

    for child in tag.children:
        if not is_valid_content_child(child):
            continue

        link = None
        if child.name == 'p':
            link = find_first_link_in_p(child)
        elif child.name == 'ul':
            # Articles (usually disambiguations) may have the first link in a list (ex: Lachheb)
            link = find_first_link_in_children(child)
        elif child.name == 'li':
            link = find_first_link_in_li(child)

        if link:
            return link

    return None

def find_first_link_in_p(p_tag):
    link = find_first_link_in_tag(p_tag)
    # Maybe it is within a <b> tag, thus it is not a direct child,
    # then we need to use another selector (ex: César Award for Best Film)
    return link or find_first_link_in_tag(p_tag, selector='p > b > a')

def find_first_link_in_li(li_tag):
    link = find_first_link_in_tag(li_tag)
    # Maybe it is within a <b> tag, thus it is not a direct child,
    # then we need to use another selector (ex: Portal:Amphibians and reptiles)
    return link or find_first_link_in_tag(li_tag, selector='li > b > a')

def find_first_link_in_tag(tag, selector=None):
    # It must be:
    # blue (not red)
    # not in a box
    # not in parentheses
    # not italic
    # not a footnote
    # not directing to wiktionary?

    # we may delete parenthesis that are in valid links, let's save them
    selector = selector or tag.name + ' > a'
    links_dict = {}
    for child in tag.select(selector):
        links_dict[remove_parentheses(str(child))] = child

    # get the html without parentheses, find the first link there and corroborate the link is
    # valid in the original html using the saved links
    clean_tag_html_str = remove_parentheses(str(tag))
    clean_tag = BeautifulSoup(clean_tag_html_str, 'html.parser')

    # it must be a direct child
    links = clean_tag.select(selector)
    if not links:
        return None

    for link in links:
        # red links
        class_ = link.get('class')
        if class_ and 'new' in class_:
            continue

        # wiktionary link
        if class_ and 'extiw' in class_:
            continue

        # link outside the main text
        if class_ and "external text" == " ".join(class_):
            continue

        # could be a link to a section within the article. (ex: Folk Music)
        if not link.get('title') or not link.get('href') or not "/wiki/" in link.get("href"):
            continue

        return links_dict[str(link)]

    # no links are outside of a parenthesis
    return None

def get_to_philosophy(url, request_delay=REQUEST_DELAY, request_timeout=REQUEST_TIMEOUT, early_stop=False):
    visited = set()
    path = []
    while True:
        resp = requests.get(url, timeout=request_timeout)
        if resp.status_code != requests.codes.ok:
            raise InvalidResponse(resp)

        doc = BeautifulSoup(resp.text, 'html.parser')
        title = doc.title.text.replace(" - Wikipedia", "")
        if title in visited:
            path.append("*Looped to %s*" % title)
            return path

        path.append(title)
        visited.add(title)
        print(title)
        first_link = find_first_link(doc)
        if not first_link:
            path.append("*Page without a valid first link found*")
            break

        uri = first_link['href']
        next_page_title = first_link['title']
        if next_page_title == 'Philosophy':
            path.append("Philosophy")
            break

        if early_stop and next_page_title in EARLY_STOPS:
            print("Landed on an early stop page, finishing.")
            path.append(next_page_title)
            break

        url = "%s%s" % (WIKI_ROOT, uri)
        time.sleep(request_delay)

    return path


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-u', '--url', 'url', type=str, default=WIKI_URL,
    help="URL to start the path to Philosophy.", show_default=True)

@click.option('--early-stop', 'early_stop', is_flag=True, type=bool, default=False,
    help="Stop if the next page is in EARLY_STOPS. Used for quicker debugging.", show_default=True)

@click.option('-d', '--request-delay', 'request_delay', type=float, default=REQUEST_DELAY,
    help="Seconds to wait until another request is done to Wikipedia.", show_default=True)

@click.option('-t', '--request-timeout', 'request_timeout', type=float, default=REQUEST_TIMEOUT,
    help="Maximum time in seconds allowed to wait for a response.", show_default=True)
def get_to_philosophy_command(url, request_delay, request_timeout, early_stop):
    """
    Script which attempts to find the path from a given Wikipedia article to the Philosophy Wikipedia article,
    by following the first link in the main text and repeating the process for subsequent articles.

    https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy

    It will only follow links that are blue and directing to a wiki article, not in parenthesis,
    not a footnote, not in a box and not italic.
    If any loops are detected, it will stop and attach the looping page at the end of the path.
    If it encounters an article without any valid links, it will stop and attach a message.
    """
    try:
        path = get_to_philosophy(url, request_delay, request_timeout, early_stop)
        print("Path:")
        print('\n'.join(path))
    except Exception as e:
        print("An error occurred: %s" % repr(e))
        exit(1)


if __name__ == '__main__':
    get_to_philosophy_command()
