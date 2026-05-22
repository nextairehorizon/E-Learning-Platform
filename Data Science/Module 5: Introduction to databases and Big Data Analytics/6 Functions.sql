--Round the number 42.169994 to 3 decimal places
SELECT ROUND(42.1699944, 3)

--Calculate the second root of 169 and the square of number 42 (in one query) 
SELECT SQRT(169), SQUARE(42)

--Calculate what 2 is on the 10th.
SELECT POWER(2, 10)

--5. From the string ‘http://www.racunarstvo.hr’, select
--a) protocol (http)
--b) service (www)
--c) name (computer science)
--d) domain 
SELECT LEFT('http://www.racunarstvo.hr', 4) as Protocol,
	SUBSTRING('http://www.racunarstvo.hr', 8, 3) as Service,
	substring('http://www.racunarstvo.hr', 12, 11) as Name,
	Right('http://www.racunarstvo.hr', 2) as Domain

--Write the string ‘www.racunarstvo.hr’ in all uppercase and lowercase letters 
SELECT UPPER('www.racunarstvo.hr'), lower('www.racunarstvo.hr')

--Remove the unnecessary space from the string ‘ John goes into the woods ’
SELECT 
	'    John goes into the woods     ',
	LTRIM('    John goes into the woods     '),
	RTRIM('    John goes into the woods     '),
	TRIM('    John goes into the woods     ')
	


--9. From today's date, select:
--a) year
--b) month
--c) day
--d) week
SELECT DATEPART(year, GETDATE() ) 'Year',
	DATEPART(month, GETDATE() ) 'Month',
	DATEPART(day, GETDATE() ) 'Day',
	DATEPART(week, GETDATE() ) 'Week'

--10. Which date from today is for:
--a) 1282 days
--b) 11 years
--c) 37 months
SELECT 
	DATEADD(day, 1282, GETDATE() ),
	DATEADD(month, 37, GETDATE() ),
	DATEADD(year, 11, GETDATE() )

--How old are you days, months, years, minutes?
SELECT 
DATEDIFF(day, '19901016', GETDATE()) AS 'Difference in days',
DATEDIFF(month, '19901016', GETDATE() ) AS 'Difference in months',
DATEDIFF(year, '19901016', GETDATE() ) AS 'Difference in years',
DATEDIFF(minute, '19901016', GETDATE() ) AS 'Difference in minutes'





use AdventureWorksENG

--Print the total value of invoices issued in May 2004. 
select
sum(ii.TotalPrice)
from Invoice as i
inner join InvoiceItem as ii on ii.InvoiceID = i.IDInvoice
where year(i.InvoiceDate) = 2004
and month(i.InvoiceDate) = 5

--Print how many products do not have the color entered. 
select count(*) as NumberOfProductsWithoutColor
from Product
where Color is null

--Print the number of customers from each city, sorted by descending number of customers. 
select
City.Name,
COUNT(IDCustomer) AS NumberOfCustomers
from Customer
inner join City on City.IDCity = Customer.CityID
group by City.Name
order by NumberOfCustomers DESC



use AdventureWorksENG

--Return the number of all products.
select count(*) as TotalNumberOfProducts
from Product

--Return the number of products that have a defined color.
select count(*) as TotalNumberOfProductsWithColor
from Product as p
where p.Color is not null

--Return the highest price of the product.
select max(p.PriceWithoutVAT) as MaxProductPrice
from Product as p

--Return the average price of the product from subcategory 16.
select avg(p.PriceWithoutVAT) as AverageProductPrice
from Product as p
where p.SubcategoryID=16

--Return the dates of the oldest and most recent invoice issued to the customer 131.
select min(i.InvoiceDate) as OldestInvoice, max(i.InvoiceDate) as NewestInvoice
from Invoice as i
where i.CustomerID=131


use AdventureWorksENG

--List all the colors of the product and next to each write how many products have that color.
select p.Color, count(*) as NumberOfProductsOfThatColor
from Product as p
group by p.Color

--Change the previous query by sorting the descending order by product number.
select p.Color, count(*) as NumberOfProductsOfThatColor
from Product as p
group by p.Color
order by NumberOfProductsOfThatColor desc

--Change the previous query to turn off undefined color.
select p.Color, count(*) as NumberOfProductsOfThatColor
from Product as p
group by p.Color
having p.Color is not null

--List how many products of each color there are in each of the subcategories. Sort by subcategory
--and by color.
select sc.Name, p.Color, count(*) as NumberOfProductsOfThatColor
from Product as p
inner join Subcategory as sc
on p.SubcategoryID=sc.IDSubcategory
group by sc.Name, p.Color
order by sc.Name, p.Color

--Change the previous query to print the 10 categories and colors with the most products.
select top 10 p.SubcategoryID, p.Color, count(*) as NumberOfProductsOfThatColor
from Product as p
group by p.SubcategoryID, p.Color
order by NumberOfProductsOfThatColor desc

--Change the previous query by printing its subcategory name instead.
select top 10 sc.Name, p.Color, count(*) as NumberOfProductsOfThatColor
from Product as p
left join Subcategory as sc
on p.SubcategoryID=sc.IDSubcategory
group by sc.Name, p.Color
order by NumberOfProductsOfThatColor desc

--Write the names of all categories and write next to each how many subcategories there are.
select c.Name, count(sc.IDSubcategory) as NumberOfSubcategoriesInCategory
from Category as c
inner join Subcategory as sc
on sc.CategoryID=c.IDCategory
group by c.Name

--Write the names of all the categories and write next to each one how many products are in it.
select c.Name, count(p.IDProduct) as NumberOfProductsInCategory
from Category as c
inner join Subcategory as sc
on sc.CategoryID=c.IDCategory
inner join Product as p
on p.SubcategoryID=sc.IDSubcategory
group by c.Name

--List all different product prices and write how many products each price has.
select p.PriceWithoutVAT, count(*) as HowManyProductsWithThisPrice
from Product as p
group by p.PriceWithoutVAT
order by 1

--Print how many invoices were issued in which year.
select year(i.InvoiceDate) as InvoiceMonth, count(*) as HowManyInvoices
from Invoice as i
group by year(i.InvoiceDate)
order by 1

--Print the numbers of all invoices issued to the customer 377 and next to each print the total price
for all items.
select i.InvoiceNumber, sum(ii.TotalPrice) as TotalPricePerInvoice
from Invoice as i
inner join InvoiceItem as ii
on ii.InvoiceID=i.IDInvoice
where i.CustomerID=377
group by i.InvoiceNumber



use AdventureWorksENG

--List all colors that have more than 40 products.
select p.Color, count(*) as HowManyProducts
from Product as p
group by p.Color
having count(*)>40

--List the names of all subcategories that contain more than 10 products.
select sc.Name, count(*) as HowManyProducts
from Subcategory as sc
inner join Product as p on p.SubcategoryID=sc.IDSubcategory
group by sc.Name
having count(*)<10

--Print the total amounts earned and the number of copies sold for each of the products ever sold.
select p.Name, sum(ii.TotalPrice) as Income, sum(ii.Quantity) as QuantitySold
from Product as p
inner join InvoiceItem as ii
on ii.ProductID=p.IDProduct
group by p.Name

--Print the total amounts earned for each of the products sold in more than 2000 copies.
select p.Name, sum(ii.TotalPrice) as Income, sum(ii.Quantity) as QuantitySold
from Product as p
inner join InvoiceItem as ii
on ii.ProductID=p.IDProduct
group by p.Name
having sum(ii.Quantity)>2000

--Print the total amounts earned for each of the products that sold more than 2,000 copies or earned
more than $ 2,000,000.
select p.Name, sum(ii.TotalPrice) as Income, sum(ii.Quantity) as QuantitySold
from Product as p
inner join InvoiceItem as ii
on ii.ProductID=p.IDProduct
group by p.Name
having sum(ii.Quantity)>2000
or sum(ii.TotalPrice)>2000000
