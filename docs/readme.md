Core source record and categories
---------------------------------

Every row from the source `Entities` table is represented as an `atns:Entity`.
Rows with source CategoryID 1 are also represented as `schema:CreativeWork` and
soft-typed `catobjtyp:Agreement` using `schema:additionalType`. The corresponding
ATNS Agreement category concept is retained as source classification evidence.
This publication classification does not entail `odrl:Agreement`.

The following controlled category values are retained:

- Agreement — CategoryID 1
- Organisation — CategoryID 3
- Event — CategoryID 4
- Legislation — CategoryID 5
- Person/People — CategoryID 6
- Place — CategoryID 8
- Case Law — CategoryID 272
- Policy/Strategy — CategoryID 273

Published external classes such as `schema:Organization` may be asserted in
addition where the category-to-class mapping is clear.

Core tables
-----------

Entities
    EntityID
    EID
    Name
    CategoryID
    DateFrom
    DateTo
    Location
    Place
    State
    Country
    URL
    Summary
    References
    PreparedBy
    Public
    Deleted

ListElements
    ListElementID
    ListID
    Value
    Description

Refs
    RefID
    Type
    TypeID
    Author
    Year
    Title
    SecondaryAuthor
    SecondaryTitle
    PlacePublished
    Publisher
    Volume
    Number
    PageNos
    ISBN/ISSN
    Language
    PUBID
    DataSource
    Public
    Deleted

Entity_Refs
    Entity_RefID
    EntityID
    RefID
    Relationship


Observed relationships
----------------------

Agreement ----signatory--------> Organisation
Agreement ----respondent-------> Organisation
Agreement ----claimant---------> Person

Organisation --member----------> Person
Organisation --partner---------> Organisation
Organisation --formerlyKnownAs-> Organisation

Entity -------relatedReference-> Reference


Reference relationship types
----------------------------

Entity ----primaryReference----> Reference
Entity ----seeAlsoReference----> Reference


Lookup lists
------------

ListID 1  = Entity Categories
ListID 2  = Subject Matter
ListID 3  = Document Types
ListID 4  = Attachment Types
ListID 5  = Payment Types
ListID 6  = Subcategories
ListID 7  = Reference Types
ListID 8  = Countries
ListID 9  = Scale
ListID 10 = Link Types
ListID 11 = Binomial Names
ListID 12 = Relationship Types


Current modelling principle
---------------------------

Treat Entity as the fundamental record class.

Type records with Agreement CategoryID 1 as `schema:CreativeWork`, add
`schema:additionalType catobjtyp:Agreement`, and retain the source category
concept. Do not transform this hard or soft type into `odrl:Agreement`.

Model Reference as a separate first-class ATNS class and explicitly type each
instance as `schema:CreativeWork`; do not type references as `dcat:Resource`.

Keep author, publisher and preparedBy as literals initially.

Only introduce Document, Attachment, Author or Publisher classes once the XML evidence supports them.
