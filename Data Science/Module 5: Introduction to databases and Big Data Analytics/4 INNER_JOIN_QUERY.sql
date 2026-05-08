USE AdventureWorksENG;
-----------------------------------------------------------------
-- Print the invoice list (date, total amount, customer Name)
SELECT DISTINCT
	Invoice.InvoiceDate AS 'Invoice date',
	InvoiceItem.TotalPrice AS 'Total price',
	Customer.FirstName+' '+Customer.LastName AS 'Customer'
FROM Invoice
INNER JOIN Customer  ON Customer.IDCustomer  = Invoice.CustomerID
INNER JOIN InvoiceItem ON InvoiceItem.InvoiceID = Invoice.IDInvoice;
-----------------------------------------------------------------
-----------------------------------------------------------------
-- For a customer, list all the goods he bought.
SELECT DISTINCT
	Customer.FirstName+' '+Customer.LastName AS 'Customer',
	Product.Name AS 'Product'
FROM Invoice
INNER JOIN Customer    ON Customer.IDCustomer  = Invoice.CustomerID
INNER JOIN InvoiceItem   ON InvoiceItem.InvoiceID = Invoice.IDInvoice
INNER JOIN Product ON Product.IDProduct = InvoiceItem.ProductID
WHERE Customer.IDCustomer = 1;
-----------------------------------------------------------------
-----------------------------------------------------------------
-- For a customer, list all categories of goods he has ever ordered.
SELECT DISTINCT
	Customer.FirstName+' '+Customer.LastName as 'Customer',
	Subcategory.Name AS 'Category'
FROM Invoice
INNER JOIN Customer         ON Customer.IDCustomer  = Invoice.CustomerID
INNER JOIN InvoiceItem        ON InvoiceItem.InvoiceID = Invoice.IDInvoice
INNER JOIN Product      ON Product.IDProduct = InvoiceItem.ProductID
INNER JOIN Subcategory ON Product.SubcategoryID = Subcategory.IDSubcategory
WHERE Customer.IDCustomer = 1;
-----------------------------------------------------------------
-----------------------------------------------------------------
-- For a product, list all its subcategories and categories.
SELECT DISTINCT
	Product.Name AS 'Product Name',
	Category.Name AS 'Category',
	Subcategory.Name AS 'Subcategory'
FROM Product
INNER JOIN Subcategory ON Product.SubCategoryID = SubCategory.IDSubCategory
INNER JOIN Category    ON Subcategory.CategoryID = Category.IDCategory
WHERE Product.IDProduct = 771;
-----------------------------------------------------------------
