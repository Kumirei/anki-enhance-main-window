from anki.lang import _
from anki.stats import *

from .config import getUserOption

# Associate each column to its title
defaultHeader = {**{
    "learning card": "Learning"+"<br/>"+"(card)",
    "learning later": "Learning"+"<br/>"+"later"+" ("+"review"+")",
    "learning now": "Learning"+"<br/>"+"now",
    "learning today": "Learning"+"<br/>"+"now"+"<br/>"+"and later",
    "learning all": "Learning"+"<br/>"+"now"+"<br/>("+"later today"+"<br/>("+"other day"+"))",
    "review due": "Due"+"<br/>"+"all",
    "due tomorrow": "Due"+"<br/>"+"tomorrow",
    "review today": "Due"+"<br/>"+"today",
    "review": "Due"+"<br/>"+"today"+" ("+"all"+")",
    "unseen": "Unseen"+"<br/>"+"all",
    "unseen later": "Unseen"+"<br/>"+"later",
    "review later": "review"+"<br/>"+"later",
    "reviewed today": "reviewed"+"<br/>"+"today",
    "reviewed today/repeated today": "reviewed"+"/"+"<br/>"+"repeated"+"<br/>"+"today",
    "repeated today": "repeated"+"<br/>"+"today",
    "repeated": "repeated",
    "new": "New"+"<br/>"+"today",
    "unseen new": "New"+"<br/>"+"("+"Unseen"+")",
    "buried": "Buried",
    "buried/suspended": "Buried"+"/<br/>"+"Suspended",
    "suspended": "Suspended",
    "cards": "Total",
    "notes/cards": "Total"+"/<br/>"+"Card/Note",
    "notes": "Total"+"<br/>"+"Note",
    "new today": "New"+"<br/>"+"Today",
    "today": "Today",
    "undue": "Undue",
    "mature": "Mature",
    "mature/young": "Mature"+"/<br/>"+"Young",
    "young": "Young",
    "marked": "Marked",
    "leech": "Leech",
    "bar": "Progress",
    "flags": "Flags",
    "all flags": "Flags",
    "today all": "Due",
    "due week": "Week",
    "due week avg": "W",
    "due month": "Month",
    "due month avg": "M",
    "due year": "Year",
    "due year avg": "Y",
    "days left": "Days Left",
    "expected daily": "Expected",
    "seen": "Seen"
}, **{f"flag {i}": "Flag"+" {i}" for i in range(5)}}


def getHeader(conf):
    """The header for the configuration in argument"""
    if "header" not in conf:
        return None
    header = conf["header"]
    if header is None:
        return defaultHeader[conf["name"]]
    return header


# Associate each column to its overlay
defaultOverlay = {**{
    "learning card": "Cards in learning"+"<br/>"+"""(either new cards you see again,"""+"<br/>"+"or cards which you have forgotten recently."+"<br/>"+"""Assuming those cards didn't graduated)""",
    "learning later": "Review which will happen later."+"<br/>"+"Either because a review happened recently,"+"<br/>"+"or because the card have many review left.",
    "learning now": "Cards in learning which are due now."+"<br/>"+"If there are no such cards,"+"<br/>"+"the time in minutes"+"<br/>"+"or seconds until another learning card is due",
    "learning today": "Cards in learning which are due now and then later.",
    "learning all": "Cards in learning which are due now"+"<br/>"+"(and in parenthesis, the number of reviews"+"<br/>"+"which are due later)",
    "review due": "Review cards which are due today"+"<br/>"+"(not counting the one in learning)",
    "due tomorrow": "Review cards which are due tomorrow"+"<br/>"+"(note: new cards and lapsed card seen today may increase this number.)",
    "review today": "Review cards you will see today",
    "review": "Review cards cards you will see today"+"<br/>"+"(and the ones you will not see today)",
    "unseen": "Cards that have never been answered",
    "unseen later": "Cards that have never been answered<br/>and you won't see today",
    "review later": "Cards that you must review,<br/>but can't review now",
    "reviewed today": "Number of time<br/>you did review a card from this deck.",
    "reviewed today/repeated today": "Number of cards and of review<br/>from this deck today.",
    "repeated today": "Number of time you saw a question<br/> from this deck today.",
    "repeated": "Number of time<br/>you saw a question from this deck.",
    "new": "Unseen" + "cards" + "you will see today"+"<br/>"+"(what anki calls "+"new cards",
    "unseen new": "Unseen cards you will see today"+"<br/>"+"(and those you will not see today)",
    "buried": "number of buried cards,"+"<br/>"+"(cards you decided not to see today)",
    "buried/suspended": "number of buried cards,"+"<br/>"+"(cards you decided not to see today)"+"number of suspended cards,"+"<br/>"+"(cards you will never see"+"<br/>"+"unless you unsuspend them in the browser)",
    "suspended": "number of suspended cards,"+"<br/>"+"(cards you will never see"+"<br/>"+"unless you unsuspend them in the browser)",
    "cards": "Number of cards in the deck",
    "notes/cards": "Number of cards/note in the deck",
    "notes": "Number of cards/note in the deck",
    "today": "Number of review you will see today"+"<br/>"+"(new, review and learning)",
    "undue": "Number of cards reviewed, not yet due",
    "mature/young": "Number of cards reviewed,"+"<br/>"+"with interval at least 3 weeks/"+"<br/>"+"less than 3 weeks",
    "mature": "Number of cards reviewed,"+"<br/>"+"with interval at least 3 weeks",
    "young": "Number of cards reviewed,"+"<br/>"+"with interval less than 3 weeks",
    "marked": "Number of marked note",
    "leech": "Number of note with a leech card",
    "new today": "Number of new cards you'll see today",
    "bar": None,  # It provides its own overlays,
    "flags": "Number of cards for each flag",
    "all flags": "Number of cards for each flag",
    "today all": "Reviews and lessons due today",
    "due week": "Total cards due this week",
    "due week avg": "Average daily cards due this week",
    "due month": "Total cards due this month",
    "due month avg": "Average daily cards due this month",
    "due year": "Total cards due this year",
    "due year avg": "Average daily cards due this year",
    "days left": "Number of days left until you finish the deck",
    "expected daily": "Expected daily reviews",
    "seen": "Cards reviewed at least once, not suspended"
}, **{f"flag {i}": f"Number of cards with flag {i}" for i in range(5)}}


def getOverlay(conf):
    """The overlay for the configuration in argument"""
    overlay = conf.get("overlay")
    if overlay is None:
        name = conf["name"]
        return defaultOverlay[name]
    return overlay


def getColor(conf):
    if "color" in conf and conf.get('color') is not None:
        return conf.get('color')
    name = conf.get('name', "")
    for word, color in [
            ("learning", colRelearn),
            ("unseen", colUnseen),
            ("new", colLearn),
            ("suspend", colSusp),
            ("young", colYoung),
            ("mature", colMature),
            ("buried", colSusp),
            ("repeated", colCum)
    ]:
        if word in name:
            return color
    return getUserOption("default column color", "grey")
