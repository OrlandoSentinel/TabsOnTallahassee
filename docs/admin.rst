Using the Admin
===============

The Admin Site allows easier access to the database and also offers several useful utilities for ensuring data quality.

The admin allows superusers access to all objects in the system, but extreme caution should be used when modifying objects.

Administering Users
-------------------

Clicking the 'Users' link on the admin page will allow viewing/modifying users.

* To grant admin access: check the 'Staff status' and 'Superuser status' boxes on a user's page.
* To disable a user: uncheck the 'Active' box on a user's page.
* To change a user's password: click the link under the 'Password' information on a user's page.

Browsing Legislative Data
-------------------------

All of the legislative data collected by the scraper is browsable under the 'Open Civic Data' heading.  Most of these views are nearly 100% read-only as data should only be modified with extreme caution as the scraper will overwrite most changes.  These admin views are instead designed to be useful for reviewing data.

Bills
    bills and related information (actions, sponsorships, etc.)
Divisions
    boundaries
Jurisdictions
    top-level object representing Florida's state government
Organizations
    political parties and other relevant statewide organizations
People
    legislators and related information (contact details, etc.)
Posts
    definition of seats in the legislature
Vote Events
    votes taken within the legislature


Unresolved Legislators Tool
---------------------------

Legislators are quite commonly referred to in different ways across the official data sources.  A common example is having legislators referred to by last name only when they're bill sponsors or voting in committee.

While it is possible to automatically resolve legislators in many cases it is a common source of hard-to-diagnose data quality issues.  To avoid this, the system in place here is to not make assumptions and favor a quick manual reconciliation step.

The tool takes the form of a list of entities referred to in the system (as sponsors or voters) that are currently unresolved to legislators.  The list is prioritized by the number of times the name in question occurs.

.. note::
    Due to the nature of legislative data it is not possible to resolve 100% of the entities.  Occasionally non-legislator entities are listed as sponsors, and sometimes that upstream site (i.e. the FL legislature) does not provide enough information to disambiguate legislators.  In this case it is unfortunately the case that the legislator cannot be properly resolved.

Merge Tool
----------

From time to time a legislature will change the way they refer to a legislator.  For example, adding a nickname or perhaps the legislator's legal name has changed.

For example let's say that a legislator named William Smith is now known as Bill Smith.

In this case the scraper will assume that Bill Smith is a new legislator and create a duplicate entitiy in the system.  In this case, the solution is to navigate to the merge tool and select the two legislators.

After selecting the legislators a long list of the data that'll be modified will be shown.  This should be reviewed carefully as the change is irreversible.

Once the data to be merged has been reviewed, the merge can be confirmed and the entities will be updated as shown in the merge plan.

Pupa Runlog
-----------

View a list of scraper runs.

Runs are either marked as successes or failures.  If a run is a success it will have details such as how many objects it created/updated and if a run fails it will have an exception traceback showing what failed.  In the case of repeated failures it is typically necessary to make modifications to the scraper as it is likely the site structure has changed.

Glossary
--------

Edit terms that are highlighed on the site & listed on the glossary page.

Preferences
-----------

View & modify user preferences such as tracked information & location.

