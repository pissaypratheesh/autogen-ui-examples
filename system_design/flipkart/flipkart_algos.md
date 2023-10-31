# Flipkart Algos

## Low-Level Design

### 1. User Registration Service
- The User Registration Service is responsible for handling user registration and authentication.
- It provides APIs for user registration, login, and logout.
- The service stores user information in a database, including username, password (hashed), email, and other relevant details.
- The service uses encryption algorithms to securely store and transmit user credentials.

### 2. Product Catalog Service
- The Product Catalog Service manages the catalog of products available on Flipkart.
- It provides APIs for searching, browsing, and filtering products.
- The service stores product information in a database, including product name, description, price, availability, and other relevant details.
- The service uses indexing and search algorithms to efficiently retrieve products based on user queries.

### 3. Shopping Cart Service
- The Shopping Cart Service handles the management of user shopping carts.
- It provides APIs for adding, removing, and updating items in the cart.
- The service stores cart information in a database, including user ID, product ID, quantity, and other relevant details.
- The service uses data structures and algorithms to efficiently handle cart operations and calculate totals.

### 4. Order Processing Service
- The Order Processing Service handles the processing of user orders.
- It provides APIs for placing orders, tracking order status, and managing order history.
- The service stores order information in a database, including user ID, product ID, quantity, payment details, and other relevant details.
- The service uses algorithms for order fulfillment, inventory management, and payment processing.

## Possible Algorithms

### 1. User Authentication Algorithm
- The User Authentication Algorithm verifies user credentials during login.
- It uses hashing algorithms (e.g., bcrypt) to securely store and compare passwords.
- The algorithm checks if the provided username and password match the stored credentials in the database.

### 2. Product Search Algorithm
- The Product Search Algorithm efficiently retrieves products based on user queries.
- It uses indexing techniques (e.g., inverted index) to quickly find relevant products.
- The algorithm considers factors like product name, description, category, and price to rank search results.

### 3. Shopping Cart Calculation Algorithm
- The Shopping Cart Calculation Algorithm calculates the total price and quantity of items in the cart.
- It iterates through the cart items and aggregates the prices and quantities.
- The algorithm applies any applicable discounts or promotions to the cart total.

### 4. Order Fulfillment Algorithm
- The Order Fulfillment Algorithm handles the processing and fulfillment of user orders.
- It checks the availability of products in the inventory.
- The algorithm updates the inventory quantities, generates order IDs, and triggers payment processing.