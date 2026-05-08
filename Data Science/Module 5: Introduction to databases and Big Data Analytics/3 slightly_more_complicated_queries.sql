USE AdventureWorksENG;

-----------------------------------------------------------------
-- Select all customers from the Customer table whose name does not end with the letter ‘a’. 
SELECT * FROM Customer;
SELECT * FROM Customer WHERE LastName NOT LIKE '%a';
-----------------------------------------------------------------
-----------------------------------------------------------------
-- Select all customers whose last name starts with ‘Van’. 
SELECT * FROM Customer;
SELECT * FROM Customer WHERE LastName LIKE 'Van%';
-----------------------------------------------------------------
-----------------------------------------------------------------
-- Add the ‘third’ suffix to customer Vargas Gary. 
SELECT * FROM Customer WHERE FirstName='Gary' AND LastName='Vargas';
SELECT * FROM Customer WHERE IDCustomer = 892;
UPDATE Customer
	SET LastName = LastName + ' third' 
	WHERE IDCustomer = 892;
SELECT * FROM Customer WHERE IDCustomer = 892;
-----------------------------------------------------------------
-----------------------------------------------------------------
-- Select all customers named Ana or Tamara from Osijek.
SELECT * FROM City
WHERE Name='Osijek'

SELECT * FROM Customer
WHERE (FirstName='ana' or FirstName='tamara') AND CityID=2

-- Select all customers whose last name starts with the letter "D" and the last name contains the string "re".
SELECT * FROM Customer
WHERE LastName LIKE 'D%re%'

-- Select only the last names of half of the first persons called "Jack".
SELECT TOP 50 PERCENT LastName
FROM Customer
WHERE FirstName='Jack'

-----------------------------------------------------------------
-- For all customers who do not have a suffix entered, change (add) it as the string ‘no suffix 
SELECT * FROM Customer WHERE LastName NOT LIKE '% %';

SELECT * FROM Customer WHERE LastName NOT LIKE '% %';
UPDATE Customer
	SET LastName = LastName + ' nema' 
	WHERE LastName NOT LIKE '% %';
SELECT * FROM Customer WHERE LastName LIKE '% nema';
-----------------------------------------------------------------
--Select all customers whose last name contains an apostrophe sign
select * from Customer
where LastName like '%''%'
-----------------------------------------------------------------
--Select all products for which the ProductNumber data contains a percentage sign (%). If there are no
--such products, change the ‘Adjustable Race’ product number to ‘AR% 5381’. 
update Product
set ProductNumber='AR%5381'
where Name='Adjustable Race'

select *
from Product
where ProductNumber like '%|%%' escape '|'
