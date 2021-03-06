# Chewse Marketplace Optimization

## For a visual description of the "Order Engine" Product, see the PDF below:

[Order Engine Instructions.pdf](https://github.com/nicholaslwright/marketplaceOptimization/files/7290533/Order.Engine.Instructions.pdf)

## Product Description

### Business Context

Chewse was a startup that managed the corporate catering experience for their customers.
This product was designed to reduce the Costs of Goods Sold (COGS) for Chewse by reducing
the amount of money spent on catering orders. Chewse had a great idea to find lower prices for 
meals provided by resteraunt vendors by securing price discounts based on guarunteed order
volumes for the month. This created a challenging optimization problem because a vendor would have
several levels of pricing, depending on volume (ie $11 per meal for <300 meals, $9 for >300 and <800 meals, and $6.60 for >800 meals).
Optimal pricing was also subject to complext constraints such as ensuring corporate clients
received a sufficient variety of cuisines, as well as a myriad of other customer preferences.

### Backend Optimization Development

The non-linear optimization required to reduce costs and maintain customer satisfaction was originally solved 
by a special type of piecewise-linear approximation referenced as a Specialed Ordered Set - Type 2, or SOS2. To
implement this technique, I used Google's Operations Research library which wrapped C++ functions into python using SWIG.

### Front-End Interface through Google Sheets

I decided that the best way for Account Managers and Business Operations staff to interact with this product would be through 
a Spreadsheet menu button enabled by Google Apps Script. The script would call the backend optimization algorithm through an 
http request to the AWS server, which initiated the optimization through the Flask framework.

After Google Apps Script received the optimal assignments of meals for the customers and vendors, it would create 
several pivot tables and charts to visualize several performance metrics that the users were interested in. This human-machine interaction
allowed for Chewse to either override some decisions or select custom assignments for customer
orders that were not feasible under the constraints (the program would suggest several options in this circumstance).

