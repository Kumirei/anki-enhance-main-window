from anki.utils import intTime
from aqt import mw
from math import ceil

from .consts import *
from .debug import debug

# Associate [column name][deck id name] to some value corresponding to
# the number of card of this deck in this column
values = dict()

def getAdditionalInfo():
    # Find all configs
    configs = mw.col.decks.all_config()
    confs = {}
    for conf in configs:
        confs[conf["id"]] = conf

    # Find out how many cards are left in each deck
    cardsLeft = {}
    query = f"select did, count(*) from cards where queue = {QUEUE_NEW_CRAM} group by did"
    results = mw.col.db.all(query)
    for did, value in results:
        cardsLeft[did] = value

    # Find out how many cards are due in each deck
    cutoff = intTime() + mw.col.get_config('collapseTime')
    due = {}
    query = f"select did, count(*) from cards where (queue in ({QUEUE_REV}, {QUEUE_DAY_LRN}) and due <= {mw.col.sched.today}) or (queue = {QUEUE_LRN} and due <= {cutoff}) group by did"
    results = mw.col.db.all(query)
    for did, value in results:
        due[did] = value

    # Find days left and reviews
    decksDaysLeft = {}
    decksDue = {}
    def recursiveFunction(node, maxNew, maxRev):
        deck = mw.col.decks.get(node.deck_id)
        conf = confs[deck["conf"]]
        deckMaxNew = conf["new"]["perDay"]
        deckMaxRev = conf["rev"]["perDay"]
        maxNew = min(maxNew, deckMaxNew)
        maxRev = min(maxRev, deckMaxRev)
        
        totalCardsLeft = 0 if not node.deck_id in cardsLeft else cardsLeft[node.deck_id]
        maxChildDaysLeft = 0
        totalDue = 0 if not node.deck_id in due else due[node.deck_id]
        for child in node.children:
            childCardsLeft, childDaysLeft, childDue = recursiveFunction(child, maxNew, maxRev)
            totalCardsLeft += childCardsLeft
            maxChildDaysLeft = max(maxChildDaysLeft, childDaysLeft)
            totalDue += childDue
        daysLeft = 0 if maxNew == 0 or maxNew > 9000 else ceil(totalCardsLeft / maxNew)
        daysLeft = max(daysLeft, maxChildDaysLeft)
        decksDaysLeft[node.deck_id] = daysLeft
        totalDue = totalDue if totalDue < maxRev else maxRev
        decksDue[node.deck_id] = totalDue
        return totalCardsLeft, daysLeft, totalDue
    
    root = mw.col.decks.deck_tree().children[0]
    recursiveFunction(root, 99999999999, 99999999999)
    
    return decksDaysLeft, decksDue


def computeValues():
    debug("Compute values")
    cutoff = intTime() + mw.col.get_config('collapseTime')
    today = mw.col.sched.today
    tomorrow = today+1
    yesterdayLimit = (mw.col.sched.dayCutoff-86400)*1000
    debug(f"Yesterday limit is {yesterdayLimit}")
    queriesCardCount = ([(f"flag {i}", f"(flags & 7) == {i}", "", "") for i in range(5)] +
                        [
        ("due tomorrow", f"queue in ({QUEUE_REV},{QUEUE_DAY_LRN}) and due = {tomorrow}", "", ""),
        ("learning now from today", f"queue = {QUEUE_LRN} and due <= {cutoff}", "", ""),
        ("learning today from past", f"queue = {QUEUE_DAY_LRN} and due <= {today}", "", ""),
        ("learning later today", f"queue = {QUEUE_LRN} and due > {cutoff}", "", ""),
        ("learning future", f"queue = {QUEUE_DAY_LRN} and due > {today}", "", ""),
        ("learning today repetition from today", f"queue = {QUEUE_LRN}", f"left/1000", ""),
        ("learning today repetition from past", f"queue = {QUEUE_DAY_LRN}", f"left/1000", ""),
        ("learning repetition from today", f"queue = {QUEUE_LRN}", f"mod%1000", ""),
        ("learning repetition from past", f"queue = {QUEUE_DAY_LRN}", f"mod%1000", ""),
        ("review due", f"queue = {QUEUE_REV} and due <= {today}", "", ""),
        ("reviewed today", f"queue = {QUEUE_REV} and due>0 and due-ivl = {today}", "", ""),
        ("repeated today", f"revlog.id>{yesterdayLimit}", "", "revlog inner join cards on revlog.cid = cards.id"),
        ("repeated", "", "", f"revlog inner join cards on revlog.cid = cards.id"),
        ("unseen", f"queue = {QUEUE_NEW_CRAM} and type <> {QUEUE_SUSPENDED}", "", ""),
        ("buried", f"queue = {QUEUE_USER_BURIED} or queue = {QUEUE_SCHED_BURIED}", "", ""),
        ("suspended", f"queue = {QUEUE_SUSPENDED}", "", ""),
        ("cards", "", "", ""),
        ("undue", f"queue = {QUEUE_REV} and due >  {today}", "", ""),
        ("mature", f"queue = {QUEUE_REV} and ivl >= 21", "", ""),
        ("young", f"queue = {QUEUE_REV} and 0<ivl and ivl <21", "", ""),
        ("today all", f"queue in ({QUEUE_REV}, {QUEUE_LRN}, {QUEUE_DAY_LRN}) and due <= {today}", "", ""),
        ("due week", f"queue in ({QUEUE_REV}, {QUEUE_DAY_LRN}) and due > {today} and due <= {today+7}", "", ""),
        ("due month", f"queue in ({QUEUE_REV}, {QUEUE_DAY_LRN}) and due > {today} and due <= {today+30}", "", ""),
        ("due year", f"queue in ({QUEUE_REV}, {QUEUE_DAY_LRN}) and due > {today} and due <= {today+365}", "", ""),
        ("due week avg", f"queue = {QUEUE_REV} and due > {today} and due <= {today+7}", "", ""),
        ("due month avg", f"queue = {QUEUE_REV} and due > {today} and due <= {today+30}", "", ""),
        ("due year avg", f"queue = {QUEUE_REV} and due > {today} and due <= {today+365}", "", ""),
        ("expected daily", f"queue = {QUEUE_REV} and due >= {today}", f"100000/(due-{today}+1)", ""),
        ("days left", "", "", ""),
        ("seen", f"queue <> {QUEUE_SUSPENDED} and type <> {QUEUE_NEW_CRAM}", "", ""),
        ("due limited", "", "", ""),
    ])

    decksDaysLeft, decksDue = getAdditionalInfo()

    for name, condition, addend, table in queriesCardCount:
        if addend:
            element = f" sum({addend})"
        else:
            element = f" count(*)"
        if condition:
            condition = f" where {condition}"
        if not table:
            table = "cards"
        if name == "days left":
            values[name] = decksDaysLeft
            continue
        if name == "due limited":
            values[name] = decksDue
            continue
        query = f"select did, {element} from {table} {condition} group by did"
        results = mw.col.db.all(query)
        debug("""For {name}: query "{query}".""")
        values[name] = dict()
        for did, value in results:
            if name == "due week avg":
                value = round(value/7)
            if name == "due month avg":
                value = round(value/30)
            if name == "due year avg":
                value = round(value/365)
            if name == "expected daily":
                value = round(value/100000)
            debug(f"In deck {did} there are {value} cards of kind {name}")
            values[name][did] = value


times = dict()


def computeTime():
    times.clear()
    for did, time in mw.col.db.all(f"select did,min(case when queue = {QUEUE_LRN} then due else null end) from cards group by did"):
        times[did] = time
