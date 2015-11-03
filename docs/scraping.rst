Scraping
========

Scraping is an inheriently fragile process, and because it depends on an outside resource (in this case the Florida State Legislature's websites) it is the one most likely to break at some point.

This document assumes you can run the scraper locally, the process in :ref:`developing` will walk you through getting a basic environment set up to run the scraper locally.

pupa basics
-----------

``pupa update`` is the command used to run the scrapers

It takes a module name and a list of scrapers to run, each of which can have it's own keyword arguments.

For our purposes it will always be invoked as ``pupa update fl people`` or ``pupa update fl bills session=...``

Run ``pupa update --help`` for additional details.

Scraper Structure
-----------------

The scrapers in ``bills.py`` and ``people.py`` are composed of Page objects that return either a single piece of information or a list of similar information using XPath.

The pattern is something the author refers to as 'Spatula' and there's a decent summary in ``fl/base.py``.

Generally this makes it possible to swap out functionality when a page changes without affecting other parts of the scraper.

One other note about the general philosophy applied to the scrapers is that they use the tried & true "break early & break often" method.  The more "intelligent" a scraper tries to be against page changes, the more bad data sneaks into the system.  Given the relative importance of clean data for the purposes of trustworthiness, the scraper will more than likely bail if the page has changed substantially.  Often these are small one-line fixes, but this method prevents bad data from being exposed publicly.


When Things Change
------------------

When things inevitably do change on the sites being scraped, the process looks something like this:

* isolate the pages that have changed (hopefully just one or two types of pages)
  and modify the appropriate page subclasses.
* locally, run the modified scraper and watch the pupa output to see if there are 
  unexpected numbers of modified items.  (Ideally you can test against stable data
  and ensure 0 modified items.)
* use the :ref:`admin` to verify that any changes are desired/acceptable
* merge the scraper changes into production & redeploy to the server

New Sessions
------------

Updating the scraper for new sessions is a matter of looking at __init__.py and adding a new dictionary to ``legislative_sessions`` in the format of the others.

It is also necessary to modify the ``session_number`` dict in ``HousePage.do_request`` (found in ``bills.py``)  Look at the source of http://www.myfloridahouse.gov/Sections/Bills/bills.aspx to determine the appropriate value.
