Use AdventureWorksENG

--we want to retrieve the names and surnames of customers from the Customer table
select FirstName, LastName 
from Person.Person

--: we want to print the names and surnames of the customers,
--but so that the result is sorted by customer last name:
select  FirstName, LastName 
from Person.Person
order by lastname

--: we want to print the name and surname
--the first 5 customers are sorted by customer last name:
select top 5 FirstName, LastName 
from Person.Person
order by lastname

--We want to print a list of customer names and surnames, so
--that they are sorted descendingly by last name
select FirstName, LastName 
from Person.Person
order by lastname desc

--We want to print only products that are black
select *
from Production.Product
where Color='black'

--we want to print all products that do not have a value entered in Color column
select *
from Production.Product
where Color is null


-- from the product table, print a list of all products
select *
from Production.Product

-- from the product table, list all colors (with and without repetition)
select Color
from Production.Product
where Color is not null

select distinct Color
from Production.Product
where Color is not null

-- print the list of product
--names and the corresponding minimum quantity in stock, in descending order
--(from the highest minimum quantity in stock to the lower ones)
select Name, ReorderPoint 
from Production.Product
order by ReorderPoint desc

-- print 15 product
--names with the smallest minimum quantity in stock.
select top 15 with ties Name, ReorderPoint 
from Production.Product
order by ReorderPoint 



-- from the product table, list all product names with
--a quantity less than 100
select Name, ReorderPoint
from Production.Product
where ReorderPoint<100

-- from the product table, list the product names,
--quantities and colors for which the quantity is a
--minimum of 300 and a maximum of 400, and the products are arranged by color descending.
select Name, ReorderPoint, Color
from Production.Product
where ReorderPoint>=300 and ReorderPoint<=400
order by Color desc

-- list all
--salesmen who are currently employed
select *
from HumanResources.Employee
where CurrentFlag=1

-- list all credit cards (recurring and non
--recurring) sorted by type
select *
from Sales.CreditCard
order by CardType

-- list all customers who have an
--CityID entered
select * 
from Sales.Customer
where StoreID is not null

-- list all city names
--and state ID’s , sorted from minor to major (A to Z), by city names and state province
--ID’s
select City, StateProvinceID
from Person.Address
order by City, StateProvinceID

-- list all city names (without repetition) located in
--Croatia ( StateID is equal to 1), sorted larger to smaller
--(from Z to A)
select distinct City, StateProvinceID
from Person.Address
where StateProvinceID=1
order by City desc
