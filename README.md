# Chewse Marketplace Optimization

        Chewse was a startup that managed the corporate catering experience for their customers.
        This program was designed to reduce the Costs of Goods Sold (COGS) for Chewse by reducing
        the amount of money spent on catering orders. Chewse had a great idea to find lower prices for 
        meals provided by resteraunt vendors by securing price discounts based on guarunteed order
        volumes for the month. This created a challenging optimization problem because a vendor would have
        several levels of pricing, depending on volume (ie $11 per meal for <300 meals, $9 for >300 and <800 meals, and $6.60 for >800 meals).
        Optimal pricing was also subject to complext constraints such as ensuring corporate clients
        received a sufficient variety of cuisines, as well as a myriad of other customer preferences.

        The non-linear optimization was originally solved by a special type of piecewise-linear approximation
        called Specialed Ordered Set - Type 2, or SOS2. It used a very useful Google Operations Research library
        which wrapped C++ functions into python using SWIG.

        The users of this code could interact with it through a Spreadsheet menu button enabled by Google Apps Script
        The script would call this python code through an http request to the AWS server, which initiated the optimization
        through the Flask framework.

        After Google Apps Script received the optimal assignments of meals for the customers and vendors, it would create 
        several pivot tables and charts to visualize several performance metrics. This human-machine interaction
        allowed for Chewse to either override some decisions or select custom assignments for customer
        orders that were not feasible under the constraints (the program would suggest several options in this circumstance)

# See a visual depiction of the "Order Engine" product below[Order Engine Instructions.pdf](https://github.com/nicholaslwright/marketplaceOptimization/files/7290533/Order.Engine.Instructions.pdf)
