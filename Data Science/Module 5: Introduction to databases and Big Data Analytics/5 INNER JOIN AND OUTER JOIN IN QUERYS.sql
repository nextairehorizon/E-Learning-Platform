use AdventureWorksENG
-- 
-- Use the left outer to retrieve the names of all customers who have not purchased anything.
select c.Firstname, c.Lastname, i.IDInvoice 
from Customer as c
left outer join Invoice as i
on i.CustomerID=c.IDCustomer
where i.IDInvoice is null

-- 
-- Using the right outer join to retrieve the names of all customers who have not purchased anything.
select c.Firstname, c.Lastname, i.IDInvoice 
from Invoice as i
right outer join Customer as c
on i.CustomerID=c.IDCustomer
where i.IDInvoice is null

-- 
-- Using full outer join, print country and city names.
select c.Name as City, s.Name as State
from State as s
full outer join City as c
on s.IDState=c.StateID

-- 
-- Insert the country of India and the city of London, without stating which country it belongs to. 
-- Using full outer join, print country and city names. Print only those cities that do not have a defined state and those countries that do not have registered cities.
insert into City(Name)
values ('London')

insert into State(Name)
values ('India')

select c.Name as City, s.Name as State
from State as s
full outer join City as c
on s.IDState=c.StateID
where s.Name is null
or c.Name is null


-- 

-- 
-- List all customers who bought products (name, surname, order date and total sales amount)
SELECT DISTINCT
	Customer.FirstName,
	Customer.LastName,
	Invoice.InvoiceDate AS 'Invoice date',
	InvoiceItem.TotalPrice AS 'Total price'
FROM Invoice
INNER JOIN Customer  ON Customer.IDCustomer  = Invoice.CustomerID
INNER JOIN InvoiceItem ON InvoiceItem.InvoiceID = Invoice.IDInvoice;

-- 
-- List all products sold on an invoice.
SELECT
	Product.*
FROM Invoice
INNER JOIN InvoiceItem   ON InvoiceItem.InvoiceID = Invoice.IDInvoice
INNER JOIN Product ON Product.IDProduct = InvoiceItem.ProductID
WHERE Invoice.IDInvoice = 43659;

-- 
-- List all products sold in one invoice and write in which category and subcategory each product belongs.
SELECT
	Product.*,
	Category.Name AS 'Category',
	SubCategory.Name AS 'SubCategory'
FROM Invoice
INNER JOIN InvoiceItem   ON InvoiceItem.InvoiceID = Invoice.IDInvoice
INNER JOIN Product ON Product.IDProduct = InvoiceItem.ProductID
LEFT OUTER JOIN SubCategory ON Product.SubCategoryID = SubCategory.IDSubCategory
LEFT OUTER JOIN Category    ON Subcategory.CategoryID = Category.IDCategory
WHERE Invoice.IDInvoice = 43659;

-- 
-- Print a list of models arranged by category (for each product print the corresponding subcategory and category to which it belongs).
SELECT
	Product.*,
	Category.Name as Category,
	SubCategory.Name as SubCategory
FROM Product
LEFT OUTER JOIN SubCategory ON Product.SubCategoryID = SubCategory.IDSubCategory
LEFT OUTER JOIN Category    ON SubCategory.CategoryID = Category.IDCategory;

-- 
-- Print a list of product categories sold there for each country to which an invoice went.
SELECT DISTINCT
	State.Name AS 'State',
	Category.Name AS 'Product Category'
FROM Customer
INNER JOIN City ON Customer.CityID = City.IDCity
INNER JOIN State ON City.StateID = State.IDState
INNER JOIN Invoice    ON Customer.IDCustomer  = Invoice.CustomerID
INNER JOIN InvoiceItem   ON InvoiceItem.InvoiceID = Invoice.IDInvoice
INNER JOIN Product ON Product.IDProduct = InvoiceItem.ProductID
LEFT OUTER JOIN SubCategory ON Product.SubCategoryID = SubCategory.IDSubcategory
LEFT OUTER JOIN Category ON Subcategory.CategoryID = Category.IDCategory
order by 1

-- 
-- Print a list of customers and the corresponding subcategories of products they bought.
SELECT DISTINCT
	Customer.FirstName + ' ' + Customer.LastName AS 'Customer',
	SubCategory.Name AS 'Subcategory'
FROM Invoice
INNER JOIN Customer    ON Customer.IDCustomer  = Invoice.CustomerID
INNER JOIN InvoiceItem   ON InvoiceItem.InvoiceID = Invoice.IDInvoice
INNER JOIN Product ON Product.IDProduct = InvoiceItem.ProductID
LEFT OUTER JOIN SubCategory ON Product.SubCategoryID = SubCategory.IDSubCategory
order by 1
